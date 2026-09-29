#!/usr/bin/env python3
"""Combine frozen capacity batches into the standalone all-template dataset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique_project_id(project_id: str, source_sha256: str, used: set[str]) -> str:
    candidate = project_id
    if candidate in used:
        candidate = f"{project_id}-{source_sha256[:8]}"
    if candidate in used:
        raise ValueError(f"project id still collides after source-hash suffix: {candidate}")
    used.add(candidate)
    return candidate


def combine_csv(
    paths: list[tuple[str, Path]],
    output: Path,
    project_aliases: dict[tuple[str, str], str],
) -> int:
    rows = []
    fields = None
    for batch_id, path in paths:
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            if fields is None:
                fields = ["batch_id"] + list(reader.fieldnames or [])
            for row in reader:
                row["project_id"] = project_aliases[(batch_id, row["project_id"])]
                rows.append({"batch_id": batch_id, **row})
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or ["batch_id"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("batches", nargs="+", type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    projects = []
    batch_rows = []
    project_aliases: dict[tuple[str, str], str] = {}
    used_project_ids: set[str] = set()
    for batch_path in args.batches:
        batch = batch_path.resolve()
        if not (batch / "measurement-freeze.json").is_file():
            raise SystemExit(f"Batch is not frozen: {batch}")
        summary = json.loads((batch / "batch-summary.json").read_text())
        batch_id = batch.name
        batch_rows.append((batch_id, batch, summary))
        for project in summary["projects"]:
            original_id = project["id"]
            project_id = unique_project_id(
                original_id,
                project["expectedSourceSha256"],
                used_project_ids,
            )
            project_aliases[(batch_id, original_id)] = project_id
            combined = {"batchId": batch_id, **project, "id": project_id}
            if project_id != original_id:
                combined["sourceBatchProjectId"] = original_id
            projects.append(combined)

    composition_count = combine_csv(
        [(batch_id, batch / "all-compositions.csv") for batch_id, batch, _ in batch_rows],
        output / "all-template-compositions.csv",
        project_aliases,
    )
    text_count = combine_csv(
        [(batch_id, batch / "text-fields.csv") for batch_id, batch, _ in batch_rows],
        output / "all-template-text-fields.csv",
        project_aliases,
    )
    counts = {
        "sourceProjects": len(projects),
        "twoPassExactAgreementProjects": sum(row["resultStatus"] == "two_pass_exact_agreement" for row in projects),
        "staticSourceBoundNativeIncompatibleProjects": sum(row["resultStatus"] == "static_source_bound_native_incompatible_with_ae25" for row in projects),
        "nativeSourceBoundStaticParserUnresolvedProjects": sum(row["resultStatus"] == "native_source_bound_static_parser_unresolved" for row in projects),
        "reportedCompositions": composition_count,
        "reportedTextFields": text_count,
    }
    payload = {
        "schemaVersion": 1,
        "purpose": "Standalone all-template technical capacity measurement; no rendering, selector merge, or accuracy scoring",
        "renderingPerformed": False,
        "accuracyTestStatus": "not_started_separate_later_stage",
        "counts": counts,
        "projects": projects,
        "batches": [
            {
                "id": batch_id,
                "path": str(batch),
                "freeze": str(batch / "measurement-freeze.json"),
                "freezeSha256": sha256(batch / "measurement-freeze.json"),
            }
            for batch_id, batch, _ in batch_rows
        ],
    }
    summary_path = output / "all-template-summary.json"
    summary_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# All-template technical-capacity measurement",
        "",
        "No rendering or preview-video analysis was performed. Accuracy testing remains a separate next stage.",
        "",
        f"- Source projects measured: {counts['sourceProjects']}",
        f"- Exact two-pass agreements: {counts['twoPassExactAgreementProjects']}",
        f"- Static-only because the source requires AE26: {counts['staticSourceBoundNativeIncompatibleProjects']}",
        f"- Native-only because the static parser cannot read the source encoding: {counts['nativeSourceBoundStaticParserUnresolvedProjects']}",
        f"- Compositions reported: {counts['reportedCompositions']}",
        f"- Editable text fields reported: {counts['reportedTextFields']}",
        "",
        "| Template | Evidence | Project media slots | Text fields | Compositions | Source unchanged |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for project in projects:
        summary = project.get("projectSummary") or {}
        lines.append(
            f"| {project['id']} | {project['resultStatus']} | "
            f"{summary.get('verifiedIndependentVisualMediaInputs', '—')} | "
            f"{summary.get('editableTextFields', '—')} | {project['compositionCount']} | "
            f"{'yes' if project['sourceUnchanged'] else 'NO'} |"
        )
    lines.extend([
        "",
        "Per-composition duration, frame timing, total media inputs, maximum simultaneously enabled inputs, and recursive text availability are in `all-template-compositions.csv`. Every individual editable text layer is in `all-template-text-fields.csv`.",
        "",
        "## Evidence boundary",
        "",
        "Exact agreement means both passes match on composition structure, timing, media capacity, simultaneous maxima, and text-field availability. Current sample-text serialization differences are retained in the batch reconciliation but do not change field availability. AE26-incompatible and static-parser-incompatible sources remain explicitly labeled; their available source-bound pass is not presented as two-pass agreement.",
        "",
    ])
    report_path = output / "ALL-TEMPLATES-REPORT.md"
    report_path.write_text("\n".join(lines))

    freeze_files = [summary_path, report_path, output / "all-template-compositions.csv", output / "all-template-text-fields.csv"]
    freeze = {
        "schemaVersion": 1,
        "scope": "All current template technical-capacity measurements; accuracy scoring not included",
        "renderingPerformed": False,
        "sourceHashesVerifiedUnchanged": all(row["sourceUnchanged"] for row in projects),
        "batchFreezeHashes": {row["id"]: row["freezeSha256"] for row in payload["batches"]},
        "files": [
            {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in freeze_files
        ],
    }
    (output / "all-template-measurement-freeze.json").write_text(json.dumps(freeze, indent=2) + "\n")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
