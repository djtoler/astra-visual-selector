"""Deterministic P3 semantic replay; no provider, ranking or native execution."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline import storypackage_splitter as splitter
from tests.test_astra_p0_p2 import digest


def build():
    cases = []
    for name in ("year-seventeen-regression", "future-regression", "jayz-drake-heldout"):
        folder = ROOT / "reports/matching-agent-evaluation-20261004" / name
        path = folder / "10-storypackage-adapter.json"
        if not path.is_file():
            raise ValueError("pinned calibration adapter missing: " + str(path))
        adapter = json.loads(path.read_text())
        baseline_path = folder / "20-visualtask-proposals.json"
        baseline = json.loads(baseline_path.read_text())
        current = splitter.build(adapter, source_path=path)
        claims = {r["claimId"]: r for r in adapter["claims"]}
        old_by_id = {r["taskProposalId"]: r for r in baseline["taskProposals"]}
        mutations = []
        for row in current["taskProposals"]:
            if row.get("proposalSpan"):
                span = row["proposalSpan"]
                script = adapter["script"]["text"]
                if row["taskText"] != script[span["start"]:span["start"] + span["len"]]:
                    raise ValueError("task source text/span mismatch: " + row["taskProposalId"])
            expected = [{"claimId": cid, **v} for cid in row["claimIds"] for v in claims[cid].get("values") or []]
            if row["values"] != expected:
                raise ValueError("typed source value/role changed")
            previous = old_by_id.get(row["taskProposalId"])
            if previous is None or any(previous.get(key) != row.get(key) for key in ("taskText", "claimIds", "primaryPresentationOperation")):
                mutations.append({"taskId": row["taskProposalId"], "oldText": (previous or {}).get("taskText"),
                                  "newText": row["taskText"], "claimIds": row["claimIds"],
                                  "proposalSpan": row.get("proposalSpan"), "primaryOperation": row["primaryPresentationOperation"]})
        cases.append({"packageId": adapter["packageId"], "source": {"path": str(path.relative_to(ROOT)), "sha256": digest(path)},
                      "baseline": {"path": str(baseline_path.relative_to(ROOT)), "sha256": digest(baseline_path)},
                      "baselineTasks": len(baseline["taskProposals"]), "newCounts": current["counts"],
                      "sourceValuesUnchanged": True, "exactSpansChecked": True, "changedTasks": mutations,
                      "unverifiedSourceFacts": sum(g["gap"] == "source_fact_unverified" for g in current["gaps"])})
    return {"schemaVersion": "astra-semantic-shadow@1", "cases": cases,
            "reviewState": "proposal_requires_editor_review", "modelExecution": False,
            "selectionAuthorized": False, "renderingAuthorized": False}


if __name__ == "__main__":
    result = build()
    (ROOT / "reports/astra-p3-p4/p3-shadow.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps([{ "packageId": x["packageId"], "baselineTasks": x["baselineTasks"], "tasks": x["newCounts"]["taskProposals"]} for x in result["cases"]]))
