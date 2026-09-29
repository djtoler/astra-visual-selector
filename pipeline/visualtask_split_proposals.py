#!/usr/bin/env python3
"""Prepare and validate review-only semantic VisualTask split proposals."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BEATS = ROOT / "pipeline" / "beats-all.json"
REVIEWS = ROOT / "grammar" / "beat-review-export-2026-09-27.json"
ISSUES = ROOT / "grammar" / "issues_matching_layer.json"
PROMPT = ROOT / "prompts" / "PROMPT-visual-task-splits.md"
CONTENT_MGR = ROOT.parent / "content-project-mgr"
MATCHING_DOCS = (
    CONTENT_MGR / "HANDOFF_data_matching_media.md",
    CONTENT_MGR / "documentary_system_handoff.md",
    CONTENT_MGR / "handoff_comparison_and_updates.md",
    CONTENT_MGR / "final_documentary_system_plan.md",
)
REQUEST = ROOT / "visual-task-splits" / "review-001" / "request.json"
DRAFT = ROOT / "visual-task-splits" / "review-001" / "draft.json"
JOBS = {
    "one_vs_aggregate", "one_vs_many_individually", "entity_vs_benchmark",
    "proportion_of_cohort", "parallel_instances", "change_across_set",
    "members_then_total", "category_breakdown", "inversion", "intersection_of_sets",
    "streak_over_time", "equivalence_restatement", "derived_quantity",
    "locate_in_distribution", "explain_the_encoding", "pose_a_question",
    "enumerate", "define_terms", "narrate_an_event", "assert_without_data", "unclassified",
}


def _read(path: Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _source(path: Path) -> dict[str, Any]:
    resolved = Path(path).resolve()
    try:
        stored_path = resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        stored_path = resolved.as_posix()
    return {"path": stored_path, "sha256": _sha(path)}


def _resolve_source(source: dict[str, Any]) -> Path:
    path = Path(source["path"])
    return path if path.is_absolute() else ROOT / path


def _beats() -> list[dict[str, Any]]:
    return [{**beat, "sourceBeatId": f"{passage}-{beat['id']}"} for passage, rows in _read(BEATS).items() for beat in rows]


def prepare() -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "purpose": "Source-bound semantic VisualTask split proposal request",
        "reviewState": "awaiting_model_draft",
        "activationState": "review_only_not_connected",
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "sources": {
            "beats": _source(BEATS),
            "editorReviews": _source(REVIEWS),
            "matchingIssues": _source(ISSUES),
            "matchingPlanDocs": [_source(path) for path in MATCHING_DOCS],
            "prompt": _source(PROMPT),
        },
        "inputContract": "Read every source beat, saved editor review, matching issue, and linked matching-plan section from the bound sources; assess each sourceBeatId exactly once and explicitly reconcile every PI-05 beat.",
    }


def _validate_coverage(full: str, tasks: list[dict[str, Any]], source_id: str) -> None:
    spans = []
    for task in tasks:
        quote = task.get("quote") or ""
        if full.count(quote) != 1:
            raise ValueError(f"task quote must be one exact unique substring: {source_id}")
        start = full.index(quote); spans.append((start, start + len(quote)))
    spans.sort(); cursor = 0
    for start, end in spans:
        if start < cursor or full[cursor:start].strip():
            raise ValueError(f"split tasks overlap or lose source text: {source_id}")
        cursor = end
    if full[cursor:].strip():
        raise ValueError(f"split tasks lose source text: {source_id}")


def validate_draft(draft: dict[str, Any], request: dict[str, Any]) -> dict[str, int]:
    if request.get("reviewState") != "awaiting_model_draft" or draft.get("reviewState") != "model_draft_unreviewed":
        raise ValueError("split proposal review state is invalid")
    if draft.get("activationState") != "review_only_not_connected":
        raise ValueError("split proposals must remain review-only")
    if draft.get("selectionAuthorized") is not False or draft.get("renderingAuthorized") is not False:
        raise ValueError("split proposals cannot authorize selection or rendering")
    if draft.get("requestSha256") != hashlib.sha256(dumps(request).encode()).hexdigest():
        raise ValueError("split proposal request hash mismatch")
    source_records = []
    for value in request["sources"].values():
        source_records.extend(value if isinstance(value, list) else [value])
    for source in source_records:
        path = _resolve_source(source)
        if not path.is_file() or _sha(path) != source["sha256"]:
            raise ValueError(f"split proposal source is missing or stale: {source['path']}")
    by_id = {row["sourceBeatId"]: row for row in _beats()}
    singles = draft.get("keepSingle") or []
    proposals = draft.get("proposals") or []
    existing = draft.get("existingApprovedSplits") or []
    mismatches = draft.get("sourceMismatches") or []
    decided = [row["sourceBeatId"] for row in singles + proposals + existing + mismatches]
    if len(decided) != len(set(decided)) or set(decided) != set(by_id):
        raise ValueError("split proposal must assess every source beat exactly once")
    for row in singles:
        if not row.get("reason"):
            raise ValueError("keep-single decision lacks reason")
    for row in mismatches:
        if not row.get("reason") or not row.get("missingReviewedText"):
            raise ValueError("source mismatch lacks evidence")
    for proposal in proposals:
        source_id = proposal["sourceBeatId"]
        tasks = proposal.get("tasks") or []
        if len(tasks) < 2:
            raise ValueError(f"split proposal needs at least two tasks: {source_id}")
        _validate_coverage(by_id[source_id]["quote"], tasks, source_id)
        for task in tasks:
            if task.get("matchingJob") not in JOBS or not task.get("taskRole") or not task.get("reason"):
                raise ValueError(f"split task lacks job, role, or reason: {source_id}")
        if proposal.get("editorDecision") is not None:
            raise ValueError("model draft cannot invent an editor decision")
    pi05 = {
        "13-13a", "13-13b", "14-14", "21-21b", "23-23", "24-24", "25-25a", "28-28",
    }
    reconciliation = draft.get("issueReconciliation", {}).get("PI-05") or []
    reconciled = [row.get("sourceBeatId") for row in reconciliation]
    if len(reconciled) != len(set(reconciled)) or set(reconciled) != pi05:
        raise ValueError("draft must explicitly reconcile every PI-05 beat exactly once")
    disposition_by_id = {row["sourceBeatId"]: row.get("disposition") for row in reconciliation}
    actual_by_id = {
        **{row["sourceBeatId"]: "keep_single" for row in singles},
        **{row["sourceBeatId"]: "propose_split" for row in proposals},
        **{row["sourceBeatId"]: "existing_approved_split" for row in existing},
        **{row["sourceBeatId"]: "source_mismatch" for row in mismatches},
    }
    for source_id in pi05:
        if disposition_by_id[source_id] != actual_by_id[source_id]:
            raise ValueError(f"PI-05 disposition disagrees with draft decision: {source_id}")
    return {
        "sourceBeats": len(by_id), "keepSingle": len(singles), "proposedSplits": len(proposals),
        "existingApprovedSplits": len(existing), "sourceMismatches": len(mismatches),
        "pi05Reconciled": len(reconciliation),
    }


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "validate"))
    args = parser.parse_args()
    if args.command == "prepare":
        artifact = prepare(); REQUEST.parent.mkdir(parents=True, exist_ok=True); REQUEST.write_text(dumps(artifact), encoding="utf-8"); print(dumps(artifact), end="")
    else:
        print(json.dumps(validate_draft(_read(DRAFT), _read(REQUEST)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
