#!/usr/bin/env python3
"""Reconcile source-bound static capacity with available native AE evidence."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


METRIC_FIELDS = (
    "totalIndependentVisualMediaInputs",
    "maxSimultaneouslyEnabledRecursiveVisualInputs",
    "maxSimultaneouslyEnabledRecursiveTextFields",
    "durationSeconds",
    "frameRate",
    "frameCount",
    "workAreaStartSeconds",
    "workAreaDurationSeconds",
    "workAreaFrameCount",
)

LEGACY_NATIVE_FILES = {
    "vertical-cinematic-24": "vertical-cinematic-24.json",
    "gallery-pro-carousel": "gallery-pro-carousel.json",
    "carousel-flow-loops": "carousel-flow-loops.provisional.json",
    "carousel-photo-logo-reveal": "carousel-photo-logo-reveal.provisional.json",
}


def same(left, right) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(float(left), float(right), rel_tol=1e-10, abs_tol=1e-10)
    return left == right


def normalized_composition_path(value: str) -> str:
    """Match paths when AE drops edge whitespace from folder-name segments.

    The final segment is a composition name and remains byte-for-byte distinct;
    projects can legitimately contain both ``Texture`` and ``Texture `` comps.
    """
    segments = value.split("/")
    if len(segments) == 1:
        return value
    return "/".join([*(segment.strip() for segment in segments[:-1]), segments[-1]])


def indexed_compositions(rows: list[dict], evidence_name: str) -> dict[str, dict]:
    indexed: dict[str, dict] = {}
    originals: dict[str, str] = {}
    for row in rows:
        original = row["compositionPath"]
        normalized = normalized_composition_path(original)
        if normalized in indexed and originals[normalized] != original:
            raise ValueError(
                f"{evidence_name} composition paths collide after edge-whitespace "
                f"normalization: {originals[normalized]!r} and {original!r}"
            )
        indexed[normalized] = row
        originals[normalized] = original
    return indexed


def text_identity(row: dict) -> tuple:
    return (
        normalized_composition_path(row["compositionPath"]),
        row["layerIndex"], row["layerName"],
        row["enabled"],
    )


def normalized_text(value):
    return value.replace("\r\n", "\n").replace("\r", "\n") if isinstance(value, str) else value


def reconcile(static: dict, native: dict) -> dict:
    static_comps = indexed_compositions(static["compositions"], "static")
    native_comps = indexed_compositions(native["compositions"], "native")
    static_paths = set(static_comps)
    native_paths = set(native_comps)
    shared = sorted(static_paths & native_paths)
    mismatches = []
    for path in shared:
        for field in METRIC_FIELDS:
            if not same(static_comps[path][field], native_comps[path][field]):
                mismatches.append({
                    "compositionPath": path,
                    "field": field,
                    "static": static_comps[path][field],
                    "native": native_comps[path][field],
                })
        static_text_count = len(static_comps[path]["recursiveEditableTextFields"])
        native_text_count = len(native_comps[path]["recursiveEditableTextFields"])
        if static_text_count != native_text_count:
            mismatches.append({
                "compositionPath": path,
                "field": "recursiveEditableTextFieldCount",
                "static": static_text_count,
                "native": native_text_count,
            })
    static_slots = sorted(normalized_composition_path(row["path"]) for row in static["mediaSlots"])
    native_slots = sorted(normalized_composition_path(row["path"]) for row in native["mediaSlots"])
    static_texts = sorted(text_identity(row) for row in static["textFields"])
    native_texts = sorted(text_identity(row) for row in native["textFields"])
    static_text_values = {text_identity(row): normalized_text(row.get("text")) for row in static["textFields"]}
    native_text_values = {text_identity(row): normalized_text(row.get("text")) for row in native["textFields"]}
    text_value_mismatches = [
        {
            "identity": list(identity),
            "static": static_text_values[identity],
            "native": native_text_values[identity],
        }
        for identity in sorted(set(static_text_values) & set(native_text_values))
        if static_text_values[identity] != native_text_values[identity]
    ]
    return {
        "staticCompositionCount": len(static_paths),
        "nativeCompositionCount": len(native_paths),
        "sharedCompositionCount": len(shared),
        "compositionPathSetExact": static_paths == native_paths,
        "staticOnlyCompositionPaths": sorted(static_paths - native_paths),
        "nativeOnlyCompositionPaths": sorted(native_paths - static_paths),
        "metricMismatchCount": len(mismatches),
        "metricMismatches": mismatches,
        "mediaSlotPathSetExact": static_slots == native_slots,
        "staticMediaSlotPaths": static_slots,
        "nativeMediaSlotPaths": native_slots,
        "textFieldIdentitySetExact": static_texts == native_texts,
        "staticTextFieldIdentities": [list(row) for row in static_texts],
        "nativeTextFieldIdentities": [list(row) for row in native_texts],
        "textValueMismatchCount": len(text_value_mismatches),
        "textValueMismatches": text_value_mismatches,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch_dir", type=Path)
    args = parser.parse_args()
    batch = args.batch_dir.resolve()
    manifest_path = batch / "batch.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {"projects": []}
    project_ids = [row["id"] for row in manifest.get("projects", [])]
    if not project_ids:
        project_ids = sorted(path.stem for path in (batch / "capacity-static").glob("*.json"))
    results = []
    for project_id in project_ids:
        static_path = batch / "capacity-static" / f"{project_id}.json"
        native_path = batch / "capacity" / f"{project_id}.json"
        if not native_path.is_file() and project_id in LEGACY_NATIVE_FILES:
            native_path = batch / "capacity" / LEGACY_NATIVE_FILES[project_id]
        static = json.loads(static_path.read_text()) if static_path.is_file() else None
        native = json.loads(native_path.read_text()) if native_path.is_file() else None
        if static is None and native is not None:
            results.append({
                "projectId": project_id,
                "status": "native_source_bound_static_parser_unresolved",
                "staticSourceSha256": None,
                "staticCompositionCount": None,
                "nativeCapacityFile": str(native_path),
                "nativeCompositionCount": len(native["compositions"]),
                "nativeProjectSummary": native["projectSummary"],
            })
            continue
        if static is None:
            results.append({
                "projectId": project_id,
                "status": "both_passes_unresolved",
                "staticSourceSha256": None,
                "nativeCapacityFile": None,
            })
            continue
        if native is None:
            failed_native_path = batch / "raw" / f"{project_id}.json"
            failed_native = json.loads(failed_native_path.read_text()) if failed_native_path.is_file() else None
            incompatible = bool(
                failed_native
                and not failed_native.get("ok")
                and "cannot be opened with this version" in (failed_native.get("error") or "")
            )
            results.append({
                "projectId": project_id,
                "status": "static_source_bound_native_incompatible_with_ae25" if incompatible else "static_only_native_unresolved",
                "staticSourceSha256": static["sourceSha256"],
                "staticCompositionCount": len(static["compositions"]),
                "staticProjectSummary": static["projectSummary"],
                "nativeCapacityFile": None,
                "nativeFailureReport": str(failed_native_path) if failed_native else None,
                "nativeFailure": failed_native.get("error") if failed_native else None,
            })
            continue
        comparison = reconcile(static, native)
        exact = (
            comparison["compositionPathSetExact"]
            and comparison["metricMismatchCount"] == 0
            and comparison["mediaSlotPathSetExact"]
            and comparison["textFieldIdentitySetExact"]
        )
        if exact:
            status = "two_pass_exact_agreement"
        elif comparison["sharedCompositionCount"] == 0:
            status = "native_report_rejected_wrong_project"
        else:
            status = "two_pass_disagreement"
        results.append({
            "projectId": project_id,
            "status": status,
            "staticSourceSha256": static["sourceSha256"],
            "staticProjectSummary": static["projectSummary"],
            "staticCapacityFile": str(static_path),
            "nativeCapacityFile": str(native_path),
            "nativeEvidenceStatus": native["evidenceStatus"],
            "comparison": comparison,
        })

    by_id = {row["projectId"]: row for row in results}
    vertical_24 = batch / "capacity-static" / "vertical-cinematic-24.json"
    vertical_26 = batch / "capacity-static" / "vertical-cinematic-26.json"
    if vertical_24.is_file() and vertical_26.is_file() and "vertical-cinematic-26" in by_id:
        sibling = reconcile(json.loads(vertical_26.read_text()), json.loads(vertical_24.read_text()))
        by_id["vertical-cinematic-26"]["siblingComparison"] = {
            "comparedTo": "vertical-cinematic-24 static source-bound result",
            "exactCapacityAgreement": (
                sibling["compositionPathSetExact"]
                and sibling["metricMismatchCount"] == 0
                and sibling["mediaSlotPathSetExact"]
                and sibling["textFieldIdentitySetExact"]
            ),
            "comparison": sibling,
        }
    output = {
        "schemaVersion": 1,
        "measurementFields": list(METRIC_FIELDS) + ["recursiveEditableTextFieldCount"],
        "results": sorted(results, key=lambda row: row["projectId"]),
    }
    path = batch / "pass-reconciliation.json"
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps([
        {"projectId": row["projectId"], "status": row["status"]}
        for row in output["results"]
    ], indent=2))


if __name__ == "__main__":
    main()
