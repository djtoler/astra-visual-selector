#!/usr/bin/env python3
"""Reconcile a focused editor queue without converting comments into approvals."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .matching_contract_gate import enforce_contracts
except ImportError:
    from matching_contract_gate import enforce_contracts


THEMES = {
    "broll_route": ("broll", "b-roll"),
    "no_template_required": ("no templates needed", "only broll", "only b-roll"),
    "document_or_screen": ("document/screen", "documents or screens", "tracklist", "track list", "interview evidence"),
    "lyric_presentation": ("lyrics template", "lyric template"),
    "sequence_or_carousel": ("carousel", "multiple mixtapes", "one card then the next"),
    "relationship_or_people": ("familial relationship", "portraits/cards", "visuals of people", "both artists"),
    "transformation": ("transformation", "before and after"),
    "incidental_numbers_not_data": ("nothing to do with data", "counters has no relevance", "no counters", "not comparing"),
    "slot_count_or_media_demand": ("slots", "slot", "cards", "supporting images"),
    "irrelevant_candidate_family": ("irrelevant", "no good", "horrible", "not a good fit"),
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _themes(comment: str) -> list[str]:
    lowered = comment.lower()
    return [name for name, phrases in THEMES.items() if any(phrase in lowered for phrase in phrases)]


def build(queue_path: Path, review_path: Path) -> dict[str, Any]:
    contract_receipt = enforce_contracts("focused_review_reconciliation.build")
    queue = json.loads(queue_path.read_text())
    review = json.loads(review_path.read_text())
    task_ids = queue.get("taskIds") or []
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("focused queue contains duplicate task ids")
    decisions = review.get("decisions") or {}
    rows = []
    for task_id in task_ids:
        matches = [value for value in decisions.values() if value.get("taskId") == task_id]
        if len(matches) != 1:
            raise ValueError(f"focused task must have exactly one persisted review record: {task_id}: {len(matches)}")
        decision = matches[0]
        comment = str(decision.get("comment") or "").strip()
        if not comment:
            raise ValueError(f"focused task lacks editor comment: {task_id}")
        rows.append({
            "taskId": task_id,
            "reviewKey": decision.get("id"),
            "candidateId": decision.get("candidateId"),
            "status": decision.get("status"),
            "comment": comment,
            "calibrationThemes": _themes(comment),
            "selectionAuthorized": False,
            "renderingAuthorized": False,
        })
    theme_counts = Counter(theme for row in rows for theme in row["calibrationThemes"])
    return {
        "schemaVersion": 1,
        "purpose": "Editor-feedback reconciliation evidence for general matching-layer rules",
        "contractEnforcementReceipt": contract_receipt,
        "packageId": review.get("packageId"),
        "sources": {
            "focusedQueue": {"path": str(queue_path), "sha256": _sha(queue_path)},
            "candidateReview": {"path": str(review_path), "sha256": _sha(review_path)},
        },
        "coverage": {
            "expectedTasks": len(task_ids),
            "reconciledTasks": len(rows),
            "eachTaskExactlyOnce": True,
            "commentsPresentForEveryTask": True,
        },
        "themeCounts": dict(sorted(theme_counts.items())),
        "tasks": rows,
        "interpretationPolicy": {
            "commentsAreCalibrationEvidence": True,
            "commentsDoNotAuthorizeSelection": True,
            "commentsDoNotAuthorizeRendering": True,
            "runtimeRulesMustRemainStoryNeutral": True,
        },
        "selectionAuthorized": False,
        "renderingAuthorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build(args.queue, args.review)
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps(artifact["coverage"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
