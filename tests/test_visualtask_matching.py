import copy
import json
import unittest
from pathlib import Path

from pipeline import visualtask_matching as subject


ROOT = Path(__file__).resolve().parents[1]


class VisualTaskMatching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = subject.build(source_beat="28-28")
        cls.by_id = {row["taskId"]: row for row in cls.artifact["tasks"]}

    def test_split_tasks_receive_independent_template_slates(self):
        setup = self.by_id["28-28.setup"]
        overlap = self.by_id["28-28.overlap"]
        self.assertEqual(setup["matchingJob"], "define_terms")
        self.assertEqual(overlap["matchingJob"], "intersection_of_sets")
        self.assertNotEqual(
            [row["candidateId"] for row in setup["templateCandidates"]],
            [row["candidateId"] for row in overlap["templateCandidates"]],
        )

    def test_split_tasks_receive_independent_media_results(self):
        self.assertEqual(self.by_id["28-28.setup"]["mediaCandidates"]["status"], "no_entity_media_demand")
        self.assertEqual(len(self.by_id["28-28.overlap"]["mediaCandidates"]["entities"]), 10)
        self.assertTrue(self.by_id["28-28.overlap"]["mediaCandidates"]["individualCandidateIds"])

    def test_every_candidate_has_task_level_provenance(self):
        for task in self.artifact["tasks"]:
            for candidate in task["templateCandidates"]:
                provenance = candidate["candidateMatchingProvenance"]
                self.assertEqual(provenance["scope"], "visual_task")
                self.assertEqual(provenance["taskId"], task["taskId"])

    def test_missing_task_provenance_fails_closed(self):
        broken = copy.deepcopy(self.artifact)
        del broken["tasks"][0]["templateCandidates"][0]["candidateMatchingProvenance"]
        with self.assertRaisesRegex(ValueError, "lacks VisualTask provenance"):
            subject.validate(broken, verify_sources=False)

    def test_written_artifact_replays(self):
        written = json.loads((ROOT / "reports" / "visualtask-match-pilot-28-28.json").read_text())
        subject.validate(written)

    def test_generic_legacy_binding_cannot_admit_incompatible_data_template(self):
        pool = {row["id"]: row for row in subject.C.load()}
        task = {
            "id": "new-story.statement", "job": "assert_without_data", "taskRole": "main",
            "quote": "The artist remains deeply misunderstood.", "entityCount": 1,
            "entities": {"displayEligible": ["artist"]}, "mustBePerceptible": [],
            "presentationOperations": ["concept_statement"], "templateAdmissions": [],
            "ignorePriorSelections": True, "candidateDisplayLimit": 50,
        }
        rows = subject.template_candidates(
            task, {"assert_without_data": [{"id": "3d-pie-chart-set--scene-003"}]},
            pool, exhaustive_families=True,
        )
        self.assertNotIn("3d-pie-chart-set--scene-003", {row["candidateId"] for row in rows})

    def test_subject_profile_uses_identity_capability_not_generic_documentary_word(self):
        pool = {row["id"]: row for row in subject.C.load()}
        task = {
            "id": "new-story.profile", "job": "introduce", "taskRole": "main",
            "quote": "Who is the artist?", "entityCount": 1,
            "entities": {"displayEligible": ["artist"]}, "mustBePerceptible": [],
            "presentationOperations": ["subject_profile"], "templateAdmissions": [],
            "ignorePriorSelections": True, "candidateDisplayLimit": 500,
        }
        rows = subject.template_candidates(task, {}, pool, exhaustive_families=True)
        ids = {row["candidateId"] for row in rows}
        self.assertIn("03-history-documentary-10-slides--scene-001", ids)
        self.assertNotIn("3d-pie-chart-set--scene-003", ids)
        self.assertTrue(all(
            row["bindingProvenance"]["source"] == "structured-presentation-contract"
            for row in rows
        ))

    def test_task_scoped_editor_admission_survives_family_diversification(self):
        pool = {row["id"]: row for row in subject.C.load()}
        task = {
            "id": "new-story.admission", "job": "assert_without_data", "taskRole": "main",
            "quote": "A statement.", "entityCount": 1,
            "entities": {"displayEligible": ["artist"]}, "mustBePerceptible": [],
            "presentationOperations": ["concept_statement"],
            "templateAdmissions": [{"id": "03-history-documentary-10-slides--scene-001", "source": "user"}],
            "ignorePriorSelections": True, "candidateDisplayLimit": 16,
        }
        rows = subject.template_candidates(task, {}, pool)
        self.assertIn("03-history-documentary-10-slides--scene-001", {row["candidateId"] for row in rows})


if __name__ == "__main__":
    unittest.main()
