#!/usr/bin/env python3
"""Match existing templates and Production Ready media independently per VisualTask."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "match-trial"))
sys.path.insert(0, str(ROOT / "pipeline"))

import candidates as C  # noqa: E402
import media_candidates as M  # noqa: E402

DEFAULT_TASKS = ROOT / "grammar" / "visual-tasks.json"
DEFAULT_BINDINGS = ROOT / "grammar" / "bindings.json"
DEFAULT_OUTPUT = ROOT / "reports" / "visualtask-match-pilot-28-28.json"


def _read(path: Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _source(path: Path) -> dict[str, Any]:
    path = Path(path)
    return {"path": path.resolve().relative_to(ROOT.resolve()).as_posix(), "sha256": _sha(path), "bytes": path.stat().st_size}


def _template_candidates(task: dict[str, Any], bindings: dict[str, Any], pool: dict[str, Any]) -> list[dict[str, Any]]:
    job = task["job"]
    rows = [dict(row) for row in bindings.get(job) or [] if row.get("id") in pool]
    seen = {row["id"] for row in rows}
    for admission in task.get("templateAdmissions") or []:
        template_id = admission.get("id")
        if template_id not in pool:
            raise ValueError(f"task admission references unavailable template: {task['id']}: {template_id}")
        if template_id not in seen:
            rows.insert(0, {"id": template_id, "name": pool[template_id].get("description"), "provenance": admission})
            seen.add(template_id)
    if C.needs_spatial(task.get("entityCount")):
        for record in pool.values():
            if C.is_spatial(record) and record["id"] not in seen:
                rows.append({"id": record["id"], "name": record.get("description"), "provenance": {"source": "spatial-route", "reason": "20+ VisualTask identity demand"}})
                seen.add(record["id"])
    ranked = C.diversify(rows, limit=10, corpus_size=len(pool), pool_index=pool)[0]
    return [{
        "candidateId": row["id"],
        "name": row.get("name") or pool[row["id"]].get("description"),
        "condition": row.get("condition"),
        "bindingProvenance": row.get("provenance"),
        "candidateMatchingProvenance": {
            "scope": "visual_task", "taskId": task["id"], "matchingJob": job,
            "taskRole": task["taskRole"], "quote": task["quote"],
            "displayIdentityCount": len((task.get("entities") or {}).get("displayEligible") or []),
            "perceptibilityConstraints": task.get("mustBePerceptible") or [],
        },
    } for row in ranked]


def _summarize_media(task: dict[str, Any], pool: dict[str, Any]) -> dict[str, Any]:
    entities = list((task.get("entities") or {}).get("displayEligible") or [])
    provenance = {"scope": "visual_task", "taskId": task["id"], "quote": task["quote"]}
    if not entities:
        return {
            "status": "no_entity_media_demand", "entities": [], "groupCandidateIds": [],
            "individualCandidateIds": {}, "gaps": [],
            "candidateMatchingProvenance": {**provenance, "reason": "No display-eligible identities; sibling media is not inherited."},
        }
    resolved = M.resolve(entities, pool=pool, quote=task["quote"])
    return {
        "status": "resolved_with_gaps" if resolved.get("gaps") else "resolved",
        "entities": entities,
        "groupCandidateIds": [row["id"] for row in (resolved.get("group") or [])[:8]],
        "individualCandidateIds": {entity: [row["id"] for row in rows[:8]] for entity, rows in (resolved.get("individual") or {}).items()},
        "gaps": resolved.get("gaps") or [],
        "candidateMatchingProvenance": {**provenance, "identitySource": "VisualTask displayEligible identities", "resolver": "existing Production Ready media_candidates.resolve"},
    }


def build(*, source_beat: str, tasks_path: Path = DEFAULT_TASKS, bindings_path: Path = DEFAULT_BINDINGS) -> dict[str, Any]:
    tasks_artifact = _read(tasks_path)
    if tasks_artifact.get("activationState") != "review_only_not_connected":
        raise ValueError("VisualTask matching input must remain review-only")
    tasks = [row for row in tasks_artifact.get("tasks") or [] if row.get("sourceBeatId") == source_beat]
    if not tasks:
        raise ValueError(f"no VisualTasks for source beat: {source_beat}")
    bindings = _read(bindings_path)
    template_pool = {row["id"]: row for row in C.load()}
    media_pool = M.load()
    rows = [{
        "taskId": task["id"], "sourceBeatId": source_beat, "ordinal": task["ordinal"],
        "taskRole": task["taskRole"], "matchingJob": task["job"], "quote": task["quote"],
        "continuityGroup": task.get("continuityGroup"),
        "templateCandidates": _template_candidates(task, bindings, template_pool),
        "mediaCandidates": _summarize_media(task, media_pool),
    } for task in tasks]
    artifact = {
        "schemaVersion": 1, "purpose": "Review-only independent template and media matching per VisualTask",
        "activationState": "review_only_not_connected", "selectionAuthorized": False,
        "renderingAuthorized": False, "sourceBeatId": source_beat,
        "sources": {"visualTasks": _source(tasks_path), "bindings": _source(bindings_path)}, "tasks": rows,
    }
    validate(artifact, verify_sources=False)
    return artifact


def validate(artifact: dict[str, Any], *, verify_sources: bool = True) -> None:
    if artifact.get("activationState") != "review_only_not_connected":
        raise ValueError("VisualTask matching must remain review-only")
    if artifact.get("selectionAuthorized") is not False or artifact.get("renderingAuthorized") is not False:
        raise ValueError("VisualTask matching cannot authorize selection or rendering")
    rows = artifact.get("tasks") or []
    if len({row.get("taskId") for row in rows}) != len(rows):
        raise ValueError("duplicate matched VisualTask")
    for row in rows:
        for candidate in row.get("templateCandidates") or []:
            provenance = candidate.get("candidateMatchingProvenance") or {}
            if provenance.get("scope") != "visual_task" or provenance.get("taskId") != row.get("taskId"):
                raise ValueError("template candidate lacks VisualTask provenance")
        provenance = (row.get("mediaCandidates") or {}).get("candidateMatchingProvenance") or {}
        if provenance.get("scope") != "visual_task" or provenance.get("taskId") != row.get("taskId"):
            raise ValueError("media result lacks VisualTask provenance")
    if verify_sources:
        for source in (artifact.get("sources") or {}).values():
            path = ROOT / source["path"]
            if not path.is_file() or _sha(path) != source["sha256"]:
                raise ValueError("VisualTask matching source is missing or stale")
        replay = build(source_beat=artifact["sourceBeatId"], tasks_path=ROOT / artifact["sources"]["visualTasks"]["path"], bindings_path=ROOT / artifact["sources"]["bindings"]["path"])
        if dumps(replay) != dumps(artifact):
            raise ValueError("VisualTask matching does not replay from bound inputs")


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-beat", required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        validate(_read(args.output)); print("VisualTask matching passed."); return 0
    artifact = build(source_beat=args.source_beat)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(dumps(artifact), encoding="utf-8")
    print(dumps(artifact), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
