#!/usr/bin/env python3
"""Audit focused StoryPackage review tasks without changing candidate admission.

The report separates structurally admitted-but-hidden families from catalog
families that were not admitted. It never validates fit, selects a candidate or
authorizes rendering.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from . import visualtask_matching as matching
    from .matching_contract_gate import enforce_contracts
except ImportError:
    import visualtask_matching as matching
    from matching_contract_gate import enforce_contracts


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def build(gallery_path: Path, queue_path: Path) -> dict[str, Any]:
    receipt = enforce_contracts("focused_candidate_diversity.build")
    gallery = _read(gallery_path)
    queue = _read(queue_path)
    if gallery.get("packageId") != queue.get("packageId"):
        raise ValueError("gallery and focused queue package IDs differ")
    if queue.get("selectionAuthorized") is not False or queue.get("renderingAuthorized") is not False:
        raise ValueError("focused queue authorization boundary is invalid")
    for source in gallery.get("sources", {}).values():
        path = Path(source["path"])
        if not path.is_file() or _sha(path) != source["sha256"]:
            raise ValueError("focused gallery source receipt missing or stale")
    try:
        from .storypackage_matching_handoff import build_projection, validate_projection, no_template_reason
    except ImportError:
        from storypackage_matching_handoff import build_projection, validate_projection, no_template_reason
    projection = gallery.get("taskProjection")
    if projection is None:
        if gallery.get("taskProjectionStatus") or any(r.get("projectionVersion") for r in gallery.get("tasks") or []):
            raise ValueError("versioned gallery projection omitted")
        projection = build_projection(
            Path(gallery["sources"]["taskProposals"]["path"]), Path(gallery["sources"]["adapter"]["path"]),
            admissions_path=Path(gallery["sources"]["taskScopedAdmissions"]["path"]) if "taskScopedAdmissions" in gallery["sources"] else None)
        projection_status = "legacy_gallery_centrally_projected_review_only"
    else:
        projection_status = "source_bound_versioned"
    validate_projection(projection)
    projected_by_id = {row["id"]: row for row in projection["tasks"]}
    if projection["packageId"] != gallery["packageId"]:
        raise ValueError("projection/gallery package identity mismatch")
    for label, source in projection["sources"].items():
        if gallery["sources"].get(label, {}).get("sha256") != source["sha256"]:
            raise ValueError("projection/gallery source digest mismatch")

    bindings = _read(Path(gallery["sources"]["bindings"]["path"]))
    shown_by_id = {row["taskId"]: row for row in gallery.get("tasks") or []}
    pool = {row["id"]: row for row in matching.C.load(content_class="*")}
    catalog_families = sorted({matching.C._family(row) for row in pool.values()})

    tasks = []
    exploration_frequency: dict[str, int] = {}
    for task_id in queue.get("taskIds") or []:
        shown = shown_by_id[task_id]
        task = projected_by_id[task_id]
        if gallery.get("taskProjection") is not None and any(shown.get(key) != value for key, value in task.items()):
            raise ValueError("gallery task contract omitted or locally reconstructed")
        exhaustive = matching.template_candidates(task, bindings, pool, exhaustive_families=True)
        admitted_families = [matching.C._family(row["candidateId"]) for row in exhaustive]
        displayed_families = [matching.C._family(row["candidateId"]) for row in shown.get("candidates") or []]
        hidden = [family for family in admitted_families if family not in set(displayed_families)]
        displayed_candidates = shown.get("candidates") or []
        if task["routeDisposition"].get("templateEligible") is False:
            if displayed_candidates:
                raise ValueError("intentional non-template route contains displayed candidates")
            displayed_candidates = []
        primary = displayed_candidates[:8]
        primary_families = {matching.C._family(row["candidateId"]) for row in primary}
        exploration_pool = [row for row in exhaustive
                            if matching.C._family(row["candidateId"]) not in primary_families]
        exploration_pool.sort(key=lambda row: (
            exploration_frequency.get(matching.C._family(row["candidateId"]), 0),
            admitted_families.index(matching.C._family(row["candidateId"])),
        ))
        exploration = exploration_pool[:8]
        for row in exploration:
            family = matching.C._family(row["candidateId"])
            exploration_frequency[family] = exploration_frequency.get(family, 0) + 1
        review_candidates = primary + exploration
        review_families = [matching.C._family(row["candidateId"]) for row in review_candidates]
        if len(review_families) != len(set(review_families)):
            raise ValueError(f"focused review slate repeats a template family: {task_id}")
        tasks.append({
            **task,
            "taskId": task_id,
            "sourceBeatIds": shown.get("sourceBeatIds") or [],
            "presentationOperations": task["presentationOperations"],
            "displayLimit": 16,
            "slideshowLimit": 6,
            "displayedFamilyCount": len(displayed_families),
            "admittedFamilyCount": len(admitted_families),
            "displayedFamilies": displayed_families,
            "hiddenAdmittedFamilies": hidden,
            "focusedReviewCandidates": review_candidates,
            "noTemplateReason": no_template_reason(task, review_candidates),
            "focusedReviewFamilies": review_families,
            "focusedReviewStrategy": "eight_primary_plus_eight_least_exposed_admitted_families",
            "notAdmittedCatalogFamilies": [family for family in catalog_families
                                            if family not in set(admitted_families)],
        })

    return {
        "schemaVersion": 1,
        "packageId": gallery["packageId"],
        "purpose": "focused_candidate_family_diversity_audit",
        "activationState": "review_only_not_connected",
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "fitValidated": False,
        "contractEnforcementReceipt": receipt,
        "taskProjection": projection,
        "taskProjectionStatus": projection_status,
        "sourceGallerySha256": _sha(gallery_path),
        "sourceFocusedQueueSha256": _sha(queue_path),
        "tasks": tasks,
        "counts": {
            "focusedTasks": len(tasks),
            "tasksWithHiddenAdmittedFamilies": sum(bool(row["hiddenAdmittedFamilies"]) for row in tasks),
            "hiddenAdmittedFamilyAppearances": sum(len(row["hiddenAdmittedFamilies"]) for row in tasks),
            "uniqueFamiliesInOriginalFocusedSlates": len({family for row in tasks
                                                          for family in row["displayedFamilies"]}),
            "uniqueFamiliesInBalancedFocusedSlates": len({family for row in tasks
                                                          for family in row["focusedReviewFamilies"]}),
        },
        "boundary": "An admitted family is eligible for editor review only; this report does not establish native fit.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gallery", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.gallery.resolve(), args.queue.resolve())
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
