#!/usr/bin/env python3
"""Prepare and validate unreviewed treatment-requirements drafts.

Preparation is deterministic and free. This module does not call a model, approve
a treatment, compute fillability, select a candidate, or render anything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMPARISON = ROOT / "reports" / "visualtask-ae-spec-comparison.json"
DEFAULT_CATALOG = ROOT / "astra-selector-design" / "approved_media" / "approved-list.json"
DEFAULT_SLATE = ROOT / "pipeline" / "shotlist.capacity.json"
DEFAULT_PROMPT = ROOT / "prompts" / "PROMPT-treatment-requirements.md"
DEFAULT_SCHEMA = ROOT / "grammar" / "treatment-requirements.schema.json"
DEFAULT_OUTPUT = ROOT / "treatment-requirements" / "pilot-001" / "request.json"
PILOT_TASK_ID = "02-02a.main"
PILOT_CANDIDATE_ID = "screen-mockup-rfx--review-002"
MEDIA_KINDS = {"person", "footage", "document", "artwork", "graphic", "composite"}
BATCH_INPUT_KEYS = {"schemaVersion", "pairs"}
PAIR_KEYS = {"taskId", "candidateId"}
REQUEST_KEYS = {
    "schemaVersion", "purpose", "reviewState", "selectionAuthorized",
    "renderingAuthorized", "sources", "taskId", "sourceBeatId", "candidateId",
    "task", "baselineCandidate", "reviewedPreview", "nativeComposition",
    "timingObservation", "timingPolicy", "draftingRules", "requestSha256ForDraft",
}
BATCH_REQUEST_KEYS = {
    "schemaVersion", "purpose", "reviewState", "selectionAuthorized",
    "renderingAuthorized", "pairs", "requests", "batchSha256ForDrafts",
}


def _read(path: Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _source(path: Path) -> dict[str, Any]:
    return {"path": Path(path).name, "sha256": _sha(path), "bytes": Path(path).stat().st_size}


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def artifact_sha(value: Any) -> str:
    return hashlib.sha256(dumps(value).encode()).hexdigest()


def _scene(catalog: dict[str, Any], scene_id: str) -> dict[str, Any]:
    found = [
        scene
        for family in catalog.get("items") or []
        for scene in family.get("scenes") or []
        if scene.get("id") == scene_id
    ]
    if len(found) != 1:
        raise ValueError(f"candidate must resolve to one reviewed scene: {scene_id}")
    return found[0]


def _baseline_option(slate: list[dict[str, Any]], source_id: str, candidate_id: str) -> dict[str, Any]:
    rows = [row for row in slate if f"{row['passage']}-{row['beat']}" == source_id]
    if len(rows) != 1:
        raise ValueError(f"task must resolve to one baseline source beat: {source_id}")
    options = [row for row in rows[0].get("options") or [] if row.get("id") == candidate_id]
    if len(options) != 1:
        raise ValueError(f"candidate is not in the task's baseline slate: {candidate_id}")
    return options[0]


def build_request(
    task_id: str,
    candidate_id: str,
    *,
    comparison_path: Path = DEFAULT_COMPARISON,
    catalog_path: Path = DEFAULT_CATALOG,
    slate_path: Path = DEFAULT_SLATE,
    prompt_path: Path = DEFAULT_PROMPT,
    schema_path: Path = DEFAULT_SCHEMA,
) -> dict[str, Any]:
    paths = {
        "comparison": Path(comparison_path),
        "catalog": Path(catalog_path),
        "baselineSlate": Path(slate_path),
        "prompt": Path(prompt_path),
        "schema": Path(schema_path),
    }
    comparison = _read(paths["comparison"])
    if comparison.get("activationState") != "review_only_not_connected":
        raise ValueError("comparison is not review-only")
    chosen_task = next(
        (task for task in comparison.get("tasks") or [] if task.get("taskId") == task_id),
        None,
    )
    if not chosen_task:
        raise ValueError(f"unknown VisualTask: {task_id}")
    chosen_candidate = next(
        (
            candidate
            for candidate in (chosen_task or {}).get("candidateComparisons") or []
            if candidate.get("candidateId") == candidate_id
        ),
        None,
    )
    if not chosen_candidate:
        raise ValueError(f"candidate was not offered to VisualTask {task_id}: {candidate_id}")
    if not chosen_candidate.get("exactComposition"):
        raise ValueError(f"candidate lacks exact native composition mapping: {candidate_id}")
    exact_span = (
        ((chosen_task or {}).get("technicalRequirements") or {})
        .get("timingRequirement", {})
        .get("exactTaskAudioSpan")
    )
    if not exact_span:
        raise ValueError(f"VisualTask lacks exact task timing: {task_id}")

    scene = _scene(_read(paths["catalog"]), chosen_candidate["candidateId"])
    option = _baseline_option(_read(paths["baselineSlate"]), chosen_task["sourceBeatId"], chosen_candidate["candidateId"])
    exact = chosen_candidate["exactComposition"]
    request = {
        "schemaVersion": 1,
        "purpose": "Prepare one unreviewed treatment-requirements draft for human review",
        "reviewState": "awaiting_model_draft",
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "sources": {name: _source(path) for name, path in paths.items()},
        "taskId": chosen_task["taskId"],
        "sourceBeatId": chosen_task["sourceBeatId"],
        "candidateId": chosen_candidate["candidateId"],
        "task": {
            "quote": chosen_task["quote"],
            "taskRole": chosen_task["taskRole"],
            "resolvedIdentities": chosen_task["resolvedIdentities"],
            "displayEligibleIdentities": chosen_task["displayEligibleIdentities"],
            "requirements": chosen_task["technicalRequirements"],
        },
        "baselineCandidate": {
            "name": option.get("name"),
            "condition": option.get("condition"),
            "mechanism": option.get("mechanism"),
            "evidence": option.get("evidence"),
        },
        "reviewedPreview": {
            "title": scene.get("title"),
            "description": scene.get("description"),
            "clip": scene.get("clip"),
            "thumbnail": scene.get("thumbnail"),
            "reusableStructure": scene.get("reusableStructure"),
            "scriptMatching": scene.get("scriptMatching"),
            "replacementConstraints": scene.get("replacementConstraints") or [],
            "uncertainties": (scene.get("sceneAnalysis") or {}).get("uncertainties") or [],
        },
        "nativeComposition": {
            "id": exact["id"],
            "path": exact["path"],
            "width": exact["width"],
            "height": exact["height"],
            "durationSeconds": exact["durationSeconds"],
            "totalIndependentVisualMediaInputs": exact["totalIndependentVisualMediaInputs"],
            "maxSimultaneouslyEnabledRecursiveVisualInputs": exact["maxSimultaneouslyEnabledRecursiveVisualInputs"],
            "recursiveEditableTextFields": exact["recursiveEditableTextFields"],
            "allowedMediaSlots": exact["recursiveVisualMediaInputs"],
            "allowedTextFields": exact["recursiveTextFields"],
            "mappingEvidence": exact["mappingEvidence"],
        },
        "timingObservation": chosen_candidate.get("timingObservation"),
        "timingPolicy": {
            "status": "requires_user_decision",
            "allowedAdjustments": None,
            "optionsRequiringDecision": ["trim", "loop", "freeze", "speed_change", "extend"],
        },
        "draftingRules": {
            "modelMayPropose": True,
            "modelMayApprove": False,
            "userReviewRequired": True,
            "unknownsRemainUnresolved": True,
            "customStructuralExtensionAllowed": False,
        },
    }
    request["requestSha256ForDraft"] = artifact_sha(request)
    validate_request(request)
    return request


def build_pilot_request(
    *,
    comparison_path: Path = DEFAULT_COMPARISON,
    catalog_path: Path = DEFAULT_CATALOG,
    slate_path: Path = DEFAULT_SLATE,
    prompt_path: Path = DEFAULT_PROMPT,
    schema_path: Path = DEFAULT_SCHEMA,
) -> dict[str, Any]:
    """Compatibility wrapper for the accepted first pilot pairing."""
    return build_request(
        PILOT_TASK_ID,
        PILOT_CANDIDATE_ID,
        comparison_path=comparison_path,
        catalog_path=catalog_path,
        slate_path=slate_path,
        prompt_path=prompt_path,
        schema_path=schema_path,
    )


def validate_pair_batch_input(value: dict[str, Any]) -> list[dict[str, str]]:
    if not isinstance(value, dict) or set(value) - BATCH_INPUT_KEYS:
        raise ValueError("batch input contains unknown fields")
    if value.get("schemaVersion") != 1:
        raise ValueError("batch input schema version must be 1")
    pairs = value.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        raise ValueError("batch input must contain at least one explicit pair")
    normalized = []
    seen: set[tuple[str, str]] = set()
    for index, pair in enumerate(pairs):
        if not isinstance(pair, dict) or set(pair) != PAIR_KEYS:
            raise ValueError(f"batch pair {index} must contain only taskId and candidateId")
        task_id = pair.get("taskId")
        candidate_id = pair.get("candidateId")
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError(f"batch pair {index} has invalid taskId")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            raise ValueError(f"batch pair {index} has invalid candidateId")
        key = (task_id, candidate_id)
        if key in seen:
            raise ValueError(f"duplicate treatment pair: {task_id} / {candidate_id}")
        seen.add(key)
        normalized.append({"taskId": task_id, "candidateId": candidate_id})
    return normalized


def validate_batch_request(batch: dict[str, Any]) -> None:
    if not isinstance(batch, dict) or set(batch) != BATCH_REQUEST_KEYS:
        raise ValueError("batch request contains unknown or missing fields")
    if batch.get("reviewState") != "awaiting_model_drafts":
        raise ValueError("batch request has invalid review state")
    if batch.get("selectionAuthorized") is not False or batch.get("renderingAuthorized") is not False:
        raise ValueError("batch request cannot authorize selection or rendering")
    expected = dict(batch)
    claimed = expected.pop("batchSha256ForDrafts", None)
    if claimed != artifact_sha(expected):
        raise ValueError("batch request hash mismatch")
    pairs = validate_pair_batch_input({
        "schemaVersion": batch.get("schemaVersion"),
        "pairs": batch.get("pairs"),
    })
    requests = batch.get("requests")
    if not isinstance(requests, list) or len(requests) != len(pairs):
        raise ValueError("batch request count does not match explicit pairs")
    for pair, request in zip(pairs, requests):
        validate_request(request)
        if request.get("taskId") != pair["taskId"] or request.get("candidateId") != pair["candidateId"]:
            raise ValueError("batch request pairing mismatch")


def build_batch_request(
    pair_input: dict[str, Any],
    *,
    comparison_path: Path = DEFAULT_COMPARISON,
    catalog_path: Path = DEFAULT_CATALOG,
    slate_path: Path = DEFAULT_SLATE,
    prompt_path: Path = DEFAULT_PROMPT,
    schema_path: Path = DEFAULT_SCHEMA,
) -> dict[str, Any]:
    pairs = validate_pair_batch_input(pair_input)
    requests = [
        build_request(
            pair["taskId"],
            pair["candidateId"],
            comparison_path=comparison_path,
            catalog_path=catalog_path,
            slate_path=slate_path,
            prompt_path=prompt_path,
            schema_path=schema_path,
        )
        for pair in pairs
    ]
    batch = {
        "schemaVersion": 1,
        "purpose": "Prepare explicit unreviewed treatment-requirements drafts for human review",
        "reviewState": "awaiting_model_drafts",
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "pairs": pairs,
        "requests": requests,
    }
    batch["batchSha256ForDrafts"] = artifact_sha(batch)
    validate_batch_request(batch)
    return batch


def validate_request(request: dict[str, Any]) -> None:
    if not isinstance(request, dict) or set(request) != REQUEST_KEYS:
        raise ValueError("treatment request contains unknown or missing fields")
    if request.get("schemaVersion") != 1:
        raise ValueError("treatment request schema version must be 1")
    if request.get("reviewState") != "awaiting_model_draft":
        raise ValueError("treatment request has invalid review state")
    if request.get("selectionAuthorized") is not False or request.get("renderingAuthorized") is not False:
        raise ValueError("treatment request cannot authorize selection or rendering")
    expected = dict(request)
    claimed = expected.pop("requestSha256ForDraft", None)
    if claimed != artifact_sha(expected):
        raise ValueError("treatment request hash mismatch")
    native = request.get("nativeComposition") or {}
    media = native.get("allowedMediaSlots") or []
    text = native.get("allowedTextFields") or []
    if len({row.get("id") for row in media}) != len(media):
        raise ValueError("duplicate native media slot")
    if len({row.get("id") for row in text}) != len(text):
        raise ValueError("duplicate native text field")
    if len(media) != native.get("totalIndependentVisualMediaInputs"):
        raise ValueError("native media-slot count mismatch")
    if len(text) != native.get("recursiveEditableTextFields"):
        raise ValueError("native text-field count mismatch")


def empty_draft(request: dict[str, Any]) -> dict[str, Any]:
    validate_request(request)
    return {
        "schemaVersion": 1,
        "requestSha256": request["requestSha256ForDraft"],
        "taskId": request["taskId"],
        "candidateId": request["candidateId"],
        "reviewState": "model_draft_unreviewed",
        "verdict": None,
        "treatmentSummary": None,
        "mediaAssignments": [],
        "textAssignments": [],
        "dataAssignments": [],
        "timingProposal": {
            "status": "unresolved_user_policy",
            "nativeDurationSeconds": request["nativeComposition"]["durationSeconds"],
            "taskDurationSeconds": request["task"]["requirements"]["timingRequirement"]["exactTaskAudioSpan"]["durationSeconds"],
            "proposedAdjustments": None,
            "evidence": "duration observation only",
        },
        "unresolved": [],
        "evidence": [],
        "selectionAuthorized": False,
        "renderingAuthorized": False,
    }


def validate_draft(draft: dict[str, Any], request: dict[str, Any]) -> dict[str, int]:
    validate_request(request)
    if draft.get("requestSha256") != request["requestSha256ForDraft"]:
        raise ValueError("request hash mismatch")
    if draft.get("taskId") != request["taskId"] or draft.get("candidateId") != request["candidateId"]:
        raise ValueError("draft pairing mismatch")
    if draft.get("reviewState") != "model_draft_unreviewed":
        raise ValueError("model draft cannot approve a treatment")
    if draft.get("verdict") is not None:
        raise ValueError("model draft cannot issue a fillability verdict")
    if draft.get("selectionAuthorized") is not False or draft.get("renderingAuthorized") is not False:
        raise ValueError("model draft cannot authorize selection or rendering")
    allowed_media = {row["id"] for row in request["nativeComposition"]["allowedMediaSlots"]}
    allowed_text = {row["id"] for row in request["nativeComposition"]["allowedTextFields"]}
    media_ids = []
    for row in draft.get("mediaAssignments") or []:
        slot_id = row.get("slotId")
        if slot_id not in allowed_media:
            raise ValueError(f"unknown native media slot: {slot_id}")
        if row.get("mediaKind") not in MEDIA_KINDS:
            raise ValueError(f"invalid media kind: {row.get('mediaKind')}")
        if row.get("status") != "proposed" or not row.get("evidence"):
            raise ValueError("media assignment lacks proposed status or evidence")
        media_ids.append(slot_id)
    if len(media_ids) != len(set(media_ids)):
        raise ValueError("duplicate native media-slot assignment")
    text_ids = []
    for row in draft.get("textAssignments") or []:
        field_id = row.get("fieldId")
        if field_id not in allowed_text:
            raise ValueError(f"unknown native text field: {field_id}")
        if row.get("fitStatus") != "unverified" or not row.get("evidence"):
            raise ValueError("text assignment overclaims fit or lacks evidence")
        text_ids.append(field_id)
    if len(text_ids) != len(set(text_ids)):
        raise ValueError("duplicate native text-field assignment")
    timing = draft.get("timingProposal") or {}
    if request["timingPolicy"]["status"] == "requires_user_decision":
        if timing.get("status") != "unresolved_user_policy" or timing.get("proposedAdjustments") is not None:
            raise ValueError("timing adjustment requires a user decision")
    return {
        "mediaAssignments": len(media_ids),
        "textAssignments": len(text_ids),
        "dataAssignments": len(draft.get("dataAssignments") or []),
        "unresolved": len(draft.get("unresolved") or []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    prepare_pair = sub.add_parser("prepare-pair")
    prepare_pair.add_argument("--task-id", required=True)
    prepare_pair.add_argument("--candidate-id", required=True)
    prepare_pair.add_argument("--output", type=Path, required=True)
    prepare_batch = sub.add_parser("prepare-batch")
    prepare_batch.add_argument("--input", type=Path, required=True)
    prepare_batch.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        request = build_pilot_request()
        summary = {
            "taskId": request["taskId"],
            "candidateId": request["candidateId"],
            "nativeCompositionId": request["nativeComposition"]["id"],
            "reviewState": request["reviewState"],
            "paidModelCallMade": False,
        }
    elif args.command == "prepare-pair":
        request = build_request(args.task_id, args.candidate_id)
        summary = {
            "taskId": request["taskId"],
            "candidateId": request["candidateId"],
            "nativeCompositionId": request["nativeComposition"]["id"],
            "reviewState": request["reviewState"],
            "paidModelCallMade": False,
        }
    else:
        request = build_batch_request(_read(args.input))
        summary = {
            "pairs": len(request["pairs"]),
            "reviewState": request["reviewState"],
            "paidModelCallMade": False,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(dumps(request), encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
