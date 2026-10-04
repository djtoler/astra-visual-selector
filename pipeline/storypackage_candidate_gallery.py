#!/usr/bin/env python3
"""Retrieve review-only template candidates for StoryPackage task proposals."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
from pathlib import Path
from typing import Any

try:
    from . import visualtask_matching as matching
    from .matching_contract_gate import enforce_contracts
except ImportError:
    import visualtask_matching as matching
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


def build(*, proposals_path: Path, adapter_path: Path,
          bindings_path: Path = DEFAULT_BINDINGS,
          admissions_path: Path | None = None) -> dict[str, Any]:
    contract_receipt = enforce_contracts("storypackage_candidate_gallery.build")
    proposals = _read(proposals_path)
    adapter = _read(adapter_path)
    bindings = _read(bindings_path)
    admissions = _read(admissions_path) if admissions_path else {"admissions": []}
    admissions_by_task: dict[str, list[dict[str, Any]]] = {}
    for admission in admissions.get("admissions") or []:
        admissions_by_task.setdefault(admission["taskId"], []).append(admission)
    if proposals.get("activationState") != "review_only_not_connected":
        raise ValueError("candidate gallery requires review-only task proposals")
    if proposals.get("selectionAuthorized") is not False or proposals.get("renderingAuthorized") is not False:
        raise ValueError("task proposals cannot authorize selection or rendering")
    if adapter.get("packageId") != proposals.get("packageId"):
        raise ValueError("adapter and proposal package IDs differ")

    claims = {row["claimId"]: row for row in adapter.get("claims") or []}
    beats = {row["beatId"]: row for row in adapter.get("beats") or []}
    template_pool = {row["id"]: row for row in matching.C.load(content_class="*")}
    proposal_rows = list(proposals.get("taskProposals") or [])
    queries = [
        " ".join(filter(None, [
            proposal.get("taskText") or " ".join(claims[claim_id]["text"] for claim_id in proposal["claimIds"]),
            " ".join(proposal.get("presentationOperations") or []),
            " ".join(
                text for obligation in proposal.get("obligations") or []
                for text in obligation.get("mustBePerceptible") or []
            ),
        ]))
        for proposal in proposal_rows
    ]
    relevance_rows, relevance_receipt = _local_relevance(queries, list(template_pool.values()))
    tasks = []
    for proposal, candidate_relevance in zip(proposal_rows, relevance_rows):
        claim_rows = [claims[claim_id] for claim_id in proposal["claimIds"]]
        display_entities = _unique([
            ref.get("entity") for row in claim_rows for ref in row.get("entityRefs") or []
            if ref.get("display") in {"required", "eligible"}
        ])
        quote = (proposal.get("taskText") or " ".join(row["text"] for row in claim_rows)).strip()
        task = {
            "id": proposal["taskProposalId"],
            "job": proposal["job"],
            "taskRole": "attributed_quote" if proposal.get("speakerDerived") else "main",
            "quote": quote,
            "mustBePerceptible": _unique([
                text for obligation in proposal.get("obligations") or []
                for text in obligation.get("mustBePerceptible") or []
            ]),
            "entityCount": len(display_entities),
            "entities": {"displayEligible": display_entities},
            "templateAdmissions": [
                {
                    "id": row["candidateId"],
                    "source": "task-scoped-editor-feedback",
                    "comment": row.get("comment"),
                    "reviewState": "unvalidated",
                    "selectionAuthorized": False,
                    "renderingAuthorized": False,
                }
                for row in admissions_by_task.get(proposal["taskProposalId"], [])
            ],
            "presentationOperations": proposal.get("presentationOperations") or [],
            "primaryPresentationOperation": proposal.get("primaryPresentationOperation"),
            "routeDisposition": proposal.get("routeDisposition") or {},
            "values": proposal.get("values") or [],
            "cohortRefs": proposal.get("cohortRefs") or [],
            "obligations": proposal.get("obligations") or [],
            "ignorePriorSelections": True,
            "candidateDisplayLimit": 16,
            "slideshowDisplayLimit": 6,
            "candidateRelevance": candidate_relevance,
        }
        candidates = matching.template_candidates(task, bindings, template_pool)
        tasks.append({
            "taskId": task["id"],
            "sourceBeatIds": _unique([row["beatId"] for row in claim_rows]),
            "job": task["job"],
            "quote": quote,
            "candidateStatus": "retrieved_unvalidated" if candidates else "no_bound_template_candidates",
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposals", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--bindings", type=Path, default=DEFAULT_BINDINGS)
    parser.add_argument("--admissions", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build(
        proposals_path=args.proposals,
        adapter_path=args.adapter,
        bindings_path=args.bindings,
        admissions_path=args.admissions,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps(artifact["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
