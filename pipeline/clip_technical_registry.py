"""Validate clip-level joins between semantic preview scenes and native AE capacity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TECHNICAL_INDEX = ROOT / "grammar" / "ae-template-technical-index.json"
PILOT = ROOT / "reports" / "carousel-slideshow-clip-native-pilot.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_registry(registry: dict, *, technical_index_path: Path = TECHNICAL_INDEX) -> dict:
    if registry.get("schemaVersion") != 1:
        raise ValueError("unsupported clip technical registry schema")
    if registry.get("activationState") != "pilot_review_only":
        raise ValueError("pilot registry must remain review-only")

    source = registry.get("sources", {}).get("technicalIndex", {})
    technical_index_path = Path(technical_index_path)
    if source.get("sha256") != _sha256(technical_index_path):
        raise ValueError("technical index source is missing or stale")
    index = json.loads(technical_index_path.read_text())
    projects = {project["id"]: project for project in index["projects"]}

    expected_ids = registry.get("scope", {}).get("expectedClipIds", [])
    records = registry.get("clips", [])
    ids = [record.get("clipId") for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate clip id")
    if set(ids) != set(expected_ids):
        raise ValueError("clip coverage mismatch")

    approximate = 0
    verified_compositions = 0
    for record in records:
        project_id = record.get("native", {}).get("projectId")
        if project_id not in projects:
            raise ValueError(f"unknown technical project: {project_id}")
        composition = record["native"].get("composition", {})
        measured = [
            row
            for row in projects[project_id]["compositions"]
            if row["id"] == composition.get("id") and row["path"] == composition.get("path")
        ]
        if len(measured) != 1:
            raise ValueError(f"composition id/path mismatch: {record['clipId']}")
        measured = measured[0]
        verified_compositions += 1

        capacity = record.get("technicalCapacity", {})
        expected_capacity = {
            "compositionDurationSeconds": measured["durationSeconds"],
            "absoluteMediaSlots": measured["totalIndependentVisualMediaInputs"],
            "maxSimultaneouslyEnabledInputs": measured[
                "maxSimultaneouslyEnabledRecursiveVisualInputs"
            ],
            "editableTextFields": measured["recursiveEditableTextFields"],
        }
        if capacity != expected_capacity:
            raise ValueError(f"technical capacity differs from measured composition: {record['clipId']}")

        status = record.get("mappingStatus")
        if status not in {"verified", "composition_verified_window_approximate", "unresolved"}:
            raise ValueError(f"invalid mapping status: {record['clipId']}")
        window = record.get("native", {}).get("window")
        if status == "composition_verified_window_approximate":
            approximate += 1
            if not isinstance(window, dict) or window.get("precision") != "approximate":
                raise ValueError(f"approximate mapping requires an approximate window: {record['clipId']}")
        if status == "verified" and window and window.get("precision") != "exact":
            raise ValueError(f"verified mapping requires an exact window: {record['clipId']}")
        if window:
            start = float(window["startSeconds"])
            end = float(window["endSeconds"])
            if start < 0 or end <= start or end > measured["durationSeconds"] + 1e-6:
                raise ValueError(f"native window is outside the composition: {record['clipId']}")
            preview_duration = float(record["semantic"]["previewDurationSeconds"])
            if abs((end - start) - preview_duration) > (1 / 25 + 1e-6):
                raise ValueError(f"preview/native window duration mismatch: {record['clipId']}")

        if record.get("windowSlotExposureStatus") not in {"verified", "unresolved"}:
            raise ValueError(f"window slot exposure status is required: {record['clipId']}")

    render_evidence = registry.get("sources", {}).get("nativeRenderEvidence", [])
    render_paths = [row.get("compositionPath") for row in render_evidence]
    used_compositions = {row["native"]["composition"]["path"] for row in records}
    if len(render_paths) != len(set(render_paths)) or set(render_paths) != used_compositions:
        raise ValueError("native render evidence does not cover each mapped composition exactly once")
    for row in render_evidence:
        if row.get("decodeVerified") is not True:
            raise ValueError(f"native render decode is unverified: {row.get('compositionPath')}")
        if int(row["frames"]) != round(float(row["durationSeconds"]) * float(row["fps"])):
            raise ValueError(f"native render frame math is inconsistent: {row.get('compositionPath')}")
        if not isinstance(row.get("sha256"), str) or len(row["sha256"]) != 64:
            raise ValueError(f"native render hash is missing: {row.get('compositionPath')}")

    counts = registry.get("counts", {})
    actual = {
        "clips": len(records),
        "compositionVerified": verified_compositions,
        "approximateWindows": approximate,
        "windowSlotExposureUnresolved": sum(
            row["windowSlotExposureStatus"] == "unresolved" for row in records
        ),
        "nativeRenders": len(render_evidence),
    }
    if counts != actual:
        raise ValueError("registry counts are stale")
    return actual


def load_and_validate(path: Path = PILOT) -> dict:
    registry = json.loads(Path(path).read_text())
    validate_registry(registry)
    return registry
