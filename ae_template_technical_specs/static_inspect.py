#!/usr/bin/env python3
"""Read an AEP directly with py-aep and emit a capacity-lab raw report.

The source project is never written. This adapter deliberately emits the same
core composition/layer fields as the native AE inspection so both independent
passes can be derived with the same capacity rules.
"""

from __future__ import annotations

import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path

import py_aep


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def item_path(item, root_folder) -> str:
    parts = [item.name]
    parent = getattr(item, "parent_folder", None)
    seen = set()
    while parent is not None and parent is not root_folder and id(parent) not in seen:
        seen.add(id(parent))
        parts.append(parent.name)
        parent = getattr(parent, "parent_folder", None)
    return "/".join(reversed(parts))


def source_text(layer) -> tuple[dict | None, dict | None]:
    text_group = getattr(layer, "text", None)
    if text_group is None:
        return None, None
    for prop in getattr(text_group, "properties", []):
        if getattr(prop, "match_name", None) != "ADBE Text Document":
            continue
        document = getattr(prop, "value", None)
        if document is None:
            return None, None
        box_size = getattr(document, "box_text_size", None)
        if box_size is not None:
            try:
                box_size = list(box_size)
            except TypeError:
                box_size = str(box_size)
        field = {
            "text": getattr(document, "text", None),
            "textKind": "paragraph" if getattr(document, "box_text", False) else "point",
            "font": getattr(document, "font", None),
            "fontSize": getattr(document, "font_size", None),
            "boxTextSize": box_size,
        }
        return field, property_state(prop)
    return None, None


def json_value(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    return str(value)


def interpolation_name(value) -> str:
    return getattr(value, "name", None) or str(value)


def property_state(prop, *, capture_keyframes: bool = False) -> dict:
    keyframes = list(getattr(prop, "keyframes", []))
    state = {
        "numKeys": len(keyframes),
        "expression": getattr(prop, "expression", ""),
        "expressionEnabled": bool(getattr(prop, "expression_enabled", False)),
    }
    if capture_keyframes and keyframes:
        state["keyframes"] = [
            {
                "index": index,
                "time": keyframe.time,
                "value": json_value(keyframe.value),
                "inInterpolationType": interpolation_name(keyframe.in_interpolation_type),
                "outInterpolationType": interpolation_name(keyframe.out_interpolation_type),
            }
            for index, keyframe in enumerate(keyframes, start=1)
        ]
    return state


def property_by_match_name(properties, match_name):
    return next(
        (prop for prop in (properties or []) if getattr(prop, "match_name", None) == match_name),
        None,
    )


def transform_states(layer) -> dict:
    transform = getattr(layer, "transform", None)
    properties = getattr(transform, "properties", []) if transform is not None else []
    matches = {
        "anchorPoint": "ADBE Anchor Point",
        "position": "ADBE Position",
        "scale": "ADBE Scale",
        "rotation": "ADBE Rotate Z",
        "opacity": "ADBE Opacity",
    }
    states = {}
    for field, match_name in matches.items():
        prop = property_by_match_name(properties, match_name)
        if prop is not None:
            states[field] = property_state(prop, capture_keyframes=field == "opacity")
    return states


def inspect(source: Path) -> dict:
    source = source.resolve()
    source_hash = sha256(source)
    app = py_aep.parse(source)
    project = app.project
    root = project.root_folder
    items = []
    for item in project.items.values():
        item_type = type(item).__name__
        row = {
            "id": item.id,
            "itemType": item_type,
            "name": item.name,
            "path": item_path(item, root),
        }
        if item_type == "FootageItem":
            main_source = getattr(item, "main_source", None)
            row.update({
                "sourceType": type(main_source).__name__ if main_source is not None else None,
                "file": str(item.file) if getattr(item, "file", None) is not None else None,
                "hasAudio": bool(getattr(item, "has_audio", False)),
                "hasVideo": bool(getattr(item, "has_video", False)),
                "missing": bool(getattr(item, "footage_missing", False)),
            })
        items.append(row)

    compositions = []
    for comp in project.compositions:
        layers = []
        for layer in comp.layers:
            source_item = getattr(layer, "source", None)
            row = {
                "id": layer.id,
                "index": layer.index + 1,
                "name": layer.name,
                "layerType": type(layer).__name__,
                "enabled": bool(layer.enabled),
                "inPoint": layer.in_point,
                "outPoint": layer.out_point,
                "startTime": layer.start_time,
                "stretch": layer.stretch,
                "timeRemapEnabled": bool(getattr(layer, "time_remap_enabled", False)),
                "sourceId": getattr(source_item, "id", None),
                "source": getattr(source_item, "name", None),
                "transform": transform_states(layer),
            }
            if row["timeRemapEnabled"]:
                time_remap = property_by_match_name(
                    getattr(layer, "properties", []), "ADBE Time Remapping"
                )
                if time_remap is not None:
                    row["timeRemap"] = property_state(
                        time_remap, capture_keyframes=True
                    )
            text_field, source_text_state = source_text(layer)
            if text_field is not None:
                row["textField"] = text_field
                row["sourceText"] = source_text_state
            effects = []
            for effect in (getattr(layer, "effects", None) or []):
                effects.append({
                    "name": getattr(effect, "name", None),
                    "matchName": getattr(effect, "match_name", None),
                    "enabled": bool(getattr(effect, "enabled", True)),
                })
            if effects:
                row["effects"] = effects
            layers.append(row)
        compositions.append({
            "id": comp.id,
            "name": comp.name,
            "path": item_path(comp, root),
            "width": comp.width,
            "height": comp.height,
            "duration": comp.duration,
            "fps": comp.frame_rate,
            "frameDuration": comp.frame_duration,
            "workAreaStart": comp.work_area_start,
            "workAreaDuration": comp.work_area_duration,
            "layers": layers,
        })

    return {
        "schemaVersion": 1,
        "mode": "static_py_aep",
        "ok": True,
        "sourceProject": str(source),
        "sourceSha256": source_hash,
        "parser": {"name": "py-aep", "version": version("py-aep")},
        "aepVersion": getattr(app, "version", None),
        "projectName": getattr(project, "project_name", None),
        "items": items,
        "compositions": compositions,
        "warnings": [
            "Static parser does not evaluate expressions or render-time visibility.",
            "Parser results require comparison with native AE evidence before verified-capacity status.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite existing report: {args.output}")
    report = inspect(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(args.output)
    print(json.dumps({
        "sourceProject": report["sourceProject"],
        "sourceSha256": report["sourceSha256"],
        "compositionCount": len(report["compositions"]),
        "itemCount": len(report["items"]),
        "parser": report["parser"],
    }, indent=2))


if __name__ == "__main__":
    main()
