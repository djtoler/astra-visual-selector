import copy
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VisualTaskPilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pipeline import visual_tasks

        cls.V = visual_tasks
        cls.artifact = visual_tasks.build_visual_tasks()

    def task(self, task_id):
        return next(t for t in self.artifact["tasks"] if t["id"] == task_id)

    def test_one_default_task_per_beat_and_one_reviewed_split(self):
        self.assertEqual(40, self.artifact["counts"]["sourceBeats"])
        self.assertEqual(41, self.artifact["counts"]["visualTasks"])
        self.assertEqual(["28-28.setup", "28-28.overlap"], [
            t["id"] for t in self.artifact["tasks"]
            if t["sourceBeatId"] == "28-28"
        ])

    def test_documentary_subject_is_not_globally_inherited(self):
        task = self.task("07-07.main")
        self.assertNotIn("Drake", task["entities"]["resolved"])
        self.assertNotIn("Drake", task["entities"]["displayEligible"])
        self.assertFalse(any(
            row.get("entity") == "Drake"
            for row in task["entities"]["implied"]
        ))

    def test_opening_resolves_drake_but_keeps_identity_withheld(self):
        task = self.task("01-01.subject")
        self.assertIn("Drake", task["entities"]["resolved"])
        self.assertNotIn("Drake", task["entities"]["displayEligible"])
        implied = next(x for x in task["entities"]["implied"] if x["entity"] == "Drake")
        self.assertEqual("withheld", implied["displayPolicy"])
        self.assertEqual("user_approved_plan", implied["evidence"]["kind"])

    def test_currensy_context_does_not_inherit_drake(self):
        task = self.task("02-02b.currensy_catalog")
        self.assertEqual(["Curren$y"], task["entities"]["displayEligible"])
        self.assertNotIn("Drake", task["entities"]["resolved"])
        self.assertEqual("other_catalog_identity_withheld", task["entities"]["unresolved"][0]["kind"])

    def test_explicit_entities_carry_shared_registry_ids(self):
        ref = self.task("02-02a.main")["entities"]["explicitRefs"][0]
        self.assertEqual("Curren$y", ref["canonicalName"])
        self.assertEqual("person:curren-y", ref["entityId"])
        self.assertEqual("person", ref["entityType"])

    def test_opening_chart_uses_versioned_93_member_cohort(self):
        task = self.task("03-03.opening_chart")
        cohort = task["entities"]["cohorts"][0]
        self.assertEqual("spotify-opening-chart", cohort["id"])
        self.assertEqual("2026-08-28-status-ok", cohort["version"])
        self.assertEqual(93, cohort["memberCount"])
        self.assertEqual(93, len(task["entities"]["displayEligible"]))
        self.assertIn("Drake", task["entities"]["displayEligible"])
        self.assertEqual(1, task["entities"]["displayEligible"].count("Drake"))

    def test_beat_28_has_separate_setup_and_spatial_tasks(self):
        setup = self.task("28-28.setup")
        overlap = self.task("28-28.overlap")
        self.assertEqual("setup_text", setup["taskRole"])
        self.assertEqual("spatial_comparison", overlap["taskRole"])
        self.assertEqual([], setup["entities"]["displayEligible"])
        self.assertEqual(10, len(overlap["entities"]["displayEligible"]))
        self.assertTrue(setup["quote"].endswith("everyone else's."))
        self.assertTrue(overlap["quote"].startswith("Five clear the left floor."))

    def test_unknown_override_entity_fails_closed(self):
        overrides = json.loads((ROOT / "grammar" / "visual-task-overrides.json").read_text())
        overrides["beats"]["01-01"]["tasks"][0]["impliedEntities"][0]["entity"] = "Not A Roster Person"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "overrides.json"
            path.write_text(json.dumps(overrides))
            with self.assertRaisesRegex(ValueError, "unknown roster entity"):
                self.V.build_visual_tasks(overrides_path=path)

    def test_non_exact_override_span_fails_closed(self):
        overrides = json.loads((ROOT / "grammar" / "visual-task-overrides.json").read_text())
        overrides["beats"]["28-28"]["tasks"][0]["quote"] += " invented"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "overrides.json"
            path.write_text(json.dumps(overrides))
            with self.assertRaisesRegex(ValueError, "exact substring"):
                self.V.build_visual_tasks(overrides_path=path)

    def test_unresolved_subject_is_not_guessed_as_drake(self):
        overrides = json.loads((ROOT / "grammar" / "visual-task-overrides.json").read_text())
        beat = next(x for x in json.loads((ROOT / "pipeline" / "beats-all.json").read_text())["07"] if x["id"] == "07")
        overrides["beats"]["07-07"] = {"tasks": [{
            "suffix": "unresolved_subject",
            "taskRole": "main",
            "quote": beat["quote"],
            "identityCount": 1,
            "unresolved": [{
                "kind": "implied_subject_unresolved",
                "reference": "generic year-seventeen rapper",
                "reason": "No source-bound identity decision was supplied."
            }]
        }]}
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "overrides.json"
            path.write_text(json.dumps(overrides))
            artifact = self.V.build_visual_tasks(overrides_path=path)
        task = next(t for t in artifact["tasks"] if t["id"] == "07-07.unresolved_subject")
        self.assertNotIn("Drake", task["entities"]["resolved"])
        self.assertTrue(any(x["kind"] == "implied_subject_unresolved" for x in task["entities"]["unresolved"]))

    def test_missing_cohort_version_fails_closed(self):
        overrides = json.loads((ROOT / "grammar" / "visual-task-overrides.json").read_text())
        overrides["beats"]["03-03"]["tasks"][0]["cohortRefs"][0]["version"] = "wrong"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "overrides.json"
            path.write_text(json.dumps(overrides))
            with self.assertRaisesRegex(ValueError, "unknown cohort version"):
                self.V.build_visual_tasks(overrides_path=path)

    def test_build_is_byte_deterministic(self):
        first = self.V.dumps(self.V.build_visual_tasks())
        second = self.V.dumps(self.V.build_visual_tasks())
        self.assertEqual(first, second)

    def test_consumer_rejects_tampered_artifact(self):
        broken = copy.deepcopy(self.artifact)
        broken["tasks"][1]["id"] = broken["tasks"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate task id"):
            self.V.consume_visual_tasks(broken)

    def test_consumer_rejects_stale_source_hash(self):
        broken = copy.deepcopy(self.artifact)
        broken["sources"]["beats"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source is missing or stale: beats"):
            self.V.consume_visual_tasks(broken)

    def test_consumer_rejects_content_that_does_not_replay(self):
        broken = copy.deepcopy(self.artifact)
        broken["tasks"][0]["takeaway"] = "tampered"
        with self.assertRaisesRegex(ValueError, "does not replay"):
            self.V.consume_visual_tasks(broken)

    def test_consumer_accepts_written_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "visual-tasks.json"
            self.V.write_visual_tasks(path)
            status = self.V.consume_visual_tasks(json.loads(path.read_text()))
        self.assertEqual(41, status["visualTasks"])
        self.assertEqual(1, status["splitBeats"])
        self.assertEqual(2, status["cohortTasks"])


if __name__ == "__main__":
    unittest.main()
