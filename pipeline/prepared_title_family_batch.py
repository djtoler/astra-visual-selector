#!/usr/bin/env python3
"""Prepare source-bound title-family window mappings without activating them."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ae_template_technical_specs.derive_capacity import build_capacity, measure_composition_window
from .clip_technical_coverage import _semantic_rows


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REQUEST = ROOT / "clip-mapping-batches" / "batch-016" / "request.json"
DEFAULT_REPORT = ROOT / "reports" / "clip-mapping-batch-016.json"
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


def _reachable_native_texts(
    composition_id: int,
    raw_compositions: dict[int, dict[str, Any]],
) -> set[str]:
    texts: set[str] = set()
    pending = [composition_id]
    visited: set[int] = set()
    while pending:
        current_id = pending.pop()
        if current_id in visited:
            continue
        visited.add(current_id)
        composition = raw_compositions.get(current_id)
        if not composition:
            continue
        for layer in composition.get("layers", []):
            text = layer.get("textField", {}).get("text")
            if isinstance(text, str) and text:
                texts.add(text.strip())
            source_id = layer.get("sourceId")
            if isinstance(source_id, int) and source_id in raw_compositions:
                pending.append(source_id)
    return texts


def _overlapping_children(
    master: dict[str, Any],
    *,
    allowed_ids: set[int],
    start: float,
    end: float,
) -> set[int]:
    return {
        int(layer["sourceId"])
        for layer in master.get("layers", [])
        if layer.get("enabled", True)
        and layer.get("sourceId") in allowed_ids
        and float(layer["inPoint"]) < end
        and float(layer["outPoint"]) > start
    }


def build_report(request: dict[str, Any]) -> dict[str, Any]:
    if request.get("activationState") != "reviewed_title_family_mapping_batch":
        raise ValueError("title family batch is not reviewed for activation")
    if request.get("preparationOnly") is not False or request.get("renderingAuthorized") is not False:
        raise ValueError("title family batch activation state is invalid")
    if request.get("familyBatchingAuthorization") != "editor_approved_family_batching_2026-09-30":
        raise ValueError("title family batching authorization missing")

    paths = {name: _bound(row) for name, row in request["sources"].items()}
    review = read(paths["reviewCatalog"])
    approved = read(paths["approvedCatalog"])
    semantic = {row["clipId"]: row for row in _semantic_rows(review, approved)}
    technical = read(paths["technicalIndex"])
    projects = {row["id"]: row for row in technical["projects"]}
    links = {row["familyId"]: row for row in read(paths["familyLinks"])["links"]}
    registry = {
        row["sceneId"]: row
        for row in read(resolve(request["registryPath"]))["mappings"]
    }

    proposals: list[dict[str, Any]] = []
    family_results: list[dict[str, Any]] = []
    claimed: set[str] = set()
    for family in request.get("windowFamilies", []):
        family_id = family["familyId"]
        project_id = family["projectId"]
        project = projects.get(project_id)
        link = links.get(family_id)
        if not project or not link or link["projectId"] != project_id:
            raise ValueError(f"family/project link mismatch: {family_id}")
        if project["sourceProjectSha256"] != family["sourceProjectSha256"]:
            raise ValueError(f"project source changed: {family_id}")
        if link["sourceProjectSha256"] != family["sourceProjectSha256"]:
            raise ValueError(f"family source link changed: {family_id}")

        raw = read(paths[family["nativeReportSource"]])
        if raw.get("sourceSha256") != family["sourceProjectSha256"]:
            raise ValueError(f"native report source changed: {family_id}")
        raw_compositions = {int(row["id"]): row for row in raw["compositions"]}
        master = raw_compositions.get(int(family["compositionId"]))
        if not master or master.get("path") != family["compositionPath"]:
            raise ValueError(f"native master changed: {family_id}")
        if abs(float(master["duration"]) - float(family["nativeDurationSeconds"])) > 1e-9:
            raise ValueError(f"native master duration changed: {family_id}")
        index_matches = [
            row for row in project["compositions"]
            if row["id"] == family["compositionId"] and row["path"] == family["compositionPath"]
        ]
        if len(index_matches) != 1:
            raise ValueError(f"technical master changed: {family_id}")

        family_semantic = {
            clip_id for clip_id, row in semantic.items() if row["familyId"] == family_id
        }
        windows = family.get("clipWindows", [])
        window_ids = [row["clipId"] for row in windows]
        if set(window_ids) != family_semantic or len(window_ids) != len(family_semantic):
            raise ValueError(f"title family window scope incomplete: {family_id}")
        allowed_ids = {int(value) for value in family["allowedChildCompositionIds"]}
        if any(value not in raw_compositions for value in allowed_ids):
            raise ValueError(f"title family child set changed: {family_id}")

        anchor_ids: set[str] = set()
        for anchor in family.get("sampleTextAnchors", []):
            clip_id = anchor["clipId"]
            child_id = int(anchor["compositionId"])
            native_text = str(anchor["nativeText"]).strip()
            if clip_id not in family_semantic or child_id not in allowed_ids:
                raise ValueError(f"invalid title-family text anchor: {family_id}:{clip_id}")
            if native_text not in _reachable_native_texts(child_id, raw_compositions):
                raise ValueError(f"native anchor text changed: {family_id}:{clip_id}")
            anchor_ids.add(clip_id)
        if len(anchor_ids) < int(family["minimumSampleTextAnchorCount"]):
            raise ValueError(f"insufficient title-family text anchors: {family_id}")

        capacity = build_capacity(raw)
        family_proposals = []
        for window in windows:
            clip_id = window["clipId"]
            if clip_id in claimed:
                raise ValueError(f"duplicate prepared title clip: {clip_id}")
            claimed.add(clip_id)
            start = float(window["startSeconds"])
            end = float(window["endSeconds"])
            if start < 0 or end <= start or end > float(master["duration"]) + 1e-9:
                raise ValueError(f"invalid title-family window: {clip_id}")
            expected_children = {int(value) for value in window["expectedChildCompositionIds"]}
            actual_children = _overlapping_children(
                master,
                allowed_ids=allowed_ids,
                start=start,
                end=end,
            )
            if actual_children != expected_children:
                raise ValueError(f"title-family child window changed: {clip_id}")
            clip = semantic[clip_id]
            expected_semantic = {
                "description": clip["semantic"].get("description"),
                "sourceStartSeconds": clip["semantic"].get("sourceStartSeconds"),
                "sourceEndSeconds": clip["semantic"].get("sourceEndSeconds"),
            }
            if window.get("semanticEvidence") != expected_semantic:
                raise ValueError(f"title-family semantic evidence changed: {clip_id}")
            measurement = measure_composition_window(
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
                "window": measurement["window"],
                "expectedChildCompositionIds": sorted(expected_children),
                "semanticEvidence": expected_semantic,
                "nativeFacts": {
                    "absoluteMediaSlots": measurement["totalIndependentVisualMediaInputs"],
                    "maxSimultaneouslyEnabledInputs": measurement["maxSimultaneouslyEnabledRecursiveVisualInputs"],
                    "editableTextFields": len(measurement["recursiveEditableTextFields"]),
                },
            }
            current = registry.get(clip_id)
            if current and not (
                current.get("status") == "verified_window"
                and current.get("projectId") == project_id
                and current.get("compositionId") == family["compositionId"]
                and current.get("compositionPath") == family["compositionPath"]
                and current.get("windowCapacityId") == clip_id
            ):
                raise ValueError(f"title family clip conflicts with activated registry: {clip_id}")
            family_proposals.append(proposal)
            proposals.append(proposal)
        family_results.append({
            "familyId": family_id,
            "projectId": project_id,
            "evidenceMode": family["evidenceMode"],
            "sampleTextAnchorCount": len(anchor_ids),
            "proposalCount": len(family_proposals),
            "proposals": family_proposals,
        })

    blocked_results = []
    for blocked in request.get("blockedFamilies", []):
        family_id = blocked["familyId"]
        project_id = blocked["projectId"]
        project = projects.get(project_id)
        link = links.get(family_id)
        if not project or not link or link["projectId"] != project_id:
            raise ValueError(f"blocked family/project link mismatch: {family_id}")
        if project["sourceProjectSha256"] != blocked["sourceProjectSha256"]:
            raise ValueError(f"blocked family source changed: {family_id}")
        raw = read(paths[blocked["nativeReportSource"]])
        if raw.get("sourceSha256") != blocked["sourceProjectSha256"]:
            raise ValueError(f"blocked native report source changed: {family_id}")
        family_semantic = {
            clip_id for clip_id, row in semantic.items() if row["familyId"] == family_id
        }
        unsafe = set(blocked.get("unsafeClipIds", []))
        if unsafe != family_semantic or unsafe & claimed:
            raise ValueError(f"blocked family scope incomplete: {family_id}")
        if not str(blocked.get("blocker", "")).strip() or not str(blocked.get("requiredEvidence", "")).strip():
            raise ValueError(f"blocked family explanation missing: {family_id}")
        blocked_results.append({
            "familyId": family_id,
            "projectId": project_id,
            "unsafeClipIds": sorted(unsafe),
            "blocker": blocked["blocker"],
            "requiredEvidence": blocked["requiredEvidence"],
        })

    return {
        "schemaVersion": 1,
        "batchId": request["batchId"],
        "activationState": "reviewed_title_family_mapping_evidence",
        "preparationOnly": False,
        "renderingAuthorized": False,
        "sourceHashes": {name: row["sha256"] for name, row in request["sources"].items()},
        "summary": {
            "windowFamilyCount": len(family_results),
            "proposedWindowCount": len(proposals),
            "blockedFamilyCount": len(blocked_results),
            "blockedClipCount": sum(len(row["unsafeClipIds"]) for row in blocked_results),
        },
        "families": family_results,
        "blockedFamilies": blocked_results,
        "proposals": proposals,
    }


def validate_report(report: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    if report != build_report(request):
        raise ValueError("saved title-family report differs from deterministic rebuild")
    return report["summary"]


def activate_report(
    report: dict[str, Any],
    request: dict[str, Any],
    *,
    mappings_path: Path = DEFAULT_MAPPINGS,
    windows_path: Path = DEFAULT_WINDOWS,
) -> dict[str, int]:
    """Activate reviewed exact title-family windows in the shared registries."""
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
            "The editor-authorized family batch binds this reviewed clip to an exact "
            "native master interval and its measured child compositions; exact evidence "
            f"is frozen in reports/{batch_id}.json."
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
        windows[clip_id] = {
            "sceneId": clip_id,
            "projectId": proposal["projectId"],
            "compositionId": proposal["compositionId"],
            "compositionPath": proposal["compositionPath"],
            "startSeconds": window["startSeconds"],
            "endSeconds": window["endSeconds"],
            "evidence": evidence,
        }
        if clip_id not in mapping_order:
            mapping_order.append(clip_id)
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
    else:
        report = read(args.output)
    result = activate_report(report, request) if args.command == "activate" else validate_report(report, request)
    print(dumps(result), end="")


if __name__ == "__main__":
    main()
