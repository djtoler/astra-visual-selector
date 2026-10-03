#!/usr/bin/env python3
"""Build a non-destructive bridge between Data and Matching entity rosters."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _unique_index(items: list[dict[str, Any]], field: str, label: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for item in items:
        value = item.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} item is missing non-empty {field}")
        key = normalize(value)
        if not key:
            raise ValueError(f"{label} item normalizes to an empty key: {value!r}")
        if key in index:
            raise ValueError(f"{label} normalized-key collision: {value!r} and {index[key][field]!r}")
        index[key] = item
    return index


def reconcile(
    data: dict[str, Any],
    matching: dict[str, Any],
    *,
    data_source: dict[str, str],
    matching_source: dict[str, str],
    generated_at: str,
) -> dict[str, Any]:
    entities = data.get("entities")
    names = matching.get("names")
    aliases = matching.get("aliases", {})
    if not isinstance(entities, list) or not isinstance(names, list) or not isinstance(aliases, dict):
        raise ValueError("expected Data entities[], Matching names[] and Matching aliases{}")

    data_index = _unique_index(entities, "canonicalName", "Data roster")
    matching_items = [{"canonicalName": name} for name in names]
    matching_index = _unique_index(matching_items, "canonicalName", "Matching roster")

    matching_alias_index: dict[str, str] = {}
    invalid_matching_aliases: list[dict[str, str]] = []
    for surface, target in aliases.items():
        target_key = normalize(target)
        if target_key not in matching_index:
            invalid_matching_aliases.append({"surface": surface, "target": target})
            continue
        surface_key = normalize(surface)
        prior = matching_alias_index.get(surface_key)
        if prior is not None and prior != target:
            raise ValueError(f"Matching alias collision for {surface!r}: {prior!r} vs {target!r}")
        matching_alias_index[surface_key] = target

    data_alias_index: dict[str, dict[str, str]] = {}
    data_alias_collisions: list[dict[str, str]] = []
    for entity in entities:
        for alias in entity.get("aliases", []):
            surface = alias.get("value")
            if not isinstance(surface, str) or not surface.strip():
                continue
            key = normalize(surface)
            resolved = {"entityId": entity["id"], "canonicalName": entity["canonicalName"], "surface": surface}
            prior = data_alias_index.get(key)
            if prior is not None and prior["entityId"] != entity["id"]:
                data_alias_collisions.append({
                    "surface": surface,
                    "firstEntityId": prior["entityId"],
                    "secondEntityId": entity["id"],
                })
            else:
                data_alias_index[key] = resolved

    shared_keys = set(data_index) & set(matching_index)
    aligned: list[dict[str, Any]] = []
    for key in sorted(shared_keys):
        entity = data_index[key]
        matching_name = matching_index[key]["canonicalName"]
        aligned.append({
            "normalizedKey": key,
            "entityId": entity["id"],
            "entityType": entity["type"],
            "dataCanonicalName": entity["canonicalName"],
            "matchingCanonicalName": matching_name,
            "matchMethod": "canonical_normalized",
            "canonicalSpellingDiffers": entity["canonicalName"] != matching_name,
        })

    remaining_data = set(data_index) - shared_keys
    remaining_matching = set(matching_index) - shared_keys

    # Resolve cross-roster surface/canonical differences through explicit aliases only.
    for data_key in sorted(list(remaining_data)):
        target = matching_alias_index.get(data_key)
        if target is None:
            continue
        target_key = normalize(target)
        if target_key not in remaining_matching:
            continue
        entity = data_index[data_key]
        aligned.append({
            "normalizedKey": target_key,
            "entityId": entity["id"],
            "entityType": entity["type"],
            "dataCanonicalName": entity["canonicalName"],
            "matchingCanonicalName": target,
            "matchMethod": "matching_alias",
            "aliasSurface": entity["canonicalName"],
            "canonicalSpellingDiffers": True,
        })
        remaining_data.remove(data_key)
        remaining_matching.remove(target_key)

    for matching_key in sorted(list(remaining_matching)):
        resolved = data_alias_index.get(matching_key)
        if resolved is None:
            continue
        data_key = normalize(resolved["canonicalName"])
        if data_key not in remaining_data:
            continue
        entity = data_index[data_key]
        matching_name = matching_index[matching_key]["canonicalName"]
        aligned.append({
            "normalizedKey": matching_key,
            "entityId": entity["id"],
            "entityType": entity["type"],
            "dataCanonicalName": entity["canonicalName"],
            "matchingCanonicalName": matching_name,
            "matchMethod": "data_alias",
            "aliasSurface": matching_name,
            "canonicalSpellingDiffers": True,
        })
        remaining_data.remove(data_key)
        remaining_matching.remove(matching_key)

    data_only = [
        {
            "entityId": data_index[key]["id"],
            "entityType": data_index[key]["type"],
            "canonicalName": data_index[key]["canonicalName"],
            "disposition": (
                "matching_scope_review_required"
                if data_index[key]["type"] == "person"
                else "retain_in_data_context_only_unless_visual_task_requires_it"
            ),
        }
        for key in sorted(remaining_data)
    ]
    matching_only = [
        {
            "canonicalName": matching_index[key]["canonicalName"],
            "disposition": "data_entity_resolution_request",
        }
        for key in sorted(remaining_matching)
    ]
    spelling = [item for item in aligned if item["canonicalSpellingDiffers"]]

    return {
        "schemaVersion": "1.0.0",
        "kind": "entity-roster-reconciliation",
        "generatedAt": generated_at,
        "policy": {
            "dataAuthority": "stable entity IDs, typed context, evidence and reviewed alias state",
            "matchingAuthority": "compact artist-name gazetteer for deterministic extraction",
            "automaticPromotion": False,
            "matchingRuntimeRosterChanged": False,
        },
        "inputs": {
            "data": data_source,
            "matching": matching_source,
        },
        "counts": {
            "dataEntities": len(entities),
            "matchingNames": len(names),
            "aligned": len(aligned),
            "canonicalNormalizedMatches": sum(x["matchMethod"] == "canonical_normalized" for x in aligned),
            "aliasMatches": sum(x["matchMethod"] != "canonical_normalized" for x in aligned),
            "canonicalSpellingDifferences": len(spelling),
            "dataOnly": len(data_only),
            "matchingOnly": len(matching_only),
            "invalidMatchingAliases": len(invalid_matching_aliases),
            "dataAliasCollisions": len(data_alias_collisions),
        },
        "aligned": sorted(aligned, key=lambda x: (x["matchingCanonicalName"].casefold(), x["entityId"])),
        "canonicalSpellingDifferences": spelling,
        "dataOnly": data_only,
        "matchingOnly": matching_only,
        "invalidMatchingAliases": invalid_matching_aliases,
        "dataAliasCollisions": data_alias_collisions,
        "acceptance": {
            "inputsReconstructed": len(aligned) + len(data_only) == len(entities)
            and len(aligned) + len(matching_only) == len(names),
            "noNormalizedCollisions": not data_alias_collisions,
            "allMatchingAliasesResolve": not invalid_matching_aliases,
            "passed": (
                len(aligned) + len(data_only) == len(entities)
                and len(aligned) + len(matching_only) == len(names)
                and not data_alias_collisions
                and not invalid_matching_aliases
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-roster", type=Path, required=True)
    parser.add_argument("--matching-roster", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--data-branch", required=True)
    parser.add_argument("--data-commit", required=True)
    parser.add_argument("--matching-branch", required=True)
    parser.add_argument("--matching-commit", required=True)
    args = parser.parse_args()

    data = json.loads(args.data_roster.read_text())
    matching = json.loads(args.matching_roster.read_text())
    result = reconcile(
        data,
        matching,
        data_source={
            "path": "hiphop-research-engine/config/roster_from_csv_v1.json",
            "branch": args.data_branch,
            "commit": args.data_commit,
            "sha256": sha256(args.data_roster),
            "registryId": data.get("registryId", ""),
            "registryVersion": str(data.get("registryVersion", "")),
        },
        matching_source={
            "path": "grammar/entity-roster.json",
            "branch": args.matching_branch,
            "commit": args.matching_commit,
            "sha256": sha256(args.matching_roster),
            "snapshotAt": matching.get("_snapshotAt", ""),
        },
        generated_at=args.generated_at,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"output": str(args.output), "counts": result["counts"], "passed": result["acceptance"]["passed"]}))
    return 0 if result["acceptance"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
