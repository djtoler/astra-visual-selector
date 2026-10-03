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

    def test_evaluator_is_declarative_and_contains_no_fixture_ids(self):
        source = (self.root / "pipeline" / "matching_accuracy_batch.py").read_text()
        for fixture_id in (
            "eleven_person_long_carousel_test",
            "split_beat_visual_tasks",
            "28-28",
            "screen-mockup-rfx",
            "no available broll",
        ):
            self.assertNotIn(fixture_id, source)

    def test_unknown_assertion_operator_fails_closed(self):
        broken = copy.deepcopy(self.request)
        broken["cases"][0]["assertions"][0]["operator"] = "run_case_specific_code"
        with self.assertRaisesRegex(ValueError, "unsupported assertion operator"):
            self.subject.evaluate(broken)

    def test_unrelated_heldout_harness_scores_automated_stages_and_holds_human_review(self):
        heldout = json.loads(
            (self.root / "matching-accuracy" / "held-out-001" / "request.json").read_text()
        )
        report = self.subject.evaluate(heldout)
        self.assertEqual(report["summary"], {
            "total": 6, "passed": 5, "failed": 0, "pending": 1, "allPassed": False
        })
        self.assertEqual(
            [row["id"] for row in report["cases"] if row["status"] == "pending"],
            ["heldout-human-approval"],
        )
        self.assertFalse(report["selectionAuthorized"])
        self.assertFalse(report["renderingAuthorized"])

    def test_ten_plus_case_uses_a_long_ae_carousel_not_spatial_or_infographic(self):
        case = self.cases["eleven_person_long_carousel_test"]
        self.assertEqual(case["status"], "pass")
        self.assertEqual(case["observed"]["taskEntityCount"], 11)
        self.assertTrue(case["observed"]["batchTreatmentRequiresLongCarousel"])
        self.assertGreaterEqual(case["observed"]["eligibleLongCarouselCount"], 1)
        self.assertGreaterEqual(len(case["observed"]["offeredLongCarouselIds"]), 1)
        self.assertFalse(
            case["observed"]["spatialOrInfographicSatisfiesThisBatchTreatment"]
        )

    def test_split_beat_matches_templates_and_media_independently_per_task(self):
        case = self.cases["split_beat_visual_tasks"]
        self.assertEqual(case["status"], "pass")
        self.assertEqual(case["observed"]["taskIds"], ["28-28.setup", "28-28.overlap"])
        self.assertEqual(case["observed"]["taskRoles"], ["setup_text", "spatial_comparison"])
        self.assertEqual(case["observed"]["timingStates"], [
            "exact_reviewed_split_task_span", "exact_reviewed_split_task_span"
        ])
        self.assertTrue(case["observed"]["taskLevelCandidateMatchingEvidence"])
        self.assertNotEqual(case["observed"]["candidateIdsByTask"]["28-28.setup"], case["observed"]["candidateIdsByTask"]["28-28.overlap"])
        self.assertEqual(case["observed"]["mediaEntityCountByTask"], {"28-28.setup": 0, "28-28.overlap": 10})

    def test_text_candidate_is_not_promoted_when_treatment_exceeds_native_fields(self):
        case = self.cases["text_heavy_document"]
        self.assertEqual(case["status"], "pass")
        self.assertTrue(case["observed"]["candidateOnSlate"])
        self.assertTrue(case["observed"]["exactCompositionMapped"])
        self.assertEqual(case["observed"]["measuredEditableTextFields"], 3)
        self.assertEqual(case["observed"]["requiredTextItems"], 5)
        self.assertEqual(case["observed"]["technicalVerdict"], "exact_technical_evidence_partial")
        self.assertIn("editor_approved_treatment", case["missingRequirements"])

    def test_saved_footage_requirement_is_encoded(self):
        case = self.cases["actual_footage_required"]
        self.assertEqual(case["status"], "pass")
        self.assertTrue(case["observed"]["reviewDirectionFound"])
        self.assertEqual(case["observed"]["encodedRequiredMediaKinds"], ["footage"])
        self.assertEqual(case["missingRequirements"], [])

    def test_missing_media_emits_typed_conditional(self):
        case = self.cases["missing_media_conditional"]
        self.assertEqual(case["status"], "pass")
        self.assertEqual(case["observed"]["savedReviewNote"], "no available broll")
        self.assertTrue(case["observed"]["typedMissingMediaBriefPresent"])
        self.assertEqual(case["observed"]["currentTechnicalVerdict"], "conditional")
        self.assertEqual(case["expectedMissingMediaBrief"]["status"], "missing")


if __name__ == "__main__":
    unittest.main()
