#!/usr/bin/env python3
"""Build and validate the derived VisualTask pilot.

This module does not change the existing beat, selection, media, or pairing
artifacts. It gives those stages a reviewable future input without silently
turning it on.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from . import entities as entity_extractor


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BEATS = ROOT / "pipeline" / "beats-all.json"
DEFAULT_TIMING = ROOT / "narration" / "year-seventeen-narration-timing.json"
DEFAULT_ROSTER = ROOT / "grammar" / "entity-roster.json"
DEFAULT_OVERRIDES = ROOT / "grammar" / "visual-task-overrides.json"
DEFAULT_COHORTS = ROOT / "grammar" / "cohorts.json"
DEFAULT_OUTPUT = ROOT / "grammar" / "visual-tasks.json"
JOBS = {
    "one_vs_aggregate", "one_vs_many_individually", "entity_vs_benchmark",
    "proportion_of_cohort", "parallel_instances", "change_across_set",
    "members_then_total", "category_breakdown", "inversion",
    "intersection_of_sets", "streak_over_time", "equivalence_restatement",
    "derived_quantity", "locate_in_distribution", "explain_the_encoding",
    "pose_a_question", "enumerate", "define_terms", "narrate_an_event",
    "assert_without_data", "unclassified",
}


def _read(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _logical(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    return [value for value in values if not (value in seen or seen.add(value))]


def _source_beats(raw: dict[str, list[dict[str, Any]]]) -> list[tuple[str, str, dict[str, Any]]]:
    out: list[tuple[str, str, dict[str, Any]]] = []
    ids: set[str] = set()
    for passage_id, rows in raw.items():
        for beat in rows:
            source_id = f"{passage_id}-{beat['id']}"
            if source_id in ids:
                raise ValueError(f"duplicate source beat id: {source_id}")
            ids.add(source_id)
            out.append((passage_id, source_id, beat))
    return out


def _cohort_index(raw: dict[str, Any], roster: set[str]) -> dict[tuple[str, str], dict[str, Any]]:
    if raw.get("schemaVersion") != 1:
        raise ValueError("unsupported cohort schema")
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for row in raw.get("cohorts", []):
        key = (row.get("id"), row.get("version"))
        if not all(key) or key in out:
            raise ValueError(f"invalid or duplicate cohort version: {key}")
        members = row.get("members") or []
        if len(members) != len(set(members)):
            raise ValueError(f"duplicate cohort member: {key}")
        unknown = sorted(set(members) - roster)
        if unknown:
            raise ValueError(f"unknown roster entity in cohort {key}: {unknown}")
        out[key] = row
    return out


def _verify_cohort_sources(cohorts: dict[tuple[str, str], dict[str, Any]]) -> None:
    for key, row in cohorts.items():
        source = row.get("source") or {}
        raw_path = source.get("path")
        if not raw_path:
            raise ValueError(f"cohort has no source path: {key}")
        path = Path(raw_path)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            raise ValueError(f"cohort source missing: {path}")
        expected = source.get("sha256")
        if expected and _sha(path) != expected:
            raise ValueError(f"cohort source hash changed: {key}")


def _exact_span(full: str, part: str, source_id: str) -> dict[str, int]:
    if not part or full.count(part) != 1:
        raise ValueError(f"override quote must be one exact substring of {source_id}")
    start = full.index(part)
    return {"start": start, "end": start + len(part)}


def _validate_coverage(full: str, tasks: list[dict[str, Any]], source_id: str) -> None:
    spans = sorted((row["sourceSpan"]["start"], row["sourceSpan"]["end"]) for row in tasks)
    last = 0
    for start, end in spans:
        if start < last:
            raise ValueError(f"overlapping task spans for {source_id}")
        if full[last:start].strip():
            raise ValueError(f"task split loses source text for {source_id}")
        last = end
    if full[last:].strip():
        raise ValueError(f"task split loses source text for {source_id}")


def _task(
    *,
    passage_id: str,
    source_id: str,
    beat: dict[str, Any],
    spec: dict[str, Any],
    roster_names: list[str],
    roster: set[str],
    cohorts: dict[tuple[str, str], dict[str, Any]],
    passage_timing: dict[str, Any],
) -> dict[str, Any]:
    quote = spec.get("quote", beat["quote"])
    span = _exact_span(beat["quote"], quote, source_id)
    suffix = spec.get("suffix", "main")
    task_id = f"{source_id}.{suffix}"
    matching_job = spec.get("matchingJob", beat["job"])
    if matching_job not in JOBS:
        raise ValueError(f"invalid matching job in {task_id}: {matching_job}")
    extracted = entity_extractor.extract(quote + " " + (beat.get("entity_kind") or ""), roster_names)
    explicit = list(extracted["entities"])

    implied: list[dict[str, Any]] = []
    for row in spec.get("impliedEntities", []):
        entity = row.get("entity")
        if entity not in roster:
            raise ValueError(f"unknown roster entity in {task_id}: {entity}")
        if row.get("displayPolicy") not in {"eligible", "withheld"}:
            raise ValueError(f"invalid implied-entity display policy in {task_id}")
        if not (row.get("evidence") or {}).get("reference"):
            raise ValueError(f"implied entity lacks evidence in {task_id}")
        implied.append(row)

    cohort_rows: list[dict[str, Any]] = []
    cohort_members: list[str] = []
    display_cohort_members: list[str] = []
    for ref in spec.get("cohortRefs", []):
        key = (ref.get("id"), ref.get("version"))
        if key not in cohorts:
            raise ValueError(f"unknown cohort version in {task_id}: {key}")
        policy = ref.get("displayPolicy", "eligible")
        if policy not in {"eligible", "withheld"}:
            raise ValueError(f"invalid cohort display policy in {task_id}")
        cohort = cohorts[key]
        members = cohort["members"]
        cohort_members.extend(members)
        if policy == "eligible":
            display_cohort_members.extend(members)
        cohort_rows.append({
            "id": cohort["id"],
            "version": cohort["version"],
            "label": cohort["label"],
            "memberCount": len(members),
            "displayPolicy": policy,
            "source": cohort["source"],
        })

    resolved = _unique(explicit + [row["entity"] for row in implied] + cohort_members)
    display = _unique(
        explicit
        + [row["entity"] for row in implied if row["displayPolicy"] == "eligible"]
        + display_cohort_members
    )
    unresolved = list(spec.get("unresolved", []))
    entity_count = spec.get("entityCount", beat.get("entity_count"))
    identity_count = spec.get("identityCount", len(explicit))
    if not isinstance(identity_count, int) or identity_count < 0:
        raise ValueError(f"invalid identity count in {task_id}")
    if identity_count > len(resolved):
        unresolved.append({
            "kind": "identity_count_not_fully_resolved",
            "expected": identity_count,
            "resolved": len(resolved),
            "reason": "This task requires more depicted identities than it resolves to stable roster entities.",
        })

    return {
        "id": task_id,
        "sourceBeatId": source_id,
        "passageId": passage_id,
        "ordinal": 0,
        "taskRole": spec.get("taskRole", "main"),
        "quote": quote,
        "sourceSpan": span,
        "job": matching_job,
        "sourceBeatJob": beat["job"],
        "entityCount": entity_count,
        "identityCount": identity_count,
        "entityKind": beat.get("entity_kind"),
        "takeaway": beat.get("takeaway"),
        "mustBeTrue": spec.get("mustBeTrue", beat.get("must_be_true", [])),
        "mustBePerceptible": spec.get("mustBePerceptible", beat.get("must_be_perceptible", [])),
        "wouldBeALie": spec.get("wouldBeALie", beat.get("would_be_a_lie", [])),
        "unstated": spec.get("unstated", beat.get("unstated", [])),
        "continuityGroup": spec.get("continuityGroup"),
        "templateAdmissions": list(spec.get("templateAdmissions") or []),
        "timing": {
            "status": "passage_bounds_only",
            "passageStartSeconds": passage_timing["startSeconds"],
            "passageEndSeconds": passage_timing["endSeconds"],
            "exactTaskAudioSpan": None,
        },
        "entities": {
            "explicit": explicit,
            "implied": implied,
            "cohorts": cohort_rows,
            "resolved": resolved,
            "displayEligible": display,
            "ambiguous": extracted["ambiguous"],
            "unknownNames": extracted["unknown"],
            "unresolved": unresolved,
        },
    }


def build_visual_tasks(
    *,
    beats_path: Path = DEFAULT_BEATS,
    timing_path: Path = DEFAULT_TIMING,
    roster_path: Path = DEFAULT_ROSTER,
    overrides_path: Path = DEFAULT_OVERRIDES,
    cohorts_path: Path = DEFAULT_COHORTS,
) -> dict[str, Any]:
    paths = {
        "beats": Path(beats_path),
        "timing": Path(timing_path),
        "roster": Path(roster_path),
        "overrides": Path(overrides_path),
        "cohorts": Path(cohorts_path),
    }
    beats_raw = _read(paths["beats"])
    timing_raw = _read(paths["timing"])
    roster_raw = _read(paths["roster"])
    overrides_raw = _read(paths["overrides"])
    cohorts_raw = _read(paths["cohorts"])
    roster_names = list(roster_raw["names"])
    roster = set(roster_names)
    cohorts = _cohort_index(cohorts_raw, roster)
    _verify_cohort_sources(cohorts)
    if overrides_raw.get("schemaVersion") != 1:
        raise ValueError("unsupported override schema")

    source_rows = _source_beats(beats_raw)
    source_ids = {source_id for _, source_id, _ in source_rows}
    overrides = overrides_raw.get("beats", {})
    unknown_overrides = sorted(set(overrides) - source_ids)
    if unknown_overrides:
        raise ValueError(f"overrides reference unknown beats: {unknown_overrides}")
    timing = {row["passageId"]: row for row in timing_raw["passages"]}

    tasks: list[dict[str, Any]] = []
    for passage_id, source_id, beat in source_rows:
        if passage_id not in timing:
            raise ValueError(f"missing passage timing: {passage_id}")
        specs = (overrides.get(source_id) or {}).get("tasks") or [{}]
        if not specs:
            raise ValueError(f"empty task override: {source_id}")
        if len(specs) > 1:
            review = (overrides.get(source_id) or {}).get("splitReview") or {}
            if review.get("status") != "approved" or not review.get("source"):
                raise ValueError(f"split task override lacks editor approval: {source_id}")
            if any(not spec.get("matchingJob") for spec in specs):
                raise ValueError(f"split task override lacks a per-task matching job: {source_id}")
        beat_tasks = [
            _task(
                passage_id=passage_id,
                source_id=source_id,
                beat=beat,
                spec=spec,
                roster_names=roster_names,
                roster=roster,
                cohorts=cohorts,
                passage_timing=timing[passage_id],
            )
            for spec in specs
        ]
        _validate_coverage(beat["quote"], beat_tasks, source_id)
        for ordinal, row in enumerate(beat_tasks, 1):
            row["ordinal"] = ordinal
            tasks.append(row)

    task_ids = [row["id"] for row in tasks]
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("duplicate task id")
    task_counts = Counter(row["sourceBeatId"] for row in tasks)
    issues = [
        {"taskId": row["id"], "unresolved": row["entities"]["unresolved"]}
        for row in tasks if row["entities"]["unresolved"]
    ]
    artifact = {
        "schemaVersion": 1,
        "purpose": "Derived VisualTask pilot; not yet consumed by slate, media or pairing stages",
        "activationState": "review_only_not_connected",
        "sources": {
            name: {"path": _logical(path), "sha256": _sha(path)}
            for name, path in paths.items()
        },
        "counts": {
            "sourceBeats": len(source_rows),
            "visualTasks": len(tasks),
            "splitBeats": sum(1 for count in task_counts.values() if count > 1),
            "impliedEntityTasks": sum(bool(row["entities"]["implied"]) for row in tasks),
            "cohortTasks": sum(bool(row["entities"]["cohorts"]) for row in tasks),
            "unresolvedTasks": len(issues),
        },
        "tasks": tasks,
        "issues": issues,
    }
    consume_visual_tasks(artifact, verify_sources=False)
    return artifact


def _resolve_source_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def consume_visual_tasks(artifact: dict[str, Any], *, verify_sources: bool = True) -> dict[str, int]:
    if artifact.get("schemaVersion") != 1:
        raise ValueError("unsupported VisualTask schema")
    tasks = artifact.get("tasks") or []
    ids = [row.get("id") for row in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate task id")
    if any(not row.get("sourceBeatId") or not row.get("quote") for row in tasks):
        raise ValueError("task missing source identity or quote")
    if verify_sources:
        for name, source in (artifact.get("sources") or {}).items():
            path = _resolve_source_path(source["path"])
            if not path.exists() or _sha(path) != source["sha256"]:
                raise ValueError(f"source is missing or stale: {name}")
    counts = Counter(row["sourceBeatId"] for row in tasks)
    status = {
        "sourceBeats": len(counts),
        "visualTasks": len(tasks),
        "splitBeats": sum(1 for count in counts.values() if count > 1),
        "impliedEntityTasks": sum(bool(row["entities"]["implied"]) for row in tasks),
        "cohortTasks": sum(bool(row["entities"]["cohorts"]) for row in tasks),
        "unresolvedTasks": sum(bool(row["entities"]["unresolved"]) for row in tasks),
    }
    if status != artifact.get("counts"):
        raise ValueError(f"artifact counts are stale: expected {status}, found {artifact.get('counts')}")
    if verify_sources:
        source_paths = {
            name: _resolve_source_path(source["path"])
            for name, source in artifact["sources"].items()
        }
        replay = build_visual_tasks(
            beats_path=source_paths["beats"],
            timing_path=source_paths["timing"],
            roster_path=source_paths["roster"],
            overrides_path=source_paths["overrides"],
            cohorts_path=source_paths["cohorts"],
        )
        if dumps(replay) != dumps(artifact):
            raise ValueError("artifact content does not replay from its bound sources")
    return status


def dumps(artifact: dict[str, Any]) -> str:
    return json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def write_visual_tasks(path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    artifact = build_visual_tasks()
    path = Path(path)
    path.write_text(dumps(artifact), encoding="utf-8")
    consume_visual_tasks(_read(path))
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    validate = sub.add_parser("validate")
    validate.add_argument("artifact", type=Path, nargs="?", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.command == "build":
        artifact = write_visual_tasks(args.output)
        print(json.dumps(consume_visual_tasks(artifact, verify_sources=False), sort_keys=True))
    else:
        print(json.dumps(consume_visual_tasks(_read(args.artifact)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
