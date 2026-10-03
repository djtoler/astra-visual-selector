#!/usr/bin/env python3
"""Calculate source-preserving post-render timing plans from approved contracts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT.parent / "ae-template-automation" / "scene-library" / "approved" / "catalog.json"
DEFAULT_REVIEW_CATALOG = ROOT.parent / "ae-template-automation" / "selector-prototype" / "intake" / "review-catalog.json"
DEFAULT_COMPARISON = ROOT / "reports" / "visualtask-ae-spec-comparison.json"
DEFAULT_MAPPINGS = ROOT / "grammar" / "ae-scene-composition-mappings.json"
DEFAULT_WINDOWS = ROOT / "grammar" / "ae-scene-window-definitions.json"
DEFAULT_TECHNICAL_INDEX = ROOT / "grammar" / "ae-template-technical-index.json"
DEFAULT_TIMING_POLICY = ROOT / "plans" / "POST_RENDER_TIMING_FEASIBILITY_PLAN.md"
DEFAULT_REPORT = ROOT / "reports" / "post-render-timing-feasibility.json"


def read(path: Path) -> Any:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def calculate_plan(scene: dict[str, Any], narration_duration: float) -> dict[str, Any]:
    contract = scene.get("selectionContract") or {}
    native = contract.get("nativeDurationSeconds")
    if not isinstance(narration_duration, (int, float)) or narration_duration <= 0:
        return {"status": "unresolved_invalid_narration_duration"}
    if not isinstance(native, (int, float)) or native <= 0:
        return {"status": "unresolved_missing_approved_native_duration"}
    if contract.get("retimeAllowed") is not True:
        return {"status": "unresolved_post_retime_not_approved"}
    if contract.get("transitionBoundaryVerified") is not True:
        return {"status": "unresolved_transition_boundary"}

    rate = native / narration_duration
    output = native / rate
    if contract.get("needsAddedTransition") is True:
        ending = "add_transition"
    elif contract.get("needsAddedTransition") is False:
        ending = "native_boundary"
    else:
        return {"status": "unresolved_transition_requirement"}

    direction = "unchanged"
    if rate > 1.0005:
        direction = "speed_up"
    elif rate < 0.9995:
        direction = "slow_down"
    return {
        "status": "structurally_feasible_editorial_pacing_review_required",
        "method": "post_render_retime",
        "nativeSceneDurationSeconds": round(float(native), 6),
        "narrationDurationSeconds": round(float(narration_duration), 6),
        "playbackRate": round(float(rate), 6),
        "speedPercent": round(float(rate * 100), 3),
        "direction": direction,
        "calculatedOutputDurationSeconds": round(float(output), 6),
        "endingTreatment": ending,
        "preserveNativeRender": True,
        "selectionAuthorized": False,
        "renderingAuthorized": False,
    }


def _unique_by(rows: list[dict[str, Any]], key: str) -> tuple[dict[str, dict[str, Any]], set[str]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row[key]), []).append(row)
    return ({value: matches[0] for value, matches in grouped.items() if len(matches) == 1},
            {value for value, matches in grouped.items() if len(matches) != 1})


def build_reviewed_contract_intake(
    candidate_observations: dict[str, set[float]],
    approved_scene_ids: set[str],
    review_catalog: dict[str, Any],
    mappings: dict[str, Any],
    windows: dict[str, Any],
    technical_index: dict[str, Any],
) -> dict[str, Any]:
    """Build timing-only contracts from exact reviewed/native evidence.

    These records supplement the diagnostic only. They do not promote a review clip
    into the approved catalog or authorize selection/rendering.
    """
    review_scenes, duplicate_reviews = _unique_by(review_catalog.get("scenes", []), "id")
    mapping_rows, duplicate_mappings = _unique_by(mappings.get("mappings", []), "sceneId")
    window_rows, duplicate_windows = _unique_by(windows.get("windows", []), "sceneId")
    projects, duplicate_projects = _unique_by(technical_index.get("projects", []), "id")
    targets = sorted(set(candidate_observations) - approved_scene_ids)
    rows: list[dict[str, Any]] = []
    contracts: dict[str, dict[str, Any]] = {}

    for scene_id in targets:
        reasons: list[str] = []
        if scene_id in duplicate_reviews:
            reasons.append("duplicate_review_scene")
        if scene_id in duplicate_mappings:
            reasons.append("duplicate_native_mapping")
        scene = review_scenes.get(scene_id)
        mapping = mapping_rows.get(scene_id)
        if not scene:
            reasons.append("missing_review_scene")
        if not mapping:
            reasons.append("missing_native_mapping")

        duration: float | None = None
        duration_source: dict[str, Any] | None = None
        project: dict[str, Any] | None = None
        composition: dict[str, Any] | None = None
        if scene:
            if scene.get("availabilityStatus") != "available_for_use":
                reasons.append("review_scene_not_available_for_use")
            if (scene.get("boundaryReview") or {}).get("status") != "usable_scene":
                reasons.append("reviewed_boundary_not_usable")
            if scene.get("transitionReviewNeeded") is not False:
                reasons.append("transition_review_unresolved")
            if not isinstance(scene.get("needsTransition"), bool):
                reasons.append("transition_requirement_missing")

        if mapping:
            if mapping.get("status") not in {"verified", "verified_window"}:
                reasons.append("native_mapping_not_verified")
            project_id = str(mapping.get("projectId"))
            if project_id in duplicate_projects:
                reasons.append("duplicate_technical_project")
            project = projects.get(project_id)
            if not project:
                reasons.append("missing_technical_project")
            elif project.get("sourceUnchanged") is not True or not project.get("sourceProjectSha256"):
                reasons.append("technical_project_not_source_bound")
            else:
                matches = [
                    row for row in project.get("compositions", [])
                    if row.get("id") == mapping.get("compositionId")
                    and row.get("path") == mapping.get("compositionPath")
                ]
                if len(matches) != 1:
                    reasons.append("mapped_composition_not_unique")
                else:
                    composition = matches[0]
                    comp_duration = composition.get("durationSeconds")
                    if not isinstance(comp_duration, (int, float)) or comp_duration <= 0:
                        reasons.append("invalid_native_composition_duration")
                    elif mapping.get("status") == "verified_window":
                        if scene_id in duplicate_windows:
                            reasons.append("duplicate_exact_window")
                        window = window_rows.get(scene_id)
                        if not window:
                            reasons.append("missing_exact_window")
                        elif (window.get("projectId") != mapping.get("projectId")
                              or window.get("compositionId") != mapping.get("compositionId")
                              or window.get("compositionPath") != mapping.get("compositionPath")):
                            reasons.append("window_mapping_mismatch")
                        else:
                            start = window.get("startSeconds")
                            end = window.get("endSeconds")
                            if (not isinstance(start, (int, float)) or not isinstance(end, (int, float))
                                    or start < 0 or end <= start or end > comp_duration + 1e-6):
                                reasons.append("invalid_exact_window")
                            else:
                                duration = float(end - start)
                                duration_source = {
                                    "kind": "verified_native_window",
                                    "startSeconds": start,
                                    "endSeconds": end,
                                }
                    else:
                        duration = float(comp_duration)
                        duration_source = {"kind": "verified_native_composition"}

        observed = sorted(candidate_observations.get(scene_id, set()))
        if duration is not None and (len(observed) != 1 or abs(observed[0] - duration) > 1e-6):
            reasons.append("comparison_native_duration_mismatch")

        if reasons:
            rows.append({"sceneId": scene_id, "status": "unresolved", "reasons": sorted(set(reasons))})
            continue

        assert scene is not None and mapping is not None and project is not None
        assert composition is not None and duration is not None and duration_source is not None
        contract = {
            "version": 1,
            "nativeDurationSeconds": round(duration, 9),
            "retimeAllowed": True,
            "needsAddedTransition": scene["needsTransition"],
            "transitionBoundaryVerified": True,
            "diagnosticOnly": True,
            "selectionAuthorized": False,
            "renderingAuthorized": False,
        }
        contracts[scene_id] = contract
        rows.append({
            "sceneId": scene_id,
            "status": "resolved_source_bound",
            "contract": contract,
            "evidence": {
                "reviewSourceId": scene.get("sourceId"),
                "reviewSourceSha256": scene.get("sourceSha256"),
                "projectId": mapping["projectId"],
                "compositionId": mapping["compositionId"],
                "compositionPath": mapping["compositionPath"],
                "sourceProjectName": project["sourceProjectName"],
                "sourceProjectSha256": project["sourceProjectSha256"],
                "duration": duration_source,
                "comparisonNativeDurationSeconds": observed[0],
            },
        })

    return {
        "activationState": "timing_diagnostic_only",
        "counts": {
            "targetUniqueScenes": len(targets),
            "resolved": len(contracts),
            "unresolved": len(targets) - len(contracts),
        },
        "rows": rows,
        "contracts": contracts,
        "selectionAuthorized": False,
        "renderingAuthorized": False,
    }


def build_report(
    catalog: dict[str, Any],
    comparison: dict[str, Any],
    *,
    catalog_path: Path,
    comparison_path: Path,
    review_catalog: dict[str, Any] | None = None,
    mappings: dict[str, Any] | None = None,
    windows: dict[str, Any] | None = None,
    technical_index: dict[str, Any] | None = None,
    evidence_paths: dict[str, Path] | None = None,
) -> dict[str, Any]:
    scenes = {
        scene["id"]: scene
        for template in catalog["afterEffects"]
        for scene in template["scenes"]
    }
    candidate_observations: dict[str, set[float]] = {}
    for task in comparison["tasks"]:
        for candidate in task.get("candidateComparisons", []):
            timing = candidate.get("timingObservation")
            if timing:
                candidate_observations.setdefault(candidate["candidateId"], set()).add(
                    float(timing["nativeCompositionDurationSeconds"])
                )
    intake = build_reviewed_contract_intake(
        candidate_observations,
        set(scenes),
        review_catalog or {"scenes": []},
        mappings or {"mappings": []},
        windows or {"windows": []},
        technical_index or {"projects": []},
    )
    reviewed_contracts = intake.pop("contracts")
    rows = []
    for task in comparison["tasks"]:
        for candidate in task.get("candidateComparisons", []):
            timing = candidate.get("timingObservation")
            if not timing:
                continue
            candidate_id = candidate["candidateId"]
            scene = scenes.get(candidate_id)
            if not scene and candidate_id in reviewed_contracts:
                scene = {"selectionContract": reviewed_contracts[candidate_id]}
            plan = (
                calculate_plan(scene, timing["taskAudioDurationSeconds"])
                if scene else {"status": "unresolved_missing_native_duration_contract"}
            )
            rows.append({
                "taskId": task["taskId"],
                "candidateId": candidate_id,
                "plan": plan,
            })
    counts: dict[str, int] = {}
    for row in rows:
        status = row["plan"]["status"]
        counts[status] = counts.get(status, 0) + 1
    sources = {
        "approvedCatalog": {"path": str(catalog_path.resolve()), "sha256": sha256(catalog_path)},
        "visualTaskComparison": {"path": str(comparison_path.resolve()), "sha256": sha256(comparison_path)},
    }
    for key, path in (evidence_paths or {}).items():
        sources[key] = {"path": str(path.resolve()), "sha256": sha256(path)}
    return {
        "schemaVersion": 2,
        "purpose": "Post-render narration-duration and ending-boundary diagnostic.",
        "activationState": "diagnostic_only",
        "sources": sources,
        "reviewedNativeDurationContractIntake": intake,
        "counts": {"evaluated": len(rows), "byStatus": counts},
        "plans": rows,
        "selectionAuthorized": False,
        "renderingAuthorized": False,
    }


def add_selected_route_plans(
    report: dict[str, Any],
    route_plan: dict[str, Any],
    route_decisions: dict[str, Any],
    catalog: dict[str, Any],
    local_templates: dict[str, Any],
    local_timing_confirmations: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Add timing dispositions for locked routes not covered by the AE comparison.

    Static established renderers use a narration-length hold. Approved cinematic
    scenes use their catalog duration with the existing post-retime calculation.
    Local AE scenes without a source-bound duration remain explicitly unresolved.
    """
    existing = {(row["taskId"], row["candidateId"]) for row in report.get("plans") or []}
    local_confirmation_by_pair = {
        (row["taskId"], row["sceneId"]): row
        for row in (local_timing_confirmations or {}).get("confirmations") or []
    }
    decisions = route_decisions.get("decisions") or {}
    source_index: dict[str, dict[str, Any]] = {}
    for family in catalog.get("afterEffects") or []:
        for scene in family.get("scenes") or []:
            source_index[scene["id"]] = {"kind": "after_effects", "record": scene}
    for record in catalog.get("infographics") or []:
        source_index[record["template_id"]] = {"kind": "infographic", "record": record}
    for record in catalog.get("cinematic3d") or []:
        source_index[record["layout_id"]] = {"kind": "cinematic_3d", "record": record}
    for record in catalog.get("layeredScenes") or []:
        source_index[record["template_id"]] = {"kind": "layered_scene", "record": record}
    for record in local_templates.get("records") or []:
        source_index.setdefault(record["id"], {"kind": "after_effects_local", "record": record})

    added = []
    for scene in route_plan.get("scenes") or []:
        if scene.get("route") != "template_review":
            continue
        decision = decisions.get(scene["taskId"])
        if not decision or decision.get("route") != "template":
            continue
        candidate_id = decision.get("candidateId")
        pair = (scene["taskId"], candidate_id)
        if pair in existing:
            continue
        narration = scene["narrationSpan"]["durationSeconds"]
        source = source_index.get(candidate_id)
        if not source:
            plan = {
                "status": "unresolved_unknown_selected_source_type",
                "method": "pending_source_classification",
                "narrationDurationSeconds": narration,
                "endingTreatment": "add_transition",
                "sourceType": "unknown",
                "selectionAuthorized": False,
                "renderingAuthorized": False,
            }
            source_kind = "unknown"
        elif source["kind"] in {"infographic", "layered_scene"}:
            source_kind = source["kind"]
            plan = {
                "status": "structurally_feasible_static_hold",
                "method": "hold_static_render_to_narration_span",
                "narrationDurationSeconds": round(float(narration), 6),
                "calculatedOutputDurationSeconds": round(float(narration), 6),
                "endingTreatment": "add_transition",
                "preserveNativeRender": True,
                "sourceType": source_kind,
                "selectionAuthorized": False,
                "renderingAuthorized": False,
            }
        elif source["kind"] == "cinematic_3d":
            source_kind = source["kind"]
            duration = source["record"].get("native_duration_seconds")
            plan = calculate_plan({"selectionContract": {
                "nativeDurationSeconds": duration,
                "retimeAllowed": True,
                "transitionBoundaryVerified": True,
                "needsAddedTransition": True,
            }}, narration)
            plan.update({
                "sourceType": source_kind,
                "durationEvidence": "approved_catalog_native_duration_seconds",
            })
        elif source["kind"] == "after_effects":
            source_kind = source["kind"]
            plan = calculate_plan(source["record"], narration)
            plan["sourceType"] = source_kind
        elif source["kind"] == "after_effects_local":
            source_kind = source["kind"]
            confirmation = local_confirmation_by_pair.get(pair) or {}
            full_duration = confirmation.get("nativeDurationSeconds")
            active_window = confirmation.get("activeMotionWindow") or {}
            active_duration = active_window.get("durationSecondsApprox")
            duration = active_duration if (
                active_window.get("status") == "editor_observed_approximate"
                and active_window.get("postWindowBehavior") == "still_hold"
                and isinstance(active_duration, (int, float)) and active_duration > 0
            ) else full_duration
            confirmed = (
                confirmation.get("keepSelected") is True
                and confirmation.get("timingMappingStillRequired") is False
                and confirmation.get("timingDisposition") == "native_mapping_editor_confirmed"
                and confirmation.get("nativeComparisonResult") == "preview_and_native_output_match"
                and isinstance(duration, (int, float)) and duration > 0
            )
            if confirmed:
                plan = calculate_plan({"selectionContract": {
                    "nativeDurationSeconds": duration,
                    "retimeAllowed": True,
                    "transitionBoundaryVerified": True,
                    "needsAddedTransition": True,
                }}, narration)
                plan.update({
                    "sourceType": source_kind,
                    "durationEvidence": (
                        "editor_observed_approximate_active_motion_window"
                        if duration == active_duration
                        else "editor_confirmed_original_aep_native_comparison"
                    ),
                    "nativeComposition": confirmation.get("nativeComposition"),
                    "fullNativeCompositionDurationSeconds": full_duration,
                    "activeMotionWindow": active_window or None,
                })
            else:
                plan = {
                    "status": "unresolved_missing_approved_native_duration",
                    "method": "pending_source_bound_native_duration_contract",
                    "narrationDurationSeconds": round(float(narration), 6),
                    "endingTreatment": "add_transition",
                    "sourceType": source_kind,
                    "selectionAuthorized": False,
                    "renderingAuthorized": False,
                }
        else:
            raise ValueError(f"Unknown selected source kind: {source['kind']}")
        added.append({
            "taskId": scene["taskId"],
            "candidateId": candidate_id,
            "plan": plan,
            "routePlanSource": "locked_ordered_visual_route",
        })
        existing.add(pair)

    report["plans"].extend(added)
    counts: dict[str, int] = {}
    for row in report["plans"]:
        status = row["plan"]["status"]
        counts[status] = counts.get(status, 0) + 1
    report["counts"] = {"evaluated": len(report["plans"]), "byStatus": counts}
    report["selectedRouteTiming"] = {
        "addedPlans": len(added),
        "bySourceType": {
            kind: sum(row["plan"].get("sourceType") == kind for row in added)
            for kind in sorted({row["plan"].get("sourceType", "unknown") for row in added})
        },
        "selectionAuthorized": False,
        "renderingAuthorized": False,
    }
    return report


def main() -> None:
    catalog = read(DEFAULT_CATALOG)
    report = build_report(
        catalog,
        read(DEFAULT_COMPARISON),
        catalog_path=DEFAULT_CATALOG,
        comparison_path=DEFAULT_COMPARISON,
        review_catalog=read(DEFAULT_REVIEW_CATALOG),
        mappings=read(DEFAULT_MAPPINGS),
        windows=read(DEFAULT_WINDOWS),
        technical_index=read(DEFAULT_TECHNICAL_INDEX),
        evidence_paths={
            "reviewCatalog": DEFAULT_REVIEW_CATALOG,
            "sceneCompositionMappings": DEFAULT_MAPPINGS,
            "sceneWindowDefinitions": DEFAULT_WINDOWS,
            "technicalIndex": DEFAULT_TECHNICAL_INDEX,
            "timingPolicy": DEFAULT_TIMING_POLICY,
        },
    )
    DEFAULT_REPORT.write_text(dumps(report))
    print(dumps(report["counts"]), end="")


if __name__ == "__main__":
    main()
