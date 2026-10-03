#!/usr/bin/env python3
"""Carry the editor's first surviving prior choice into each final template route."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .matching_contract_gate import enforce_contracts
except ImportError:
    from matching_contract_gate import enforce_contracts

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "reports" / "ordered-visual-route-plan.json"
DEFAULT_OUTPUT = ROOT / "reports" / "ordered-visual-route-decisions.json"


def read(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def build(plan_path: Path = DEFAULT_PLAN) -> dict[str, Any]:
    contract_receipt = enforce_contracts("carry_prior_route_choices.build")
    plan = read(plan_path)
    decisions = {}
    unresolved = []
    for row in plan.get("scenes") or []:
        if row.get("route") != "template_review":
            continue
        prior = [choice for choice in row.get("templateChoices") or [] if choice.get("priorEditorSelected")]
        if not prior:
            unresolved.append(row["taskId"])
            continue
        choice = prior[0]
        decisions[row["taskId"]] = {
            "taskId": row["taskId"],
            "route": "template",
            "candidateId": choice["candidateId"],
            "humanSelected": True,
            "selectionSource": "carried_prior_editor_choice",
            "selectionReason": "User instructed the system to use the earlier choice rather than ask again.",
            "tieBreak": "first_surviving_prior_choice_in_preserved_review_order",
            "note": "",
            "reviewer": "human_prior_decision",
            "revision": 1,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "renderingAuthorized": False,
        }
    artifact = {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": 1,
        "sourcePlanSha256": sha(plan_path),
        "sourcePlanId": plan.get("planId"),
        "decisionAuthority": "user_instruction_reuse_earlier_choice_2026-10-02",
        "decisions": decisions,
        "unresolvedTaskIds": unresolved,
        "counts": {
            "templateReviewTasks": sum(row.get("route") == "template_review" for row in plan.get("scenes") or []),
            "carriedPriorChoices": len(decisions),
            "unresolved": len(unresolved),
        },
        "selectionAuthorizedForRecordedTasks": True,
        "renderingAuthorized": False,
    }
    validate(artifact, plan_path=plan_path)
    return artifact


def validate(artifact: dict[str, Any], *, plan_path: Path = DEFAULT_PLAN) -> dict[str, Any]:
    plan = read(plan_path)
    if artifact.get("sourcePlanSha256") != sha(plan_path):
        raise ValueError("Prior-choice decisions refer to a stale ordered plan.")
    routes = {row["taskId"]: row for row in plan.get("scenes") or [] if row.get("route") == "template_review"}
    decisions = artifact.get("decisions") or {}
    if set(decisions) | set(artifact.get("unresolvedTaskIds") or []) != set(routes):
        raise ValueError("Prior-choice reconciliation does not cover every template route.")
    for task_id, decision in decisions.items():
        valid = [choice["candidateId"] for choice in routes[task_id]["templateChoices"] if choice.get("priorEditorSelected")]
        if not valid or decision.get("candidateId") != valid[0]:
            raise ValueError("Carried decision is not the first surviving prior editor choice.")
        if decision.get("route") != "template" or decision.get("humanSelected") is not True:
            raise ValueError("Carried decision lost its editorial source.")
    if artifact.get("renderingAuthorized") is not False:
        raise ValueError("Prior-choice reconciliation cannot authorize rendering.")
    counts = artifact.get("counts") or {}
    if counts != {"templateReviewTasks": len(routes), "carriedPriorChoices": len(decisions),
                  "unresolved": len(artifact.get("unresolvedTaskIds") or [])}:
        raise ValueError("Prior-choice reconciliation counts are stale.")
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "validate"))
    args = parser.parse_args()
    if args.command == "build":
        artifact = build()
        DEFAULT_OUTPUT.write_text(dumps(artifact))
        print(json.dumps(validate(artifact), sort_keys=True))
    else:
        print(json.dumps(validate(read(DEFAULT_OUTPUT)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
