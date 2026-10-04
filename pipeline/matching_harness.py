#!/usr/bin/env python3
"""Audit matching execution against the master cross-layer stage contract."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .matching_contract_gate import enforce_contracts
except ImportError:
    from matching_contract_gate import enforce_contracts

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "grammar" / "matching-harness-stage-contract.json"
DEFAULT_GENERAL_CONTRACT = ROOT / "grammar" / "general-matching-layer-contract.json"
DEFAULT_ENTRYPOINT_CONTRACT = ROOT / "grammar" / "matching-entrypoint-contract.json"
DEFAULT_TASKS = ROOT / "grammar" / "visual-tasks.json"
DEFAULT_REQUIREMENTS = ROOT / "grammar" / "visual-task-technical-requirements.json"
DEFAULT_COMPARISON = ROOT / "reports" / "visualtask-ae-spec-comparison.json"
DEFAULT_RECONCILIATION = ROOT / "reports" / "prior-editor-review-reconciliation.json"
DEFAULT_TIMING = ROOT / "reports" / "post-render-timing-feasibility.json"
DEFAULT_EXECUTION_PLAN = ROOT / "plans" / "general-matching-layer-tasks.json"
DEFAULT_STORY_ADAPTER = ROOT / "reports" / "storypackage-02-year-seventeen-full-adapter.json"
DEFAULT_STORY_TASKS = ROOT / "reports" / "storypackage-02-year-seventeen-full-task-proposals.json"
DEFAULT_STORY_MATCHING_HANDOFF = ROOT / "reports" / "storypackage-02-year-seventeen-matching-handoff.json"
DEFAULT_STORY_EXCEPTIONS = ROOT / "grammar" / "story-handoff-exceptions.json"
DEFAULT_DATA_HANDOFF = ROOT / "reports" / "storypackage-02-data-handoff-queue.json"
DEFAULT_DATA_ASSIGNMENTS = ROOT / "reports" / "storypackage-02-data-assignments.json"
DEFAULT_BATCH_MATCHING = ROOT / "reports" / "full-visualtask-batch-matching-current.json"
DEFAULT_SEQUENCE_PLAN = ROOT / "reports" / "ordered-visual-route-plan.json"
DEFAULT_ROUTE_DECISIONS = ROOT / "reports" / "ordered-visual-route-decisions.json"
DEFAULT_RENDER_RELEASE = ROOT / "reports" / "render-release-preparation.json"
DEFAULT_OUTPUT = ROOT / "reports" / "matching-harness-audit.json"
DEFAULT_GENERAL_PACKAGE_RECEIPTS = (
    (
        ROOT / "reports" / "storypackage-02-apollo-adapter.json",
        ROOT / "reports" / "storypackage-02-apollo-task-proposals.json",
        "regression",
    ),
    (
        ROOT / "reports" / "storypackage-02-year-seventeen-v12-adapter.json",
        ROOT / "reports" / "storypackage-02-year-seventeen-v12-task-proposals.json",
        "regression",
    ),
    (
        ROOT / "reports" / "storypackage-02-future-volksgeist-v12-adapter.json",
        ROOT / "reports" / "storypackage-02-future-volksgeist-v12-task-proposals.json",
        "user_supplied_calibration",
    ),
    (
        ROOT / "reports" / "storypackage-02-jayz-drake-settle-it-v12-adapter.json",
        ROOT / "reports" / "storypackage-02-jayz-drake-settle-it-v12-task-proposals.json",
        "user_supplied_held_out",
    ),
)
DEFAULT_STRUCTURED_GALLERY = ROOT / "reports" / "storypackage-02-jayz-drake-settle-it-v12-candidate-gallery.json"
GENERAL_RUNTIME_SOURCES = (
    ROOT / "pipeline" / "storypackage_adapter.py",
    ROOT / "pipeline" / "storypackage_splitter.py",
    ROOT / "pipeline" / "visualtask_matching.py",
    ROOT / "pipeline" / "storypackage_candidate_gallery.py",
)
FIXTURE_IDENTIFIERS = (
    "apollo-collins", "year-seventeen", "future-volksgeist", "p01-1",
)
CONTINUATION_TARGET = "objective_complete_or_user_input_required"
ALLOWED_STOP_CONDITIONS = (
    "objective_complete",
    "explicit_user_input_required",
    "authorization_boundary_requires_user",
    "external_blocker_requires_user_action",
)
ALLOWED_BLOCKER_PARTIES = ("you", "data", "story", "matching", "none")
REVIEW_PRINCIPLES = (
    "examplesRequireStoryNeutralReconciliation",
    "visualJobIsNotEveryNarrationDetail",
    "admissionFollowsPrimaryCommunicationRequirement",
    "templateCapabilityEvidenceOverridesHistoricalPopularity",
    "nonTemplateRouteMayBeBetterThanWeakTemplate",
    "humanCommentsAreEvidenceNotApproval",
)
REVIEW_RULES = (
    "editorStatusAndCommentAuthoritySeparated",
    "primaryPresentationOperationControlsAdmission",
    "secondaryOperationsCannotUnionAdmission",
    "incidentalNumbersDoNotCreateDataJobs",
    "scopedFamiliesRequireMatchingOperation",
    "identityRoutesRejectUnrelatedQuantitativeSemantics",
    "templateCapacityMustMatchSemanticAndMediaDemand",
    "brollFallbackDoesNotAuthorizeMedia",
    "pureRhetoricalQuestionMayUseNoTemplate",
    "commentsNeverAuthorizeSelectionOrRendering",
)


def blocker_party(owner: str | None, *, user_input_required: bool,
                  objective_complete: bool) -> str:
    if objective_complete:
        return "none"
    if user_input_required:
        return "you"
    return {
        "story": "story",
        "data": "data",
        "matching": "matching",
        "cross_layer": "matching",
        "editor": "you",
        "render_release": "matching",
    }.get(owner, "matching")


def read(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _source(path: Path) -> dict[str, str]:
    return {"path": Path(path).resolve().relative_to(ROOT.resolve()).as_posix(), "sha256": sha(path)}


def validate_contract(contract: dict[str, Any]) -> None:
    stages = contract.get("stages") or []
    expected = [
        "general_matching_contract", "baseline_reconciliation", "story_handoff", "data_handoff",
        "template_media_feasibility", "sequence_planning", "human_review",
        "render_release_handoff",
    ]
    if [row.get("id") for row in stages] != expected:
        raise ValueError("matching harness stage is missing or reordered")
    if [row.get("order") for row in stages] != list(range(len(expected))):
        raise ValueError("matching harness stage order is invalid")
    if any(not row.get("requires") or not row.get("produces") for row in stages):
        raise ValueError("matching harness stage lacks inputs or receipt")
    policy = contract.get("continuationPolicy") or {}
    if policy.get("objective") != "general-storypackage-matching-layer":
        raise ValueError("matching harness continuation objective is missing")
    if policy.get("taskList") != "plans/general-matching-layer-tasks.json":
        raise ValueError("matching harness continuation task list is invalid")
    if policy.get("reconcileBeforeEveryRun") is not True:
        raise ValueError("matching harness does not require task reconciliation")
    if policy.get("continueUntil") != CONTINUATION_TARGET:
        raise ValueError("matching harness continuation target is invalid")
    if tuple(policy.get("stopOnlyFor") or ()) != ALLOWED_STOP_CONDITIONS:
        raise ValueError("matching harness stop conditions are invalid")
    if policy.get("taskCompletionAloneAllowsStop") is not False:
        raise ValueError("matching harness permits stopping after a routine task")
    if policy.get("statusReportingAloneAllowsStop") is not False:
        raise ValueError("matching harness permits stopping after a status report")
    if policy.get("currentBlockerRequired") is not True:
        raise ValueError("matching harness does not require current-blocker reporting")
    if tuple(policy.get("allowedBlockerParties") or ()) != ALLOWED_BLOCKER_PARTIES:
        raise ValueError("matching harness blocker parties are invalid")
    if "objective_task_reconciliation" not in stages[0]["requires"]:
        raise ValueError("general matching stage does not require objective/task reconciliation")
    if "continuation_receipt" not in stages[0]["produces"]:
        raise ValueError("general matching stage does not produce a continuation receipt")
    if "review_rule_principles_contract" not in stages[0]["requires"]:
        raise ValueError("general matching stage omits review-rule principles")
    if "review_rule_enforcement_receipt" not in stages[0]["produces"]:
        raise ValueError("general matching stage omits review-rule enforcement receipt")
    feasibility = next(row for row in stages if row["id"] == "template_media_feasibility")
    if not {"primary_presentation_operation", "scoped_family_contract", "honest_non_template_disposition"}.issubset(feasibility["requires"]):
        raise ValueError("template/media feasibility omits reconciled review rules")
    human_review = next(row for row in stages if row["id"] == "human_review")
    if not {"editor_status_comment_authority_separation", "scoped_feedback_reconciliation"}.issubset(human_review["requires"]):
        raise ValueError("human review omits scoped feedback principles")
    if contract.get("selectionAuthorized") is not False or contract.get("renderingAuthorized") is not False:
        raise ValueError("stage contract cannot authorize selection or rendering")


def validate_general_contract(contract: dict[str, Any]) -> None:
    runtime = contract.get("runtime") or {}
    evidence = contract.get("evidence") or {}
    required_false = (
        "storySpecificBranchesAllowed", "fixtureIdentifiersAllowed",
        "priorStoryDecisionsCanAdmitCandidates", "priorStoryDecisionsCanOrderCandidates",
        "taskFeedbackCanBecomeGlobalWithoutReconciliation",
    )
    required_true = (
        "templateNeutralTaskContractRequired", "structuredCapabilityAdmissionRequired",
        "brollFallbackAvailable",
    )
    if contract.get("productBoundary") != "any_validated_supported_storypackage":
        raise ValueError("general matching contract has a story-specific product boundary")
    if any(runtime.get(key) is not False for key in required_false):
        raise ValueError("general matching contract permits story-specific runtime behavior")
    if any(runtime.get(key) is not True for key in required_true):
        raise ValueError("general matching contract omits a reusable runtime requirement")
    if evidence.get("minimumDistinctPackages", 0) < 3:
        raise ValueError("general matching contract lacks cross-story proof")
    if evidence.get("userSuppliedHeldOutPackageRequired") is not True:
        raise ValueError("general matching contract lacks a held-out package requirement")
    reconciliation = contract.get("reviewReconciliation") or {}
    principles = reconciliation.get("principles") or {}
    rules = reconciliation.get("rules") or {}
    if any(principles.get(key) is not True for key in REVIEW_PRINCIPLES):
        raise ValueError("general matching contract omits a review-reconciliation principle")
    if any(rules.get(key) is not True for key in REVIEW_RULES):
        raise ValueError("general matching contract omits an enforced editor-review rule")
    execution = contract.get("execution") or {}
    if execution.get("objectiveSource") != "plans/general-matching-layer-tasks.json":
        raise ValueError("general matching contract has no canonical objective source")
    if execution.get("taskListReconciliationRequired") is not True:
        raise ValueError("general matching contract does not require task-list reconciliation")
    if execution.get("objectiveReconciliationRequired") is not True:
        raise ValueError("general matching contract does not require objective reconciliation")
    if execution.get("continueUntil") != CONTINUATION_TARGET:
        raise ValueError("general matching contract continuation target is invalid")
    if tuple(execution.get("allowedStopConditions") or ()) != ALLOWED_STOP_CONDITIONS:
        raise ValueError("general matching contract stop conditions are invalid")
    if execution.get("routineTaskCompletionAllowsStop") is not False:
        raise ValueError("general matching contract permits stopping after a routine task")
    if execution.get("routineStatusUpdateAllowsStop") is not False:
        raise ValueError("general matching contract permits stopping after a status report")
    if execution.get("currentBlockerRequired") is not True:
        raise ValueError("general matching contract omits current-blocker reporting")
    if tuple(execution.get("allowedBlockerParties") or ()) != ALLOWED_BLOCKER_PARTIES:
        raise ValueError("general matching contract blocker parties are invalid")
    if contract.get("selectionAuthorized") is not False or contract.get("renderingAuthorized") is not False:
        raise ValueError("general matching contract cannot authorize selection or rendering")


def execution_plan_summary(plan: dict[str, Any]) -> dict[str, Any]:
    tasks = plan.get("tasks") or []
    if not tasks or len({row.get("id") for row in tasks}) != len(tasks):
        raise ValueError("execution plan tasks are missing or duplicated")
    allowed = {"pending", "in_progress", "passed", "blocked"}
    if any(row.get("status") not in allowed for row in tasks):
        raise ValueError("execution plan has invalid task status")
    if plan.get("planId") != "general-storypackage-matching-layer" or not plan.get("objective"):
        raise ValueError("execution plan does not define the general matching objective")
    policy = plan.get("executionPolicy") or {}
    if policy.get("continueUntil") != CONTINUATION_TARGET:
        raise ValueError("execution plan continuation target is invalid")
    if policy.get("reconcileTaskListBeforeEveryRun") is not True:
        raise ValueError("execution plan does not require task-list reconciliation")
    if policy.get("reconcileObjectiveBeforeEveryRun") is not True:
        raise ValueError("execution plan does not require objective reconciliation")
    if tuple(policy.get("allowedStopConditions") or ()) != ALLOWED_STOP_CONDITIONS:
        raise ValueError("execution plan stop conditions are invalid")
    if policy.get("routineTaskCompletionAllowsStop") is not False:
        raise ValueError("execution plan permits stopping after a routine task")
    if policy.get("routineStatusUpdateAllowsStop") is not False:
        raise ValueError("execution plan permits stopping after a status report")
    if policy.get("currentBlockerRequired") is not True:
        raise ValueError("execution plan omits current-blocker reporting")
    if tuple(policy.get("allowedBlockerParties") or ()) != ALLOWED_BLOCKER_PARTIES:
        raise ValueError("execution plan blocker parties are invalid")
    task_ids = {row["id"] for row in tasks}
    for row in tasks:
        if not row.get("name") or not row.get("owner"):
            raise ValueError("execution plan task lacks a name or owner")
        if not isinstance(row.get("dependsOn"), list):
            raise ValueError("execution plan task lacks explicit dependencies")
        if not isinstance(row.get("userInputRequired"), bool):
            raise ValueError("execution plan task lacks explicit user-input disposition")
        if row["id"] in row["dependsOn"] or not set(row["dependsOn"]).issubset(task_ids):
            raise ValueError("execution plan task has an invalid dependency")
        if row["status"] == "passed" and not row.get("receipt"):
            raise ValueError("passed execution plan task lacks a receipt")
        if row["status"] == "passed" and isinstance(row.get("receipt"), str):
            receipt = Path(row["receipt"])
            if not any((base / receipt).is_file() for base in (ROOT, ROOT.parent)):
                raise ValueError(f"passed execution plan task receipt is missing: {row['receipt']}")
    status_by_id = {row["id"]: row["status"] for row in tasks}
    for row in tasks:
        if row["status"] == "passed" and any(status_by_id[item] != "passed" for item in row["dependsOn"]):
            raise ValueError("passed execution plan task has an incomplete dependency")
    if plan.get("selectionAuthorized") is not False or plan.get("renderingAuthorized") is not False:
        raise ValueError("execution plan cannot authorize selection or rendering")
    incomplete = [row for row in tasks if row["status"] != "passed"]
    ready = [row for row in incomplete if all(status_by_id[item] == "passed" for item in row["dependsOn"])]
    ready_non_user = [row for row in ready if not row["userInputRequired"]]
    user_input_tasks = [row for row in ready if row["userInputRequired"]]
    next_task = ready_non_user[0] if ready_non_user else (ready[0] if ready else (incomplete[0] if incomplete else None))
    objective_complete = not incomplete
    user_input_required = bool(user_input_tasks) and not ready_non_user
    stop_allowed = objective_complete or user_input_required
    current_blocker = blocker_party(
        next_task["owner"] if next_task else None,
        user_input_required=user_input_required,
        objective_complete=objective_complete,
    )
    return {
        "planId": plan["planId"],
        "objective": plan["objective"],
        "completed": sum(row["status"] == "passed" for row in tasks),
        "total": len(tasks),
        "nextTaskId": next_task["id"] if next_task else None,
        "nextTaskName": next_task["name"] if next_task else None,
        "nextTaskOwner": next_task["owner"] if next_task else None,
        "readyTaskIds": [row["id"] for row in ready],
        "readyNonUserTaskIds": [row["id"] for row in ready_non_user],
        "objectiveComplete": objective_complete,
        "userInputRequired": user_input_required,
        "userInputTaskIds": [row["id"] for row in user_input_tasks],
        "continuationRequired": not stop_allowed,
        "stopAllowed": stop_allowed,
        "stopReason": ("objective_complete" if objective_complete else
                       "explicit_user_input_required" if user_input_required else None),
        "currentBlocker": {
            "party": current_blocker,
            "taskId": next_task["id"] if next_task else None,
            "taskName": next_task["name"] if next_task else None,
            "reason": ("objective_complete" if objective_complete else
                       "user_input_required" if user_input_required else
                       "next_ready_task_owned_by_layer"),
            "userActionRequired": current_blocker == "you",
        },
    }


def build(*, mode: str = "evaluation_fixture", contract_path: Path = DEFAULT_CONTRACT,
          general_contract_path: Path = DEFAULT_GENERAL_CONTRACT,
          general_package_receipts: tuple[tuple[Path, Path, str], ...] = DEFAULT_GENERAL_PACKAGE_RECEIPTS,
          structured_gallery_path: Path = DEFAULT_STRUCTURED_GALLERY,
          general_runtime_sources: tuple[Path, ...] = GENERAL_RUNTIME_SOURCES,
          tasks_path: Path = DEFAULT_TASKS, requirements_path: Path = DEFAULT_REQUIREMENTS,
          comparison_path: Path = DEFAULT_COMPARISON, reconciliation_path: Path = DEFAULT_RECONCILIATION,
          timing_path: Path = DEFAULT_TIMING, execution_plan_path: Path = DEFAULT_EXECUTION_PLAN,
          story_adapter_path: Path = DEFAULT_STORY_ADAPTER,
          story_tasks_path: Path = DEFAULT_STORY_TASKS,
          story_matching_handoff_path: Path = DEFAULT_STORY_MATCHING_HANDOFF,
          story_exceptions_path: Path = DEFAULT_STORY_EXCEPTIONS,
          data_handoff_path: Path = DEFAULT_DATA_HANDOFF,
          data_assignments_path: Path = DEFAULT_DATA_ASSIGNMENTS,
          batch_matching_path: Path = DEFAULT_BATCH_MATCHING,
          sequence_plan_path: Path = DEFAULT_SEQUENCE_PLAN,
          route_decisions_path: Path = DEFAULT_ROUTE_DECISIONS,
          render_release_path: Path = DEFAULT_RENDER_RELEASE) -> dict[str, Any]:
    contract_receipt = enforce_contracts(
        "matching_harness.build", mode="production" if mode == "production" else "review_only"
    )
    contract = read(contract_path)
    validate_contract(contract)
    general_contract = read(general_contract_path)
    validate_general_contract(general_contract)
    if mode not in contract["modes"]:
        raise ValueError("unsupported matching harness mode")
    tasks = read(tasks_path).get("tasks") or []
    requirements = read(requirements_path).get("tasks") or []
    comparison = read(comparison_path)
    reconciliation = read(reconciliation_path)
    timing = read(timing_path)
    execution_plan = read(execution_plan_path)
    plan_summary = execution_plan_summary(execution_plan)
    story_adapter = read(story_adapter_path)
    story_tasks = read(story_tasks_path)
    story_matching_handoff = read(story_matching_handoff_path)
    story_exceptions = read(story_exceptions_path)
    data_handoff = read(data_handoff_path)
    data_assignments = read(data_assignments_path)
    batch_matching = read(batch_matching_path)
    sequence_plan = read(sequence_plan_path)
    route_decisions = read(route_decisions_path)
    render_release = read(render_release_path)
    structured_gallery = read(structured_gallery_path)

    generality_gaps: list[dict[str, Any]] = []
    if not plan_summary["objectiveComplete"]:
        generality_gaps.append({
            "kind": "general_matching_objective_tasks_incomplete",
            "nextTaskId": plan_summary["nextTaskId"],
            "nextTaskOwner": plan_summary["nextTaskOwner"],
            "continuationRequired": plan_summary["continuationRequired"],
            "userInputRequired": plan_summary["userInputRequired"],
        })
    package_evidence = []
    package_ids = set()
    held_out_count = 0
    regression_count = 0
    for adapter_path, proposal_path, role in general_package_receipts:
        adapter = read(adapter_path)
        proposals = read(proposal_path)
        package_id = adapter.get("packageId")
        package_ids.add(package_id)
        if role == "user_supplied_held_out":
            held_out_count += 1
        elif role in {"regression", "user_supplied_calibration"}:
            regression_count += 1
        gaps = []
        if not package_id or proposals.get("packageId") != package_id:
            gaps.append("adapter_task_package_mismatch")
        if adapter.get("storyHandoffReceipt", {}).get("accepted") is not True:
            gaps.append("storypackage_adapter_not_accepted")
        if proposals.get("activationState") != "review_only_not_connected":
            gaps.append("task_proposals_not_review_only")
        if proposals.get("selectionAuthorized") is not False or proposals.get("renderingAuthorized") is not False:
            gaps.append("task_proposals_authorize_selection_or_rendering")
        if proposals.get("counts", {}).get("uncoveredClaims") != 0:
            gaps.append("narrator_claims_not_completely_routed")
        if proposals.get("source", {}).get("sha256") != sha(adapter_path):
            gaps.append("task_proposal_source_stale")
        package_evidence.append({
            "packageId": package_id, "role": role,
            "claims": proposals.get("counts", {}).get("claims"),
            "taskProposals": proposals.get("counts", {}).get("taskProposals"),
            "uncoveredClaims": proposals.get("counts", {}).get("uncoveredClaims"),
            "status": "passed" if not gaps else "blocked", "gaps": gaps,
        })
        generality_gaps.extend({"kind": gap, "packageId": package_id} for gap in gaps)

    evidence_contract = general_contract["evidence"]
    if len(package_ids) < evidence_contract["minimumDistinctPackages"]:
        generality_gaps.append({"kind": "insufficient_distinct_storypackages", "count": len(package_ids)})
    if regression_count < evidence_contract["minimumRegressionPackages"]:
        generality_gaps.append({"kind": "insufficient_regression_storypackages", "count": regression_count})
    if held_out_count < 1:
        generality_gaps.append({"kind": "user_supplied_held_out_storypackage_missing"})

    source_violations = []
    for source_path in general_runtime_sources:
        content = source_path.read_text(encoding="utf-8").lower()
        found = [identifier for identifier in FIXTURE_IDENTIFIERS if identifier in content]
        if found:
            source_violations.append({"path": source_path.relative_to(ROOT).as_posix(), "identifiers": found})
    if source_violations:
        generality_gaps.append({"kind": "fixture_identifier_in_general_runtime", "sources": source_violations})

    retrieval = structured_gallery.get("retrievalReceipt") or {}
    if structured_gallery.get("packageId") not in package_ids:
        generality_gaps.append({"kind": "structured_gallery_package_not_in_cross_story_evidence"})
    if retrieval.get("structuredCompatibilityRequired") is not True:
        generality_gaps.append({"kind": "structured_candidate_admission_not_required"})
    if retrieval.get("legacyJobBindingCanAdmit") is not False:
        generality_gaps.append({"kind": "legacy_job_binding_can_admit"})
    if structured_gallery.get("selectionAuthorized") is not False or structured_gallery.get("renderingAuthorized") is not False:
        generality_gaps.append({"kind": "structured_gallery_authorizes_selection_or_rendering"})
    task_by_id = {row["taskId"]: row for row in requirements}
    batch_tasks = batch_matching.get("tasks") or []
    candidate_verdicts: Counter[str] = Counter()
    media_needing_resolution: list[str] = []
    for row in batch_tasks:
        candidates = row.get("templateResult", {}).get("candidates") or []
        for candidate in candidates:
            verdict = candidate.get("fitAssessment", {}).get("verdict", "unresolved")
            candidate_verdicts[verdict] += 1
        if row.get("mediaResult", {}).get("availabilityVerdict") not in {"available", "not_required"}:
            media_needing_resolution.append(row["taskId"])

    required_review_keys = {row["id"].split(".", 1)[0] for row in tasks}
    covered_review_keys = {
        key for row in story_tasks.get("taskProposals") or []
        for key in row.get("reviewKeys") or []
    }
    exceptions = story_exceptions.get("exceptions") or []
    def exception_for(row: dict[str, Any]) -> dict[str, Any] | None:
        return next((item for item in exceptions if
            item.get("packageId") == story_adapter.get("packageId") and
            item.get("gap") == row.get("gap") and
            item.get("claim") == row.get("claim") and
            item.get("text") == row.get("text") and
            item.get("effect") == "non_blocking_deferred_registry_cleanup" and
            item.get("provenance", {}).get("source") == "user"
        ), None)
    story_gaps = []
    for row in story_tasks.get("gaps") or []:
        exception = exception_for(row)
        story_gaps.append({
            "kind": row["gap"],
            **{key: value for key, value in row.items() if key != "gap"},
            "blocking": exception is None,
            "exceptionId": exception.get("id") if exception else None,
        })
    missing_review_keys = sorted(required_review_keys - covered_review_keys)
    if missing_review_keys:
        story_gaps.append({"kind": "review_keys_uncovered", "reviewKeys": missing_review_keys})
    if story_adapter.get("storyHandoffReceipt", {}).get("accepted") is not True:
        story_gaps.append({"kind": "storypackage_checker_receipt_missing"})
    if story_tasks.get("source", {}).get("sha256") != sha(story_adapter_path):
        story_gaps.append({"kind": "storypackage_splitter_receipt_stale"})
    if story_matching_handoff.get("storyMatchingHandoffReceipt", {}).get("accepted") is not True:
        story_gaps.append({"kind": "story_matching_handoff_checker_receipt_missing"})
    if story_matching_handoff.get("packageId") != story_adapter.get("packageId"):
        story_gaps.append({"kind": "story_matching_handoff_package_mismatch"})
    matching_handoff_ids = {row.get("taskId") for row in story_matching_handoff.get("tasks") or []}
    if matching_handoff_ids != {row.get("id") for row in tasks}:
        story_gaps.append({"kind": "story_matching_handoff_task_scope_mismatch"})
    for row in story_matching_handoff.get("unresolved") or []:
        story_gaps.append({
            "kind": row["kind"],
            "itemId": row["itemId"],
            "taskId": row.get("taskId"),
            "claimIds": row.get("claimIds") or [],
            "reason": row["reason"],
            "blocking": False,
            "deferredTo": "template_media_feasibility" if row["kind"] == "focal_unknown" else "sequence_planning",
        })
    sequence_scenes = sequence_plan.get("scenes") or []
    sequence_gaps = []
    if sequence_plan.get("sequencePlanningReceipt", {}).get("accepted") is not True:
        sequence_gaps.append({"kind": "sequence_planning_receipt_missing"})
    if {row.get("taskId") for row in sequence_scenes} != {row.get("id") for row in tasks}:
        sequence_gaps.append({"kind": "sequence_task_scope_mismatch"})
    if any(not row.get("transition", {}).get("required") or not row.get("brollFallbackAvailable") for row in sequence_scenes):
        sequence_gaps.append({"kind": "route_timing_or_transition_disposition_missing"})
    if sequence_plan.get("counts", {}).get("sequenceConflicts"):
        sequence_gaps.append({"kind": "sequence_conflicts_remaining", "count": sequence_plan["counts"]["sequenceConflicts"]})
    deferred_routes = [row for row in sequence_scenes if row.get("route") == "deferred"]
    if deferred_routes:
        sequence_gaps.append({
            "kind": "editor_ruled_out_broll_but_template_route_is_not_gate_complete",
            "count": len(deferred_routes),
            "taskIds": [row["taskId"] for row in deferred_routes],
        })
    for name, item in sequence_plan.get("sources", {}).items():
        path = ROOT / item.get("path", "")
        if not path.is_file() or sha(path) != item.get("sha256"):
            sequence_gaps.append({"kind": "sequence_source_missing_or_stale", "source": name})
    template_review_routes = [row for row in sequence_scenes if row.get("route") == "template_review"]
    human_review_gaps = []
    decisions = route_decisions.get("decisions") or {}
    if route_decisions.get("sourcePlanSha256") != sha(sequence_plan_path):
        human_review_gaps.append({"kind": "route_decisions_stale"})
    for row in template_review_routes:
        decision = decisions.get(row["taskId"])
        valid_ids = {choice["candidateId"] for choice in row.get("templateChoices") or []}
        if not decision:
            human_review_gaps.append({"kind": "final_template_selection_pending", "taskId": row["taskId"]})
        elif (decision.get("route") != "template" or decision.get("candidateId") not in valid_ids or
              decision.get("humanSelected") is not True):
            human_review_gaps.append({"kind": "invalid_route_decision", "taskId": row["taskId"]})
    stage_results = [
        {"id": "general_matching_contract", "status": "blocked" if generality_gaps else "passed", "gaps": generality_gaps},
        {"id": "baseline_reconciliation", "status": "passed" if reconciliation.get("priorSelectionCoverage", {}).get("total") == 107 else "blocked", "gaps": [] if reconciliation.get("priorSelectionCoverage", {}).get("total") == 107 else ["prior_editor_decisions_incomplete"]},
        {"id": "story_handoff", "status": "blocked" if any(row.get("blocking", True) for row in story_gaps) else "passed", "gaps": story_gaps},
        {"id": "data_handoff", "status": "blocked" if not data_assignments.get("dataHandoffComplete") else "passed", "gaps": ([{"kind": "typed_data_gaps_remaining", "taskIds": [row["taskId"] for row in data_assignments.get("assignments") or [] if row.get("status") != "resolved"], "count": data_assignments.get("counts", {}).get("typedGaps", 0)}] if not data_assignments.get("dataHandoffComplete") else [])},
        {"id": "template_media_feasibility", "status": "passed", "gaps": [
            {"kind": "system_resolution_queue", "count": len(reconciliation.get("systemResolutionQueue") or [])},
            {"kind": "template_fit_not_final", "verdicts": batch_matching.get("counts", {}).get("templateVerdicts", {})},
            {"kind": "media_availability_not_final", "verdicts": batch_matching.get("counts", {}).get("mediaVerdicts", {})},
            {"kind": "preferred_media_unresolved_broll_fallback_available", "blocking": False, "taskIds": media_needing_resolution},
            {"kind": "story_focal_unknown", "taskIds": [row["taskId"] for row in story_matching_handoff.get("unresolved") or [] if row["kind"] == "focal_unknown"]},
        ]},
        {"id": "sequence_planning", "status": "blocked" if sequence_gaps else "passed", "gaps": sequence_gaps},
        {"id": "human_review", "status": "blocked" if human_review_gaps else "passed", "gaps": human_review_gaps},
        {"id": "render_release_handoff",
         "status": "passed" if render_release.get("releaseReady") else "blocked",
         "gaps": ([] if render_release.get("releaseReady") else [
             {"kind": "render_release_receipts_incomplete",
              "blockedScenes": render_release.get("counts", {}).get("blocked"),
              "blockersByKind": render_release.get("counts", {}).get("blockersByKind", {}),
              "requiredReceipts": render_release.get("requiredReceipts", {})}
         ])},
    ]
    first_blocked = next((row["id"] for row in stage_results if row["status"] != "passed"), None)
    return {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": 1,
        "mode": mode,
        "purpose": "Enforce master-plan stage order and cross-layer requirement timing",
        "sources": {name: _source(path) for name, path in {
            "generalMatchingContract": general_contract_path,
            "matchingEntrypointContract": DEFAULT_ENTRYPOINT_CONTRACT,
            "contract": contract_path, "visualTasks": tasks_path, "technicalRequirements": requirements_path,
            "technicalComparison": comparison_path, "priorReviewReconciliation": reconciliation_path,
            "timingPlans": timing_path, "executionPlan": execution_plan_path,
            "storyPackageAdapter": story_adapter_path, "storyTaskProposals": story_tasks_path,
            "storyMatchingHandoff": story_matching_handoff_path,
            "storyHandoffExceptions": story_exceptions_path,
            "dataHandoffQueue": data_handoff_path,
            "dataAssignments": data_assignments_path,
            "fullVisualTaskBatchMatching": batch_matching_path,
            "orderedVisualRoutePlan": sequence_plan_path,
            "orderedVisualRouteDecisions": route_decisions_path,
            "renderReleasePreparation": render_release_path,
            "structuredCandidateGallery": structured_gallery_path,
            **{
                f"generalPackageAdapter{index + 1}": pair[0]
                for index, pair in enumerate(general_package_receipts)
            },
            **{
                f"generalPackageTasks{index + 1}": pair[1]
                for index, pair in enumerate(general_package_receipts)
            },
            **{
                f"generalRuntimeSource{index + 1}": path
                for index, path in enumerate(general_runtime_sources)
            },
        }.items()},
        "executionPlan": plan_summary,
        "continuation": {
            "objective": plan_summary["objective"],
            "taskListPath": _source(execution_plan_path)["path"],
            "taskListReconciled": True,
            "objectiveReconciled": True,
            "objectiveComplete": plan_summary["objectiveComplete"],
            "nextTaskId": plan_summary["nextTaskId"],
            "nextTaskName": plan_summary["nextTaskName"],
            "nextTaskOwner": plan_summary["nextTaskOwner"],
            "continuationRequired": plan_summary["continuationRequired"],
            "userInputRequired": plan_summary["userInputRequired"],
            "stopAllowed": plan_summary["stopAllowed"],
            "stopReason": plan_summary["stopReason"],
            "currentBlocker": plan_summary["currentBlocker"],
        },
        "generalMatchingLayer": {
            "contractId": general_contract.get("contractId"),
            "productBoundary": general_contract.get("productBoundary"),
            "distinctPackages": len(package_ids),
            "regressionPackages": regression_count,
            "userSuppliedHeldOutPackages": held_out_count,
            "packages": package_evidence,
            "runtimeSourcesChecked": len(general_runtime_sources),
            "runtimeSourceViolations": source_violations,
            "structuredCapabilityAdmissionRequired": retrieval.get("structuredCompatibilityRequired"),
            "legacyJobBindingCanAdmit": retrieval.get("legacyJobBindingCanAdmit"),
            "taskFeedbackScope": "story_and_task_until_reconciled",
            "reviewRulePrinciples": {
                "principles": {key: general_contract["reviewReconciliation"]["principles"][key] for key in REVIEW_PRINCIPLES},
                "rules": {key: general_contract["reviewReconciliation"]["rules"][key] for key in REVIEW_RULES},
                "principleCount": len(REVIEW_PRINCIPLES),
                "ruleCount": len(REVIEW_RULES),
                "contractSha256": sha(general_contract_path),
                "selectionAuthorized": False,
                "renderingAuthorized": False,
            },
            "complete": not generality_gaps,
            "selectionAuthorized": False,
            "renderingAuthorized": False,
        },
        "storyHandoff": {
            "packageId": story_adapter.get("packageId"),
            "packageSha256": story_adapter.get("storyHandoffReceipt", {}).get("packageSha256"),
            "authorityCommit": story_adapter.get("storyHandoffReceipt", {}).get("authorityCommit"),
            "requiredReviewKeys": len(required_review_keys),
            "coveredReviewKeys": len(required_review_keys & covered_review_keys),
            "taskProposals": len(story_tasks.get("taskProposals") or []),
            "uncoveredClaims": story_tasks.get("counts", {}).get("uncoveredClaims"),
            "matchingHandoffTasks": story_matching_handoff.get("counts", {}).get("tasks"),
            "matchingHandoffUnresolved": story_matching_handoff.get("counts", {}).get("unresolved"),
            "typedGaps": len(story_gaps),
        },
        "dataHandoff": {
            "packageId": data_handoff.get("packageId"),
            "assignments": data_handoff.get("counts", {}).get("assignments"),
            "awaitingDataLayer": (data_assignments.get("counts", {}).get("partial", 0) + data_assignments.get("counts", {}).get("blocked", 0)),
            "resolved": data_assignments.get("counts", {}).get("resolved"),
            "partial": data_assignments.get("counts", {}).get("partial"),
            "blocked": data_assignments.get("counts", {}).get("blocked"),
            "typedFields": data_assignments.get("counts", {}).get("typedFields"),
            "typedGaps": data_assignments.get("counts", {}).get("typedGaps"),
            "complete": data_assignments.get("dataHandoffComplete"),
        },
        "templateMediaFeasibility": {
            "beatTemplateRequired": False,
            "brollFallbackAlwaysAllowed": True,
            "minimumTemplateChoiceCount": 0,
            "visualTasks": batch_matching.get("counts", {}).get("visualTasks"),
            "templateVerdicts": batch_matching.get("counts", {}).get("templateVerdicts", {}),
            "mediaVerdicts": batch_matching.get("counts", {}).get("mediaVerdicts", {}),
            "candidateVerdicts": dict(sorted(candidate_verdicts.items())),
            "emptyTemplateChoiceSetsBlocking": False,
            "mediaTasksNeedingResolution": len(media_needing_resolution),
            "mediaTaskIdsNeedingResolution": media_needing_resolution,
            "preferredMediaGapsBlocking": 0,
            "selectionAuthorized": batch_matching.get("selectionAuthorized"),
            "renderingAuthorized": batch_matching.get("renderingAuthorized"),
        },
        "sequencePlanning": {
            "planId": sequence_plan.get("planId"),
            "scenes": sequence_plan.get("counts", {}).get("scenes"),
            "brollRoutes": sequence_plan.get("counts", {}).get("brollRoutes"),
            "templateReviewRoutes": sequence_plan.get("counts", {}).get("templateReviewRoutes"),
            "deferredRoutes": sequence_plan.get("counts", {}).get("deferredRoutes"),
            "postBeatBrollSegments": sequence_plan.get("counts", {}).get("postBeatBrollSegments"),
            "transitionsRequired": sequence_plan.get("counts", {}).get("transitionsRequired"),
            "sequenceConflicts": sequence_plan.get("counts", {}).get("sequenceConflicts"),
            "complete": not sequence_gaps,
            "selectionAuthorized": sequence_plan.get("selectionAuthorized"),
            "renderingAuthorized": sequence_plan.get("renderingAuthorized"),
        },
        "humanReview": {
            "templateReviewTasks": len(template_review_routes),
            "decisions": len(decisions),
            "carriedPriorChoices": sum(row.get("selectionSource") == "carried_prior_editor_choice" for row in decisions.values()),
            "unresolved": len(human_review_gaps),
            "complete": not human_review_gaps,
            "renderingAuthorized": route_decisions.get("renderingAuthorized"),
        },
        "renderRelease": {
            "packetId": render_release.get("packetId"),
            "scenes": render_release.get("counts", {}).get("scenes"),
            "releaseReady": render_release.get("counts", {}).get("releaseReady"),
            "blocked": render_release.get("counts", {}).get("blocked"),
            "blockersByKind": render_release.get("counts", {}).get("blockersByKind", {}),
            "requiredReceipts": render_release.get("requiredReceipts", {}),
            "renderingAuthorized": render_release.get("renderingAuthorized"),
        },
        "stageResults": stage_results,
        "firstBlockingStage": first_blocked,
        "productionAllowed": mode == "production" and first_blocked is None,
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "counts": {
            "visualTasks": len(tasks), "technicalRequirementTasks": len(task_by_id),
            "comparisonCandidates": comparison.get("counts", {}).get("baselineCandidates"),
            "timingPlans": timing.get("counts", {}).get("evaluated", len(timing.get("rows") or [])),
        },
    }


def validate(artifact: dict[str, Any], *, verify_sources: bool = True) -> dict[str, Any]:
    enforcement = artifact.get("contractEnforcementReceipt") or {}
    if enforcement.get("enforced") is not True or enforcement.get("entrypoint") != "matching_harness.build":
        raise ValueError("matching harness contract enforcement receipt is missing")
    enforced_contracts = enforcement.get("contracts") or {}
    expected_contract_hashes = {
        "generalMatching": sha(DEFAULT_GENERAL_CONTRACT),
        "stageOrder": sha(DEFAULT_CONTRACT),
        "entrypoints": sha(DEFAULT_ENTRYPOINT_CONTRACT),
    }
    if any((enforced_contracts.get(name) or {}).get("sha256") != digest
           for name, digest in expected_contract_hashes.items()):
        raise ValueError("matching harness contract enforcement receipt is stale")
    expected = ["general_matching_contract", "baseline_reconciliation", "story_handoff", "data_handoff", "template_media_feasibility", "sequence_planning", "human_review", "render_release_handoff"]
    if [row.get("id") for row in artifact.get("stageResults") or []] != expected:
        raise ValueError("matching audit stage is missing or reordered")
    if artifact.get("productionAllowed") and any(row.get("status") != "passed" for row in artifact["stageResults"]):
        raise ValueError("production allowed with incomplete stage")
    if artifact.get("selectionAuthorized") is not False or artifact.get("renderingAuthorized") is not False:
        raise ValueError("matching audit cannot authorize selection or rendering")
    review_policy = (artifact.get("generalMatchingLayer") or {}).get("reviewRulePrinciples") or {}
    if any((review_policy.get("principles") or {}).get(key) is not True for key in REVIEW_PRINCIPLES):
        raise ValueError("matching audit omits review-reconciliation principles")
    if any((review_policy.get("rules") or {}).get(key) is not True for key in REVIEW_RULES):
        raise ValueError("matching audit omits enforced editor-review rules")
    if review_policy.get("contractSha256") != sha(DEFAULT_GENERAL_CONTRACT):
        raise ValueError("matching audit review-rule contract is stale")
    if review_policy.get("selectionAuthorized") is not False or review_policy.get("renderingAuthorized") is not False:
        raise ValueError("matching audit review-rule receipt authorizes selection or rendering")
    continuation = artifact.get("continuation") or {}
    if continuation.get("taskListReconciled") is not True or continuation.get("objectiveReconciled") is not True:
        raise ValueError("matching audit lacks mandatory objective/task reconciliation")
    objective_complete = continuation.get("objectiveComplete") is True
    user_input_required = continuation.get("userInputRequired") is True
    continuation_required = continuation.get("continuationRequired") is True
    stop_allowed = continuation.get("stopAllowed") is True
    if stop_allowed != (objective_complete or user_input_required):
        raise ValueError("matching audit stop receipt is inconsistent")
    if continuation_required != (not stop_allowed):
        raise ValueError("matching audit continuation receipt is inconsistent")
    if not objective_complete and not user_input_required and not continuation_required:
        raise ValueError("matching audit silently stops before the general objective is complete")
    if continuation_required and not continuation.get("nextTaskId"):
        raise ValueError("matching audit requires continuation but has no next task")
    blocker = continuation.get("currentBlocker") or {}
    if blocker.get("party") not in ALLOWED_BLOCKER_PARTIES:
        raise ValueError("matching audit current blocker is missing or invalid")
    if (blocker.get("party") == "you") != user_input_required:
        raise ValueError("matching audit blocker does not match its user-input state")
    if blocker.get("userActionRequired") != (blocker.get("party") == "you"):
        raise ValueError("matching audit blocker action requirement is inconsistent")
    if verify_sources:
        for item in artifact.get("sources", {}).values():
            path = ROOT / item["path"]
            if not path.is_file() or sha(path) != item["sha256"]:
                raise ValueError("matching harness input is missing or stale")
    return {
        "firstBlockingStage": artifact.get("firstBlockingStage"),
        "productionAllowed": artifact.get("productionAllowed"),
        "continuationRequired": continuation_required,
        "nextTaskId": continuation.get("nextTaskId"),
        "userInputRequired": user_input_required,
        "currentBlocker": blocker.get("party"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "validate"))
    parser.add_argument("--mode", choices=("evaluation_fixture", "production"), default="evaluation_fixture")
    args = parser.parse_args()
    if args.command == "build":
        artifact = build(mode=args.mode)
        DEFAULT_OUTPUT.write_text(dumps(artifact))
        print(json.dumps(validate(artifact, verify_sources=False), sort_keys=True))
    else:
        print(json.dumps(validate(read(DEFAULT_OUTPUT)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
