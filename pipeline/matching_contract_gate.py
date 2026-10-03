#!/usr/bin/env python3
"""Mandatory application-level contract gate for matching entry points."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GENERAL_CONTRACT = ROOT / "grammar" / "general-matching-layer-contract.json"
STAGE_CONTRACT = ROOT / "grammar" / "matching-harness-stage-contract.json"
ENTRYPOINT_CONTRACT = ROOT / "grammar" / "matching-entrypoint-contract.json"
HARNESS_AUDIT = ROOT / "reports" / "matching-harness-audit.json"

EXPECTED_STAGES = [
    "general_matching_contract", "baseline_reconciliation", "story_handoff",
    "data_handoff", "template_media_feasibility", "sequence_planning",
    "human_review", "render_release_handoff",
]
CONTINUATION_TARGET = "objective_complete_or_user_input_required"
ALLOWED_STOP_CONDITIONS = [
    "objective_complete",
    "explicit_user_input_required",
    "authorization_boundary_requires_user",
    "external_blocker_requires_user_action",
]
ALLOWED_BLOCKER_PARTIES = ["you", "data", "story", "matching", "none"]


class MatchingContractError(ValueError):
    pass


def _read(path: Path) -> dict[str, Any]:
    if not Path(path).is_file():
        raise MatchingContractError(f"mandatory matching contract missing: {path}")
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _validate_general(contract: dict[str, Any]) -> None:
    runtime = contract.get("runtime") or {}
    if contract.get("productBoundary") != "any_validated_supported_storypackage":
        raise MatchingContractError("general matching product boundary is invalid")
    for key in (
        "storySpecificBranchesAllowed", "fixtureIdentifiersAllowed",
        "priorStoryDecisionsCanAdmitCandidates", "priorStoryDecisionsCanOrderCandidates",
        "taskFeedbackCanBecomeGlobalWithoutReconciliation",
    ):
        if runtime.get(key) is not False:
            raise MatchingContractError(f"general matching contract permits {key}")
    for key in (
        "templateNeutralTaskContractRequired", "structuredCapabilityAdmissionRequired",
        "brollFallbackAvailable",
    ):
        if runtime.get(key) is not True:
            raise MatchingContractError(f"general matching contract omits {key}")
    execution = contract.get("execution") or {}
    if execution.get("objectiveSource") != "plans/general-matching-layer-tasks.json":
        raise MatchingContractError("general matching contract lacks its objective source")
    if execution.get("taskListReconciliationRequired") is not True:
        raise MatchingContractError("general matching contract omits task-list reconciliation")
    if execution.get("objectiveReconciliationRequired") is not True:
        raise MatchingContractError("general matching contract omits objective reconciliation")
    if execution.get("continueUntil") != CONTINUATION_TARGET:
        raise MatchingContractError("general matching contract has an invalid continuation target")
    if execution.get("allowedStopConditions") != ALLOWED_STOP_CONDITIONS:
        raise MatchingContractError("general matching contract has invalid stop conditions")
    if execution.get("routineTaskCompletionAllowsStop") is not False:
        raise MatchingContractError("general matching contract permits routine-task stopping")
    if execution.get("routineStatusUpdateAllowsStop") is not False:
        raise MatchingContractError("general matching contract permits status-report stopping")
    if execution.get("currentBlockerRequired") is not True:
        raise MatchingContractError("general matching contract omits current-blocker reporting")
    if execution.get("allowedBlockerParties") != ALLOWED_BLOCKER_PARTIES:
        raise MatchingContractError("general matching contract has invalid blocker parties")
    if contract.get("selectionAuthorized") is not False or contract.get("renderingAuthorized") is not False:
        raise MatchingContractError("general matching contract authorizes selection or rendering")


def _validate_stages(contract: dict[str, Any]) -> None:
    stages = contract.get("stages") or []
    if [row.get("id") for row in stages] != EXPECTED_STAGES:
        raise MatchingContractError("mandatory matching stages are missing or reordered")
    if [row.get("order") for row in stages] != list(range(len(EXPECTED_STAGES))):
        raise MatchingContractError("mandatory matching stage order is invalid")
    if any(not row.get("requires") or not row.get("produces") for row in stages):
        raise MatchingContractError("mandatory matching stage lacks contract inputs or receipt")
    policy = contract.get("continuationPolicy") or {}
    if policy.get("objective") != "general-storypackage-matching-layer":
        raise MatchingContractError("matching stage contract lacks the general objective")
    if policy.get("taskList") != "plans/general-matching-layer-tasks.json":
        raise MatchingContractError("matching stage contract has an invalid task list")
    if policy.get("reconcileBeforeEveryRun") is not True:
        raise MatchingContractError("matching stage contract omits run reconciliation")
    if policy.get("continueUntil") != CONTINUATION_TARGET:
        raise MatchingContractError("matching stage contract has an invalid continuation target")
    if policy.get("stopOnlyFor") != ALLOWED_STOP_CONDITIONS:
        raise MatchingContractError("matching stage contract has invalid stop conditions")
    if policy.get("taskCompletionAloneAllowsStop") is not False:
        raise MatchingContractError("matching stage contract permits routine-task stopping")
    if policy.get("statusReportingAloneAllowsStop") is not False:
        raise MatchingContractError("matching stage contract permits status-report stopping")
    if policy.get("currentBlockerRequired") is not True:
        raise MatchingContractError("matching stage contract omits current-blocker reporting")
    if policy.get("allowedBlockerParties") != ALLOWED_BLOCKER_PARTIES:
        raise MatchingContractError("matching stage contract has invalid blocker parties")
    if "objective_task_reconciliation" not in stages[0]["requires"]:
        raise MatchingContractError("general matching stage omits objective/task reconciliation")
    if "continuation_receipt" not in stages[0]["produces"]:
        raise MatchingContractError("general matching stage omits its continuation receipt")
    if contract.get("selectionAuthorized") is not False or contract.get("renderingAuthorized") is not False:
        raise MatchingContractError("matching stage contract authorizes selection or rendering")


def _validate_entrypoints(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if contract.get("unknownEntrypointsAllowed") is not False:
        raise MatchingContractError("unknown matching entry points are allowed")
    if contract.get("productionRequiresCompleteHarness") is not True:
        raise MatchingContractError("production does not require the complete harness")
    if contract.get("selectionAuthorized") is not False or contract.get("renderingAuthorized") is not False:
        raise MatchingContractError("entrypoint contract authorizes selection or rendering")
    rows = contract.get("entrypoints") or []
    by_id = {row.get("id"): row for row in rows}
    if len(by_id) != len(rows) or None in by_id:
        raise MatchingContractError("matching entry points are missing or duplicated")
    for row in rows:
        if not row.get("module") or not row.get("callable") or not row.get("modes"):
            raise MatchingContractError("matching entry point is incomplete")
        source = ROOT / row["module"]
        if not source.is_file():
            raise MatchingContractError(f"registered matching entry point source missing: {source}")
    return by_id


def _validate_production_harness() -> None:
    audit = _read(HARNESS_AUDIT)
    if audit.get("productionAllowed") is not True:
        raise MatchingContractError("production matching is blocked by the current harness")
    if [row.get("id") for row in audit.get("stageResults") or []] != EXPECTED_STAGES:
        raise MatchingContractError("production harness stages are missing or reordered")
    if any(row.get("status") != "passed" for row in audit["stageResults"]):
        raise MatchingContractError("production matching has incomplete harness stages")
    continuation = audit.get("continuation") or {}
    if continuation.get("objectiveComplete") is not True or continuation.get("stopReason") != "objective_complete":
        raise MatchingContractError("production matching objective is incomplete")
    for item in (audit.get("sources") or {}).values():
        path = ROOT / item.get("path", "")
        if not path.is_file() or _sha(path) != item.get("sha256"):
            raise MatchingContractError("production harness has missing or stale sources")


def enforce_contracts(entrypoint: str, *, mode: str = "review_only") -> dict[str, Any]:
    """Fail closed unless this exact entry point is registered and contracts are valid."""
    general = _read(GENERAL_CONTRACT)
    stages = _read(STAGE_CONTRACT)
    entrypoints = _read(ENTRYPOINT_CONTRACT)
    _validate_general(general)
    _validate_stages(stages)
    registered = _validate_entrypoints(entrypoints)
    row = registered.get(entrypoint)
    if row is None:
        raise MatchingContractError(f"unregistered matching entry point: {entrypoint}")
    if mode not in row["modes"]:
        raise MatchingContractError(f"matching entry point {entrypoint} does not allow mode {mode}")
    if mode == "production" and not row.get("buildsHarness"):
        _validate_production_harness()
    return {
        "schemaVersion": 1,
        "enforced": True,
        "entrypoint": entrypoint,
        "mode": mode,
        "contracts": {
            "generalMatching": {"id": general["contractId"], "sha256": _sha(GENERAL_CONTRACT)},
            "stageOrder": {"sha256": _sha(STAGE_CONTRACT)},
            "entrypoints": {"id": entrypoints["contractId"], "sha256": _sha(ENTRYPOINT_CONTRACT)},
        },
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "productionRequiresCompleteHarness": True,
    }
