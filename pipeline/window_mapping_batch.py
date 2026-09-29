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
                    alignment["mode"] == "native_render_receipt"
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
    batch_id = report["batchId"]
    for proposal in report["proposals"]:
        clip_id = proposal["clipId"]
        window = proposal["window"]
        evidence = (
            f"The reviewed {window['startSeconds']:.2f}–{window['endSeconds']:.2f} second boundary "
            "is byte-hash bound to a completed native AE render of this final composition; "
            f"exact window capacity and receipts are frozen in reports/{batch_id}.json."
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
