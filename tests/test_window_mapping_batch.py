import copy
import json
from pathlib import Path
import unittest

from pipeline import window_mapping_batch as subject


ROOT = Path(__file__).resolve().parents[1]


class ExactWindowMappingBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(subject.DEFAULT_REQUEST.read_text())
        cls.report = subject.build_report(cls.request)

    def test_batch_has_67_exact_windows_and_no_errors(self):
        self.assertEqual(self.report["summary"], {
            "families": 3,
            "anchors": 14,
            "exactWindows": 67,
            "errors": 0,
        })

    def test_every_window_is_exact_and_within_native_duration(self):
        durations = {row["familyId"]: row["nativeDurationSeconds"] for row in self.report["families"]}
        for proposal in self.report["proposals"]:
            window = proposal["window"]
            self.assertEqual(window["precision"], "exact")
            self.assertGreater(window["endSeconds"], window["startSeconds"])
            self.assertLessEqual(window["endSeconds"], durations[proposal["familyId"]])

    def test_proposals_do_not_claim_final_verification(self):
        self.assertEqual({row["status"] for row in self.report["proposals"]}, {"proposed_verified_window"})

    def test_saved_report_is_deterministic(self):
        saved = json.loads(subject.DEFAULT_REPORT.read_text())
        self.assertEqual(subject.validate_report(saved, self.request), self.report["summary"])
        self.assertEqual(subject.DEFAULT_REPORT.read_text(), subject.dumps(subject.build_report(self.request)))

    def test_changed_boundary_source_fails(self):
        broken = copy.deepcopy(self.request)
        broken["sources"]["sceneLibraryScenes"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            subject.build_report(broken)

    def test_window_capacity_is_not_whole_composition_capacity(self):
        row = next(
            item for item in self.report["proposals"]
            if item["clipId"] == "photo-slideshow-smooth-envato--scene-005"
        )
        self.assertAlmostEqual(row["window"]["startSeconds"], 16.3)
        self.assertAlmostEqual(row["window"]["endSeconds"], 22.57)
        self.assertEqual(row["nativeFacts"]["absoluteMediaSlots"], 10)
        self.assertEqual(row["nativeFacts"]["maxSimultaneouslyEnabledInputs"], 9)


if __name__ == "__main__":
    unittest.main()
