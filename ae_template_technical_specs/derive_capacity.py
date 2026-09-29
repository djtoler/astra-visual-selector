#!/usr/bin/env python3
"""Derive source-bound per-composition capacity from a native AE report.

This does not guess that every footage layer is an editable slot. It counts
explicit placeholder compositions, explicitly named edit-media compositions,
and placeholder footage. Other media-bearing sources remain unresolved
candidates for the later accuracy pass.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re


STRONG_SLOT = re.compile(r"(?:^|[\s_\-/])(placeholder|replace)(?:$|[\s_\-/0-9])", re.I)
EDIT_IMAGE_SLOT = re.compile(r"^image\s+(?:(?:square|vertical|wide)\s+)?\d+$", re.I)
EDIT_PHOTO_SLOT = re.compile(r"^photo\s+\d+$", re.I)
EDIT_PREFIXED_MEDIA_SLOT = re.compile(r"^(?:f|fl|or|s)_media_\d+$", re.I)
EDIT_NUMBERED_MEDIA_SLOT = re.compile(r"^(?:background\s+)?media\s*\d+(?:\.\d+)?$", re.I)
AUDIO_HINT = re.compile(r"audio|music|sound|song|beat|sfx|voice", re.I)


def explicit_edit_slot_evidence(path: str) -> str | None:
    """Recognize native replacement comps whose naming is explicit but legacy.

    These are intentionally narrow conventions observed in the source projects.
    Generic comps such as ``Media 01`` or ordinary footage are not admitted.
    """
    normalized = path.replace("\\", "/")
    leaf = normalized.rsplit("/", 1)[-1]
    lowered = normalized.lower()
    if EDIT_IMAGE_SLOT.fullmatch(leaf) and (
        "edit/image/" in lowered
        or re.search(r"(?:^|/)\d*\.?\s*edit/image/", lowered)
        or "other/footage/" in lowered
    ):
        return "explicit_edit_image_composition"
    if EDIT_PHOTO_SLOT.fullmatch(leaf) and "edit/" in lowered and (
        "photo/" in lowered
        or re.search(r"(?:^|/)\d*\.?\s*edit/scene\s+\d+/photo\s+\d+$", lowered)
    ):
        return "explicit_edit_photo_composition"
    if EDIT_PREFIXED_MEDIA_SLOT.fullmatch(leaf) and "edit comps/media/" in lowered:
        return "explicit_edit_media_composition"
    if EDIT_NUMBERED_MEDIA_SLOT.fullmatch(leaf) and (
        "/edit media/" in lowered
        or re.search(r"(?:^|/)edit/scene\s+\d+/edit/media\s+", lowered)
        or re.search(r"(?:^|/)\d*\.?edit comps/scene\s+\d+/media\s+", lowered)
    ):
        return "explicit_legacy_edit_media_composition"
    if leaf.lower() == "your logo" and "edit/" in lowered and "logo/" in lowered:
        return "explicit_edit_logo_composition"
    return None


def layer_interval(layer: dict, duration: float) -> tuple[float, float] | None:
    start = max(0.0, float(layer.get("inPoint", 0.0)))
    end = min(float(duration), float(layer.get("outPoint", duration)))
    return (start, end) if end > start else None


def transform_interval(interval: tuple[float, float], layer: dict, duration: float) -> tuple[float, float] | None:
    stretch = float(layer.get("stretch") or 100.0) / 100.0
    if stretch == 0:
        return None
    start_time = float(layer.get("startTime") or 0.0)
    a = start_time + interval[0] * stretch
    b = start_time + interval[1] * stretch
    mapped = (min(a, b), max(a, b))
    bounds = layer_interval(layer, duration)
    if not bounds:
        return None
    start = max(mapped[0], bounds[0])
    end = min(mapped[1], bounds[1])
    return (start, end) if end > start else None


def max_active(intervals_by_id: dict[str, list[tuple[float, float]]]) -> int:
    raw_boundaries = sorted(
        {point for intervals in intervals_by_id.values() for interval in intervals for point in interval}
    )
    boundaries: list[float] = []
    for point in raw_boundaries:
        if boundaries and math.isclose(point, boundaries[-1], rel_tol=1e-10, abs_tol=1e-10):
            continue
        boundaries.append(point)
    if len(boundaries) < 2:
        return 0
    maximum = 0
    for start, end in zip(boundaries, boundaries[1:]):
        if end <= start:
            continue
        instant = (start + end) / 2.0
        active = sum(any(a <= instant < b for a, b in intervals) for intervals in intervals_by_id.values())
        maximum = max(maximum, active)
    return maximum


def _clip_intervals(
    intervals_by_id: dict[str, list[tuple[float, float]]],
    start: float,
    end: float,
) -> dict[str, list[tuple[float, float]]]:
    clipped: dict[str, list[tuple[float, float]]] = {}
    for item_id, intervals in intervals_by_id.items():
        rows = []
        for interval_start, interval_end in intervals:
            clipped_start = max(float(interval_start), start)
            clipped_end = min(float(interval_end), end)
            if clipped_end > clipped_start:
                rows.append((clipped_start, clipped_end))
        if rows:
            clipped[item_id] = rows
    return clipped


def measure_composition_window(
    capacity: dict,
    *,
    composition_id: int,
    start_seconds: float,
    end_seconds: float,
) -> dict:
    """Measure media and text exposure inside one exact native-comp window."""
    matches = [
        row for row in capacity.get("compositions", [])
        if int(row["compositionId"]) == int(composition_id)
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one measured composition: {composition_id}")
    comp = matches[0]
    start = float(start_seconds)
    end = float(end_seconds)
    duration = float(comp["durationSeconds"])
    if start < 0 or end <= start or end > duration + 1e-8:
        raise ValueError("window is outside the measured composition")

    slot_intervals = {
        row["id"]: [tuple(interval) for interval in row.get("activationIntervals", [])]
        for row in comp.get("recursiveVisualMediaInputs", [])
    }
    text_intervals = {
        row["id"]: [tuple(interval) for interval in row.get("activationIntervals", [])]
        for row in comp.get("recursiveEditableTextFields", [])
    }
    clipped_slots = _clip_intervals(slot_intervals, start, end)
    clipped_texts = _clip_intervals(text_intervals, start, end)
    slots_by_id = {row["id"]: row for row in comp.get("recursiveVisualMediaInputs", [])}
    texts_by_id = {row["id"]: row for row in comp.get("recursiveEditableTextFields", [])}

    def without_intervals(row: dict) -> dict:
        return {key: value for key, value in row.items() if key != "activationIntervals"}

    return {
        "compositionId": int(comp["compositionId"]),
        "compositionPath": comp["compositionPath"],
        "window": {
            "startSeconds": start,
            "endSeconds": end,
            "durationSeconds": end - start,
            "precision": "exact",
        },
        "totalIndependentVisualMediaInputs": len(clipped_slots),
        "maxSimultaneouslyEnabledRecursiveVisualInputs": max_active(clipped_slots),
        "recursiveVisualMediaInputs": [
            without_intervals(slots_by_id[item_id]) for item_id in sorted(clipped_slots)
        ],
        "recursiveEditableTextFields": [
            without_intervals(texts_by_id[item_id]) for item_id in sorted(clipped_texts)
        ],
        "maxSimultaneouslyEnabledRecursiveTextFields": max_active(clipped_texts),
        "unresolvedCount": len(comp.get("unresolved", [])),
    }


def build_capacity(report: dict) -> dict:
    if not report.get("ok"):
        raise ValueError("Native report is not successful")
    compositions = {int(comp["id"]): comp for comp in report.get("compositions", [])}
    items = {int(item["id"]): item for item in report.get("items", [])}
    compositions_by_name: dict[str, list[dict]] = defaultdict(list)
    for comp in compositions.values():
        compositions_by_name[comp.get("name") or comp["path"].rsplit("/", 1)[-1]].append(comp)

    def legacy_source_comp(parent: dict, source_name: str | None) -> dict | None:
        if not source_name:
            return None
        candidates = compositions_by_name.get(source_name, [])
        if len(candidates) == 1:
            return candidates[0]
        parent_root = parent["path"].split("/", 1)[0]
        same_root = [candidate for candidate in candidates if candidate["path"].split("/", 1)[0] == parent_root]
        return same_root[0] if len(same_root) == 1 else None

    slots: dict[str, dict] = {}
    unresolved_sources: dict[str, dict] = {}
    for comp in compositions.values():
        edit_slot_evidence = explicit_edit_slot_evidence(comp["path"])
        if STRONG_SLOT.search(comp["path"]) or edit_slot_evidence:
            slot_id = f"comp:{comp['id']}"
            slots[slot_id] = {
                "id": slot_id,
                "kind": "visual",
                "projectItemId": comp["id"],
                "path": comp["path"],
                "evidence": edit_slot_evidence or "explicit_placeholder_composition",
            }
    for item in items.values():
        if item.get("itemType") != "FootageItem" or item.get("sourceType") == "SolidSource":
            continue
        slot_id = f"footage:{item['id']}"
        text = f"{item.get('path', '')} {item.get('name', '')}"
        kind = "audio" if AUDIO_HINT.search(text) or (item.get("hasAudio") and not item.get("hasVideo")) else "visual"
        row = {
            "id": slot_id,
            "kind": kind,
            "projectItemId": item["id"],
            "path": item.get("path"),
            "sourceType": item.get("sourceType"),
            "missing": item.get("missing"),
        }
        if item.get("sourceType") == "PlaceholderSource" or STRONG_SLOT.search(text):
            row["evidence"] = "native_placeholder_footage"
            slots[slot_id] = row
        else:
            row["reason"] = "file_footage_is_not_proof_of_an_independent_replacement_slot"
            unresolved_sources[slot_id] = row

    text_fields: dict[str, dict] = {}
    for comp in compositions.values():
        for layer in comp.get("layers", []):
            if "textField" not in layer and "text" not in layer:
                continue
            field_id = f"text:{comp['id']}:{layer['index']}"
            text_state = layer.get("textField") or {"text": layer.get("text")}
            text_fields[field_id] = {
                "id": field_id,
                "compositionId": comp["id"],
                "compositionPath": comp["path"],
                "layerIndex": layer["index"],
                "layerName": layer["name"],
                "enabled": bool(layer.get("enabled")),
                "inPoint": layer.get("inPoint"),
                "outPoint": layer.get("outPoint"),
                "text": text_state.get("text"),
                "textKind": text_state.get("textKind"),
                "font": text_state.get("font"),
                "fontSize": text_state.get("fontSize"),
                "boxTextSize": text_state.get("boxTextSize"),
                "sourceText": layer.get("sourceText"),
                "metadataComplete": "textField" in layer,
            }

    memo: dict[int, dict] = {}
    resolving: set[int] = set()

    def resolve(comp_id: int) -> dict:
        if comp_id in memo:
            return memo[comp_id]
        if comp_id in resolving:
            return {"slots": {}, "texts": {}, "unresolved": ["composition_cycle"]}
        resolving.add(comp_id)
        comp = compositions[comp_id]
        duration = float(comp["duration"])
        slot_intervals: dict[str, list[tuple[float, float]]] = defaultdict(list)
        text_intervals: dict[str, list[tuple[float, float]]] = defaultdict(list)
        direct_slots: set[str] = set()
        direct_texts: set[str] = set()
        unresolved: list[dict | str] = []

        own_slot_id = f"comp:{comp_id}"
        if own_slot_id in slots:
            slot_intervals[own_slot_id].append((0.0, duration))
            direct_slots.add(own_slot_id)

        for layer in comp.get("layers", []):
            interval = layer_interval(layer, duration)
            enabled = bool(layer.get("enabled")) and interval is not None
            field_id = f"text:{comp_id}:{layer['index']}"
            if field_id in text_fields:
                direct_texts.add(field_id)
                text_intervals.setdefault(field_id, [])
                if enabled:
                    text_intervals[field_id].append(interval)
            source_id = layer.get("sourceId")
            if source_id is None:
                legacy_child = legacy_source_comp(comp, layer.get("source"))
                if legacy_child is None:
                    continue
                source_id = legacy_child["id"]
            source_id = int(source_id)
            comp_slot_id = f"comp:{source_id}"
            footage_slot_id = f"footage:{source_id}"
            if comp_slot_id in slots:
                direct_slots.add(comp_slot_id)
                slot_intervals.setdefault(comp_slot_id, [])
                if enabled:
                    slot_intervals[comp_slot_id].append(interval)
                child = resolve(source_id)
                for child_field_id, child_intervals in child["texts"].items():
                    text_intervals.setdefault(child_field_id, [])
                    if not enabled or not child_intervals:
                        continue
                    if "startTime" not in layer:
                        text_intervals[child_field_id].append(interval)
                        continue
                    for child_interval in child_intervals:
                        mapped = transform_interval(child_interval, layer, duration)
                        if mapped:
                            text_intervals[child_field_id].append(mapped)
                unresolved.extend(child["unresolved"])
                continue
            if footage_slot_id in slots:
                direct_slots.add(footage_slot_id)
                slot_intervals.setdefault(footage_slot_id, [])
                if enabled:
                    slot_intervals[footage_slot_id].append(interval)
                continue
            if source_id in compositions:
                child = resolve(source_id)
                if layer.get("timeRemapEnabled") and child["slots"]:
                    unresolved.append({"layerIndex": layer["index"], "reason": "time_remapped_nested_media_timing"})
                for slot_id, child_intervals in child["slots"].items():
                    slot_intervals.setdefault(slot_id, [])
                    if not enabled:
                        continue
                    if not child_intervals:
                        continue
                    if "startTime" not in layer:
                        slot_intervals[slot_id].append(interval)
                        continue
                    for child_interval in child_intervals:
                        mapped = transform_interval(child_interval, layer, duration)
                        if mapped:
                            slot_intervals[slot_id].append(mapped)
                for field_id, child_intervals in child["texts"].items():
                    text_intervals.setdefault(field_id, [])
                    if not enabled:
                        continue
                    if not child_intervals:
                        continue
                    if "startTime" not in layer:
                        text_intervals[field_id].append(interval)
                        continue
                    for child_interval in child_intervals:
                        mapped = transform_interval(child_interval, layer, duration)
                        if mapped:
                            text_intervals[field_id].append(mapped)
                unresolved.extend(child["unresolved"])
            elif footage_slot_id in unresolved_sources:
                unresolved.append({"layerIndex": layer["index"], "source": unresolved_sources[footage_slot_id]})

        result = {
            "slots": dict(slot_intervals),
            "texts": dict(text_intervals),
            "directSlots": sorted(direct_slots),
            "directTexts": sorted(direct_texts),
            "unresolved": unresolved,
        }
        resolving.remove(comp_id)
        memo[comp_id] = result
        return result

    capacity_rows = []
    for comp_id, comp in compositions.items():
        resolved = resolve(comp_id)
        visual_slots = sorted(slot_id for slot_id in resolved["slots"] if slots[slot_id]["kind"] == "visual")
        audio_slots = sorted(slot_id for slot_id in resolved["slots"] if slots[slot_id]["kind"] == "audio")
        direct_visual = sorted(slot_id for slot_id in resolved["directSlots"] if slots[slot_id]["kind"] == "visual")
        direct_all_intervals = {slot_id: resolved["slots"].get(slot_id, []) for slot_id in resolved["directSlots"]}
        recursive_visual_intervals = {slot_id: resolved["slots"][slot_id] for slot_id in visual_slots}
        duration = float(comp["duration"])
        fps = float(comp["fps"])
        work_duration = float(comp["workAreaDuration"])
        capacity_rows.append({
            "compositionId": comp_id,
            "compositionPath": comp["path"],
            "width": comp["width"],
            "height": comp["height"],
            "durationSeconds": comp["duration"],
            "frameRate": comp["fps"],
            "frameDuration": comp.get("frameDuration") or (1.0 / fps if fps else None),
            "frameCount": int(round(duration * fps)),
            "workAreaStartSeconds": comp["workAreaStart"],
            "workAreaDurationSeconds": comp["workAreaDuration"],
            "workAreaFrameCount": int(round(work_duration * fps)),
            "directEditableTextFields": [
                {**text_fields[field_id], "activationIntervals": resolved["texts"].get(field_id, [])}
                for field_id in resolved["directTexts"]
            ],
            "recursiveEditableTextFields": [
                {**text_fields[field_id], "activationIntervals": resolved["texts"].get(field_id, [])}
                for field_id in sorted(resolved["texts"])
            ],
            "directVisualMediaInputs": [
                {**slots[slot_id], "activationIntervals": resolved["slots"].get(slot_id, [])}
                for slot_id in direct_visual
            ],
            "recursiveVisualMediaInputs": [
                {**slots[slot_id], "activationIntervals": resolved["slots"].get(slot_id, [])}
                for slot_id in visual_slots
            ],
            "recursiveAudioOrOtherMediaInputs": [slots[slot_id] for slot_id in audio_slots],
            "totalIndependentVisualMediaInputs": len(visual_slots),
            "maxSimultaneouslyEnabledDirectInputs": max_active(direct_all_intervals),
            "maxSimultaneouslyEnabledRecursiveVisualInputs": max_active(recursive_visual_intervals),
            "maxSimultaneouslyEnabledRecursiveTextFields": max_active(resolved["texts"]),
            "unresolved": resolved["unresolved"],
        })

    capacity_rows.sort(key=lambda row: row["compositionPath"].lower())
    visual_project_slots = sorted(slot_id for slot_id, row in slots.items() if row["kind"] == "visual")
    audio_project_slots = sorted(slot_id for slot_id, row in slots.items() if row["kind"] == "audio")
    return {
        "schemaVersion": 1,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "sourceProject": report.get("sourceProject") or report.get("inspectionProject"),
        "sourceSha256": report.get("sourceSha256"),
        "nativeReport": {
            "aeVersion": report.get("aeVersion"),
            "inspectionProject": report.get("inspectionProject"),
            "compositionCount": len(compositions),
            "projectItemCount": len(items),
            "missingFootage": report.get("missingFootage", []),
            "missingFonts": report.get("missingFonts", []),
        },
        "measurementRules": {
            "visualSlots": "explicit placeholder compositions, explicit edit-media compositions, and native placeholder footage",
            "solidsExcluded": True,
            "ordinaryFileFootage": "unresolved unless explicit placeholder evidence exists",
            "disabledInputs": "included in total capacity but excluded from simultaneous enabled counts",
            "nestedCompositions": "expanded recursively and deduplicated by independent project item",
        },
        "projectSummary": {
            "verifiedIndependentVisualMediaInputs": len(visual_project_slots),
            "verifiedAudioOrOtherMediaInputs": len(audio_project_slots),
            "editableTextFields": len(text_fields),
            "unresolvedFileFootageCandidates": len(unresolved_sources),
        },
        "mediaSlots": [slots[slot_id] for slot_id in sorted(slots)],
        "textFields": [text_fields[field_id] for field_id in sorted(text_fields)],
        "unresolvedFileFootage": [unresolved_sources[key] for key in sorted(unresolved_sources)],
        "compositions": capacity_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-project", type=Path)
    parser.add_argument("--source-sha256")
    parser.add_argument("--evidence-status", default="fresh_native_report")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite existing capacity output: {args.output}")
    capacity = build_capacity(json.loads(args.report.read_text()))
    if args.source_project:
        capacity["nativeReport"]["reportedInspectionProject"] = capacity.get("sourceProject")
        capacity["sourceProject"] = str(args.source_project.resolve())
    if args.source_sha256:
        capacity["sourceSha256"] = args.source_sha256
    capacity["evidenceStatus"] = args.evidence_status
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(capacity, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(args.output)
    print(json.dumps(capacity["projectSummary"], indent=2))


if __name__ == "__main__":
    main()
