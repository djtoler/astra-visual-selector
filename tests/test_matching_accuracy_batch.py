import copy
import json
import unittest
from pathlib import Path


class MatchingAccuracyBatch01(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pipeline import matching_accuracy_batch

        cls.subject = matching_accuracy_batch
        cls.root = Path(__file__).resolve().parents[1]
        cls.request = json.loads(
            (cls.root / "matching-accuracy" / "batch-001" / "request.json").read_text()
        )
        cls.report = cls.subject.evaluate(cls.request)
        cls.cases = {row["id"]: row for row in cls.report["cases"]}

    def test_batch_is_read_only_and_has_five_distinct_cases(self):
        self.assertEqual(self.report["activationState"], "review_only_not_connected")
        self.assertFalse(self.report["selectionAuthorized"])
        self.assertFalse(self.report["renderingAuthorized"])
        self.assertEqual(self.report["summary"]["total"], 5)

    def test_source_hash_change_fails_before_evaluation(self):
        stale = copy.deepcopy(self.request)
        stale["sources"]["visualTasks"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "bound source changed: visualTasks"):
            self.subject.evaluate(stale)

    def test_evaluation_is_deterministic(self):
        first = self.subject.dumps(self.subject.evaluate(self.request))
        second = self.subject.dumps(self.subject.evaluate(self.request))
        self.assertEqual(first, second)

    def test_ten_plus_case_exposes_the_old_threshold_defect(self):
        case = self.cases["ten_plus_all_spatial"]
        self.assertEqual(case["status"], "fail")
        self.assertEqual(case["observed"]["taskEntityCount"], 11)
        self.assertEqual(case["observed"]["availableSpatialCount"], 10)
        self.assertEqual(case["observed"]["offeredSpatialIds"], [])
        self.assertEqual(len(case["observed"]["missingSpatialIds"]), 10)

    def test_split_beat_remains_two_tasks_with_unknown_task_timing(self):
        case = self.cases["split_beat_visual_tasks"]
        self.assertEqual(case["status"], "pass")
        self.assertEqual(case["observed"]["taskIds"], ["28-28.setup", "28-28.overlap"])
        self.assertEqual(case["observed"]["taskRoles"], ["setup_text", "spatial_comparison"])
        self.assertEqual(case["observed"]["timingStates"], [
            "unresolved_split_task_span", "unresolved_split_task_span"
        ])

    def test_text_candidate_is_not_promoted_without_native_field_evidence(self):
        case = self.cases["text_heavy_document"]
        self.assertEqual(case["status"], "pass")
        self.assertTrue(case["observed"]["candidateOnSlate"])
        self.assertFalse(case["observed"]["exactCompositionMapped"])
        self.assertEqual(case["observed"]["technicalVerdict"], "technical_spec_unmapped")
        self.assertIn("editor_approved_treatment", case["missingRequirements"])

    def test_saved_footage_requirement_is_not_encoded_yet(self):
        case = self.cases["actual_footage_required"]
        self.assertEqual(case["status"], "fail")
        self.assertTrue(case["observed"]["reviewDirectionFound"])
        self.assertIsNone(case["observed"]["encodedRequiredMediaKinds"])
        self.assertIn("required_media_kind:footage", case["missingRequirements"])

    def test_missing_media_does_not_yet_emit_typed_conditional(self):
        case = self.cases["missing_media_conditional"]
        self.assertEqual(case["status"], "fail")
        self.assertEqual(case["observed"]["savedReviewNote"], "no available broll")
        self.assertFalse(case["observed"]["typedMissingMediaBriefPresent"])
        self.assertEqual(case["expectedMissingMediaBrief"]["status"], "missing")


if __name__ == "__main__":
    unittest.main()

