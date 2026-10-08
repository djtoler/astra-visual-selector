import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pipeline import storypackage_matching_handoff as contract
from pipeline import storypackage_candidate_gallery as gallery
from pipeline import focused_candidate_diversity as focused
from pipeline import matching_agent
from tests.test_astra_p0_p2 import rebased_gallery

ROOT = Path(__file__).resolve().parents[1]


class P2ProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        legacy = rebased_gallery("jayz-drake-settle-it-v13")
        cls.adapter_path = Path(legacy["sources"]["adapter"]["path"])
        from pipeline import storypackage_splitter
        proposals = storypackage_splitter.build(
            json.loads(cls.adapter_path.read_text()), source_path=cls.adapter_path)
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.proposals_path = Path(cls.tempdir.name) / "current-proposals.json"
        cls.proposals_path.write_text(json.dumps(proposals))

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def source_paths(self):
        cls = type(self)
        if not hasattr(cls, "proposals_path"):
            cls.setUpClass()
        return cls.proposals_path, cls.adapter_path

    def projection(self):
        return contract.build_projection(*self.source_paths())

    def test_projection_omission_mutation_and_receipt_fail_closed(self):
        original = self.projection()
        contract.validate_projection(original)
        for mutation in ("omission", "value", "receipt", "version"):
            broken = copy.deepcopy(original)
            if mutation == "omission": del broken["tasks"][0]["obligations"]
            elif mutation == "value": broken["tasks"][0]["values"] = [{"value": 0}]
            elif mutation == "receipt": del broken["receipt"]
            else: broken["version"] = "stale"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                contract.validate_projection(broken)

    def test_all_consumers_bind_same_projection_and_routes(self):
        pp, ap = self.source_paths()
        source = json.loads(pp.read_text())
        with patch.object(gallery, "_local_relevance", return_value=([{}] * len(source["taskProposals"]), {"scope": "test_no_model"})):
            result = gallery.build(proposals_path=pp, adapter_path=ap)
        requirements = matching_agent._requirements(source, projection=result["taskProjection"])
        ids = [r["taskId"] for r in result["tasks"] if not r["routeDisposition"]["templateEligible"]]
        self.assertEqual(ids, [])
        self.assertTrue(all(not r["candidates"] for r in result["tasks"] if r["taskId"] in ids))
        with tempfile.TemporaryDirectory() as folder:
            gp, qp = Path(folder) / "gallery.json", Path(folder) / "queue.json"
            gp.write_text(json.dumps(result))
            qp.write_text(json.dumps({"packageId": result["packageId"], "taskIds": ids,
                                     "selectionAuthorized": False, "renderingAuthorized": False}))
            audit = focused.build(gp, qp)
            self.assertEqual(audit["taskProjection"]["receipt"], result["taskProjection"]["receipt"])
            self.assertEqual(audit["tasks"], [])
            del result["taskProjection"]["receipt"]
            gp.write_text(json.dumps(result))
            with self.assertRaises(ValueError): focused.build(gp, qp)
        self.assertEqual(requirements["taskProjection"]["receipt"], self.projection()["receipt"])

    def test_foreign_admissions_fail(self):
        pp, ap = self.source_paths()
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "admissions.json"
            p.write_text(json.dumps({"packageId": "foreign@1", "admissions": [{"taskId": self.projection()["tasks"][0]["id"], "candidateId": "x"}]}))
            with self.assertRaises(ValueError): contract.build_projection(pp, ap, admissions_path=p)

    def test_changed_source_bytes_fail(self):
        pp, ap = self.source_paths()
        with tempfile.TemporaryDirectory() as folder:
            local = Path(folder) / "proposal.json"
            local.write_bytes(pp.read_bytes())
            projected = contract.build_projection(local, ap)
            local.write_text("{}")
            with self.assertRaises(ValueError): contract.validate_projection(projected)

    def test_consumer_reconstruction_even_with_new_hash_fails(self):
        from pipeline.visualtask_matching import template_candidates
        projected = self.projection()["tasks"][0]
        projected["quote"] = "An invented replacement."
        projected["taskContractReceipt"]["taskSha256"] = contract._digest(
            {k: v for k, v in projected.items() if k != "taskContractReceipt"})
        with self.assertRaisesRegex(ValueError, "reconstruction"):
            template_candidates(projected, {}, {})

    def test_dropping_projection_version_cannot_bypass_retrieval_gate(self):
        from pipeline.visualtask_matching import template_candidates
        projected = self.projection()["tasks"][0]
        del projected["projectionVersion"]
        with self.assertRaises(ValueError): template_candidates(projected, {}, {})

    def test_media_and_cohort_demand_remain_required(self):
        pp, ap = self.source_paths()
        source = json.loads(pp.read_text())
        row = copy.deepcopy(source["taskProposals"][0])
        row["entityRefs"] = []
        row["primaryPresentationOperation"] = "concept_statement"
        row["presentationOperations"] = ["concept_statement"]
        row["cohortRefs"] = [{"cohort": "example@1", "representedBy": [{"kind": "person", "entity": "example"}]}]
        row["obligations"] = [{"mediaNeeds": [{"kind": "document", "required": True}]}]
        source["taskProposals"] = [row]
        with tempfile.TemporaryDirectory() as folder:
            local = Path(folder) / "proposals.json"
            local.write_text(json.dumps(source))
            projection = contract.build_projection(local, ap)
            result = matching_agent._requirements(source, projection=projection)
            self.assertTrue(result["tasks"][0]["media"]["required"])
            self.assertTrue(result["tasks"][0]["cohortMediaNeeds"])

    def test_prior_choices_cannot_enter_projection(self):
        row = {"taskProposalId": "new", "job": "assert_without_data", "priorSelections": ["old-story-choice"]}
        with self.assertRaisesRegex(ValueError, "prior-story"):
            contract.project_task(row, package_id="new@1", source_digest="1" * 64, admissions=[])

    def test_global_prior_picks_cannot_change_new_slate(self):
        from pipeline import visualtask_matching as matcher
        task = next(row for row in self.projection()["tasks"] if row["routeDisposition"].get("templateEligible") is not False)
        pool = {row["id"]: row for row in matcher.C.load(content_class="*")}
        baseline = matcher.template_candidates(task, {}, pool)
        with patch.object(matcher.C, "_picked_ids", return_value=set(pool)) as global_picks:
            changed = matcher.template_candidates(task, {}, pool)
        self.assertEqual(baseline, changed)
        global_picks.assert_not_called()

    def test_missing_or_failed_upstream_stage_receipt_fails(self):
        from tests.verify_astra_stage import verify
        original = Path.read_text
        def altered(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name == "p1-receipt.json":
                value = json.loads(text)
                value["status"] = "pending"
                return json.dumps(value)
            return text
        with patch.object(Path, "read_text", altered), self.assertRaisesRegex(ValueError, "incomplete"):
            verify("P1")

    def test_quote_obligations_override_question_and_keep_attribution(self):
        pp, ap = self.source_paths()
        proposals = json.loads(pp.read_text())
        row = copy.deepcopy(proposals["taskProposals"][0])
        row.update(taskProposalId="new.quote", job="attributed_quote", speakerDerived=True,
                   taskText="How did this happen?", presentationOperations=["rhetorical_question"],
                   primaryPresentationOperation="rhetorical_question", routeDisposition={"templateEligible": False},
                   obligations=[{"needsOnScreenText": True, "mustBePerceptible": ["How did this happen?"],
                                 "mediaNeeds": [{"kind": "document", "required": True}]}])
        row["sourceBeats"][0]["speaker"] = {"role": "quote", "entity": "person:example"}
        projected = contract.project_task(row, package_id="new@1", source_digest="1" * 64, admissions=[])
        self.assertEqual(projected["primaryPresentationOperation"], "evidence_presentation")
        self.assertTrue(projected["routeDisposition"]["templateEligible"])
        self.assertEqual(projected["quoteRequirements"]["attribution"], ["person:example"])
        self.assertEqual(projected["quoteRequirements"]["requiredText"], ["How did this happen?"])
        self.assertTrue(projected["mediaNeeds"])

    def test_no_template_reasons_are_distinct(self):
        source = {"packageId": "new@1", "clipRoutes": [], "tasks": [
            {"taskId": "intentional", "sourceBeatIds": [], "routeDisposition": {"templateEligible": False}, "candidates": []},
            {"taskId": "missing", "sourceBeatIds": [], "routeDisposition": {"templateEligible": True}, "candidates": []},
            {"taskId": "unknown", "sourceBeatIds": [], "routeDisposition": {"templateEligible": True}, "candidates": [{"candidateId": "c"}], "fitValidated": False}]}
        reasons = [r["noTemplateReason"] for r in matching_agent._route_plan(source)["scenes"]]
        self.assertEqual(reasons, ["intentional_route", "missing_discovery", "unresolved_feasibility"])


if __name__ == "__main__": unittest.main()
