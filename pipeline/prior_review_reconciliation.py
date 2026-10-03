#!/usr/bin/env python3
"""Reconcile prior editor template decisions with current VisualTask candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REVIEW = ROOT / "grammar" / "beat-review-export-2026-09-27.json"
DEFAULT_COMPARISON = ROOT / "reports" / "visualtask-ae-spec-comparison.json"
DEFAULT_OUTPUT = ROOT / "reports" / "prior-editor-review-reconciliation.json"


def read(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def source(path: Path) -> dict[str, Any]:
    resolved = Path(path).resolve()
    try:
        logical = resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        logical = str(resolved)
    return {"path": logical, "sha256": sha(path)}


def _review_rows(raw: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = (((raw.get("grammar") or {}).get("templatePicks") or {}).get("beats") or {})
    if not isinstance(rows, dict):
        raise ValueError("review export lacks template-pick beats")
    out = {}
    for beat, row in rows.items():
        if row.get("reviewed") is not True:
            continue
        shown = row.get("shown") or []
        selected = row.get("selected") or []
        if len(shown) != len(set(shown)) or len(selected) != len(set(selected)):
            raise ValueError(f"duplicate prior review candidate: {beat}")
        if not set(selected).issubset(shown):
            raise ValueError(f"prior selection was not shown: {beat}")
        out[beat] = row
    return out


def build(*, review_path: Path = DEFAULT_REVIEW, comparison_path: Path = DEFAULT_COMPARISON) -> dict[str, Any]:
    review = _review_rows(read(review_path))
    comparison = read(comparison_path)
    task_counts = Counter(row["sourceBeatId"] for row in comparison.get("tasks") or [])
    rows = []
    attention = []
    present_source_candidates: set[tuple[str, str]] = set()
    for task in comparison.get("tasks") or []:
        beat = task["sourceBeatId"]
        prior = review.get(beat)
        if prior is None:
            raise ValueError(f"current task lacks prior beat review: {beat}")
        selected = set(prior.get("selected") or [])
        shown = set(prior.get("shown") or [])
        split = task_counts[beat] > 1
        for candidate in task.get("candidateComparisons") or []:
            candidate_id = candidate["candidateId"]
            present_source_candidates.add((beat, candidate_id))
            if candidate_id in selected:
                source_disposition = "selected"
            elif candidate_id in shown:
                source_disposition = "none_acceptable" if prior.get("noneAcceptable") is True else "dismissed"
            else:
                source_disposition = "not_previously_shown"
            if split:
                state = "split_task_requires_independent_review"
            elif source_disposition == "selected":
                state = "prior_selected"
            elif source_disposition == "dismissed":
                state = "prior_dismissed"
            elif source_disposition == "none_acceptable":
                state = "prior_none_acceptable"
            else:
                state = "not_previously_shown"
            technical = candidate.get("technicalEvidenceVerdict") or candidate.get("verdict")
            system_resolution_required = technical in {"technical_spec_unmapped", "technical_spec_unreviewed"}
            conflict = technical in {"technical_capacity_incompatible", "verified_incompatible"}
            row = {
                "taskId": task["taskId"], "sourceBeatId": beat, "candidateId": candidate_id,
                "state": state, "sourceDisposition": source_disposition,
                "technicalEvidenceVerdict": technical,
                "compositionMappingStatus": candidate.get("compositionMappingStatus"),
                "systemResolutionRequired": system_resolution_required,
                "concreteTechnicalConflict": conflict,
            }
            rows.append(row)
            if split or (state == "prior_selected" and conflict):
                attention.append({
                    "taskId": task["taskId"], "sourceBeatId": beat, "candidateId": candidate_id,
                    "reason": "split_task_requires_independent_review" if split else technical,
                })
    all_prior_selected = {
        (beat, candidate_id)
        for beat, row in review.items()
        for candidate_id in (row.get("selected") or [])
    }
    absent = [
        {"sourceBeatId": beat, "candidateId": candidate_id, "reason": "prior_selection_absent_from_current_comparison"}
        for beat, candidate_id in sorted(all_prior_selected - present_source_candidates)
    ]
    system_resolution = [
        {"taskId": row["taskId"], "sourceBeatId": row["sourceBeatId"], "candidateId": row["candidateId"], "reason": row["technicalEvidenceVerdict"]}
        for row in rows
        if row["state"] == "prior_selected" and row["systemResolutionRequired"]
    ] + absent
    counts = Counter(row["state"] for row in rows)
    return {
        "schemaVersion": 1,
        "purpose": "Prevent duplicate editorial review and preserve prior template decisions in universal matching",
        "activationState": "review_only_not_connected",
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "sources": {"priorReview": source(review_path), "comparison": source(comparison_path)},
        "reviewedBeatCount": len(review),
        "priorSelectedOptionCount": sum(len(row.get("selected") or []) for row in review.values()),
        "priorNoneAcceptableBeatCount": sum(row.get("noneAcceptable") is True for row in review.values()),
        "priorSelectionCoverage": {
            "total": len(all_prior_selected),
            "presentInCurrentComparison": len(all_prior_selected & present_source_candidates),
            "absentFromCurrentComparison": len(absent),
        },
        "counts": dict(sorted(counts.items())),
        "rows": rows,
        "systemResolutionQueue": system_resolution,
        "humanAttentionQueue": attention,
    }


def validate(artifact: dict[str, Any], *, verify_sources: bool = True) -> dict[str, Any]:
    if artifact.get("selectionAuthorized") is not False or artifact.get("renderingAuthorized") is not False:
        raise ValueError("reconciliation cannot authorize selection or rendering")
    rows = artifact.get("rows") or []
    keys = [(r.get("taskId"), r.get("candidateId")) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate reconciled task/candidate")
    if any(r.get("state") == "prior_dismissed" and r.get("sourceDisposition") != "dismissed" for r in rows):
        raise ValueError("dismissed state lacks prior evidence")
    if verify_sources:
        for item in (artifact.get("sources") or {}).values():
            path = Path(item["path"])
            if not path.is_absolute():
                path = ROOT / path
            if not path.is_file() or sha(path) != item["sha256"]:
                raise ValueError("reconciliation source is missing or stale")
        review_path = Path(artifact["sources"]["priorReview"]["path"])
        comparison_path = Path(artifact["sources"]["comparison"]["path"])
        replay = build(
            review_path=review_path if review_path.is_absolute() else ROOT / review_path,
            comparison_path=comparison_path if comparison_path.is_absolute() else ROOT / comparison_path,
        )
        if dumps(replay) != dumps(artifact):
            raise ValueError("reconciliation does not replay")
    return {"rows": len(rows), "attention": len(artifact.get("humanAttentionQueue") or [])}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "validate"))
    parser.add_argument("artifact", type=Path, nargs="?", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.command == "build":
        artifact = build()
        args.artifact.parent.mkdir(parents=True, exist_ok=True)
        args.artifact.write_text(dumps(artifact))
        print(json.dumps(validate(artifact, verify_sources=False), sort_keys=True))
    else:
        print(json.dumps(validate(read(args.artifact)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
