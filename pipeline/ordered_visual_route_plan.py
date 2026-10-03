#!/usr/bin/env python3
"""Build the ordered route, timing and transition receipt without selecting a template."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .matching_contract_gate import enforce_contracts
except ImportError:
    from matching_contract_gate import enforce_contracts

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS = ROOT / "grammar" / "visual-tasks.json"
DEFAULT_REQUIREMENTS = ROOT / "grammar" / "visual-task-technical-requirements.json"
DEFAULT_BATCH = ROOT / "reports" / "full-visualtask-batch-matching-current.json"
DEFAULT_RECONCILIATION = ROOT / "reports" / "prior-editor-review-reconciliation.json"
DEFAULT_REVIEW = ROOT / "grammar" / "beat-review-export-2026-09-27.json"
DEFAULT_TIMING = ROOT / "reports" / "post-render-timing-feasibility.json"
DEFAULT_BROLL_OVERRIDES = ROOT / "grammar" / "broll-route-editorial-overrides.json"
DEFAULT_LOCAL_TEMPLATES = ROOT / "grammar" / "local-templates.json"
DEFAULT_OUTPUT = ROOT / "reports" / "ordered-visual-route-plan.json"
MAX_REVIEW_CHOICES = 6


def read(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source(path: Path) -> dict[str, str]:
    return {"path": Path(path).resolve().relative_to(ROOT.resolve()).as_posix(), "sha256": sha(path)}


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def build(*, tasks_path: Path = DEFAULT_TASKS, requirements_path: Path = DEFAULT_REQUIREMENTS,
          batch_path: Path = DEFAULT_BATCH, reconciliation_path: Path = DEFAULT_RECONCILIATION,
          review_path: Path = DEFAULT_REVIEW, timing_path: Path = DEFAULT_TIMING,
          broll_overrides_path: Path = DEFAULT_BROLL_OVERRIDES,
          local_templates_path: Path = DEFAULT_LOCAL_TEMPLATES) -> dict[str, Any]:
    contract_receipt = enforce_contracts("ordered_visual_route_plan.build")
    tasks = read(tasks_path).get("tasks") or []
    requirements = read(requirements_path).get("tasks") or []
    batch = read(batch_path)
    reconciliation = read(reconciliation_path)
    review = read(review_path)
    timing = read(timing_path)
    broll_overrides = read(broll_overrides_path)
    local_templates = read(local_templates_path)
    retired_template_ids = set((local_templates.get("remove") or {}).keys())
    if broll_overrides.get("renderingAuthorized") is not False:
        raise ValueError("B-roll editorial overrides cannot authorize rendering")
    route_overrides = broll_overrides.get("overrides") or {}

    requirement_by_id = {row["taskId"]: row for row in requirements}
    batch_by_id = {row["taskId"]: row for row in batch.get("tasks") or []}
    review_by_beat = {row["beat"]: row for row in review.get("beats") or []}
    selected_by_task: dict[str, set[str]] = {}
    for row in reconciliation.get("rows") or []:
        if row.get("state") in {"prior_selected", "split_task_requires_independent_review"}:
            selected_by_task.setdefault(row["taskId"], set()).add(row["candidateId"])
    timing_by_pair = {
        (row["taskId"], row["candidateId"]): row["plan"]
        for row in timing.get("plans") or []
    }

    def exact_span(task_id: str) -> dict[str, Any]:
        value = requirement_by_id[task_id]["timingRequirement"].get("exactTaskAudioSpan")
        if value:
            return value
        value = requirement_by_id[task_id]["timingRequirement"].get("sourceBeatSpan")
        if not value:
            raise ValueError(f"No timing span for {task_id}")
        return value

    ordered_tasks = sorted(tasks, key=lambda row: (
        exact_span(row["id"])["startSeconds"],
        exact_span(row["id"])["endSeconds"],
        row.get("ordinal", 0),
        row["id"],
    ))
    scenes = []
    for sequence_index, task in enumerate(ordered_tasks, start=1):
        task_id = task["id"]
        batch_task = batch_by_id[task_id]
        candidates = [
            row for row in batch_task.get("templateResult", {}).get("candidates") or []
            if row.get("candidateId") not in retired_template_ids
            if row.get("fitAssessment", {}).get("verdict") in {
                "conditional", "split_task_requires_independent_review",
            }
        ]
        prior_selected = selected_by_task.get(task_id, set()) - retired_template_ids
        reviewed_by_id = {
            row["id"]: row
            for row in review_by_beat.get(task["sourceBeatId"], {}).get("templates", {}).get("boundToJob", [])
        }
        for candidate_id in sorted(prior_selected - {row["candidateId"] for row in candidates}):
            reviewed = reviewed_by_id.get(candidate_id)
            if reviewed:
                candidates.append({
                    "candidateId": candidate_id,
                    "name": reviewed.get("name"),
                    "condition": reviewed.get("condition"),
                    "fitAssessment": {
                        "verdict": "split_task_requires_independent_review",
                        "gaps": [{
                            "type": "split_task_candidate_specific_validation",
                            "status": "conditional",
                            "reason": "Preserved from the editor-selected split-beat treatment; exact task binding remains a use-time check.",
                        }],
                    },
                })
        current_prior = [row for row in candidates if row["candidateId"] in prior_selected]
        user_review = (review_by_beat.get(task["sourceBeatId"], {}).get("userReview") or {})
        editor_requested_broll = user_review.get("broll") is True
        override = route_overrides.get(task_id) or {}
        disposition = override.get("disposition")
        post_beat_broll = disposition == "template_with_post_broll"
        if disposition == "clarification_required":
            route = "deferred"
            route_reason = "editorial_broll_ruling_conflict_requires_clarification"
        elif disposition in {"broll", "broll_or_images"}:
            route = "broll"
            route_reason = "current_editor_broll_ruling"
        elif disposition in {"template", "template_with_post_broll"}:
            if not candidates:
                route = "deferred"
                route_reason = "current_editor_no_broll_and_empty_template_slate"
            elif not current_prior:
                route = "deferred"
                route_reason = "current_editor_no_broll_and_no_surviving_prior_template"
            else:
                route = "template_review"
                route_reason = "current_editor_template_route"
        elif editor_requested_broll:
            route = "broll"
            route_reason = "prior_editor_requested_broll"
        elif not candidates:
            route = "broll"
            route_reason = "optional_template_route_has_no_valid_choices"
        elif not current_prior:
            route = "broll"
            route_reason = "no_prior_selected_candidate_remains_in_current_conditional_set"
        else:
            route = "template_review"
            route_reason = "prior_editor_choice_preserved_in_existing_choice_review_set"

        span = exact_span(task_id)
        scene: dict[str, Any] = {
            "sequenceIndex": sequence_index,
            "taskId": task_id,
            "sourceBeatId": task["sourceBeatId"],
            "quote": task["quote"],
            "continuityGroup": task.get("continuityGroup"),
            "route": route,
            "routeReason": route_reason,
            "editorialOverride": override or None,
            "brollFallbackAvailable": True,
            "narrationSpan": span,
            "transition": {
                "required": True,
                "treatment": "short_editorial_transition",
                "source": "user_ruling_all_scenes_require_transition",
            },
            "selectionAuthorized": False,
            "renderingAuthorized": False,
        }
        if route == "broll":
            media = batch_task.get("mediaResult") or {}
            scene["treatment"] = {
                "kind": "broll",
                "timingMethod": "edit_to_narration_span",
                "targetDurationSeconds": span["durationSeconds"],
                "preferredMediaVerdict": media.get("availabilityVerdict"),
                "preferredMediaGaps": media.get("gaps") or [],
                "assetBinding": "pending_release_handoff",
            }
            scene["templateChoices"] = []
        elif route == "template_review":
            ordered_candidates = current_prior + [row for row in candidates if row not in current_prior]
            choices = []
            for candidate in ordered_candidates[:MAX_REVIEW_CHOICES]:
                plan = timing_by_pair.get((task_id, candidate["candidateId"]))
                choices.append({
                    "candidateId": candidate["candidateId"],
                    "name": candidate.get("name"),
                    "condition": candidate.get("condition"),
                    "priorEditorSelected": candidate["candidateId"] in prior_selected,
                    "fitVerdict": candidate.get("fitAssessment", {}).get("verdict"),
                    "validationGaps": candidate.get("fitAssessment", {}).get("gaps") or [],
                    "timingDisposition": plan or {
                        "status": "candidate_specific_use_time_review_required",
                        "method": "preserve_native_render_then_post_retime",
                        "narrationDurationSeconds": span["durationSeconds"],
                        "endingTreatment": "add_transition",
                        "selectionAuthorized": False,
                        "renderingAuthorized": False,
                    },
                })
            scene["treatment"] = {
                "kind": "template_review",
                "finalChoice": None,
                "timingMethod": "preserve_native_render_then_post_retime",
                "repetitionReview": "pending_after_final_template_selection",
            }
            scene["templateChoices"] = choices
            if post_beat_broll:
                scene["postBeatBroll"] = {
                    "required": True,
                    "placement": "after_beat",
                    "assetBinding": "pending_release_handoff",
                    "source": "current_editor_ruling",
                }
        else:
            scene["treatment"] = {
                "kind": "deferred",
                "reason": route_reason,
                "editorialClarificationRequired": disposition == "clarification_required",
            }
            scene["templateChoices"] = []
        scenes.append(scene)

    artifact = {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": 1,
        "planId": "year-seventeen-ordered-visual-routes-20261001",
        "purpose": "Ordered route, continuity, timing and transition plan before final human template selection",
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "sources": {name: source(path) for name, path in {
            "visualTasks": tasks_path,
            "technicalRequirements": requirements_path,
            "batchMatching": batch_path,
            "priorReviewReconciliation": reconciliation_path,
            "priorBeatReview": review_path,
            "timingFeasibility": timing_path,
            "brollEditorialOverrides": broll_overrides_path,
            "localTemplateRetirements": local_templates_path,
        }.items()},
        "counts": {
            "scenes": len(scenes),
            "brollRoutes": sum(row["route"] == "broll" for row in scenes),
            "templateReviewRoutes": sum(row["route"] == "template_review" for row in scenes),
            "deferredRoutes": sum(row["route"] == "deferred" for row in scenes),
            "postBeatBrollSegments": sum(bool(row.get("postBeatBroll")) for row in scenes),
            "transitionsRequired": sum(row["transition"]["required"] for row in scenes),
            "sequenceConflicts": 0,
        },
        "sequencePlanningReceipt": {
            "accepted": True,
            "orderedTasks": len(scenes),
            "brollFallbackOnEveryTask": all(row["brollFallbackAvailable"] for row in scenes),
            "finalTemplateSelectionDeferredToHumanReview": True,
        },
        "scenes": scenes,
    }
    validate(artifact, verify_sources=False)
    return artifact


def validate(artifact: dict[str, Any], *, verify_sources: bool = True) -> dict[str, Any]:
    scenes = artifact.get("scenes") or []
    if len(scenes) != 41 or len({row.get("taskId") for row in scenes}) != 41:
        raise ValueError("Ordered visual plan must contain exactly 41 unique tasks.")
    if [row.get("sequenceIndex") for row in scenes] != list(range(1, 42)):
        raise ValueError("Ordered visual plan has missing or reordered sequence indexes.")
    starts = [row["narrationSpan"]["startSeconds"] for row in scenes]
    if starts != sorted(starts):
        raise ValueError("Ordered visual plan is not in narration order.")
    if any(not row.get("brollFallbackAvailable") or not row.get("transition", {}).get("required") for row in scenes):
        raise ValueError("Every task must retain b-roll fallback and a transition.")
    for row in scenes:
        choices = row.get("templateChoices") or []
        if row.get("route") == "template_review":
            if not choices or len(choices) > MAX_REVIEW_CHOICES or len({item["candidateId"] for item in choices}) != len(choices):
                raise ValueError("Every template review route must present one or more distinct choices within the display limit.")
            if not any(item.get("priorEditorSelected") for item in choices):
                raise ValueError("Template review route lost the prior editor decision.")
        elif row.get("route") in {"broll", "deferred"}:
            if choices:
                raise ValueError("B-roll or deferred route cannot silently select a template.")
        else:
            raise ValueError("Unknown visual route.")
    if artifact.get("selectionAuthorized") is not False or artifact.get("renderingAuthorized") is not False:
        raise ValueError("Sequence planning cannot authorize selection or rendering.")
    receipt = artifact.get("sequencePlanningReceipt") or {}
    if receipt.get("accepted") is not True or receipt.get("orderedTasks") != 41:
        raise ValueError("Sequence planning receipt is missing or incomplete.")
    if verify_sources:
        for item in artifact.get("sources", {}).values():
            path = ROOT / item["path"]
            if not path.is_file() or sha(path) != item["sha256"]:
                raise ValueError("Ordered visual plan source is missing or stale.")
    return artifact["counts"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "validate"))
    args = parser.parse_args()
    if args.command == "build":
        artifact = build()
        DEFAULT_OUTPUT.write_text(dumps(artifact))
        print(json.dumps(validate(artifact, verify_sources=False), sort_keys=True))
    else:
        print(json.dumps(validate(read(DEFAULT_OUTPUT)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
