#!/usr/bin/env python3
"""Fail-closed P7 evaluation receipts; never authorizes selection or rendering."""

from __future__ import annotations

import hashlib
import json
import argparse
from pathlib import Path
from typing import Any


SCHEMA = "astra-p7-quality-thresholds@1"
BASE = "c4b5ce0e49952c2fdbb36f30af01f73ace62fc12"
RATIO_GATES = {
    "criticalPositiveCandidateRecall", "overallPositiveCandidateRecallMinimum",
    "hardConstraintNegativeRejection", "noTemplateAndBrollRouteCorrectness", "semanticFidelity",
}
COUNT_GATES = {
    "maximumUnsupportedNativeFitClaims", "maximumHiddenValidatedAlternatives",
    "maximumUnknownToExhaustedTransitions",
}


def _read(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _source(path: Path) -> dict[str, Any]:
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError(f"P7 input missing: {path}")
    return {"path": path.as_posix(), "sha256": _sha(path), "bytes": path.stat().st_size}


def validate_thresholds(value: dict[str, Any]) -> None:
    if value.get("schemaVersion") != SCHEMA or value.get("baseCommit") != BASE:
        raise ValueError("P7 thresholds use the wrong schema or P6 boundary")
    if value.get("labelsMustPrecedeTuning") is not True:
        raise ValueError("P7 labels must precede tuning")
    if value.get("selectionAuthorized") is not False or value.get("renderingAuthorized") is not False:
        raise ValueError("P7 thresholds cannot authorize selection or rendering")
    gates = value.get("gates") or {}
    if set(gates) != RATIO_GATES | COUNT_GATES:
        raise ValueError("P7 threshold gate set is incomplete or unknown")
    if any(type(gates[key]) not in (int, float) or not 0 <= gates[key] <= 1 for key in RATIO_GATES):
        raise ValueError("P7 ratio threshold is invalid")
    if any(type(gates[key]) is not int or gates[key] < 0 for key in COUNT_GATES):
        raise ValueError("P7 count threshold is invalid")
    effort = value.get("reviewEffort") or {}
    if effort.get("mode") != "measure_baseline_only" or effort.get("improvementClaimAllowed") is not False:
        raise ValueError("P7 cannot claim unmeasured review-effort improvement")


def build_pre_review(threshold_path: Path, package_path: Path, release_path: Path,
                     p6_receipt_path: Path) -> dict[str, Any]:
    thresholds = _read(threshold_path)
    validate_thresholds(thresholds)
    if _read(package_path).get("packageId") != thresholds.get("heldOutPackageId"):
        raise ValueError("held-out package identity differs from frozen thresholds")
    if _read(release_path).get("packageId") != thresholds.get("heldOutPackageId"):
        raise ValueError("release identity differs from frozen thresholds")
    if _read(p6_receipt_path).get("stage") != "P6":
        raise ValueError("P7 requires the accepted P6 receipt")
    return {
        "schemaVersion": "astra-p7-pre-review@1",
        "status": "pending_blind_editor_labels",
        "baseCommit": BASE,
        "heldOutPackageId": thresholds["heldOutPackageId"],
        "inputs": {
            "threshold": _source(threshold_path), "package": _source(package_path),
            "release": _source(release_path), "p6": _source(p6_receipt_path),
        },
        "preliminaryRunExcluded": True,
        "migrationAuthorized": False,
        "selectionAuthorized": False,
        "renderingAuthorized": False,
    }


def validate_pre_review(receipt: dict[str, Any]) -> None:
    if receipt.get("schemaVersion") != "astra-p7-pre-review@1":
        raise ValueError("unsupported P7 pre-review receipt")
    if receipt.get("status") != "pending_blind_editor_labels" or receipt.get("baseCommit") != BASE:
        raise ValueError("P7 pre-review status or boundary changed")
    if receipt.get("preliminaryRunExcluded") is not True:
        raise ValueError("preliminary run was not excluded")
    if any(receipt.get(key) is not False for key in ("migrationAuthorized", "selectionAuthorized", "renderingAuthorized")):
        raise ValueError("P7 pre-review receipt cannot authorize migration, selection or rendering")
    for key in ("threshold", "package", "release", "p6"):
        source = receipt.get("inputs", {}).get(key) or {}
        path = Path(source.get("path", ""))
        if not path.is_file() or _sha(path) != source.get("sha256") or path.stat().st_size != source.get("bytes"):
            raise ValueError(f"P7 input is missing or stale: {key}")
    thresholds = _read(Path(receipt["inputs"]["threshold"]["path"]))
    validate_thresholds(thresholds)
    if thresholds["heldOutPackageId"] != receipt.get("heldOutPackageId"):
        raise ValueError("held-out identity changed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("pre-review", "validate-pre-review"))
    parser.add_argument("--thresholds", type=Path)
    parser.add_argument("--package", type=Path)
    parser.add_argument("--release", type=Path)
    parser.add_argument("--p6", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "pre-review":
        if not all((args.thresholds, args.package, args.release, args.p6)):
            parser.error("pre-review requires --thresholds, --package, --release and --p6")
        receipt = build_pre_review(args.thresholds, args.package, args.release, args.p6)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    else:
        receipt = _read(args.output)
    validate_pre_review(receipt)
    print(json.dumps({"status": receipt["status"], "heldOutPackageId": receipt["heldOutPackageId"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
