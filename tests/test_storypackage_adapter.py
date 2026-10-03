import copy
import json
import tempfile
import unittest
from pathlib import Path

from pipeline import storypackage_adapter as subject


class StoryPackageAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upstream = Path(__file__).resolve().parents[2] / "patterns-storypackage-review"
        cls.python = Path("/Users/dwaynetoler/Documents/ChatGPT/Polish/person-cutout-system/image-tools/.venv-rembg/bin/python")
        cls.apollo = cls.upstream / "architecture/storypackage/examples/apollo-collins-sample.storypackage-0.2.json"

    def test_unrelated_package_is_consumed_without_story_specific_code(self):
        artifact = subject.build(self.apollo, upstream_root=self.upstream, checker_python=self.python)
        self.assertTrue(artifact["storyHandoffReceipt"]["accepted"])
        self.assertEqual(artifact["story"]["storyId"], "apollo-collins-sample")
        self.assertEqual(artifact["gaps"][0]["gap"], "cohort_incomplete")
        self.assertFalse(artifact["selectionAuthorized"])
        self.assertFalse(artifact["renderingAuthorized"])

    def test_semantic_fields_survive_normalization(self):
        artifact = subject.build(self.apollo, upstream_root=self.upstream, checker_python=self.python)
        self.assertEqual(len(artifact["claims"]), 8)
        self.assertTrue(any(row["lane"] == "interpretive" for row in artifact["claims"]))
        self.assertTrue(any(ref["display"] == "withheld" for row in artifact["claims"] for ref in row["entityRefs"]))
        self.assertTrue(artifact["jobProposals"])
        self.assertTrue(artifact["obligations"])
        self.assertTrue(artifact["continuity"])
        self.assertEqual(artifact["timing"]["status"], "absent")

    def test_authoritative_checker_rejects_invalid_package(self):
        broken = json.loads(self.apollo.read_text())
        broken["beats"][0]["template"] = "forbidden"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "broken.json"
            path.write_text(json.dumps(broken))
            with self.assertRaisesRegex(ValueError, "authoritative StoryPackage checker rejected"):
                subject.build(path, upstream_root=self.upstream, checker_python=self.python)


if __name__ == "__main__":
    unittest.main()
