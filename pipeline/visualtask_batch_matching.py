#!/usr/bin/env python3
"""Run review-only template and media matching for every VisualTask in a story.

The request is the portable input envelope. This runner retrieves candidates and
reports evidence boundaries; it never selects, pairs, approves, or renders them.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from . import visualtask_matching as matching
    from .matching_contract_gate import enforce_contracts
except ImportError:  # Allow the documented direct-script entry point too.
    import visualtask_matching as matching
    from matching_contract_gate import enforce_contracts


ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_SCHEMA_VERSION = 1
REVIEW_ONLY = "review_only_not_connected"


def _read(path: Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _source(path: Path) -> dict[str, Any]:
    path = Path(path).resolve()
    return {"path": path.as_posix(), "sha256": _sha(path), "bytes": path.stat().st_size}


def _resolve_source(request_path: Path, value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (request_path.parent / path).resolve()


def _review_only(artifact: dict[str, Any], label: str) -> None:
    if artifact.get("schemaVersion") != SUPPORTED_SCHEMA_VERSION:
        raise ValueError(f"unsupported {label} schema version")
    if artifact.get("activationState") != REVIEW_ONLY:
        raise ValueError(f"{label} must remain review-only")
    if artifact.get("selectionAuthorized") not in (None, False):
        raise ValueError(f"{label} cannot authorize selection")
    if artifact.get("renderingAuthorized") not in (None, False):
        raise ValueError(f"{label} cannot authorize rendering")


def _load_inputs(request_path: Path) -> tuple[dict[str, Any], dict[str, Path], dict[str, Any]]:
    request_path = Path(request_path).resolve()
    request = _read(request_path)
    _review_only(request, "batch request")
    if not request.get("batchId"):
        raise ValueError("batch request lacks batchId")
    required = {
        "storyPackage", "visualTasks", "technicalRequirements", "bindings",
        "technicalComparison", "timingPlans",
    }
    optional = {
        "treatmentAssessments", "dataAssignments", "storyMatchingHandoff",
        "priorReviewReconciliation",
    }
    sources = request.get("sources") or {}
    if not required.issubset(sources) or set(sources) - required - optional:
        raise ValueError(
            f"batch request sources require {sorted(required)} and allow only {sorted(optional)}"
        )
    paths = {name: _resolve_source(request_path, value) for name, value in sources.items()}
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        raise ValueError(f"batch request source missing: {', '.join(sorted(missing))}")
    values = {name: _read(path) for name, path in paths.items()}
    return request, paths, values


def _validate_scope(values: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    story = values["storyPackage"]
    tasks_artifact = values["visualTasks"]
    requirements_artifact = values["technicalRequirements"]
    _review_only(story, "StoryPackage")
    _review_only(tasks_artifact, "VisualTask artifact")
    _review_only(requirements_artifact, "technical-requirements artifact")
    if not story.get("storyId") or not story.get("namespace"):
        raise ValueError("StoryPackage requires storyId and namespace")
    declaration = story.get("visualTasks")
    if declaration is not None and declaration.get("schemaVersion") != tasks_artifact.get("schemaVersion"):
        raise ValueError("StoryPackage VisualTask schema declaration does not match")
    tasks = tasks_artifact.get("tasks") or []
    task_ids = [row.get("id") for row in tasks]
    if not tasks or any(not value for value in task_ids) or len(task_ids) != len(set(task_ids)):
        raise ValueError("VisualTask artifact requires distinct nonempty task IDs")
    expected = declaration.get("expectedTaskCount") if declaration else None
    if expected is not None and expected != len(tasks):
        raise ValueError("StoryPackage VisualTask count does not match")
    requirements = copy.deepcopy(requirements_artifact.get("tasks") or [])
    requirements_by_id = {row.get("taskId"): row for row in requirements}
    if len(requirements_by_id) != len(requirements) or set(requirements_by_id) != set(task_ids):
        raise ValueError("VisualTask technical requirement scope mismatch")
    if "storyMatchingHandoff" in values:
        handoff = values["storyMatchingHandoff"]
        _review_only(handoff, "story matching handoff")
        if handoff.get("storyMatchingHandoffReceipt", {}).get("accepted") is not True:
            raise ValueError("story matching handoff lacks an accepted checker receipt")
        handed = handoff.get("tasks") or []
        handed_by_id = {row.get("taskId"): row for row in handed}
        if len(handed_by_id) != len(handed) or set(handed_by_id) != set(task_ids):
            raise ValueError("story matching handoff task scope mismatch")
        for task in tasks:
            task_id = task["id"]
            row = handed_by_id[task_id]
            if row.get("sourceBeatId") != task.get("sourceBeatId"):
                raise ValueError(f"story matching handoff source beat drift: {task_id}")
            source_job = task.get("sourceBeatJob", task.get("job"))
            if row.get("linkage", {}).get("visualJob") != source_job:
                raise ValueError(f"story matching handoff visual job drift: {task_id}")
            requirement = requirements_by_id[task_id]
            story_media = row["media"]
            focal = story_media["focal"]
            media = requirement["mediaRequirements"]
            existing_status = media.get("status")
            existing_required = existing_status in {"required", "missing_required_media"}
            story_entities = [
                entity["entity"] for entity in story_media["entities"]
                if entity["recognition"] != "none"
            ]
            cohort_entities = []
            for cohort in story_media["cohorts"]:
                if cohort["recognition"] == "none":
                    continue
                key = f"{cohort['cohort']}@{cohort['version']}"
                members = cohort.get("shownIds") or (handoff.get("cohortMembers") or {}).get(key)
                if members is None:
                    raise ValueError(f"story matching handoff cohort lacks members: {task_id}: {key}")
                cohort_entities.extend(members)
            story_entities = list(dict.fromkeys(story_entities + cohort_entities))
            media["storyFocalRequirement"] = focal
            media["storySourceSpecific"] = list(story_media["sourceSpecific"])
            media["storyCohortMembers"] = cohort_entities
            if story_media["storyRequiresKind"]:
                media["requiredEntities"] = list(dict.fromkeys((media.get("requiredEntities") or []) + story_entities))
                media["requiredMediaKinds"] = list(dict.fromkeys((media.get("requiredMediaKinds") or []) + story_media["kinds"]))
                media["status"] = existing_status if existing_status == "missing_required_media" else "required"
            elif not existing_required:
                # Recognition can be carried by labels, marks, or data encodings. A
                # named story entity is not by itself a Media Library requirement.
                media["requiredEntities"] = []
                media["requiredMediaKinds"] = []
                media["status"] = "not_required"
            text = requirement["textRequirements"]
            fields = row["text"]["fields"]
            text["requiredFieldCount"] = len(fields)
            text["requiredExactStrings"] = [
                field.get("copy") or (field.get("contentRef") or {}).get("text") or field.get("entity")
                for field in fields
            ]
            text["characterAndLineLimits"] = [
                {key: field.get(key) for key in ("fieldId", "role", "maxChars", "truncation", "abbreviation", "wrap")}
                for field in fields
            ]
            text["status"] = "exact_story_fields" if fields else "not_required"
            data = requirement["dataRequirements"]
            data["storyPresentationBinding"] = row["data"]
            requirement["storyMatchingHandoff"] = {
                "handoffId": handoff["handoffId"],
                "packageId": handoff["packageId"],
                "taskId": task_id,
            }
    if "priorReviewReconciliation" in values:
        prior = values["priorReviewReconciliation"]
        _review_only(prior, "prior-review reconciliation")
        rows = prior.get("rows") or []
        keys = [(row.get("taskId"), row.get("candidateId")) for row in rows]
        if any(not all(key) for key in keys) or len(keys) != len(set(keys)):
            raise ValueError("prior-review reconciliation requires distinct task/candidate rows")
        unknown_tasks = {task_id for task_id, _ in keys} - set(task_ids)
        if unknown_tasks:
            raise ValueError("prior-review reconciliation task scope mismatch")
    bindings = values["bindings"]
    if not isinstance(bindings, dict):
        raise ValueError("template bindings must be an object keyed by matching job")
    comparison = values["technicalComparison"]
    _review_only(comparison, "technical comparison")
    comparison_ids = [row.get("taskId") for row in comparison.get("tasks") or []]
    if len(comparison_ids) != len(set(comparison_ids)) or not set(comparison_ids).issubset(task_ids):
        raise ValueError("technical comparison task scope mismatch")
    timing = values["timingPlans"]
    if timing.get("activationState") != "diagnostic_only":
        raise ValueError("timing plans must remain diagnostic-only")
    if timing.get("selectionAuthorized") not in (None, False) or timing.get("renderingAuthorized") not in (None, False):
        raise ValueError("timing plans cannot authorize selection or rendering")
    if "treatmentAssessments" in values:
        assessments = values["treatmentAssessments"]
        if assessments.get("selectionAuthorized") not in (None, False) or assessments.get("renderingAuthorized") not in (None, False):
            raise ValueError("treatment assessments cannot authorize selection or rendering")
    if "dataAssignments" in values:
        assignments = values["dataAssignments"]
        if assignments.get("schemaVersion") != 1:
            raise ValueError("unsupported data-assignment schema version")
        if assignments.get("dataHandoffComplete") is not True:
            raise ValueError("data assignments must be complete before batch matching")
        if assignments.get("selectionAuthorized") is not False or assignments.get("renderingAuthorized") is not False:
            raise ValueError("data assignments cannot authorize selection or rendering")
        rows = assignments.get("assignments") or []
        assignment_by_id = {row.get("taskId"): row for row in rows}
        if len(assignment_by_id) != len(rows):
            raise ValueError("data assignments require distinct task IDs")
        required_data_ids = {
            row["taskId"] for row in requirements
            if (row.get("dataRequirements") or {}).get("requiredEncodings")
        }
        if set(assignment_by_id) != required_data_ids:
            raise ValueError("data-assignment task scope mismatch")
        for task_id, assignment in assignment_by_id.items():
            if assignment.get("status") != "resolved" or assignment.get("gaps"):
                raise ValueError("data assignment is not fully resolved")
            typed_fields = assignment.get("typedFields") or []
            if not typed_fields:
                raise ValueError("resolved data assignment lacks typed fields")
            requirements_by_id[task_id]["dataRequirements"]["requiredTypedFields"] = typed_fields
            try:
                from .storypackage_data_assignment import _validate_field
            except ImportError:
                from storypackage_data_assignment import _validate_field
            requirements_by_id[task_id]["dataRequirements"]["fieldVerification"] = {
                field["fieldId"]: "supported" if _validate_field(field, assignments.get("sources") or {}, verify_sources=True) else "unknown"
                for field in typed_fields}
            requirements_by_id[task_id]["dataRequirements"]["assignmentReceipt"] = {
                "packageId": assignments.get("packageId"),
                "taskId": task_id,
                "fieldCount": len(typed_fields),
            }
    return tasks, requirements_by_id


def _template_gaps(requirements: dict[str, Any]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    timing = requirements.get("timingRequirement") or {}
    media = requirements.get("mediaRequirements") or {}
    text = requirements.get("textRequirements") or {}
    data = requirements.get("dataRequirements") or {}
    checks = (
        (timing.get("exactTaskAudioSpan") is None, "exact_task_audio_span", timing.get("reason")),
        (
            media.get("status") in {"required", "missing_required_media"}
            and media.get("requiredSlotCount") is None,
            "task_required_media_slot_count", media.get("reason"),
        ),
        (text.get("requiredFieldCount") is None, "treatment_required_text_fields", text.get("reason")),
        (
            (text.get("requiredFieldCount") or 0) > 0 and text.get("characterAndLineLimits") is None,
            "text_character_and_line_limits", text.get("reason"),
        ),
        (bool(data.get("requiredEncodings")) and data.get("requiredTypedFields") is None,
         "task_required_data_fields", data.get("reason")),
    )
    for missing, gap_type, reason in checks:
        if missing:
            gaps.append({"type": gap_type, "status": "unresolved", "reason": reason})
    return gaps


def _comparison_index(artifact: dict[str, Any], task_sources: dict[str, Any] | None = None) -> dict[tuple[str, str], dict[str, Any]]:
    sources = artifact.get("sources") or {}
    stale = False
    # Hashing the comparison envelope cannot keep an obsolete native mapping
    # current. Validate its existing source bindings before consuming any fit.
    for name, source in sources.items():
        if name not in {"sceneMappings", "technicalIndex", "sceneWindowCapacities", "specLinks"}:
            continue
        path = Path(source.get("path") or "")
        if not path.is_absolute():
            path = ROOT / path
        if not path.is_file() or _sha(path) != source.get("sha256"):
            stale = True
    native_verified = set()
    bound_tasks = task_sources and all(
        sources.get(key, {}).get("sha256") == task_sources[name]["sha256"]
        for key, name in (("visualTasks", "visualTasks"), ("taskRequirements", "technicalRequirements")))
    if not stale and bound_tasks and {"sceneMappings", "technicalIndex"}.issubset(sources):
        def source_value(name):
            path = Path(sources[name]["path"])
            return _read(path if path.is_absolute() else ROOT / path)
        mappings = {row["sceneId"]: row for row in source_value("sceneMappings").get("mappings") or []}
        projects = {row["id"]: row for row in source_value("technicalIndex").get("projects") or [] if row.get("id")}
        for task in artifact.get("tasks") or []:
            for candidate in task.get("candidateComparisons") or []:
                mapping = mappings.get(candidate["candidateId"]) or {}
                project = projects.get(mapping.get("projectId")) or {}
                comp = next((row for row in project.get("compositions") or [] if row.get("id") == mapping.get("compositionId")), None)
                exact = candidate.get("exactComposition") or {}
                fields = ("id", "path", "durationSeconds", "frameRate", "maxSimultaneouslyEnabledDirectInputs",
                          "maxSimultaneouslyEnabledRecursiveVisualInputs", "maxSimultaneouslyEnabledRecursiveTextFields")
                if (mapping.get("status") == "verified" and comp and candidate.get("projectId") == mapping.get("projectId")
                        and project.get("sourceUnchanged") is True and project.get("resultStatus") == "two_pass_exact_agreement"
                        and len(project.get("sourceProjectSha256") or "") == 64
                        and candidate.get("projectEvidenceStatus") == "two_pass_exact_agreement"
                        and all(key in comp and exact.get(key) == comp[key] for key in fields)):
                    native_verified.add((task["taskId"], candidate["candidateId"]))
    return {
        (task["taskId"], candidate["candidateId"]): {
            **candidate,
            "nativeSourceVerified": (task["taskId"], candidate["candidateId"]) in native_verified,
            **({"projectEvidenceStatus": "stale_native_mapping_evidence"} if stale else
               {"projectEvidenceStatus": "unbound_native_mapping_evidence"}
               if not {"sceneMappings", "technicalIndex"}.issubset(sources) else {}),
        }
        for task in artifact.get("tasks") or []
        for candidate in task.get("candidateComparisons") or []
    }


def _timing_index(artifact: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (row["taskId"], row["candidateId"]): row.get("plan") or {}
        for row in artifact.get("plans") or []
    }


def _assessment_rows(artifact: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not artifact:
        return []
    if "assessments" in artifact:
        return list(artifact.get("assessments") or [])
    # A single reviewed treatment-capacity assessment is also a valid source.
    return [artifact] if artifact.get("taskId") and artifact.get("candidateId") else []


def _assessment_index(artifact: dict[str, Any] | None) -> dict[tuple[str, str], dict[str, Any]]:
    rows = _assessment_rows(artifact)
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        key = (row.get("taskId"), row.get("candidateId"))
        if not all(key) or key in index:
            raise ValueError("treatment assessments require distinct task/candidate pairs")
        index[key] = {**row, "sources": row.get("sources") or artifact.get("sources") or {}}
    return index


def _candidate_fit(
    task: dict[str, Any], requirements: dict[str, Any], candidate: dict[str, Any],
    comparison: dict[str, Any] | None, timing_plan: dict[str, Any] | None,
    treatment: dict[str, Any] | None, catalog_record: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return an evidence verdict for one retrieved candidate, never a ranking."""
    cid = candidate["candidateId"]
    evidence: dict[str, Any] = {
        "technicalComparison": "present" if comparison else "missing",
        "timingPlan": "present" if timing_plan else "missing",
        "editorReviewedTreatment": bool(treatment and treatment.get("reviewState") == "editor_reviewed"),
        "nativeMappingEvidence": comparison.get("projectEvidenceStatus") if comparison else "missing",
    }
    gaps: list[dict[str, Any]] = []
    if comparison and comparison.get("projectEvidenceStatus") in {"stale_native_mapping_evidence", "unbound_native_mapping_evidence"}:
        return {
            "verdict": "unresolved", "candidateId": cid, "evidence": evidence,
            "gaps": [{"type": "current_native_mapping_evidence", "status": "unresolved",
                      "reason": "The comparison's native source binding is missing or stale."}],
        }
    exact = comparison.get("exactComposition") if comparison else None
    if not comparison or comparison.get("compositionMappingStatus") not in {"verified", "verified_window"} or not exact:
        capability = (catalog_record or {}).get("capability") or {}
        text = requirements.get("textRequirements") or {}
        media = requirements.get("mediaRequirements") or {}
        data = requirements.get("dataRequirements") or {}
        text_slots = capability.get("text_slots")
        required_text = text.get("requiredFieldCount")
        if not capability or text_slots is None:
            evidence["technicalBasis"] = "none"
            return {
                "verdict": "unresolved", "candidateId": cid, "evidence": evidence,
                "gaps": [{
                    "type": "exact_candidate_technical_comparison" if not comparison else "verified_exact_composition_mapping",
                    "status": "unresolved",
                }],
            }
        evidence.update({
            "technicalBasis": "catalog_family_capability",
            "catalogTextSlots": text_slots,
            "catalogMediaSlots": capability.get("media_slots"),
            "catalogSlotsAtOnce": capability.get("slots_at_once"),
        })
        if required_text is not None and text_slots < required_text:
            return {
                "verdict": "incompatible", "candidateId": cid, "evidence": evidence,
                "gaps": [{
                    "type": "family_text_capacity", "status": "failed",
                    "required": required_text, "available": text_slots,
                }],
            }
        gaps.append({
            "type": "exact_child_validation_deferred_until_use", "status": "conditional",
            "reason": "Family capability is recorded, but the exact child mapping, native controls and timing remain use-time checks.",
        })
        if media.get("status") in {"required", "missing_required_media"}:
            gaps.append({
                "type": "candidate_specific_media_slot_mapping", "status": "conditional",
                "reason": "Story focal counts are not template slot counts; the chosen child still needs an exact media-slot plan.",
            })
        if required_text:
            gaps.append({"type": "native_text_editability_and_layout", "status": "conditional"})
        if data.get("storyPresentationBinding") or data.get("requiredTypedFields"):
            gaps.append({"type": "native_typed_data_encoding", "status": "conditional"})
        return {"verdict": "conditional", "candidateId": cid, "evidence": evidence, "gaps": gaps}

    media = requirements.get("mediaRequirements") or {}
    text = requirements.get("textRequirements") or {}
    data = requirements.get("dataRequirements") or {}
    required_media = media.get("requiredSlotCount")
    required_text = text.get("requiredFieldCount")
    media_capacity = max(
        exact.get("maxSimultaneouslyEnabledRecursiveVisualInputs") or 0,
        exact.get("maxSimultaneouslyEnabledDirectInputs") or 0,
    )
    text_capacity = exact.get("maxSimultaneouslyEnabledRecursiveTextFields")
    if text_capacity is None:
        text_capacity = exact.get("recursiveEditableTextFields")
    deficits = []
    if required_media is not None and media_capacity < required_media:
        deficits.append({"type": "native_media_capacity", "required": required_media, "available": media_capacity})
    if required_text is not None and (text_capacity or 0) < required_text:
        deficits.append({"type": "native_text_capacity", "required": required_text, "available": text_capacity or 0})
    if deficits:
        return {
            "verdict": "incompatible", "candidateId": cid, "evidence": evidence,
            "gaps": [{**gap, "status": "failed"} for gap in deficits],
        }

    project_status = comparison.get("projectEvidenceStatus")
    unavailable = project_status == "static_source_bound_native_incompatible_with_ae25"
    if unavailable:
        gaps.append({
            "type": "native_project_availability", "status": "conditional",
            "reason": "The exact source requires a newer native host than the current AE installation.",
        })

    reviewed = treatment and treatment.get("reviewState") == "editor_reviewed"
    treatment_verdict = treatment.get("verdict") if reviewed else None
    if treatment_verdict in {"native_fit", "adapted_fit", "conditional", "incompatible"}:
        evidence["treatmentVerdict"] = treatment_verdict
        if treatment_verdict in {"native_fit", "adapted_fit"}:
            unclear = ((catalog_record or {}).get("capability") or {}).get("unclear") or []
            numeric_unknown = "numeric_text_controls:unresolved" in ((candidate.get("bindingProvenance") or {}).get("evidence") or [])
            if project_status == "unbound_native_mapping_evidence" or numeric_unknown or any("staging" in flag for flag in unclear):
                return {
                    "verdict": "unresolved", "candidateId": cid, "evidence": evidence,
                    "gaps": [{"type": "verified_native_controls_and_mapping", "status": "unresolved",
                              "reason": "Unbound native mapping, numeric-text controls or contradictory staging cannot certify qualitative fit."}],
                }
        if unavailable and treatment_verdict in {"native_fit", "adapted_fit"}:
            treatment_verdict = "conditional"
        return {
            "verdict": treatment_verdict, "candidateId": cid, "evidence": evidence,
            "gaps": gaps + list(treatment.get("unresolvedRequirements") or []),
        }

    typed_gaps = _template_gaps(requirements)
    if typed_gaps:
        deferred_types = {
            "task_required_media_slot_count": "candidate_specific_media_slot_mapping",
            "text_character_and_line_limits": "native_text_editability_and_layout",
            "task_required_data_fields": "native_typed_data_encoding",
        }
        if all(gap["type"] in deferred_types for gap in typed_gaps):
            deferred = [{
                **gap,
                "type": deferred_types[gap["type"]],
                "status": "conditional",
                "reason": gap.get("reason") or "Treatment-specific assignment is deferred until this exact child is used.",
            } for gap in typed_gaps]
            return {"verdict": "conditional", "candidateId": cid, "evidence": evidence, "gaps": deferred + gaps}
        return {"verdict": "unresolved", "candidateId": cid, "evidence": evidence, "gaps": typed_gaps + gaps}

    # Exact layer counts do not prove that a visual slot accepts a requested media
    # kind, that copy is readable at its required limits, or that typed data has a
    # native encoding. Those treatment-specific claims need reviewed evidence.
    if required_media and media.get("requiredMediaKinds"):
        gaps.append({"type": "media_kind_slot_compatibility", "status": "conditional"})
    if required_text:
        gaps.append({"type": "text_readability_with_required_limits", "status": "conditional"})
    if data.get("requiredTypedFields") or data.get("storyPresentationBinding"):
        gaps.append({"type": "native_typed_data_encoding", "status": "conditional"})
    if gaps and any(gap.get("status") in {"unresolved", "conditional"} for gap in gaps):
        return {"verdict": "conditional", "candidateId": cid, "evidence": evidence, "gaps": gaps}

    span = (requirements.get("timingRequirement") or {}).get("exactTaskAudioSpan") or {}
    task_duration = span.get("durationSeconds")
    native_duration = exact.get("durationSeconds")
    frame_rate = exact.get("frameRate") or 30.0
    exact_timing = (
        task_duration is not None and native_duration is not None
        and abs(task_duration - native_duration) <= 1.0 / frame_rate
    )
    if not exact_timing:
        status = (timing_plan or {}).get("status")
        if status in {"approved", "editor_approved"}:
            return {"verdict": "adapted_fit", "candidateId": cid, "evidence": evidence, "gaps": gaps}
        if status == "structurally_feasible_editorial_pacing_review_required":
            gaps.append({"type": "editorial_pacing_review", "status": "conditional"})
            return {"verdict": "conditional", "candidateId": cid, "evidence": evidence, "gaps": gaps}
        gaps.append({"type": "approved_timing_fit", "status": "unresolved"})
        return {"verdict": "unresolved", "candidateId": cid, "evidence": evidence, "gaps": gaps}
    if unavailable:
        return {"verdict": "conditional", "candidateId": cid, "evidence": evidence, "gaps": gaps}
    return {"verdict": "native_fit", "candidateId": cid, "evidence": evidence, "gaps": gaps}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode()).hexdigest()


