#!/usr/bin/env python3
"""Build source-bound exact-window mapping proposals for aligned final timelines."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ae_template_technical_specs.derive_capacity import build_capacity, measure_composition_window
from .clip_technical_coverage import _semantic_rows


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REQUEST = ROOT / "clip-mapping-batches" / "batch-003" / "request.json"
DEFAULT_REPORT = ROOT / "reports" / "clip-mapping-batch-003.json"
DEFAULT_MAPPINGS = ROOT / "grammar" / "ae-scene-composition-mappings.json"
DEFAULT_WINDOWS = ROOT / "grammar" / "ae-scene-window-definitions.json"


def read(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def resolve(path: str) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _bound(source: dict[str, Any]) -> Path:
    path = resolve(source["path"])
    if not path.is_file() or sha(path) != source["sha256"]:
        raise ValueError(f"bound source missing or changed: {path}")
    return path


def _validate_native_render_receipt(
    family: dict[str, Any],
    paths: dict[str, Path],
    composition: dict[str, Any],
) -> dict[str, Any]:
    evidence = family["alignmentEvidence"]
    build_script = paths[evidence["buildScriptSource"]].read_text()
    build_report = read(paths[evidence["buildReportSource"]])
    render_report = read(paths[evidence["renderReportSource"]])
    rendered_video = paths[evidence["renderedVideoSource"]]
    expected_native = evidence["nativeCompositionSelector"]
    expected_review = evidence["reviewCompositionName"]
    if f'"main_comp": "{expected_native}"' not in build_script:
        raise ValueError(f"render build does not select native composition: {family['familyId']}")
    required_wrapper_code = (
        "addComp('AUTO REVIEW ' + main.name",
        "var mainLayer = c.layers.add(main);",
    )
    if any(fragment not in build_script for fragment in required_wrapper_code):
        raise ValueError(f"render build lacks transparent review wrapper: {family['familyId']}")
    duration = family["nativeDurationSeconds"]
    if build_report.get("mainComposition") != expected_review:
        raise ValueError(f"build receipt composition mismatch: {family['familyId']}")
    if abs(float(build_report.get("fullRenderDuration", -1)) - duration) > 1e-6:
        raise ValueError(f"build receipt duration mismatch: {family['familyId']}")
    if (
        render_report.get("status") != "complete"
        or render_report.get("rendered") is not True
        or render_report.get("mainComposition") != expected_review
        or abs(float(render_report.get("fullRenderDuration", -1)) - duration) > 1e-6
        or abs(float(render_report.get("renderedDuration", -1)) - duration) > 1e-6
        or Path(render_report.get("video", "")) != rendered_video
    ):
        raise ValueError(f"render receipt mismatch: {family['familyId']}")
    if composition["path"] != evidence["nativeCompositionPath"]:
        raise ValueError(f"receipt native composition path mismatch: {family['familyId']}")
    return {
        "mode": "native_render_receipt",
        "nativeCompositionSelector": expected_native,
        "reviewCompositionName": expected_review,
        "renderedVideoSha256": sha(rendered_video),
    }


def _validate_editor_checkpoints(
    family: dict[str, Any],
    paths: dict[str, Path],
    composition: dict[str, Any],
) -> dict[str, Any]:
    evidence = family["alignmentEvidence"]
    record = read(paths[evidence["checkpointSource"]])
    if (
        record.get("familyId") != family["familyId"]
        or record.get("projectId") != family["projectId"]
        or record.get("sourceProjectSha256") != family["sourceProjectSha256"]
        or record.get("compositionId") != family["compositionId"]
        or record.get("compositionPath") != family["compositionPath"]
        or record.get("evaluation") != "exact_match"
        or record.get("evaluatorRole") != "editor"
    ):
        raise ValueError(f"editor checkpoint identity mismatch: {family['familyId']}")
    checkpoints = record.get("checkpoints", [])
    times = [float(row["seconds"]) for row in checkpoints if row.get("result") == "exact_match"]
    duration = float(composition["durationSeconds"])
    if (
        len(times) < 2
        or len(times) != len(checkpoints)
        or times != sorted(set(times))
        or times[0] > duration * 0.25
        or times[-1] < duration * 0.75
        or any(value < 0 or value > duration for value in times)
    ):
        raise ValueError(f"editor checkpoints do not span timeline: {family['familyId']}")
    return {
        "mode": "editor_verified_checkpoints",
        "checkpointCount": len(times),
        "firstCheckpointSeconds": times[0],
        "lastCheckpointSeconds": times[-1],
    }


def _validate_master_child_anchors(
    family: dict[str, Any],
    registry: dict[str, dict[str, Any]],
    review_boundaries: dict[str, dict[str, Any]],
    raw: dict[str, Any],
) -> dict[str, Any]:
    """Prove a constant preview offset against verified child layers in one master."""
    evidence = family["alignmentEvidence"]
    anchors = family.get("anchors", [])
    if len(anchors) < 3:
        raise ValueError(f"master-child alignment needs at least three anchors: {family['familyId']}")
    raw_compositions = {row["id"]: row for row in raw["compositions"]}
    master = raw_compositions.get(family["compositionId"])
    if not master or master.get("path") != family["compositionPath"]:
        raise ValueError(f"master-child native master missing: {family['familyId']}")
    layers = [row for row in master.get("layers", []) if row.get("enabled", True)]
    child_bindings = {
        row["clipId"]: row for row in evidence.get("anchorChildBindings", [])
    }
    if set(child_bindings) != set(anchors):
        raise ValueError(f"master-child anchor bindings incomplete: {family['familyId']}")
    offset = float(evidence["previewToNativeOffsetSeconds"])
    tolerance = float(evidence.get("boundaryToleranceSeconds", 0.02))
    matched_edges = 0
    native_starts = []
    for clip_id in anchors:
        current = registry.get(clip_id)
        child = child_bindings[clip_id]
        boundary = review_boundaries.get(clip_id)
        if (
            not current
            or current.get("projectId") != family["projectId"]
            or current.get("status") not in {"verified", "verified_window"}
            or not boundary
        ):
            raise ValueError(f"master-child anchor missing: {clip_id}")
        current_is_child = (
            current.get("compositionId") == child["compositionId"]
            and current.get("compositionPath") == child["compositionPath"]
        )
        current_is_promoted_master = (
            clip_id in family.get("supersedeClipIds", [])
            and current.get("status") == "verified_window"
            and current.get("compositionId") == family["compositionId"]
            and current.get("compositionPath") == family["compositionPath"]
            and current.get("windowCapacityId") == clip_id
        )
        if not current_is_child and not current_is_promoted_master:
            raise ValueError(f"master-child anchor identity changed: {clip_id}")
        matches = [
            row for row in layers
            if row.get("sourceId") == child["compositionId"]
            and (row.get("sourcePath") or raw_compositions[row["sourceId"]]["path"]) == child["compositionPath"]
        ]
        if len(matches) != 1:
            raise ValueError(f"master-child anchor layer mismatch: {clip_id}")
        layer = matches[0]
        start = float(boundary["sourceStartSeconds"]) - offset
        end = float(boundary["sourceEndSeconds"]) - offset
        if start < float(layer["inPoint"]) - tolerance or end > float(layer["outPoint"]) + tolerance:
            raise ValueError(f"master-child anchor boundary mismatch: {clip_id}")
        edge_matches = sum((
            abs(start - float(layer["inPoint"])) <= tolerance,
            abs(end - float(layer["outPoint"])) <= tolerance,
        ))
        if not edge_matches:
            raise ValueError(f"master-child anchor does not prove preview offset: {clip_id}")
        matched_edges += edge_matches
        native_starts.append(start)
    target_boundaries = [review_boundaries.get(clip_id) for clip_id in family["targetClipIds"]]
    if any(row is None for row in target_boundaries):
        raise ValueError(f"master-child target boundary missing: {family['familyId']}")
    target_native_end = max(float(row["sourceEndSeconds"]) - offset for row in target_boundaries)
    if min(native_starts) > target_native_end * 0.25 or max(native_starts) < target_native_end * 0.75:
        raise ValueError(f"master-child anchors do not span timeline: {family['familyId']}")
    return {
        "mode": "verified_master_child_anchors",
        "anchorCount": len(anchors),
        "matchedBoundaryEdges": matched_edges,
        "previewToNativeOffsetSeconds": offset,
        "boundaryToleranceSeconds": tolerance,
    }


def _validate_mixed_master_timeline_anchors(
    family: dict[str, Any],
    registry: dict[str, dict[str, Any]],
    review_boundaries: dict[str, dict[str, Any]],
    raw: dict[str, Any],
) -> dict[str, Any]:
    """Validate one exact master-window anchor plus child anchors across a timeline."""
    evidence = family["alignmentEvidence"]
    raw_compositions = {row["id"]: row for row in raw["compositions"]}
    master = raw_compositions.get(family["compositionId"])
    if not master or master.get("path") != family["compositionPath"]:
        raise ValueError(f"mixed master timeline missing: {family['familyId']}")
    preview_duration = float(evidence["previewDurationSeconds"])
    duration_tolerance = float(evidence.get("durationToleranceSeconds", 0.03))
    native_duration = float(family["nativeDurationSeconds"])
    coverage_mode = evidence.get("previewCoverageMode", "full_duration")
    if coverage_mode == "full_duration":
        if abs(preview_duration - native_duration) > duration_tolerance:
            raise ValueError(f"mixed master preview duration mismatch: {family['familyId']}")
    elif coverage_mode == "truncated_prefix":
        maximum_tail = float(evidence["maximumTruncatedTailSeconds"])
        if preview_duration > native_duration + duration_tolerance or native_duration - preview_duration > maximum_tail:
            raise ValueError(f"mixed master truncated preview mismatch: {family['familyId']}")
    else:
        raise ValueError(f"unsupported mixed master preview coverage: {family['familyId']}")
    layers = [row for row in master.get("layers", []) if row.get("enabled", True)]
    child_bindings = {row["clipId"]: row for row in evidence.get("childAnchorBindings", [])}
    master_bindings = {row["clipId"]: row for row in evidence.get("masterWindowAnchorBindings", [])}
    anchors = set(family.get("anchors", []))
    minimum_anchor_count = max(2, int(evidence.get("minimumAnchorCount", 4)))
    if len(anchors) < minimum_anchor_count or not master_bindings or set(child_bindings) | set(master_bindings) != anchors:
        raise ValueError(f"mixed master anchor bindings incomplete: {family['familyId']}")
    if set(child_bindings) & set(master_bindings):
        raise ValueError(f"mixed master anchor binding overlap: {family['familyId']}")

    starts = []
    overlap_ratios = []
    for clip_id in family["anchors"]:
        current = registry.get(clip_id)
        boundary = review_boundaries.get(clip_id)
        if not current or current.get("projectId") != family["projectId"] or not boundary:
            raise ValueError(f"mixed master anchor missing: {clip_id}")
        promoted = (
            clip_id in family.get("supersedeClipIds", [])
            and current.get("status") == "verified_window"
            and current.get("compositionId") == family["compositionId"]
            and current.get("compositionPath") == family["compositionPath"]
            and current.get("windowCapacityId") == clip_id
        )
        binding = child_bindings.get(clip_id) or master_bindings.get(clip_id)
        original = (
            current.get("compositionId") == binding["compositionId"]
            and current.get("compositionPath") == binding["compositionPath"]
            and current.get("status") in {"verified", "verified_window"}
        )
        if not original and not promoted:
            raise ValueError(f"mixed master anchor identity changed: {clip_id}")
        matches = [
            row for row in layers
            if row.get("sourceId") == binding["compositionId"]
            and (row.get("sourcePath") or raw_compositions[row["sourceId"]]["path"]) == binding["compositionPath"]
        ]
        if len(matches) != 1:
            raise ValueError(f"mixed master child layer mismatch: {clip_id}")
        layer = matches[0]
        start = float(boundary["sourceStartSeconds"])
        end = min(float(boundary["sourceEndSeconds"]), float(family["nativeDurationSeconds"]))
        starts.append(start)
        if clip_id in master_bindings:
            unsupported_time_remap = layer.get("timeRemapEnabled") and not binding.get("linearTimeRemapVerified")
            if unsupported_time_remap or abs(float(layer.get("stretch", 100)) - 100) > 1e-6:
                raise ValueError(f"mixed master anchor transform unsupported: {clip_id}")
            local_start = float(binding["localStartSeconds"])
            local_end = float(binding["localEndSeconds"])
            parent_start = float(layer["startTime"])
            if abs(local_start + parent_start - start) > 0.02 or abs(local_end + parent_start - end) > 0.02:
                raise ValueError(f"mixed master exact window mismatch: {clip_id}")
        else:
            overlap = max(0.0, min(end, float(layer["outPoint"])) - max(start, float(layer["inPoint"])))
            ratio = overlap / (end - start)
            if ratio < float(evidence.get("minimumChildOverlapRatio", 0.7)):
                raise ValueError(f"mixed master child overlap too small: {clip_id}")
            overlap_ratios.append(ratio)
    late_fraction = float(evidence.get("minimumLateAnchorFraction", 0.75))
    if min(starts) > preview_duration * 0.1 or max(starts) < preview_duration * late_fraction:
        raise ValueError(f"mixed master anchors do not span timeline: {family['familyId']}")
    return {
        "mode": "verified_mixed_master_timeline_anchors",
        "anchorCount": len(anchors),
        "masterWindowAnchorCount": len(master_bindings),
        "childAnchorCount": len(child_bindings),
        "minimumObservedChildOverlapRatio": min(overlap_ratios) if overlap_ratios else None,
        "previewDurationSeconds": preview_duration,
        "previewCoverageMode": coverage_mode,
        "durationToleranceSeconds": duration_tolerance,
    }


def build_report(request: dict[str, Any]) -> dict[str, Any]:
    if request.get("activationState") != "reviewed_exact_window_batch":
        raise ValueError("window batch lacks reviewed exact-timeline evidence")
    if request.get("renderingAuthorized") is not False:
        raise ValueError("window batch cannot authorize rendering")
    paths = {name: _bound(row) for name, row in request["sources"].items()}
    review = read(paths["reviewCatalog"])
    approved = read(paths["approvedCatalog"])
    semantic = {row["clipId"]: row for row in _semantic_rows(review, approved)}
    review_boundaries = {row["id"]: row for row in review["scenes"]}
    scene_boundaries = {row["id"]: row for row in read(paths["sceneLibraryScenes"])}
    technical = read(paths["technicalIndex"])
    projects = {row["id"]: row for row in technical["projects"]}
    links = {row["familyId"]: row for row in read(paths["familyLinks"])["links"]}
    registry = {
        row["sceneId"]: row
        for row in read(resolve(request["registryPath"]))["mappings"]
    }

    proposals = []
    family_results = []
    seen: set[str] = set()
    for family in request["families"]:
        family_id = family["familyId"]
        project_id = family["projectId"]
        project = projects.get(project_id)
        link = links.get(family_id)
        if not project or not link or link["projectId"] != project_id:
            raise ValueError(f"family/project link mismatch: {family_id}")
        if project["sourceProjectSha256"] != family["sourceProjectSha256"]:
            raise ValueError(f"project source hash mismatch: {family_id}")
        compositions = {row["id"]: row for row in project["compositions"]}
        composition = compositions.get(family["compositionId"])
        if not composition or composition["path"] != family["compositionPath"]:
            raise ValueError(f"final composition missing: {family_id}")
        if abs(composition["durationSeconds"] - family["nativeDurationSeconds"]) > 1e-6:
            raise ValueError(f"native duration changed: {family_id}")
        raw = read(paths[family["nativeReportSource"]])
        if raw.get("sourceSha256") != project["sourceProjectSha256"]:
            raise ValueError(f"native report source mismatch: {family_id}")
        capacity = build_capacity(raw)

        anchors = family.get("anchors", [])
        alignment = family.get("alignmentEvidence", {"mode": "verified_anchors"})
        if alignment["mode"] == "verified_anchors":
            if len(anchors) < 2:
                raise ValueError(f"window family needs at least two verified anchors: {family_id}")
            for anchor in anchors:
                current = registry.get(anchor)
                if not current or current.get("projectId") != project_id:
                    raise ValueError(f"window anchor missing: {anchor}")
                if current.get("compositionId") != family["compositionId"] or current.get("compositionPath") != family["compositionPath"]:
                    raise ValueError(f"window anchor composition changed: {anchor}")
                if current.get("status") not in {"verified", "verified_window"}:
                    raise ValueError(f"window anchor not verified: {anchor}")
            alignment_result = {"mode": "verified_anchors", "anchorCount": len(anchors)}
        elif alignment["mode"] == "native_render_receipt":
            alignment_result = _validate_native_render_receipt(family, paths, composition)
        elif alignment["mode"] == "editor_verified_checkpoints":
            alignment_result = _validate_editor_checkpoints(family, paths, composition)
        elif alignment["mode"] == "verified_master_child_anchors":
            alignment_result = _validate_master_child_anchors(
                family,
                registry,
                review_boundaries,
                raw,
            )
        elif alignment["mode"] == "verified_mixed_master_timeline_anchors":
            semantic_family_ids = {
                clip_id for clip_id, row in semantic.items() if row["familyId"] == family_id
            }
            if set(family["targetClipIds"]) != semantic_family_ids:
                raise ValueError(f"mixed master batch does not cover complete semantic family: {family_id}")
            if family["boundarySource"] == "scene_library":
                mixed_boundaries = {
                    clip_id: {
                        "sourceStartSeconds": row["start"],
                        "sourceEndSeconds": row["end"],
                    }
                    for clip_id, row in scene_boundaries.items()
                }
            else:
                mixed_boundaries = review_boundaries
            alignment_result = _validate_mixed_master_timeline_anchors(
                family,
                registry,
                mixed_boundaries,
                raw,
            )
        else:
            raise ValueError(f"unsupported alignment evidence: {family_id}")

        family_proposals = []
        for clip_id in family["targetClipIds"]:
            if clip_id in seen:
                raise ValueError(f"duplicate target clip: {clip_id}")
            seen.add(clip_id)
            clip = semantic.get(clip_id)
            if not clip or clip["familyId"] != family_id:
                raise ValueError(f"target clip absent from semantic family: {clip_id}")
            if family["boundarySource"] == "scene_library":
                boundary = scene_boundaries.get(clip_id)
                if not boundary:
                    raise ValueError(f"scene-library boundary missing: {clip_id}")
                if alignment["mode"] == "native_render_receipt":
                    source_video = Path(boundary.get("source", ""))
                    rendered_video = paths[alignment["renderedVideoSource"]]
                    if (
                        boundary.get("origin") != "Our render"
                        or not source_video.is_file()
                        or sha(source_video) != sha(rendered_video)
                    ):
                        raise ValueError(f"scene boundary is not bound to native render: {clip_id}")
                start = round(float(boundary["start"]), 2)
                end = round(float(boundary["end"]), 2)
            elif family["boundarySource"] == "review_catalog":
                boundary = review_boundaries.get(clip_id)
                if not boundary:
                    raise ValueError(f"review boundary missing: {clip_id}")
                start = round(float(boundary["sourceStartSeconds"]), 2)
                end = round(float(boundary["sourceEndSeconds"]), 2)
            else:
                raise ValueError(f"unsupported boundary source: {family_id}")
            if alignment["mode"] == "verified_master_child_anchors":
                offset = float(alignment["previewToNativeOffsetSeconds"])
                start = round(start - offset, 2)
                end = round(end - offset, 2)
            overshoot = end - family["nativeDurationSeconds"]
            if overshoot > family["endClampToleranceSeconds"] + 1e-9:
                raise ValueError(f"clip exceeds native timeline: {clip_id}")
            end = min(end, family["nativeDurationSeconds"])
            if start < 0 or end <= start:
                raise ValueError(f"invalid exact window: {clip_id}")
            measured = measure_composition_window(
                capacity,
                composition_id=family["compositionId"],
                start_seconds=start,
                end_seconds=end,
            )
            proposal = {
                "clipId": clip_id,
                "familyId": family_id,
                "projectId": project_id,
                "status": "proposed_verified_window",
                "compositionId": family["compositionId"],
                "compositionPath": family["compositionPath"],
                "window": measured["window"],
                "nativeFacts": {
                    "durationSeconds": measured["window"]["durationSeconds"],
                    "absoluteMediaSlots": measured["totalIndependentVisualMediaInputs"],
                    "maxSimultaneouslyEnabledInputs": measured["maxSimultaneouslyEnabledRecursiveVisualInputs"],
                    "editableTextFields": len(measured["recursiveEditableTextFields"]),
                    "maxSimultaneouslyEnabledTextFields": measured["maxSimultaneouslyEnabledRecursiveTextFields"],
                },
            }
            current = registry.get(clip_id)
            if current:
                exact_match = (
                    current.get("projectId") == project_id
                    and current.get("compositionId") == family["compositionId"]
                    and current.get("compositionPath") == family["compositionPath"]
                    and current.get("status") in {"verified", "verified_window"}
                )
                allowed_supersession = (
                    alignment["mode"] in {
                        "native_render_receipt",
                        "editor_verified_checkpoints",
                        "verified_master_child_anchors",
                        "verified_mixed_master_timeline_anchors",
                    }
                    and clip_id in family.get("supersedeClipIds", [])
                    and current.get("projectId") == project_id
                    and current.get("status") in {"verified", "verified_window"}
                )
                if not exact_match and not allowed_supersession:
                    raise ValueError(f"target conflicts with registry: {clip_id}")
            proposals.append(proposal)
            family_proposals.append(proposal)
        family_result = {
            "familyId": family_id,
            "projectId": project_id,
            "boundarySource": family["boundarySource"],
            "anchorCount": len(anchors),
            "nativeDurationSeconds": family["nativeDurationSeconds"],
            "proposalCount": len(family_proposals),
            "proposals": family_proposals,
        }
        if "alignmentEvidence" in family:
            family_result["alignmentEvidence"] = alignment_result
        family_results.append(family_result)

    if set(request["targetClipIds"]) != seen or len(request["targetClipIds"]) != len(seen):
        raise ValueError("window batch target scope mismatch")
    summary = {
        "families": len(family_results),
        "anchors": sum(len(row.get("anchors", [])) for row in request["families"]),
        "exactWindows": len(proposals),
        "errors": 0,
    }
    native_render_receipts = sum(
        row.get("alignmentEvidence", {}).get("mode") == "native_render_receipt"
        for row in request["families"]
    )
    if native_render_receipts:
        summary["nativeRenderReceipts"] = native_render_receipts
    editor_checkpoint_families = sum(
        row.get("alignmentEvidence", {}).get("mode") == "editor_verified_checkpoints"
        for row in request["families"]
    )
    if editor_checkpoint_families:
        summary["editorVerifiedCheckpointFamilies"] = editor_checkpoint_families
    return {
        "schemaVersion": 1,
        "batchId": request["batchId"],
        "activationState": "reviewed_native_window_evidence",
        "renderingAuthorized": False,
        "sourceHashes": {name: row["sha256"] for name, row in request["sources"].items()},
        "summary": summary,
        "families": family_results,
        "proposals": proposals,
    }


def validate_report(report: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    if report != build_report(request):
        raise ValueError("saved window mapping report differs from deterministic rebuild")
    return report["summary"]


def activate_report(
    report: dict[str, Any],
    request: dict[str, Any],
    *,
    mappings_path: Path = DEFAULT_MAPPINGS,
    windows_path: Path = DEFAULT_WINDOWS,
) -> dict[str, int]:
    """Activate a validated batch as exact inspection-only registry windows."""
    validate_report(report, request)
    mappings_doc = read(mappings_path)
    windows_doc = read(windows_path)
    mapping_order = [row["sceneId"] for row in mappings_doc["mappings"]]
    window_order = [row["sceneId"] for row in windows_doc["windows"]]
    mappings = {row["sceneId"]: row for row in mappings_doc["mappings"]}
    windows = {row["sceneId"]: row for row in windows_doc["windows"]}
    raw_overrides = windows_doc.setdefault("rawReportOverrides", {})
    for family in request["families"]:
        source_key = family["nativeReportSource"]
        raw_overrides[family["projectId"]] = str(resolve(request["sources"][source_key]["path"]))
    batch_id = report["batchId"]
    alignment_modes = {
        row["familyId"]: row.get("alignmentEvidence", {}).get("mode")
        for row in report["families"]
    }
    for proposal in report["proposals"]:
        clip_id = proposal["clipId"]
        window = proposal["window"]
        if alignment_modes[proposal["familyId"]] == "native_render_receipt":
            alignment_text = "byte-hash bound to a completed native AE render of this final composition"
        elif alignment_modes[proposal["familyId"]] == "editor_verified_checkpoints":
            alignment_text = "bound to editor-verified native/preview checkpoints spanning this final composition"
        elif alignment_modes[proposal["familyId"]] == "verified_master_child_anchors":
            alignment_text = "bound by a constant preview offset to verified native child layers spanning this master composition"
        elif alignment_modes[proposal["familyId"]] == "verified_mixed_master_timeline_anchors":
            alignment_text = "bound to one exact native master-window anchor plus verified child layers spanning this master timeline"
        else:
            alignment_text = "bound to previously verified native timeline anchors"
        evidence = (
            f"The reviewed {window['startSeconds']:.2f}–{window['endSeconds']:.2f} second boundary "
            f"is {alignment_text}; exact window capacity and receipts are frozen in "
            f"reports/{batch_id}.json."
        )
        mappings[clip_id] = {
            "sceneId": clip_id,
            "projectId": proposal["projectId"],
            "status": "verified_window",
            "compositionId": proposal["compositionId"],
            "compositionPath": proposal["compositionPath"],
            "windowCapacityId": clip_id,
            "evidence": evidence,
        }
        if clip_id not in mapping_order:
            mapping_order.append(clip_id)
        windows[clip_id] = {
            "sceneId": clip_id,
            "projectId": proposal["projectId"],
            "compositionId": proposal["compositionId"],
            "compositionPath": proposal["compositionPath"],
            "startSeconds": window["startSeconds"],
            "endSeconds": window["endSeconds"],
            "evidence": evidence,
        }
        if clip_id not in window_order:
            window_order.append(clip_id)
    mappings_doc["scope"]["uniqueScenes"] = len(mappings)
    mappings_doc["mappings"] = [mappings[scene_id] for scene_id in mapping_order]
    windows_doc["windows"] = [windows[scene_id] for scene_id in window_order]
    mappings_path.write_text(json.dumps(mappings_doc, indent=2, ensure_ascii=False) + "\n")
    windows_path.write_text(json.dumps(windows_doc, indent=2, ensure_ascii=False) + "\n")
    return {"mappings": len(mappings), "windows": len(windows), "activated": len(report["proposals"])}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "validate", "activate"))
    parser.add_argument("--request", type=Path, default=DEFAULT_REQUEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    request = read(args.request)
    if args.command == "build":
        report = build_report(request)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(dumps(report))
        result = validate_report(report, request)
    else:
        report = read(args.output)
        result = activate_report(report, request) if args.command == "activate" else validate_report(report, request)
    print(dumps(result), end="")


if __name__ == "__main__":
    main()
