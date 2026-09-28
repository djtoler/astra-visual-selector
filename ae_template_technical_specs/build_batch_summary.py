#!/usr/bin/env python3
"""Build a standalone, evidence-labeled summary of one capacity batch."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


LEGACY_PROJECT_ORDER = (
    "vertical-cinematic-24",
    "vertical-cinematic-26",
    "gallery-pro-carousel",
    "carousel-flow-loops",
    "carousel-photo-logo-reveal",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_headline(project_id: str, path: str) -> bool:
    if project_id in {"vertical-cinematic-24", "vertical-cinematic-26"}:
        return path == "Main_comp/Main"
    if project_id == "gallery-pro-carousel":
        return path.startswith("02. Final Comp/")
    if project_id == "carousel-flow-loops":
        return path.startswith("02. Final/")
    if project_id == "carousel-photo-logo-reveal":
        return path.startswith("02 FINAL/")
    return False


def composition_row(project_id: str, evidence_status: str, row: dict) -> dict:
    return {
        "project_id": project_id,
        "evidence_status": evidence_status,
        "composition_id": row["compositionId"],
        "composition_path": row["compositionPath"],
        "width": row["width"],
        "height": row["height"],
        "duration_seconds": row["durationSeconds"],
        "frame_rate": row["frameRate"],
        "frame_count": row["frameCount"],
        "work_area_start_seconds": row["workAreaStartSeconds"],
        "work_area_duration_seconds": row["workAreaDurationSeconds"],
        "work_area_frame_count": row["workAreaFrameCount"],
        "direct_editable_text_fields": len(row["directEditableTextFields"]),
        "recursive_editable_text_fields": len(row["recursiveEditableTextFields"]),
        "max_simultaneously_enabled_recursive_text_fields": row["maxSimultaneouslyEnabledRecursiveTextFields"],
        "direct_visual_media_inputs": len(row["directVisualMediaInputs"]),
        "total_independent_visual_media_inputs": row["totalIndependentVisualMediaInputs"],
        "max_simultaneously_enabled_direct_inputs": row["maxSimultaneouslyEnabledDirectInputs"],
        "max_simultaneously_enabled_recursive_visual_inputs": row["maxSimultaneouslyEnabledRecursiveVisualInputs"],
        "unresolved_count": len(row["unresolved"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch_dir", type=Path)
    args = parser.parse_args()
    batch_dir = args.batch_dir.resolve()
    manifest = json.loads((batch_dir / "batch.json").read_text())
    projects_by_id = {row["id"]: row for row in manifest["projects"]}
    reconciliation = json.loads((batch_dir / "pass-reconciliation.json").read_text())
    reconciliation_by_id = {row["projectId"]: row for row in reconciliation["results"]}

    projects = []
    all_compositions = []
    all_text_fields = []
    project_order = [row["id"] for row in manifest["projects"]] or list(LEGACY_PROJECT_ORDER)
    for project_id in project_order:
        capacity_path = batch_dir / "capacity-static" / f"{project_id}.json"
        if not capacity_path.is_file():
            capacity_path = batch_dir / "capacity" / f"{project_id}.json"
        capacity = json.loads(capacity_path.read_text())
        reconciliation_row = reconciliation_by_id[project_id]
        result_status = reconciliation_row["status"]
        manifest_project = projects_by_id[project_id]
        source = Path(manifest_project["source"])
        current_hash = sha256(source)
        source_unchanged = current_hash == manifest_project["sha256"]
        composition_rows = [
            composition_row(project_id, capacity["evidenceStatus"], row)
            for row in capacity["compositions"]
        ]
        all_compositions.extend(composition_rows)
        headlines = [row for row in composition_rows if is_headline(project_id, row["composition_path"])]
        for text_field in capacity["textFields"]:
            all_text_fields.append({
                "project_id": project_id,
                "evidence_status": capacity["evidenceStatus"],
                "composition_id": text_field["compositionId"],
                "composition_path": text_field["compositionPath"],
                "layer_index": text_field["layerIndex"],
                "layer_name": text_field["layerName"],
                "enabled": text_field["enabled"],
                "in_point": text_field["inPoint"],
                "out_point": text_field["outPoint"],
                "current_text": text_field["text"],
                "text_kind": text_field["textKind"],
                "font": text_field["font"],
                "font_size": text_field["fontSize"],
                "metadata_complete": text_field["metadataComplete"],
            })
        projects.append({
            "id": project_id,
            "resultStatus": result_status,
            "evidenceStatus": capacity["evidenceStatus"],
            "sourceProject": str(source),
            "expectedSourceSha256": manifest_project["sha256"],
            "currentSourceSha256": current_hash,
            "sourceUnchanged": source_unchanged,
            "staticParser": capacity["nativeReport"].get("aeVersion") or "py-aep v0.17.0",
            "nativeReconciliation": reconciliation_row,
            "capacityFile": str(capacity_path),
            "projectSummary": capacity["projectSummary"],
            "compositionCount": len(capacity["compositions"]),
            "headlineCompositions": headlines,
        })

    summary = {
        "schemaVersion": 1,
        "purpose": "Standalone technical capacity measurement; no render and no catalog or selector merge",
        "renderingPerformed": False,
        "previewVideosRequired": False,
        "accuracyTestStatus": "not_started_separate_later_stage",
        "evidenceNote": "Each result retains its explicit pass-reconciliation status. Exact agreement means the static and native capacity datasets match on every requested capacity field; unresolved pass failures remain labeled and are not promoted to verified two-pass results.",
        "projects": projects,
        "counts": {
            "requestedProjects": len(projects),
            "measuredCapacityProjects": len(projects),
            "sourceBoundStaticCapacityProjects": sum(
                (batch_dir / "capacity-static" / f"{row['id']}.json").is_file() for row in projects
            ),
            "sourceBoundNativeCapacityProjects": sum(
                (batch_dir / "capacity" / f"{row['id']}.json").is_file() for row in projects
            ),
            "twoPassExactAgreementProjects": sum(row["resultStatus"] == "two_pass_exact_agreement" for row in projects),
            "staticOnlyNativeUnresolvedProjects": sum(row["resultStatus"] == "static_only_native_unresolved" for row in projects),
            "staticSourceBoundNativeIncompatibleProjects": sum(row["resultStatus"] == "static_source_bound_native_incompatible_with_ae25" for row in projects),
            "nativeSourceBoundStaticParserUnresolvedProjects": sum(row["resultStatus"] == "native_source_bound_static_parser_unresolved" for row in projects),
            "rejectedMisassociatedNativeReports": (
                int((batch_dir / "rejected-native-association.json").is_file())
                + len(list((batch_dir / "rejected-misassociated").glob("*.json")))
            ),
            "reportedCompositions": len(all_compositions),
            "reportedTextFields": len(all_text_fields),
        },
    }
    (batch_dir / "batch-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    composition_fields = list(all_compositions[0])
    with (batch_dir / "all-compositions.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=composition_fields)
        writer.writeheader()
        writer.writerows(all_compositions)

    text_fields = [
        "project_id", "evidence_status", "composition_id", "composition_path", "layer_index",
        "layer_name", "enabled", "in_point", "out_point", "current_text", "text_kind", "font",
        "font_size", "metadata_complete",
    ]
    with (batch_dir / "text-fields.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=text_fields)
        writer.writeheader()
        writer.writerows(all_text_fields)

    lines = [
        f"# {manifest.get('name', batch_dir.name)} technical-capacity results",
        "",
        "No rendering or preview-video analysis was performed. Accuracy scoring is a separate later stage.",
        "",
        "| Template | Evidence | Project slots | Text fields | Compositions | Source unchanged |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for project in projects:
        project_summary = project["projectSummary"] or {}
        lines.append(
            f"| {project['id']} | {project['resultStatus']} | "
            f"{project_summary.get('verifiedIndependentVisualMediaInputs', '—')} | "
            f"{project_summary.get('editableTextFields', '—')} | "
            f"{project['compositionCount'] if project['compositionCount'] is not None else '—'} | "
            f"{'yes' if project['sourceUnchanged'] else 'NO'} |"
        )
    for project in projects:
        if not project["headlineCompositions"]:
            continue
        lines.extend([
            "",
            f"## {project['id']}",
            "",
            f"Evidence: `{project['resultStatus']}`",
            "",
            "| Composition | Inputs | Max enabled | Text fields | Max text enabled | Duration | FPS | Frames | Work area |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in project["headlineCompositions"]:
            lines.append(
                f"| {row['composition_path']} | {row['total_independent_visual_media_inputs']} | "
                f"{row['max_simultaneously_enabled_recursive_visual_inputs']} | "
                f"{row['recursive_editable_text_fields']} | "
                f"{row['max_simultaneously_enabled_recursive_text_fields']} | "
                f"{row['duration_seconds']}s | {row['frame_rate']} | {row['frame_count']} | "
                f"{row['work_area_start_seconds']}s + {row['work_area_duration_seconds']}s "
                f"({row['work_area_frame_count']} frames) |"
            )
    lines.extend([
        "",
        "## Evidence boundary",
        "",
        "Every project remains bound to the current source path and SHA-256 hash. Exact two-pass status is granted only when the independent static and native datasets agree on the requested capacity fields. Any unavailable or incompatible pass remains explicitly unresolved.",
        "",
        "`Maximum enabled` means AE layers enabled over overlapping in/out intervals. It does not claim that every enabled layer is visually unobscured at the same instant.",
        "",
    ])
    (batch_dir / "REPORT.md").write_text("\n".join(lines))

    print(json.dumps(summary["counts"], indent=2))


if __name__ == "__main__":
    main()
