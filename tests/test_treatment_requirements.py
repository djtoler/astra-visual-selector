import copy
import json
import unittest
from pathlib import Path


class TreatmentRequirementsPilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pipeline import treatment_requirements

        cls.subject = treatment_requirements
        cls.request = treatment_requirements.build_pilot_request()

    def test_first_pilot_is_deterministic_exact_mapped_pair(self):
        self.assertEqual(self.request["taskId"], "02-02a.main")
        self.assertEqual(self.request["candidateId"], "screen-mockup-rfx--review-002")
        self.assertEqual(self.request["nativeComposition"]["id"], 262)
        self.assertEqual(self.request["reviewState"], "awaiting_model_draft")
        self.assertFalse(self.request["selectionAuthorized"])
        self.assertFalse(self.request["renderingAuthorized"])

    def test_request_exposes_only_real_native_slots_and_text_fields(self):
        native = self.request["nativeComposition"]
        self.assertEqual(len(native["allowedMediaSlots"]), native["totalIndependentVisualMediaInputs"])
        self.assertEqual(len(native["allowedTextFields"]), native["recursiveEditableTextFields"])
        self.assertEqual(len({row["id"] for row in native["allowedMediaSlots"]}), len(native["allowedMediaSlots"]))

    def test_timing_policy_stays_a_user_decision(self):
        self.assertEqual(self.request["timingPolicy"]["status"], "requires_user_decision")
        self.assertEqual(self.request["timingPolicy"]["allowedAdjustments"], None)

    def test_draft_cannot_claim_approval_or_fillability(self):
        draft = self.subject.empty_draft(self.request)
        draft["reviewState"] = "approved"
        with self.assertRaisesRegex(ValueError, "model draft cannot approve"):
            self.subject.validate_draft(draft, self.request)
        draft = self.subject.empty_draft(self.request)
        draft["verdict"] = "fillable_now"
        with self.assertRaisesRegex(ValueError, "cannot issue a fillability verdict"):
            self.subject.validate_draft(draft, self.request)

    def test_unknown_native_slot_fails_closed(self):
        draft = self.subject.empty_draft(self.request)
        draft["mediaAssignments"] = [{
            "slotId": "invented-slot",
            "contentRole": "primary evidence",
            "mediaKind": "document",
            "content": "2009 XXL Freshman cover",
            "evidence": "Narration names the cover.",
            "status": "proposed",
        }]
        with self.assertRaisesRegex(ValueError, "unknown native media slot"):
            self.subject.validate_draft(draft, self.request)

    def test_stale_request_hash_fails_closed(self):
        draft = self.subject.empty_draft(self.request)
        draft["requestSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "request hash mismatch"):
            self.subject.validate_draft(draft, self.request)

    def test_request_cannot_smuggle_an_approval_field(self):
        request = copy.deepcopy(self.request)
        request["approval"] = {"decision": "approved"}
        request_without_hash = dict(request)
        request_without_hash.pop("requestSha256ForDraft")
        request["requestSha256ForDraft"] = self.subject.artifact_sha(request_without_hash)
        with self.assertRaisesRegex(ValueError, "unknown or missing fields"):
            self.subject.validate_request(request)

    def test_build_is_deterministic(self):
        self.assertEqual(
            self.subject.dumps(self.subject.build_pilot_request()),
            self.subject.dumps(self.subject.build_pilot_request()),
        )

    def test_pilot_wrapper_matches_general_explicit_pair_builder(self):
        self.assertEqual(
            self.subject.dumps(self.subject.build_pilot_request()),
            self.subject.dumps(self.subject.build_request(
                "02-02a.main", "screen-mockup-rfx--review-002"
            )),
        )

    def test_non_pilot_explicit_pair_builds_without_selecting_it(self):
        request = self.subject.build_request(
            "01-01.subject", "counters-envato--scene-002"
        )
        self.assertEqual(request["taskId"], "01-01.subject")
        self.assertEqual(request["candidateId"], "counters-envato--scene-002")
        self.assertEqual(request["nativeComposition"]["id"], 17651)
        self.assertEqual(request["reviewState"], "awaiting_model_draft")
        self.assertFalse(request["selectionAuthorized"])
        self.assertFalse(request["renderingAuthorized"])

    def test_pair_must_already_be_offered_and_exact_mapped(self):
        with self.assertRaisesRegex(ValueError, "was not offered"):
            self.subject.build_request(
                "01-01.subject", "screen-mockup-rfx--review-002"
            )
        with self.assertRaisesRegex(ValueError, "lacks exact native composition"):
            self.subject.build_request(
                "01-01.subject", "ai-flowchart--scene-001"
            )

    def test_explicit_batch_builds_independently_hashed_requests(self):
        batch = self.subject.build_batch_request({
            "schemaVersion": 1,
            "pairs": [
                {
                    "taskId": "01-01.subject",
                    "candidateId": "counters-envato--scene-002",
                },
                {
                    "taskId": "02-02a.main",
                    "candidateId": "screen-mockup-rfx--review-002",
                },
            ],
        })
        self.assertEqual(batch["reviewState"], "awaiting_model_drafts")
        self.assertEqual(len(batch["requests"]), 2)
        self.assertNotEqual(
            batch["requests"][0]["requestSha256ForDraft"],
            batch["requests"][1]["requestSha256ForDraft"],
        )
        self.assertFalse(batch["selectionAuthorized"])
        self.assertFalse(batch["renderingAuthorized"])
        self.subject.validate_batch_request(batch)

    def test_batch_input_is_closed_nonempty_and_duplicate_free(self):
        with self.assertRaisesRegex(ValueError, "unknown fields"):
            self.subject.build_batch_request({
                "schemaVersion": 1,
                "pairs": [],
                "approval": {"decision": "approved"},
            })
        with self.assertRaisesRegex(ValueError, "at least one"):
            self.subject.build_batch_request({"schemaVersion": 1, "pairs": []})
        pair = {
            "taskId": "01-01.subject",
            "candidateId": "counters-envato--scene-002",
        }
        with self.assertRaisesRegex(ValueError, "duplicate treatment pair"):
            self.subject.build_batch_request({
                "schemaVersion": 1,
                "pairs": [pair, dict(pair)],
            })
        with self.assertRaisesRegex(ValueError, "only taskId and candidateId"):
            self.subject.build_batch_request({
                "schemaVersion": 1,
                "pairs": [{**pair, "renderingAuthorized": True}],
            })

    def test_batch_fails_closed_on_stale_hash_or_authorization(self):
        batch = self.subject.build_batch_request({
            "schemaVersion": 1,
            "pairs": [{
                "taskId": "01-01.subject",
                "candidateId": "counters-envato--scene-002",
            }],
        })
        stale = copy.deepcopy(batch)
        stale["batchSha256ForDrafts"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "batch request hash mismatch"):
            self.subject.validate_batch_request(stale)
        authorized = copy.deepcopy(batch)
        authorized["selectionAuthorized"] = True
        authorized_without_hash = dict(authorized)
        authorized_without_hash.pop("batchSha256ForDrafts")
        authorized["batchSha256ForDrafts"] = self.subject.artifact_sha(authorized_without_hash)
        with self.assertRaisesRegex(ValueError, "cannot authorize"):
            self.subject.validate_batch_request(authorized)

    def test_batch_build_is_deterministic(self):
        value = {
            "schemaVersion": 1,
            "pairs": [{
                "taskId": "01-01.subject",
                "candidateId": "counters-envato--scene-002",
            }],
        }
        self.assertEqual(
            self.subject.dumps(self.subject.build_batch_request(value)),
            self.subject.dumps(self.subject.build_batch_request(copy.deepcopy(value))),
        )

    def test_editor_review_assigns_zoom_to_post_not_template(self):
        root = Path(__file__).resolve().parents[1]
        review = json.loads(
            (root / "treatment-requirements" / "pilot-001" / "review-001.json").read_text()
        )
        treatment = review["approvedTreatment"]
        self.assertEqual(review["decision"], "approved_treatment_requirements")
        self.assertFalse(treatment["nativeZoomRequired"])
        self.assertTrue(treatment["postZoomAuthorized"])
        self.assertFalse(review["selectionAuthorized"])
        self.assertFalse(review["renderingAuthorized"])

    def test_approved_treatment_remains_conditional_on_resolution_and_timing(self):
        root = Path(__file__).resolve().parents[1]
        comparison = json.loads(
            (root / "treatment-requirements" / "pilot-001" / "capacity-comparison.json").read_text()
        )
        self.assertEqual(comparison["verdict"], "conditional")
        self.assertEqual(comparison["mediaAssessment"]["assetId"],
                         "9109a7d753a45dc6462b4baa")
        self.assertEqual(comparison["mediaAssessment"]["pixelWidth"], 546)
        self.assertEqual(len(comparison["templateAssessment"]["missingOrUnverified"]), 3)
        preparation = comparison["nativeTestPreparation"]
        self.assertEqual(preparation["status"], "gate_passed_render_blocked_by_ae_version")
        self.assertEqual(preparation["requiredAE"], "26.0")
        self.assertFalse(preparation["outputProduced"])
        self.assertFalse(preparation["zoomIncluded"])
        self.assertEqual(preparation["trimDurationSeconds"], 3.1)
        self.assertFalse(comparison["selectionAuthorized"])
        self.assertFalse(comparison["renderingAuthorized"])


if __name__ == "__main__":
    unittest.main()
