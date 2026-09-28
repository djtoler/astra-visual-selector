#!/usr/bin/env python3
"""Prepare isolated source copies and jobs for all current projects outside batch 01."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil

from derive_capacity import build_capacity


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "template"


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
    selected = [row for row in audit["projects"] if not row["alreadyInBatch01"]]
    used: set[str] = set()
    projects = []
    for row in selected:
        source = Path(row["sourceProject"])
        project_id = slug(source.stem)
        if project_id in used:
            project_id = f"{project_id}-{row['sourceSha256'][:8]}"
        used.add(project_id)
        staged = output / "staged-projects" / project_id / source.name
        staged.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, staged)

        static_report = None
        if row.get("staticReport"):
            static_report = output / "raw-static" / f"{project_id}.json"
            static_report.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(row["staticReport"], static_report)
            capacity = build_capacity(json.loads(static_report.read_text()))
            capacity["sourceProject"] = str(source)
            capacity["sourceSha256"] = row["sourceSha256"]
            capacity["evidenceStatus"] = "source_bound_static_py_aep"
            write_json(output / "capacity-static" / f"{project_id}.json", capacity)

        job_path = output / "jobs" / f"{project_id}.json"
        job = {
            "template": os.path.relpath(staged, job_path.parent),
            "source_sha256": row["sourceSha256"],
            "disposable_staged_copy": True,
            "inspection_report": f"../raw/{project_id}.json",
            "output_dir": f"../unused-output/{project_id}",
            "font_policy": "substitute_and_flag",
        }
        write_json(job_path, job)
        projects.append({
            "id": project_id,
            "source": str(source),
            "staged": str(staged),
            "sha256": row["sourceSha256"],
            "job": str(job_path.relative_to(output)),
            "priorEvidence": row["status"],
            "staticParserStatus": "complete" if static_report else "failed_unresolved",
            "staticParserError": row.get("parserError"),
        })

    write_json(output / "batch.json", {
        "schemaVersion": 1,
        "name": "Batch 03 all remaining current templates",
        "purpose": "Fresh source-bound native inspection for every current source outside batch 01",
        "rendering": False,
        "saveSourceProjects": False,
        "projects": projects,
    })
    print(json.dumps({
        "batch": str(output),
        "projects": len(projects),
        "staticPassComplete": sum(row["staticParserStatus"] == "complete" for row in projects),
        "staticPassFailed": sum(row["staticParserStatus"] != "complete" for row in projects),
    }, indent=2))


if __name__ == "__main__":
    main()
