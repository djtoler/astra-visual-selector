import copy
import hashlib
import json
import unittest
from pathlib import Path

from pipeline import visualtask_split_proposals as subject


ROOT = Path(__file__).resolve().parents[1]


class VisualTaskSplitProposals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads((ROOT / "visual-task-splits" / "review-001" / "request.json").read_text())
        cls.draft = json.loads((ROOT / "visual-task-splits" / "review-001" / "draft.json").read_text())

    def test_request_is_deterministic_and_source_bound(self):
        self.assertEqual(subject.dumps(subject.prepare()), subject.dumps(self.request))
        self.assertEqual(self.draft["requestSha256"], hashlib.sha256(subject.dumps(self.request).encode()).hexdigest())

    def test_all_source_beats_are_assessed_once(self):
        self.assertEqual(subject.validate_draft(self.draft, self.request), {
            "sourceBeats": 40, "keepSingle": 33, "proposedSplits": 5, "existingApprovedSplits": 1,
            "sourceMismatches": 1, "pi05Reconciled": 8,
        })

    def test_new_proposals_include_issue_and_editor_review_findings(self):
        self.assertEqual([row["sourceBeatId"] for row in self.draft["proposals"]], ["13-13a", "21-21b", "23-23", "24-24", "30-30a"])
        self.assertTrue(all(row["editorDecision"] is None for row in self.draft["proposals"]))

    def test_every_pi05_beat_has_an_explicit_disposition(self):
        rows = self.draft["issueReconciliation"]["PI-05"]
        self.assertEqual({row["sourceBeatId"] for row in rows}, {
            "13-13a", "13-13b", "14-14", "21-21b", "23-23", "24-24", "25-25a", "28-28",
        })

    def test_stale_review_text_is_not_turned_into_a_task(self):
        self.assertEqual([row["sourceBeatId"] for row in self.draft["sourceMismatches"]], ["13-13b"])

    def test_non_exact_quote_fails_closed(self):
        broken = copy.deepcopy(self.draft)
        broken["proposals"][0]["tasks"][0]["quote"] += " invented"
        with self.assertRaisesRegex(ValueError, "exact unique substring"):
            subject.validate_draft(broken, self.request)

    def test_model_cannot_invent_editor_approval(self):
        broken = copy.deepcopy(self.draft)
        broken["proposals"][0]["editorDecision"] = "approved"
        with self.assertRaisesRegex(ValueError, "cannot invent an editor decision"):
            subject.validate_draft(broken, self.request)


if __name__ == "__main__":
    unittest.main()
