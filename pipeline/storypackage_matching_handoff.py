#!/usr/bin/env python3
"""Validate and normalize a StoryPackage matching handoff for review-only consumers."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .matching_contract_gate import enforce_contracts
except ImportError:
    from matching_contract_gate import enforce_contracts

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "plans" / "storypackage-02-integration-tasks.json"
PROJECTION_VERSION = "matching-task-projection@1"
_PROJECTION_CACHE: dict[str, dict[str, Any]] = {}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode()).hexdigest()


def no_template_reason(task: dict[str, Any], candidates: list[Any], *, fit_validated: bool = False) -> str | None:
    if (task.get("routeDisposition") or {}).get("templateEligible") is False:
        return "intentional_route"
    if not candidates:
        return "missing_discovery"
    return None if fit_validated else "unresolved_feasibility"


def project_task(proposal: dict[str, Any], *, package_id: str, source_digest: str,
                 admissions: list[dict[str, Any]], source_bindings: dict[str, Any] | None = None) -> dict[str, Any]:
    """Internal canonical projection, shared by registered review entrypoints."""
    if any(proposal.get(key) for key in ("priorSelections", "editorSelections", "selectedTemplates", "templateAdmissions")):
        raise ValueError("prior-story selections cannot enter a task projection")
    obligations = copy.deepcopy(proposal.get("obligations") or [])
    entity_refs = copy.deepcopy(proposal.get("entityRefs") or [])
    display = list(dict.fromkeys(ref["entity"] for ref in entity_refs
                                if ref.get("display") in {"required", "eligible"} and ref.get("entity")))
    quote = (proposal.get("taskText") or "").strip()
    speakers = [beat.get("speaker") or {} for beat in proposal.get("sourceBeats") or []]
    attributed = proposal.get("job") == "attributed_quote" or any(s.get("role") == "quote" for s in speakers)
    required_text = list(dict.fromkeys(text for obligation in obligations
                                      if obligation.get("needsOnScreenText")
                                      for text in obligation.get("mustBePerceptible") or []))
    if attributed and quote and quote not in required_text:
        required_text.insert(0, quote)
    operations = list(proposal.get("presentationOperations") or ["concept_statement"])
    primary = proposal.get("primaryPresentationOperation") or operations[0]
    route = copy.deepcopy(proposal.get("routeDisposition") or {"templateEligible": True})
    # Explicit attribution/text obligations resolve the question heuristic. This
    # changes the projection, never source semantics, spans or narration.
    if attributed and required_text and primary == "rhetorical_question":
        if "evidence_presentation" not in operations:
            operations.append("evidence_presentation")
        primary = "evidence_presentation"
        route["templateEligible"] = True
        route["reason"] = "explicit_attributed_quote_obligation"
    cohorts = copy.deepcopy(proposal.get("cohortRefs") or [])
    media_needs = []
    for obligation in obligations:
        needs = obligation.get("mediaNeeds") or []
        media_needs.extend(copy.deepcopy(needs if isinstance(needs, list) else [needs]))
    cohort_media = [{"cohortRef": copy.deepcopy(ref), "representedBy": copy.deepcopy(ref["representedBy"]),
                     "status": "required"} for ref in cohorts if ref.get("representedBy")]
    values = copy.deepcopy(proposal.get("values") or [])
    task = {
        "projectionVersion": PROJECTION_VERSION, "packageId": package_id,
        "sourceDigest": source_digest, "id": proposal["taskProposalId"],
        "sourceBindings": copy.deepcopy(source_bindings),
        "taskProposalId": proposal["taskProposalId"], "job": proposal["job"],
        "taskRole": "attributed_quote" if attributed else "main", "quote": quote,
        "claimIds": copy.deepcopy(proposal.get("claimIds") or []),
        "sourceBeatIds": list(dict.fromkeys(beat["beatId"] for beat in proposal.get("sourceBeats") or [])),
        "sourceBeats": copy.deepcopy(proposal.get("sourceBeats") or []),
        "claimSpans": copy.deepcopy(proposal.get("claimSpans") or []),
        "presentationOperations": operations, "primaryPresentationOperation": primary,
        "primaryMeaning": {"operation": primary, "job": proposal["job"]},
        "requiredMeanings": copy.deepcopy(proposal.get("presentationOperations") or []),
        "routeDisposition": route, "obligations": obligations,
        "continuity": copy.deepcopy(proposal.get("continuity") or []),
        "values": values, "cohortRefs": cohorts, "entityRefs": entity_refs,
        "mediaNeeds": media_needs, "cohortMediaNeeds": cohort_media,
        "dataNeeds": {"values": values, "cohortRefs": cohorts},
        "quoteRequirements": {"requiredText": required_text,
                              "attribution": list(dict.fromkeys(s["entity"] for s in speakers
                                                                if s.get("role") == "quote" and s.get("entity"))),
                              "speakers": copy.deepcopy(speakers)},
        "mustBePerceptible": list(dict.fromkeys(text for obligation in obligations
                                                for text in obligation.get("mustBePerceptible") or [])),
        "entities": {"displayEligible": display}, "entityCount": len(display),
        "templateAdmissions": copy.deepcopy(admissions), "ignorePriorSelections": True,
        "candidateDisplayLimit": 16, "slideshowDisplayLimit": 6,
        "selectionAuthorized": False, "renderingAuthorized": False,
    }
    task["taskContractReceipt"] = {"version": PROJECTION_VERSION, "sourceDigest": source_digest,
                                   "taskSha256": _digest(task)}
    return task


def validate_task_projection(task: dict[str, Any]) -> None:
    # Retrieval settings/relevance are existing supported controls outside the
    # semantic projection. They cannot override its source-bound meaning.
    receipt = task.get("taskContractReceipt") or {}
    body = {k: v for k, v in task.items() if k not in {"taskContractReceipt", "candidateRelevance"}}
    if receipt.get("version") != PROJECTION_VERSION or receipt.get("sourceDigest") != task.get("sourceDigest") or receipt.get("taskSha256") != _digest(body):
        raise ValueError("task projection receipt missing, stale or locally reconstructed")
    sources = task.get("sourceBindings") or {}
    if not sources or _digest(sources) != task.get("sourceDigest"):
        raise ValueError("task projection source bindings missing or stale")
    for source in sources.values():
        if not Path(source["path"]).is_file() or _sha(Path(source["path"])) != source["sha256"]:
            raise ValueError("task projection source digest is stale")
    try:
        from .storypackage_adapter import validate as validate_adapter
    except ImportError:
        from storypackage_adapter import validate as validate_adapter
    validate_adapter(_read(Path(sources["adapter"]["path"])), source_path=Path(sources["adapter"]["path"]))
    canonical = _PROJECTION_CACHE.get(task["sourceDigest"])
    if canonical is None:
        canonical = build_projection(Path(sources["taskProposals"]["path"]), Path(sources["adapter"]["path"]),
                                     admissions_path=Path(sources["taskScopedAdmissions"]["path"]) if "taskScopedAdmissions" in sources else None)
    expected = next((row for row in canonical["tasks"] if row["id"] == task.get("id")), None)
    if expected != {k: v for k, v in task.items() if k != "candidateRelevance"}:
        raise ValueError("consumer task reconstruction differs from canonical source projection")


def build_projection(proposals_path: Path, adapter_path: Path, *, admissions_path: Path | None = None) -> dict[str, Any]:
    try:
        from .storypackage_adapter import validate as validate_adapter
    except ImportError:
        from storypackage_adapter import validate as validate_adapter
    proposals = _read(proposals_path)
    adapter = _read(adapter_path)
    validation = validate_adapter(adapter, source_path=adapter_path)
    if proposals.get("packageId") != adapter.get("packageId") or (proposals.get("source") or {}).get("sha256") != _sha(adapter_path):
        raise ValueError("task projection adapter source digest/identity is stale")
    if proposals.get("activationState") != "review_only_not_connected" or proposals.get("selectionAuthorized") is not False or proposals.get("renderingAuthorized") is not False:
        raise ValueError("task projection requires review-only proposals")
    claims = {row["claimId"]: row for row in adapter.get("claims") or []}
    for row in proposals.get("taskProposals") or []:
        if any(claim_id not in claims for claim_id in row.get("claimIds") or []):
            raise ValueError("projection claim references differ from adapter source")
    sources = {"taskProposals": {"path": str(Path(proposals_path).resolve()), "sha256": _sha(proposals_path)},
               "adapter": {"path": str(Path(adapter_path).resolve()), "sha256": _sha(adapter_path)}}
    if admissions_path:
        sources["taskScopedAdmissions"] = {"path": str(Path(admissions_path).resolve()), "sha256": _sha(admissions_path)}
    source_digest = _digest(sources)
    raw_admissions = _read(admissions_path) if admissions_path else {"admissions": []}
    admissions_by_task = {}
    if raw_admissions.get("admissions"):
        if raw_admissions.get("packageId") != proposals["packageId"] or (raw_admissions.get("sources", {}).get("taskProposals") or {}).get("sha256") != sources["taskProposals"]["sha256"]:
            raise ValueError("task admissions lack current package/source scope")
        valid_ids = {r["taskProposalId"] for r in proposals["taskProposals"]}
        for row in raw_admissions["admissions"]:
            if row.get("taskId") not in valid_ids:
                raise ValueError("admission references foreign task")
            admissions_by_task.setdefault(row["taskId"], []).append({
                "id": row["candidateId"], "source": "task-scoped-editor-feedback",
                "packageId": proposals["packageId"], "taskId": row["taskId"],
                "sourceDigest": source_digest, "comment": row.get("comment"),
                "reviewState": "unvalidated", "selectionAuthorized": False, "renderingAuthorized": False})
    tasks = [project_task({**row, "taskText": row.get("taskText") or " ".join(claims[c]["text"] for c in row.get("claimIds") or [])}, package_id=proposals["packageId"], source_digest=source_digest,
                          admissions=admissions_by_task.get(row["taskProposalId"], []), source_bindings=sources)
             for row in proposals.get("taskProposals") or []]
    if len({r["id"] for r in tasks}) != len(tasks):
        raise ValueError("duplicate projected task")
    projected = {"version": PROJECTION_VERSION, "packageId": proposals["packageId"],
                 "sources": sources, "sourceDigest": source_digest, "adapterValidation": validation,
                 "tasks": tasks, "selectionAuthorized": False, "renderingAuthorized": False}
    projected["receipt"] = {"version": PROJECTION_VERSION, "sourceDigest": source_digest,
                            "projectionSha256": _digest(projected)}
    _PROJECTION_CACHE[source_digest] = copy.deepcopy(projected)
    return projected


def validate_projection(projection: dict[str, Any]) -> None:
    try:
        if projection.get("version") != PROJECTION_VERSION or not projection.get("receipt"):
            raise ValueError("projection receipt missing or stale")
        sources = projection["sources"]
        for source in sources.values():
            if not Path(source["path"]).is_file() or _sha(Path(source["path"])) != source["sha256"]:
                raise ValueError("projection source missing or stale")
        replay = build_projection(Path(sources["taskProposals"]["path"]), Path(sources["adapter"]["path"]),
                                  admissions_path=Path(sources["taskScopedAdmissions"]["path"]) if "taskScopedAdmissions" in sources else None)
        if projection != replay:
            raise ValueError("projection omission, mutation or local reconstruction")
    except (KeyError, TypeError) as exc:
        raise ValueError("projection source/receipt omitted") from exc


def _read(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _git_head(repo: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True,
        text=True, capture_output=True,
    ).stdout.strip()


def _run_checker(path: Path, *, upstream_root: Path, checker_python: Path,
                 repo_mappings: dict[str, Path]) -> str:
    authority = _read(DEFAULT_PLAN)["authority"]
    if _git_head(upstream_root) != authority["commit"]:
        raise ValueError("StoryPackage authority checkout is not at the pinned commit")
    checker = upstream_root / authority["handoffCheckerPath"]
    command = [str(Path(checker_python).absolute()), str(checker), str(path)]
    for name, repo in sorted(repo_mappings.items()):
        command.extend(["--repo", f"{name}={Path(repo).resolve()}"])
    result = subprocess.run(command, cwd=checker.parent.parent, text=True, capture_output=True)
    output = (result.stdout + result.stderr).strip()
    if result.returncode:
        raise ValueError(f"authoritative StoryPackage matching-handoff checker rejected handoff: {output}")
    return output


def validate_current_task_compatibility(handoff: dict[str, Any], current: dict[str, Any]) -> None:
    handed = {row["taskId"]: row for row in handoff.get("tasks") or []}
    tasks = {row["id"]: row for row in current.get("tasks") or []}
    if set(handed) != set(tasks):
        raise ValueError("matching handoff and current VisualTask IDs differ")
    for task_id, row in handed.items():
        current_row = tasks[task_id]
        if row["sourceBeatId"] != current_row.get("sourceBeatId"):
            raise ValueError(f"source beat drift: {task_id}")
        source_job = current_row.get("sourceBeatJob", current_row.get("job"))
        if row["linkage"]["visualJob"] != source_job:
            raise ValueError(f"visual job drift: {task_id}")


def build(path: Path, *, upstream_root: Path, checker_python: Path,
          repo_mappings: dict[str, Path]) -> dict[str, Any]:
    contract_receipt = enforce_contracts("storypackage_matching_handoff.build")
    path = Path(path).resolve()
    upstream_root = Path(upstream_root).resolve()
    output = _run_checker(
        path, upstream_root=upstream_root, checker_python=checker_python,
        repo_mappings=repo_mappings,
    )
    handoff = _read(path)
    package = _read(upstream_root / handoff["package"]["path"])
    cohort_members = {
        f"{row['id']}@{row['version']}": [member["entity"] for member in row["members"] if member["entity"] is not None]
        for row in package.get("cohorts") or []
    }
    authority = _read(DEFAULT_PLAN)["authority"]
    tasks = handoff["tasks"]
    return {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": 1,
        "sourceSchema": handoff["schema"],
        "handoffId": handoff["handoffId"],
        "packageId": handoff["package"]["packageId"],
        "package": handoff["package"],
        "visualTasks": handoff["visualTasks"],
        "entityRegistry": handoff["entityRegistry"],
        "cohortMembers": cohort_members,
        "tasks": tasks,
        "unresolved": handoff["unresolved"],
        "counts": {
            "tasks": len(tasks),
            "storyMediaRequired": sum(row["media"]["storyRequiresKind"] for row in tasks),
            "textRequiredTasks": sum(row["text"]["required"] for row in tasks),
            "textFields": sum(len(row["text"]["fields"]) for row in tasks),
            "dataBindingTasks": sum(row["data"] is not None for row in tasks),
            "dataValues": sum(len((row["data"] or {}).get("values", [])) for row in tasks),
            "unresolved": len(handoff["unresolved"]),
            "unresolvedKinds": dict(sorted(Counter(row["kind"] for row in handoff["unresolved"]).items())),
        },
        "storyMatchingHandoffReceipt": {
            "accepted": True,
            "handoffSha256": _sha(path),
            "authorityCommit": authority["commit"],
            "checkerPath": authority["handoffCheckerPath"],
            "checkerSha256": _sha(upstream_root / authority["handoffCheckerPath"]),
            "checkerOutput": output,
        },
        "activationState": "review_only_not_connected",
        "selectionAuthorized": False,
        "treatmentApproved": False,
        "renderingAuthorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("handoff", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--upstream-root", required=True, type=Path)
    parser.add_argument("--checker-python", required=True, type=Path)
    parser.add_argument("--repo", action="append", default=[])
    args = parser.parse_args()
    mappings = {}
    for item in args.repo:
        name, separator, value = item.partition("=")
        if not separator:
            raise ValueError("--repo must be owner/name=/local/path")
        mappings[name] = Path(value)
    artifact = build(
        args.handoff, upstream_root=args.upstream_root,
        checker_python=args.checker_python, repo_mappings=mappings,
    )
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps(artifact["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
