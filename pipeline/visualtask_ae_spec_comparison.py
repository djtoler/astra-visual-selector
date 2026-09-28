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
    "media_kind_constraints",
    "single_person_group_eligibility",
    "text_character_and_line_limits",
    "exact_task_audio_span_and_timing_fit",
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
    for row in project_rows:
        project_id = row["id"]
        if project_id in projects:
            raise ValueError(f"duplicate measured project id: {project_id}")
        source_project = Path(row["sourceProject"])
        projects[project_id] = {
            "id": project_id,
            "batchId": row["batchId"],
            "resultStatus": row["resultStatus"],
            "evidenceStatus": row["evidenceStatus"],
            "sourceProjectName": source_project.name,
            "sourceProjectSha256": row["expectedSourceSha256"],
            "sourceUnchanged": bool(row["sourceUnchanged"]),
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
            projects[project_id]["compositions"].append({
                "id": _int(row["composition_id"]),
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
            })

    with text_fields_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            project_id = row["project_id"]
            if project_id not in projects:
                raise ValueError(f"text field references unknown measured project: {project_id}")
            projects[project_id]["textFields"].append({
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
        if row.get("compositionMappingStatus") not in {"verified", "unverified"}:
            raise ValueError(f"invalid composition mapping status: {family_id}")
        out[family_id] = row
    return out


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
    baseline_entities_path: Path = DEFAULT_BASELINE_ENTITIES,
) -> dict[str, Any]:
    paths = {
        "visualTasks": Path(tasks_path),
        "baselineSlate": Path(slate_path),
        "approvedCatalog": Path(catalog_path),
        "specLinks": Path(links_path),
        "technicalIndex": Path(index_path),
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

    rows = []
    verdict_counts: Counter[str] = Counter()
    mapped_candidates = 0
    candidate_count = 0
    for task in tasks:
        source_id = task["sourceBeatId"]
        if source_id not in slate:
            raise ValueError(f"VisualTask has no baseline slate row: {source_id}")
        baseline = slate[source_id]
        display_entities = task["entities"]["displayEligible"]
        display_demand = len(display_entities)
        comparisons = []
        for option in baseline.get("options") or []:
            candidate_count += 1
            scene_id = option["id"]
            scene = scenes.get(scene_id)
            family_id = scene.get("familyId") if scene else None
            link = links.get(family_id) if family_id else None
            if not link:
                verdict = "technical_spec_unmapped"
                comparisons.append({
                    "candidateId": scene_id,
                    "familyId": family_id,
                    "verdict": verdict,
                    "reason": "No explicit reviewed link connects this candidate family to a measured AE project.",
                    "missingForFillableNow": list(MISSING_FOR_FILLABLE_NOW),
                })
                verdict_counts[verdict] += 1
                continue
            mapped_candidates += 1
            project = projects[link["projectId"]]
            maximum = project["capacityEnvelope"]["maxSimultaneouslyEnabledRecursiveVisualInputs"]
            unresolved_slots = int(project["projectSummary"].get("unresolvedFileFootageCandidates") or 0)
            verified_slots = int(project["projectSummary"].get("verifiedIndependentVisualMediaInputs") or 0)
            if display_demand > maximum and (maximum == 0 or verified_slots == 0 or unresolved_slots > 0):
                verdict = "project_capacity_unknown"
                reason = (
                    f"The family is linked, but the inspector verified {verified_slots} project media slots "
                    f"and retained {unresolved_slots} unresolved footage candidates; zero or a lower bound is "
                    "not treated as proof that the preview scene cannot hold the task."
                )
            elif display_demand > maximum:
                verdict = "project_capacity_conflict"
                reason = (
                    f"Task needs {display_demand} display-eligible identities, exceeding the measured "
                    f"project-wide simultaneous visual-input maximum of {maximum}."
                )
            else:
                verdict = "project_capacity_possible"
                reason = (
                    f"Project-wide simultaneous capacity {maximum} does not rule out display demand "
                    f"{display_demand}; the individual preview scene is not mapped to a native composition."
                )
            missing = list(MISSING_FOR_FILLABLE_NOW)
            if link["compositionMappingStatus"] == "verified" and scene and scene["nativeCompositionId"] is not None:
                missing.remove("exact_scene_to_native_composition_mapping")
            comparisons.append({
                "candidateId": scene_id,
                "familyId": family_id,
                "projectId": project["id"],
                "projectEvidenceStatus": project["resultStatus"],
                "compositionMappingStatus": link["compositionMappingStatus"],
                "displayIdentityDemand": display_demand,
                "projectCapacityEnvelope": project["capacityEnvelope"],
                "verdict": verdict,
                "reason": reason,
                "missingForFillableNow": missing,
            })
            verdict_counts[verdict] += 1
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
            "projectCapacityPossible": verdict_counts["project_capacity_possible"],
            "projectCapacityConflicts": verdict_counts["project_capacity_conflict"],
            "projectCapacityUnknown": verdict_counts["project_capacity_unknown"],
        },
        "evidenceBoundary": {
            "canDecide": [
                "whether display-identity demand exceeds every composition's measured simultaneous visual-input capacity in a linked project whose replacement-slot inventory is complete",
                "whether a baseline candidate family lacks an explicit measured-project link",
            ],
            "cannotYetDecide": list(MISSING_FOR_FILLABLE_NOW),
            "fillableNowStatus": "not_computable_from_current_fields",
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
    if artifact.get("evidenceBoundary", {}).get("fillableNowStatus") != "not_computable_from_current_fields":
        raise ValueError("comparison overclaims fillability")
    tasks = artifact.get("tasks") or []
    ids = [row.get("taskId") for row in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate comparison task id")
    counts_by_source = Counter(row.get("sourceBeatId") for row in tasks)
    comparisons = [candidate for row in tasks for candidate in row.get("candidateComparisons") or []]
    verdicts = Counter(row.get("verdict") for row in comparisons)
    counts = {
        "sourceBeats": len(counts_by_source),
        "visualTasks": len(tasks),
        "splitBeats": sum(count > 1 for count in counts_by_source.values()),
        "baselineCandidates": len(comparisons),
        "mappedCandidates": sum(row.get("projectId") is not None for row in comparisons),
        "unmappedCandidates": verdicts["technical_spec_unmapped"],
        "projectCapacityPossible": verdicts["project_capacity_possible"],
        "projectCapacityConflicts": verdicts["project_capacity_conflict"],
        "projectCapacityUnknown": verdicts["project_capacity_unknown"],
    }
    if counts != artifact.get("counts"):
        raise ValueError(f"comparison counts are stale: {counts}")
    allowed = {
        "technical_spec_unmapped",
        "project_capacity_possible",
        "project_capacity_conflict",
        "project_capacity_unknown",
    }
    if any(row.get("verdict") not in allowed for row in comparisons):
        raise ValueError("comparison contains an unauthorized verdict")
    if any("fillable_now" in json.dumps(row) for row in comparisons):
        raise ValueError("candidate comparison must not claim fillable_now")
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
