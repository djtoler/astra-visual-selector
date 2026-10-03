#!/usr/bin/env python3
"""Route story-linked data-bearing VisualTasks to typed field assignment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .matching_contract_gate import enforce_contracts
except ImportError:
    from matching_contract_gate import enforce_contracts

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STORY_TASKS = ROOT / "reports" / "storypackage-02-year-seventeen-full-task-proposals.json"
DEFAULT_REQUIREMENTS = ROOT / "grammar" / "visual-task-technical-requirements.json"
DEFAULT_OUTPUT = ROOT / "reports" / "storypackage-02-data-handoff-queue.json"


def _read(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(*, story_tasks: dict[str, Any] | None = None,
          requirements: dict[str, Any] | None = None) -> dict[str, Any]:
    contract_receipt = enforce_contracts("storypackage_data_handoff.build")
    story = story_tasks if story_tasks is not None else _read(DEFAULT_STORY_TASKS)
    technical = requirements if requirements is not None else _read(DEFAULT_REQUIREMENTS)
    proposals = story.get("taskProposals") or []
    assignments = []
    for task in technical.get("tasks") or []:
        data = task.get("dataRequirements") or {}
        encodings = data.get("requiredEncodings") or []
        if not encodings:
            continue
        review_key = task.get("sourceBeatId") or task["taskId"].split(".", 1)[0]
        linked = [row for row in proposals if review_key in (row.get("reviewKeys") or [])]
        if not linked:
            raise ValueError(f"data-bearing VisualTask lacks StoryPackage proposal: {task['taskId']}")
        assignments.append({
            "taskId": task["taskId"],
            "reviewKey": review_key,
            "claimIds": sorted({claim for row in linked for claim in row["claimIds"]}),
            "jobProposalIds": sorted({row["jobProposalId"] for row in linked}),
            "jobs": sorted({row["job"] for row in linked}),
            "requiredEncodings": encodings,
            "semanticConstraints": data.get("semanticConstraints") or [],
            "requiredTypedFields": None,
            "status": "awaiting_data_layer",
        })
    return {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": 1,
        "packageId": story["packageId"],
        "purpose": "Source-bound queue for typed data field assignment before template/media feasibility",
        "sources": {
            "storyTaskProposals": {"path": str(DEFAULT_STORY_TASKS), "sha256": _sha(DEFAULT_STORY_TASKS)},
            "technicalRequirements": {"path": str(DEFAULT_REQUIREMENTS), "sha256": _sha(DEFAULT_REQUIREMENTS)},
        },
        "assignments": assignments,
        "counts": {
            "currentVisualTasks": len(technical.get("tasks") or []),
            "assignments": len(assignments),
            "awaitingDataLayer": len(assignments),
        },
        "dataHandoffComplete": False,
        "selectionAuthorized": False,
        "renderingAuthorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build",))
    args = parser.parse_args()
    artifact = build()
    DEFAULT_OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps(artifact["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
