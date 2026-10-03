#!/usr/bin/env python3
"""Build a fail-closed render-release preparation packet from locked matching outputs."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .matching_contract_gate import enforce_contracts
except ImportError:
    from matching_contract_gate import enforce_contracts

from pipeline.post_render_timing import add_selected_route_plans

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STORY = ROOT / "reports" / "storypackage-02-year-seventeen-matching-handoff.json"
DEFAULT_PLAN = ROOT / "reports" / "ordered-visual-route-plan.json"
DEFAULT_DECISIONS = ROOT / "reports" / "ordered-visual-route-decisions.json"
DEFAULT_DATA = ROOT / "reports" / "storypackage-02-data-assignments.json"
DEFAULT_BATCH = ROOT / "reports" / "full-visualtask-batch-matching-current.json"
DEFAULT_LIBRARY = ROOT / "grammar" / "library-snapshot.json"
DEFAULT_TIMING = ROOT / "reports" / "post-render-timing-feasibility.json"
DEFAULT_CATALOG = ROOT.parent / "ae-template-automation" / "scene-library" / "approved" / "catalog.json"
DEFAULT_LOCAL_TEMPLATES = ROOT / "grammar" / "local-templates.json"
DEFAULT_TIMING_CONFIRMATIONS = ROOT / "grammar" / "selected-local-ae-timing-confirmations.json"
DEFAULT_OUTPUT = ROOT / "reports" / "render-release-preparation.json"


def read(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source(path: Path) -> dict[str, str]:
    resolved = path.resolve()
    try:
        recorded = resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        recorded = resolved.as_posix()
    return {"path": recorded, "sha256": sha(path)}


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _candidate_assets(media: dict[str, Any], library: dict[str, Any]) -> list[dict[str, Any]]:
    delivery = {
        row["asset_id"]: row["delivery_path"]
        for rows in (library.get("delivery", {}).get("categories") or {}).values()
        for row in rows
    }
    ids = list(media.get("groupCandidateIds") or [])
    for entity_ids in (media.get("individualCandidateIds") or {}).values():
        ids.extend(entity_ids)
    ids.extend(media.get("sourceSpecificCandidateIds") or [])
    result = []
    for asset_id in dict.fromkeys(ids):
        item = library.get("assets", {}).get(asset_id) or {}
        result.append({
            "assetId": asset_id,
            "deliveryPath": delivery.get(asset_id),
            "mediaType": item.get("media_type"),
            "durationSeconds": item.get("duration"),
            "productionReady": bool(delivery.get(asset_id)),
            "useRightsStatus": "unrecorded",
        })
    return result


def _proposed_asset_ids(media: dict[str, Any]) -> list[str]:
    """Carry the existing resolver's deterministic first choices as proposals only."""
    groups = media.get("groupCandidateIds") or []
    if groups:
        return [groups[0]]
    return [ids[0] for ids in (media.get("individualCandidateIds") or {}).values() if ids]