RECONCILIATION_STAGES = ["source_contract_validation", "full_variant_discovery",
                         "candidate_treatment_reconciliation"]


def _requirement_specs(task: dict[str, Any], requirements: dict[str, Any], record: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Account for every source duty, without deriving additional Story meaning."""
    rows = []
    def visit(path, value):
        if isinstance(value, dict) and value:
            for key, item in sorted(value.items()):
                visit(path + "." + key, item)
        elif isinstance(value, list) and value:
            for index, item in enumerate(value):
                visit(f"{path}[{index}]", item)
        else:
            rows.append({"requirementId": path, "value": copy.deepcopy(value)})
    keys = ("primaryMeaning", "requiredMeanings", "primaryPresentationOperation",
            "presentationOperations", "routeDisposition", "relationships", "entityRefs",
            "entities", "quoteRequirements", "obligations", "mustBePerceptible", "values",
            "cohortRefs", "mediaNeeds", "cohortMediaNeeds", "dataNeeds", "continuity",
            "quote", "job", "taskRole", "sourceBeatJob", "sourceBeats")
    for key in keys:
        if key in task:
            visit("task." + key, task[key])
    if not task.get("primaryMeaning") and not task.get("primaryPresentationOperation"):
        visit("task.primaryMeaning", {"job": task.get("job"), "status": "legacy_unresolved"})
    for key in ("timingRequirement", "mediaRequirements", "textRequirements", "dataRequirements"):
        visit(key, requirements.get(key))
    visit("nativeMapping", "exact_current_candidate_mapping_required")
    visit("candidate.scopeRestriction", (record or {}).get("scope") or "unscoped")
    return rows


def _bound_treatment(treatment: dict[str, Any] | None, sources: dict[str, Any]) -> bool:
    if not treatment or treatment.get("reviewState") != "editor_reviewed":
        return False
    bindings = treatment.get("sources") or {}
    required = set(sources) - {"request", "treatmentAssessments", "priorReviewReconciliation"}
    return bool(required) and all(
        bindings.get(name, {}).get("sha256") == sources[name]["sha256"]
        and bindings.get(name, {}).get("path") == sources[name]["path"]
        for name in required)


def _reconcile_candidate(task, requirements, candidate, comparison, timing_plan,
                         treatment, record, sources):
    """Extend the existing fit evidence; native/review unknowns never mean exhaustion."""
    fit = _candidate_fit(task, requirements, candidate, comparison, timing_plan, treatment, record)
    current_native = bool(comparison and comparison.get("nativeSourceVerified") is True and comparison.get("projectEvidenceStatus") not in {
        "stale_native_mapping_evidence", "unbound_native_mapping_evidence",
        "static_source_bound_native_incompatible_with_ae25"}
        and comparison.get("compositionMappingStatus") == "verified"
        and comparison.get("exactComposition"))
    reviewed = _bound_treatment(treatment, sources)
    specs = _requirement_specs(task, requirements, record)
    duty_rows = []
    contract = matching.presentation_contract(task)
    exact = (comparison or {}).get("exactComposition") or {}
    for spec in specs:
        path, value = spec["requirementId"], spec["value"]
        status, basis = "unknown", "No current candidate-specific proof; source requirement retained."
        if path == "candidate.scopeRestriction":
            allowed = {"lyrics": "lyric_presentation", "timelines": "archival_progression"}
            if value == "unscoped":
                status, basis = "supported", "No scoped restriction supplied by the bound catalog record."
            elif value in allowed:
                required_operations = set(task.get("requiredMeanings") or task.get("presentationOperations") or ([task["primaryPresentationOperation"]] if task.get("primaryPresentationOperation") else []))
                if required_operations:
                    status = "supported" if required_operations <= {allowed[value]} else "conflict"
                    basis = "Existing scoped restriction permits only " + allowed[value]
        # An observed operation proves discovery compatibility, never complete fit.
        operation_path = path in {"task.primaryPresentationOperation", "task.primaryMeaning.operation"} or path.startswith(("task.requiredMeanings[", "task.presentationOperations["))
        if operation_path and isinstance(value, str):
            supports = matching._supports_operation(value, record or {}, contract)
            if supports and not any("unresolved" in flag for flag in supports):
                status, basis = "supported", "Existing structured operation evidence: " + ", ".join(supports)
            elif (record or {}).get("scope") and value not in {
                "lyric_presentation" if record["scope"] == "lyrics" else "archival_progression" if record["scope"] == "timelines" else None}:
                status, basis = "conflict", "Existing scoped restriction excludes this required operation."
        if current_native and path in {"mediaRequirements.requiredSlotCount", "textRequirements.requiredFieldCount"} and type(value) is int:
            capacity = (max(exact.get("maxSimultaneouslyEnabledRecursiveVisualInputs") or 0,
                            exact.get("maxSimultaneouslyEnabledDirectInputs") or 0)
                        if path.startswith("media") else exact.get("maxSimultaneouslyEnabledRecursiveTextFields", exact.get("recursiveEditableTextFields")))
            if capacity is not None:
                status = "supported" if capacity >= value else "conflict"
                basis = f"Current exact native simultaneous capacity {capacity}; required {value}."
        if path == "nativeMapping" and current_native:
            status, basis = "supported", "Current exact whole-composition mapping and technical comparison."
        # Reuse the established textual treatment assessment. A verdict alone is
        # not evidence for every duty, nor can it bypass an exact native deficit.
        data_unverified = path.startswith(("dataRequirements.requiredTypedFields", "dataRequirements.fieldVerification")) and "unknown" in (requirements.get("dataRequirements", {}).get("fieldVerification") or {}).values()
        source_unresolved = (path.endswith((".status", ".availabilityStatus")) and isinstance(value, str)
                             and value in {"unknown", "unresolved", "unverified", "legacy_unresolved"}) or ".unknown" in path
        source_unresolved = source_unresolved or (value is None and path.endswith(("requiredSlotCount", "requiredFieldCount", "exactTaskAudioSpan", "characterAndLineLimits", "requiredTypedFields")))
        if reviewed and current_native and status != "conflict" and not data_unverified and not source_unresolved:
            assessment = treatment.get("templateAssessment") or {}
            supported = [r for r in assessment.get("satisfied") or []
                         if r.get("requirement") == path and r.get("evidence")]
            if supported:
                status, basis = "supported", supported[0]["evidence"]
        duty_rows.append({**spec, "status": status, "evidence": basis})
    approved = list((treatment or {}).get("approvedAdjustments") or []) if reviewed and current_native else []
    method = (timing_plan or {}).get("method")
    permitted_adjustments = [name for name in approved if name == method and (timing_plan or {}).get("status") in {"approved", "editor_approved"}]
    permitted = {"approvedAdjustments": permitted_adjustments,
                 "unresolvedAdjustments": [name for name in approved if name not in permitted_adjustments],
                 "evaluation": "native_as_is" if not permitted_adjustments else "source_bound_reviewed_timing_plan",
                 "status": "supported" if reviewed and current_native and len(approved) == len(permitted_adjustments) else "unknown",
                 "basis": "Current task-bound reviewed existing treatment" if reviewed and current_native else "Evaluate native as-is only; no adjustment permission inferred."}
    statuses = {r["status"] for r in duty_rows}
    verdict = "incompatible" if "conflict" in statuses else "unresolved" if "unknown" in statuses else fit["verdict"]
    if verdict not in {"incompatible", "unresolved", "native_fit", "adapted_fit", "conditional"}:
        verdict = "unresolved"
    if verdict in {"native_fit", "adapted_fit"} and permitted["status"] != "supported":
        verdict = "unresolved"
    fit["evidence"].update({"discoveryFitVerdict": fit["verdict"],
                            "requirements": duty_rows, "permittedAdjustmentPlan": permitted,
                            "taskContract": copy.deepcopy(task),
                            "technicalRequirements": copy.deepcopy(requirements),
                            "taskSha256": _digest(task), "requirementsSha256": _digest(requirements),
                            "catalogRecordSha256": _digest(record),
                            "catalogRecord": copy.deepcopy(record),
                            "sourceBindings": copy.deepcopy(sources),
                            "assessmentComplete": True, "nativeFitUnknown": not current_native,
                            "customFallbackAuthorized": False, "catalogExhausted": False})
    fit["verdict"] = verdict
    fit["gaps"].extend({"type": r["requirementId"], "status": "unresolved" if r["status"] == "unknown" else "failed",
                        "reason": r["evidence"]} for r in duty_rows if r["status"] != "supported")
    return fit


def _reconciliation_body(artifact):
    receipt = (artifact.get("contractEnforcementReceipt") or {}).get("candidateReconciliation") or {}
    return {"sources": artifact.get("sources"), "consumerFingerprints": artifact.get("consumerFingerprints"),
            "tasks": artifact.get("tasks"), "counts": artifact.get("counts"),
            "discoveredVariants": receipt.get("discoveredVariants"), "discoveryLineage": receipt.get("discoveryLineage")}


def _validate_reconciliation(artifact):
    if artifact.get("fitValidated") is not False:
        raise ValueError("reconciliation completeness cannot certify all discovery choices as fit")
    receipt = (artifact.get("contractEnforcementReceipt") or {}).get("candidateReconciliation") or {}
    if (receipt.get("version") != "existing-batch-treatment-policy@1"
            or receipt.get("stages") != RECONCILIATION_STAGES
            or receipt.get("bodySha256") != _digest(_reconciliation_body(artifact))):
        raise ValueError("candidate reconciliation receipt missing, stale or stage-ordered incorrectly")
    for task in artifact["tasks"]:
        candidates = task["templateResult"]["candidates"]
        ids = [row["candidateId"] for row in candidates]
        if len(ids) != len(set(ids)) or receipt.get("discoveredVariants", {}).get(task["taskId"]) != ids:
            raise ValueError("candidate reconciliation omits discovered variants")
        for candidate in candidates:
            evidence = candidate["fitAssessment"]["evidence"]
            source_task = evidence.get("taskContract") or {}
            requirements = evidence.get("technicalRequirements") or {}
            specs = _requirement_specs(source_task, requirements, evidence.get("catalogRecord"))
            duties = evidence.get("requirements") or []
            if ([{k: row[k] for k in ("requirementId", "value")} for row in duties] != specs
                    or any(row.get("status") not in {"supported", "conflict", "unknown"} or not row.get("evidence") for row in duties)
                    or evidence.get("taskSha256") != _digest(source_task)
                    or evidence.get("requirementsSha256") != _digest(requirements)
                    or evidence.get("catalogRecordSha256") != _digest(evidence.get("catalogRecord"))
                    or evidence.get("sourceBindings") != artifact["sources"]):
                raise ValueError("candidate reconciliation duty/source coverage missing or stale")
            if evidence.get("catalogExhausted") is not False or evidence.get("customFallbackAuthorized") is not False:
                raise ValueError("reconciliation cannot authorize exhaustion or custom work")
            states = {row["status"] for row in duties}
            verdict = candidate["fitAssessment"]["verdict"]
            if (("conflict" in states and verdict != "incompatible") or
                    ("conflict" not in states and "unknown" in states and verdict != "unresolved")):
                raise ValueError("candidate reconciliation verdict does not preserve unknown/conflict")


def _template_result(
    task: dict[str, Any], requirements: dict[str, Any], bindings: dict[str, Any], pool: dict[str, Any],
    comparisons: dict[tuple[str, str], dict[str, Any]],
    timing_plans: dict[tuple[str, str], dict[str, Any]],
    assessments: dict[tuple[str, str], dict[str, Any]],
    sources: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidates = matching.template_candidates(task, bindings, pool, exhaustive_variants=True)
    gaps = _template_gaps(requirements)
    if not candidates:
        gaps.insert(0, {
            "type": "existing_template_candidate",
            "status": "missing",
            "matchingJob": task.get("job"),
            "reason": "The existing template consumer returned no candidate for this VisualTask.",
        })
        verdict = "no_candidate"
    else:
        for candidate in candidates:
            key = (task["id"], candidate["candidateId"])
            candidate["fitAssessment"] = _reconcile_candidate(
                task, requirements, candidate, comparisons.get(key), timing_plans.get(key),
                assessments.get(key), pool.get(candidate["candidateId"]), sources or {},
            )
        verdicts = {candidate["fitAssessment"]["verdict"] for candidate in candidates}
        if "native_fit" in verdicts:
            verdict = "native_fit"
        elif "adapted_fit" in verdicts:
            verdict = "adapted_fit"
        elif "conditional" in verdicts:
            verdict = "conditional"
        elif verdicts == {"incompatible"}:
            verdict = "incompatible"
        else:
            verdict = "unresolved"
    return {
        "fitVerdict": verdict,
        "candidateCount": len(candidates),
        "candidates": candidates,
        "gaps": gaps,
        "evidenceBoundary": "retrieval_is_candidate_discovery; fit_is_exact_evidence_comparison; neither_is_selection",
    }


def _media_kind(record: dict[str, Any]) -> str | None:
    return record.get("kind") or matching.M.kind_of(record)


def _source_specific_media(phrases: list[str], pool: dict[str, Any]) -> tuple[list[str], list[str]]:
    generic = {"broll", "footage", "artwork", "person", "image", "images"}
    usable = [phrase for phrase in phrases if matching.M.norm(phrase) not in generic]
    matches = []
    for asset_id, record in pool.items():
        evidence = [tag.get("tag", "") for tag in record.get("tags") or []]
        evidence.extend(record.get("captions") or [])
        if any(
            matching.M.norm(phrase) in matching.M.norm(value)
            for phrase in usable for value in evidence
        ):
            matches.append(asset_id)
    return usable, matches


def _media_result(task: dict[str, Any], requirements: dict[str, Any], pool: dict[str, Any]) -> dict[str, Any]:
    media = requirements.get("mediaRequirements") or {}
    typed_entities = media.get("requiredEntities")
    entities = list(typed_entities if isinstance(typed_entities, list) else (task.get("entities") or {}).get("displayEligible") or [])
    kinds = list(media.get("requiredMediaKinds") or [])
    unknown_kinds = sorted(set(kinds) - set(matching.M.MEDIA_KINDS))
    if unknown_kinds:
        return {
            "availabilityVerdict": "unavailable",
            "entities": entities,
            "groupCandidateIds": [],
            "individualCandidateIds": {},
            "gaps": [{
                "type": "production_ready_media_kind",
                "status": "missing",
                "mediaKind": kind,
                "reason": "The typed StoryPackage media kind has no corresponding kind in the current Production Ready consumer vocabulary.",
            } for kind in unknown_kinds],
            "candidateMatchingProvenance": {
                "scope": "visual_task",
                "taskId": task["id"],
                "quote": task.get("quote"),
                "resolver": "existing Production Ready media_candidates.resolve",
                "requiredMediaKinds": kinds,
            },
        }
    eligible_pool = pool
    if kinds:
        eligible_pool = {key: row for key, row in pool.items() if _media_kind(row) in kinds}
    provenance = {
        "scope": "visual_task",
        "taskId": task["id"],
        "quote": task.get("quote"),
        "resolver": "existing Production Ready media_candidates.resolve",
        "requiredMediaKinds": kinds,
    }
    reviewed_gap = media.get("missingMediaBrief")
    if reviewed_gap is not None:
        if (
            media.get("availabilityStatus") != "missing"
            or reviewed_gap.get("status") != "missing"
            or reviewed_gap.get("mediaKind") not in kinds
        ):
            raise ValueError(f"invalid typed missing-media brief: {task['id']}")
    if not entities:
        if kinds or media.get("status") == "required":
            phrases = list(media.get("storySourceSpecific") or [])
            queries, matches = _source_specific_media(phrases, eligible_pool)
            if queries:
                if matches:
                    return {
                        "availabilityVerdict": "available",
                        "entities": [], "groupCandidateIds": [], "individualCandidateIds": {},
                        "sourceSpecificCandidateIds": matches[:8], "gaps": [],
                        "candidateMatchingProvenance": {
                            **provenance,
                            "resolver": "existing Production Ready tags/captions with normalized contains matching",
                            "sourceSpecificQueries": queries,
                        },
                    }
                return {
                    "availabilityVerdict": "unavailable",
                    "entities": [], "groupCandidateIds": [], "individualCandidateIds": {},
                    "sourceSpecificCandidateIds": [],
                    "gaps": [{
                        "type": "source_specific_media", "status": "missing",
                        "requiredMediaKinds": kinds, "queries": queries,
                        "reason": "No Production Ready asset contains the exact source-specific phrase in its tags or captions.",
                    }],
                    "candidateMatchingProvenance": {
                        **provenance,
                        "resolver": "existing Production Ready tags/captions with normalized contains matching",
                        "sourceSpecificQueries": queries,
                    },
                }
            gap = reviewed_gap or {
                "type": "entity_or_non_entity_media_query",
                "status": "unresolved",
                "requiredMediaKinds": kinds,
                "reason": "The current Production Ready resolver is identity-based and this typed requirement has no required entity.",
            }
            return {
                "availabilityVerdict": "conditional" if reviewed_gap else "unresolved",
                "entities": [], "groupCandidateIds": [], "individualCandidateIds": {},
                "gaps": [gap], "candidateMatchingProvenance": provenance,
            }
        return {
            "availabilityVerdict": "not_required",
            "entities": [], "groupCandidateIds": [], "individualCandidateIds": {}, "gaps": [],
            "candidateMatchingProvenance": {**provenance, "reason": "No task-level media demand; sibling media is not inherited."},
        }
    resolved = matching.M.resolve(entities, pool=eligible_pool, kinds=kinds, quote=task.get("quote") or "")
    missing_entities = list(resolved.get("gaps") or [])
    gaps: list[Any] = []
    if reviewed_gap:
        gaps.append(reviewed_gap)
        verdict = "conditional"
    elif missing_entities:
        gaps.extend({
            "type": "required_entity_media",
            "status": "missing",
            "entity": entity,
            "requiredMediaKinds": kinds,
        } for entity in missing_entities)
        verdict = "unavailable"
    else:
        verdict = "available"
    return {
        "availabilityVerdict": verdict,
        "entities": entities,
        "groupCandidateIds": [row["id"] for row in (resolved.get("group") or [])[:8]],
        "individualCandidateIds": {
            entity: [row["id"] for row in rows[:8]]
            for entity, rows in (resolved.get("individual") or {}).items()
        },
        "slotsNeeded": resolved.get("slotsNeeded"),
        "gaps": gaps,
        "candidateMatchingProvenance": provenance,
    }


def build(request_path: Path) -> dict[str, Any]:
    contract_receipt = enforce_contracts("visualtask_batch_matching.build")
    request, paths, values = _load_inputs(request_path)
    tasks, requirements_by_id = _validate_scope(values)
    template_pool = {row["id"]: row for row in matching.C.load(content_class="*")}
    media_pool = matching.M.load()
    sources = {"request": _source(Path(request_path)), **{name: _source(path) for name, path in paths.items()}}
    comparisons = _comparison_index(values["technicalComparison"], sources)
    timing_plans = _timing_index(values["timingPlans"])
    assessments = _assessment_index(values.get("treatmentAssessments"))
    prior_admissions: dict[str, list[dict[str, Any]]] = {}
    for row in (values.get("priorReviewReconciliation") or {}).get("rows") or []:
        if row.get("state") != "prior_selected" or row.get("candidateId") not in template_pool:
            continue
        prior_admissions.setdefault(row["taskId"], []).append({
            "id": row["candidateId"],
            "source": "prior_editor_review_reconciliation",
            "sourceBeatId": row.get("sourceBeatId"),
            "sourceDisposition": row.get("sourceDisposition"),
            "technicalEvidenceVerdict": row.get("technicalEvidenceVerdict"),
            "reason": "The editor selected this existing candidate for this exact unsplit task's source beat.",
        })
    rows = []
    for task in tasks:
        task = copy.deepcopy(task)
        existing_admissions = list(task.get("templateAdmissions") or [])
        existing_ids = {row.get("id") for row in existing_admissions}
        task["templateAdmissions"] = existing_admissions + [
            row for row in prior_admissions.get(task["id"], [])
            if row["id"] not in existing_ids
        ]
        requirements = requirements_by_id[task["id"]]
        story_requirement = None
        if "storyMatchingHandoff" in values:
            handed = next(row for row in values["storyMatchingHandoff"]["tasks"] if row["taskId"] == task["id"])
            story_requirement = {
                "linkage": handed["linkage"],
                "media": {**handed["media"], "simultaneous": handed["media"]["focal"]["simultaneous"]},
                "text": {**handed["text"], "fieldCount": len(handed["text"]["fields"])},
                "data": handed["data"],
            }
        rows.append({
            "taskId": task["id"],
            "sourceBeatId": task.get("sourceBeatId"),
            "ordinal": task.get("ordinal"),
            "taskRole": task.get("taskRole"),
            "matchingJob": task.get("job"),
            "quote": task.get("quote"),
            "continuityGroup": task.get("continuityGroup"),
            "storyRequirements": story_requirement,
            "templateResult": _template_result(
                task, requirements, values["bindings"], template_pool,
                comparisons, timing_plans, assessments, sources,
            ),
            "mediaResult": _media_result(task, requirements, media_pool),
        })
    artifact = {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": SUPPORTED_SCHEMA_VERSION,
        "batchId": request["batchId"],
        "storyId": values["storyPackage"]["storyId"],
        "storyNamespace": values["storyPackage"]["namespace"],
        "purpose": "Review-only full-VisualTask template and media matching",
        "activationState": REVIEW_ONLY,
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "sources": sources,
        "consumerFingerprints": {
            "templatePool": _digest(template_pool),
            "productionReadyMediaPool": _digest(media_pool),
        },
        "counts": {
            "visualTasks": len(rows),
            "sourceBeats": len({row["sourceBeatId"] for row in rows}),
            "templateVerdicts": dict(sorted(Counter(row["templateResult"]["fitVerdict"] for row in rows).items())),
            "mediaVerdicts": dict(sorted(Counter(row["mediaResult"]["availabilityVerdict"] for row in rows).items())),
            "storyHandoffTasks": sum(row["storyRequirements"] is not None for row in rows),
        },
        "tasks": rows,
    }
    artifact["contractEnforcementReceipt"]["candidateReconciliation"] = {
        "version": "existing-batch-treatment-policy@1", "stages": RECONCILIATION_STAGES,
        "discoveredVariants": {row["taskId"]: [r["candidateId"] for r in row["templateResult"]["candidates"]] for row in rows},
        "discoveryLineage": {row["taskId"]: [
            {"candidateId": cid, "status": "supported" if cid in {r["candidateId"] for r in row["templateResult"]["candidates"]} else "unknown",
             "reason": "Discovered; candidate-specific duties reconciled below" if cid in {r["candidateId"] for r in row["templateResult"]["candidates"]} else "No primary-operation discovery evidence or binding; not a native-fit rejection or exhaustion",
             "catalogRecordSha256": _digest(record)} for cid, record in sorted(template_pool.items())]
            for row in rows},
    }
    artifact["contractEnforcementReceipt"]["candidateReconciliation"]["bodySha256"] = _digest(_reconciliation_body(artifact))
    artifact["fitValidated"] = False
    validate(artifact, verify_sources=False)
    return artifact


def validate(artifact: dict[str, Any], *, verify_sources: bool = True) -> None:
    _review_only(artifact, "batch match artifact")
    rows = artifact.get("tasks") or []
    ids = [row.get("taskId") for row in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ValueError("batch output requires distinct VisualTasks")
    template_verdicts = {
        "native_fit", "adapted_fit", "conditional", "incompatible", "unresolved", "no_candidate"
    }
    media_verdicts = {"not_required", "available", "conditional", "unavailable", "unresolved"}
    for row in rows:
        template = row.get("templateResult") or {}
        media = row.get("mediaResult") or {}
        if template.get("fitVerdict") not in template_verdicts:
            raise ValueError("invalid template-fit verdict")
        if media.get("availabilityVerdict") not in media_verdicts:
            raise ValueError("invalid media-availability verdict")
        for candidate in template.get("candidates") or []:
            provenance = candidate.get("candidateMatchingProvenance") or {}
            if provenance.get("scope") != "visual_task" or provenance.get("taskId") != row["taskId"]:
                raise ValueError("template candidate lacks VisualTask provenance")
            assessment = candidate.get("fitAssessment") or {}
            if assessment.get("candidateId") != candidate.get("candidateId"):
                raise ValueError("template candidate lacks candidate-bound fit assessment")
            if assessment.get("verdict") not in template_verdicts - {"no_candidate"}:
                raise ValueError("invalid candidate template-fit verdict")
        candidates = template.get("candidates") or []
        if not candidates:
            expected_template_verdict = "no_candidate"
        else:
            candidate_verdicts = {row["fitAssessment"]["verdict"] for row in candidates}
            if "native_fit" in candidate_verdicts:
                expected_template_verdict = "native_fit"
            elif "adapted_fit" in candidate_verdicts:
                expected_template_verdict = "adapted_fit"
            elif "conditional" in candidate_verdicts:
                expected_template_verdict = "conditional"
            elif candidate_verdicts == {"incompatible"}:
                expected_template_verdict = "incompatible"
            else:
                expected_template_verdict = "unresolved"
        if template.get("fitVerdict") != expected_template_verdict:
            raise ValueError("task template-fit verdict is stale")
        if any(key in template for key in ("selectedCandidateId", "selection", "approval")):
            raise ValueError("template-fit result cannot select or approve a candidate")
        provenance = media.get("candidateMatchingProvenance") or {}
        if provenance.get("scope") != "visual_task" or provenance.get("taskId") != row["taskId"]:
            raise ValueError("media result lacks VisualTask provenance")
        if media.get("availabilityVerdict") == "conditional":
            gaps = media.get("gaps") or []
            if not any(isinstance(gap, dict) and gap.get("status") == "missing" for gap in gaps):
                raise ValueError("conditional media verdict lacks typed missing gap")
    expected_counts = {
        "visualTasks": len(rows),
        "sourceBeats": len({row.get("sourceBeatId") for row in rows}),
        "templateVerdicts": dict(sorted(Counter(row["templateResult"]["fitVerdict"] for row in rows).items())),
        "mediaVerdicts": dict(sorted(Counter(row["mediaResult"]["availabilityVerdict"] for row in rows).items())),
        "storyHandoffTasks": sum(row.get("storyRequirements") is not None for row in rows),
    }
    if artifact.get("counts") != expected_counts:
        raise ValueError("batch match counts are stale")
    _validate_reconciliation(artifact)
    if verify_sources:
        for name, source in (artifact.get("sources") or {}).items():
            path = Path(source.get("path", ""))
            if not path.is_file() or _sha(path) != source.get("sha256"):
                raise ValueError(f"batch match source is missing or stale: {name}")
        replay = build(Path(artifact["sources"]["request"]["path"]))
        if dumps(replay) != dumps(artifact):
            raise ValueError("batch match does not replay from bound inputs")


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--request", required=True, type=Path)
    build_parser.add_argument("--output", required=True, type=Path)
    check_parser = sub.add_parser("validate")
    check_parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    if args.command == "build":
        artifact = build(args.request)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(dumps(artifact), encoding="utf-8")
        print(dumps(artifact), end="")
        return 0
    validate(_read(args.artifact))
    print("Full VisualTask batch matching passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
