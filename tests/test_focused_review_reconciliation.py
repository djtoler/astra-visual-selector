import json
import tempfile
import unittest
from pathlib import Path

from pipeline import focused_review_reconciliation as subject


class FocusedReviewReconciliationTest(unittest.TestCase):
    def test_requires_one_commented_record_per_focused_task(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            queue = root / "queue.json"
            review = root / "review.json"
            queue.write_text(json.dumps({"taskIds": ["a", "b"]}))
            review.write_text(json.dumps({"decisions": {
                "a::x": {"id": "a::x", "taskId": "a", "candidateId": "x", "status": "acceptable", "comment": "Only b-roll."},
                "b::y": {"id": "b::y", "taskId": "b", "candidateId": "y", "status": "unreviewed", "comment": "Use a document/screen."},
            }}))
            artifact = subject.build(queue, review)
            self.assertEqual(artifact["coverage"]["reconciledTasks"], 2)
            self.assertEqual(artifact["themeCounts"]["broll_route"], 1)
            self.assertFalse(artifact["selectionAuthorized"])


if __name__ == "__main__":
    unittest.main()