def build(*, story_path: Path = DEFAULT_STORY, plan_path: Path = DEFAULT_PLAN,
          decisions_path: Path = DEFAULT_DECISIONS, data_path: Path = DEFAULT_DATA,
          batch_path: Path = DEFAULT_BATCH, library_path: Path = DEFAULT_LIBRARY,
          timing_path: Path = DEFAULT_TIMING, catalog_path: Path = DEFAULT_CATALOG,
          local_templates_path: Path = DEFAULT_LOCAL_TEMPLATES,
          timing_confirmations_path: Path = DEFAULT_TIMING_CONFIRMATIONS) -> dict[str, Any]:
    contract_receipt = enforce_contracts("render_release_preparation.build")
    story, plan, decisions, data, batch, library, timing, catalog, local_templates, timing_confirmations = [
        read(path) for path in (story_path, plan_path, decisions_path, data_path,
                                batch_path, library_path, timing_path, catalog_path,
                                local_templates_path, timing_confirmations_path)
    ]
    timing = add_selected_route_plans(
        copy.deepcopy(timing), plan, decisions, catalog, local_templates,
        timing_confirmations,
    )
    batch_by_task = {row["taskId"]: row for row in batch.get("tasks") or []}
    data_by_task = {row["taskId"]: row for row in data.get("assignments") or []}
    timing_by_pair = {(row["taskId"], row["candidateId"]): row["plan"] for row in timing.get("plans") or []}
    decision_by_task = decisions.get("decisions") or {}
    timing_dispositions = {
        (row["taskId"], row["sceneId"]): row.get("timingDisposition")
        for row in timing_confirmations.get("confirmations") or []
    }
    rows = []
    blocker_counts: Counter[str] = Counter()

    for scene in plan.get("scenes") or []:
        task_id = scene["taskId"]
        match = batch_by_task[task_id]
        media = match.get("mediaResult") or {}
        candidates = _candidate_assets(media, library)
        proposed_asset_ids = _proposed_asset_ids(media)
        blockers: list[dict[str, Any]] = []
        route = scene["route"]
        selected_template = None
        timing_plan = None

        if route == "template_review":
            decision = decision_by_task.get(task_id)
            if not decision:
                blockers.append({"kind": "template_selection_missing", "owner": "editor"})
            else:
                selected_template = decision["candidateId"]
                selected = next((row for row in scene.get("templateChoices") or []
                                 if row.get("candidateId") == selected_template), None)
                if not selected:
                    blockers.append({"kind": "selected_template_not_in_locked_route_slate", "owner": "matching"})
                else:
                    for gap in selected.get("validationGaps") or []:
                        blockers.append({"kind": gap["type"], "owner": "render_release",
                                         "reason": gap.get("reason")})
                timing_plan = timing_by_pair.get((task_id, selected_template))
                if not timing_plan:
                    blockers.append({"kind": "selected_template_timing_plan_missing", "owner": "render_release"})
                elif str(timing_plan.get("status", "")).startswith("unresolved_"):
                    disposition = timing_dispositions.get((task_id, selected_template))
                    if disposition == "deferred_until_use_missing_source_project":
                        blockers.append({
                            "kind": "selected_template_timing_deferred_until_use",
                            "owner": "render_release",
                            "reason": "source_project_missing",
                            "note": "Selection is preserved; restore and validate the native source before production render.",
                        })
                    else:
                        blockers.append({
                            "kind": "selected_template_timing_unresolved",
                            "owner": "render_release",
                            "reason": timing_plan.get("status"),
                        })
        elif route == "broll":
            blockers.append({
                "kind": "exact_broll_asset_binding_pending",
                "owner": "render_release",
                "candidateCount": len(candidates),
                "preferredMediaVerdict": media.get("availabilityVerdict"),
                "note": "General b-roll fallback is valid; bind a production-ready asset before release.",
            })
        else:
            blockers.append({
                "kind": "editorial_route_deferred",
                "owner": "matching",
                "reason": scene.get("routeReason"),
                "note": "The editor ruled out b-roll; release waits for a compliant existing-template route.",
            })

        supplemental_broll = None
        if scene.get("postBeatBroll", {}).get("required"):
            supplemental_broll = {
                **scene["postBeatBroll"],
                "proposedAssetIds": proposed_asset_ids,
                "candidateAssets": candidates,
                "boundAssetIds": [],
            }
            blockers.append({
                "kind": "exact_post_beat_broll_asset_binding_pending",
                "owner": "render_release",
                "candidateCount": len(candidates),
            })

        if media.get("availabilityVerdict") not in {"not_required", None}:
            blockers.append({"kind": "asset_use_rights_receipt_missing", "owner": "render_release"})

        blockers.append({"kind": "full_export_human_qc_pending", "owner": "editor",
                         "note": "This receipt can only exist after a full export."})
        for blocker in blockers:
            blocker_counts[blocker["kind"]] += 1

        rows.append({
            "sequenceIndex": scene["sequenceIndex"],
            "taskId": task_id,
            "sourceBeatId": scene["sourceBeatId"],
            "quote": scene["quote"],
            "route": {"template_review": "template", "broll": "broll"}.get(route, "deferred"),
            "selectedTemplateId": selected_template,
            "narrationSpan": scene["narrationSpan"],
            "timingPlan": timing_plan or {
                "method": "edit_to_narration_span" if route == "broll" else "pending",
                "targetDurationSeconds": scene["narrationSpan"]["durationSeconds"],
                "renderingAuthorized": False,
            },
            "transition": scene["transition"],
            "typedData": data_by_task.get(task_id),
            "mediaRequirement": {
                "availabilityVerdict": media.get("availabilityVerdict"),
                "requiredKinds": media.get("candidateMatchingProvenance", {}).get("requiredMediaKinds") or [],
                "entities": media.get("entities") or [],
                "gaps": media.get("gaps") or [],
            },
            "candidateAssets": candidates,
            "proposedAssetIds": proposed_asset_ids,
            "assetProposalStatus": ("system_proposed_pending_editor" if proposed_asset_ids
                                    else "sourcing_required"),
            "boundAssetIds": [],
            "supplementalBroll": supplemental_broll,
            "blockers": blockers,
            "releaseReady": not blockers,
            "renderingAuthorized": False,
        })

    return {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": 1,
        "packetId": "year-seventeen-render-release-preparation",
        "purpose": "Fail-closed binding and receipt inventory between matching and render release",
        "sources": {name: source(path) for name, path in {
            "storyHandoff": story_path, "orderedVisualPlan": plan_path,
            "routeDecisions": decisions_path, "dataAssignments": data_path,
            "batchMatching": batch_path, "mediaLibrarySnapshot": library_path,
            "timingPlans": timing_path, "approvedCatalog": catalog_path,
            "localTemplates": local_templates_path,
            "timingConfirmations": timing_confirmations_path,
        }.items()},
        "lockedInputs": {
            "storyPackageId": story.get("packageId"),
            "visualPlanId": plan.get("planId"),
            "visualPlanSha256": sha(plan_path),
            "routeDecisionsSha256": sha(decisions_path),
        },
        "counts": {
            "scenes": len(rows),
            "templateRoutes": sum(row["route"] == "template" for row in rows),
            "brollRoutes": sum(row["route"] == "broll" for row in rows),
            "deferredRoutes": sum(row["route"] == "deferred" for row in rows),
            "postBeatBrollSegments": sum(bool(row.get("supplementalBroll")) for row in rows),
            "releaseReady": sum(row["releaseReady"] for row in rows),
            "blocked": sum(not row["releaseReady"] for row in rows),
            "routesWithSystemAssetProposal": sum(bool(row["proposedAssetIds"]) for row in rows),
            "routesNeedingAssetSourcing": sum(row["route"] == "broll" and not row["proposedAssetIds"]
                                               for row in rows),
            "blockersByKind": dict(sorted(blocker_counts.items())),
        },
        "scenes": rows,
        "requiredReceipts": {
            "lockedScript": True,
            "lockedVisualPlan": True,
            "assetUseRights": False,
            "renderGate": False,
            "fullExportHumanQc": False,
        },
        "releaseReady": all(row["releaseReady"] for row in rows),
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "publishAuthorized": False,
    }


