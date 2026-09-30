import copy
import json
from pathlib import Path
import unittest

from pipeline.prepared_title_family_batch import activate_report, build_report, validate_report


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = ROOT / "clip-mapping-batches" / "batch-016" / "request.json"
REPORT_PATH = ROOT / "reports" / "clip-mapping-batch-016.json"


class PreparedTitleFamilyBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text())
        cls.report = json.loads(REPORT_PATH.read_text())

    def test_saved_report_rebuilds_deterministically(self):
        summary = validate_report(self.report, self.request)
        self.assertEqual(summary["proposedWindowCount"], 14)
        self.assertEqual(summary["blockedClipCount"], 2)
        self.assertFalse(self.report["preparationOnly"])
        self.assertFalse(self.report["renderingAuthorized"])

    def test_variable_text_uses_explicit_master_windows(self):
        proposals = {
            row["clipId"]: row
            for row in self.report["proposals"]
            if row["familyId"] == "archive3-variable-text-animation"
        }
        self.assertEqual(len(proposals), 9)
        self.assertEqual(
            proposals["archive3-variable-text-animation--review-009"]["expectedChildCompositionIds"],
            [952, 1142, 1157],
        )
        self.assertEqual(
            proposals["archive3-variable-text-animation--review-009"]["window"],
            {"durationSeconds": 5.550000000000001, "endSeconds": 30.55, "precision": "exact", "startSeconds": 25.0},
        )

    def test_urban_multi_terminal_clips_are_not_false_single_bindings(self):
        proposals = {
            row["clipId"]: row
            for row in self.report["proposals"]
            if row["familyId"] == "archive3-urban-grunge-titles-2026-09-12-09-49-42-utc"
        }
        self.assertEqual(len(proposals), 5)
        self.assertEqual(
            proposals["archive3-urban-grunge-titles-2026-09-12-09-49-42-utc--review-002"]["expectedChildCompositionIds"],
            [823, 981],
        )
        self.assertEqual(
            proposals["archive3-urban-grunge-titles-2026-09-12-09-49-42-utc--review-005"]["expectedChildCompositionIds"],
            [2315, 2390, 2404],
        )

    def test_grunge_lyric_clips_remain_explicitly_blocked(self):
        self.assertEqual(len(self.report["blockedFamilies"]), 1)
        blocked = self.report["blockedFamilies"][0]
        self.assertEqual(blocked["familyId"], "archive3-grunge-lyric-video-template")
        self.assertEqual(len(blocked["unsafeClipIds"]), 2)
        self.assertIn("exact native interval", blocked["requiredEvidence"])

    def test_window_child_tamper_fails_closed(self):
        request = copy.deepcopy(self.request)
        request["windowFamilies"][1]["clipWindows"][1]["expectedChildCompositionIds"] = [823]
        with self.assertRaisesRegex(ValueError, "child window changed"):
            build_report(request)

    def test_blocked_scope_tamper_fails_closed(self):
        request = copy.deepcopy(self.request)
        request["blockedFamilies"][0]["unsafeClipIds"].pop()
        with self.assertRaisesRegex(ValueError, "blocked family scope incomplete"):
            build_report(request)

    def test_activation_writes_exact_windows_and_preserves_blockers(self):
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            mappings_path = Path(temp_dir) / "mappings.json"
            windows_path = Path(temp_dir) / "windows.json"
            mappings_path.write_text((ROOT / "grammar" / "ae-scene-composition-mappings.json").read_text())
            windows_path.write_text((ROOT / "grammar" / "ae-scene-window-definitions.json").read_text())
            result = activate_report(
                self.report,
                self.request,
                mappings_path=mappings_path,
                windows_path=windows_path,
            )
            self.assertEqual(result["activated"], 14)
            mappings = {row["sceneId"]: row for row in json.loads(mappings_path.read_text())["mappings"]}
            self.assertEqual(
                mappings["archive3-variable-text-animation--review-001"]["status"],
                "verified_window",
            )
            self.assertNotIn(
                "archive3-grunge-lyric-video-template--review-001",
                mappings,
            )


if __name__ == "__main__":
    unittest.main()
