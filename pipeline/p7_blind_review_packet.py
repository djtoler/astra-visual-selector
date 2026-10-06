#!/usr/bin/env python3
"""Create a compact blind review batch from the complete P5 candidate ledger.

Membership comes only from P5. Semantic similarity orders already-admitted
candidates for review and cannot establish fit, selection, or render authority.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from . import storypackage_candidate_gallery as gallery
from . import visualtask_batch_matching as batch
from . import visualtask_matching as matching
from .matching_contract_gate import enforce_contracts


def _read(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _query(task: dict[str, Any]) -> str:
    candidates = task["templateResult"]["candidates"]
    contract = (candidates[0]["fitAssessment"]["evidence"].get("taskContract") if candidates else {}) or {}
    parts = [task.get("quote"), contract.get("primaryPresentationOperation"),
             " ".join(contract.get("presentationOperations") or []), contract.get("job")]
    return " ".join(str(value) for value in parts if value)


def _order_scores(tasks: list[dict[str, Any]]) -> tuple[dict[str, dict[str, float]], dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for task in tasks:
        for candidate in task["templateResult"]["candidates"]:
            record = candidate["fitAssessment"]["evidence"].get("catalogRecord")
            if record:
                records[candidate["candidateId"]] = record
    if not records:
        return {task["taskId"]: {} for task in tasks}, {
            "stage": "no_admitted_candidates", "scope": "ordering_only_not_admission_fit_selection_or_rendering"}
    ordered_ids = sorted(records)
    raw, receipt = gallery._local_relevance([_query(task) for task in tasks], [records[key] for key in ordered_ids])
    return {
        task["taskId"]: {candidate_id: row.get(candidate_id, 0.0) for candidate_id in ordered_ids}
        for task, row in zip(tasks, raw)
    }, receipt


def _write_ui_bundle(packet: dict[str, Any], output_path: Path) -> dict[str, str]:
    """Adapt the packet to the established review UI and storage API."""
    wrapped = [candidate for task in packet["tasks"] for candidate in task["reviewCandidates"]]
    if not wrapped:
        raise ValueError("blind packet has no candidate carrying projection source bindings")
    contract = wrapped[0]["candidate"]["fitAssessment"]["evidence"]["taskContract"]
    adapter_path = Path(contract["sourceBindings"]["adapter"]["path"])
    proposals_path = Path(contract["sourceBindings"]["taskProposals"]["path"])
    ui_tasks = []
    for row in packet["tasks"]:
        ui_candidates, task_contract = [], {}
        for representative in row["reviewCandidates"]:
            candidate = copy.deepcopy(representative["candidate"])
            task_contract = candidate["fitAssessment"]["evidence"]["taskContract"]
            record = candidate["fitAssessment"]["evidence"].get("catalogRecord") or {}
            candidate.update({
                "name": record.get("title") or candidate["candidateId"],
                "familyRepresentative": True, "representedFamily": representative["family"],
                "representedFamilyMemberIds": representative["familyMemberIds"],
                "p7CandidateSha256": representative["candidateSha256"],
            })
            ui_candidates.append(candidate)
        ui_tasks.append({
            "taskId": row["taskId"], "id": row["taskId"], "job": row["matchingJob"],
            "quote": row["quote"], "sourceBeatIds": ([row["sourceBeatId"]] if row.get("sourceBeatId") else []),
            "presentationOperations": task_contract.get("presentationOperations") or [],
            "primaryPresentationOperation": task_contract.get("primaryPresentationOperation"),
            "candidateCount": row["candidatePoolCount"], "candidates": ui_candidates,
            "candidateStatus": "p7_blind_unresolved_family_representatives" if ui_candidates else "no_admitted_candidate",
            "noTemplateReason": "Review the explicit no-template route." if not ui_candidates else None,
        })
    gallery_path = output_path.with_name("p7-ui-gallery.json")
    queue_path = output_path.with_name("p7-ui-focused-queue.json")
    diversity_path = output_path.with_name("p7-ui-diversity.json")
    review_path = output_path.with_name("p7-ui-review.json")
    gallery_artifact = {
        "schemaVersion": 1, "packageId": packet["packageId"],
        "purpose": "p7_blind_exact_candidate_family_representative_review",
        "activationState": "review_only_not_connected", "selectionAuthorized": False,
        "renderingAuthorized": False, "fitValidated": False,
        "sources": {"adapter": batch._source(adapter_path), "taskProposals": batch._source(proposals_path)},
        "tasks": ui_tasks, "clipRoutes": [], "uncoveredNarratorClaims": 0,
        "counts": {"taskProposals": len(ui_tasks), "tasksWithCandidates": sum(bool(r["candidates"]) for r in ui_tasks),
                   "tasksWithoutCandidates": sum(not r["candidates"] for r in ui_tasks),
                   "candidateCards": sum(len(r["candidates"]) for r in ui_tasks), "sourceClipRoutes": 0},
        "boundary": packet["boundary"],
    }
    gallery_path.write_text(json.dumps(gallery_artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    queue_artifact = {
        "schemaVersion": 1, "packageId": packet["packageId"], "purpose": "p7_blind_review_batch_queue",
        "activationState": "review_only_not_connected", "selectionAuthorized": False,
        "renderingAuthorized": False, "fitValidated": False,
        "taskIds": [row["taskId"] for row in ui_tasks], "fullQueuePreserved": True,
        "batch": packet["batch"], "boundary": packet["boundary"],
    }
    queue_path.write_text(json.dumps(queue_artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    diversity_artifact = {
        "schemaVersion": 1, "packageId": packet["packageId"], "purpose": "p7_blind_family_representative_audit",
        "activationState": "review_only_not_connected", "selectionAuthorized": False,
        "renderingAuthorized": False, "fitValidated": False,
        "sourceGallerySha256": hashlib.sha256(gallery_path.read_bytes()).hexdigest(),
        "sourceFocusedQueueSha256": hashlib.sha256(queue_path.read_bytes()).hexdigest(),
        "tasks": [{
            "taskId": row["taskId"], "displayedFamilyCount": len(row["candidates"]),
            "admittedFamilyCount": next(item["reviewableFamilyCount"] for item in packet["tasks"] if item["taskId"] == row["taskId"]),
            "hiddenAdmittedFamilies": next(item["omittedFamilies"] for item in packet["tasks"] if item["taskId"] == row["taskId"]),
            "focusedReviewStrategy": "top_source_neutral_semantic_ordered_exact_representative_per_distinct_admitted_family",
            "focusedReviewCandidates": copy.deepcopy(row["candidates"]),
        } for row in ui_tasks],
        "counts": {"focusedTasks": len(ui_tasks), "candidateCards": sum(len(row["candidates"]) for row in ui_tasks)},
        "boundary": packet["boundary"],
    }
    diversity_path.write_text(json.dumps(diversity_artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    return {"gallery": str(gallery_path), "focusedQueue": str(queue_path),
            "diversity": str(diversity_path), "review": str(review_path)}


def build(*, ledger_path: Path, output_path: Path, batch_index: int = 0,
          tasks_per_batch: int = 20, candidates_per_task: int = 4) -> dict[str, Any]:
    # This packet is an internal stage of the registered held-out integration.
    # Do not mutate the frozen P0 entrypoint registry for an evaluation helper.
    receipt = enforce_contracts("heldout_matching_integration.build")
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 0
           for value in (batch_index, tasks_per_batch, candidates_per_task)):
        raise ValueError("batch controls must be nonnegative integers")
    if tasks_per_batch == 0 or candidates_per_task == 0:
        raise ValueError("blind review batches require at least one task and candidate slot")
    ledger_path = Path(ledger_path).resolve()
    ledger = _read(ledger_path)
    batch.validate(ledger)
    tasks = ledger["tasks"]
    scores, ordering_receipt = _order_scores(tasks)
    start = batch_index * tasks_per_batch
    chosen_tasks = tasks[start:start + tasks_per_batch]
    rows = []
    for task in chosen_tasks:
        candidates = task["templateResult"]["candidates"]
        by_family: dict[str, list[dict[str, Any]]] = {}
        for candidate in candidates:
            if candidate["fitAssessment"]["verdict"] == "incompatible":
                continue
            by_family.setdefault(matching.C._family(candidate["candidateId"]), []).append(candidate)
        representatives = []
        for family, members in by_family.items():
            members = sorted(members, key=lambda row: (-scores[task["taskId"]].get(row["candidateId"], 0.0), row["candidateId"]))
            chosen = members[0]
            representatives.append({
                "family": family,
                "candidateId": chosen["candidateId"],
                "candidateSha256": batch._digest(chosen),
                "orderingScore": scores[task["taskId"]].get(chosen["candidateId"], 0.0),
                "fitVerdict": chosen["fitAssessment"]["verdict"],
                "nativeFitUnknown": chosen["fitAssessment"]["evidence"]["nativeFitUnknown"],
                "familyMemberCount": len(members),
                "familyMemberIds": [row["candidateId"] for row in members],
                "candidate": copy.deepcopy(chosen),
            })
        representatives.sort(key=lambda row: (-row["orderingScore"], row["family"], row["candidateId"]))
        displayed = representatives[:candidates_per_task]
        rows.append({
            "taskId": task["taskId"], "taskSha256": batch._digest(task),
            "sourceBeatId": task.get("sourceBeatId"), "matchingJob": task.get("matchingJob"),
            "quote": task.get("quote"), "routeDisposition": (
                candidates[0]["fitAssessment"]["evidence"]["taskContract"].get("routeDisposition") if candidates else None),
            "candidatePoolCount": len(candidates), "reviewableFamilyCount": len(representatives),
            "reviewCandidates": displayed,
            "omittedFamilyCount": len(representatives) - len(displayed),
            "omittedFamilies": [row["family"] for row in representatives[candidates_per_task:]],
            "noTemplateReviewRequired": not candidates,
        })
    total_batches = math.ceil(len(tasks) / tasks_per_batch)
    artifact = {
        "schemaVersion": 1, "packageId": ledger["storyId"],
        "purpose": "p7_blind_exact_candidate_family_representative_review",
        "activationState": "review_only_not_connected", "selectionAuthorized": False,
        "renderingAuthorized": False, "fitValidated": False, "humanReviewed": False,
        "contractEnforcementReceipt": receipt,
        "sources": {"ledger": batch._source(ledger_path)},
        "orderingReceipt": ordering_receipt,
        "batch": {"index": batch_index, "tasksPerBatch": tasks_per_batch,
                  "candidatesPerTask": candidates_per_task, "totalBatches": total_batches,
                  "taskStart": start, "taskStop": min(start + tasks_per_batch, len(tasks))},
        "counts": {
            "fullTaskCount": len(tasks), "batchTaskCount": len(rows),
            "reviewCards": sum(len(row["reviewCandidates"]) for row in rows),
            "noTemplateRows": sum(row["noTemplateReviewRequired"] for row in rows),
            "fullCandidatePool": sum(len(row["templateResult"]["candidates"]) for row in tasks),
        },
        "tasks": rows,
        "labelContract": {
            "allowedStatuses": ["acceptable", "unacceptable", "conditional", "no_template_preferred", "unreviewed"],
            "exactCandidateBindingRequired": True, "commentAuthority": "evidence_only",
            "selectionAuthorized": False, "renderingAuthorized": False,
        },
        "boundary": "Each card is one exact candidate representing a distinct admitted family. Omitted families and every family member remain bound to the full P5 ledger. Ordering does not validate fit.",
    }
    artifact["contractEnforcementReceipt"]["blindReviewPacket"] = {
        "version": "p7-blind-review-packet@1", "ledgerSha256": artifact["sources"]["ledger"]["sha256"],
        "bodySha256": batch._digest({key: value for key, value in artifact.items() if key != "contractEnforcementReceipt"}),
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    artifact["uiBundle"] = _write_ui_bundle(artifact, output_path)
    artifact["contractEnforcementReceipt"]["blindReviewPacket"]["bodySha256"] = batch._digest(
        {key: value for key, value in artifact.items() if key != "contractEnforcementReceipt"})
    output_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--batch-index", type=int, default=0)
    parser.add_argument("--tasks-per-batch", type=int, default=20)
    parser.add_argument("--candidates-per-task", type=int, default=4)
    args = parser.parse_args()
    result = build(ledger_path=args.ledger, output_path=args.output, batch_index=args.batch_index,
                   tasks_per_batch=args.tasks_per_batch, candidates_per_task=args.candidates_per_task)
    print(json.dumps(result["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
