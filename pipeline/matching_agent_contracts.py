#!/usr/bin/env python3
"""Fail-closed validation and immutable input preflight for Matching-agent tasks."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
ROOT_KEYS = {
    "schemaVersion", "taskId", "objectiveId", "owner", "requestedBy",
    "storyPackage", "entityRoster", "templateCatalog", "dataHandoff", "mediaHandoff",
    "output", "dependencyReceiptIds", "dependencyReceipts", "profile", "toolAllowList", "mutationScope",
    "acceptanceChecks", "timeoutClass", "retryClass", "userInput",
    "selectionAuthorized", "renderingAuthorized",
}


class AgentContractError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AgentContractError(f"invalid JSON contract {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AgentContractError("task contract must be an object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=Path(root), text=True,
        capture_output=True, check=False,
    )
    if result.returncode:
        raise AgentContractError(f"declared repository is not readable: {root}")
    return result.stdout.strip()


def _keys(value: dict[str, Any], required: set[str], allowed: set[str], label: str) -> None:
    missing = required - set(value)
    unknown = set(value) - allowed
    if missing or unknown:
        raise AgentContractError(f"{label} keys invalid; missing={sorted(missing)} unknown={sorted(unknown)}")


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AgentContractError(f"{label} must be a non-empty string")
    return value


def _file_input(value: Any, label: str, *, authority: bool = False,
                story: bool = False, catalog: bool = False) -> None:
    if not isinstance(value, dict):
        raise AgentContractError(f"{label} must be an object")
    required = {"path", "sha256"}
    if authority or catalog or story:
        required |= {"repositoryId", "repositoryRoot", "repositoryCommit"}
    if authority:
        required.add("version")
    if catalog:
        required.add("identity")
    if story:
        required |= {"authorityRoot", "authorityCommit", "checkerPython"}
    _keys(value, required, required, label)
    for key in required - {"sha256", "repositoryCommit", "authorityCommit"}:
        _text(value[key], f"{label}.{key}")
    if not SHA256.fullmatch(str(value["sha256"])):
        raise AgentContractError(f"{label}.sha256 is not an exact digest")
    if "repositoryCommit" in value and not COMMIT.fullmatch(str(value["repositoryCommit"])):
        raise AgentContractError(f"{label}.repositoryCommit is not an exact commit")
    if "authorityCommit" in value and not COMMIT.fullmatch(str(value["authorityCommit"])):
        raise AgentContractError(f"{label}.authorityCommit is not an exact commit")


def validate_task_contract(task: dict[str, Any]) -> dict[str, Any]:
    _keys(task, ROOT_KEYS - {"dataHandoff", "mediaHandoff"}, ROOT_KEYS, "task contract")
    if task.get("schemaVersion") != "matching-agent-task@1":
        raise AgentContractError("unsupported task contract version")
    for key in ("taskId", "objectiveId", "requestedBy"):
        _text(task.get(key), key)
    if task.get("owner") != "matching":
        raise AgentContractError("task owner must be matching")
    if task.get("selectionAuthorized") is not False or task.get("renderingAuthorized") is not False:
        raise AgentContractError("task contract cannot authorize selection or rendering")
    _file_input(task.get("storyPackage"), "storyPackage", story=True)
    _file_input(task.get("entityRoster"), "entityRoster", authority=True)
    _file_input(task.get("templateCatalog"), "templateCatalog", catalog=True)
    for optional in ("dataHandoff", "mediaHandoff"):
        if optional in task:
            _file_input(task[optional], optional)
    output = task.get("output")
    if not isinstance(output, dict):
        raise AgentContractError("output must be an object")
    _keys(output, {"schema", "directory"}, {"schema", "directory"}, "output")
    if output["schema"] != "matching-agent-receipt@1":
        raise AgentContractError("unsupported output schema")
    _text(output["directory"], "output.directory")
    profile = task.get("profile")
    expected_profile_keys = {"profileId", "promptVersion", "toolPolicy", "permissionPolicy", "evaluationProfile"}
    if not isinstance(profile, dict):
        raise AgentContractError("profile binding must be an object")
    _keys(profile, expected_profile_keys, expected_profile_keys, "profile binding")
    versions = {
        "promptVersion": "matching-agent-prompt@1", "toolPolicy": "matching-tools@1",
        "permissionPolicy": "matching-review-only@1", "evaluationProfile": "matching-cross-story@1",
    }
    if any(profile.get(key) != value for key, value in versions.items()):
        raise AgentContractError("task profile versions are stale or unsupported")
    _text(profile.get("profileId"), "profile.profileId")
    if task.get("toolAllowList") != ["read_matching_artifacts"]:
        raise AgentContractError("tool allow-list must be the frozen review-only policy")
    for key in ("dependencyReceiptIds", "mutationScope", "acceptanceChecks"):
        if not isinstance(task.get(key), list) or (key != "dependencyReceiptIds" and not task[key]):
            raise AgentContractError(f"{key} must be a list")
        if len(task[key]) != len(set(task[key])) or any(not isinstance(item, str) or not item for item in task[key]):
            raise AgentContractError(f"{key} must contain unique non-empty strings")
    dependencies = task.get("dependencyReceipts")
    if not isinstance(dependencies, list):
        raise AgentContractError("dependencyReceipts must be a list")
    dependency_ids = []
    for index, receipt in enumerate(dependencies):
        if not isinstance(receipt, dict) or set(receipt) != {"id", "path", "sha256"}:
            raise AgentContractError("dependency receipt has missing or unknown fields")
        _text(receipt["path"], f"dependencyReceipts[{index}].path")
        if not SHA256.fullmatch(str(receipt["sha256"])):
            raise AgentContractError("dependency receipt digest is invalid")
        dependency_ids.append(_text(receipt["id"], "dependency receipt id"))
    if dependency_ids != task["dependencyReceiptIds"]:
        raise AgentContractError("dependency receipt IDs do not match their immutable bindings")
    if task.get("timeoutClass") not in {"short", "standard", "long"}:
        raise AgentContractError("invalid timeout class")
    if task.get("retryClass") not in {"none", "transient_once"}:
        raise AgentContractError("invalid retry class")
    user_input = task.get("userInput")
    if not isinstance(user_input, dict):
        raise AgentContractError("userInput must be an object")
    _keys(user_input, {"allowed", "required"}, {"allowed", "required"}, "userInput")
    if not all(isinstance(user_input[key], bool) for key in user_input):
        raise AgentContractError("userInput flags must be boolean")
    if user_input["required"] and not user_input["allowed"]:
        raise AgentContractError("required user input must be allowed")
    return task


def _resolved_file(value: dict[str, Any], label: str) -> Path:
    path = Path(value["path"]).expanduser().resolve()
    if not path.is_file():
        raise AgentContractError(f"{label} is missing: {path}")
    if sha256(path) != value["sha256"]:
        raise AgentContractError(f"{label} digest is stale")
    return path


def preflight(task: dict[str, Any]) -> dict[str, Any]:
    validate_task_contract(task)
    inputs: dict[str, Any] = {}
    for label in ("storyPackage", "entityRoster", "templateCatalog"):
        value = task[label]
        root = Path(value["repositoryRoot"]).expanduser().resolve()
        head = git_head(root)
        if head != value["repositoryCommit"]:
            raise AgentContractError(f"{label} repository moved: expected {value['repositoryCommit']} got {head}")
        path = _resolved_file(value, label)
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise AgentContractError(f"{label} path is outside its declared repository") from exc
        inputs[label] = {**value, "path": path.as_posix(), "repositoryRoot": root.as_posix()}
    story = task["storyPackage"]
    authority_root = Path(story["authorityRoot"]).expanduser().resolve()
    authority_head = git_head(authority_root)
    if authority_head != story["authorityCommit"]:
        raise AgentContractError(
            f"StoryPackage authority moved: expected {story['authorityCommit']} got {authority_head}")
    checker_python = Path(story["checkerPython"]).expanduser().absolute()
    if not checker_python.is_file():
        raise AgentContractError("StoryPackage checker Python is missing")
    inputs["storyPackage"].update({
        "authorityRoot": authority_root.as_posix(), "checkerPython": checker_python.as_posix()})
    for optional in ("dataHandoff", "mediaHandoff"):
        if optional in task:
            inputs[optional] = {**task[optional], "path": _resolved_file(task[optional], optional).as_posix()}
    inputs["dependencyReceipts"] = [
        {**receipt, "path": _resolved_file(receipt, f"dependency receipt {receipt['id']}").as_posix()}
        for receipt in task["dependencyReceipts"]
    ]
    output = Path(task["output"]["directory"]).expanduser().resolve()
    scopes = [Path(value).expanduser().resolve() for value in task["mutationScope"]]
    if not any(output == scope or output.is_relative_to(scope) for scope in scopes):
        raise AgentContractError("output directory is outside the declared mutation scope")
    return {
        "schemaVersion": "matching-agent-preflight@1",
        "taskId": task["taskId"],
        "inputs": inputs,
        "outputDirectory": output.as_posix(),
        "dependencyReceiptIds": task["dependencyReceiptIds"],
        "selectionAuthorized": False,
        "renderingAuthorized": False,
    }
