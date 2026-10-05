"""Replay the P2 semantic shadow through existing consumers without a model."""
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline import storypackage_candidate_gallery as gallery
from pipeline import focused_candidate_diversity as focused
from pipeline import matching_agent
from pipeline import storypackage_matching_handoff as contract
from tests.test_astra_p0_p2 import rebased_gallery


def build():
    cases = []
    for stem in ("future-volksgeist-v12", "jayz-drake-settle-it-v13", "apollo"):
        if stem == "apollo":
            pp = ROOT / "reports/storypackage-02-apollo-task-proposals.json"
            ap = ROOT / "reports/storypackage-02-apollo-adapter.json"
            legacy = None
        else:
            legacy = rebased_gallery(stem)
            pp = Path(legacy["sources"]["taskProposals"]["path"])
            ap = Path(legacy["sources"]["adapter"]["path"])
        proposals = json.loads(pp.read_text())
        # Existing semantic admission and diversity are executed. Relevance is
        # deliberately an empty test input; this is not a live ranking claim.
        with patch.object(gallery, "_local_relevance", return_value=(
            [{}] * len(proposals["taskProposals"]), {"scope": "semantic_shadow_no_model_execution"})):
            result = gallery.build(proposals_path=pp, adapter_path=ap)
        requirements = matching_agent._requirements(proposals, projection=result["taskProjection"])
        with tempfile.TemporaryDirectory() as folder:
            gp, qp = Path(folder) / "gallery.json", Path(folder) / "queue.json"
            gp.write_text(json.dumps(result))
            qp.write_text(json.dumps({"packageId": result["packageId"], "taskIds": [r["taskId"] for r in result["tasks"]],
                                     "selectionAuthorized": False, "renderingAuthorized": False}))
            audit = focused.build(gp, qp)
        assert requirements["taskProjection"] == result["taskProjection"] == audit["taskProjection"]
        indexed = [{r["taskId"]: r for r in consumer["tasks"]} for consumer in (requirements, result, audit)]
        comparisons = []
        for task in result["taskProjection"]["tasks"]:
            rows = [index[task["id"]] for index in indexed]
            for row in rows:
                assert all(row.get(key) == value for key, value in task.items()), task["id"]
            if task["routeDisposition"].get("templateEligible") is False:
                assert not rows[1]["candidates"] and not rows[2]["focusedReviewCandidates"]
            old = next((r for r in (legacy or {}).get("tasks", []) if r["taskId"] == task["id"]), {})
            comparisons.append({"taskId": task["id"], "taskContractReceipt": task["taskContractReceipt"],
                                "allConsumersEqual": True, "templateEligible": task["routeDisposition"].get("templateEligible"),
                                "legacyOmittedFields": [key for key in ("obligations", "continuity", "values", "cohortRefs", "entityRefs") if key not in old]})
        cases.append({"packageId": result["packageId"], "sources": result["taskProjection"]["sources"],
                      "projectionReceipt": result["taskProjection"]["receipt"], "tasks": comparisons,
                      "counts": {"tasks": len(comparisons), "intentionalEmptyRoutes": sum(r["templateEligible"] is False for r in comparisons)}})
    return {"schemaVersion": "astra-projection-shadow@1", "projectionVersion": contract.PROJECTION_VERSION,
            "cases": cases, "modelExecution": False, "rankingEvidence": "No live embedding/model execution; empty relevance controls isolate semantic projection and admission.",
            "selectionAuthorized": False, "renderingAuthorized": False}


if __name__ == "__main__":
    output = ROOT / "reports/astra-p0-p2/p2-shadow-consumers.json"
    result = build()
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps([{"packageId": r["packageId"], **r["counts"]} for r in result["cases"]]))
