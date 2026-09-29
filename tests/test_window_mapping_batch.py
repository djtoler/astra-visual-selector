import copy
import json
from pathlib import Path
import tempfile
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


class NativeRenderReceiptWindowBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_path = ROOT / "clip-mapping-batches" / "batch-004" / "request.json"
        cls.report_path = ROOT / "reports" / "clip-mapping-batch-004.json"
        cls.request = json.loads(cls.request_path.read_text())
        cls.report = subject.build_report(cls.request)

    def test_batch_has_32_exact_windows_backed_by_three_receipts(self):
        self.assertEqual(self.report["summary"], {
            "families": 3,
            "anchors": 0,
            "exactWindows": 32,
            "errors": 0,
            "nativeRenderReceipts": 3,
        })

    def test_receipts_bind_rendered_video_to_native_final_composition(self):
        expected = {
            "03-history-documentary-10-slides": "FINAL",
            "07-history-slideshow": "FINAL",
            "08-documentary-slideshow": "02. Final Comp/Final Comp",
        }
        for family in self.report["families"]:
            evidence = family["alignmentEvidence"]
            self.assertEqual(evidence["mode"], "native_render_receipt")
            self.assertEqual(evidence["nativeCompositionSelector"], expected[family["familyId"]])
            self.assertEqual(len(evidence["renderedVideoSha256"]), 64)

    def test_saved_report_is_deterministic(self):
        saved = json.loads(self.report_path.read_text())
        self.assertEqual(subject.validate_report(saved, self.request), self.report["summary"])
        self.assertEqual(self.report_path.read_text(), subject.dumps(subject.build_report(self.request)))

    def test_wrong_review_composition_fails(self):
        broken = copy.deepcopy(self.request)
        broken["families"][0]["alignmentEvidence"]["reviewCompositionName"] = "wrong"
        with self.assertRaisesRegex(ValueError, "build receipt composition mismatch"):
            subject.build_report(broken)

    def test_wrong_video_receipt_fails(self):
        broken = copy.deepcopy(self.request)
        broken["families"][0]["alignmentEvidence"]["renderedVideoSource"] = "historySlideshowVideo"
        with self.assertRaisesRegex(ValueError, "render receipt mismatch"):
            subject.build_report(broken)

    def test_unlisted_existing_mapping_cannot_be_superseded(self):
        broken = copy.deepcopy(self.request)
        broken["families"][2]["supersedeClipIds"].remove("08-documentary-slideshow--scene-004")
        mappings = json.loads((ROOT / broken["registryPath"]).read_text())
        row = next(
            item for item in mappings["mappings"]
            if item["sceneId"] == "08-documentary-slideshow--scene-004"
        )
        row.update({
            "status": "verified",
            "compositionId": 265349916,
            "compositionPath": "03. Other/SCENES/Scene 03",
        })
        row.pop("windowCapacityId", None)
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / "registry.json"
            registry.write_text(json.dumps(mappings))
            broken["registryPath"] = str(registry)
            with self.assertRaisesRegex(ValueError, "target conflicts with registry"):
                subject.build_report(broken)


class EditorCheckpointEvidence(unittest.TestCase):
    def test_checkpoints_must_span_the_native_timeline(self):
        family = {
            "familyId": "photo-slideshow",
            "projectId": "photo-slideshow",
            "sourceProjectSha256": "a" * 64,
            "compositionId": 104,
            "compositionPath": "03. Final/Final",
            "alignmentEvidence": {"checkpointSource": "checkpoints"},
        }
        record = {
            "familyId": "photo-slideshow",
            "projectId": "photo-slideshow",
            "sourceProjectSha256": "a" * 64,
            "compositionId": 104,
            "compositionPath": "03. Final/Final",
            "evaluation": "exact_match",
            "evaluatorRole": "editor",
            "checkpoints": [
                {"seconds": 20, "result": "exact_match"},
                {"seconds": 210, "result": "exact_match"},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "checkpoints.json"
            evidence.write_text(json.dumps(record))
            result = subject._validate_editor_checkpoints(
                family,
                {"checkpoints": evidence},
                {"durationSeconds": 237.58333333333334},
            )
        self.assertEqual(result["checkpointCount"], 2)

    def test_checkpoints_confined_to_one_section_fail(self):
        family = {
            "familyId": "photo-slideshow",
            "projectId": "photo-slideshow",
            "sourceProjectSha256": "a" * 64,
            "compositionId": 104,
            "compositionPath": "03. Final/Final",
            "alignmentEvidence": {"checkpointSource": "checkpoints"},
        }
        record = {
            "familyId": "photo-slideshow",
            "projectId": "photo-slideshow",
            "sourceProjectSha256": "a" * 64,
            "compositionId": 104,
            "compositionPath": "03. Final/Final",
            "evaluation": "exact_match",
            "evaluatorRole": "editor",
            "checkpoints": [
                {"seconds": 20, "result": "exact_match"},
                {"seconds": 40, "result": "exact_match"},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "checkpoints.json"
            evidence.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "do not span timeline"):
                subject._validate_editor_checkpoints(
                    family,
                    {"checkpoints": evidence},
                    {"durationSeconds": 237.58333333333334},
                )


class EditorCheckpointWindowBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_path = ROOT / "clip-mapping-batches" / "batch-005" / "request.json"
        cls.report_path = ROOT / "reports" / "clip-mapping-batch-005.json"
        cls.request = json.loads(cls.request_path.read_text())
        cls.report = subject.build_report(cls.request)

    def test_photo_slideshow_has_57_exact_windows(self):
        self.assertEqual(self.report["summary"], {
            "families": 1,
            "anchors": 0,
            "exactWindows": 57,
            "errors": 0,
            "editorVerifiedCheckpointFamilies": 1,
        })

    def test_recovered_native_capacity_is_applied_per_window(self):
        media_counts = {row["nativeFacts"]["absoluteMediaSlots"] for row in self.report["proposals"]}
        simultaneous = {row["nativeFacts"]["maxSimultaneouslyEnabledInputs"] for row in self.report["proposals"]}
        text_counts = {row["nativeFacts"]["editableTextFields"] for row in self.report["proposals"]}
        self.assertEqual(media_counts, {10, 20})
        self.assertEqual(simultaneous, {10, 20})
        self.assertEqual(text_counts, {0})

    def test_saved_report_is_deterministic(self):
        saved = json.loads(self.report_path.read_text())
        self.assertEqual(subject.validate_report(saved, self.request), self.report["summary"])
        self.assertEqual(self.report_path.read_text(), subject.dumps(subject.build_report(self.request)))


if __name__ == "__main__":
    unittest.main()
