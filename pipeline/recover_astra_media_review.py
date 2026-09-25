#!/usr/bin/env python3
"""Reconstruct a live ui5-media review after its local-only save path failed.

The browser still rendered the ordered candidate queues after every W decision.
For each tier, a W removes a card and the next candidate backfills until ten are
visible or the queue is exhausted.  The recovery file records that final visible
frontier, which is sufficient to reconstruct the entity-scoped corrections and
verify them by replaying the same visibility rule.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def tiers(data: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for brief in data["briefs"]:
        name = brief["brief"]
        if brief.get("group"):
            out[f"{name}::group"] = brief["group"]
        for entity, cards in brief.get("individual", {}).items():
            out[f"{name}::e:{entity}"] = cards
    return out


def infer(data: dict, recovery: dict) -> list[dict]:
    show = int(data["show"])
    observed = recovery["visibleAfterReview"]
    found: dict[tuple[str, str], dict] = {}

    for key, cards in tiers(data).items():
        visible = observed.get(key, [])
        ids = [card["id"] for card in cards]
        entity_by_id = {card["id"]: card["entity"] for card in cards}
        missing = [asset_id for asset_id in visible if asset_id not in entity_by_id]
        if missing:
            raise ValueError(f"{key}: observed IDs are absent from data.json: {missing}")

        if not visible:
            frontier = len(ids)
        elif len(visible) < show:
            frontier = len(ids)
        else:
            frontier = max(ids.index(asset_id) for asset_id in visible) + 1

        keep = set(visible)
        for asset_id in ids[:frontier]:
            if asset_id in keep:
                continue
            entity = entity_by_id[asset_id]
            found[(asset_id, entity.lower())] = {
                "assetId": asset_id,
                "entity": entity,
            }

    return sorted(found.values(), key=lambda row: (row["entity"].lower(), row["assetId"]))


def replay(data: dict, recovery: dict, wrong: list[dict]) -> list[str]:
    show = int(data["show"])
    observed = recovery["visibleAfterReview"]
    blocked = {(row["assetId"], row["entity"].lower()) for row in wrong}
    errors = []
    for key, cards in tiers(data).items():
        actual = [
            card["id"]
            for card in cards
            if (card["id"], card["entity"].lower()) not in blocked
        ][:show]
        expected = observed.get(key, [])
        if actual != expected:
            errors.append(f"{key}: expected {expected}, replayed {actual}")
    return errors


def note_document(recovery: dict) -> dict:
    briefs: dict[str, dict] = {}
    for row in recovery["notes"]:
        current = briefs.setdefault(row["brief"], {"note": "", "entityNotes": {}})
        if row["tier"] == "__brief":
            current["note"] = row["text"]
        else:
            current["entityNotes"][row["tier"]] = row["text"]
    return {"briefs": briefs}


def merge_corrections(existing: dict, recovered: list[dict]) -> dict:
    rows = {}
    for row in list(existing.get("wrong", [])) + list(recovered):
        rows[(row["assetId"], row["entity"].lower())] = {
            "assetId": row["assetId"],
            "entity": row["entity"],
        }
    wrong = sorted(rows.values(), key=lambda row: (row["entity"].lower(), row["assetId"]))
    return {
        **existing,
        "_count": len(wrong),
        "_recoveredAt": "2026-09-25",
        "_recoveredFrom": "astra-media-review-recovered-decisions-2026-09-25.json",
        "wrong": wrong,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-data", required=True, type=Path)
    parser.add_argument("--recovery", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    data = json.loads(args.review_data.read_text())
    recovery = json.loads(args.recovery.read_text())
    wrong = infer(data, recovery)
    errors = replay(data, recovery, wrong)
    if errors:
        raise SystemExit("replay failed:\n" + "\n".join(errors))
    if len(wrong) != recovery["liveState"]["wrongCount"]:
        raise SystemExit(
            f"wrong-count mismatch: reconstructed {len(wrong)}, "
            f"live UI reported {recovery['liveState']['wrongCount']}"
        )

    output = {
        "schemaVersion": 1,
        "source": str(args.recovery),
        "verification": {
            "reportedWrongCount": recovery["liveState"]["wrongCount"],
            "reconstructedWrongCount": len(wrong),
            "replayErrors": 0,
            "noteCount": len(recovery["notes"]),
        },
        "wrong": wrong,
        "notes": note_document(recovery),
    }
    args.out.write_text(json.dumps(output, indent=2) + "\n")
    print(
        f"recovered {len(wrong)} entity corrections and "
        f"{len(recovery['notes'])} notes; replay matched every tier"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
