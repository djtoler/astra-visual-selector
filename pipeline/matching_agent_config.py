#!/usr/bin/env python3
"""Strict, dependency-free resolution of the versioned Matching-agent profile."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = ROOT / "config" / "matching-agent-profiles.yaml"
PLACEHOLDER = re.compile(r"^\$\{([A-Z][A-Z0-9_]*)(?::-(.*))?\}$")
ALLOWED_ENV = {
    "MATCHING_PROFILE",
    "MATCHING_OPENAI_MODEL", "MATCHING_OPENAI_TRANSPORT", "MATCHING_OPENAI_EFFORT",
    "MATCHING_ANTHROPIC_MODEL", "MATCHING_ANTHROPIC_TRANSPORT", "MATCHING_ANTHROPIC_EFFORT",
}
ROOT_KEYS = {"schema_version", "agent_id", "contract_version", "active_profile", "profiles"}
PROFILE_KEYS = {
    "provider", "model", "transport", "reasoning_effort", "prompt_version",
    "tool_policy", "permission_policy", "evaluation_profile",
}
EFFORTS = {"low", "medium", "high", "xhigh", "max", "ultra"}


class AgentConfigurationError(ValueError):
    pass


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _strict_keys(value: Mapping[str, Any], allowed: set[str], label: str) -> None:
    unknown = set(value) - allowed
    missing = allowed - set(value)
    if unknown or missing:
        raise AgentConfigurationError(
            f"{label} keys invalid; missing={sorted(missing)} unknown={sorted(unknown)}")


def _resolve(value: str, environment: Mapping[str, str]) -> str:
    match = PLACEHOLDER.fullmatch(value)
    if not match:
        if "${" in value:
            raise AgentConfigurationError(f"unsupported embedded environment expression: {value}")
        return value
    name, default = match.groups()
    if name not in ALLOWED_ENV:
        raise AgentConfigurationError(f"environment variable is not allow-listed: {name}")
    resolved = environment.get(name, default)
    if resolved is None or not str(resolved).strip():
        raise AgentConfigurationError(f"required environment variable is unresolved: {name}")
    return str(resolved)


def resolve_profile(path: Path = DEFAULT_PROFILE, *, profile_id: str | None = None,
                    environment: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Resolve exactly one profile and return a redacted, digest-bound receipt.

    The file is JSON-compatible YAML. Parsing it as JSON is intentional: it keeps
    the format valid YAML while preventing YAML tags, aliases, and implicit types
    from expanding the configuration language.
    """
    environment = dict(os.environ if environment is None else environment)
    path = Path(path).resolve()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AgentConfigurationError(f"profile YAML must be strict JSON-compatible YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise AgentConfigurationError("profile document must be an object")
    _strict_keys(raw, ROOT_KEYS, "profile document")
    if raw["schema_version"] != "matching-agent-profile@1":
        raise AgentConfigurationError("unsupported profile schema version")
    if raw["agent_id"] != "matching" or raw["contract_version"] != "general-matching-agent@1":
        raise AgentConfigurationError("profile has the wrong agent or contract")
    profiles = raw["profiles"]
    if not isinstance(profiles, dict) or not profiles:
        raise AgentConfigurationError("profiles must be a non-empty object")
    for name, value in profiles.items():
        if not isinstance(name, str) or not isinstance(value, dict):
            raise AgentConfigurationError("profile entries must be named objects")
        _strict_keys(value, PROFILE_KEYS, f"profile {name}")
    selected = profile_id or _resolve(raw["active_profile"], environment)
    if selected not in profiles:
        raise AgentConfigurationError(f"unknown active profile: {selected}")
    resolved = {key: _resolve(str(value), environment) for key, value in profiles[selected].items()}
    if resolved["provider"] not in {"openai", "anthropic"}:
        raise AgentConfigurationError("unsupported provider")
    if resolved["transport"] != "cli":
        raise AgentConfigurationError("the initial build supports only CLI transports")
    if resolved["reasoning_effort"] not in EFFORTS:
        raise AgentConfigurationError("unsupported reasoning effort")
    expected = {
        "prompt_version": "matching-agent-prompt@1",
        "tool_policy": "matching-tools@1",
        "permission_policy": "matching-review-only@1",
        "evaluation_profile": "matching-cross-story@1",
    }
    if any(resolved[key] != value for key, value in expected.items()):
        raise AgentConfigurationError("profile versions do not match the frozen agent contract")
    if resolved["provider"] == "openai" and selected == "openai_gpt":
        runner = "CodexCliRunner"
    elif resolved["provider"] == "anthropic":
        runner = "unavailable"
    else:
        raise AgentConfigurationError("unsupported provider/profile combination")
    configured_tuple = {
        "profileId": selected,
        "provider": resolved["provider"],
        "model": resolved["model"],
        "servedModel": "unavailable_until_runner_reports",
        "transport": resolved["transport"],
        "reasoningEffort": resolved["reasoning_effort"],
        "promptVersion": resolved["prompt_version"],
        "toolPolicy": resolved["tool_policy"],
        "permissionPolicy": resolved["permission_policy"],
        "evaluationVersion": resolved["evaluation_profile"],
        "runner": runner,
    }
    return {
        "schemaVersion": "matching-agent-configuration-receipt@1",
        "source": {"path": path.as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()},
        "configuredTuple": configured_tuple,
        "configuredTupleSha256": _digest(configured_tuple),
        "redacted": True,
        "selectionAuthorized": False,
        "renderingAuthorized": False,
    }
