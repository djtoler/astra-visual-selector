#!/usr/bin/env python3
"""Build a deterministic, package-neutral editor calibration queue.

The queue represents every distinct semantic/capability signature in a full
candidate gallery once. It reduces repetitive human review without changing
candidate admission, validating fit, selecting a template, or hiding the full
gallery from optional inspection.
"""

from __future__ import annotations

import argparse
import hashlib
import gzip
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    from .matching_contract_gate import enforce_contracts
    from . import storypackage_candidate_gallery as shared_gallery
    from . import visualtask_batch_matching as batch
except ImportError:
    from matching_contract_gate import enforce_contracts
    import storypackage_candidate_gallery as shared_gallery
    import visualtask_batch_matching as batch


def _read(path: Path) -> dict[str, Any]:
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes())


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _entity_bucket(count: int) -> str:
    if count <= 0:
        return "none"
    if count == 1:
        return "one"
    if count == 2:
        return "two"
    return "three_or_more"


def _signature(task: dict[str, Any]) -> dict[str, Any]:
    contract = task.get("presentationContract") or {}
    return {
        "primaryPresentationOperation": (
            task.get("primaryPresentationOperation")
            or contract.get("primaryOperation")
            or "unspecified"
        ),
        "job": task.get("job") or "unspecified",
        "entityCount": _entity_bucket(int(contract.get("entityCount") or 0)),
        "hasTypedValues": bool(contract.get("hasTypedValues")),
        "hasCohort": bool(contract.get("hasCohort")),
        "hasPerceptibilityConstraint": bool(contract.get("mustBePerceptible")),
        "needsOnScreenText": bool(contract.get("needsOnScreenText")),
        "candidateState": "has_candidates" if task.get("candidates") else "no_candidates",
    }


def _signature_key(signature: dict[str, Any]) -> str:
    return json.dumps(signature, sort_keys=True, separators=(",", ":"))


def build(gallery_path: Path) -> dict[str, Any]:
    receipt = enforce_contracts("focused_review_queue.build")
    gallery = _read(gallery_path)
    if (gallery.get("activationState") != "review_only_not_connected"
            or gallery.get("selectionAuthorized") is not False
            or gallery.get("renderingAuthorized") is not False
            or gallery.get("fitValidated") is not False):
        raise ValueError("candidate gallery review boundary is invalid")

    display = gallery.get('contractEnforcementReceipt', {}).get('candidateDisplay')
    ledger_mode = display is not None or 'ledger' in gallery.get('sources', {})
    if ledger_mode:
        shared_gallery.validate(gallery)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    signatures: dict[str, dict[str, Any]] = {}
    for task in gallery.get("tasks") or []:
        signature = _signature(task)
        if ledger_mode:
            # Sampling observes existing ledger evidence; no candidate retrieval.
            members = task['templateResult']['candidates']
            signature['matchingJob'] = task['matchingJob']
            signature['fitStates'] = sorted({r['fitAssessment']['verdict'] for r in members})
            signature['declaredDuties'] = [{'requirementId': d['requirementId'], 'value': d['value']} for d in members[0]['fitAssessment']['evidence']['requirements']] if members else []
        key = _signature_key(signature)
        signatures[key] = signature
        grouped[key].append(task)

    representatives = []
    for key in sorted(grouped):
        rows = sorted(
            grouped[key],
            key=lambda row: hashlib.sha256(
                f"{gallery.get('packageId')}:{row['taskId']}".encode("utf-8")
            ).hexdigest(),
        )
        chosen = rows[0]
        representatives.append({
            "taskId": chosen["taskId"],
            "signature": signatures[key],
            "representedTaskCount": len(rows),
            "representedTaskIds": [row["taskId"] for row in rows],
        })

    representatives.sort(key=lambda row: row["taskId"])
    all_task_ids = [row["taskId"] for row in gallery.get("tasks") or []]
    represented = [task_id for row in representatives for task_id in row["representedTaskIds"]]
    if sorted(represented) != sorted(all_task_ids) or len(represented) != len(set(represented)):
        raise ValueError("focused review signatures do not cover every gallery task exactly once")

    artifact = {
        "schemaVersion": 1,
        "packageId": gallery.get("packageId"),
        "purpose": "package_neutral_semantic_capability_calibration_queue",
        "activationState": "review_only_not_connected",
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "fitValidated": False,
        "contractEnforcementReceipt": receipt,
        "sourceGallerySha256": _sha(gallery_path),
        "taskIds": [row["taskId"] for row in representatives],
        "representatives": representatives,
        "counts": {
            "fullGalleryTasks": len(all_task_ids),
            "focusedReviewTasks": len(representatives),
            "representedSignatures": len(representatives),
            "tasksDeferredAsSameSignature": len(all_task_ids) - len(representatives),
        },
        "coverageBasis": (
            "One deterministic task per distinct primary-operation, job, entity-count, "
            "typed-value, cohort, perceptibility, text and candidate-state signature."
        ),
        "fullQueuePreserved": True,
        "boundary": (
            "Focused review reduces repetitive calibration only. The complete gallery remains "
            "available, and no fit, selection or rendering authority is implied."
        ),
    }

    if ledger_mode:
        artifact['humanReviewed'] = False
        artifact['ledgerTaskReferences'] = dict(display['ledgerTaskReferences'])
        artifact['contractEnforcementReceipt']['focusedQueue'] = {
            'galleryDisplaySha256': display['bodySha256'],
            'reviewerSequence': list(gallery['reviewerSequence']),
            'fullQueuePreserved': True}
        artifact['contractEnforcementReceipt']['focusedQueue']['bodySha256'] = batch._digest(artifact)
    return artifact


def validate(queue: dict[str, Any], gallery_path: Path) -> None:
    if queue != build(gallery_path):
        raise ValueError('focused queue does not replay from exact shared gallery')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gallery", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.gallery.resolve())
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
