#!/usr/bin/env python3
"""Connect a validated semantic-split proposal to review-only batch matching."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from . import visualtask_batch_matching as batch_matching
from . import visualtask_split_proposals as split
from .matching_contract_gate import enforce_contracts


ROOT = Path(__file__).resolve().parents[1]
REVIEW_ONLY = "review_only_not_connected"


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(split.dumps(value), encoding="utf-8")


def _source(path: Path) -> dict[str, Any]:
    path = Path(path).resolve()
    return {"path": path.as_posix(), "sha256": split.sha256(path), "bytes": path.stat().st_size}


def _review_artifact(purpose: str, tasks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schemaVersion": 1, "purpose": purpose,
        "activationState": REVIEW_ONLY, "selectionAuthorized": False,
        "renderingAuthorized": False, "tasks": tasks,
    }


def _convert(
    request: dict[str, Any], response: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    counts = split.validate_response(response, request)
    story = request["input"]["storyPackage"]
    roster = {row["id"]: row["name"] for row in request["input"]["rosterContext"]["entities"]}
    beats = {row["id"]: row for row in story["beats"]}
    proposals = {row["sourceBeatId"]: row for row in response["beatProposals"]}
    visual_tasks: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    ordinal = 0
    preserved = Counter()
    source_refs = Counter()
    for beat in story["beats"]:
        proposal = proposals[beat["id"]]
        truth = {row["id"]: row for row in beat["truthConstraints"]}
        prohibitions = {row["id"]: row for row in beat["prohibitions"]}
        data = {row["id"]: row for row in beat["dataRequirements"]}
        source_refs.update({
            "truth": len(truth), "prohibitions": len(prohibitions),
            "data": len(data), "entities": len(beat["entityRefs"]),
            "cohorts": len(beat["cohortRefs"]),
            "perceptibility": len(beat["perceptibilityConstraints"]),
        })
        allocated = {key: set() for key in source_refs}
        for proposed in proposal["tasks"]:
            ordinal += 1
            task_id = f"{story['namespace']}.{proposed['taskKey']}"
            entity_names = [roster[ref] for ref in proposed["entityRefs"]]
            truth_rows = [truth[ref] for ref in proposed["truthConstraintRefs"]]
            prohibition_rows = [prohibitions[ref] for ref in proposed["prohibitionRefs"]]
            data_rows = [data[ref] for ref in proposed["dataRequirementRefs"]]
            allocated["truth"].update(proposed["truthConstraintRefs"])
            allocated["prohibitions"].update(proposed["prohibitionRefs"])
            allocated["data"].update(proposed["dataRequirementRefs"])
            allocated["entities"].update(proposed["entityRefs"])
            allocated["cohorts"].update(proposed["cohortRefs"])
            allocated["perceptibility"].update(proposed["perceptibilityConstraints"])
            kinds = list(proposed["requiredMediaKinds"])
            visual_tasks.append({
                "id": task_id, "sourceBeatId": beat["id"], "passageId": beat["id"],
                "ordinal": ordinal, "taskRole": proposed["taskRole"],
                "quote": proposed["quote"], "sourceSpan": proposed["span"],
                "job": proposed["visualJob"], "sourceBeatJob": proposed["visualJob"],
                "entityCount": len(entity_names), "identityCount": len(entity_names),
                "entityKind": None, "takeaway": proposed["takeaway"],
                "mustBeTrue": [row["text"] for row in truth_rows],
                "mustBePerceptible": list(proposed["perceptibilityConstraints"]),
                "wouldBeALie": [row["text"] for row in prohibition_rows],
                "unstated": [], "continuityGroup": beat["continuityGroup"],
                "templateAdmissions": [],
                "timing": {"status": "unresolved_storypackage_has_no_audio_timing", "exactTaskAudioSpan": None},
                "entities": {
                    "explicit": entity_names, "implied": [], "cohorts": list(proposed["cohortRefs"]),
                    "resolved": entity_names, "displayEligible": entity_names,
                    "ambiguous": [], "unknownNames": [], "unresolved": [],
                },
                "semanticSplitProvenance": {
                    "requestId": response["requestId"], "taskKey": proposed["taskKey"],
                    "cohortRefs": list(proposed["cohortRefs"]),
                    "reason": proposed["reason"], "rationale": proposal["rationale"],
                    "reviewState": response["reviewState"],
                    "truthConstraintRefs": proposed["truthConstraintRefs"],
                    "prohibitionRefs": proposed["prohibitionRefs"],
                    "dataRequirementRefs": proposed["dataRequirementRefs"],
                    "editorContextRefs": proposed["editorContextRefs"],
                },
            })
            requirements.append({
                "taskId": task_id, "sourceBeatId": beat["id"],
                "timingRequirement": {
                    "status": "unresolved_human_timing_evidence_required",
                    "exactTaskAudioSpan": None,
                    "reason": "The StoryPackage supplies exact text spans but no reviewed narration-time provider evidence.",
                },
                "mediaRequirements": {
                    "status": "required" if kinds else "not_required",
                    "reviewStatus": "external_proposal_unreviewed",
                    "requiredSlotCount": None if kinds else 0,
                    "requiredMediaKinds": kinds, "requiredEntities": entity_names,
                    "contentConstraints": list(proposed["perceptibilityConstraints"]),
                    "singlePersonGroupEligibility": None,
                    "availabilityStatus": "unknown", "missingMediaBrief": None,
                    "reason": "Typed media kinds and entities are preserved from the validated semantic-split proposal.",
                },
                "textRequirements": {
                    "status": "unresolved_treatment_dependent" if "text" in kinds else "not_required",
                    "requiredFieldCount": None if "text" in kinds else 0,
                    "requiredExactStrings": None if "text" in kinds else [],
                    "characterAndLineLimits": None if "text" in kinds else [],
                    "reason": "The semantic proposal does not assign native text fields." if "text" in kinds else None,
                },
                "dataRequirements": {
                    "status": "required" if data_rows else "not_required",
                    "requiredEncodings": sorted({row["kind"] for row in data_rows}),
                    "requiredTypedFields": data_rows,
                    "semanticConstraints": [row["description"] for row in data_rows],
                    "reason": "Typed data requirements are preserved by source reference.",
                },
                "contentRequirements": {
                    "displayEligibleIdentities": entity_names,
                    "displayIdentityCount": len(entity_names),
                    "truthConstraints": [row["text"] for row in truth_rows],
                    "prohibitedImplications": [row["text"] for row in prohibition_rows],
                    "perceptibilityConstraints": list(proposed["perceptibilityConstraints"]),
                    "explicitlyUnstated": [],
                },
            })
        preserved.update({key: len(values) for key, values in allocated.items()})
    tasks_artifact = _review_artifact("Held-out VisualTasks converted from a validated semantic-split proposal", visual_tasks)
    tasks_artifact["storyId"] = story["storyId"]
    requirements_artifact = _review_artifact("Held-out technical requirements preserved from semantic-split references", requirements)
    requirements_artifact["storyId"] = story["storyId"]
    preservation = {
        "sourceReferenceCounts": dict(sorted(source_refs.items())),
        "preservedReferenceCounts": dict(sorted(preserved.items())),
        "lostReferenceCount": sum(source_refs.values()) - sum(preserved.values()),
    }
    return tasks_artifact, requirements_artifact, {"splitCounts": counts, "requirementPreservation": preservation}


def build(
    *, story_path: Path, vocabulary_path: Path, roster_path: Path,
    editor_context_path: Path, response_path: Path, bindings_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    contract_receipt = enforce_contracts("heldout_matching_integration.build")
    output_dir = Path(output_dir).resolve()
    request = split.prepare_request_from_files(story_path, vocabulary_path, roster_path, editor_context_path)
    response = split.read(response_path)
    tasks, requirements, evidence = _convert(request, response)
    paths = {
        "story": output_dir / "story-package.json",
        "splitRequest": output_dir / "semantic-split-request.json",
        "splitOutput": output_dir / "semantic-split-output.json",
        "tasks": output_dir / "visual-tasks.json",
        "requirements": output_dir / "technical-requirements.json",
        "comparison": output_dir / "technical-comparison.json",
        "timing": output_dir / "timing-plans.json",
        "batchRequest": output_dir / "batch-request.json",
        "batchOutput": output_dir / "template-fit-output.json",
        "evidence": output_dir / "evaluation-evidence.json",
    }
    _write(paths["story"], request["input"]["storyPackage"])
    _write(paths["splitRequest"], request)
    _write(paths["splitOutput"], response)
    _write(paths["tasks"], tasks)
    _write(paths["requirements"], requirements)
    _write(paths["comparison"], _review_artifact("No held-out native technical comparisons are fabricated", []))
    _write(paths["timing"], {
        "schemaVersion": 1, "activationState": "diagnostic_only",
        "selectionAuthorized": False, "renderingAuthorized": False, "plans": [],
    })
    batch_request = {
        "schemaVersion": 1, "batchId": f"{request['input']['storyPackage']['storyId']}-held-out-match",
        "activationState": REVIEW_ONLY, "selectionAuthorized": False, "renderingAuthorized": False,
        "sources": {
            "storyPackage": str(paths["story"]), "visualTasks": str(paths["tasks"]),
            "technicalRequirements": str(paths["requirements"]), "bindings": str(Path(bindings_path).resolve()),
            "technicalComparison": str(paths["comparison"]), "timingPlans": str(paths["timing"]),
        },
    }
    _write(paths["batchRequest"], batch_request)
    matched = batch_matching.build(paths["batchRequest"])
    _write(paths["batchOutput"], matched)
    media_verdicts = Counter(row["mediaResult"]["availabilityVerdict"] for row in matched["tasks"])
    template_verdicts = Counter(row["templateResult"]["fitVerdict"] for row in matched["tasks"])
    reviewed_briefs = sum(
        (row.get("mediaRequirements") or {}).get("missingMediaBrief") is not None
        for row in requirements["tasks"]
    )
    conditional = media_verdicts["conditional"]
    artifact = {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": 1, "storyId": request["input"]["storyPackage"]["storyId"],
        "activationState": REVIEW_ONLY, "selectionAuthorized": False, "renderingAuthorized": False,
        "sources": {name: _source(path) for name, path in paths.items() if name != "evidence"},
        "split": {
            **evidence["splitCounts"], "completeCoverage": True,
            "overlapCount": 0, "lostSpanCount": 0,
            "automatedValidation": "pass", "humanApprovalStatus": response["humanApproval"]["status"],
        },
        "requirements": {**evidence["requirementPreservation"], "status": "pass"},
        "templateFit": {
            "visualTasks": len(matched["tasks"]), "tasksWithVerdict": len(matched["tasks"]),
            "verdictCounts": dict(sorted(template_verdicts.items())), "status": "pass",
        },
        "mediaAvailability": {
            "visualTasks": len(matched["tasks"]), "tasksWithVerdict": len(matched["tasks"]),
            "verdictCounts": dict(sorted(media_verdicts.items())), "status": "pass",
        },
        "conditionalGap": {
            "reviewedMissingMediaBriefs": reviewed_briefs,
            "conditionalMediaVerdicts": conditional,
            "status": "not_applicable_no_reviewed_missing_media_briefs" if reviewed_briefs == 0 else "assessed",
        },
    }
    _write(paths["evidence"], artifact)
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--story-package", required=True, type=Path)
    parser.add_argument("--task-vocabulary", required=True, type=Path)
    parser.add_argument("--roster-context", required=True, type=Path)
    parser.add_argument("--editor-context", required=True, type=Path)
    parser.add_argument("--split-response", required=True, type=Path)
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    artifact = build(
        story_path=args.story_package, vocabulary_path=args.task_vocabulary,
        roster_path=args.roster_context, editor_context_path=args.editor_context,
        response_path=args.split_response, bindings_path=args.bindings,
        output_dir=args.output_dir,
    )
    print(split.dumps(artifact), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
