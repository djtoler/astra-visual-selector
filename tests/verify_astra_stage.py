"""Verify stage artifact bindings before continuing the authorized sequence."""
import hashlib
import json
from pathlib import Path
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def verify(stage):
    folder = "astra-p0-p2" if stage in {"P0", "P1", "P2"} else "astra-p5" if stage == "P5" else "astra-p6" if stage == "P6" else "astra-p3-p4"
    path = ROOT / f"reports/{folder}/{stage.lower()}-receipt.json"
    receipt = json.loads(path.read_text())
    if receipt.get("stage") != stage or receipt.get("status") != "complete":
        raise ValueError("upstream receipt missing or incomplete")
    revision = subprocess.check_output(["git", "log", "-1", "--format=%H", "--", str(path.relative_to(ROOT))], cwd=ROOT, text=True).strip()
    for row in receipt.get("inputs", {}).get("implementationFiles", []):
        data = subprocess.check_output(["git", "show", f"{revision}:{row['path']}"], cwd=ROOT) if revision else (ROOT / row["path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError("stage implementation digest mismatch")
    for row in receipt["outputs"]:
        if hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("stage output missing or stale: " + row["path"])
    for row in receipt.get("inputs", {}).get("sourceAndCatalogFiles", []):
        source = ROOT / row["path"]
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("stage source/input digest mismatch: " + row["path"])
    predecessor = receipt.get("upstreamReceipt")
    if predecessor:
        previous = verify(predecessor["stage"])
        if hashlib.sha256(previous.read_bytes()).hexdigest() != predecessor["sha256"]:
            raise ValueError("upstream receipt digest mismatch")
    for predecessor in receipt.get("upstreamReceipts") or []:
        previous = verify(predecessor["stage"])
        if hashlib.sha256(previous.read_bytes()).hexdigest() != predecessor["sha256"]:
            raise ValueError("upstream receipt digest mismatch")
    sys.path.insert(0, str(ROOT))
    from tests.test_astra_p0_p2 import validate_calibration
    validate_calibration(json.loads((ROOT / "reports/astra-p0-p2/calibration-manifest.json").read_text()))
    return path


if __name__ == "__main__":
    verify(sys.argv[1])
    print("Stage receipt bindings and immutable evidence passed.")
