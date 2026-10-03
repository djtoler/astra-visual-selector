import copy
import json
import unittest
from pathlib import Path

from pipeline import storypackage_data_handoff as subject


class StoryPackageDataHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]

    def test_only_current_data_bearing_tasks_enter_assignment_queue(self):
        artifact = subject.build()
        self.assertEqual(artifact["counts"]["currentVisualTasks"], 41)
        self.assertEqual(artifact["counts"]["assignments"], 28)
        self.assertTrue(all(row["requiredEncodings"] for row in artifact["assignments"]))
        self.assertNotIn("02-02a.main", {row["taskId"] for row in artifact["assignments"]})

    def test_assignments_keep_story_claim_and_proposal_links(self):
        artifact = subject.build()
        self.assertTrue(all(row["claimIds"] for row in artifact["assignments"]))
        self.assertTrue(all(row["jobProposalIds"] for row in artifact["assignments"]))
        self.assertTrue(all(row["requiredTypedFields"] is None for row in artifact["assignments"]))
        self.assertTrue(all(row["status"] == "awaiting_data_layer" for row in artifact["assignments"]))

    def test_queue_cannot_authorize_matching_or_rendering(self):
        artifact = subject.build()
        self.assertFalse(artifact["selectionAuthorized"])
        self.assertFalse(artifact["renderingAuthorized"])
        self.assertFalse(artifact["dataHandoffComplete"])

    def test_missing_story_link_fails_closed(self):
        proposals = json.loads(subject.DEFAULT_STORY_TASKS.read_text())
        broken = copy.deepcopy(proposals)
        broken["taskProposals"] = [row for row in broken["taskProposals"] if "01-01" not in row.get("reviewKeys", [])]
        with self.assertRaisesRegex(ValueError, "data-bearing VisualTask lacks StoryPackage proposal"):
            subject.build(story_tasks=broken)


if __name__ == "__main__":
    unittest.main()
