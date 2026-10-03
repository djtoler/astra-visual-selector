#!/usr/bin/env python3
"""Consume StoryPackage 0.2 only after its authoritative checker accepts it."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from .matching_contract_gate import enforce_contracts
except ImportError:
    from matching_contract_gate import enforce_contracts

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "plans" / "storypackage-02-integration-tasks.json"


def _read(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _git_head(repo: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True,
        text=True, capture_output=True,
    )
    return result.stdout.strip()


def _run_checker(package_path: Path, *, upstream_root: Path, checker_python: Path,
                 repo_mappings: dict[str, Path] | None = None) -> tuple[list[dict[str, Any]], str, str]:
    plan = _read(DEFAULT_PLAN)
    authority = plan["authority"]
    authority_commit = _git_head(upstream_root)
    supported_commits = set(authority.get("supportedCommits") or [authority["commit"]])
    if authority_commit not in supported_commits:
        raise ValueError("StoryPackage authority checkout is not at a supported pinned commit")
    checker = upstream_root / authority["checkerPath"]
    command = [str(checker_python), str(checker), str(package_path)]
    for name, path in sorted((repo_mappings or {}).items()):
        command.extend(["--repo", f"{name}={Path(path).resolve()}"])
    result = subprocess.run(
        command, cwd=checker.parent.parent, text=True, capture_output=True,
    )
    output = (result.stdout + result.stderr).strip()
    if result.returncode:
        raise ValueError(f"authoritative StoryPackage checker rejected package: {output}")
    gaps = []
    for line in result.stdout.splitlines():
        if line.startswith("  gap: "):
            gaps.append(json.loads(line.removeprefix("  gap: ")))
    return gaps, output, authority_commit


def build(package_path: Path, *, upstream_root: Path, checker_python: Path,
          repo_mappings: dict[str, Path] | None = None) -> dict[str, Any]:
    contract_receipt = enforce_contracts("storypackage_adapter.build")
    package_path = Path(package_path).resolve()
    upstream_root = Path(upstream_root).resolve()
    # Keep a virtualenv launcher intact; resolving its symlink bypasses that
    # environment's site-packages and can make the upstream checker unavailable.
    checker_python = Path(checker_python).absolute()
    gaps, checker_output, authority_commit = _run_checker(
        package_path, upstream_root=upstream_root, checker_python=checker_python,
        repo_mappings=repo_mappings,
    )
    package = _read(package_path)
    plan = _read(DEFAULT_PLAN)
    authority = plan["authority"]
    preserved = {
        key: package.get(key, [] if key in {"cohorts", "jobProposals", "obligations", "continuity"} else None)
        for key in (
            "story", "script", "entityRegistry", "entities", "cohorts", "beats", "claims",
            "jobProposals", "obligations", "continuity", "timing",
        )
    }
    return {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": 1,
        "sourceSchema": package["schema"],
        "packageId": package["packageId"],
        **preserved,
        "gaps": gaps,
        "storyHandoffReceipt": {
            "accepted": True,
            "packageSha256": _sha(package_path),
            "authorityCommit": authority_commit,
            "checkerPath": authority["checkerPath"],
            "checkerSha256": _sha(upstream_root / authority["checkerPath"]),
            "checkerOutput": checker_output,
        },
        "selectionAuthorized": False,
        "renderingAuthorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--upstream-root", required=True, type=Path)
    parser.add_argument("--checker-python", required=True, type=Path)
    parser.add_argument("--repo", action="append", default=[])
    args = parser.parse_args()
    mappings = {}
    for item in args.repo:
        name, separator, path = item.partition("=")
        if not separator:
            raise ValueError("--repo must be owner/name=/local/path")
        mappings[name] = Path(path)
    artifact = build(
        args.package, upstream_root=args.upstream_root,
        checker_python=args.checker_python, repo_mappings=mappings,
    )
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps({"packageId": artifact["packageId"], "gaps": len(artifact["gaps"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
