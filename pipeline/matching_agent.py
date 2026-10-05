#!/usr/bin/env python3
"""Public contract-enforced StoryPackage-to-review Matching-agent command."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .matching_agent_config import DEFAULT_PROFILE, resolve_profile
from .matching_agent_contracts import (
    AgentContractError, preflight, read_json, sha256, validate_task_contract,
)
from .matching_agent_runner import AgentRunnerError, Runner, runner_for
from .matching_contract_gate import enforce_contracts
from . import matching_harness, storypackage_adapter, storypackage_candidate_gallery, storypackage_splitter


ROOT = Path(__file__).resolve().parents[1]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _dump(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _write(path: Path, value: Any) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(_dump(value), encoding="utf-8")
    temporary.replace(path)
    return {"path": path.as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size}


def _provider_source(value: dict[str, Any]) -> dict[str, Any]:
    """Expose immutable identity to the model without local filesystem locations."""
    return {
        key: value[key] for key in (
            "repositoryId", "repositoryCommit", "sha256", "version", "identity", "authorityCommit"
        ) if key in value
    }


def _matching_runtime() -> dict[str, Any]:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    dirty = bool(subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip())
    return {"repository": "djtoler/astra-visual-selector", "commit": head, "dirty": dirty}


def _validate_registry_binding(adapter: dict[str, Any], roster: dict[str, Any]) -> None:
    snapshot = (adapter.get("entityRegistry") or {}).get("snapshot") or {}
    if snapshot.get("sha256") != roster["sha256"]:
        raise AgentContractError("StoryPackage entity-registry digest does not match the task authority")
    if snapshot.get("commit") and snapshot["commit"] != roster["repositoryCommit"]:
        raise AgentContractError("StoryPackage entity-registry commit does not match the task authority")
    if snapshot.get("repo") and snapshot["repo"] != roster["repositoryId"]:
        raise AgentContractError("StoryPackage entity-registry repository does not match the task authority")


def _requirements(proposals: dict[str, Any], *, data_bound: bool = False, media_bound: bool = False,
                  data_handoff: dict[str, Any] | None = None,
                  media_handoff: dict[str, Any] | None = None) -> dict[str, Any]:
    # Deprecated presence flags are deliberately insufficient. Existing typed
    # assignments can bind exact task fields after replay, never an entire file.
    verified = {}
    assignments = {}
    if data_handoff and data_handoff.get("assignments") and data_handoff.get("packageId") == proposals.get("packageId"):
        from .storypackage_data_assignment import validate as validate_data
        checked = validate_data(data_handoff)
        verified = checked["verifiedFields"]
        assignments = {r["taskId"]: r for r in data_handoff["assignments"]}
    tasks = []
    for row in proposals.get("taskProposals") or []:
        task_id = row["taskProposalId"]
        data_needed = bool(row.get("values") or row.get("cohortRefs") or
                           row.get("primaryPresentationOperation") == "data_explanation")
        media_needed = bool(row.get("entityRefs") or row.get("primaryPresentationOperation") in {
            "subject_profile", "relationship_intro", "item_sequence", "archival_progression",
        })
        requested = row.get("values") or []
        required_fields = [value.get("fieldId") or value.get("label") for value in requested]
        fields = {field["fieldId"]: field for field in assignments.get(task_id, {}).get("typedFields") or []}
        task_data_bound = bool(required_fields) and all(required_fields) and not row.get("cohortRefs") and all(
            field_id in verified.get(task_id, []) and
            fields[field_id].get("value") == value.get("value") and
            fields[field_id].get("unit") == value.get("unit")
            for field_id, value in zip(required_fields, requested))
        # Legacy delivery/catalog files express availability, not task demand
        # coverage. No supported task-bound Media receipt is silently invented.
        task_media_bound = False
        gaps = []
        if data_needed and not task_data_bound:
            gaps.append({
                "kind": "typed_data_handoff_missing", "owner": "data", "status": "missing",
                "claimIds": row.get("claimIds") or [],
                "requiredFields": requested,
            })
        if media_needed and not task_media_bound:
            gaps.append({
                "kind": "production_ready_media_handoff_missing", "owner": "media", "status": "missing",
                "claimIds": row.get("claimIds") or [],
            })
        tasks.append({
            "taskId": row["taskProposalId"],
            "data": {"required": data_needed, "status": "bound" if data_needed and task_data_bound else ("gap" if data_needed else "not_required")},
            "media": {"required": media_needed, "status": "bound" if media_needed and task_media_bound else ("gap" if media_needed else "not_required")},
            "gaps": gaps,
            "brollFallbackAvailable": True,
            "selectionAuthorized": False,
            "renderingAuthorized": False,
        })
    return {
        "schemaVersion": "matching-agent-requirements@1", "packageId": proposals["packageId"],
        "tasks": tasks,
        "counts": {
            "tasks": len(tasks), "typedGaps": sum(len(row["gaps"]) for row in tasks),
            "dataRequired": sum(row["data"]["required"] for row in tasks),
            "mediaRequired": sum(row["media"]["required"] for row in tasks),
        },
        "selectionAuthorized": False, "renderingAuthorized": False,
    }


def _route_plan(gallery: dict[str, Any]) -> dict[str, Any]:
    scenes = []
    for index, row in enumerate(gallery.get("tasks") or [], 1):
        disposition = row.get("routeDisposition") or {}
        candidates = row.get("candidates") or []
        template_route = disposition.get("templateEligible") is not False and bool(candidates)
        scenes.append({
            "sequenceIndex": index, "taskId": row["taskId"], "sourceBeatIds": row["sourceBeatIds"],
            "route": "template_review" if template_route else "broll",
            "routeReason": (
                "structured_capability_candidates_require_editor_review" if template_route
                else ("non_template_disposition" if disposition.get("templateEligible") is False
                      else "no_structurally_admitted_template_candidate")
            ),
            "candidateIds": [candidate["candidateId"] for candidate in candidates] if template_route else [],
            "brollFallbackAvailable": True,
            "transition": {"status": "review_required", "owner": "matching"},
            "selectionAuthorized": False, "renderingAuthorized": False,
        })
    for row in gallery.get("clipRoutes") or []:
        scenes.append({
            "sequenceIndex": len(scenes) + 1, "taskId": f"source-clip:{row['beatId']}",
            "sourceBeatIds": [row["beatId"]], "route": "source_clip", "routeReason": row["reason"],
            "candidateIds": [], "brollFallbackAvailable": True,
            "transition": {"status": "review_required", "owner": "matching"},
            "selectionAuthorized": False, "renderingAuthorized": False,
        })
    counts = Counter(row["route"] for row in scenes)
    return {
        "schemaVersion": "matching-agent-route-plan@1", "packageId": gallery["packageId"],
        "purpose": "Review-only ordered route proposal with b-roll fallback",
        "scenes": scenes, "counts": {"scenes": len(scenes), **dict(sorted(counts.items()))},
        "selectionAuthorized": False, "renderingAuthorized": False,
    }


def _failed_receipt(task: dict[str, Any], configuration: dict[str, Any] | None,
                    started_at: str, exc: Exception, checks: list[dict[str, Any]],
                    outputs: list[dict[str, Any]]) -> dict[str, Any]:
    text = str(exc)
    if isinstance(exc, AgentRunnerError):
        party = "matching"
    elif "automation-data" in text.lower():
        party = "data"
    elif "StoryPackage" in text or "story" in text.lower():
        party = "story"
    elif "entity" in text.lower() or "data" in text.lower():
        party = "data"
    else:
        party = "coordinator" if isinstance(exc, AgentContractError) else "matching"
    return {
        "schemaVersion": "matching-agent-receipt@1",
        "taskId": task.get("taskId", "unknown"), "objectiveId": task.get("objectiveId", "unknown"),
        "status": "failed", "startedAt": started_at, "endedAt": _now(),
        "currentBlocker": {"party": party, "reason": type(exc).__name__, "missingInputOrAction": text},
        "configuration": configuration or {"status": "unresolved"},
        "inputs": {}, "outputs": outputs, "checks": checks,
        "commands": [row["id"] for row in checks],
        "telemetry": {"usage": "unavailable", "cost": "unavailable", "servedModel": "unavailable"},
        "warnings": [], "typedGaps": [], "invalidatedDownstreamReceipts": task.get("dependencyReceiptIds") or [],
        "selectionAuthorized": False, "renderingAuthorized": False,
    }


def run_task(task_path: Path, *, profile_path: Path = DEFAULT_PROFILE,
             profile_id: str | None = None, executable: str | Path = "codex",
             runner: Runner | None = None) -> dict[str, Any]:
    """Execute the immutable task contract and return its final structured receipt."""
    contract_receipt = enforce_contracts("matching_agent.run")
    matching_runtime = _matching_runtime()
    started_at = _now()
    monotonic_start = time.monotonic()
    task = read_json(task_path)
    output_directory: Path | None = None
    configuration: dict[str, Any] | None = None
    outputs: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = [{"id": "matching_contract_gate", "status": "passed", "receipt": contract_receipt}]
    try:
        validate_task_contract(task)
        configuration = resolve_profile(profile_path, profile_id=profile_id or task["profile"]["profileId"])
        configured = configuration["configuredTuple"]
        binding = task["profile"]
        if configured["profileId"] != binding["profileId"] or any((
            configured[profile_key] != binding[task_key]
            for profile_key, task_key in (
                ("promptVersion", "promptVersion"), ("toolPolicy", "toolPolicy"),
                ("permissionPolicy", "permissionPolicy"), ("evaluationVersion", "evaluationProfile"),
            )
        )):
            raise AgentContractError("resolved profile does not match the task binding")
        preflight_receipt = preflight(task)
        output_directory = Path(preflight_receipt["outputDirectory"])
        output_directory.mkdir(parents=True, exist_ok=True)
        outputs.append(_write(output_directory / "00-preflight.json", preflight_receipt))
        checks.append({"id": "immutable_authority_preflight", "status": "passed"})

        story = preflight_receipt["inputs"]["storyPackage"]
        roster = preflight_receipt["inputs"]["entityRoster"]
        old_catalog = os.environ.get("ASTRA_APPROVED_LIST")
        os.environ["ASTRA_APPROVED_LIST"] = preflight_receipt["inputs"]["templateCatalog"]["path"]
        try:
            repo_mappings = {
                roster["repositoryId"]: Path(roster["repositoryRoot"]),
                **{
                    mapping["repositoryId"]: Path(mapping["repositoryRoot"])
                    for mapping in preflight_receipt["inputs"]["repositoryMappings"]
                },
            }
            adapter = storypackage_adapter.build(
                Path(story["path"]), upstream_root=Path(story["authorityRoot"]),
                checker_python=Path(story["checkerPython"]),
                repo_mappings=repo_mappings,
            )
            _validate_registry_binding(adapter, roster)
            adapter_path = output_directory / "10-storypackage-adapter.json"
            outputs.append(_write(adapter_path, adapter))

            proposals = storypackage_splitter.build(adapter, source_path=adapter_path)
            proposal_path = output_directory / "20-visualtask-proposals.json"
            outputs.append(_write(proposal_path, proposals))

            requirements = _requirements(
                proposals,
                data_handoff=read_json(Path(preflight_receipt["inputs"]["dataHandoff"]["path"])) if "dataHandoff" in preflight_receipt["inputs"] else None,
                media_handoff=read_json(Path(preflight_receipt["inputs"]["mediaHandoff"]["path"])) if "mediaHandoff" in preflight_receipt["inputs"] else None,
            )
            outputs.append(_write(output_directory / "30-data-media-requirements.json", requirements))

            gallery = storypackage_candidate_gallery.build(
                proposals_path=proposal_path, adapter_path=adapter_path,
            )
            gallery_path = output_directory / "40-candidate-admissions.json"
            gallery_source = _write(gallery_path, gallery)
            outputs.append(gallery_source)
        finally:
            if old_catalog is None:
                os.environ.pop("ASTRA_APPROVED_LIST", None)
            else:
                os.environ["ASTRA_APPROVED_LIST"] = old_catalog
        checks.extend([
            {"id": "authoritative_storypackage_adapter", "status": "passed"},
            {"id": "complete_claim_routing", "status": "passed" if proposals["counts"]["uncoveredClaims"] == 0 else "failed"},
            {"id": "structured_capability_admission", "status": "passed"},
        ])
        if proposals["counts"]["uncoveredClaims"]:
            raise AgentContractError("StoryPackage contains narration claims without a typed route")

        route_plan = _route_plan(gallery)
        outputs.append(_write(output_directory / "50-ordered-review-route.json", route_plan))

        harness = matching_harness.build(mode="evaluation_fixture")
        matching_harness.validate(harness, verify_sources=False)
        outputs.append(_write(output_directory / "60-matching-harness-audit.json", harness))
        checks.append({"id": "matching_harness", "status": "passed"})

        provider_workspace = output_directory / "provider-workspace"
        provider_workspace.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "-q"], cwd=provider_workspace, check=True)
        review_input = {
            "schemaVersion": "matching-agent-review-input@1", "taskId": task["taskId"],
            "packageId": adapter["packageId"],
            "immutableInputs": {
                key: _provider_source(value)
                for key, value in preflight_receipt["inputs"].items()
                if isinstance(value, dict)
            },
            "counts": {
                "claims": proposals["counts"]["claims"], "taskProposals": proposals["counts"]["taskProposals"],
                "uncoveredClaims": proposals["counts"]["uncoveredClaims"],
                "candidateCards": gallery["counts"]["candidateCards"],
                "tasksWithoutCandidates": gallery["counts"]["tasksWithoutCandidates"],
                "typedGaps": requirements["counts"]["typedGaps"],
                "routes": route_plan["counts"],
            },
            "typedGapSummary": dict(sorted(Counter(
                gap["kind"] for row in requirements["tasks"] for gap in row["gaps"]
            ).items())),
            "harness": {
                "generalMatchingComplete": harness["generalMatchingLayer"]["complete"],
                "firstBlockingStage": harness["firstBlockingStage"],
            },
            "selectionAuthorized": False, "renderingAuthorized": False,
        }
        outputs.append(_write(provider_workspace / "agent-review-input.json", review_input))
        active_runner = runner or runner_for(configuration, executable=executable)
        capability = active_runner.capabilities()
        outputs.append(_write(output_directory / "70-runner-capabilities.json", capability))
        runner_task = {**task, "_packageIdForRunner": adapter["packageId"]}
        runner_configuration = {**configuration, "_packageIdForRunner": adapter["packageId"]}
        attempts = 2 if task["retryClass"] == "transient_once" else 1
        runner_receipt = None
        last_runner_error = None
        for attempt in range(1, attempts + 1):
            try:
                handle = active_runner.run(runner_task, provider_workspace, runner_configuration)
                runner_receipt = active_runner.collect(handle)
                checks.append({"id": f"provider_attempt_{attempt}", "status": "passed"})
                break
            except AgentRunnerError as exc:
                last_runner_error = exc
                checks.append({"id": f"provider_attempt_{attempt}", "status": "failed", "reason": str(exc)})
        if runner_receipt is None:
            raise last_runner_error or AgentRunnerError("provider runner failed without a receipt")
        outputs.append(_write(output_directory / "80-runner-receipt.json", runner_receipt))
        outputs.append(_write(output_directory / "90-candidate-review.json", {
            "schemaVersion": "matching-agent-candidate-review@1", "packageId": adapter["packageId"],
            "gallery": gallery_source, "modelReview": runner_receipt["review"],
            "selectionAuthorized": False, "renderingAuthorized": False,
        }))
        checks.append({"id": "schema_bound_provider_review", "status": "passed"})

        receipt = {
            "schemaVersion": "matching-agent-receipt@1", "taskId": task["taskId"],
            "objectiveId": task["objectiveId"], "status": "passed",
            "receiptPath": (output_directory / "matching-agent-receipt.json").as_posix(),
            "startedAt": started_at, "endedAt": _now(),
            "wallTimeSeconds": round(time.monotonic() - monotonic_start, 6),
            "currentBlocker": {"party": "none", "reason": "agent_review_complete", "missingInputOrAction": None},
            "configuration": configuration,
            "inputs": {**preflight_receipt["inputs"], "matchingRuntime": matching_runtime},
            "outputs": outputs, "checks": checks,
            "commands": [
                "matching_agent.run", "storypackage_adapter.build", "storypackage_splitter.build",
                "storypackage_candidate_gallery.build", "matching_harness.build", "matching_harness.validate",
                f"{configuration['configuredTuple']['runner']}.run", f"{configuration['configuredTuple']['runner']}.collect",
            ],
            "telemetry": {
                "servedModel": runner_receipt["servedModel"], "usage": runner_receipt["usage"],
                "cost": runner_receipt["cost"], "providerSessionId": runner_receipt["providerSessionId"],
                "mcpServers": "unavailable", "skills": "unavailable",
                "tools": task["toolAllowList"],
                "permissions": {"runner": ["read_only_workspace"], "orchestratorMutationScope": task["mutationScope"]},
            },
            "warnings": runner_receipt["review"]["warnings"],
            "typedGaps": [gap for row in requirements["tasks"] for gap in row["gaps"]],
            "invalidatedDownstreamReceipts": [],
            "selectionAuthorized": False, "renderingAuthorized": False,
        }
        _write(output_directory / "matching-agent-receipt.json", receipt)
        return receipt
    except Exception as exc:
        receipt = _failed_receipt(task, configuration, started_at, exc, checks, outputs)
        if output_directory is not None:
            _write(output_directory / "matching-agent-receipt.json", receipt)
        raise AgentRunnerError(_dump(receipt)) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run",))
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--profile")
    parser.add_argument("--codex", default="codex")
    args = parser.parse_args()
    receipt = run_task(
        args.task, profile_path=args.profiles, profile_id=args.profile, executable=args.codex)
    print(json.dumps({
        "taskId": receipt["taskId"], "status": receipt["status"],
        "currentBlocker": receipt["currentBlocker"]["party"],
        "receipt": receipt["receiptPath"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
