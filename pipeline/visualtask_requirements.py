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


def build_requirements(
    *,
    tasks_path: Path = DEFAULT_TASKS,
    slate_path: Path = DEFAULT_SLATE,
) -> dict[str, Any]:
    paths = {"visualTasks": Path(tasks_path), "baselineSlate": Path(slate_path)}
    task_artifact = _read(paths["visualTasks"])
    if task_artifact.get("activationState") != "review_only_not_connected":
        raise ValueError("VisualTask artifact is not review-only")
    tasks = task_artifact.get("tasks") or []
    slate = _slate_index(_read(paths["baselineSlate"]))
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
            timing = {
                "status": "unresolved_split_task_span",
                "exactTaskAudioSpan": None,
                "sourceBeatSpan": {
                    "startSeconds": baseline["start"],
                    "endSeconds": baseline["end"],
                    "durationSeconds": baseline["duration"],
                },
                "reason": "More than one VisualTask shares this source beat and no exact per-task audio split is saved.",
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
            "mediaRequirements": {
                "status": "unresolved_treatment_dependent",
                "requiredSlotCount": None,
                "requiredMediaKinds": None,
                "singlePersonGroupEligibility": None,
                "reason": "A semantic identity can be encoded by media, text, a mark, or a grouped asset; the current VisualTask does not assign identities to template media slots.",
            },
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
            "knownTextFieldRequirements": sum(row["textRequirements"]["requiredFieldCount"] is not None for row in rows),
            "knownTypedDataRequirements": sum(row["dataRequirements"]["requiredTypedFields"] is not None for row in rows),
        },
        "evidenceBoundary": {
            "known": [
                "visual intent and semantic constraints",
                "display-eligible identities without assuming one media slot per identity",
                "source-beat encoding categories for unsplit tasks",
                "exact saved audio spans for unsplit tasks",
            ],
            "unresolved": [
                "treatment-specific media-slot count",
                "task-required media kinds",
                "single-person versus group eligibility",
                "treatment-specific editable text fields and exact strings",
                "typed data field names and values",
                "exact audio spans for split VisualTasks",
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
        if media.get("requiredMediaKinds") is not None or media.get("singlePersonGroupEligibility") is not None:
            raise ValueError("unreviewed task media constraints were populated")
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
