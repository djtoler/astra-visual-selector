#!/usr/bin/env python3
"""Provider-neutral runner contract and the initial Codex CLI adapter."""

from __future__ import annotations

import json
import os
import subprocess
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


ROOT = Path(__file__).resolve().parents[1]
REVIEW_SCHEMA = ROOT / "grammar" / "matching-agent-review.schema.json"


class AgentRunnerError(RuntimeError):
    pass


class Runner(Protocol):
    def capabilities(self) -> dict[str, Any]: ...
    def run(self, task_contract: dict[str, Any], workspace: Path,
            agent_profile: dict[str, Any]) -> "RunHandle": ...
    def status(self, run_handle: "RunHandle") -> dict[str, Any]: ...
    def steer(self, run_handle: "RunHandle", message: str) -> dict[str, Any]: ...
    def cancel(self, run_handle: "RunHandle") -> dict[str, Any]: ...
    def collect(self, run_handle: "RunHandle") -> dict[str, Any]: ...


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RunHandle:
    run_id: str
    task_id: str
    process: subprocess.Popen[str]
    started_at: str
    monotonic_start: float
    output_path: Path
    event_path: Path
    profile: dict[str, Any]
    timeout_seconds: int
    collected: dict[str, Any] | None = None


def validate_review(value: Any, *, task_id: str, package_id: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AgentRunnerError("runner review must be an object")
    expected = {
        "schemaVersion", "taskId", "packageId", "reviewSummary", "warnings",
        "typedGaps", "selectionAuthorized", "renderingAuthorized",
    }
    if set(value) != expected:
        raise AgentRunnerError("runner review has missing or unknown fields")
    if value["schemaVersion"] != "matching-agent-review@1":
        raise AgentRunnerError("runner review schema is unsupported")
    if value["taskId"] != task_id or value["packageId"] != package_id:
        raise AgentRunnerError("runner review is not bound to the requested task and package")
    if not isinstance(value["reviewSummary"], str) or not value["reviewSummary"].strip():
        raise AgentRunnerError("runner review summary is empty")
    if not isinstance(value["warnings"], list) or any(not isinstance(row, str) for row in value["warnings"]):
        raise AgentRunnerError("runner review warnings are invalid")
    if not isinstance(value["typedGaps"], list) or any(not isinstance(row, dict) for row in value["typedGaps"]):
        raise AgentRunnerError("runner review typed gaps are invalid")
    if value["typedGaps"]:
        raise AgentRunnerError("runner review duplicated deterministic typed gaps")
    if value["selectionAuthorized"] is not False or value["renderingAuthorized"] is not False:
        raise AgentRunnerError("runner review attempted to authorize selection or rendering")
    return value


class CodexCliRunner:
    """Run one bounded, read-only structured review through the installed CLI."""

    def __init__(self, executable: str | Path = "codex") -> None:
        self.executable = str(executable)

    def capabilities(self) -> dict[str, Any]:
        return {
            "schemaVersion": "matching-agent-capability-manifest@1",
            "runner": "CodexCliRunner",
            "operations": {"run": True, "status": True, "steer": False, "cancel": True, "collect": True},
            "servedModelTelemetry": "reported_when_available",
            "costTelemetry": "unsupported",
            "selectionAuthorized": False,
            "renderingAuthorized": False,
        }

    def run(self, task_contract: dict[str, Any], workspace: Path,
            agent_profile: dict[str, Any]) -> RunHandle:
        configured = agent_profile["configuredTuple"]
        if configured["provider"] != "openai" or configured["transport"] != "cli":
            raise AgentRunnerError("CodexCliRunner requires an OpenAI CLI profile")
        workspace = Path(workspace).resolve()
        workspace.mkdir(parents=True, exist_ok=True)
        run_id = str(uuid.uuid4())
        output_path = workspace / f"{run_id}-model-review.json"
        event_path = workspace / f"{run_id}-events.jsonl"
        prompt = (
            "You are the review-only Matching agent. Read the deterministic run manifest named "
            "agent-review-input.json in the current workspace. Summarize only facts present in that "
            "manifest. Do not select a candidate, do not authorize rendering, do not edit files, and "
            "do not invent Story, Data, Media, or template facts. Return exactly the requested JSON "
            f"schema for taskId {task_contract['taskId']} and packageId "
            f"{task_contract['_packageIdForRunner']}. The canonical typed gaps remain in the "
            "deterministic requirements artifact; return typedGaps as an empty array and summarize "
            "only the supplied gap counts in reviewSummary or warnings."
        )
        command = [
            self.executable, "exec", "--ephemeral", "--json", "--color", "never",
            "--sandbox", "read-only", "--ignore-user-config", "--output-schema", str(REVIEW_SCHEMA),
            "--output-last-message", str(output_path), "--cd", str(workspace),
            "--model", configured["model"],
            "-c", f'model_reasoning_effort="{configured["reasoningEffort"]}"',
            "-",
        ]
        try:
            process = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, env={**os.environ},
            )
        except OSError as exc:
            raise AgentRunnerError(f"failed to start Codex CLI: {exc}") from exc
        assert process.stdin is not None
        process.stdin.write(prompt)
        process.stdin.close()
        process.stdin = None
        bound_profile = {**agent_profile, "_packageIdForRunner": task_contract["_packageIdForRunner"]}
        return RunHandle(
            run_id=run_id, task_id=task_contract["taskId"], process=process,
            started_at=_now(), monotonic_start=time.monotonic(), output_path=output_path,
            event_path=event_path, profile=bound_profile,
            timeout_seconds={"short": 120, "standard": 600, "long": 1800}[task_contract["timeoutClass"]],
        )

    def status(self, run_handle: RunHandle) -> dict[str, Any]:
        code = run_handle.process.poll()
        state = "running" if code is None else ("passed" if code == 0 else "failed")
        return {
            "schemaVersion": "matching-agent-run-state@1", "runId": run_handle.run_id,
            "state": state, "startedAt": run_handle.started_at,
            "endedAt": None if code is None else _now(),
            "selectionAuthorized": False, "renderingAuthorized": False,
        }

    def steer(self, run_handle: RunHandle, message: str) -> dict[str, Any]:
        raise AgentRunnerError("CodexCliRunner does not declare steering support")

    def cancel(self, run_handle: RunHandle) -> dict[str, Any]:
        if run_handle.process.poll() is None:
            run_handle.process.terminate()
            try:
                run_handle.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                run_handle.process.kill()
                run_handle.process.wait(timeout=5)
        return {
            "schemaVersion": "matching-agent-cancellation-receipt@1",
            "runId": run_handle.run_id, "cancelled": True, "endedAt": _now(),
            "selectionAuthorized": False, "renderingAuthorized": False,
        }

    def collect(self, run_handle: RunHandle) -> dict[str, Any]:
        if run_handle.collected is not None:
            return run_handle.collected
        try:
            stdout, stderr = run_handle.process.communicate(timeout=run_handle.timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            run_handle.process.kill()
            stdout, stderr = run_handle.process.communicate()
            run_handle.event_path.write_text(stdout, encoding="utf-8")
            raise AgentRunnerError(
                f"Codex CLI exceeded the declared timeout ({run_handle.timeout_seconds}s)") from exc
        run_handle.event_path.write_text(stdout, encoding="utf-8")
        if run_handle.process.returncode:
            raise AgentRunnerError(
                f"Codex CLI failed with exit {run_handle.process.returncode}: {stderr.strip()[-2000:]}")
        if not run_handle.output_path.is_file():
            raise AgentRunnerError("Codex CLI did not produce its schema-bound review")
        try:
            review = json.loads(run_handle.output_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise AgentRunnerError(f"Codex CLI review is not JSON: {exc}") from exc
        package_id = run_handle.profile.get("_packageIdForRunner")
        validate_review(review, task_id=run_handle.task_id, package_id=package_id)
        events = []
        for line in stdout.splitlines():
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                events.append(value)
        served_model = next((
            value for event in events for key, value in event.items()
            if key in {"model", "served_model", "servedModel"} and isinstance(value, str)
        ), "unavailable")
        session_id = next((
            value for event in events for key, value in event.items()
            if key in {"thread_id", "session_id", "sessionId"} and isinstance(value, str)
        ), "unavailable")
        usage = next((event.get("usage") for event in reversed(events) if isinstance(event.get("usage"), dict)), None)
        configured = run_handle.profile["configuredTuple"]
        run_handle.collected = {
            "schemaVersion": "matching-agent-runner-receipt@1",
            "runId": run_handle.run_id,
            "status": "passed",
            "review": review,
            "provider": configured["provider"],
            "configuredModel": configured["model"],
            "servedModel": served_model,
            "transport": configured["transport"],
            "reasoningEffort": configured["reasoningEffort"],
            "providerSessionId": session_id,
            "startedAt": run_handle.started_at,
            "endedAt": _now(),
            "wallTimeSeconds": round(time.monotonic() - run_handle.monotonic_start, 6),
            "usage": usage if usage is not None else "unavailable",
            "cost": "unsupported",
            "stderr": stderr.strip() or None,
            "eventLog": run_handle.event_path.as_posix(),
            "selectionAuthorized": False,
            "renderingAuthorized": False,
        }
        return run_handle.collected


def runner_for(configuration: dict[str, Any], *, executable: str | Path = "codex") -> Runner:
    configured = configuration["configuredTuple"]
    if configured["runner"] == "CodexCliRunner":
        runner = CodexCliRunner(executable)
        # Attach the package binding later without changing the configured tuple digest.
        return runner
    raise AgentRunnerError(
        f"no runner is implemented for profile {configured['profileId']}; "
        "the provider-neutral contract resolved successfully but activation is unavailable")
