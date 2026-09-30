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
DEFAULT_MAPPINGS = ROOT / "grammar" / "ae-scene-composition-mappings.json"


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


def _build_explicit_terminal_family(
    *,
    family: dict[str, Any],
    project: dict[str, Any],
    raw: dict[str, Any],
    semantic: dict[str, dict[str, Any]],
    registry: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Validate a complete one-to-one terminal set with explicit semantic bindings."""
    family_id = family["familyId"]
    project_id = family["projectId"]
    anchors = family["anchors"]
    targets = family["targetClipIds"]
    bindings = family.get("terminalBindings", [])
    if len(anchors) < 2:
        raise ValueError(f"family needs at least two anchors: {family_id}")
    if not bindings:
        raise ValueError(f"explicit terminal bindings missing: {family_id}")

    binding_by_clip: dict[str, dict[str, Any]] = {}
    binding_by_composition: dict[tuple[int, str], dict[str, Any]] = {}
    for binding in bindings:
        clip_id = binding["clipId"]
        composition_key = (binding["compositionId"], binding["compositionPath"])
        if clip_id in binding_by_clip or composition_key in binding_by_composition:
            raise ValueError(f"duplicate explicit terminal binding: {family_id}")
        if not str(binding.get("bindingEvidence", "")).strip():
            raise ValueError(f"explicit binding lacks evidence: {clip_id}")
        binding_by_clip[clip_id] = binding
        binding_by_composition[composition_key] = binding

    semantic_family_ids = {
        clip_id for clip_id, row in semantic.items() if row["familyId"] == family_id
    }
    anchor_ids = {row["clipId"] for row in anchors}
    requested_ids = anchor_ids | set(targets)
    if (
        set(binding_by_clip) != semantic_family_ids
        or requested_ids != semantic_family_ids
        or anchor_ids & set(targets)
    ):
        raise ValueError(f"batch does not cover exact semantic terminal set: {family_id}")

    pattern = family["terminalCompositionPathPattern"]
    technical_terminals = {
        (row["id"], row["path"]): row
        for row in project["compositions"]
        if re.fullmatch(pattern, row["path"])
    }
    if set(binding_by_composition) != set(technical_terminals):
        raise ValueError(f"technical index explicit terminal set changed: {family_id}")
    raw_compositions = {row["id"]: row for row in raw["compositions"]}
    for composition_id, composition_path in technical_terminals:
        raw_composition = raw_compositions.get(composition_id)
        if not raw_composition or raw_composition.get("path") != composition_path:
            raise ValueError(f"native report explicit terminal mismatch: {family_id}:{composition_id}")

    anchor_replay_errors = 0
    for anchor in anchors:
        clip_id = anchor["clipId"]
        binding = binding_by_clip.get(clip_id)
        current = registry.get(clip_id)
        expected = {
            "projectId": project_id,
            "status": anchor["status"],
            "compositionId": binding["compositionId"] if binding else None,
            "compositionPath": binding["compositionPath"] if binding else None,
        }
        if not binding or not current or any(current.get(key) != value for key, value in expected.items()):
            anchor_replay_errors += 1
    if anchor_replay_errors:
        raise ValueError(f"explicit terminal anchor replay failed: {family_id}")

    proposals = []
    for clip_id in targets:
        clip = semantic.get(clip_id)
        binding = binding_by_clip[clip_id]
        if not clip or clip["familyId"] != family_id:
            raise ValueError(f"target absent from family semantic catalog: {clip_id}")
        composition = technical_terminals[(binding["compositionId"], binding["compositionPath"])]
        proposal = {
            "clipId": clip_id,
            "familyId": family_id,
            "projectId": project_id,
            "status": "proposed_verified",
            "compositionId": composition["id"],
            "compositionPath": composition["path"],
            "bindingEvidence": binding["bindingEvidence"],
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

    return ({
        "familyId": family_id,
        "projectId": project_id,
        "rule": {
            "nativeEvidence": {
                "mode": "explicit_terminal_set",
                "terminalCompositionCount": len(technical_terminals),
            },
            "anchorCount": len(anchors),
            "anchorReplayErrors": anchor_replay_errors,
            "bindingCount": len(bindings),
        },
        "proposalCount": len(proposals),
        "proposals": proposals,
    }, proposals)


def _build_source_bound_explicit_family(
    *,
    family: dict[str, Any],
    project: dict[str, Any],
    raw: dict[str, Any],
    semantic: dict[str, dict[str, Any]],
    registry: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Validate explicit clip bindings while preserving declared family exceptions.

    This mode is for source-bound families whose usable semantic subset does not
    form a simple ordinal terminal set. Every included clip has a direct native
    binding; omitted semantic clips must be named and explained. Shared native
    terminals fail closed unless the exact composition is explicitly allowed.
    """
    family_id = family["familyId"]
    project_id = family["projectId"]
    anchors = family["anchors"]
    targets = family["targetClipIds"]
    bindings = family.get("terminalBindings", [])
    exceptions = family.get("semanticExceptions", [])
    if not anchors:
        raise ValueError(f"source-bound family needs at least one anchor: {family_id}")
    if not bindings:
        raise ValueError(f"source-bound explicit bindings missing: {family_id}")

    semantic_family_ids = {
        clip_id for clip_id, row in semantic.items() if row["familyId"] == family_id
    }
    exception_ids: set[str] = set()
    for exception in exceptions:
        clip_id = exception.get("clipId")
        if clip_id in exception_ids or clip_id not in semantic_family_ids:
            raise ValueError(f"invalid source-bound semantic exception: {family_id}:{clip_id}")
        if not str(exception.get("reason", "")).strip():
            raise ValueError(f"source-bound semantic exception lacks reason: {clip_id}")
        exception_ids.add(clip_id)

    anchor_ids = {row["clipId"] for row in anchors}
    requested_ids = anchor_ids | set(targets)
    if anchor_ids & set(targets):
        raise ValueError(f"source-bound anchors overlap targets: {family_id}")
    if requested_ids & exception_ids or requested_ids | exception_ids != semantic_family_ids:
        raise ValueError(f"source-bound family scope is incomplete: {family_id}")

    pattern = family["terminalCompositionPathPattern"]
    technical_terminals = {
        (row["id"], row["path"]): row
        for row in project["compositions"]
        if re.fullmatch(pattern, row["path"])
    }
    raw_compositions = {row["id"]: row for row in raw["compositions"]}
    binding_by_clip: dict[str, dict[str, Any]] = {}
    composition_to_clips: dict[tuple[int, str], list[str]] = {}
    for binding in bindings:
        clip_id = binding["clipId"]
        key = (binding["compositionId"], binding["compositionPath"])
        if clip_id in binding_by_clip or clip_id not in requested_ids:
            raise ValueError(f"invalid source-bound explicit binding: {family_id}:{clip_id}")
        if not str(binding.get("bindingEvidence", "")).strip():
            raise ValueError(f"source-bound explicit binding lacks evidence: {clip_id}")
        composition = technical_terminals.get(key)
        raw_composition = raw_compositions.get(binding["compositionId"])
        if not composition or not raw_composition or raw_composition.get("path") != binding["compositionPath"]:
            raise ValueError(f"source-bound terminal changed: {family_id}:{clip_id}")
        binding_by_clip[clip_id] = binding
        composition_to_clips.setdefault(key, []).append(clip_id)
    if set(binding_by_clip) != requested_ids:
        raise ValueError(f"source-bound bindings do not cover included clips: {family_id}")

    declared_shared = {
        (row["compositionId"], row["compositionPath"]): set(row["clipIds"])
        for row in family.get("allowedSharedTerminalBindings", [])
    }
    actual_shared = {
        key: set(clip_ids)
        for key, clip_ids in composition_to_clips.items()
        if len(clip_ids) > 1
    }
    if actual_shared != declared_shared:
        raise ValueError(f"source-bound shared terminal declarations differ: {family_id}")
    if family.get("requireCompleteTerminalCoverage") is True:
        if set(composition_to_clips) != set(technical_terminals):
            raise ValueError(f"source-bound terminal coverage is incomplete: {family_id}")

    anchor_replay_errors = 0
    for anchor in anchors:
        clip_id = anchor["clipId"]
        binding = binding_by_clip.get(clip_id)
        current = registry.get(clip_id)
        expected = {
            "projectId": project_id,
            "status": anchor["status"],
            "compositionId": binding["compositionId"] if binding else None,
            "compositionPath": binding["compositionPath"] if binding else None,
        }
        if not binding or not current or any(current.get(key) != value for key, value in expected.items()):
            anchor_replay_errors += 1
    if anchor_replay_errors:
        raise ValueError(f"source-bound explicit anchor replay failed: {family_id}")

    proposals = []
    for clip_id in targets:
        binding = binding_by_clip[clip_id]
        composition = technical_terminals[(binding["compositionId"], binding["compositionPath"])]
        proposal = {
            "clipId": clip_id,
            "familyId": family_id,
            "projectId": project_id,
            "status": "proposed_verified",
            "compositionId": composition["id"],
            "compositionPath": composition["path"],
            "bindingEvidence": binding["bindingEvidence"],
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

    return ({
        "familyId": family_id,
        "projectId": project_id,
        "rule": {
            "nativeEvidence": {
                "mode": "source_bound_explicit_bindings",
                "terminalCompositionCount": len(technical_terminals),
                "completeTerminalCoverageRequired": family.get("requireCompleteTerminalCoverage") is True,
            },
            "anchorCount": len(anchors),
            "anchorReplayErrors": anchor_replay_errors,
            "bindingCount": len(bindings),
            "semanticExceptionCount": len(exceptions),
            "sharedTerminalCount": len(actual_shared),
        },
        "proposalCount": len(proposals),
        "proposals": proposals,
    }, proposals)


def _reachable_native_texts(
    composition_id: int,
    raw_compositions: dict[int, dict[str, Any]],
) -> set[str]:
    """Collect native text values recursively reachable from a terminal."""
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
                texts.add(text)
            source_id = layer.get("sourceId")
            if isinstance(source_id, int) and source_id in raw_compositions:
                pending.append(source_id)
    return texts


def _build_prepared_exact_terminal_family(
    *,
    family: dict[str, Any],
    project: dict[str, Any],
    raw: dict[str, Any],
    semantic: dict[str, dict[str, Any]],
    registry: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Validate a complete, unactivated terminal binding set clip by clip."""
    family_id = family["familyId"]
    project_id = family["projectId"]
    targets = family["targetClipIds"]
    bindings = family.get("terminalBindings", [])
    if not bindings:
        raise ValueError(f"prepared exact terminal bindings missing: {family_id}")

    semantic_family_ids = {
        clip_id for clip_id, row in semantic.items() if row["familyId"] == family_id
    }
    binding_by_clip: dict[str, dict[str, Any]] = {}
    binding_by_composition: dict[tuple[int, str], dict[str, Any]] = {}
    for binding in bindings:
        clip_id = binding["clipId"]
        key = (binding["compositionId"], binding["compositionPath"])
        if clip_id in binding_by_clip or key in binding_by_composition:
            raise ValueError(f"duplicate prepared exact terminal binding: {family_id}")
        if not str(binding.get("bindingEvidence", "")).strip():
            raise ValueError(f"prepared exact binding lacks evidence: {clip_id}")
        binding_by_clip[clip_id] = binding
        binding_by_composition[key] = binding
    if (
        set(targets) != semantic_family_ids
        or len(targets) != len(semantic_family_ids)
        or set(binding_by_clip) != semantic_family_ids
    ):
        raise ValueError(f"prepared exact semantic scope is incomplete: {family_id}")

    pattern = family["terminalCompositionPathPattern"]
    technical_terminals = {
        (row["id"], row["path"]): row
        for row in project["compositions"]
        if re.fullmatch(pattern, row["path"])
    }
    if set(binding_by_composition) != set(technical_terminals):
        raise ValueError(f"prepared exact technical terminal set changed: {family_id}")
    raw_compositions = {row["id"]: row for row in raw["compositions"]}
    for composition_id, composition_path in technical_terminals:
        native = raw_compositions.get(composition_id)
        if not native or native.get("path") != composition_path:
            raise ValueError(f"prepared exact native terminal changed: {family_id}:{composition_id}")

    proposals = []
    for clip_id in targets:
        binding = binding_by_clip[clip_id]
        clip = semantic[clip_id]
        expected_semantic = {
            "description": clip["semantic"].get("description"),
            "sourceStartSeconds": clip["semantic"].get("sourceStartSeconds"),
            "sourceEndSeconds": clip["semantic"].get("sourceEndSeconds"),
        }
        if binding.get("semanticEvidence") != expected_semantic:
            raise ValueError(f"prepared exact semantic evidence changed: {clip_id}")

        evidence_type = binding.get("bindingEvidenceType")
        if evidence_type == "ordinal_labeled_terminal":
            clip_ordinal = _ordinal(family["clipIdPattern"], clip_id, "prepared exact clip")
            composition_ordinal = _ordinal(
                family["compositionOrdinalPattern"],
                binding["compositionPath"],
                "prepared exact composition",
            )
            if composition_ordinal != clip_ordinal + family.get("ordinalOffset", 0):
                raise ValueError(f"prepared exact ordinal mismatch: {clip_id}")
        elif evidence_type == "visible_sample_text":
            native_text = binding.get("nativeText")
            if not isinstance(native_text, str) or not native_text:
                raise ValueError(f"prepared exact native text missing: {clip_id}")
            if binding.get("previewVisibleText") != native_text:
                raise ValueError(f"prepared exact visible text mismatch: {clip_id}")
            if native_text not in _reachable_native_texts(binding["compositionId"], raw_compositions):
                raise ValueError(f"prepared exact native text not reachable: {clip_id}")
        else:
            raise ValueError(f"unsupported prepared exact evidence type: {clip_id}")

        composition = technical_terminals[(binding["compositionId"], binding["compositionPath"])]
        current = registry.get(clip_id)
        if current and (
            current.get("status") != "verified"
            or current.get("projectId") != project_id
            or current.get("compositionId") != composition["id"]
            or current.get("compositionPath") != composition["path"]
        ):
            raise ValueError(f"prepared exact target conflicts with registry: {clip_id}")
        proposals.append({
            "clipId": clip_id,
            "familyId": family_id,
            "projectId": project_id,
            "status": "proposed_verified",
            "compositionId": composition["id"],
            "compositionPath": composition["path"],
            "bindingEvidenceType": evidence_type,
            "bindingEvidence": binding["bindingEvidence"],
            "semanticEvidence": expected_semantic,
            "nativeFacts": {
                "durationSeconds": composition["durationSeconds"],
                "absoluteMediaSlots": composition["totalIndependentVisualMediaInputs"],
                "maxSimultaneouslyEnabledInputs": composition["maxSimultaneouslyEnabledRecursiveVisualInputs"],
                "editableTextFields": composition["recursiveEditableTextFields"],
            },
        })

    return ({
        "familyId": family_id,
        "projectId": project_id,
        "rule": {
            "nativeEvidence": {
                "mode": "prepared_exact_terminal_bindings",
                "terminalCompositionCount": len(technical_terminals),
            },
            "anchorCount": 0,
            "bindingCount": len(bindings),
            "semanticEvidenceReplayErrors": 0,
            "nativeEvidenceReplayErrors": 0,
        },
        "proposalCount": len(proposals),
        "proposals": proposals,
    }, proposals)


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

        evidence_mode = family.get("nativeEvidenceMode", "master_timeline")
        if evidence_mode == "prepared_exact_terminal_bindings":
            if (
                request.get("preparationOnly") is not False
                or request.get("familyBatchingAuthorization")
                != "editor_approved_family_batching_2026-09-30"
            ):
                raise ValueError(f"exact terminal family batching is not authorized: {family_id}")
            if family.get("anchors") != []:
                raise ValueError(f"prepared exact terminal family cannot claim anchors: {family_id}")
            raw = read(source_paths[family["nativeReportSource"]])
            if raw.get("sourceSha256") != project["sourceProjectSha256"]:
                raise ValueError(f"native report source mismatch: {family_id}")
            result, proposals = _build_prepared_exact_terminal_family(
                family=family,
                project=project,
                raw=raw,
                semantic=semantic,
                registry=registry,
            )
            for proposal in proposals:
                if proposal["clipId"] in seen_targets:
                    raise ValueError(f"duplicate target clip: {proposal['clipId']}")
                seen_targets.add(proposal["clipId"])
            family_results.append(result)
            all_proposals.extend(proposals)
            continue
        if evidence_mode == "source_bound_explicit_bindings":
            raw = read(source_paths[family["nativeReportSource"]])
            if raw.get("sourceSha256") != project["sourceProjectSha256"]:
                raise ValueError(f"native report source mismatch: {family_id}")
            result, proposals = _build_source_bound_explicit_family(
                family=family,
                project=project,
                raw=raw,
                semantic=semantic,
                registry=registry,
            )
            for proposal in proposals:
                if proposal["clipId"] in seen_targets:
                    raise ValueError(f"duplicate target clip: {proposal['clipId']}")
                seen_targets.add(proposal["clipId"])
            family_results.append(result)
            all_proposals.extend(proposals)
            continue
        if evidence_mode == "explicit_terminal_set":
            raw = read(source_paths[family["nativeReportSource"]])
            if raw.get("sourceSha256") != project["sourceProjectSha256"]:
                raise ValueError(f"native report source mismatch: {family_id}")
            result, proposals = _build_explicit_terminal_family(
                family=family,
                project=project,
                raw=raw,
                semantic=semantic,
                registry=registry,
            )
            for proposal in proposals:
                if proposal["clipId"] in seen_targets:
                    raise ValueError(f"duplicate target clip: {proposal['clipId']}")
                seen_targets.add(proposal["clipId"])
            family_results.append(result)
            all_proposals.extend(proposals)
            continue

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
        required_ordinals = sorted({
            _ordinal(family["clipIdPattern"], clip_id, "target clip") + family["ordinalOffset"]
            for clip_id in family["targetClipIds"]
        } | {
            _ordinal(family["clipIdPattern"], row["clipId"], "anchor clip") + family["ordinalOffset"]
            for row in anchors
        })
        native_evidence = {"mode": evidence_mode}
        if evidence_mode == "master_timeline":
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
            if not set(required_ordinals).issubset(master_ordinals):
                raise ValueError(f"native master lacks required terminal compositions: {family_id}")
            if family.get("requireChronologicalOrder"):
                filtered = [ordinal for ordinal in master_ordinals if ordinal in required_ordinals]
                if filtered != sorted(filtered):
                    raise ValueError(f"native master order contradicts rule: {family_id}")
            native_evidence.update({
                "masterCompositionId": family["masterCompositionId"],
                "masterCompositionPath": family["masterCompositionPath"],
                "masterOrdinals": master_ordinals,
            })
        elif evidence_mode == "exact_terminal_set":
            expected = family.get("expectedTerminalOrdinals")
            if expected != sorted(set(expected or [])) or not expected:
                raise ValueError(f"invalid exact terminal ordinal set: {family_id}")
            if sorted(composition_by_ordinal) != expected:
                raise ValueError(f"technical index terminal set changed: {family_id}")
            if required_ordinals != expected:
                raise ValueError(f"batch does not cover exact terminal set: {family_id}")
            for ordinal, composition in composition_by_ordinal.items():
                raw_composition = raw_compositions.get(composition["id"])
                if not raw_composition or raw_composition.get("path") != composition["path"]:
                    raise ValueError(f"native report terminal mismatch: {family_id}:{ordinal}")
            native_evidence["terminalOrdinals"] = expected
        else:
            raise ValueError(f"unsupported native evidence mode: {family_id}:{evidence_mode}")

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
        rule = {
            "ordinalOffset": family["ordinalOffset"],
            "anchorCount": len(anchors),
            "anchorOffsets": anchor_offsets,
            "leaveOneOutErrors": leave_one_out_errors,
            "requiredOrdinals": required_ordinals,
        }
        if evidence_mode == "master_timeline":
            rule.update({
                "nativeMasterCompositionId": family["masterCompositionId"],
                "nativeMasterCompositionPath": family["masterCompositionPath"],
                "masterOrdinals": native_evidence["masterOrdinals"],
            })
        else:
            rule["nativeEvidence"] = native_evidence
        family_results.append({
            "familyId": family_id,
            "projectId": project_id,
            "rule": rule,
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


def activate_report(
    report: dict[str, Any],
    request: dict[str, Any],
    *,
    mappings_path: Path = DEFAULT_MAPPINGS,
) -> dict[str, int]:
    """Activate a validated exact-composition batch in the clip registry."""
    validate_report(report, request)
    if request.get("preparationOnly") is True:
        raise ValueError("preparation-only family batch cannot be activated")
    document = read(mappings_path)
    order = [row["sceneId"] for row in document["mappings"]]
    mappings = {row["sceneId"]: row for row in document["mappings"]}
    batch_id = report["batchId"]
    for proposal in report["proposals"]:
        clip_id = proposal["clipId"]
        evidence = proposal.get("bindingEvidence")
        if not isinstance(evidence, str) or not evidence.strip():
            evidence = (
                "The source-bound complete-family rule resolves this reviewed clip to the "
                "exact native terminal composition."
            )
        mappings[clip_id] = {
            "sceneId": clip_id,
            "projectId": proposal["projectId"],
            "status": "verified",
            "compositionId": proposal["compositionId"],
            "compositionPath": proposal["compositionPath"],
            "evidence": f"{evidence} Frozen in reports/{batch_id}.json.",
        }
        if clip_id not in order:
            order.append(clip_id)
    document["scope"]["uniqueScenes"] = len(mappings)
    document["mappings"] = [mappings[scene_id] for scene_id in order]
    mappings_path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n")
    return {"mappings": len(mappings), "activated": len(report["proposals"])}


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
