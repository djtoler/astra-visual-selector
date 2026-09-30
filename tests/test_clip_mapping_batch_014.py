import copy
import json
from pathlib import Path
import tempfile
import unittest

from pipeline import family_mapping_rules as subject


ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "clip-mapping-batches" / "batch-014" / "request.json"
REPORT = ROOT / "reports" / "clip-mapping-batch-014.json"
DEFERRED_DROPOFF = (
    "archive3-dropoff-carousels-2026-09-15-17-30-59-utc--review-001"
)


class SourceBoundExplicitBatch014(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST.read_text())
        cls.report = subject.build_report(cls.request)

    def test_batch_is_complete_and_activated(self):
        self.assertEqual(
            self.report["summary"],
            {
                "families": 4,
                "anchors": 6,
                "proposals": 23,
                "leaveOneOutErrors": 0,
                "nativeStructureErrors": 0,
            },
        )
        self.assertEqual(
            {row["status"] for row in self.report["proposals"]},
            {"proposed_verified"},
        )
        registry = {
            row["sceneId"]: row
            for row in json.loads(
                (ROOT / self.request["registryPath"]).read_text()
            )["mappings"]
        }
        self.assertTrue(set(self.request["targetClipIds"]).issubset(registry))
        self.assertEqual(
            {registry[clip_id]["status"] for clip_id in self.request["targetClipIds"]},
            {"verified"},
        )

    def test_saved_report_is_deterministic(self):
        saved = json.loads(REPORT.read_text())
        self.assertEqual(
            subject.validate_report(saved, self.request),
            self.report["summary"],
        )
        self.assertEqual(REPORT.read_text(), subject.dumps(self.report))

    def test_activation_writes_only_batch_targets(self):
        source = ROOT / self.request["registryPath"]
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "mappings.json"
            fixture = json.loads(source.read_text())
            fixture["mappings"] = [
                row for row in fixture["mappings"]
                if row["sceneId"] not in self.request["targetClipIds"]
            ]
            fixture["scope"]["uniqueScenes"] = len(fixture["mappings"])
            target.write_text(json.dumps(fixture))
            before = json.loads(target.read_text())
            result = subject.activate_report(self.report, self.request, mappings_path=target)
            after = json.loads(target.read_text())
        self.assertEqual(result["activated"], 23)
        self.assertEqual(
            {row["sceneId"] for row in after["mappings"]}
            - {row["sceneId"] for row in before["mappings"]},
            set(self.request["targetClipIds"]),
        )
        activated = {
            row["sceneId"]: row for row in after["mappings"]
            if row["sceneId"] in self.request["targetClipIds"]
        }
        self.assertEqual({row["status"] for row in activated.values()}, {"verified"})

    def test_dropoff_montage_is_an_exception_not_a_mapping(self):
        dropoff = next(
            row
            for row in self.request["families"]
            if row["familyId"].startswith("archive3-dropoff-carousels")
        )
        self.assertNotIn(DEFERRED_DROPOFF, self.request["targetClipIds"])
        self.assertNotIn(
            DEFERRED_DROPOFF,
            {row["clipId"] for row in dropoff["terminalBindings"]},
        )
        self.assertEqual(
            {row["clipId"] for row in dropoff["semanticExceptions"]},
            {DEFERRED_DROPOFF},
        )

    def test_text_list_complete_preview_sequence_is_bound(self):
        text_list = next(
            row
            for row in self.request["families"]
            if row["familyId"] == "text-list-carousel"
        )
        self.assertEqual(text_list["semanticExceptions"], [])
        self.assertEqual(len(text_list["terminalBindings"]), 10)
        self.assertEqual(len(text_list["targetClipIds"]), 9)
        self.assertEqual(
            [row["clipId"] for row in text_list["terminalBindings"]],
            [f"text-list-carousel--review-{ordinal:03d}" for ordinal in range(1, 11)],
        )
        self.assertEqual(
            [row["compositionPath"] for row in text_list["terminalBindings"]],
            [
                "Check list text carousel/"
                f"Check list text carousel {ordinal}/Edit Here/Edit Here {ordinal}"
                for ordinal in range(1, 11)
            ],
        )

    def test_omitted_semantic_clip_fails_closed(self):
        broken = copy.deepcopy(self.request)
        text_list = broken["families"][0]
        removed = text_list["terminalBindings"].pop()
        text_list["targetClipIds"].remove(removed["clipId"])
        broken["targetClipIds"].remove(removed["clipId"])
        with self.assertRaisesRegex(ValueError, "family scope is incomplete"):
            subject.build_report(broken)

    def test_undeclared_shared_terminal_fails_closed(self):
        broken = copy.deepcopy(self.request)
        number_count = broken["families"][2]
        number_count["allowedSharedTerminalBindings"] = []
        with self.assertRaisesRegex(ValueError, "shared terminal declarations differ"):
            subject.build_report(broken)

    def test_incomplete_native_terminal_coverage_fails_closed(self):
        broken = copy.deepcopy(self.request)
        story = broken["families"][1]
        removed = story["terminalBindings"].pop()
        story["targetClipIds"].remove(removed["clipId"])
        story["semanticExceptions"].append({
            "clipId": removed["clipId"],
            "reason": "test-only exception",
        })
        broken["targetClipIds"].remove(removed["clipId"])
        with self.assertRaisesRegex(ValueError, "terminal coverage is incomplete"):
            subject.build_report(broken)

    def test_changed_native_source_hash_fails_closed(self):
        broken = copy.deepcopy(self.request)
        broken["sources"]["storyPhotoNative"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "bound source changed"):
            subject.build_report(broken)


if __name__ == "__main__":
    unittest.main()
