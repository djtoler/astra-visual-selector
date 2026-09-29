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


if __name__ == "__main__":
    unittest.main()
