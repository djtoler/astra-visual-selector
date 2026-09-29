#!/usr/bin/env python3
"""Build source-bound technical requirements for the VisualTask pilot.

Only requirements explicitly present in the current VisualTask and baseline
shot records are encoded. Treatment-dependent slot, media-kind, text and typed
data decisions remain unresolved rather than inferred.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS = ROOT / "grammar" / "visual-tasks.json"
DEFAULT_SLATE = ROOT / "pipeline" / "shotlist.capacity.json"
DEFAULT_TIMING_REVIEWS = ROOT / "grammar" / "visual-task-timing-reviews.json"
DEFAULT_MEDIA_REQUIREMENTS = ROOT / "grammar" / "visual-task-media-requirements.json"
DEFAULT_OUTPUT = ROOT / "grammar" / "visual-task-technical-requirements.json"


def _read(path: Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _logical(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return Path(path).name


def _source(path: Path) -> dict[str, Any]:
    return {"path": _logical(path), "sha256": _sha(path), "bytes": Path(path).stat().st_size}


def _slate_index(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        source_id = f"{row['passage']}-{row['beat']}"
        if source_id in out:
            raise ValueError(f"duplicate baseline source beat: {source_id}")
        out[source_id] = row
    return out


def _reviewed_timing_spans(
    raw: dict[str, Any],
    tasks: list[dict[str, Any]],
    slate: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    if raw.get("schemaVersion") != 1:
        raise ValueError("unsupported VisualTask timing-review schema")
    if raw.get("activationState") != "review_only_not_connected":
        raise ValueError("VisualTask timing reviews must remain review-only")
    if raw.get("selectionAuthorized") is not False or raw.get("renderingAuthorized") is not False:
        raise ValueError("VisualTask timing reviews cannot authorize selection or rendering")

    tasks_by_id = {row["id"]: row for row in tasks}
    spans: dict[str, dict[str, Any]] = {}
    for review in raw.get("reviews") or []:
        source_id = review.get("sourceBeatId")
        if source_id not in slate:
            raise ValueError(f"timing review references unknown source beat: {source_id}")
        if (review.get("editorReview") or {}).get("status") != "approved":
            raise ValueError(f"timing review is not editor-approved: {source_id}")
        evidence = review.get("measurementEvidence") or {}
        evidence_path = ROOT / evidence.get("path", "")
        if not evidence_path.is_file() or _sha(evidence_path) != evidence.get("sha256"):
            raise ValueError(f"timing review measurement evidence is missing or stale: {source_id}")
        evidence_artifact = _read(evidence_path)
        events = (evidence_artifact.get("contract") or {}).get("visualEvents") or evidence_artifact.get("visualEvents") or []
        measured = next(
            (row for row in events if row.get("eventId") == evidence.get("eventId")),
            None,
        )
        if measured is None or measured.get("measuredStartSeconds") != evidence.get("measuredStartSeconds"):
            raise ValueError(f"timing review measurement does not replay: {source_id}")

        source_span = slate[source_id]
        rows = review.get("taskSpans") or []
        if not rows:
            raise ValueError(f"timing review has no task spans: {source_id}")
        ordered = sorted(rows, key=lambda row: row["startSeconds"])
        for index, row in enumerate(ordered):
            task_id = row.get("taskId")
            task = tasks_by_id.get(task_id)
            if task is None or task.get("sourceBeatId") != source_id:
                raise ValueError(f"timing review references wrong task: {task_id}")
            if row.get("quote") != task.get("quote"):
                raise ValueError(f"timing review quote changed: {task_id}")
            start = row.get("startSeconds")
            end = row.get("endSeconds")
            duration = row.get("durationSeconds")
            if not all(isinstance(value, (int, float)) for value in (start, end, duration)):
                raise ValueError(f"timing review has invalid seconds: {task_id}")
            if round(end - start, 6) != round(duration, 6) or start >= end:
                raise ValueError(f"timing review duration mismatch: {task_id}")
            if start < source_span["start"] or end > source_span["end"]:
                raise ValueError(f"timing review exceeds source beat: {task_id}")
            if index and ordered[index - 1]["endSeconds"] != start:
                raise ValueError(f"timing review spans are not contiguous: {source_id}")
            if task_id in spans:
                raise ValueError(f"duplicate reviewed timing span: {task_id}")
            spans[task_id] = {
                "startSeconds": start,
                "endSeconds": end,
                "durationSeconds": duration,
                "evidence": "Editor-approved phrase boundary bound to measured narration alignment.",
                "reviewedBoundary": review["boundary"],
                "measurementEvidence": evidence,
                "editorReview": review["editorReview"],
            }
    return spans


def _reviewed_media_requirements(raw: dict[str, Any], tasks: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if raw.get("schemaVersion") != 1:
        raise ValueError("unsupported VisualTask media-requirement schema")
    if raw.get("activationState") != "review_only_not_connected":
        raise ValueError("VisualTask media requirements must remain review-only")
    if raw.get("selectionAuthorized") is not False or raw.get("renderingAuthorized") is not False:
        raise ValueError("VisualTask media requirements cannot authorize selection or rendering")
    for source in (raw.get("sources") or {}).values():
        path = ROOT / source.get("path", "")
        if not path.is_file() or _sha(path) != source.get("sha256"):
            raise ValueError("VisualTask media-requirement evidence is missing or stale")
    task_ids = {row["id"] for row in tasks}
    out: dict[str, dict[str, Any]] = {}
    for row in raw.get("requirements") or []:
        task_id = row.get("taskId")
        if task_id not in task_ids or task_id in out:
            raise ValueError(f"unknown or duplicate VisualTask media requirement: {task_id}")
        if row.get("reviewStatus") not in {"approved", "proposed"}:
            raise ValueError(f"invalid media-requirement review status: {task_id}")
        if row.get("status") not in {"required", "missing_required_media"}:
            raise ValueError(f"invalid media-requirement status: {task_id}")
        kinds = row.get("requiredMediaKinds")
        entities = row.get("requiredEntities")
        constraints = row.get("contentConstraints")
        evidence = row.get("evidence") or {}
        if not isinstance(kinds, list) or not kinds or any(not isinstance(value, str) or not value for value in kinds):
            raise ValueError(f"media requirement lacks typed media kinds: {task_id}")
        if not isinstance(entities, list) or any(not isinstance(value, str) or not value for value in entities):
            raise ValueError(f"media requirement has invalid entities: {task_id}")
        if not isinstance(constraints, list) or any(not isinstance(value, str) or not value for value in constraints):
            raise ValueError(f"media requirement has invalid content constraints: {task_id}")
        if not evidence.get("reference") or not evidence.get("quote"):
            raise ValueError(f"media requirement lacks editor evidence: {task_id}")
        missing = row.get("missingMediaBrief")
        if row["status"] == "missing_required_media":
            if row.get("availabilityStatus") != "missing" or not isinstance(missing, dict):
                raise ValueError(f"missing media requirement lacks a typed brief: {task_id}")
            if missing.get("status") != "missing" or missing.get("mediaKind") not in kinds:
                raise ValueError(f"missing media brief conflicts with its requirement: {task_id}")
        elif missing is not None:
            raise ValueError(f"available/unknown media requirement carries a missing brief: {task_id}")
        out[task_id] = row
    return out


def build_requirements(
    *,
    tasks_path: Path = DEFAULT_TASKS,
    slate_path: Path = DEFAULT_SLATE,
    timing_reviews_path: Path = DEFAULT_TIMING_REVIEWS,
    media_requirements_path: Path = DEFAULT_MEDIA_REQUIREMENTS,
) -> dict[str, Any]:
    paths = {
        "visualTasks": Path(tasks_path),
        "baselineSlate": Path(slate_path),
        "timingReviews": Path(timing_reviews_path),
        "mediaRequirements": Path(media_requirements_path),
    }
    task_artifact = _read(paths["visualTasks"])
    if task_artifact.get("activationState") != "review_only_not_connected":
        raise ValueError("VisualTask artifact is not review-only")
    tasks = task_artifact.get("tasks") or []
    slate = _slate_index(_read(paths["baselineSlate"]))
    reviewed_spans = _reviewed_timing_spans(_read(paths["timingReviews"]), tasks, slate)
    reviewed_media = _reviewed_media_requirements(_read(paths["mediaRequirements"]), tasks)
    task_counts = Counter(row["sourceBeatId"] for row in tasks)

    rows: list[dict[str, Any]] = []
    for task in tasks:
        source_id = task["sourceBeatId"]
        baseline = slate.get(source_id)
        if baseline is None:
            raise ValueError(f"VisualTask has no baseline source beat: {source_id}")
        if baseline.get("quote") != task.get("quote") and task_counts[source_id] == 1:
            raise ValueError(f"unsplit VisualTask quote differs from baseline source beat: {task['id']}")

        split = task_counts[source_id] > 1
        if split:
            exact_span = reviewed_spans.get(task["id"])
            timing = {
                "status": "exact_reviewed_split_task_span" if exact_span else "unresolved_split_task_span",
                "exactTaskAudioSpan": exact_span,
                "sourceBeatSpan": {
                    "startSeconds": baseline["start"],
                    "endSeconds": baseline["end"],
                    "durationSeconds": baseline["duration"],
                },
                "reason": None if exact_span else "More than one VisualTask shares this source beat and no exact per-task audio split is saved.",
            }
            data_requirements = {
                "status": "source_beat_only_not_task_allocated",
                "requiredEncodings": None,
                "sourceBeatRequiredEncodings": list(baseline.get("requiredEncoding") or []),
                "requiredTypedFields": None,
                "semanticConstraints": list(task.get("mustBeTrue") or []),
                "reason": "Encoding labels exist only for the unsplit source beat and cannot be allocated between its VisualTasks without a reviewed treatment plan.",
            }
        else:
            exact_span = {
                "startSeconds": baseline["start"],
                "endSeconds": baseline["end"],
                "durationSeconds": baseline["duration"],
                "evidence": "The sole VisualTask exactly matches the saved baseline source-beat quote and timing.",
            }
            timing = {
                "status": "exact_source_beat_span",
                "exactTaskAudioSpan": exact_span,
                "sourceBeatSpan": exact_span,
                "reason": None,
            }
            data_requirements = {
                "status": "exact_source_beat_encodings",
                "requiredEncodings": list(baseline.get("requiredEncoding") or []),
                "sourceBeatRequiredEncodings": list(baseline.get("requiredEncoding") or []),
                "requiredTypedFields": None,
                "semanticConstraints": list(task.get("mustBeTrue") or []),
                "reason": "Encoding categories are source-bound, but exact typed field names and values are not present in the current VisualTask contract.",
            }

        identities = list((task.get("entities") or {}).get("displayEligible") or [])
        reviewed_media_row = reviewed_media.get(task["id"])
        media_requirements = ({
            "status": reviewed_media_row["status"],
            "reviewStatus": reviewed_media_row["reviewStatus"],
            "requiredSlotCount": None,
            "requiredMediaKinds": list(reviewed_media_row["requiredMediaKinds"]),
            "requiredEntities": list(reviewed_media_row["requiredEntities"]),
            "contentConstraints": list(reviewed_media_row["contentConstraints"]),
            "singlePersonGroupEligibility": None,
            "availabilityStatus": reviewed_media_row["availabilityStatus"],
            "missingMediaBrief": reviewed_media_row.get("missingMediaBrief"),
            "evidence": reviewed_media_row["evidence"],
            "reason": "A typed editor/treatment media requirement is bound to this exact VisualTask.",
        } if reviewed_media_row else {
            "status": "unresolved_treatment_dependent",
            "reviewStatus": None,
            "requiredSlotCount": None,
            "requiredMediaKinds": None,
            "requiredEntities": None,
            "contentConstraints": None,
            "singlePersonGroupEligibility": None,
            "availabilityStatus": "unknown",
            "missingMediaBrief": None,
            "evidence": None,
            "reason": "A semantic identity can be encoded by media, text, a mark, or a grouped asset; the current VisualTask does not assign identities to template media slots.",
        })
        rows.append({
            "taskId": task["id"],
            "sourceBeatId": source_id,
            "visualIntent": {
                "job": task.get("job"),
                "taskRole": task.get("taskRole"),
                "takeaway": task.get("takeaway"),
                "continuityGroup": task.get("continuityGroup"),
            },
            "contentRequirements": {
                "displayEligibleIdentities": identities,
                "displayIdentityCount": len(identities),
                "perceptibilityConstraints": list(task.get("mustBePerceptible") or []),
                "truthConstraints": list(task.get("mustBeTrue") or []),
                "prohibitedImplications": list(task.get("wouldBeALie") or []),
                "explicitlyUnstated": list(task.get("unstated") or []),
            },
            "dataRequirements": data_requirements,
            "mediaRequirements": media_requirements,
            "textRequirements": {
                "status": "unresolved_treatment_dependent",
                "requiredFieldCount": None,
                "requiredExactStrings": None,
                "characterAndLineLimits": None,
                "reason": "The narration and semantic constraints do not specify which content must appear as editable on-screen text for a particular treatment.",
            },
            "timingRequirement": timing,
        })

    artifact = {
        "schemaVersion": 1,
        "purpose": "Source-bound VisualTask technical requirements for read-only AE matching tests",
        "activationState": "review_only_not_connected",
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "sources": {name: _source(path) for name, path in paths.items()},
        "counts": {
            "sourceBeats": len(task_counts),
            "visualTasks": len(rows),
            "exactTaskAudioSpans": sum(row["timingRequirement"]["exactTaskAudioSpan"] is not None for row in rows),
            "unresolvedTaskAudioSpans": sum(row["timingRequirement"]["exactTaskAudioSpan"] is None for row in rows),
            "knownMediaSlotRequirements": sum(row["mediaRequirements"]["requiredSlotCount"] is not None for row in rows),
            "knownMediaKindRequirements": sum(row["mediaRequirements"]["requiredMediaKinds"] is not None for row in rows),
            "missingMediaBriefs": sum(row["mediaRequirements"]["missingMediaBrief"] is not None for row in rows),
            "knownTextFieldRequirements": sum(row["textRequirements"]["requiredFieldCount"] is not None for row in rows),
            "knownTypedDataRequirements": sum(row["dataRequirements"]["requiredTypedFields"] is not None for row in rows),
        },
        "evidenceBoundary": {
            "known": [
                "visual intent and semantic constraints",
                "display-eligible identities without assuming one media slot per identity",
                "source-beat encoding categories for unsplit tasks",
                "exact saved audio spans for unsplit tasks",
                "editor-reviewed, measurement-bound audio spans for reviewed split tasks",
            ],
            "unresolved": [
                "treatment-specific media-slot count",
                "task-required media kinds when no typed editor/treatment requirement is bound",
                "single-person versus group eligibility",
                "treatment-specific editable text fields and exact strings",
                "typed data field names and values",
                "exact audio spans for split VisualTasks without an editor-approved measured boundary",
            ],
        },
        "tasks": rows,
    }
    validate_requirements(artifact, verify_sources=False)
    return artifact


def validate_requirements(artifact: dict[str, Any], *, verify_sources: bool = True) -> dict[str, int]:
    if artifact.get("schemaVersion") != 1:
        raise ValueError("unsupported VisualTask requirements schema")
    if artifact.get("activationState") != "review_only_not_connected":
        raise ValueError("VisualTask requirements must remain review-only")
    if artifact.get("selectionAuthorized") is not False or artifact.get("renderingAuthorized") is not False:
        raise ValueError("VisualTask requirements cannot authorize selection or rendering")
    rows = artifact.get("tasks") or []
    ids = [row.get("taskId") for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate VisualTask technical requirement")
    for row in rows:
        media = row.get("mediaRequirements") or {}
        text = row.get("textRequirements") or {}
        data = row.get("dataRequirements") or {}
        timing = row.get("timingRequirement") or {}
        if media.get("requiredSlotCount") is not None:
            raise ValueError("unreviewed task media-slot requirement was populated")
        if media.get("singlePersonGroupEligibility") is not None:
            raise ValueError("unreviewed single-person/group eligibility was populated")
        kinds = media.get("requiredMediaKinds")
        if kinds is not None:
            if media.get("status") not in {"required", "missing_required_media"} or media.get("reviewStatus") not in {"approved", "proposed"}:
                raise ValueError("typed task media constraints lack review state")
            if not isinstance(kinds, list) or not kinds or not (media.get("evidence") or {}).get("reference"):
                raise ValueError("typed task media constraints lack evidence")
        if media.get("status") == "missing_required_media":
            brief = media.get("missingMediaBrief") or {}
            if media.get("availabilityStatus") != "missing" or brief.get("status") != "missing" or brief.get("mediaKind") not in (kinds or []):
                raise ValueError("typed missing-media requirement is incomplete")
        elif media.get("missingMediaBrief") is not None:
            raise ValueError("non-missing task carries a missing-media brief")
        if text.get("requiredFieldCount") is not None or text.get("requiredExactStrings") is not None:
            raise ValueError("unreviewed task text requirement was populated")
        if data.get("requiredTypedFields") is not None:
            raise ValueError("unreviewed typed data requirement was populated")
        if timing.get("status") == "unresolved_split_task_span" and timing.get("exactTaskAudioSpan") is not None:
            raise ValueError("split task claims an exact audio span")
    source_counts = Counter(row.get("sourceBeatId") for row in rows)
    counts = {
        "sourceBeats": len(source_counts),
        "visualTasks": len(rows),
        "exactTaskAudioSpans": sum((row.get("timingRequirement") or {}).get("exactTaskAudioSpan") is not None for row in rows),
        "unresolvedTaskAudioSpans": sum((row.get("timingRequirement") or {}).get("exactTaskAudioSpan") is None for row in rows),
        "knownMediaSlotRequirements": sum((row.get("mediaRequirements") or {}).get("requiredSlotCount") is not None for row in rows),
        "knownMediaKindRequirements": sum((row.get("mediaRequirements") or {}).get("requiredMediaKinds") is not None for row in rows),
        "missingMediaBriefs": sum((row.get("mediaRequirements") or {}).get("missingMediaBrief") is not None for row in rows),
        "knownTextFieldRequirements": sum((row.get("textRequirements") or {}).get("requiredFieldCount") is not None for row in rows),
        "knownTypedDataRequirements": sum((row.get("dataRequirements") or {}).get("requiredTypedFields") is not None for row in rows),
    }
    if counts != artifact.get("counts"):
        raise ValueError(f"VisualTask requirement counts are stale: {counts}")
    if verify_sources:
        for name, source in (artifact.get("sources") or {}).items():
            path = ROOT / source["path"]
            if not path.is_file() or _sha(path) != source["sha256"]:
                raise ValueError(f"VisualTask requirement source is missing or stale: {name}")
        replay = build_requirements(
            tasks_path=ROOT / artifact["sources"]["visualTasks"]["path"],
            slate_path=ROOT / artifact["sources"]["baselineSlate"]["path"],
            timing_reviews_path=ROOT / artifact["sources"]["timingReviews"]["path"],
            media_requirements_path=ROOT / artifact["sources"]["mediaRequirements"]["path"],
        )
        if dumps(replay) != dumps(artifact):
            raise ValueError("VisualTask requirements do not replay from bound inputs")
    return counts


def dumps(artifact: dict[str, Any]) -> str:
    return json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    validate = sub.add_parser("validate")
    validate.add_argument("artifact", type=Path, nargs="?", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.command == "build":
        artifact = build_requirements()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(dumps(artifact), encoding="utf-8")
        print(json.dumps(validate_requirements(artifact), sort_keys=True))
    else:
        print(json.dumps(validate_requirements(_read(args.artifact)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
