#!/usr/bin/env python3
"""Add one source-bound capacity report to the portable technical index.

This is the incremental intake path for templates measured after the frozen
bulk batch. It never alters the AEP and it preserves the evidence status of
the supplied capacity report instead of promoting it to two-pass agreement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .visualtask_ae_spec_comparison import validate_technical_index


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_source(path: Path) -> dict:
    path = Path(path)
    return {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}


def project_from_capacity(
    capacity: dict,
    *,
    project_id: str,
    batch_id: str,
    result_status: str,
    capacity_path: Path,
) -> dict:
    source_path = Path(capacity["sourceProject"])
    if not source_path.is_file():
        raise ValueError(f"source project is missing: {source_path}")
    source_hash = sha256(source_path)
    if source_hash != capacity.get("sourceSha256"):
        raise ValueError("capacity report source hash is stale")

    text_fields = [
        {
            "id": row["id"],
            "compositionId": row["compositionId"],
            "compositionPath": row["compositionPath"],
            "layerIndex": row["layerIndex"],
            "layerName": row["layerName"],
            "enabled": row["enabled"],
            "inPoint": row["inPoint"],
            "outPoint": row["outPoint"],
            "textKind": row.get("textKind"),
            "font": row.get("font"),
            "fontSize": row.get("fontSize"),
            "metadataComplete": row.get("metadataComplete", False),
        }
        for row in capacity.get("textFields", [])
    ]
    text_fields.sort(key=lambda row: (row["compositionPath"], row["layerIndex"]))

    compositions = []
    for row in capacity.get("compositions", []):
        compositions.append(
            {
                "id": row["compositionId"],
                "path": row["compositionPath"],
                "width": row["width"],
                "height": row["height"],
                "durationSeconds": row["durationSeconds"],
                "frameRate": row["frameRate"],
                "frameCount": row["frameCount"],
                "workAreaStartSeconds": row["workAreaStartSeconds"],
                "workAreaDurationSeconds": row["workAreaDurationSeconds"],
                "workAreaFrameCount": row["workAreaFrameCount"],
                "directEditableTextFields": len(row["directEditableTextFields"]),
                "recursiveEditableTextFields": len(row["recursiveEditableTextFields"]),
                "maxSimultaneouslyEnabledRecursiveTextFields": row[
                    "maxSimultaneouslyEnabledRecursiveTextFields"
                ],
                "directVisualMediaInputs": len(row["directVisualMediaInputs"]),
                "totalIndependentVisualMediaInputs": row[
                    "totalIndependentVisualMediaInputs"
                ],
                "maxSimultaneouslyEnabledDirectInputs": row[
                    "maxSimultaneouslyEnabledDirectInputs"
                ],
                "maxSimultaneouslyEnabledRecursiveVisualInputs": row[
                    "maxSimultaneouslyEnabledRecursiveVisualInputs"
                ],
                "unresolvedCount": len(row["unresolved"]),
                "recursiveTextFieldIds": [
                    field["id"] for field in row["recursiveEditableTextFields"]
                ],
                "recursiveVisualMediaInputs": [
                    {
                        "id": media["id"],
                        "kind": media["kind"],
                        "path": media.get("path"),
                        "evidence": media.get("evidence"),
                    }
                    for media in row["recursiveVisualMediaInputs"]
                ],
            }
        )
    compositions.sort(key=lambda row: (row["path"], row["id"]))
    return {
        "id": project_id,
        "batchId": batch_id,
        "resultStatus": result_status,
        "evidenceStatus": capacity["evidenceStatus"],
        "sourceProjectName": source_path.name,
        "sourceProjectSha256": source_hash,
        "sourceUnchanged": True,
        "capacityReport": file_source(capacity_path),
        "projectSummary": capacity.get("projectSummary") or {},
        "reportedCompositionCount": len(compositions),
        "compositions": compositions,
        "textFields": text_fields,
        "capacityEnvelope": {
            "maxTotalIndependentVisualMediaInputs": max(
                (row["totalIndependentVisualMediaInputs"] for row in compositions),
                default=0,
            ),
            "maxSimultaneouslyEnabledRecursiveVisualInputs": max(
                (row["maxSimultaneouslyEnabledRecursiveVisualInputs"] for row in compositions),
                default=0,
            ),
            "maxRecursiveEditableTextFields": max(
                (row["recursiveEditableTextFields"] for row in compositions), default=0
            ),
            "maxDurationSeconds": max(
                (row["durationSeconds"] for row in compositions), default=0
            ),
        },
    }


def merge_project(
    index: dict, project: dict, capacity_path: Path, *, replace: bool = False
) -> dict:
    existing = {row["id"]: row for row in index.get("projects", [])}
    if project["id"] in existing and not replace:
        raise ValueError(f"technical project already exists: {project['id']}")
    index = json.loads(json.dumps(index))
    if replace:
        prior = existing.get(project["id"])
        if prior and prior.get("sourceProjectSha256") != project.get("sourceProjectSha256"):
            raise ValueError("replacement project source hash differs")
        index["projects"] = [
            row for row in index["projects"] if row["id"] != project["id"]
        ]
    index["projects"].append(project)
    index["projects"].sort(key=lambda row: row["id"])
    supplemental = index.setdefault("sourceReports", {}).setdefault(
        "supplementalCapacityReports", []
    )
    if replace:
        supplemental[:] = [
            row for row in supplemental if row.get("projectId") != project["id"]
        ]
    supplemental.append({"projectId": project["id"], **file_source(capacity_path)})
    supplemental.sort(key=lambda row: row["projectId"])
    index["counts"] = {
        "projects": len(index["projects"]),
        "compositions": sum(len(row["compositions"]) for row in index["projects"]),
        "textFields": sum(len(row["textFields"]) for row in index["projects"]),
    }
    validate_technical_index(index)
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--capacity", type=Path, required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--result-status", default="source_bound_static_ast")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() and args.output.resolve() != args.index.resolve():
        raise SystemExit(f"Refusing to overwrite existing output: {args.output}")
    capacity = json.loads(args.capacity.read_text())
    index = json.loads(args.index.read_text())
    project = project_from_capacity(
        capacity,
        project_id=args.project_id,
        batch_id=args.batch_id,
        result_status=args.result_status,
        capacity_path=args.capacity,
    )
    merged = merge_project(index, project, args.capacity, replace=args.replace)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(args.output)
    print(json.dumps({"projectId": args.project_id, "counts": merged["counts"]}, indent=2))


if __name__ == "__main__":
    main()
