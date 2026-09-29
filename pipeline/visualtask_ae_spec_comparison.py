#!/usr/bin/env python3
"""Build a read-only VisualTask versus measured AE-capacity comparison.

The comparison attaches technical evidence to the existing semantic slate. It
does not alter, rank, approve, select, pair, or render any candidate.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS = ROOT / "grammar" / "visual-tasks.json"
DEFAULT_SLATE = ROOT / "pipeline" / "shotlist.capacity.json"
DEFAULT_CATALOG = ROOT / "astra-selector-design" / "approved_media" / "approved-list.json"
DEFAULT_LINKS = ROOT / "grammar" / "ae-template-spec-links.json"
DEFAULT_INDEX = ROOT / "grammar" / "ae-template-technical-index.json"
DEFAULT_SCENE_MAPPINGS = ROOT / "grammar" / "ae-scene-composition-mappings.json"
DEFAULT_WINDOW_CAPACITIES = ROOT / "grammar" / "ae-scene-window-technical-capacities.json"
DEFAULT_TASK_REQUIREMENTS = ROOT / "grammar" / "visual-task-technical-requirements.json"
DEFAULT_OUTPUT = ROOT / "reports" / "visualtask-ae-spec-comparison.json"
DEFAULT_BASELINE_ENTITIES = ROOT / "grammar" / "beat-entities.json"
PROTECTED_LIVE_ARTIFACTS = (
    ROOT / "grammar" / "bindings.json",
    ROOT / "grammar" / "media-picks.json",
    ROOT / "grammar" / "pairings.json",
    DEFAULT_SLATE,
)

MISSING_FOR_FILLABLE_NOW = [
    "exact_scene_to_native_composition_mapping",
    "task_required_data_fields",
    "task_required_media_slot_count",
    "media_kind_constraints",
    "single_person_group_eligibility",
    "treatment_required_text_fields",
    "text_character_and_line_limits",
    "exact_task_audio_span",
    "duration_adjustment_policy_and_timing_fit",
    "media_asset_availability",
]


def _read(path: Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _logical(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return Path(path).name


def _source(path: Path) -> dict[str, Any]:
    return {"path": _logical(path), "sha256": _sha(path), "bytes": Path(path).stat().st_size}


def _int(value: str | int | None) -> int:
    return int(value or 0)


def _float(value: str | float | None) -> float:
    return float(value or 0)


def _bool(value: str | bool | None) -> bool:
    return value is True or str(value).lower() == "true"


def import_technical_index(summary_path: Path, compositions_path: Path, text_fields_path: Path) -> dict[str, Any]:
    """Create a portable exact-data snapshot from the frozen master reports."""
    summary_path = Path(summary_path)
    compositions_path = Path(compositions_path)
    text_fields_path = Path(text_fields_path)
    summary = _read(summary_path)
    project_rows = summary.get("projects") or []
    projects: dict[str, dict[str, Any]] = {}
    capacity_details: dict[str, dict[int, dict[str, Any]]] = {}
    for row in project_rows:
        project_id = row["id"]
        if project_id in projects:
            raise ValueError(f"duplicate measured project id: {project_id}")
        source_project = Path(row["sourceProject"])
        capacity_path = Path(row["capacityFile"])
        if not capacity_path.is_file():
            raise ValueError(f"measured capacity report is missing: {project_id}")
        capacity_report = _read(capacity_path)
        if capacity_report.get("sourceSha256") != row["expectedSourceSha256"]:
            raise ValueError(f"capacity report source hash mismatch: {project_id}")
        capacity_details[project_id] = {
            int(comp["compositionId"]): comp for comp in capacity_report.get("compositions") or []
        }
        projects[project_id] = {
            "id": project_id,
            "batchId": row["batchId"],
            "resultStatus": row["resultStatus"],
            "evidenceStatus": row["evidenceStatus"],
            "sourceProjectName": source_project.name,
            "sourceProjectSha256": row["expectedSourceSha256"],
            "sourceUnchanged": bool(row["sourceUnchanged"]),
            "capacityReport": _source(capacity_path),
            "projectSummary": row.get("projectSummary") or {},
            "reportedCompositionCount": int(row["compositionCount"]),
            "compositions": [],
            "textFields": [],
        }

    with compositions_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            project_id = row["project_id"]
            if project_id not in projects:
                raise ValueError(f"composition references unknown measured project: {project_id}")
            composition_id = _int(row["composition_id"])
            detail = capacity_details[project_id].get(composition_id)
            if not detail or detail.get("compositionPath") != row["composition_path"]:
                raise ValueError(f"capacity detail mismatch: {project_id}:{composition_id}")
            projects[project_id]["compositions"].append({
                "id": composition_id,
                "path": row["composition_path"],
                "width": _int(row["width"]),
                "height": _int(row["height"]),
                "durationSeconds": _float(row["duration_seconds"]),
                "frameRate": _float(row["frame_rate"]),
                "frameCount": _int(row["frame_count"]),
                "workAreaStartSeconds": _float(row["work_area_start_seconds"]),
                "workAreaDurationSeconds": _float(row["work_area_duration_seconds"]),
                "workAreaFrameCount": _int(row["work_area_frame_count"]),
                "directEditableTextFields": _int(row["direct_editable_text_fields"]),
                "recursiveEditableTextFields": _int(row["recursive_editable_text_fields"]),
                "maxSimultaneouslyEnabledRecursiveTextFields": _int(row["max_simultaneously_enabled_recursive_text_fields"]),
                "directVisualMediaInputs": _int(row["direct_visual_media_inputs"]),
                "totalIndependentVisualMediaInputs": _int(row["total_independent_visual_media_inputs"]),
                "maxSimultaneouslyEnabledDirectInputs": _int(row["max_simultaneously_enabled_direct_inputs"]),
                "maxSimultaneouslyEnabledRecursiveVisualInputs": _int(row["max_simultaneously_enabled_recursive_visual_inputs"]),
                "unresolvedCount": _int(row["unresolved_count"]),
                "recursiveTextFieldIds": [field["id"] for field in detail["recursiveEditableTextFields"]],
                "recursiveVisualMediaInputs": [
                    {
                        "id": media["id"],
                        "kind": media["kind"],
                        "path": media.get("path"),
                        "evidence": media.get("evidence"),
                    }
                    for media in detail["recursiveVisualMediaInputs"]
                ],
            })

    with text_fields_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            project_id = row["project_id"]
            if project_id not in projects:
                raise ValueError(f"text field references unknown measured project: {project_id}")
            projects[project_id]["textFields"].append({
                "id": f"text:{_int(row['composition_id'])}:{_int(row['layer_index'])}",
                "compositionId": _int(row["composition_id"]),
                "compositionPath": row["composition_path"],
                "layerIndex": _int(row["layer_index"]),
                "layerName": row["layer_name"],
                "enabled": _bool(row["enabled"]),
                "inPoint": _float(row["in_point"]),
                "outPoint": _float(row["out_point"]),
                "textKind": row["text_kind"] or None,
                "font": row["font"] or None,
                "fontSize": _float(row["font_size"]) if row["font_size"] else None,
                "metadataComplete": _bool(row["metadata_complete"]),
            })

    for project in projects.values():
        project["compositions"].sort(key=lambda row: (row["path"], row["id"]))
        project["textFields"].sort(key=lambda row: (row["compositionPath"], row["layerIndex"]))
        if len(project["compositions"]) != project["reportedCompositionCount"]:
            raise ValueError(f"composition count mismatch: {project['id']}")
        text_ids = {field["id"] for field in project["textFields"]}
        for composition in project["compositions"]:
            if len(composition["recursiveTextFieldIds"]) != composition["recursiveEditableTextFields"]:
                raise ValueError(f"recursive text count mismatch: {project['id']}:{composition['id']}")
            if any(field_id not in text_ids for field_id in composition["recursiveTextFieldIds"]):
                raise ValueError(f"recursive text field is missing: {project['id']}:{composition['id']}")
            if len(composition["recursiveVisualMediaInputs"]) != composition["totalIndependentVisualMediaInputs"]:
                raise ValueError(f"recursive media count mismatch: {project['id']}:{composition['id']}")
        project["capacityEnvelope"] = {
            "maxTotalIndependentVisualMediaInputs": max(
                (row["totalIndependentVisualMediaInputs"] for row in project["compositions"]), default=0
            ),
            "maxSimultaneouslyEnabledRecursiveVisualInputs": max(
                (row["maxSimultaneouslyEnabledRecursiveVisualInputs"] for row in project["compositions"]), default=0
            ),
            "maxRecursiveEditableTextFields": max(
                (row["recursiveEditableTextFields"] for row in project["compositions"]), default=0
            ),
            "maxDurationSeconds": max((row["durationSeconds"] for row in project["compositions"]), default=0),
        }

    counts = {
        "projects": len(projects),
        "compositions": sum(len(row["compositions"]) for row in projects.values()),
        "textFields": sum(len(row["textFields"]) for row in projects.values()),
    }
    expected = summary.get("counts") or {}
    if counts["projects"] != expected.get("sourceProjects"):
        raise ValueError("master summary project count does not reconcile")
    if counts["compositions"] != expected.get("reportedCompositions"):
        raise ValueError("master summary composition count does not reconcile")
    if counts["textFields"] != expected.get("reportedTextFields"):
        raise ValueError("master summary text-field count does not reconcile")
    artifact = {
        "schemaVersion": 1,
        "purpose": "Portable source-bound AE technical index for read-only matching tests",
        "renderingPerformed": False,
        "sourceReports": {
            "summary": _source(summary_path),
            "compositions": _source(compositions_path),
            "textFields": _source(text_fields_path),
        },
        "counts": counts,
        "projects": [projects[key] for key in sorted(projects)],
    }
    validate_technical_index(artifact)
    return artifact


def validate_technical_index(artifact: dict[str, Any]) -> dict[str, int]:
    if artifact.get("schemaVersion") != 1 or artifact.get("renderingPerformed") is not False:
        raise ValueError("unsupported or non-inspection technical index")
    projects = artifact.get("projects") or []
    ids = [row.get("id") for row in projects]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate project id in technical index")
    for project in projects:
        if not project.get("sourceProjectSha256") or not project.get("sourceUnchanged"):
            raise ValueError(f"unbound or changed measured project: {project.get('id')}")
        comp_ids = [row.get("id") for row in project.get("compositions") or []]
        if len(comp_ids) != len(set(comp_ids)):
            raise ValueError(f"duplicate composition id: {project['id']}")
        if len(comp_ids) != project.get("reportedCompositionCount"):
            raise ValueError(f"stale composition count: {project['id']}")
        text_ids = {field.get("id") for field in project.get("textFields") or []}
        for composition in project.get("compositions") or []:
            if len(composition.get("recursiveTextFieldIds") or []) != composition.get("recursiveEditableTextFields"):
                raise ValueError(f"stale recursive text fields: {project['id']}:{composition.get('id')}")
            if any(field_id not in text_ids for field_id in composition.get("recursiveTextFieldIds") or []):
                raise ValueError(f"unknown recursive text field: {project['id']}:{composition.get('id')}")
            if len(composition.get("recursiveVisualMediaInputs") or []) != composition.get("totalIndependentVisualMediaInputs"):
                raise ValueError(f"stale recursive media inputs: {project['id']}:{composition.get('id')}")
    counts = {
        "projects": len(projects),
        "compositions": sum(len(row.get("compositions") or []) for row in projects),
        "textFields": sum(len(row.get("textFields") or []) for row in projects),
    }
    if counts != artifact.get("counts"):
        raise ValueError(f"technical index counts are stale: {counts}")
    return counts


def _scene_index(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    scenes: dict[str, dict[str, Any]] = {}
    for family in catalog.get("items") or []:
        if family.get("type") != "after_effects":
            continue
        family_id = family.get("templateId")
        for scene in family.get("scenes") or []:
            scene_id = scene.get("id")
            if not scene_id or scene_id in scenes:
                raise ValueError(f"missing or duplicate approved scene id: {scene_id}")
            scenes[scene_id] = {
                "familyId": family_id,
                "nativeCompositionId": scene.get("nativeCompositionId"),
                "nativeCompositionMappingStatus": scene.get("nativeCompositionMappingStatus", "unverified"),
                "observedFocalImageCount": scene.get("focalImageCount"),
                "availabilityStatus": scene.get("availabilityStatus"),
            }
    return scenes


def _link_index(links: dict[str, Any], projects: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if links.get("schemaVersion") != 1:
        raise ValueError("unsupported AE spec-link schema")
    out: dict[str, dict[str, Any]] = {}
    for row in links.get("links") or []:
        family_id = row.get("familyId")
        project_id = row.get("projectId")
        if not family_id or family_id in out:
            raise ValueError(f"missing or duplicate scene family link: {family_id}")
        if project_id not in projects:
            raise ValueError(f"scene family links unknown measured project: {project_id}")
        if row.get("sourceProjectSha256") != projects[project_id].get("sourceProjectSha256"):
            raise ValueError(f"scene family link source hash mismatch: {family_id}")
        if row.get("compositionMappingStatus") not in {"verified", "unverified"}:
            raise ValueError(f"invalid composition mapping status: {family_id}")
        out[family_id] = row
    return out


def validate_scene_mappings(
    artifact: dict[str, Any],
    technical: dict[str, Any],
    expected_scene_projects: dict[str, str],
    window_capacities: dict[str, Any] | None = None,
) -> dict[str, int]:
    """Validate exact mappings against both the comparison scope and measured index."""
    if artifact.get("schemaVersion") != 1:
        raise ValueError("unsupported scene-composition mapping schema")
    projects = {row["id"]: row for row in technical.get("projects") or []}
    rows = artifact.get("mappings") or []
    ids = [row.get("sceneId") for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate scene-composition mapping")
    if not set(expected_scene_projects).issubset(ids):
        missing = sorted(set(expected_scene_projects) - set(ids))
        raise ValueError(f"scene-composition mapping scope mismatch: missing={missing}")
    if (artifact.get("scope") or {}).get("uniqueScenes") != len(rows):
        raise ValueError("scene-composition mapping scope count is stale")
    verified = 0
    verified_window = 0
    unresolved = 0
    unreviewed = 0
    for row in rows:
        scene_id = row["sceneId"]
        project_id = row.get("projectId")
        in_comparison_scope = scene_id in expected_scene_projects
        if in_comparison_scope and project_id != expected_scene_projects[scene_id]:
            raise ValueError(f"mapping uses wrong measured project: {scene_id}")
        if project_id not in projects:
            raise ValueError(f"mapping uses unknown measured project: {project_id}")
        compositions = {comp["id"]: comp for comp in projects[project_id]["compositions"]}
        paths = {comp["path"] for comp in compositions.values()}
        status = row.get("status")
        if status in {"verified", "verified_window"}:
            verified += int(in_comparison_scope)
            comp_id = row.get("compositionId")
            comp = compositions.get(comp_id)
            if not comp or comp["path"] != row.get("compositionPath"):
                raise ValueError(f"composition id/path mismatch: {scene_id}")
            if not isinstance(row.get("evidence"), str) or not row["evidence"].strip():
                raise ValueError(f"verified mapping lacks evidence: {scene_id}")
            if row.get("reason") or row.get("candidateCompositionPaths"):
                raise ValueError(f"verified mapping contains unresolved fields: {scene_id}")
            if status == "verified_window":
                verified_window += int(in_comparison_scope)
                windows = {
                    item["sceneId"]: item
                    for item in (window_capacities or {}).get("windows", [])
                }
                window = windows.get(row.get("windowCapacityId"))
                if not window or row.get("windowCapacityId") != scene_id:
                    raise ValueError(f"verified window mapping lacks capacity: {scene_id}")
                capacity = window["capacity"]
                if window["projectId"] != project_id or (
                    capacity["compositionId"] != comp_id
                    or capacity["compositionPath"] != row.get("compositionPath")
                ):
                    raise ValueError(f"verified window capacity mismatch: {scene_id}")
            elif row.get("windowCapacityId") is not None:
                raise ValueError(f"whole-composition mapping claims window capacity: {scene_id}")
        elif status == "unresolved":
            unresolved += int(in_comparison_scope)
            candidates = row.get("candidateCompositionPaths") or []
            if not isinstance(row.get("reason"), str) or not row["reason"].strip():
                raise ValueError(f"unresolved mapping lacks reason: {scene_id}")
            if len(candidates) < 1 or any(path not in paths for path in candidates):
                raise ValueError(f"unresolved mapping has invalid candidates: {scene_id}")
            if row.get("compositionId") is not None or row.get("compositionPath") is not None:
                raise ValueError(f"unresolved mapping claims an exact composition: {scene_id}")
        elif status == "unreviewed":
            unreviewed += int(in_comparison_scope)
            if not isinstance(row.get("reason"), str) or not row["reason"].strip():
                raise ValueError(f"unreviewed mapping lacks reason: {scene_id}")
            if row.get("candidateCompositionPaths"):
                raise ValueError(f"unreviewed mapping claims reviewed candidates: {scene_id}")
            if row.get("compositionId") is not None or row.get("compositionPath") is not None:
                raise ValueError(f"unreviewed mapping claims an exact composition: {scene_id}")
        else:
            raise ValueError(f"invalid scene-composition mapping status: {scene_id}")
    return {
        "scenes": len(expected_scene_projects),
        "verified": verified,
        "verifiedWindow": verified_window,
        "verifiedWholeComposition": verified - verified_window,
        "unresolved": unresolved,
        "unreviewed": unreviewed,
    }


def _slate_index(slate: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out = {}
    for row in slate:
        source_id = f"{row['passage']}-{row['beat']}"
        if source_id in out:
            raise ValueError(f"duplicate source beat in slate: {source_id}")
        out[source_id] = row
    return out


def build_comparison(
    *,
    tasks_path: Path = DEFAULT_TASKS,
    slate_path: Path = DEFAULT_SLATE,
    catalog_path: Path = DEFAULT_CATALOG,
    links_path: Path = DEFAULT_LINKS,
    index_path: Path = DEFAULT_INDEX,
    scene_mappings_path: Path = DEFAULT_SCENE_MAPPINGS,
    window_capacities_path: Path = DEFAULT_WINDOW_CAPACITIES,
    task_requirements_path: Path = DEFAULT_TASK_REQUIREMENTS,
    baseline_entities_path: Path = DEFAULT_BASELINE_ENTITIES,
) -> dict[str, Any]:
    paths = {
        "visualTasks": Path(tasks_path),
        "baselineSlate": Path(slate_path),
        "approvedCatalog": Path(catalog_path),
        "specLinks": Path(links_path),
        "technicalIndex": Path(index_path),
        "sceneMappings": Path(scene_mappings_path),
        "sceneWindowCapacities": Path(window_capacities_path),
        "taskRequirements": Path(task_requirements_path),
        "baselineEntities": Path(baseline_entities_path),
    }
    tasks_artifact = _read(paths["visualTasks"])
    if tasks_artifact.get("activationState") != "review_only_not_connected":
        raise ValueError("VisualTask artifact is not review-only")
    tasks = tasks_artifact.get("tasks") or []
    slate = _slate_index(_read(paths["baselineSlate"]))
    scenes = _scene_index(_read(paths["approvedCatalog"]))
    technical = _read(paths["technicalIndex"])
    validate_technical_index(technical)
    projects = {row["id"]: row for row in technical["projects"]}
    links = _link_index(_read(paths["specLinks"]), projects)
    baseline_entities = _read(paths["baselineEntities"])
    global_subject = (baseline_entities.get("_subject") or {}).get("entity")

    expected_scene_projects: dict[str, str] = {}
    for task in tasks:
        baseline = slate.get(task["sourceBeatId"])
        if not baseline:
            continue
        for option in baseline.get("options") or []:
            scene = scenes.get(option["id"])
            link = links.get(scene.get("familyId")) if scene else None
            if link:
                previous = expected_scene_projects.setdefault(option["id"], link["projectId"])
                if previous != link["projectId"]:
                    raise ValueError(f"scene links to multiple measured projects: {option['id']}")
    scene_mappings_artifact = _read(paths["sceneMappings"])
    window_capacities_artifact = _read(paths["sceneWindowCapacities"])
    from . import scene_window_capacity
    scene_window_capacity.validate_window_capacities(window_capacities_artifact)
    mapping_counts = validate_scene_mappings(
        scene_mappings_artifact,
        technical,
        expected_scene_projects,
        window_capacities_artifact,
    )
    scene_mappings = {row["sceneId"]: row for row in scene_mappings_artifact["mappings"]}
    scene_windows = {row["sceneId"]: row for row in window_capacities_artifact["windows"]}
    from . import visualtask_requirements

    requirements_artifact = _read(paths["taskRequirements"])
    visualtask_requirements.validate_requirements(requirements_artifact)
    requirement_rows = requirements_artifact.get("tasks") or []
    requirements = {row["taskId"]: row for row in requirement_rows}
    if set(requirements) != {row["id"] for row in tasks}:
        raise ValueError("VisualTask technical requirement scope mismatch")

    rows = []
    verdict_counts: Counter[str] = Counter()
    technical_evidence_counts: Counter[str] = Counter()
    mapped_candidates = 0
    candidate_count = 0
    for task in tasks:
        source_id = task["sourceBeatId"]
        if source_id not in slate:
            raise ValueError(f"VisualTask has no baseline slate row: {source_id}")
        baseline = slate[source_id]
        display_entities = task["entities"]["displayEligible"]
        display_demand = len(display_entities)
        task_requirements = requirements[task["id"]]
        exact_task_span = task_requirements["timingRequirement"]["exactTaskAudioSpan"]
        media_requirement = task_requirements["mediaRequirements"]
        required_media_kinds = media_requirement.get("requiredMediaKinds")
        missing_media_brief = media_requirement.get("missingMediaBrief")
        comparisons = []
        for option in baseline.get("options") or []:
            candidate_count += 1
            scene_id = option["id"]
            scene = scenes.get(scene_id)
            family_id = scene.get("familyId") if scene else None
            link = links.get(family_id) if family_id else None
            if not link:
                technical_verdict = "technical_spec_unmapped"
                verdict = "conditional" if missing_media_brief else technical_verdict
                missing = list(MISSING_FOR_FILLABLE_NOW)
                if exact_task_span:
                    missing.remove("exact_task_audio_span")
                if required_media_kinds:
                    missing.remove("media_kind_constraints")
                comparison = {
                    "candidateId": scene_id,
                    "familyId": family_id,
                    "verdict": verdict,
                    "technicalEvidenceVerdict": technical_verdict,
                    "reason": (
                        "Required media is known to be missing; this candidate remains conditional even though no explicit reviewed link connects its family to a measured AE project."
                        if missing_media_brief else
                        "No explicit reviewed link connects this candidate family to a measured AE project."
                    ),
                    "missingForFillableNow": missing,
                }
                if missing_media_brief:
                    comparison["missingMediaBrief"] = missing_media_brief
                comparisons.append(comparison)
                verdict_counts[verdict] += 1
                technical_evidence_counts[technical_verdict] += 1
                continue
            mapped_candidates += 1
            project = projects[link["projectId"]]
            mapping = scene_mappings[scene_id]
            exact_comp = None
            if mapping["status"] == "verified":
                exact_comp = next(
                    row for row in project["compositions"]
                    if row["id"] == mapping["compositionId"]
                )
            elif mapping["status"] == "verified_window":
                parent = next(
                    row for row in project["compositions"]
                    if row["id"] == mapping["compositionId"]
                )
                capacity = scene_windows[scene_id]["capacity"]
                exact_comp = {
                    **parent,
                    "durationSeconds": capacity["window"]["durationSeconds"],
                    "frameCount": round(capacity["window"]["durationSeconds"] * parent["frameRate"]),
                    "totalIndependentVisualMediaInputs": capacity["totalIndependentVisualMediaInputs"],
                    "maxSimultaneouslyEnabledRecursiveVisualInputs": capacity["maxSimultaneouslyEnabledRecursiveVisualInputs"],
                    "recursiveEditableTextFields": len(capacity["recursiveEditableTextFields"]),
                    "maxSimultaneouslyEnabledRecursiveTextFields": capacity["maxSimultaneouslyEnabledRecursiveTextFields"],
                    "recursiveTextFieldIds": [row["id"] for row in capacity["recursiveEditableTextFields"]],
                    "recursiveVisualMediaInputs": capacity["recursiveVisualMediaInputs"],
                    "measurementScope": "clip_window",
                    "window": capacity["window"],
                }
            technical_verdict = "exact_technical_evidence_partial" if exact_comp else "project_technical_evidence_partial"
            verdict = "conditional" if missing_media_brief else technical_verdict
            reason = (
                "Required media is known to be missing; measured template capacity cannot make the treatment fillable until that media is supplied."
                if missing_media_brief else
                f"{'Exact composition measurements are' if exact_comp else 'A project-wide measurement envelope is'} available, "
                "but unresolved treatment-specific requirements still prevent a fillable-now decision. "
                "Display identities are not assumed to equal media slots."
            )
            missing = list(MISSING_FOR_FILLABLE_NOW)
            if exact_comp:
                missing.remove("exact_scene_to_native_composition_mapping")
            if exact_task_span:
                missing.remove("exact_task_audio_span")
            if required_media_kinds:
                missing.remove("media_kind_constraints")
            comparison = {
                "candidateId": scene_id,
                "familyId": family_id,
                "projectId": project["id"],
                "projectEvidenceStatus": project["resultStatus"],
                "compositionMappingStatus": mapping["status"],
                "displayIdentityDemand": display_demand,
                "projectCapacityEnvelope": project["capacityEnvelope"],
                "verdict": verdict,
                "technicalEvidenceVerdict": technical_verdict,
                "reason": reason,
                "missingForFillableNow": missing,
            }
            if missing_media_brief:
                comparison["missingMediaBrief"] = missing_media_brief
            if exact_comp:
                text_fields_by_id = {field["id"]: field for field in project["textFields"]}
                comparison["exactComposition"] = {
                    **exact_comp,
                    "directTextFields": [
                        field for field in project["textFields"]
                        if field["compositionId"] == exact_comp["id"]
                    ],
                    "recursiveTextFields": [
                        text_fields_by_id[field_id]
                        for field_id in exact_comp["recursiveTextFieldIds"]
                    ],
                    "mappingEvidence": mapping["evidence"],
                }
                if exact_task_span:
                    native_duration = exact_comp["durationSeconds"]
                    task_duration = exact_task_span["durationSeconds"]
                    comparison["timingObservation"] = {
                        "taskAudioDurationSeconds": task_duration,
                        "nativeCompositionDurationSeconds": native_duration,
                        "nativeMinusTaskSeconds": native_duration - task_duration,
                        "nativeDurationCoversUnmodifiedTask": native_duration >= task_duration,
                        "status": "observation_only_not_timing_fit",
                        "reason": "No approved looping, trimming, speed, freeze, extension, or phrase-timing policy is encoded for this treatment.",
                    }
            else:
                mapping_key = "mappingUnreviewed" if mapping["status"] == "unreviewed" else "mappingUnresolved"
                comparison[mapping_key] = {
                    "reason": mapping["reason"],
                    "candidateCompositionPaths": mapping.get("candidateCompositionPaths", []),
                }
            comparisons.append(comparison)
            verdict_counts[verdict] += 1
            technical_evidence_counts[technical_verdict] += 1
        rows.append({
            "taskId": task["id"],
            "sourceBeatId": source_id,
            "taskRole": task["taskRole"],
            "quote": task["quote"],
            "legacyGlobalSubject": global_subject,
            "legacyGlobalSubjectWouldBeInjected": bool(global_subject),
            "resolvedIdentities": task["entities"]["resolved"],
            "displayEligibleIdentities": display_entities,
            "displayIdentityDemand": display_demand,
            "unresolvedIdentities": task["entities"]["unresolved"],
            "technicalRequirements": task_requirements,
            "baselineCandidateCount": len(baseline.get("options") or []),
            "candidateComparisons": comparisons,
        })

    task_ids = [row["taskId"] for row in rows]
    source_counts = Counter(row["sourceBeatId"] for row in rows)
    artifact = {
        "schemaVersion": 1,
        "purpose": "Read-only before/after VisualTask and measured AE technical-capacity comparison",
        "activationState": "review_only_not_connected",
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "sources": {name: _source(path) for name, path in paths.items()},
        "protectedLiveArtifacts": {path.relative_to(ROOT).as_posix(): _sha(path) for path in PROTECTED_LIVE_ARTIFACTS},
        "counts": {
            "sourceBeats": len(source_counts),
            "visualTasks": len(rows),
            "splitBeats": sum(count > 1 for count in source_counts.values()),
            "baselineCandidates": candidate_count,
            "mappedCandidates": mapped_candidates,
            "unmappedCandidates": candidate_count - mapped_candidates,
            "projectTechnicalEvidencePartial": technical_evidence_counts["project_technical_evidence_partial"],
            "exactTechnicalEvidencePartial": technical_evidence_counts["exact_technical_evidence_partial"],
            "conditionalCandidates": verdict_counts["conditional"],
            "exactTaskAudioSpans": requirements_artifact["counts"]["exactTaskAudioSpans"],
            "unresolvedTaskAudioSpans": requirements_artifact["counts"]["unresolvedTaskAudioSpans"],
            "exactTimingObservations": sum("timingObservation" in row for task_row in rows for row in task_row["candidateComparisons"]),
            "verifiedUniqueSceneMappings": mapping_counts["verified"],
            "verifiedWholeCompositionMappings": mapping_counts["verifiedWholeComposition"],
            "verifiedWindowMappings": mapping_counts["verifiedWindow"],
            "unresolvedUniqueSceneMappings": mapping_counts["unresolved"],
            "unreviewedUniqueSceneMappings": mapping_counts["unreviewed"],
        },
        "evidenceBoundary": {
            "canDecide": [
                "the exact native technical capacity of a verified scene/composition mapping",
                "whether an exact native composition's unmodified duration covers a source-bound task audio span, as an observation rather than a timing-fit verdict",
                "whether a baseline candidate family lacks an explicit measured-project link",
            ],
            "cannotYetDecide": list(MISSING_FOR_FILLABLE_NOW),
            "fillableNowStatus": "not_computable_until_treatment_requirements_are_reviewed",
        },
        "tasks": rows,
    }
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("duplicate task id in comparison")
    validate_comparison(artifact, verify_sources=False)
    return artifact


def validate_comparison(artifact: dict[str, Any], *, verify_sources: bool = True) -> dict[str, int]:
    if artifact.get("schemaVersion") != 1:
        raise ValueError("unsupported comparison schema")
    if artifact.get("activationState") != "review_only_not_connected":
        raise ValueError("comparison must remain review-only")
    if artifact.get("selectionAuthorized") is not False or artifact.get("renderingAuthorized") is not False:
        raise ValueError("comparison cannot authorize selection or rendering")
    if artifact.get("evidenceBoundary", {}).get("fillableNowStatus") != "not_computable_until_treatment_requirements_are_reviewed":
        raise ValueError("comparison overclaims fillability")
    tasks = artifact.get("tasks") or []
    ids = [row.get("taskId") for row in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate comparison task id")
    counts_by_source = Counter(row.get("sourceBeatId") for row in tasks)
    comparisons = [candidate for row in tasks for candidate in row.get("candidateComparisons") or []]
    verdicts = Counter(row.get("verdict") for row in comparisons)
    technical_verdicts = Counter(row.get("technicalEvidenceVerdict") for row in comparisons)
    counts = {
        "sourceBeats": len(counts_by_source),
        "visualTasks": len(tasks),
        "splitBeats": sum(count > 1 for count in counts_by_source.values()),
        "baselineCandidates": len(comparisons),
        "mappedCandidates": sum(row.get("projectId") is not None for row in comparisons),
        "unmappedCandidates": sum(row.get("projectId") is None for row in comparisons),
        "projectTechnicalEvidencePartial": technical_verdicts["project_technical_evidence_partial"],
        "exactTechnicalEvidencePartial": technical_verdicts["exact_technical_evidence_partial"],
        "conditionalCandidates": verdicts["conditional"],
        "exactTaskAudioSpans": sum(
            (row.get("technicalRequirements") or {}).get("timingRequirement", {}).get("exactTaskAudioSpan") is not None
            for row in tasks
        ),
        "unresolvedTaskAudioSpans": sum(
            (row.get("technicalRequirements") or {}).get("timingRequirement", {}).get("exactTaskAudioSpan") is None
            for row in tasks
        ),
        "exactTimingObservations": sum("timingObservation" in row for row in comparisons),
        "verifiedUniqueSceneMappings": len({row["candidateId"] for row in comparisons if row.get("exactComposition")}),
        "verifiedWholeCompositionMappings": len({
            row["candidateId"] for row in comparisons
            if row.get("exactComposition") and row["exactComposition"].get("measurementScope") != "clip_window"
        }),
        "verifiedWindowMappings": len({
            row["candidateId"] for row in comparisons
            if row.get("exactComposition", {}).get("measurementScope") == "clip_window"
        }),
        "unresolvedUniqueSceneMappings": len({row["candidateId"] for row in comparisons if row.get("mappingUnresolved")}),
        "unreviewedUniqueSceneMappings": len({row["candidateId"] for row in comparisons if row.get("mappingUnreviewed")}),
    }
    if counts != artifact.get("counts"):
        raise ValueError(f"comparison counts are stale: {counts}")
    allowed = {
        "technical_spec_unmapped",
        "project_technical_evidence_partial",
        "exact_technical_evidence_partial",
        "conditional",
    }
    if any(row.get("verdict") not in allowed for row in comparisons):
        raise ValueError("comparison contains an unauthorized verdict")
    if any("fillable_now" in json.dumps(row) for row in comparisons):
        raise ValueError("candidate comparison must not claim fillable_now")
    technical_allowed = allowed - {"conditional"}
    if any(row.get("technicalEvidenceVerdict") not in technical_allowed for row in comparisons):
        raise ValueError("comparison contains an invalid technical-evidence verdict")
    requirements_by_task = {
        row["taskId"]: (row.get("technicalRequirements") or {}).get("mediaRequirements") or {}
        for row in tasks
    }
    for task in tasks:
        requirement = requirements_by_task[task["taskId"]]
        for candidate in task.get("candidateComparisons") or []:
            if candidate.get("verdict") == "conditional":
                brief = candidate.get("missingMediaBrief") or {}
                if (
                    requirement.get("availabilityStatus") != "missing"
                    or requirement.get("missingMediaBrief") != brief
                    or brief.get("status") != "missing"
                    or brief.get("mediaKind") not in (requirement.get("requiredMediaKinds") or [])
                ):
                    raise ValueError("conditional candidate lacks a matching typed missing-media brief")
    if verify_sources:
        for name, source in (artifact.get("sources") or {}).items():
            path = ROOT / source["path"]
            if not path.is_file() or _sha(path) != source["sha256"]:
                raise ValueError(f"comparison source is missing or stale: {name}")
        for raw_path, digest in (artifact.get("protectedLiveArtifacts") or {}).items():
            path = ROOT / raw_path
            if not path.is_file() or _sha(path) != digest:
                raise ValueError(f"protected live artifact changed: {raw_path}")
        replay = build_comparison(
            tasks_path=ROOT / artifact["sources"]["visualTasks"]["path"],
            slate_path=ROOT / artifact["sources"]["baselineSlate"]["path"],
            catalog_path=ROOT / artifact["sources"]["approvedCatalog"]["path"],
            links_path=ROOT / artifact["sources"]["specLinks"]["path"],
            index_path=ROOT / artifact["sources"]["technicalIndex"]["path"],
            scene_mappings_path=ROOT / artifact["sources"]["sceneMappings"]["path"],
            task_requirements_path=ROOT / artifact["sources"]["taskRequirements"]["path"],
            baseline_entities_path=ROOT / artifact["sources"]["baselineEntities"]["path"],
        )
        if dumps(replay) != dumps(artifact):
            raise ValueError("comparison does not replay from bound inputs")
    return counts


def dumps(artifact: dict[str, Any]) -> str:
    return json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    imported = sub.add_parser("import-index")
    imported.add_argument("--summary", required=True, type=Path)
    imported.add_argument("--compositions", required=True, type=Path)
    imported.add_argument("--text-fields", required=True, type=Path)
    imported.add_argument("--output", type=Path, default=DEFAULT_INDEX)
    build = sub.add_parser("build")
    build.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    validate = sub.add_parser("validate")
    validate.add_argument("artifact", type=Path, nargs="?", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.command == "import-index":
        artifact = import_technical_index(args.summary, args.compositions, args.text_fields)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(dumps(artifact), encoding="utf-8")
        print(json.dumps(validate_technical_index(artifact), sort_keys=True))
    elif args.command == "build":
        artifact = build_comparison()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(dumps(artifact), encoding="utf-8")
        print(json.dumps(validate_comparison(artifact), sort_keys=True))
    else:
        print(json.dumps(validate_comparison(_read(args.artifact)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
