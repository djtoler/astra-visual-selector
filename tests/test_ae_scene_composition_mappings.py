import copy
import json
from pathlib import Path
import tempfile
import unittest

from pipeline import visualtask_ae_spec_comparison as subject


ROOT = Path(__file__).resolve().parents[1]


class ExactSceneCompositionMappings(unittest.TestCase):
    def test_mapping_consumer_exists(self):
        self.assertTrue(callable(subject.validate_scene_mappings))

    @staticmethod
    def _comparisons():
        result = subject.build_comparison()
        rows = [candidate for task in result["tasks"] for candidate in task["candidateComparisons"]]
        return result, {row["candidateId"]: row for row in rows}

    def test_twenty_scenes_are_exact_and_four_remain_unresolved(self):
        result, _ = self._comparisons()
        self.assertEqual(result["counts"]["verifiedUniqueSceneMappings"], 20)
        self.assertEqual(result["counts"]["unresolvedUniqueSceneMappings"], 4)

    def test_exact_flow_scene_uses_native_composition_metrics(self):
        _, rows = self._comparisons()
        row = rows["archive3-carousel-flow-loops-2026-09-15-08-02-14-utc--review-001"]
        comp = row["exactComposition"]
        self.assertEqual(comp["id"], 35052)
        self.assertEqual(comp["path"], "02. Final/Carousel Arc Flow")
        self.assertEqual(comp["totalIndependentVisualMediaInputs"], 10)
        self.assertEqual(comp["maxSimultaneouslyEnabledRecursiveVisualInputs"], 10)
        self.assertEqual(comp["durationSeconds"], 30.0)
        self.assertNotIn("exact_scene_to_native_composition_mapping", row["missingForFillableNow"])

    def test_exact_text_scene_exposes_its_native_text_fields(self):
        _, rows = self._comparisons()
        row = rows["text-list-carousel--review-002"]
        comp = row["exactComposition"]
        self.assertEqual(comp["id"], 4051)
        self.assertEqual(comp["recursiveEditableTextFields"], 8)
        self.assertEqual(len(comp["directTextFields"]), 0)
        self.assertEqual(len(comp["recursiveTextFields"]), 8)
        self.assertEqual(comp["recursiveTextFields"][0]["font"], "TikTokSans-SemiBold")

    def test_master_timeline_mapping_selects_specific_screen_comp(self):
        _, rows = self._comparisons()
        row = rows["screen-mockup-rfx--review-002"]
        comp = row["exactComposition"]
        self.assertEqual(comp["id"], 262)
        self.assertEqual(comp["path"], "03 Others/Final Scenes/Scene_02")
        self.assertAlmostEqual(comp["durationSeconds"], 8.008008008008009)

    def test_ambiguous_carousel_stays_unresolved(self):
        _, rows = self._comparisons()
        row = rows["carousel--review-001"]
        self.assertNotIn("exactComposition", row)
        self.assertEqual(row["compositionMappingStatus"], "unresolved")
        self.assertEqual(len(row["mappingUnresolved"]["candidateCompositionPaths"]), 4)
        self.assertIn("exact_scene_to_native_composition_mapping", row["missingForFillableNow"])

    def test_bad_composition_id_fails_closed(self):
        mappings = json.loads((ROOT / "grammar" / "ae-scene-composition-mappings.json").read_text())
        row = next(item for item in mappings["mappings"] if item["status"] == "verified")
        row["compositionId"] = -1
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mappings.json"
            path.write_text(json.dumps(mappings))
            with self.assertRaisesRegex(ValueError, "composition id/path mismatch"):
                subject.build_comparison(scene_mappings_path=path)

    def test_missing_scene_mapping_fails_closed(self):
        mappings = json.loads((ROOT / "grammar" / "ae-scene-composition-mappings.json").read_text())
        mappings["mappings"] = copy.deepcopy(mappings["mappings"][:-1])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mappings.json"
            path.write_text(json.dumps(mappings))
            with self.assertRaisesRegex(ValueError, "scope mismatch"):
                subject.build_comparison(scene_mappings_path=path)


if __name__ == "__main__":
    unittest.main()
