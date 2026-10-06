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
    from . import storypackage_candidate_gallery as shared_gallery
    from . import focused_review_queue as shared_queue
    from . import visualtask_batch_matching as batch
except ImportError:
    from matching_contract_gate import enforce_contracts
    import storypackage_candidate_gallery as shared_gallery
    import focused_review_queue as shared_queue
    import visualtask_batch_matching as batch


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


def build(queue_path: Path, review_path: Path, *, gallery_path: Path | None = None) -> dict[str, Any]:
    contract_receipt = enforce_contracts("focused_review_reconciliation.build")
    queue = json.loads(queue_path.read_text())
    review = json.loads(review_path.read_text())
    ledger_mode = gallery_path is not None or 'ledgerTaskReferences' in queue or 'focusedQueue' in queue.get('contractEnforcementReceipt', {})
    gallery = None
    if ledger_mode:
        if gallery_path is None:
            raise ValueError('ledger feedback requires the exact source gallery')
        shared_queue.validate(queue, gallery_path)
        gallery = shared_gallery._ledger_read(gallery_path)
        shared_gallery.validate(gallery)
        if (review.get('sourceGallerySha256') != _sha(gallery_path)
                or review.get('packageId') != gallery['packageId']
                or review.get('selectionAuthorized') is not False
                or review.get('renderingAuthorized') is not False):
            raise ValueError('saved feedback gallery hash/identity/review boundary mismatch')
        rows_by_id = {r['taskId']: r for r in gallery['tasks']}
        for key, decision in (review.get('decisions') or {}).items():
            task_id, candidate_id = decision.get('taskId'), decision.get('candidateId')
            if task_id not in queue['taskIds'] or key != f'{task_id}::{candidate_id}' or decision.get('id') != key:
                raise ValueError('saved feedback task/candidate identity mismatch')
            row = rows_by_id[task_id]
            inspectable = {r['candidateId'] for r in row['templateResult']['candidates'] if r['fitAssessment']['verdict'] != 'incompatible'}
            if candidate_id not in inspectable and not (candidate_id is None and not inspectable):
                raise ValueError('saved feedback candidate is not a reviewable ledger member')
    task_ids = queue.get("taskIds") or []
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("focused queue contains duplicate task ids")
    decisions = review.get("decisions") or {}
    rows = []
    for task_id in task_ids:
        matches = [value for value in decisions.values() if value.get("taskId") == task_id]
        if (not ledger_mode and len(matches) != 1) or (ledger_mode and not matches):
            raise ValueError(f"focused task must have exactly one persisted review record: {task_id}: {len(matches)}")
        for decision in matches:
            comment = str(decision.get("comment") or "").strip()
            if not comment and (not ledger_mode or decision.get('status') != 'unreviewed'):
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
    artifact = {
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
            "reconciledTasks": len({r["taskId"] for r in rows}),
            "eachTaskExactlyOnce": True,
            "commentsPresentForEveryTask": all(any(r["comment"] for r in rows if r["taskId"] == task_id) for task_id in task_ids),
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

    if ledger_mode:
        artifact['sources'] = {'focusedQueue': batch._source(queue_path), 'candidateReview': batch._source(review_path), 'gallery': batch._source(gallery_path)}
        artifact['contractEnforcementReceipt']['candidateDisplay'] = {
            'galleryDisplaySha256': gallery['contractEnforcementReceipt']['candidateDisplay']['bodySha256'],
            'focusedQueueSha256': _sha(queue_path), 'sourceGallerySha256': _sha(gallery_path),
            'ledgerTaskReferences': queue['ledgerTaskReferences']}
        for row in rows:
            row['ledgerTaskSha256'] = queue['ledgerTaskReferences'][row['taskId']]
        artifact['humanReviewed'] = False  # No queue/package review state inferred from comments or sampling.
    return artifact


def validate(artifact: dict[str, Any], queue_path: Path, review_path: Path, *, gallery_path: Path) -> None:
    if artifact != build(queue_path, review_path, gallery_path=gallery_path):
        raise ValueError('review reconciliation does not round-trip from exact saved feedback')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--gallery", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build(args.queue, args.review, gallery_path=args.gallery)
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps(artifact["coverage"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
