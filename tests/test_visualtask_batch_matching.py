import copy
import json
import unittest
from pathlib import Path

from pipeline import visualtask_batch_matching as subject


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "visualtask_batch_matching"


class FullVisualTaskBatchMatching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current = subject.build(FIXTURES / "current-request.json")
        cls.synthetic = subject.build(FIXTURES / "synthetic-request.json")

    def test_current_fixture_processes_every_visual_task(self):
        source = json.loads((ROOT / "grammar" / "visual-tasks.json").read_text())
        self.assertEqual(self.current["counts"]["visualTasks"], len(source["tasks"]))
        self.assertEqual(
            [row["taskId"] for row in self.current["tasks"]],
            [row["id"] for row in source["tasks"]],
        )

    def test_unrelated_story_uses_the_same_runner(self):
        self.assertEqual(self.synthetic["storyId"], "museum-opening")
        self.assertEqual(self.synthetic["counts"]["visualTasks"], 2)
        self.assertEqual(
            [row["taskId"] for row in self.synthetic["tasks"]],
            ["museum-opening.rule", "museum-opening.host"],
        )

    def test_template_and_media_verdicts_are_separate(self):
        by_id = {row["taskId"]: row for row in self.synthetic["tasks"]}
        text_only = by_id["museum-opening.rule"]
        host = by_id["museum-opening.host"]
        self.assertEqual(text_only["templateResult"]["fitVerdict"], "native_fit")
        self.assertEqual(host["templateResult"]["fitVerdict"], "adapted_fit")
        self.assertEqual(text_only["mediaResult"]["availabilityVerdict"], "not_required")
        self.assertIn(host["mediaResult"]["availabilityVerdict"], {"available", "unavailable"})
        self.assertNotIn("mediaResult", text_only["templateResult"])
        self.assertNotIn("templateResult", host["mediaResult"])

    def test_candidate_fit_uses_exact_evidence_without_selecting(self):
        by_id = {row["taskId"]: row for row in self.synthetic["tasks"]}
        host = by_id["museum-opening.host"]["templateResult"]
        by_candidate = {row["candidateId"]: row["fitAssessment"] for row in host["candidates"]}
        self.assertEqual(by_candidate["history-slideshow-envato--scene-001"]["verdict"], "adapted_fit")
        self.assertEqual(by_candidate["glass-lower-thirds--scene-001"]["verdict"], "incompatible")
        self.assertEqual(by_candidate["photo-slideshow-memories-envato--scene-010"]["verdict"], "conditional")
        self.assertIn(
            "exact_child_validation_deferred_until_use",
            {gap["type"] for gap in by_candidate["photo-slideshow-memories-envato--scene-010"]["gaps"]},
        )
        self.assertFalse(self.synthetic["selectionAuthorized"])
        self.assertFalse(self.synthetic["renderingAuthorized"])

    def test_editor_reviewed_current_treatment_is_conditional_not_selected(self):
        by_id = {row["taskId"]: row for row in self.current["tasks"]}
        result = by_id["02-02a.main"]["templateResult"]
        self.assertEqual(result["fitVerdict"], "conditional")
        candidate = next(
            row for row in result["candidates"]
            if row["candidateId"] == "screen-mockup-rfx--review-002"
        )
        self.assertEqual(candidate["fitAssessment"]["verdict"], "conditional")
        self.assertTrue(candidate["fitAssessment"]["evidence"]["editorReviewedTreatment"])

    def test_completed_data_assignments_reach_current_template_checks(self):
        requirements = json.loads((ROOT / "grammar" / "visual-task-technical-requirements.json").read_text())
        data_tasks = {row["taskId"] for row in requirements["tasks"] if (row.get("dataRequirements") or {}).get("requiredEncodings")}
        by_id = {row["taskId"]: row for row in self.current["tasks"]}
        self.assertEqual(len(data_tasks), 28)
        for task_id in by_id:
            gap_types = {gap["type"] for gap in by_id[task_id]["templateResult"]["gaps"]}
            self.assertNotIn("task_required_data_fields", gap_types, task_id)
        self.assertIn("dataAssignments", self.current["sources"])
        self.assertFalse(self.current["selectionAuthorized"])
        self.assertFalse(self.current["renderingAuthorized"])

    def test_story_matching_handoff_replaces_generic_media_and_text_unknowns(self):
        self.assertIn("storyMatchingHandoff", self.current["sources"])
        by_id = {row["taskId"]: row for row in self.current["tasks"]}
        opening = by_id["01-01.subject"]
        self.assertEqual(opening["storyRequirements"]["text"]["fieldCount"], 2)
        self.assertEqual(opening["storyRequirements"]["media"]["simultaneous"], 2)
        self.assertNotIn(
            "treatment_required_text_fields",
            {gap["type"] for gap in opening["templateResult"]["gaps"]},
        )
        unknown = by_id["30-30a.main"]["storyRequirements"]["media"]["simultaneous"]
        self.assertEqual(unknown, {"unknown": "the narration does not say how many pre-streaming rappers"})
        self.assertEqual(self.current["counts"]["storyHandoffTasks"], 41)

    def test_story_identity_does_not_become_a_media_library_requirement_without_a_kind(self):
        by_id = {row["taskId"]: row for row in self.current["tasks"]}
        labels_only = by_id["09-09.main"]
        self.assertEqual(labels_only["storyRequirements"]["media"]["kinds"], [])
        self.assertEqual(labels_only["mediaResult"]["availabilityVerdict"], "not_required")
        self.assertEqual(labels_only["mediaResult"]["entities"], [])
        self.assertNotIn(
            "task_required_media_slot_count",
            {gap["type"] for gap in labels_only["templateResult"]["gaps"]},
        )
        required = by_id["27-27.main"]
        self.assertEqual(required["storyRequirements"]["media"]["kinds"], ["footage", "person"])
        self.assertEqual(required["mediaResult"]["availabilityVerdict"], "available")
        self.assertEqual(required["mediaResult"]["gaps"], [])

    def test_story_cohort_is_expanded_before_media_availability(self):
        by_id = {row["taskId"]: row for row in self.current["tasks"]}
        population = by_id["03-03.opening_chart"]["mediaResult"]
        self.assertEqual(len(population["entities"]), 93)
        self.assertNotEqual(population["availabilityVerdict"], "unresolved")
        self.assertNotIn(
            "entity_or_non_entity_media_query",
            {gap["type"] for gap in population["gaps"]},
        )

    def test_source_specific_non_entity_media_returns_a_typed_shortage(self):
        by_id = {row["taskId"]: row for row in self.current["tasks"]}
        festival = by_id["07-07.main"]["mediaResult"]
        self.assertEqual(festival["availabilityVerdict"], "unavailable")
        self.assertIn("source_specific_media", {gap["type"] for gap in festival["gaps"]})
        era_broll = by_id["30-30b.main"]["mediaResult"]
        self.assertEqual(era_broll["availabilityVerdict"], "unavailable")
        self.assertIn("source_specific_media", {gap["type"] for gap in era_broll["gaps"]})

    def test_family_capability_never_claims_native_fit_without_exact_child_evidence(self):
        by_id = {row["taskId"]: row for row in self.current["tasks"]}
        candidate = next(
            row for row in by_id["30-30b.main"]["templateResult"]["candidates"]
            if row["candidateId"] == "glass-lower-thirds--scene-001"
        )
        assessment = candidate["fitAssessment"]
        self.assertEqual(assessment["verdict"], "conditional")
        self.assertEqual(assessment["evidence"]["technicalBasis"], "catalog_family_capability")
        self.assertNotEqual(assessment["verdict"], "native_fit")

    def test_batch_reconciles_every_bound_family_before_reporting_a_shortage(self):
        by_id = {row["taskId"]: row for row in self.current["tasks"]}
        exhaustive = by_id["17-17.main"]["templateResult"]["candidates"]
        self.assertEqual(len(exhaustive), 17)
        self.assertEqual(len({row["candidateId"] for row in exhaustive}), 17)

    def test_prior_selected_candidate_is_admitted_but_dismissed_candidates_are_not(self):
        by_id = {row["taskId"]: row for row in self.current["tasks"]}
        candidates = {
            row["candidateId"]: row
            for row in by_id["02-02b.currensy_catalog"]["templateResult"]["candidates"]
        }
        admitted = candidates["archive3-looped-slideshow-background--review-001"]
        self.assertEqual(
            admitted["bindingProvenance"]["source"],
            "prior_editor_review_reconciliation",
        )
        dismissed = "archive3-carousel-flow-loops-2026-09-15-08-02-14-utc--review-004"
        self.assertNotIn(dismissed, candidates)

        tasks = json.loads((ROOT / "grammar" / "visual-tasks.json").read_text())["tasks"]
        task = next(row for row in tasks if row["id"] == "17-17.main")
        bindings = json.loads((ROOT / "grammar" / "bindings.json").read_text())
        pool = {row["id"]: row for row in subject.matching.C.load()}
        compact = subject.matching.template_candidates(task, bindings, pool)
        self.assertEqual(len(compact), 10)

    def test_every_candidate_and_media_result_has_task_provenance(self):
        for artifact in (self.current, self.synthetic):
            for task in artifact["tasks"]:
                for candidate in task["templateResult"]["candidates"]:
                    provenance = candidate["candidateMatchingProvenance"]
                    self.assertEqual(provenance["taskId"], task["taskId"])
                self.assertEqual(
                    task["mediaResult"]["candidateMatchingProvenance"]["taskId"],
                    task["taskId"],
                )

    def test_conditional_media_requires_a_typed_missing_gap(self):
        broken = copy.deepcopy(self.synthetic)
        broken["tasks"][0]["mediaResult"]["availabilityVerdict"] = "conditional"
        with self.assertRaisesRegex(ValueError, "typed missing gap"):
            subject.validate(broken, verify_sources=False)

    def test_task_fit_cannot_disagree_with_candidate_evidence(self):
        broken = copy.deepcopy(self.synthetic)
        broken["tasks"][0]["templateResult"]["fitVerdict"] = "unresolved"
        broken["counts"]["templateVerdicts"] = {"adapted_fit": 1, "unresolved": 1}
        with self.assertRaisesRegex(ValueError, "template-fit verdict is stale"):
            subject.validate(broken, verify_sources=False)

    def test_scope_mismatch_fails_closed(self):
        values = {
            "storyPackage": json.loads((FIXTURES / "synthetic-story-package.json").read_text()),
            "visualTasks": json.loads((FIXTURES / "synthetic-visual-tasks.json").read_text()),
            "technicalRequirements": json.loads((FIXTURES / "synthetic-technical-requirements.json").read_text()),
            "bindings": json.loads((ROOT / "grammar" / "bindings.json").read_text()),
        }
        values["technicalRequirements"]["tasks"].pop()
        with self.assertRaisesRegex(ValueError, "scope mismatch"):
            subject._validate_scope(values)

    def test_production_runner_contains_no_fixture_identifiers(self):
        source = (ROOT / "pipeline" / "visualtask_batch_matching.py").read_text()
        self.assertNotIn("28-28", source)
        self.assertNotIn("museum-opening", source)
        self.assertNotIn("year-seventeen", source)


if __name__ == "__main__":
    unittest.main()
