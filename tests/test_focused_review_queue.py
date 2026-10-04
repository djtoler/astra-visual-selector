import json
import tempfile
import unittest
from pathlib import Path

from pipeline import focused_review_queue as subject


class FocusedReviewQueueTests(unittest.TestCase):
    def test_one_deterministic_representative_per_semantic_capability_signature(self):
        tasks = [
            self.task("t1", "concept_statement", "assert_without_data", 1),
            self.task("t2", "concept_statement", "assert_without_data", 1),
            self.task("t3", "identity_comparison", "parallel_instances", 2),
        ]
        gallery = {
            "packageId": "unrelated-package@1",
            "activationState": "review_only_not_connected",
            "selectionAuthorized": False,
            "renderingAuthorized": False,
            "fitValidated": False,
            "tasks": tasks,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "gallery.json"
            path.write_text(json.dumps(gallery), encoding="utf-8")
            first = subject.build(path)
            second = subject.build(path)
        self.assertEqual(first["taskIds"], second["taskIds"])
        self.assertEqual(first["counts"]["focusedReviewTasks"], 2)
        self.assertEqual(first["counts"]["fullGalleryTasks"], 3)
        self.assertTrue(first["fullQueuePreserved"])
        self.assertFalse(first["selectionAuthorized"])
        self.assertFalse(first["renderingAuthorized"])
        represented = [task_id for row in first["representatives"] for task_id in row["representedTaskIds"]]
        self.assertEqual(sorted(represented), ["t1", "t2", "t3"])

    def test_boundary_rejects_authorized_gallery(self):
        gallery = {
            "packageId": "unrelated-package@1",
            "activationState": "review_only_not_connected",
            "selectionAuthorized": True,
            "renderingAuthorized": False,
            "fitValidated": False,
            "tasks": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "gallery.json"
            path.write_text(json.dumps(gallery), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "boundary"):
                subject.build(path)

    @staticmethod
    def task(task_id, operation, job, entity_count):
        return {
            "taskId": task_id,
            "job": job,
            "primaryPresentationOperation": operation,
            "presentationContract": {
                "primaryOperation": operation,
                "entityCount": entity_count,
                "hasTypedValues": False,
                "hasCohort": False,
                "mustBePerceptible": [],
                "needsOnScreenText": False,
            },
            "candidates": [{"candidateId": "example"}],
        }


if __name__ == "__main__":
    unittest.main()
