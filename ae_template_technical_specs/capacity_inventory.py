#!/usr/bin/env python3
"""Freeze the read-only AE project inventory for the isolated capacity lab."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Iterable

LIBRARY_ROOT = Path("/Users/dwaynetoler/timeline/templates")
CHUNK_SIZE = 4 * 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def raw_class(path: Path, root: Path = LIBRARY_ROOT) -> str:
    relative = path.relative_to(root)
    lowered_parts = [part.lower() for part in relative.parts]
    lowered = "/".join(lowered_parts)
    if "_duplicates-review" in relative.parts:
        return "duplicate_review"
    if any("adobe after effects auto-save" in part for part in lowered_parts) or "auto-save" in path.name.lower() or "autosave" in path.name.lower():
        return "autosave"
    if "working-copy" in lowered or "working copy" in lowered:
        return "working_copy"
    if "converted" in lowered or path.name.lower().startswith("tmpaetoameproject"):
        return "converted"
    return "primary_candidate"


def package_key(path: Path, root: Path = LIBRARY_ROOT) -> str:
    parts = path.relative_to(root).parts
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return parts[0]


def choose_exact_duplicate_keeper(records: Iterable[dict]) -> dict:
    priority = {
        "primary_candidate": 0,
        "converted": 1,
    }
    return min(
        records,
        key=lambda row: (
            priority.get(row["rawClass"], 9),
            len(row["relativePath"]),
            row["relativePath"].lower(),
        ),
    )


def build_inventory(root: Path) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)
    paths = sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".aep", ".aepx"}
        and not path.name.startswith("._")
    )
    records = []
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        stat = path.stat()
        records.append(
            {
                "absolutePath": str(path),
                "relativePath": str(path.relative_to(root)),
                "extension": path.suffix.lower(),
                "sizeBytes": stat.st_size,
                "mtimeNs": stat.st_mtime_ns,
                "sha256": sha256_file(path),
                "rawClass": raw_class(path, root),
                "packageKey": package_key(path, root),
            }
        )

    primary_packages = {
        row["packageKey"]
        for row in records
        if row["rawClass"] == "primary_candidate"
    }
    for row in records:
        classification = row["rawClass"]
        if classification in {"duplicate_review", "autosave", "working_copy"}:
            row["scopeStatus"] = "excluded"
            row["scopeReason"] = classification
        elif classification == "converted" and row["packageKey"] in primary_packages:
            row["scopeStatus"] = "fallback"
            row["scopeReason"] = "converted_copy_with_primary_in_same_package"
        else:
            row["scopeStatus"] = "inspect"
            row["scopeReason"] = "primary_project" if classification == "primary_candidate" else "only_project_class_in_package"

    by_hash = defaultdict(list)
    for row in records:
        if row["scopeStatus"] in {"inspect", "fallback"}:
            by_hash[row["sha256"]].append(row)
    exact_duplicate_groups = []
    for digest, group in sorted(by_hash.items()):
        if len(group) < 2:
            continue
        keeper = choose_exact_duplicate_keeper(group)
        members = []
        for row in group:
            members.append(row["absolutePath"])
            if row is not keeper and row["scopeStatus"] == "inspect":
                row["scopeStatus"] = "excluded"
                row["scopeReason"] = "exact_byte_duplicate"
                row["duplicateOf"] = keeper["absolutePath"]
        exact_duplicate_groups.append(
            {
                "sha256": digest,
                "keeper": keeper["absolutePath"],
                "members": sorted(members),
            }
        )

    records.sort(key=lambda row: row["relativePath"].lower())
    raw_counts = Counter(row["rawClass"] for row in records)
    scope_counts = Counter(row["scopeStatus"] for row in records)
    return {
        "schemaVersion": 1,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "source": "read-only recursive discovery of the user-specified local template root",
        "libraryRoot": str(root),
        "sourceSnapshot": {
            "projectPaths": [row["absolutePath"] for row in records],
            "projectVersions": {
                row["absolutePath"]: {"size": row["sizeBytes"], "mtimeNs": row["mtimeNs"]}
                for row in records
            },
        },
        "policy": {
            "sourcesAreReadOnly": True,
            "excludeClasses": ["duplicate_review", "autosave", "working_copy"],
            "convertedWithPrimaryInSamePackage": "fallback",
            "exactByteDuplicates": "keep_one",
            "versionSiblings": "retain_until_native_composition_signatures_are_available",
        },
        "summary": {
            "rawProjectFiles": len(records),
            "rawClassCounts": dict(sorted(raw_counts.items())),
            "scopeStatusCounts": dict(sorted(scope_counts.items())),
            "sourceBytesHashed": sum(row["sizeBytes"] for row in records),
            "exactDuplicateGroups": len(exact_duplicate_groups),
        },
        "exactDuplicateGroups": exact_duplicate_groups,
        "projects": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=LIBRARY_ROOT)
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing inventory: {output}")
    inventory = build_inventory(args.root)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(output)
    print(json.dumps(inventory["summary"], indent=2))


if __name__ == "__main__":
    main()
