import copy
import json
from pathlib import Path
import unittest

from pipeline import scene_window_capacity as subject


ROOT = Path(__file__).resolve().parents[1]


class SceneWindowCapacityTests(unittest.TestCase):
    def test_builds_source_bound_windows_without_rendering(self):
        artifact = subject.build_window_capacities()
        self.assertEqual(artifact["counts"], {"windows": 17})
        self.assertFalse(artifact["renderingPerformed"])

    def test_smooth_three_photo_window_reports_window_capacity(self):
        rows = {row["sceneId"]: row for row in subject.build_window_capacities()["windows"]}
        capacity = rows["photo-slideshow-smooth-envato--scene-005"]["capacity"]
        self.assertEqual(capacity["totalIndependentVisualMediaInputs"], 10)
        self.assertEqual(capacity["maxSimultaneouslyEnabledRecursiveVisualInputs"], 9)
        self.assertEqual(len(capacity["recursiveEditableTextFields"]), 10)

    def test_photo_memories_window_does_not_inherit_other_scenes(self):
        rows = {row["sceneId"]: row for row in subject.build_window_capacities()["windows"]}
        capacity = rows["photo-slideshow-memories-envato--scene-006"]["capacity"]
        self.assertEqual(capacity["compositionPath"], "02.Edit Comps/Scene 05/Scene 05")
        self.assertEqual(capacity["totalIndependentVisualMediaInputs"], 6)

    def test_saved_artifact_matches_native_reports(self):
        saved = json.loads((ROOT / "grammar/ae-scene-window-technical-capacities.json").read_text())
        self.assertEqual(subject.validate_window_capacities(saved, verify_native_reports=True), {"windows": 17})

    def test_mutation_fails_closed(self):
        artifact = subject.build_window_capacities()
        broken = copy.deepcopy(artifact)
        broken["windows"][0]["capacity"]["totalIndependentVisualMediaInputs"] += 1
        with self.assertRaisesRegex(ValueError, "stale"):
            subject.validate_window_capacities(broken, verify_native_reports=True)


if __name__ == "__main__":
    unittest.main()
