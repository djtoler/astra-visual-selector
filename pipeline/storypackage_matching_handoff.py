#!/usr/bin/env python3
"""Validate and normalize a StoryPackage matching handoff for review-only consumers."""

from __future__ import annotations

import argparse
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
