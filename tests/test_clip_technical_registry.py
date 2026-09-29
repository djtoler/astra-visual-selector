import copy
import json
from pathlib import Path
import unittest

from pipeline import clip_technical_registry as subject


ROOT = Path(__file__).resolve().parents[1]


class ClipTechnicalRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads(
            (ROOT / "reports" / "carousel-slideshow-clip-native-pilot.json").read_text()
        )

    def test_pilot_covers_all_five_preview_clips(self):
        self.assertEqual(
            subject.validate_registry(self.registry),
            {
                "clips": 5,
                "compositionVerified": 5,
                "approximateWindows": 5,
                "windowSlotExposureUnresolved": 5,
                "nativeRenders": 3,
            },
        )

    def test_native_render_evidence_covers_each_mapped_composition(self):
        evidence = self.registry["sources"]["nativeRenderEvidence"]
        self.assertEqual(
            {row["compositionPath"] for row in evidence},
            {"2.Final/Render 01", "2.Final/Render 02", "2.Final/Render 03"},
        )
        self.assertTrue(all(row["decodeVerified"] for row in evidence))

    def test_landscape_clips_bind_to_six_slot_text_comp(self):
        rows = {row["clipId"]: row for row in self.registry["clips"]}
        for clip_id in ("carousel-slideshow--review-002", "carousel-slideshow--review-005"):
            row = rows[clip_id]
            self.assertEqual(row["native"]["composition"]["path"], "2.Final/Render 02")
            self.assertEqual(row["technicalCapacity"]["absoluteMediaSlots"], 6)
            self.assertEqual(row["technicalCapacity"]["editableTextFields"], 6)

    def test_two_portrait_slices_can_share_one_native_comp(self):
        rows = {row["clipId"]: row for row in self.registry["clips"]}
        self.assertEqual(
            rows["carousel-slideshow--review-003"]["native"]["composition"],
            rows["carousel-slideshow--review-004"]["native"]["composition"],
        )
        self.assertEqual(
            rows["carousel-slideshow--review-003"]["native"]["window"]["endSeconds"],
            rows["carousel-slideshow--review-004"]["native"]["window"]["startSeconds"],
        )

    def test_project_envelope_cannot_replace_exact_composition_capacity(self):
        broken = copy.deepcopy(self.registry)
        broken["clips"][0]["technicalCapacity"]["absoluteMediaSlots"] = 12
        with self.assertRaisesRegex(ValueError, "differs from measured composition"):
            subject.validate_registry(broken)

    def test_approximate_window_cannot_be_relabelled_exact(self):
        broken = copy.deepcopy(self.registry)
        broken["clips"][0]["mappingStatus"] = "verified"
        broken["clips"][0]["native"]["window"]["precision"] = "approximate"
        with self.assertRaisesRegex(ValueError, "requires an exact window"):
            subject.validate_registry(broken)

    def test_missing_clip_fails_coverage(self):
        broken = copy.deepcopy(self.registry)
        broken["clips"].pop()
        with self.assertRaisesRegex(ValueError, "coverage mismatch"):
            subject.validate_registry(broken)


if __name__ == "__main__":
    unittest.main()
