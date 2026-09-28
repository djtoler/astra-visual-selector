#!/usr/bin/env python3
"""Materialize source-matched prior inspections as a resumable capacity batch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil

from derive_capacity import build_capacity


def slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "template"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matches", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"Refusing to overwrite batch: {output}")

    audit = json.loads(args.matches.read_text())
    selected = [
        row for row in audit["projects"]
        if not row["alreadyInBatch01"] and row["status"] == "existing_native_exact_structural_match"
    ]
    used: set[str] = set()
    manifest_projects = []
    for row in selected:
        source = Path(row["sourceProject"])
        project_id = slug(source.stem)
        if project_id in used:
            project_id = f"{project_id}-{row['sourceSha256'][:8]}"
        used.add(project_id)
        static_source = Path(row["staticReport"])
        native_source = Path(row["exactMatches"][0]["reports"][0])
        raw_static = output / "raw-static" / f"{project_id}.json"
        raw_native = output / "raw-existing" / f"{project_id}.json"
        raw_static.parent.mkdir(parents=True, exist_ok=True)
        raw_native.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(static_source, raw_static)
        shutil.copy2(native_source, raw_native)

        static_capacity = build_capacity(json.loads(raw_static.read_text()))
        static_capacity["sourceProject"] = str(source)
        static_capacity["sourceSha256"] = row["sourceSha256"]
        static_capacity["evidenceStatus"] = "source_bound_static_py_aep"
        write_json(output / "capacity-static" / f"{project_id}.json", static_capacity)

        native_capacity = build_capacity(json.loads(raw_native.read_text()))
        native_capacity["nativeReport"]["reportedInspectionProject"] = native_capacity.get("sourceProject")
        native_capacity["sourceProject"] = str(source)
        native_capacity["sourceSha256"] = row["sourceSha256"]
        native_capacity["evidenceStatus"] = "recovered_native_exact_structural_match"
        write_json(output / "capacity" / f"{project_id}.json", native_capacity)

        manifest_projects.append({
            "id": project_id,
            "source": str(source),
            "sha256": row["sourceSha256"],
            "staticReport": str(raw_static.relative_to(output)),
            "nativeReport": str(raw_native.relative_to(output)),
            "recoveryFingerprint": row["exactMatches"][0]["fingerprint"],
        })

    manifest = {
        "schemaVersion": 1,
        "name": "Batch 02 recovered exact inspections",
        "purpose": "Promote exact current-source structural matches from prior native inspections",
        "rendering": False,
        "saveSourceProjects": False,
        "projects": manifest_projects,
    }
    write_json(output / "batch.json", manifest)
    print(json.dumps({"batch": str(output), "projects": len(manifest_projects)}, indent=2))


if __name__ == "__main__":
    main()
