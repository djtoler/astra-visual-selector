#!/usr/bin/env python3
"""Build source-bound technical capacities for exact native clip windows."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ae_template_technical_specs.derive_capacity import build_capacity, measure_composition_window


ROOT = Path(__file__).resolve().parents[1]
POLISH_ROOT = ROOT.parent
DEFAULT_DEFINITIONS = ROOT / "grammar/ae-scene-window-definitions.json"
DEFAULT_INDEX = ROOT / "grammar/ae-template-technical-index.json"
DEFAULT_RAW_DIR = POLISH_ROOT / "ae-template-capacity-lab/runs/2026-09-29-registry-gap-v1/native-batch/raw"
DEFAULT_OUTPUT = ROOT / "grammar/ae-scene-window-technical-capacities.json"


def _read(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _source(path: Path) -> dict[str, Any]:
    path = Path(path)
    try:
        logical = path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        try:
            logical = "../" + path.resolve().relative_to(POLISH_ROOT.resolve()).as_posix()
        except ValueError:
            logical = path.name
    return {"path": logical, "sha256": _sha(path), "bytes": path.stat().st_size}


def build_window_capacities(
    *,
    definitions_path: Path = DEFAULT_DEFINITIONS,
    technical_index_path: Path = DEFAULT_INDEX,
    raw_dir: Path = DEFAULT_RAW_DIR,
) -> dict[str, Any]:
    definitions_path = Path(definitions_path)
    technical_index_path = Path(technical_index_path)
    raw_dir = Path(raw_dir)
    definitions = _read(definitions_path)
    if definitions.get("schemaVersion") != 1 or definitions.get("activationState") != "inspection_only":
        raise ValueError("unsupported or active scene-window definitions")
    technical = _read(technical_index_path)
    projects = {row["id"]: row for row in technical["projects"]}
    seen: set[str] = set()
    capacity_cache: dict[str, dict] = {}
    raw_sources: dict[str, dict] = {}
    records = []
    raw_report_overrides = definitions.get("rawReportOverrides") or {}
    for definition in definitions.get("windows") or []:
        scene_id = definition["sceneId"]
        if scene_id in seen:
            raise ValueError(f"duplicate scene window: {scene_id}")
        seen.add(scene_id)
        project_id = definition["projectId"]
        if project_id not in projects:
            raise ValueError(f"unknown measured project: {project_id}")
        raw_project_id = definition.get("nativeReportProjectId", project_id)
        override = raw_report_overrides.get(project_id)
        raw_path = Path(override) if override else raw_dir / f"{raw_project_id}.json"
        if not raw_path.is_absolute():
            raw_path = ROOT / raw_path
        if raw_project_id not in capacity_cache:
            raw = _read(raw_path)
            if raw.get("sourceSha256") != projects[project_id]["sourceProjectSha256"]:
                raise ValueError(f"native report source hash mismatch: {scene_id}")
            capacity_cache[raw_project_id] = build_capacity(raw)
            raw_sources[raw_project_id] = _source(raw_path)
        measured = measure_composition_window(
            capacity_cache[raw_project_id],
            composition_id=definition["compositionId"],
            start_seconds=definition["startSeconds"],
            end_seconds=definition["endSeconds"],
        )
        if measured["compositionPath"] != definition["compositionPath"]:
            raise ValueError(f"window composition id/path mismatch: {scene_id}")
        records.append({
            "sceneId": scene_id,
            "projectId": project_id,
            "sourceProjectSha256": projects[project_id]["sourceProjectSha256"],
            "boundaryBasis": "reviewed_clip_window_on_directly_aligned_native_timeline",
            "evidence": definition["evidence"],
            "capacity": measured,
        })
    records.sort(key=lambda row: row["sceneId"])
    return {
        "schemaVersion": 1,
        "purpose": "Exact technical capacity inside reviewed native composition windows",
        "activationState": "inspection_only",
        "renderingPerformed": False,
        "measurementBoundary": {
            "simultaneouslyEnabled": "Counts AE layers enabled with overlapping in/out intervals inside the clip window.",
            "notMeasured": "Simultaneous visual visibility through animated opacity, masks, effects, expressions, or time-remap keyframe values is not claimed by this artifact."
        },
        "sources": {
            "definitions": _source(definitions_path),
            "technicalIndex": _source(technical_index_path),
            "nativeReports": {key: raw_sources[key] for key in sorted(raw_sources)},
        },
        "counts": {"windows": len(records)},
        "windows": records,
    }


def validate_window_capacities(
    artifact: dict,
    *,
    verify_native_reports: bool = False,
    definitions_path: Path = DEFAULT_DEFINITIONS,
    technical_index_path: Path = DEFAULT_INDEX,
    raw_dir: Path = DEFAULT_RAW_DIR,
) -> dict[str, int]:
    if artifact.get("schemaVersion") != 1 or artifact.get("activationState") != "inspection_only":
        raise ValueError("unsupported or active scene-window capacity artifact")
    if artifact.get("renderingPerformed") is not False:
        raise ValueError("scene-window capacity must be inspection-only")
    rows = artifact.get("windows") or []
    ids = [row.get("sceneId") for row in rows]
    if ids != sorted(ids) or len(ids) != len(set(ids)):
        raise ValueError("scene-window capacity IDs are duplicate or unsorted")
    definitions_path = Path(definitions_path)
    technical_index_path = Path(technical_index_path)
    sources = artifact.get("sources") or {}
    if sources.get("definitions", {}).get("sha256") != _sha(definitions_path):
        raise ValueError("scene-window definitions source is stale")
    if sources.get("technicalIndex", {}).get("sha256") != _sha(technical_index_path):
        raise ValueError("scene-window technical index source is stale")
    definitions = _read(definitions_path)
    expected_ids = sorted(row["sceneId"] for row in definitions.get("windows") or [])
    if ids != expected_ids or artifact.get("counts") != {"windows": len(rows)}:
        raise ValueError("scene-window capacity scope is stale")
    projects = {row["id"]: row for row in _read(technical_index_path)["projects"]}
    for row in rows:
        if row.get("projectId") not in projects:
            raise ValueError(f"unknown scene-window project: {row.get('sceneId')}")
        if row.get("sourceProjectSha256") != projects[row["projectId"]]["sourceProjectSha256"]:
            raise ValueError(f"scene-window project source is stale: {row.get('sceneId')}")
        capacity = row.get("capacity") or {}
        window = capacity.get("window") or {}
        if window.get("precision") != "exact" or float(window.get("endSeconds", 0)) <= float(window.get("startSeconds", 0)):
            raise ValueError(f"invalid exact scene window: {row.get('sceneId')}")
    if verify_native_reports:
        expected = build_window_capacities(
            definitions_path=definitions_path,
            technical_index_path=technical_index_path,
            raw_dir=raw_dir,
        )
        if artifact != expected:
            raise ValueError("scene-window capacity artifact is stale")
    return artifact["counts"]


def write_window_capacities(path: Path = DEFAULT_OUTPUT, **build_kwargs: Any) -> dict:
    artifact = build_window_capacities(**build_kwargs)
    Path(path).write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n")
    return artifact


if __name__ == "__main__":
    write_window_capacities()
