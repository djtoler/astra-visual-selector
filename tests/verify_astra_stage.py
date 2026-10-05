"""Verify stage artifact bindings before continuing the authorized sequence."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def verify(stage):
    path = ROOT / f"reports/astra-p0-p2/{stage.lower()}-receipt.json"
    receipt = json.loads(path.read_text())
    if receipt.get("stage") != stage or receipt.get("status") != "complete":
        raise ValueError("upstream receipt missing or incomplete")
    for row in receipt["outputs"]:
        if hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("stage output missing or stale: " + row["path"])
    predecessor = receipt.get("upstreamReceipt")
    if predecessor:
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
