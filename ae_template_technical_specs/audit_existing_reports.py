#!/usr/bin/env python3
"""Inventory and deduplicate existing AE reports without launching After Effects."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


def is_native_shaped(report: object) -> bool:
    if not isinstance(report, dict):
        return False
    comps = report.get("compositions")
    return bool(
        isinstance(comps, list)
        and comps
        and isinstance(comps[0], dict)
        and "layers" in comps[0]
        and "duration" in comps[0]
    )


def composition_fingerprint(report: dict) -> str:
    canonical = []
    for comp in report["compositions"]:
        layers = []
        for layer in comp.get("layers", []):
            text = layer.get("text")
            if text is None:
                text = (layer.get("textField") or {}).get("text")
            layers.append([
                layer.get("index"), layer.get("name"), layer.get("source"),
                layer.get("enabled"), layer.get("inPoint"), layer.get("outPoint"), text,
            ])
        canonical.append([
            comp.get("path") or comp.get("name"), comp.get("width"), comp.get("height"),
            comp.get("duration"), comp.get("fps"), comp.get("workAreaStart"),
            comp.get("workAreaDuration"), layers,
        ])
    payload = json.dumps(canonical, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def report_row(path: Path, report: dict) -> dict:
    compositions = report["compositions"]
    roots = sorted({
        (comp.get("path") or comp.get("name") or "").split("/", 1)[0]
        for comp in compositions
    })
    return {
        "path": str(path),
        "mode": report.get("mode"),
        "ok": report.get("ok"),
        "aeVersion": report.get("aeVersion"),
        "sourceProject": report.get("sourceProject"),
        "sourceSha256": report.get("sourceSha256"),
        "inspectionProject": report.get("inspectionProject"),
        "compositionCount": len(compositions),
        "textLayerCount": sum(
            1 for comp in compositions for layer in comp.get("layers", [])
            if "text" in layer or "textField" in layer
        ),
        "rootNames": roots,
        "error": report.get("error"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--exclude-fragment", action="append", default=[])
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    records = []
    for root in args.root:
        for path in root.resolve().rglob("*.json"):
            path_text = str(path)
            if any(fragment in path_text for fragment in args.exclude_fragment):
                continue
            try:
                report = json.loads(path.read_text())
            except Exception:
                continue
            if not is_native_shaped(report):
                continue
            row = report_row(path, report)
            row["fingerprint"] = composition_fingerprint(report)
            records.append(row)

    successful_inspections = [row for row in records if row["mode"] == "inspect" and row["ok"] is True]
    groups = defaultdict(list)
    for row in successful_inspections:
        groups[row["fingerprint"]].append(row)
    inspection_groups = []
    for fingerprint, rows in groups.items():
        first = rows[0]
        inspection_names = sorted({
            Path(row["inspectionProject"]).name
            for row in rows if row["inspectionProject"]
        })
        source_hashes = sorted({row["sourceSha256"] for row in rows if row["sourceSha256"]})
        inspection_groups.append({
            "fingerprint": fingerprint,
            "status": "source_bound_native_inspection" if source_hashes else "native_inspection_complete_lineage_unverified",
            "compositionCount": first["compositionCount"],
            "textLayerCount": first["textLayerCount"],
            "rootNames": first["rootNames"],
            "inspectionProjectNames": inspection_names,
            "sourceHashes": source_hashes,
            "duplicateReportCount": len(rows),
            "reports": [row["path"] for row in rows],
        })
    inspection_groups.sort(key=lambda row: (row["compositionCount"], row["rootNames"], row["fingerprint"]))

    counts = Counter((row["mode"] or "unknown", "ok" if row["ok"] is True else "failed" if row["ok"] is False else "unknown") for row in records)
    output = {
        "schemaVersion": 1,
        "purpose": "Read-only recovery audit; no report is attributed to a current source until hash or full static composition fingerprint reconciliation succeeds.",
        "roots": [str(root.resolve()) for root in args.root],
        "excludedFragments": args.exclude_fragment,
        "summary": {
            "nativeShapedReportFiles": len(records),
            "successfulInspectionReports": len(successful_inspections),
            "uniqueSuccessfulInspectionFingerprints": len(inspection_groups),
            "modeStatusCounts": {f"{mode}:{status}": count for (mode, status), count in sorted(counts.items())},
        },
        "successfulInspectionGroups": inspection_groups,
        "partialOrModifiedEvidence": [
            row for row in records if not (row["mode"] == "inspect" and row["ok"] is True)
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "existing-report-audit.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Existing After Effects report audit",
        "",
        "This is a read-only discovery audit. A successful old inspection is reusable evidence only after its full composition fingerprint or recorded source hash matches a current source project.",
        "",
        f"- Native-shaped report files: {len(records)}",
        f"- Successful inspection reports: {len(successful_inspections)}",
        f"- Distinct successful inspection fingerprints: {len(inspection_groups)}",
        "",
        "| Group | Comps | Text layers | Duplicate reports | Inspection-project names | Root names | Status |",
        "|---:|---:|---:|---:|---|---|---|",
    ]
    for index, group in enumerate(inspection_groups, 1):
        inspections = ", ".join(group["inspectionProjectNames"]) or "—"
        roots = ", ".join(group["rootNames"][:6])
        if len(group["rootNames"]) > 6:
            roots += ", …"
        lines.append(
            f"| {index} | {group['compositionCount']} | {group['textLayerCount']} | "
            f"{group['duplicateReportCount']} | {inspections} | {roots} | {group['status']} |"
        )
    lines.extend([
        "",
        "## Safe reuse rule",
        "",
        "1. Parse the current source AEP read-only and bind its SHA-256 hash.",
        "2. Compare its complete composition paths, timing, media-slot paths and text identities with each old-report fingerprint.",
        "3. Reuse exact matches; mark near matches partial; reject zero-overlap or conflicting structures.",
        "4. Keep successful build/render reports as partial evidence only because they may describe modified projects.",
        "",
    ])
    (output_dir / "REPORT.md").write_text("\n".join(lines))
    print(json.dumps(output["summary"], indent=2))


if __name__ == "__main__":
    main()