def validate(packet: dict[str, Any], *, verify_sources: bool = True) -> dict[str, Any]:
    scenes = packet.get("scenes") or []
    if len(scenes) != 41 or len({row.get("taskId") for row in scenes}) != 41:
        raise ValueError("render-release packet does not cover every scene exactly once")
    if [row.get("sequenceIndex") for row in scenes] != list(range(1, 42)):
        raise ValueError("render-release scene order is invalid")
    if any(not row.get("transition", {}).get("required") for row in scenes):
        raise ValueError("a required scene transition is missing")
    if packet.get("renderingAuthorized") is not False or packet.get("publishAuthorized") is not False:
        raise ValueError("preparation packet cannot authorize rendering or publishing")
    if verify_sources:
        for item in packet.get("sources", {}).values():
            path = Path(item["path"])
            if not path.is_absolute():
                path = ROOT / path
            if not path.is_file() or sha(path) != item["sha256"]:
                raise ValueError("render-release input is missing or stale")
    return {"scenes": len(scenes), "blocked": packet["counts"]["blocked"],
            "releaseReady": packet["releaseReady"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "validate"))
    args = parser.parse_args()
    if args.command == "build":
        packet = build()
        DEFAULT_OUTPUT.write_text(dumps(packet))
        print(json.dumps(validate(packet, verify_sources=False), sort_keys=True))
    else:
        print(json.dumps(validate(read(DEFAULT_OUTPUT)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
