import copy
import json
from pathlib import Path
import tempfile
import unittest

from pipeline.technical_index_increment import merge_project


class TechnicalIndexIncrementTests(unittest.TestCase):
    def test_adds_one_sorted_project_and_recalculates_counts(self):
        index = {
            "schemaVersion": 1,
            "renderingPerformed": False,
            "sourceReports": {},
            "counts": {"projects": 0, "compositions": 0, "textFields": 0},
            "projects": [],
        }
        project = {
            "id": "new-project",
            "sourceProjectSha256": "a" * 64,
            "sourceUnchanged": True,
            "reportedCompositionCount": 0,
            "compositions": [],
            "textFields": [],
        }
        with tempfile.TemporaryDirectory() as temporary:
            capacity = Path(temporary) / "capacity.json"
            capacity.write_text("{}")
            result = merge_project(copy.deepcopy(index), project, capacity)
        self.assertEqual(result["counts"], {"projects": 1, "compositions": 0, "textFields": 0})
        self.assertEqual(result["projects"][0]["id"], "new-project")
        self.assertEqual(
            result["sourceReports"]["supplementalCapacityReports"][0]["projectId"],
            "new-project",
        )

    def test_duplicate_project_fails_closed(self):
        index = {"projects": [{"id": "same"}]}
        with tempfile.TemporaryDirectory() as temporary:
            capacity = Path(temporary) / "capacity.json"
            capacity.write_text(json.dumps({}))
            with self.assertRaisesRegex(ValueError, "already exists"):
                merge_project(index, {"id": "same"}, capacity)

    def test_replacement_requires_the_same_source_hash(self):
        index = {
            "schemaVersion": 1,
            "renderingPerformed": False,
            "sourceReports": {},
            "counts": {"projects": 1, "compositions": 0, "textFields": 0},
            "projects": [
                {
                    "id": "same",
                    "sourceProjectSha256": "a" * 64,
                    "sourceUnchanged": True,
                    "reportedCompositionCount": 0,
                    "compositions": [],
                    "textFields": [],
                }
            ],
        }
        replacement = copy.deepcopy(index["projects"][0])
        replacement["resultStatus"] = "refreshed"
        with tempfile.TemporaryDirectory() as temporary:
            capacity = Path(temporary) / "capacity.json"
            capacity.write_text("{}")
            result = merge_project(index, replacement, capacity, replace=True)
            self.assertEqual(result["projects"][0]["resultStatus"], "refreshed")
            self.assertEqual(
                [
                    row["projectId"]
                    for row in result["sourceReports"]["supplementalCapacityReports"]
                ],
                ["same"],
            )
            replacement["sourceProjectSha256"] = "b" * 64
            with self.assertRaisesRegex(ValueError, "source hash differs"):
                merge_project(index, replacement, capacity, replace=True)


if __name__ == "__main__":
    unittest.main()
