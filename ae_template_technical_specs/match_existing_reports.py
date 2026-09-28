#!/usr/bin/env python3
"""Match current source AEPs to existing native reports by full structure."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from static_inspect import inspect


def close(left, right) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(float(left), float(right), rel_tol=1e-10, abs_tol=1e-10)
    return left == right


def text_value(layer: dict):
    return layer.get("text") if "text" in layer else (layer.get("textField") or {}).get("text")


def compare_reports(static: dict, native: dict) -> dict:
    static_comps = {row.get("path") or row.get("name"): row for row in static["compositions"]}
    native_comps = {row.get("path") or row.get("name"): row for row in native["compositions"]}
    static_paths = set(static_comps)
    native_paths = set(native_comps)
    shared = sorted(static_paths & native_paths)
    metric_mismatches = 0
    layer_mismatches = 0
    for path in shared:
        left = static_comps[path]
        right = native_comps[path]
        for field in ("width", "height", "duration", "fps", "workAreaStart", "workAreaDuration"):
            if not close(left.get(field), right.get(field)):
                metric_mismatches += 1
        left_layers = left.get("layers", [])
        right_layers = right.get("layers", [])
        if len(left_layers) != len(right_layers):
            layer_mismatches += 1
            continue
        for left_layer, right_layer in zip(left_layers, right_layers):
            for field in ("index", "name", "source", "enabled", "inPoint", "outPoint"):
                if not close(left_layer.get(field), right_layer.get(field)):
                    layer_mismatches += 1
            if text_value(left_layer) != text_value(right_layer):
                layer_mismatches += 1
    union = static_paths | native_paths
    return {
        "staticCompositionCount": len(static_paths),
        "nativeCompositionCount": len(native_paths),
        "sharedCompositionCount": len(shared),
        "compositionPathOverlap": len(shared) / len(union) if union else 1.0,
        "compositionPathSetExact": static_paths == native_paths,
        "metricMismatchCount": metric_mismatches,
        "layerMismatchCount": layer_mismatches,
        "exactStructuralMatch": static_paths == native_paths and metric_mismatches == 0 and layer_mismatches == 0,
    }


def inventory_projects(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    rows = data.get("projects") or data.get("selected") or []
    return [row for row in rows if row.get("kind", "aep") == "aep" and Path(row["absolutePath"]).suffix.lower() == ".aep"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, action="append", required=True)
    parser.add_argument("--report-audit", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--batch-01", type=Path, required=True)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    static_dir = output_dir / "static-source-reports"
    static_dir.mkdir(parents=True, exist_ok=True)
    audit = json.loads(args.report_audit.read_text())
    groups = audit["successfulInspectionGroups"]
    native_reports = {}
    for group in groups:
        native_reports[group["fingerprint"]] = json.loads(Path(group["reports"][0]).read_text())
    batch = json.loads((args.batch_01 / "batch.json").read_text())
    batch_hashes = {row["sha256"] for row in batch["projects"]}

    sources = {}
    for inventory in args.inventory:
        for row in inventory_projects(inventory):
            sources[row["sha256"]] = {
                "sourceProject": row["absolutePath"],
                "sourceSha256": row["sha256"],
                "sizeBytes": row["sizeBytes"],
                "inventory": str(inventory.resolve()),
            }
    results = []
    for source_hash, source in sorted(sources.items(), key=lambda item: item[1]["sourceProject"].lower()):
        raw_path = static_dir / f"{source_hash}.json"
        if raw_path.is_file():
            static = json.loads(raw_path.read_text())
        else:
            try:
                static = inspect(Path(source["sourceProject"]))
            except Exception as error:
                results.append({
                    **source,
                    "alreadyInBatch01": source_hash in batch_hashes,
                    "staticReport": None,
                    "staticCompositionCount": None,
                    "status": "static_parser_failed_unresolved",
                    "parserError": f"{type(error).__name__}: {error}",
                    "exactMatches": [],
                    "partialMatches": [],
                })
                continue
            raw_path.write_text(json.dumps(static, indent=2, ensure_ascii=False) + "\n")
        exact = []
        partial = []
        for group in groups:
            comparison = compare_reports(static, native_reports[group["fingerprint"]])
            match = {
                "fingerprint": group["fingerprint"],
                "compositionCount": group["compositionCount"],
                "inspectionProjectNames": group["inspectionProjectNames"],
                "reports": group["reports"],
                "comparison": comparison,
            }
            if comparison["exactStructuralMatch"]:
                exact.append(match)
            elif comparison["compositionPathSetExact"] or comparison["compositionPathOverlap"] >= 0.8:
                partial.append(match)
        if exact:
            status = "existing_native_exact_structural_match"
        elif partial:
            status = "existing_native_partial_structural_match"
        else:
            status = "no_matching_existing_native_inspection"
        results.append({
            **source,
            "alreadyInBatch01": source_hash in batch_hashes,
            "staticReport": str(raw_path),
            "staticCompositionCount": len(static["compositions"]),
            "status": status,
            "exactMatches": exact,
            "partialMatches": partial,
        })

    outside = [row for row in results if not row["alreadyInBatch01"]]
    summary = {
        "currentSourceProjects": len(results),
        "batch01Projects": sum(row["alreadyInBatch01"] for row in results),
        "outsideBatch01Projects": len(outside),
        "outsideBatch01ExactExistingNativeMatches": sum(row["status"] == "existing_native_exact_structural_match" for row in outside),
        "outsideBatch01PartialExistingNativeMatches": sum(row["status"] == "existing_native_partial_structural_match" for row in outside),
        "outsideBatch01NoExistingNativeMatch": sum(row["status"] == "no_matching_existing_native_inspection" for row in outside),
        "outsideBatch01StaticParserFailures": sum(row["status"] == "static_parser_failed_unresolved" for row in outside),
    }
    payload = {
        "schemaVersion": 1,
        "purpose": "Read-only source-to-report reconciliation. Exact structural matches are reusable evidence; partial matches require review.",
        "summary": summary,
        "projects": results,
    }
    (output_dir / "source-report-matches.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    lines = [
        "# Existing-work matches against current sources",
        "",
        f"- Current AEP sources: {summary['currentSourceProjects']}",
        f"- Already in batch 01: {summary['batch01Projects']}",
        f"- Outside batch 01 with exact existing native match: {summary['outsideBatch01ExactExistingNativeMatches']}",
        f"- Outside batch 01 with partial structural match: {summary['outsideBatch01PartialExistingNativeMatches']}",
        f"- Outside batch 01 with no native match: {summary['outsideBatch01NoExistingNativeMatch']}",
        f"- Outside batch 01 unresolved because the static parser failed: {summary['outsideBatch01StaticParserFailures']}",
        "",
        "| Source | Comps | Batch 01 | Existing evidence | Matched inspection |",
        "|---|---:|---:|---|---|",
    ]
    for row in results:
        match_names = []
        for match in row["exactMatches"] or row["partialMatches"]:
            match_names.extend(match["inspectionProjectNames"])
        label = ", ".join(sorted(set(match_names))) or "—"
        lines.append(
            f"| {row['sourceProject']} | {row['staticCompositionCount'] if row['staticCompositionCount'] is not None else '—'} | "
            f"{'yes' if row['alreadyInBatch01'] else 'no'} | {row['status']} | {label} |"
        )
    lines.extend([
        "",
        "Exact structural match means every composition path, composition timing/size, layer count, layer identity, source name, enabled state, in/out range and text value matched within numeric tolerance.",
        "",
    ])
    (output_dir / "SOURCE-MATCHES.md").write_text("\n".join(lines))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
