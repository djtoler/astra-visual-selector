#!/usr/bin/env python3
"""Replay a frozen, read-only matching accuracy batch.

This evaluator measures current artifacts. It never changes the slate, approves a
treatment, selects a template, pairs media, or authorizes rendering.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REQUEST = ROOT / "matching-accuracy" / "batch-001" / "request.json"
DEFAULT_REPORT = ROOT / "matching-accuracy" / "batch-001" / "report.json"
MATCH_TRIAL = ROOT / "match-trial"
if str(MATCH_TRIAL) not in sys.path:
    sys.path.insert(0, str(MATCH_TRIAL))

import candidates as candidate_pool  # noqa: E402


def _read(path: Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _one(rows: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    found = [row for row in rows if row.get(key) == value]
    if len(found) != 1:
        raise ValueError(f"expected one {key}={value}, found {len(found)}")
    return found[0]


def _shot_id(row: dict[str, Any]) -> str:
    return f"{row['passage']}-{row['beat']}"


def _reachable_option_ids(shot: dict[str, Any]) -> set[str]:
    return {
        item["id"]
        for option in shot.get("options") or []
        for item in [option, *(option.get("siblings") or [])]
    }


def validate_request(request: dict[str, Any], *, root: Path = ROOT) -> None:
    if request.get("activationState") != "review_only_not_connected":
        raise ValueError("accuracy batch must remain review-only")
    if request.get("selectionAuthorized") is not False:
        raise ValueError("accuracy batch cannot authorize selection")
    if request.get("renderingAuthorized") is not False:
        raise ValueError("accuracy batch cannot authorize rendering")
    cases = request.get("cases") or []
    if len(cases) != 5 or len({row.get("id") for row in cases}) != 5:
        raise ValueError("accuracy batch requires five distinct cases")
    for name, source in (request.get("sources") or {}).items():
        path = root / source["path"]
        if not path.is_file():
            raise ValueError(f"bound source missing: {name}: {path}")
        actual = _sha(path)
        if actual != source.get("sha256"):
            raise ValueError(f"bound source changed: {name}: {actual}")


def evaluate(request: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    validate_request(request, root=root)
    visual_tasks = _read(root / request["sources"]["visualTasks"]["path"])["tasks"]
    comparison = _read(root / request["sources"]["technicalComparison"]["path"])["tasks"]
    shots = _read(root / request["sources"]["currentSlate"]["path"])
    review = _read(root / request["sources"]["reviewExport"]["path"])["beats"]
    issues = _read(root / request["sources"]["matchingIssues"]["path"])["issues"]
    pool = candidate_pool.load()
    pool_by_id = {row["id"]: row for row in pool}
    cases = {row["id"]: row for row in request["cases"]}
    results: list[dict[str, Any]] = []

    # 1. Eleven people must expose a capacity-qualified AE long-media carousel.
    case = cases["eleven_person_long_carousel_test"]
    task = _one(visual_tasks, "id", case["taskIds"][0])
    shot = _one(shots, "__sourceBeatId", case["sourceBeatId"]) if any(
        "__sourceBeatId" in row for row in shots
    ) else _one([{**row, "__sourceBeatId": _shot_id(row)} for row in shots],
                "__sourceBeatId", case["sourceBeatId"])
    reachable = _reachable_option_ids(shot)
    entity_count = task.get("entityCount", 0)
    eligible_carousel_ids = sorted(
        row["id"] for row in pool
        if candidate_pool.is_long_media_carousel(row, entity_count)
    )
    offered_carousel_ids = sorted(set(eligible_carousel_ids) & reachable)
    offered_non_ae_ids = sorted(
        row_id for row_id in reachable
        if row_id in pool_by_id and pool_by_id[row_id].get("kind") != "after_effects"
    )
    passed = (
        entity_count >= case["minimumPeople"]
        and bool(offered_carousel_ids)
        and all(pool_by_id[row_id].get("kind") == "after_effects" for row_id in offered_carousel_ids)
    )
    results.append({
        "id": case["id"],
        "status": "pass" if passed else "fail",
        "expected": case["expected"],
        "observed": {
            "taskEntityCount": entity_count,
            "batchTreatmentRequiresLongCarousel": True,
            "eligibleLongCarouselCount": len(eligible_carousel_ids),
            "eligibleLongCarouselIds": eligible_carousel_ids,
            "offeredLongCarouselIds": offered_carousel_ids,
            "offeredNonAfterEffectsIds": offered_non_ae_ids,
            "spatialOrInfographicSatisfiesThisBatchTreatment": False,
        },
        "reason": (
            "A capacity-qualified long-carousel After Effects scene is offered."
            if passed else
            "The eleven-person task does not offer a capacity-qualified long-carousel After Effects scene."
        ),
    })

    # 2. The split beat must remain two source-bound tasks and retain unknown timing.
    case = cases["split_beat_visual_tasks"]
    split = [_one(visual_tasks, "id", task_id) for task_id in case["taskIds"]]
    split_comparison = [_one(comparison, "taskId", task_id) for task_id in case["taskIds"]]
    roles = [row.get("taskRole") for row in split]
    timing_states = [
        (row.get("technicalRequirements") or {}).get("timingRequirement", {}).get("status")
        for row in split_comparison
    ]
    passed = (
        len({row["id"] for row in split}) == 2
        and len({row["quote"] for row in split}) == 2
        and roles == ["setup_text", "spatial_comparison"]
        and timing_states == ["unresolved_split_task_span", "unresolved_split_task_span"]
    )
    results.append({
        "id": case["id"],
        "status": "pass" if passed else "fail",
        "expected": case["expected"],
        "observed": {
            "taskIds": [row["id"] for row in split],
            "taskRoles": roles,
            "quotesAreDistinct": len({row["quote"] for row in split}) == 2,
            "timingStates": timing_states,
            "continuityGroups": [row.get("continuityGroup") for row in split],
        },
        "reason": (
            "The VisualTask layer preserves the two communication jobs and correctly refuses to invent per-task timing."
            if passed else
            "The split task or its unresolved timing boundary was collapsed."
        ),
    })

    # 3. Text-heavy document treatment must remain unresolved without exact fields.
    case = cases["text_heavy_document"]
    comp_task = _one(comparison, "taskId", case["taskIds"][0])
    candidate = _one(comp_task.get("candidateComparisons") or [], "candidateId", case["candidateId"])
    on_slate = case["candidateId"] in _reachable_option_ids(
        _one([{**row, "__sourceBeatId": _shot_id(row)} for row in shots],
             "__sourceBeatId", case["sourceBeatId"])
    )
    exact = candidate.get("exactComposition")
    verdict = candidate.get("verdict")
    passed = on_slate and exact is None and verdict != "fillable_now"
    results.append({
        "id": case["id"],
        "status": "pass" if passed else "fail",
        "expected": case["expected"],
        "observed": {
            "candidateId": case["candidateId"],
            "candidateOnSlate": on_slate,
            "technicalVerdict": verdict,
            "exactCompositionMapped": exact is not None,
            "requiredOnScreenText": case["treatmentProposal"]["requiredOnScreenText"],
            "treatmentReviewState": case["treatmentProposal"]["status"],
        },
        "missingRequirements": [
            "exact_scene_to_native_composition_mapping",
            "exact_editable_text_fields_and_limits",
            "editor_approved_treatment",
        ],
        "reason": (
            "The existing document candidate is retained, but the system does not overclaim its unmeasured text capacity."
            if passed else
            "The text-heavy proposal was lost or promoted without exact text evidence."
        ),
    })

    # 4. The saved footage direction must be encoded as a hard media-kind need.
    case = cases["actual_footage_required"]
    comp_task = _one(comparison, "taskId", case["taskIds"][0])
    issue = _one(issues, "id", "PI-12")
    saved_words = [row["words"] for row in issue.get("userWords") or []
                   if row.get("beat") == case["sourceBeatId"]]
    media_req = (comp_task.get("technicalRequirements") or {}).get("mediaRequirements") or {}
    encoded_kinds = media_req.get("requiredMediaKinds")
    requirement_found = case["reviewQuote"] in saved_words
    passed = (
        requirement_found
        and isinstance(encoded_kinds, list)
        and case["requiredMediaKind"] in encoded_kinds
    )
    results.append({
        "id": case["id"],
        "status": "pass" if passed else "fail",
        "expected": case["expected"],
        "observed": {
            "reviewDirectionFound": requirement_found,
            "reviewDirection": saved_words,
            "encodedRequiredMediaKinds": encoded_kinds,
            "currentMediaRequirementStatus": media_req.get("status"),
            "currentCandidateIds": [row.get("candidateId") for row in comp_task.get("candidateComparisons") or []],
        },
        "missingRequirements": [] if passed else [
            "required_media_kind:footage",
            "required_footage_entity:Drake",
            "performance_footage_content_constraint",
        ],
        "reason": (
            "The saved footage direction is encoded in the task contract."
            if passed else
            "The review explicitly requires Drake performance footage, but the task still says its media kind is unresolved."
        ),
    })

    # 5. A reviewed missing-media statement must produce a typed conditional gap.
    case = cases["missing_media_conditional"]
    beat = _one(review, "beat", case["sourceBeatId"])
    note = (beat.get("userReview") or {}).get("note")
    candidate_on_slate = case["candidateId"] in {
        row.get("id") for row in (beat.get("templates") or {}).get("offeredOnSlate") or []
    }
    comp_task = _one(comparison, "taskId", case["taskIds"][0])
    comp_candidate = _one(comp_task.get("candidateComparisons") or [], "candidateId", case["candidateId"])
    current_verdict = comp_candidate.get("verdict")
    media_requirements = (comp_task.get("technicalRequirements") or {}).get("mediaRequirements") or {}
    typed_gap = comp_candidate.get("missingMediaBrief") or media_requirements.get("missingMediaBrief")
    typed_gap_present = (
        isinstance(typed_gap, dict)
        and typed_gap.get("status") == "missing"
        and typed_gap.get("mediaKind") == case["treatmentProposal"]["missingMediaBrief"]["mediaKind"]
    )
    passed = (
        note == case["reviewQuote"]
        and candidate_on_slate
        and current_verdict == "conditional"
        and typed_gap_present
    )
    results.append({
        "id": case["id"],
        "status": "pass" if passed else "fail",
        "expected": case["expected"],
        "observed": {
            "candidateId": case["candidateId"],
            "candidateOnSlate": candidate_on_slate,
            "savedReviewNote": note,
            "currentTechnicalVerdict": current_verdict,
            "typedMissingMediaBriefPresent": typed_gap_present,
        },
        "expectedMissingMediaBrief": case["treatmentProposal"]["missingMediaBrief"],
        "reason": (
            "The missing b-roll is preserved as a typed conditional requirement."
            if passed else
            "The saved review says no appropriate b-roll is available, but the current matcher does not emit a typed conditional media brief."
        ),
    })

    pass_count = sum(row["status"] == "pass" for row in results)
    return {
        "schemaVersion": 1,
        "batchId": request["batchId"],
        "activationState": "review_only_not_connected",
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "sourceHashes": {name: row["sha256"] for name, row in request["sources"].items()},
        "summary": {
            "total": len(results),
            "passed": pass_count,
            "failed": len(results) - pass_count,
            "allPassed": pass_count == len(results),
        },
        "cases": results,
        "nextBoundary": "Treat failures as measured matching-layer work. Do not activate unreviewed treatment proposals.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, default=DEFAULT_REQUEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    request = _read(args.request)
    report = evaluate(request)
    if not args.check:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(dumps(report), encoding="utf-8")
    print(dumps(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
