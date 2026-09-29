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

    def test_review_states_remain_distinct(self):
        result, _ = self._comparisons()
        self.assertEqual(result["counts"]["verifiedUniqueSceneMappings"], 73)
        self.assertEqual(result["counts"]["verifiedWholeCompositionMappings"], 56)
        self.assertEqual(result["counts"]["verifiedWindowMappings"], 17)
        self.assertEqual(result["counts"]["unresolvedUniqueSceneMappings"], 0)
        self.assertEqual(result["counts"]["unreviewedUniqueSceneMappings"], 0)

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

    def test_native_test_resolves_first_carousel_to_carousel_01(self):
        _, rows = self._comparisons()
        row = rows["carousel--review-001"]
        self.assertEqual(row["compositionMappingStatus"], "verified")
        self.assertEqual(row["exactComposition"]["id"], 1)
        self.assertEqual(row["exactComposition"]["path"], "Carousel 01/Carousel 01")
        self.assertEqual(row["exactComposition"]["totalIndependentVisualMediaInputs"], 6)
        self.assertNotIn("exact_scene_to_native_composition_mapping", row["missingForFillableNow"])

    def test_native_comparison_resolves_last_carousel_and_gallery_scenes(self):
        _, rows = self._comparisons()
        carousel = rows["carousel--review-011"]
        gallery_dark = rows["archive3-gallery-pro-carousel-2026-09-11-10-23-37-utc--review-001"]
        gallery_light = rows["archive3-gallery-pro-carousel-2026-09-11-10-23-37-utc--review-002"]
        self.assertEqual(carousel["exactComposition"]["path"], "Carousel 10/Carousel 10")
        self.assertEqual(carousel["exactComposition"]["totalIndependentVisualMediaInputs"], 5)
        self.assertEqual(gallery_dark["exactComposition"]["path"], "02. Final Comp/Gallery Pro - Focus")
        self.assertEqual(gallery_light["exactComposition"]["path"], "02. Final Comp/Gallery Pro - Showcase")

    def test_moving_contact_sheet_uses_exact_clip_window_capacity(self):
        _, rows = self._comparisons()
        row = rows["archive3-moving-contact-sheets-2026-09-13-14-49-02-utc--review-v3-001a"]
        self.assertEqual(row["compositionMappingStatus"], "verified_window")
        self.assertEqual(row["exactComposition"]["path"], "03. Other/Scenes/SCENE 01")
        self.assertEqual(row["exactComposition"]["measurementScope"], "clip_window")
        self.assertEqual(row["exactComposition"]["totalIndependentVisualMediaInputs"], 10)
        self.assertEqual(row["exactComposition"]["maxSimultaneouslyEnabledRecursiveVisualInputs"], 10)
        self.assertAlmostEqual(row["exactComposition"]["durationSeconds"], 2.625)
        self.assertNotIn("exact_scene_to_native_composition_mapping", row["missingForFillableNow"])

    def test_carousel_slideshow_native_pilot_resolves_parent_composition(self):
        _, rows = self._comparisons()
        row = rows["carousel-slideshow--review-001"]
        self.assertEqual(row["compositionMappingStatus"], "verified")
        self.assertEqual(row["exactComposition"]["path"], "2.Final/Render 01")
        self.assertEqual(row["exactComposition"]["totalIndependentVisualMediaInputs"], 8)

    def test_verified_window_uses_only_clip_window_capacity(self):
        _, rows = self._comparisons()
        row = rows["photo-slideshow-smooth-envato--scene-005"]
        comp = row["exactComposition"]
        self.assertEqual(row["compositionMappingStatus"], "verified_window")
        self.assertEqual(comp["measurementScope"], "clip_window")
        self.assertEqual(comp["totalIndependentVisualMediaInputs"], 10)
        self.assertEqual(comp["maxSimultaneouslyEnabledRecursiveVisualInputs"], 9)
        self.assertAlmostEqual(comp["durationSeconds"], 6.27)
        self.assertNotIn("exact_scene_to_native_composition_mapping", row["missingForFillableNow"])

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
        mappings["mappings"] = [
            copy.deepcopy(row)
            for row in mappings["mappings"]
            if row["sceneId"] != "screen-mockup-rfx--review-002"
        ]
        mappings["scope"]["uniqueScenes"] -= 1
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mappings.json"
            path.write_text(json.dumps(mappings))
            with self.assertRaisesRegex(ValueError, "scope mismatch"):
                subject.build_comparison(scene_mappings_path=path)

    def test_registry_can_expand_beyond_current_comparison_scope(self):
        mappings = json.loads((ROOT / "grammar" / "ae-scene-composition-mappings.json").read_text())
        self.assertEqual(mappings["scope"]["uniqueScenes"], 76)
        result, _ = self._comparisons()
        self.assertEqual(result["counts"]["verifiedUniqueSceneMappings"], 73)


if __name__ == "__main__":
    unittest.main()
