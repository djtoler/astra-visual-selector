#!/usr/bin/env python3
"""Freeze a capacity batch so later accuracy scoring uses immutable inputs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


INCLUDE = (
    "batch.json",
    "batch-summary.json",
    "pass-reconciliation.json",
    "rejected-native-association.json",
    "REPORT.md",
    "all-compositions.csv",
    "text-fields.csv",
    "raw-static/*.json",
    "raw-existing/*.json",
    "raw/*.json",
    "rejected-misassociated/*.json",
    "capacity-static/*.json",
    "capacity/*.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch_dir", type=Path)
    args = parser.parse_args()
    batch = args.batch_dir.resolve()
    output = batch / "measurement-freeze.json"
    if output.exists():
        raise SystemExit(f"Refusing to overwrite frozen measurement: {output}")
    paths = set()
    for pattern in INCLUDE:
        paths.update(path for path in batch.glob(pattern) if path.is_file())
    summary = json.loads((batch / "batch-summary.json").read_text())
    if not all(project["sourceUnchanged"] for project in summary["projects"]):
        raise SystemExit("Cannot freeze: at least one source hash changed")
    reconciliation = json.loads((batch / "pass-reconciliation.json").read_text())
    permitted = {
        "two_pass_exact_agreement",
        "static_source_bound_native_incompatible_with_ae25",
        "native_source_bound_static_parser_unresolved",
    }
    statuses = {row["status"] for row in reconciliation["results"]}
    if not statuses <= permitted:
        raise SystemExit(f"Cannot freeze unresolved reconciliation statuses: {sorted(statuses - permitted)}")
    payload = {
        "schemaVersion": 1,
        "frozenAt": datetime.now(timezone.utc).isoformat(),
        "scope": f"{batch.name} technical measurement only; accuracy scoring is not included",
        "renderingPerformed": False,
        "sourceHashesVerifiedUnchanged": True,
        "reconciliationStatuses": {
            row["projectId"]: row["status"] for row in reconciliation["results"]
        },
        "files": [
            {
                "path": str(path.relative_to(batch)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in sorted(paths)
        ],
    }
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "freeze": str(output),
        "fileCount": len(payload["files"]),
        "sourceHashesVerifiedUnchanged": True,
    }, indent=2))


if __name__ == "__main__":
    main()
