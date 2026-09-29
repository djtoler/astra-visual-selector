#!/usr/bin/env python3
"""Build and validate source-bound family-specific mapping batches."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .clip_technical_coverage import _semantic_rows


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REQUEST = ROOT / "clip-mapping-batches" / "batch-002" / "request.json"
DEFAULT_REPORT = ROOT / "reports" / "clip-mapping-batch-002.json"


def read(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def resolve(path: str) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _bound_source(source: dict[str, Any]) -> Path:
    path = resolve(source["path"])
    if not path.is_file():
        raise ValueError(f"bound source missing: {path}")
    actual = sha(path)
    if actual != source["sha256"]:
        raise ValueError(f"bound source changed: {path}: {actual}")
    return path


def _ordinal(pattern: str, value: str, label: str) -> int:
    match = re.fullmatch(pattern, value)
    if not match or "ordinal" not in match.groupdict():
        raise ValueError(f"{label} does not match ordinal pattern: {value}")
    return int(match.group("ordinal"))


def build_report(request: dict[str, Any]) -> dict[str, Any]:
    if request.get("activationState") != "reviewed_native_mapping_batch":
        raise ValueError("mapping batch lacks reviewed native evidence")
    if request.get("renderingAuthorized") is not False:
        raise ValueError("mapping batch cannot authorize rendering")
    source_paths = {
        name: _bound_source(source)
        for name, source in request["sources"].items()
    }
    review = read(source_paths["reviewCatalog"])
    approved = read(source_paths["approvedCatalog"])
    semantic = {row["clipId"]: row for row in _semantic_rows(review, approved)}
    technical_doc = read(source_paths["technicalIndex"])
    projects = {row["id"]: row for row in technical_doc["projects"]}
    link_doc = read(source_paths["familyLinks"])
    links = {row["familyId"]: row for row in link_doc["links"]}
    registry_doc = read(resolve(request["registryPath"]))
    registry = {row["sceneId"]: row for row in registry_doc["mappings"]}

    family_results = []
    all_proposals = []
    seen_targets: set[str] = set()
    for family in request["families"]:
        family_id = family["familyId"]
        project_id = family["projectId"]
        project = projects.get(project_id)
        if not project:
            raise ValueError(f"unknown project: {project_id}")
        link = links.get(family_id)
        if not link or link["projectId"] != project_id:
            raise ValueError(f"family/project link mismatch: {family_id}")
        if link["sourceProjectSha256"] != project["sourceProjectSha256"]:
            raise ValueError(f"family/project source hash mismatch: {family_id}")
        if family["sourceProjectSha256"] != project["sourceProjectSha256"]:
            raise ValueError(f"request project source hash mismatch: {family_id}")

        composition_by_ordinal = {}
        for composition in project["compositions"]:
            match = re.fullmatch(family["compositionPathPattern"], composition["path"])
            if match:
                ordinal = int(match.group("ordinal"))
                if ordinal in composition_by_ordinal:
                    raise ValueError(f"duplicate terminal ordinal: {family_id}:{ordinal}")
                composition_by_ordinal[ordinal] = composition

        anchors = family["anchors"]
        if len(anchors) < 2:
            raise ValueError(f"family needs at least two anchors: {family_id}")
        anchor_offsets = []
        for anchor in anchors:
            clip_id = anchor["clipId"]
            current = registry.get(clip_id)
            if not current or any(current.get(key) != anchor.get(key) for key in (
                "projectId", "status", "compositionId", "compositionPath"
            )):
                raise ValueError(f"anchor changed or missing: {clip_id}")
            clip_ordinal = _ordinal(family["clipIdPattern"], clip_id, "anchor clip")
            composition_ordinal = _ordinal(
                family["compositionPathPattern"], anchor["compositionPath"], "anchor composition"
            )
            if composition_by_ordinal.get(composition_ordinal, {}).get("id") != anchor["compositionId"]:
                raise ValueError(f"anchor composition absent from technical index: {clip_id}")
            anchor_offsets.append(composition_ordinal - clip_ordinal)
        if len(set(anchor_offsets)) != 1 or anchor_offsets[0] != family["ordinalOffset"]:
            raise ValueError(f"anchors do not establish requested offset: {family_id}")
        leave_one_out_errors = 0
        for index, anchor in enumerate(anchors):
            training_offsets = anchor_offsets[:index] + anchor_offsets[index + 1:]
            if not training_offsets or len(set(training_offsets)) != 1:
                leave_one_out_errors += 1
                continue
            clip_ordinal = _ordinal(family["clipIdPattern"], anchor["clipId"], "anchor clip")
            expected_ordinal = _ordinal(
                family["compositionPathPattern"], anchor["compositionPath"], "anchor composition"
            )
            if clip_ordinal + training_offsets[0] != expected_ordinal:
                leave_one_out_errors += 1
        if leave_one_out_errors:
            raise ValueError(f"leave-one-out anchor replay failed: {family_id}")

        raw_source_name = family["nativeReportSource"]
        raw = read(source_paths[raw_source_name])
        if raw.get("sourceSha256") != project["sourceProjectSha256"]:
            raise ValueError(f"native report source mismatch: {family_id}")
        raw_compositions = {row["id"]: row for row in raw["compositions"]}
        master = raw_compositions.get(family["masterCompositionId"])
        if not master or master.get("path") != family["masterCompositionPath"]:
            raise ValueError(f"native master missing: {family_id}")
        candidate_ids = {row["id"] for row in composition_by_ordinal.values()}
        master_layers = [
            layer for layer in master.get("layers", [])
            if layer.get("enabled", True) and layer.get("sourceId") in candidate_ids
        ]
        master_ordinals = []
        for layer in sorted(master_layers, key=lambda row: (row.get("inPoint", 0), row.get("index", 0))):
            path = raw_compositions[layer["sourceId"]]["path"]
            master_ordinals.append(_ordinal(family["compositionPathPattern"], path, "master child"))
        required_ordinals = sorted({
            _ordinal(family["clipIdPattern"], clip_id, "target clip") + family["ordinalOffset"]
            for clip_id in family["targetClipIds"]
        } | {
            _ordinal(family["clipIdPattern"], row["clipId"], "anchor clip") + family["ordinalOffset"]
            for row in anchors
        })
        if not set(required_ordinals).issubset(master_ordinals):
            raise ValueError(f"native master lacks required terminal compositions: {family_id}")
        if family.get("requireChronologicalOrder"):
            filtered = [ordinal for ordinal in master_ordinals if ordinal in required_ordinals]
            if filtered != sorted(filtered):
                raise ValueError(f"native master order contradicts rule: {family_id}")

        proposals = []
        for clip_id in family["targetClipIds"]:
            if clip_id in seen_targets:
                raise ValueError(f"duplicate target clip: {clip_id}")
            seen_targets.add(clip_id)
            clip = semantic.get(clip_id)
            if not clip or clip["familyId"] != family_id:
                raise ValueError(f"target absent from family semantic catalog: {clip_id}")
            ordinal = _ordinal(family["clipIdPattern"], clip_id, "target clip")
            composition_ordinal = ordinal + family["ordinalOffset"]
            composition = composition_by_ordinal.get(composition_ordinal)
            if not composition:
                raise ValueError(f"target composition absent: {clip_id}")
            proposal = {
                "clipId": clip_id,
                "familyId": family_id,
                "projectId": project_id,
                "status": "proposed_verified",
                "compositionId": composition["id"],
                "compositionPath": composition["path"],
                "nativeFacts": {
                    "durationSeconds": composition["durationSeconds"],
                    "absoluteMediaSlots": composition["totalIndependentVisualMediaInputs"],
                    "maxSimultaneouslyEnabledInputs": composition["maxSimultaneouslyEnabledRecursiveVisualInputs"],
                    "editableTextFields": composition["recursiveEditableTextFields"],
                },
            }
            current = registry.get(clip_id)
            if current and (
                current.get("status") != "verified"
                or current.get("projectId") != project_id
                or current.get("compositionId") != composition["id"]
                or current.get("compositionPath") != composition["path"]
            ):
                raise ValueError(f"target conflicts with registry: {clip_id}")
            proposals.append(proposal)
            all_proposals.append(proposal)
        family_results.append({
            "familyId": family_id,
            "projectId": project_id,
            "rule": {
                "ordinalOffset": family["ordinalOffset"],
                "anchorCount": len(anchors),
                "anchorOffsets": anchor_offsets,
                "leaveOneOutErrors": leave_one_out_errors,
                "nativeMasterCompositionId": family["masterCompositionId"],
                "nativeMasterCompositionPath": family["masterCompositionPath"],
                "requiredOrdinals": required_ordinals,
                "masterOrdinals": master_ordinals,
            },
            "proposalCount": len(proposals),
            "proposals": proposals,
        })

    expected_targets = request["targetClipIds"]
    if set(expected_targets) != seen_targets or len(expected_targets) != len(seen_targets):
        raise ValueError("batch target scope mismatch")
    return {
        "schemaVersion": 1,
        "batchId": request["batchId"],
        "activationState": "reviewed_native_mapping_evidence",
        "renderingAuthorized": False,
        "sourceHashes": {name: source["sha256"] for name, source in request["sources"].items()},
        "summary": {
            "families": len(family_results),
            "anchors": sum(len(row["anchors"]) for row in request["families"]),
            "proposals": len(all_proposals),
            "leaveOneOutErrors": 0,
            "nativeStructureErrors": 0,
        },
        "families": family_results,
        "proposals": all_proposals,
    }


def validate_report(report: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    expected = build_report(request)
    if report != expected:
        raise ValueError("saved family mapping report differs from deterministic rebuild")
    if report["summary"]["leaveOneOutErrors"] or report["summary"]["nativeStructureErrors"]:
        raise ValueError("mapping batch contains validation errors")
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
