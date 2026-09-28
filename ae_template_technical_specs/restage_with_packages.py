#!/usr/bin/env python3
"""Restage a prepared native batch with each source's adjacent template package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil


LIBRARY_ROOTS = (
    Path("/Users/dwaynetoler/Downloads/Archive 2"),
    Path("/Users/dwaynetoler/timeline/templates"),
    Path("/Users/dwaynetoler/timeline/Archive 3"),
)
ARCHIVE_2_CATEGORIES = {"Carousels & Slideshows", "Documents & Screens", "Lists & Titles"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_root(source: Path) -> Path:
    for root in LIBRARY_ROOTS:
        try:
            relative = source.relative_to(root)
        except ValueError:
            continue
        parts = relative.parts
        depth = 2 if root.name == "Archive 2" and parts[0] in ARCHIVE_2_CATEGORIES else 1
        return root.joinpath(*parts[:depth])
    return source.parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch_dir", type=Path)
    args = parser.parse_args()
    batch = args.batch_dir.resolve()
    manifest_path = batch / "batch.json"
    manifest = json.loads(manifest_path.read_text())
    copied = 0
    for project in manifest["projects"]:
        source = Path(project["source"])
        root = package_root(source)
        destination_root = batch / "staged-packages" / project["id"] / root.name
        shutil.copytree(root, destination_root, dirs_exist_ok=True)
        staged = destination_root / source.relative_to(root)
        if sha256(staged) != project["sha256"]:
            raise SystemExit(f"Staged hash mismatch: {staged}")
        project["packageRoot"] = str(root)
        project["staged"] = str(staged)
        job_path = batch / project["job"]
        job = json.loads(job_path.read_text())
        job["template"] = os.path.relpath(staged, job_path.parent)
        job_path.write_text(json.dumps(job, indent=2, ensure_ascii=False) + "\n")
        copied += 1
    for index, project in enumerate(manifest["projects"]):
        job_path = batch / project["job"]
        job = json.loads(job_path.read_text())
        job["allowed_previous_reports"] = [
            os.path.relpath(batch / "raw" / f"{previous['id']}.json", job_path.parent)
            for previous in manifest["projects"][:index]
        ]
        job_path.write_text(json.dumps(job, indent=2, ensure_ascii=False) + "\n")
    manifest["staging"] = "adjacent_template_packages"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"batch": str(batch), "packagesStaged": copied}, indent=2))


if __name__ == "__main__":
    main()
