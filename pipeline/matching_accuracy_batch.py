#!/usr/bin/env python3
"""Evaluate matching evidence from declarative, read-only fixture assertions."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from .matching_contract_gate import enforce_contracts
except ImportError:
    from matching_contract_gate import enforce_contracts

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REQUEST = ROOT / "matching-accuracy" / "batch-001" / "request.json"
DEFAULT_REPORT = ROOT / "matching-accuracy" / "batch-001" / "declarative-report.json"
ALLOWED_OPERATORS = {"equals", "not_equals", "contains", "truthy", "falsey", "length_equals", "length_gte", "distinct"}


def _read(path: Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _source_path(root: Path, source: dict[str, Any]) -> Path:
    path = Path(source.get("path", ""))
    return path if path.is_absolute() else root / path


def validate_request(request: dict[str, Any], *, root: Path = ROOT) -> dict[str, str]:
    if request.get("schemaVersion") != 2:
        raise ValueError("unsupported declarative accuracy schema")
    if request.get("activationState") != "review_only_not_connected":
        raise ValueError("accuracy batch must remain review-only")
    if request.get("selectionAuthorized") is not False or request.get("renderingAuthorized") is not False:
        raise ValueError("accuracy batch cannot authorize selection or rendering")
    cases = request.get("cases") or []
    case_ids = [row.get("id") for row in cases]
    if not cases or any(not case_id for case_id in case_ids) or len(case_ids) != len(set(case_ids)):
        raise ValueError("accuracy batch requires distinct nonempty case IDs")
    availability: dict[str, str] = {}
    for name, source in (request.get("sources") or {}).items():
        if not isinstance(source, dict) or not source.get("path"):
            raise ValueError(f"invalid bound source: {name}")
        path = _source_path(root, source)
        if not path.is_file():
            if source.get("required", True):
                raise ValueError(f"bound source missing: {name}: {path}")
            availability[name] = "pending"
            continue
        actual = _sha(path)
        if source.get("sha256") is not None and actual != source["sha256"]:
            raise ValueError(f"bound source changed: {name}: {actual}")
        availability[name] = "available"
    source_names = set((request.get("sources") or {}))
    for case in cases:
        record = case.get("record") or {}
        required_sources = set(case.get("requiresSources") or [record.get("source")])
        if None in required_sources or not required_sources <= source_names:
            raise ValueError(f"case references unknown source: {case.get('id')}")
        assertions = case.get("assertions") or []
        if not assertions:
            raise ValueError(f"case has no declarative assertions: {case.get('id')}")
        for assertion in assertions:
            if assertion.get("operator") not in ALLOWED_OPERATORS:
                raise ValueError(f"unsupported assertion operator: {assertion.get('operator')}")
            if not isinstance(assertion.get("path", []), list):
                raise ValueError(f"assertion path must be a list: {case.get('id')}")
    return availability


def _at(value: Any, path: list[Any]) -> Any:
    current = value
    for token in path:
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and isinstance(token, int) and 0 <= token < len(current):
            current = current[token]
        else:
            raise ValueError(f"declarative path does not resolve: {path}")
    return current


def _record(dataset: Any, spec: dict[str, Any]) -> Any:
    value = _at(dataset, spec.get("path") or [])
    where = spec.get("where")
    if where is None:
        return value
    if not isinstance(value, list) or not isinstance(where, dict) or not where:
        raise ValueError("record filter requires a list and a nonempty equality object")
    rows = [row for row in value if isinstance(row, dict) and all(row.get(key) == expected for key, expected in where.items())]
    if len(rows) != 1:
        raise ValueError(f"record filter expected one result, found {len(rows)}")
    return rows[0]


def _assert(actual: Any, assertion: dict[str, Any]) -> bool:
    operator, expected = assertion["operator"], assertion.get("expected")
    if operator == "equals": return actual == expected
    if operator == "not_equals": return actual != expected
    if operator == "contains": return expected in actual
    if operator == "truthy": return bool(actual)
    if operator == "falsey": return not actual
    if operator == "length_equals": return len(actual) == expected
    if operator == "length_gte": return len(actual) >= expected
    if operator == "distinct": return len(actual) == len({json.dumps(item, sort_keys=True) for item in actual})
    raise ValueError(f"unsupported assertion operator: {operator}")


def evaluate(request: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    contract_receipt = enforce_contracts("matching_accuracy_batch.evaluate")
    availability = validate_request(request, root=root)
    datasets = {name: _read(_source_path(root, source)) for name, source in request["sources"].items() if availability[name] == "available"}
    results: list[dict[str, Any]] = []
    for case in request["cases"]:
        required_sources = case.get("requiresSources") or [case["record"]["source"]]
        unavailable = [name for name in required_sources if availability[name] != "available"]
        if unavailable:
            results.append({"id": case["id"], "expected": case.get("expected"), "status": "pending", "pendingSources": unavailable, "reason": case.get("pendingReason") or "One or more declared evaluation sources are not available yet.", "assertions": []})
            continue
        spec = case["record"]
        record = _record(datasets[spec["source"]], spec)
        checks = []
        for assertion in case["assertions"]:
            actual = _at(record, assertion.get("path") or [])
            passed = _assert(actual, assertion)
            checks.append({"id": assertion.get("id"), "path": assertion.get("path") or [], "operator": assertion["operator"], "expected": assertion.get("expected"), "actual": actual, "status": "pass" if passed else "fail"})
        result = dict(record) if isinstance(record, dict) and case.get("copyRecord", False) else {}
        result.update({"id": case["id"], "expected": case.get("expected"), "status": "pass" if all(row["status"] == "pass" for row in checks) else "fail", "assertions": checks})
        results.append(result)
    counts = {state: sum(row["status"] == state for row in results) for state in ("pass", "fail", "pending")}
    return {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": 2, "batchId": request["batchId"],
        "activationState": "review_only_not_connected", "selectionAuthorized": False, "renderingAuthorized": False,
        "sourceHashes": {name: source.get("sha256") for name, source in request["sources"].items() if availability[name] == "available"},
        "sourceAvailability": availability,
        "summary": {"total": len(results), "passed": counts["pass"], "failed": counts["fail"], "pending": counts["pending"], "allPassed": counts["pass"] == len(results)},
        "cases": results,
        "nextBoundary": request.get("nextBoundary") or "Resolve failed or pending evidence without authorizing selection or rendering.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, default=DEFAULT_REQUEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = evaluate(_read(args.request))
    if not args.check:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(dumps(report), encoding="utf-8")
    print(dumps(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
