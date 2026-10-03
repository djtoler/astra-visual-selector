import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from pipeline import storypackage_matching_handoff as subject


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = Path(os.environ.get(
    "STORYPACKAGE_AUTHORITY_ROOT",
    ROOT.parent / "patterns-storypackage-review",
))
AUTOMATION_DATA = Path("/Users/dwaynetoler/yt001data")
PYTHON = Path("/Users/dwaynetoler/Documents/ChatGPT/Polish/person-cutout-system/image-tools/.venv-rembg/bin/python")
ASTRA_COMMIT = "da8b1755ea6d89a3d23c2fea157e972cee75b869"


class StoryPackageMatchingHandoffTests(unittest.TestCase):
    def _astra_snapshot(self, folder: Path) -> Path:
        for relative in ("grammar/visual-tasks.json", "grammar/entity-roster.json"):
            target = folder / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(subprocess.check_output(
                ["git", "show", f"{ASTRA_COMMIT}:{relative}"], cwd=ROOT,
            ))
        return folder

    def test_official_handoff_is_consumed_without_losing_story_requirements(self):
        with tempfile.TemporaryDirectory() as raw:
            snapshot = self._astra_snapshot(Path(raw))
            artifact = subject.build(
                UPSTREAM / "architecture/storypackage/year-seventeen.matching-handoff-0.2.json",
                upstream_root=UPSTREAM,
                checker_python=PYTHON,
                repo_mappings={
                    "djtoler/astra-visual-selector": snapshot,
                    "djtoler/automation-data": AUTOMATION_DATA,
                },
            )
        self.assertEqual(artifact["packageId"], "year-seventeen@7")
        self.assertEqual(len(artifact["tasks"]), 41)
        self.assertEqual(artifact["counts"]["textFields"], 106)
        self.assertEqual(artifact["counts"]["dataValues"], 89)
        self.assertEqual(len(artifact["cohortMembers"]["chart-93@1"]), 93)
        by_id = {row["taskId"]: row for row in artifact["tasks"]}
        self.assertEqual(by_id["27-27.main"]["media"]["kinds"], ["footage"])
        self.assertIn(
            "b-roll or a vertical carousel of the six artists",
            by_id["27-27.main"]["media"]["sourceSpecific"][0],
        )
        self.assertEqual(
            by_id["30-30b.main"]["media"]["sourceSpecific"],
            ["b-roll"],
        )
        self.assertEqual(len(artifact["unresolved"]), 3)
        self.assertTrue(artifact["storyMatchingHandoffReceipt"]["accepted"])
        self.assertFalse(artifact["selectionAuthorized"])
        self.assertFalse(artifact["treatmentApproved"])
        self.assertFalse(artifact["renderingAuthorized"])

    def test_current_visualtask_contract_is_semantically_compatible(self):
        handoff = json.loads((UPSTREAM / "architecture/storypackage/year-seventeen.matching-handoff-0.2.json").read_text())
        current = json.loads((ROOT / "grammar/visual-tasks.json").read_text())
        subject.validate_current_task_compatibility(handoff, current)
        broken = json.loads(json.dumps(current))
        broken["tasks"][0]["sourceBeatJob"] = "different_job"
        with self.assertRaisesRegex(ValueError, "visual job drift"):
            subject.validate_current_task_compatibility(handoff, broken)


if __name__ == "__main__":
    unittest.main()
