import copy
import unittest


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

    def test_build_is_deterministic(self):
        self.assertEqual(
            self.subject.dumps(self.subject.build_pilot_request()),
            self.subject.dumps(self.subject.build_pilot_request()),
        )


if __name__ == "__main__":
    unittest.main()
