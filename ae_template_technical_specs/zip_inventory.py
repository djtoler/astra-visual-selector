#!/usr/bin/env python3
"""Freeze AE project entries inside a ZIP without extracting the archive."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, ZipInfo


CHUNK_SIZE = 4 * 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_real_ae_project(info: ZipInfo) -> bool:
    parts = PurePosixPath(info.filename).parts
    return (
        not info.is_dir()
        and PurePosixPath(info.filename).suffix.lower() in {".aep", ".aepx"}
        and "__MACOSX" not in parts
        and not any(part.startswith("._") for part in parts)
    )


def entry_class(name: str) -> str:
    parts = [part.lower() for part in PurePosixPath(name).parts]
    lowered = "/".join(parts)
    if "_duplicates-review" in parts:
        return "duplicate_review"
    if any("adobe after effects auto-save" in part for part in parts) or "auto-save" in lowered or "autosave" in lowered:
        return "autosave"
    if "working-copy" in lowered or "working copy" in lowered:
        return "working_copy"
    if "converted" in lowered or PurePosixPath(name).name.lower().startswith("tmpaetoameproject"):
        return "converted"
    return "primary_candidate"


def hash_entry(archive: ZipFile, info: ZipInfo) -> str:
    digest = hashlib.sha256()
    with archive.open(info, "r") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_inventory(path: Path) -> dict:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    records = []
    with ZipFile(path) as archive:
        entries = sorted((info for info in archive.infolist() if is_real_ae_project(info)), key=lambda info: info.filename.lower())
        for info in entries:
            classification = entry_class(info.filename)
            status = "excluded" if classification in {"duplicate_review", "autosave", "working_copy"} else "inspect"
            records.append(
                {
                    "sourceKind": "zip_entry",
                    "containerPath": str(path),
                    "entryPath": info.filename,
                    "logicalPath": f"zip://{path}!/{info.filename}",
                    "extension": PurePosixPath(info.filename).suffix.lower(),
                    "sizeBytes": info.file_size,
                    "compressedSizeBytes": info.compress_size,
                    "crc32": f"{info.CRC:08x}",
                    "sha256": hash_entry(archive, info),
                    "rawClass": classification,
                    "scopeStatus": status,
                    "scopeReason": classification if status == "excluded" else "archive_project_entry",
                }
            )

    by_hash = defaultdict(list)
    for row in records:
        if row["scopeStatus"] == "inspect":
            by_hash[row["sha256"]].append(row)
    duplicate_groups = []
    for digest, group in sorted(by_hash.items()):
        if len(group) < 2:
            continue
        keeper = min(group, key=lambda row: (len(row["entryPath"]), row["entryPath"].lower()))
        for row in group:
            if row is not keeper:
                row["scopeStatus"] = "excluded"
                row["scopeReason"] = "exact_byte_duplicate"
                row["duplicateOf"] = keeper["logicalPath"]
        duplicate_groups.append(
            {"sha256": digest, "keeper": keeper["logicalPath"], "members": [row["logicalPath"] for row in group]}
        )

    return {
        "schemaVersion": 1,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "source": "read-only ZIP central-directory and entry-stream inspection",
        "archive": {
            "path": str(path),
            "sizeBytes": path.stat().st_size,
            "mtimeNs": path.stat().st_mtime_ns,
            "sha256": sha256_file(path),
        },
        "policy": {
            "archiveIsReadOnly": True,
            "metadataEntriesExcluded": True,
            "entriesExtracted": False,
            "exactByteDuplicates": "keep_one",
            "versionSiblings": "retain_until_native_composition_signatures_are_available",
        },
        "summary": {
            "rawProjectFiles": len(records),
            "rawClassCounts": dict(sorted(Counter(row["rawClass"] for row in records).items())),
            "scopeStatusCounts": dict(sorted(Counter(row["scopeStatus"] for row in records).items())),
            "projectUncompressedBytesHashed": sum(row["sizeBytes"] for row in records),
            "exactDuplicateGroups": len(duplicate_groups),
        },
        "exactDuplicateGroups": duplicate_groups,
        "projects": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing inventory: {output}")
    inventory = build_inventory(args.zip)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(output)
    print(json.dumps(inventory["summary"], indent=2))


if __name__ == "__main__":
    main()

