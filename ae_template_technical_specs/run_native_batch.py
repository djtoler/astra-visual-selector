#!/usr/bin/env python3
"""Run an isolated, resumable, non-rendering native AE inspection batch."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent
INSPECTOR = ROOT / "vendor" / "capacity-inspector" / "run.py"
CHUNK_SIZE = 4 * 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_from(base: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def report_path_for_job(job_path: Path) -> Path:
    job = json.loads(job_path.read_text())
    return resolve_from(job_path.parent, job["inspection_report"])


def close_verified_shared_project(report_path: Path) -> str:
    """Close only the disposable project proven to match a completed report."""
    report = json.loads(report_path.read_text())
    if not report.get("ok") or not report.get("disposableCloseRequested"):
        return "not_requested"
    expected = [
        {"id": item.get("id"), "name": item.get("name")}
        for item in report.get("items", [])
    ]
    script_path = report_path.parent / "close-verified-disposable.jsx"
    source = """(function () {
var expected = EXPECTED;
if (!app.project || app.project.numItems === 0) return 'already_empty';
if (app.project.renderQueue.rendering) throw Error('Refusing to close a rendering project');
if (app.project.numItems !== expected.length) throw Error('Current project item count does not match completed disposable report');
for (var i=1;i<=app.project.numItems;i++) {
    var item=app.project.item(i), prior=expected[i-1];
    if (!prior || item.id !== prior.id || item.name !== prior.name)
        throw Error('Current project identity does not match completed disposable report');
}
app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
return 'closed_verified_disposable';
})()""".replace("EXPECTED", json.dumps(expected, ensure_ascii=True))
    script_path.write_text(source)
    bridge = '''on run argv
    with timeout of 300 seconds
        tell application "/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app"
            return DoScriptFile (POSIX file (item 1 of argv))
        end tell
    end timeout
end run'''
    process = subprocess.run(
        ["osascript", "-e", bridge, str(script_path)],
        capture_output=True,
        text=True,
        timeout=330,
    )
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or "Unable to close verified disposable AE project")
    return process.stdout.strip() or "closed_verified_disposable"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--shared-ae", action="store_true", help="Use one already-running AE session instead of a dedicated process per project")
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    manifest = json.loads(manifest_path.read_text())
    batch_dir = manifest_path.parent
    status_path = batch_dir / "batch-status.json"
    status = {
        "schemaVersion": 1,
        "manifest": str(manifest_path),
        "startedAt": datetime.now(timezone.utc).isoformat(),
        "rendering": False,
        "results": [],
    }
    for entry in manifest["projects"]:
        result = {"id": entry["id"], "status": "pending"}
        status["results"].append(result)
        write_json(status_path, status)
        source = Path(entry["source"])
        staged = Path(entry["staged"])
        expected = entry["sha256"]
        source_before = sha256_file(source)
        staged_before = sha256_file(staged)
        result["sourceSha256Before"] = source_before
        result["stagedSha256Before"] = staged_before
        if source_before != expected or staged_before != expected:
            result["status"] = "blocked_hash_mismatch"
            write_json(status_path, status)
            continue
        job_path = resolve_from(batch_dir, entry["job"])
        report_path = report_path_for_job(job_path)
        result["job"] = str(job_path)
        result["report"] = str(report_path)
        if report_path.is_file():
            report = json.loads(report_path.read_text())
            if report.get("ok"):
                result["status"] = "complete_reused"
                result["compositionCount"] = len(report.get("compositions", []))
                result["itemCount"] = len(report.get("items", []))
                write_json(status_path, status)
                continue
            attempt_dir = batch_dir / "failed-attempts" / entry["id"] / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            attempt_dir.mkdir(parents=True, exist_ok=False)
            report_path.replace(attempt_dir / report_path.name)
            script_path = report_path.parent / "executed-inspector.jsx"
            if script_path.exists():
                script_path.replace(attempt_dir / script_path.name)
        started = time.monotonic()
        command = [sys.executable, str(INSPECTOR), "inspect", str(job_path), "--summary-only"]
        if not args.shared_ae:
            command.append("--dedicated-ae")
        process = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        result["elapsedSeconds"] = round(time.monotonic() - started, 3)
        result["returnCode"] = process.returncode
        result["stdout"] = process.stdout[-4000:]
        result["stderr"] = process.stderr[-4000:]
        if report_path.is_file():
            report = json.loads(report_path.read_text())
            result["status"] = "complete" if report.get("ok") else "failed"
            result["compositionCount"] = len(report.get("compositions", []))
            result["itemCount"] = len(report.get("items", []))
            result["error"] = report.get("error")
            if args.shared_ae and report.get("ok"):
                try:
                    result["sharedAECleanup"] = close_verified_shared_project(report_path)
                except (OSError, RuntimeError, subprocess.SubprocessError) as error:
                    result["status"] = "blocked_shared_ae_cleanup"
                    result["cleanupError"] = str(error)
                    status["systemicBlocker"] = "unable_to_close_verified_disposable_project"
        else:
            result["status"] = "failed_no_report"
        source_after = sha256_file(source)
        result["sourceSha256After"] = source_after
        result["sourceUnchanged"] = source_after == source_before == expected
        if not result["sourceUnchanged"]:
            result["status"] = "blocked_source_changed"
            status["systemicBlocker"] = "source_hash_changed"
        elif "Save the current project" in (result.get("error") or ""):
            status["systemicBlocker"] = "after_effects_has_dirty_or_rendering_project"
        write_json(status_path, status)
        if status.get("systemicBlocker"):
            break
    status["finishedAt"] = datetime.now(timezone.utc).isoformat()
    counts = {}
    for row in status["results"]:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    status["counts"] = counts
    write_json(status_path, status)
    print(json.dumps({"status": str(status_path), "counts": counts, "systemicBlocker": status.get("systemicBlocker")}, indent=2))
    if status.get("systemicBlocker"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
