#!/usr/bin/env python3
"""Derive capacity files for every successful raw report in a batch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from derive_capacity import build_capacity


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch_dir", type=Path)
    parser.add_argument("--evidence", choices=("native", "static"), default="native")
    parser.add_argument("--force", action="store_true", help="Regenerate existing derived capacity files")
    args = parser.parse_args()
    batch = args.batch_dir.resolve()
    manifest = json.loads((batch / "batch.json").read_text())
    raw_dir = "raw" if args.evidence == "native" else "raw-static"
    capacity_dir = "capacity" if args.evidence == "native" else "capacity-static"
    counts = {"complete": 0, "failed": 0, "missing": 0, "reused": 0}
    for project in manifest["projects"]:
        raw = batch / raw_dir / f"{project['id']}.json"
        output = batch / capacity_dir / f"{project['id']}.json"
        if output.is_file() and not args.force:
            counts["reused"] += 1
            continue
        if not raw.is_file():
            counts["missing"] += 1
            continue
        report = json.loads(raw.read_text())
        if not report.get("ok"):
            counts["failed"] += 1
            continue
        capacity = build_capacity(report)
        capacity["nativeReport"]["reportedInspectionProject"] = capacity.get("sourceProject")
        capacity["sourceProject"] = project["source"]
        capacity["sourceSha256"] = project["sha256"]
        capacity["evidenceStatus"] = (
            "fresh_source_bound_native_ae25"
            if args.evidence == "native"
            else "source_bound_static_py_aep"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(capacity, indent=2, ensure_ascii=False) + "\n")
        counts["complete"] += 1
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
