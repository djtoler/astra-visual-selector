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

        anchors = family["anchors"]
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
            if current and (
                current.get("projectId") != project_id
                or current.get("compositionId") != family["compositionId"]
                or current.get("compositionPath") != family["compositionPath"]
                or current.get("status") not in {"verified", "verified_window"}
            ):
                raise ValueError(f"target conflicts with registry: {clip_id}")
            proposals.append(proposal)
            family_proposals.append(proposal)
        family_results.append({
            "familyId": family_id,
            "projectId": project_id,
            "boundarySource": family["boundarySource"],
            "anchorCount": len(anchors),
            "nativeDurationSeconds": family["nativeDurationSeconds"],
            "proposalCount": len(family_proposals),
            "proposals": family_proposals,
        })

    if set(request["targetClipIds"]) != seen or len(request["targetClipIds"]) != len(seen):
        raise ValueError("window batch target scope mismatch")
    return {
        "schemaVersion": 1,
        "batchId": request["batchId"],
        "activationState": "reviewed_native_window_evidence",
        "renderingAuthorized": False,
        "sourceHashes": {name: row["sha256"] for name, row in request["sources"].items()},
        "summary": {
            "families": len(family_results),
            "anchors": sum(len(row["anchors"]) for row in request["families"]),
            "exactWindows": len(proposals),
            "errors": 0,
        },
        "families": family_results,
        "proposals": proposals,
    }


def validate_report(report: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    if report != build_report(request):
        raise ValueError("saved window mapping report differs from deterministic rebuild")
    return report["summary"]


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "validate"))
    parser.add_argument("--request", type=Path, default=DEFAULT_REQUEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    request = read(args.request)
    if args.command == "build":
        report = build_report(request)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(dumps(report))
    else:
        report = read(args.output)
    print(dumps(validate_report(report, request)), end="")


if __name__ == "__main__":
    main()
