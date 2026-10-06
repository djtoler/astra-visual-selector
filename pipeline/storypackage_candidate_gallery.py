#!/usr/bin/env python3
"""Retrieve review-only template candidates for StoryPackage task proposals."""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import math
import os
import subprocess
from pathlib import Path
from typing import Any

try:
    from . import visualtask_matching as matching
    from . import visualtask_batch_matching as batch
    from .matching_contract_gate import enforce_contracts
except ImportError:
    import visualtask_matching as matching
    import visualtask_batch_matching as batch
    from matching_contract_gate import enforce_contracts


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BINDINGS = ROOT / "grammar" / "bindings.json"
LOCAL_EMBEDDER = ROOT / "pipeline" / "retrieval" / "local_embeddings.swift"


def _read(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _source(path: Path) -> dict[str, Any]:
    path = Path(path).resolve()
    return {"path": path.as_posix(), "sha256": _sha(path), "bytes": path.stat().st_size}


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _embedding_text(record: dict[str, Any]) -> str:
    capability = record.get("capability") or {}
    parts = [
        record.get("title"), record.get("description"), record.get("useWhen"),
        record.get("encoding"), capability.get("asserts"),
        " ".join(record.get("narration") or []),
        " ".join(capability.get("carries") or []),
        " ".join(capability.get("readable") or []),
        capability.get("structure"), capability.get("staging"),
    ]
    return " ".join(str(value) for value in parts if value)


def _local_relevance(queries: list[str], records: list[dict[str, Any]]) -> tuple[list[dict[str, float]], dict[str, Any]]:
    """Order structurally admitted candidates with the established local model.

    The score is never an admission, fit, selection, or rendering signal.
    """
    texts = queries + [_embedding_text(record) for record in records]
    module_cache = Path("/tmp/astra-swift-module-cache")
    module_cache.mkdir(parents=True, exist_ok=True)
    environment = {**os.environ, "CLANG_MODULE_CACHE_PATH": str(module_cache)}
    completed = subprocess.run(
        ["swift", str(LOCAL_EMBEDDER)],
        input=json.dumps({"texts": texts}), text=True, capture_output=True, check=True,
        env=environment,
    )
    result = json.loads(completed.stdout)
    vectors = result["vectors"]

    def cosine(left: list[float], right: list[float]) -> float:
        denominator = math.sqrt(sum(x * x for x in left)) * math.sqrt(sum(x * x for x in right))
        return sum(x * y for x, y in zip(left, right)) / denominator if denominator else 0.0

    template_vectors = vectors[len(queries):]
    scores = [
        {record["id"]: cosine(query_vector, template_vector)
         for record, template_vector in zip(records, template_vectors)}
        for query_vector in vectors[:len(queries)]
    ]
    return scores, {
        "stage": "local_semantic_ordering_after_structured_admission",
        "model": result["model"],
        "dimension": result["dimension"],
        "script": _source(LOCAL_EMBEDDER),
        "scope": "ordering_only_not_admission_fit_selection_or_rendering",
    }


def build(*, proposals_path: Path | None = None, adapter_path: Path | None = None,
          bindings_path: Path = DEFAULT_BINDINGS,
          admissions_path: Path | None = None,
          ledger_path: Path | None = None, ordering_path: Path | None = None) -> dict[str, Any]:
    contract_receipt = enforce_contracts("storypackage_candidate_gallery.build")
    if ledger_path is not None or ordering_path is not None:
        if ledger_path is None or ordering_path is None or proposals_path is not None or adapter_path is not None or admissions_path is not None:
            raise ValueError("reconciled gallery requires only ledger and persisted ordering inputs")
        return _ledger_gallery(ledger_path, ordering_path, contract_receipt)
    if proposals_path is None or adapter_path is None:
        raise ValueError("discovery gallery requires proposals and adapter")
    proposals = _read(proposals_path)
    adapter = _read(adapter_path)
    bindings = _read(bindings_path)
    if proposals.get("activationState") != "review_only_not_connected":
        raise ValueError("candidate gallery requires review-only task proposals")
    if proposals.get("selectionAuthorized") is not False or proposals.get("renderingAuthorized") is not False:
        raise ValueError("task proposals cannot authorize selection or rendering")
    if adapter.get("packageId") != proposals.get("packageId"):
        raise ValueError("adapter and proposal package IDs differ")
    try:
        from .storypackage_adapter import validate as validate_adapter
    except ImportError:
        from storypackage_adapter import validate as validate_adapter
    adapter_validation = validate_adapter(adapter, source_path=adapter_path)
    if (proposals.get("source") or {}).get("sha256") != _sha(adapter_path):
        raise ValueError("proposal adapter source digest is stale")
    try:
        from .storypackage_matching_handoff import build_projection, validate_projection, no_template_reason
    except ImportError:
        from storypackage_matching_handoff import build_projection, validate_projection, no_template_reason
    projection = build_projection(proposals_path, adapter_path, admissions_path=admissions_path)
    validate_projection(projection)
    projected_by_id = {row["id"]: row for row in projection["tasks"]}

    beats = {row["beatId"]: row for row in adapter.get("beats") or []}
    template_pool = {row["id"]: row for row in matching.C.load(content_class="*")}
    proposal_rows = list(proposals.get("taskProposals") or [])
    queries = [
        " ".join(filter(None, [
            projected_by_id[proposal["taskProposalId"]]["quote"],
            " ".join(projected_by_id[proposal["taskProposalId"]]["presentationOperations"]),
            " ".join(
                text for obligation in projected_by_id[proposal["taskProposalId"]]["obligations"]
                for text in obligation.get("mustBePerceptible") or []
            ),
        ]))
        for proposal in proposal_rows
    ]
    relevance_rows, relevance_receipt = _local_relevance(queries, list(template_pool.values()))
    tasks = []
    for proposal, candidate_relevance in zip(proposal_rows, relevance_rows):
        task = {**projected_by_id[proposal["taskProposalId"]], "candidateRelevance": candidate_relevance}
        quote = task["quote"]
        candidates = matching.template_candidates(task, bindings, template_pool)
        tasks.append({
            **projected_by_id[task["id"]],
            "taskId": task["id"],
            "job": task["job"],
            "quote": quote,
            "candidateStatus": "retrieved_unvalidated" if candidates else "no_bound_template_candidates",
            "noTemplateReason": no_template_reason(task, candidates),
            "candidateCount": len(candidates),
            "candidates": candidates,
            "speakerDerived": bool(proposal.get("speakerDerived")),
            "semanticDerived": bool(proposal.get("semanticDerived")),
            "presentationOperations": task["presentationOperations"],
            "primaryPresentationOperation": task["primaryPresentationOperation"],
            "routeDisposition": task["routeDisposition"],
            "presentationContract": matching.presentation_contract(task),
        })
    tasks.sort(key=lambda row: (
        min((beats.get(beat_id) or {}).get("order", 10**9) for beat_id in row["sourceBeatIds"]),
        row["taskId"],
    ))

    clip_routes = []
    for route in proposals.get("speakerRoutes") or []:
        if route.get("role") != "clip":
            continue
        beat = beats[route["beatId"]]
        clip_routes.append({
            "beatId": route["beatId"],
            "quote": beat["narration"],
            "speaker": route.get("speaker"),
            "route": "source_footage_primary",
            "templateCandidateCount": 0,
            "reason": "The validated speaker contract requires the exact source clip; a replacement template would misrepresent the beat.",
        })

    return {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": 1,
        "packageId": proposals["packageId"],
        "adapterValidation": adapter_validation,
        "taskProjection": projection,
        "taskProjectionStatus": "source_bound_versioned",
        "purpose": "Review-only beat-to-template candidate retrieval for the established gallery UI",
        "activationState": "review_only_not_connected",
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "fitValidated": False,
        "retrievalReceipt": {
            "stages": [
                "semantic_visual_moment_split",
                "template_neutral_presentation_contract",
                "structured_catalog_admission",
                "local_semantic_ordering",
                "family_diversification",
            ],
            "structuredCompatibilityRequired": True,
            "legacyJobBindingCanAdmit": False,
            "localRelevance": relevance_receipt,
        },
        "sources": {
            "taskProposals": _source(proposals_path),
            "adapter": _source(adapter_path),
            "bindings": _source(bindings_path),
            **({"taskScopedAdmissions": _source(admissions_path)} if admissions_path else {}),
        },
        "tasks": tasks,
        "clipRoutes": clip_routes,
        "uncoveredNarratorClaims": proposals.get("counts", {}).get("uncoveredClaims", 0),
        "counts": {
            "taskProposals": len(tasks),
            "tasksWithCandidates": sum(bool(row["candidates"]) for row in tasks),
            "tasksWithoutCandidates": sum(not row["candidates"] for row in tasks),
            "candidateCards": sum(len(row["candidates"]) for row in tasks),
            "sourceClipRoutes": len(clip_routes),
        },
    }


def _ledger_read(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def _review_order(candidates: list[dict[str, Any]], scores: dict[str, float]) -> list[dict[str, Any]]:
    # Membership is decided by P5 before any score is read. No family quota or
    # popularity signal can add/remove an option. Unknown remains reviewable.
    rows = [r for r in candidates if r['fitAssessment']['verdict'] != 'incompatible']
    for row in rows:
        score = scores.get(row['candidateId'], 0)
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score):
            raise ValueError('review score must be finite numeric evidence')
    return sorted(rows, key=lambda r: (
        r['fitAssessment']['verdict'] not in {'native_fit', 'adapted_fit'},
        -scores.get(r['candidateId'], 0), r['candidateId']))


def _display_digest(gallery: dict[str, Any]) -> str:
    body = {**gallery, 'contractEnforcementReceipt': {**gallery['contractEnforcementReceipt'],
            'candidateDisplay': dict(gallery['contractEnforcementReceipt']['candidateDisplay'])}}
    body['contractEnforcementReceipt']['candidateDisplay'].pop('bodySha256', None)
    return batch._digest(body)


def _ledger_gallery(ledger_path: Path, ordering_path: Path, contract_receipt: dict[str, Any]) -> dict[str, Any]:
    ledger = _ledger_read(Path(ledger_path))
    batch.validate(ledger)  # Mandatory current catalog/source replay; not structural-only.
    ordering = _read(ordering_path)
    limit = ordering.get('displayLimit')
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
        raise ValueError('explicit nonnegative integer displayLimit required')
    sequence = ordering.get('taskIds')
    by_id = {r['taskId']: r for r in ledger['tasks']}
    if not isinstance(sequence, list) or len(sequence) != len(set(sequence)) or set(sequence) != set(by_id):
        raise ValueError('reviewer sequence must contain every ledger task exactly once')
    scores = ordering.get('candidateRelevance') or {}
    if set(scores) - set(by_id):
        raise ValueError('scores reference an unknown ledger task')
    tasks = []
    for task_id in sequence:
        original = by_id[task_id]
        candidates = original['templateResult']['candidates']
        task_scores = scores.get(task_id) or {}
        if not isinstance(task_scores, dict) or set(task_scores) - {r['candidateId'] for r in candidates}:
            raise ValueError('scores reference an unknown ledger candidate')
        ordered = _review_order(candidates, task_scores)
        eligible = [r for r in ordered if r['fitAssessment']['verdict'] in {'native_fit', 'adapted_fit'}]
        unresolved = [r for r in ordered if r['fitAssessment']['verdict'] not in {'native_fit', 'adapted_fit'}]
        rejected = [r for r in candidates if r['fitAssessment']['verdict'] == 'incompatible']
        groups: dict[str, list[dict[str, Any]]] = {}
        for member in sorted(candidates, key=lambda r: r['candidateId']):
            groups.setdefault(matching.C._family(member['candidateId']), []).append({
                'candidateId': member['candidateId'], 'ledgerCandidateSha256': batch._digest(member),
                'verdict': member['fitAssessment']['verdict'],
                'nativeFitUnknown': member['fitAssessment']['evidence']['nativeFitUnknown'],
                'provenance': copy.deepcopy(member.get('candidateMatchingProvenance'))})
        displayed = eligible[:limit]
        tasks.append({**copy.deepcopy(original),
            'ledgerTaskSha256': batch._digest(original),
            'candidateRelevance': copy.deepcopy(task_scores), 'displayLimit': limit,
            'candidates': copy.deepcopy(displayed), 'candidateCount': len(displayed),
            'candidateStatus': 'reconciled_review_only',
            'unresolvedCandidates': copy.deepcopy(unresolved),
            'omittedCandidateIds': [r['candidateId'] for r in eligible[limit:]],
            'orderedCandidateIds': [r['candidateId'] for r in ordered],
            'familyOrder': list(dict.fromkeys(matching.C._family(r['candidateId']) for r in ordered)),
            'variantGroups': [{'family': key, 'members': members} for key, members in sorted(groups.items())],
            'rejectionReasons': [{'candidateId': r['candidateId'], 'fitAssessment': copy.deepcopy(r['fitAssessment'])} for r in rejected],
            'counts': {'pool': len(candidates), 'eligible': len(eligible), 'incompatible': len(rejected),
                       'unresolved': len(unresolved), 'displayed': len(displayed), 'omitted': len(eligible)-len(displayed)},
            'humanReviewed': False,
            'noTemplateReason': None if displayed else 'no_verified_display_option; complete_ledger_and_non_template_routes_preserved'})
    display = {'policy': 'existing-gallery-ledger-display@1',
               'stages': ledger['contractEnforcementReceipt']['candidateReconciliation']['stages'] + ['deterministic_review_order', 'bounded_eligible_display'],
               'ledgerReconciliationSha256': ledger['contractEnforcementReceipt']['candidateReconciliation']['bodySha256'],
               'ledgerTaskReferences': {r['taskId']: batch._digest(r) for r in ledger['tasks']},
               'ignoredFamilyQuota': ordering.get('familyQuota'),
               'orderingPolicy': 'verified_first_then_descending_persisted_score_then_candidate_id; no_threshold_or_family_quota',
               'fullLedgerPreserved': True}
    artifact = {'schemaVersion': 1, 'packageId': ledger['storyId'],
                'purpose': 'reconciled_ledger_review_gallery', 'activationState': 'review_only_not_connected',
                'selectionAuthorized': False, 'renderingAuthorized': False, 'fitValidated': False,
                'contractEnforcementReceipt': {**contract_receipt, 'candidateDisplay': display},
                'sources': {'ledger': batch._source(Path(ledger_path)), 'ordering': batch._source(Path(ordering_path))},
                'consumerFingerprints': copy.deepcopy(ledger['consumerFingerprints']),
                'reviewerSequence': list(sequence), 'tasks': tasks,
                'counts': {key: sum(r['counts'][key] for r in tasks) for key in ('pool','eligible','incompatible','unresolved','displayed','omitted')},
                'humanReviewed': False, 'boundary': 'Ordering and sampling are review evidence; unknown/native flags, complete ledger and overflow remain accessible; no selection or rendering authority.'}
    display['bodySha256'] = _display_digest(artifact)
    return artifact


def validate(gallery: dict[str, Any]) -> None:
    """A rehashed edit cannot replace the immutable persisted inputs."""
    display = gallery.get('contractEnforcementReceipt', {}).get('candidateDisplay') or {}
    if display.get('policy') != 'existing-gallery-ledger-display@1' or display.get('bodySha256') != _display_digest(gallery):
        raise ValueError('gallery display receipt missing or stale')
    for source in gallery.get('sources', {}).values():
        path = batch._source_path(source.get('path', ''))
        if not path.is_file() or batch._sha(path) != source.get('sha256'):
            raise ValueError('gallery input missing or stale')
    try:
        replay = build(ledger_path=batch._source_path(gallery['sources']['ledger']['path']),
                       ordering_path=batch._source_path(gallery['sources']['ordering']['path']))
    except (KeyError, TypeError) as exc:
        raise ValueError('gallery input bindings incomplete') from exc
    if gallery != replay:
        raise ValueError('gallery does not replay from shared ledger and persisted ordering')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposals", type=Path)
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--ordering", type=Path)
    parser.add_argument("--bindings", type=Path, default=DEFAULT_BINDINGS)
    parser.add_argument("--admissions", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build(
        proposals_path=args.proposals,
        adapter_path=args.adapter,
        bindings_path=args.bindings,
        admissions_path=args.admissions,
        ledger_path=args.ledger, ordering_path=args.ordering,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps(artifact["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
