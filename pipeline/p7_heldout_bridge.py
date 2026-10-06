#!/usr/bin/env python3
"""Bridge a source-bound StoryPackage task projection into the repaired P5/P6 path.

This adapter is deliberately evidence-conservative: it preserves the canonical
task contract while leaving media, data, timing, and native template fit unknown
unless the supplied projection contains explicit evidence.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from . import focused_review_queue
from . import p7_blind_review_packet
from . import storypackage_candidate_gallery
from . import storypackage_matching_handoff
from . import visualtask_batch_matching
from .matching_contract_gate import enforce_contracts


REVIEW_ONLY = "review_only_not_connected"


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def _review_artifact(purpose: str, tasks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "purpose": purpose,
        "activationState": REVIEW_ONLY,
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "tasks": tasks,
    }


def _obligation_text(task: dict[str, Any], key: str) -> list[str]:
    return list(dict.fromkeys(
        text for obligation in task.get("obligations") or []
        for text in obligation.get(key) or []
    ))


def _convert_projection(projection: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    visual_tasks: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    preserved: dict[str, dict[str, Any]] = {}
    for ordinal, task in enumerate(projection["tasks"], 1):
        source_beat_ids = list(task.get("sourceBeatIds") or [])
        if not source_beat_ids:
            raise ValueError(f"projected task lacks source beat: {task.get('id')}")
        entity_ids = list((task.get("entities") or {}).get("displayEligible") or [])
        media_needs = list(task.get("mediaNeeds") or []) + list(task.get("cohortMediaNeeds") or [])
        media_kinds = list(dict.fromkeys(
            kind for need in media_needs
            for kind in ([need.get("kind")] if need.get("kind") else need.get("kinds") or [])
        ))
        required_text = list((task.get("quoteRequirements") or {}).get("requiredText") or [])
        values = list(task.get("values") or []) or list((task.get("dataNeeds") or {}).get("values") or [])
        must_be_true = [row.get("intent") for row in task.get("obligations") or [] if row.get("intent")]
        would_be_a_lie = _obligation_text(task, "wouldBeALie")
        withheld = _obligation_text(task, "withheld")
        continuity_ids = [row.get("groupId") for row in task.get("continuity") or [] if row.get("groupId")]
        # A task projection is a source-bound contract. Do not create a local
        # derivative by adding legacy convenience fields; consumers must accept
        # the canonical sourceBeatIds/job/meaning fields directly.
        visual_task = copy.deepcopy(task)
        visual_tasks.append(visual_task)
        media_required = bool(media_needs)
        data_required = bool(values)
        text_required = bool(required_text)
        requirements.append({
            "taskId": task["id"],
            "sourceBeatId": source_beat_ids[0],
            "visualIntent": {
                "job": task["job"], "taskRole": task.get("taskRole"),
                "takeaway": task.get("quote") or "", "continuityGroup": continuity_ids[0] if continuity_ids else None,
            },
            "contentRequirements": {
                "displayEligibleIdentities": entity_ids,
                "displayIdentityCount": len(entity_ids),
                "truthConstraints": must_be_true,
                "prohibitedImplications": would_be_a_lie,
                "perceptibilityConstraints": list(task.get("mustBePerceptible") or []),
                "explicitlyUnstated": withheld,
            },
            "mediaRequirements": {
                "status": "required" if media_required else "not_required",
                "reviewStatus": "source_projection_unreviewed",
                "requiredSlotCount": None if media_required else 0,
                "requiredMediaKinds": media_kinds,
                "requiredEntities": entity_ids if media_required else [],
                "contentConstraints": list(task.get("mustBePerceptible") or []),
                "availabilityStatus": "unknown" if media_required else "not_required",
                "missingMediaBrief": None,
                "reason": "Explicit StoryPackage media need preserved; availability is unresolved." if media_required else "No explicit task-scoped StoryPackage media need.",
            },
            "textRequirements": {
                "status": "unresolved_treatment_dependent" if text_required else "not_required",
                "requiredFieldCount": len(required_text) if text_required else 0,
                "requiredExactStrings": required_text,
                "characterAndLineLimits": None if text_required else [],
                "reason": "Required exact text preserved; native field fit is unresolved." if text_required else None,
            },
            "dataRequirements": {
                "status": "required" if data_required else "not_required",
                "requiredEncodings": list(dict.fromkeys(value.get("kind") or value.get("type") for value in values if value.get("kind") or value.get("type"))),
                "requiredTypedFields": values,
                "semanticConstraints": [value.get("description") for value in values if value.get("description")],
                "reason": "Typed StoryPackage values preserved without claiming a resolved data assignment." if data_required else "No task-scoped typed value requirement.",
            },
            "timingRequirement": {
                "status": "unresolved_human_timing_evidence_required",
                "exactTaskAudioSpan": None,
                "reason": "The StoryPackage supplies text spans but no reviewed narration-time evidence.",
            },
        })
        preserved[task["id"]] = {
            key: copy.deepcopy(task.get(key)) for key in (
                "claimIds", "sourceBeatIds", "presentationOperations", "primaryPresentationOperation",
                "primaryMeaning", "requiredMeanings", "routeDisposition", "obligations", "continuity",
                "values", "cohortRefs", "entityRefs", "mediaNeeds", "cohortMediaNeeds", "dataNeeds",
                "quoteRequirements", "mustBePerceptible", "taskContractReceipt",
            )
        }
    tasks_artifact = _review_artifact("P7 held-out VisualTasks projected from the canonical matching contract", visual_tasks)
    requirements_artifact = _review_artifact("P7 held-out technical requirements with unknown evidence preserved", requirements)
    return tasks_artifact, requirements_artifact, preserved


def build(*, proposals_path: Path, adapter_path: Path, bindings_path: Path, output_dir: Path,
          display_limit: int = 16) -> dict[str, Any]:
    # P7 is a mode of the already registered held-out integration entry point;
    # the frozen P0 entrypoint contract remains immutable.
    contract_receipt = enforce_contracts("heldout_matching_integration.build")
    output_dir = Path(output_dir).resolve()
    projection = storypackage_matching_handoff.build_projection(proposals_path, adapter_path)
    storypackage_matching_handoff.validate_projection(projection)
    tasks, requirements, preserved = _convert_projection(projection)
    package_id = projection["packageId"]
    story = {
        "schemaVersion": 1, "storyId": package_id, "namespace": package_id,
        "activationState": REVIEW_ONLY, "selectionAuthorized": False, "renderingAuthorized": False,
        "visualTasks": {"schemaVersion": 1, "expectedTaskCount": len(tasks["tasks"])},
    }
    comparison = _review_artifact("No held-out candidate-specific native comparison is fabricated", [])
    timing = {"schemaVersion": 1, "activationState": "diagnostic_only", "selectionAuthorized": False,
              "renderingAuthorized": False, "plans": []}
    paths = {name: output_dir / filename for name, filename in {
        "storyPackage": "story-package.json", "visualTasks": "visual-tasks.json",
        "technicalRequirements": "technical-requirements.json", "technicalComparison": "technical-comparison.json",
        "timingPlans": "timing-plans.json", "request": "batch-request.json", "ledger": "p5-ledger.json",
        "ordering": "p6-ordering.json", "gallery": "p6-gallery.json", "queue": "p7-review-queue.json",
        "blindPacket": "p7-blind-review-batch-00.json", "evidence": "p7-bridge-evidence.json",
    }.items()}
    for name, value in (("storyPackage", story), ("visualTasks", tasks),
                        ("technicalRequirements", requirements), ("technicalComparison", comparison),
                        ("timingPlans", timing)):
        _write(paths[name], value)
    request = {
        "schemaVersion": 1, "batchId": f"{package_id}-p7-heldout",
        "activationState": REVIEW_ONLY, "selectionAuthorized": False, "renderingAuthorized": False,
        "sources": {name: str(paths[name]) for name in (
            "storyPackage", "visualTasks", "technicalRequirements", "technicalComparison", "timingPlans")},
    }
    request["sources"]["bindings"] = str(Path(bindings_path).resolve())
    _write(paths["request"], request)
    ledger = visualtask_batch_matching.build(paths["request"])
    _write(paths["ledger"], ledger)
    p7_blind_review_packet.build(ledger_path=paths["ledger"], output_path=paths["blindPacket"])
    ordering = {"displayLimit": display_limit, "candidateRelevance": {},
                "taskIds": [row["taskId"] for row in ledger["tasks"]]}
    _write(paths["ordering"], ordering)
    gallery = storypackage_candidate_gallery.build(ledger_path=paths["ledger"], ordering_path=paths["ordering"])
    _write(paths["gallery"], gallery)
    queue = focused_review_queue.build(paths["gallery"])
    _write(paths["queue"], queue)
    intentional = [row["id"] for row in tasks["tasks"] if (row.get("routeDisposition") or {}).get("templateEligible") is False]
    ledger_by_id = {row["taskId"]: row for row in ledger["tasks"]}
    lost = [task_id for task_id, expected in preserved.items()
            if any((ledger_by_id[task_id]["templateResult"]["candidates"][0]["fitAssessment"]["evidence"]["taskContract"].get(key)
                    if ledger_by_id[task_id]["templateResult"]["candidates"] else tasks["tasks"][[r["id"] for r in tasks["tasks"]].index(task_id)].get(key)) != value
                   for key, value in expected.items())]
    evidence = {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": 1, "packageId": package_id, "activationState": REVIEW_ONLY,
        "selectionAuthorized": False, "renderingAuthorized": False,
        "counts": {
            "projectedTasks": len(projection["tasks"]), "ledgerTasks": len(ledger["tasks"]),
            "candidateVariants": sum(len(row["templateResult"]["candidates"]) for row in ledger["tasks"]),
            "eligibleCandidates": gallery["counts"]["eligible"], "unresolvedCandidates": gallery["counts"]["unresolved"],
            "intentionalNoTemplateTasks": len(intentional), "semanticContractLosses": len(lost),
        },
        "checks": {
            "allTasksReachedP5": len(projection["tasks"]) == len(ledger["tasks"]),
            "semanticContractPreserved": not lost,
            "intentionalNoTemplateRoutesHaveNoCandidates": all(not ledger_by_id[task_id]["templateResult"]["candidates"] for task_id in intentional),
            "noUnsupportedFitPromotion": gallery["counts"]["eligible"] == 0,
            "unknownCandidatesRemainReviewable": gallery["counts"]["unresolved"] > 0,
        },
        "semanticContractLossTaskIds": lost,
        "boundary": "This is blind held-out review evidence. Unknown is not fit, selection, rejection, exhaustion, or rendering authority.",
    }
    _write(paths["evidence"], evidence)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposals", required=True, type=Path)
    parser.add_argument("--adapter", required=True, type=Path)
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--display-limit", type=int, default=16)
    args = parser.parse_args()
    print(json.dumps(build(proposals_path=args.proposals, adapter_path=args.adapter,
                           bindings_path=args.bindings, output_dir=args.output_dir,
                           display_limit=args.display_limit), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
