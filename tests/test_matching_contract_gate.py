import copy
import json
import re
import unittest

from pipeline import matching_contract_gate as subject
from pipeline import matching_harness


class MatchingContractGateTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads(subject.ENTRYPOINT_CONTRACT.read_text())

    def test_every_registered_entrypoint_contains_mandatory_gate_call(self):
        for row in self.registry["entrypoints"]:
            source = (subject.ROOT / row["module"]).read_text()
            pattern = rf"enforce_contracts\(\s*[\"']{re.escape(row['id'])}[\"']"
            self.assertRegex(source, pattern, row["id"])

    def test_review_entrypoint_receipt_is_hash_bound_and_never_authorizes(self):
        receipt = subject.enforce_contracts("storypackage_splitter.build")
        self.assertTrue(receipt["enforced"])
        self.assertEqual(receipt["mode"], "review_only")
        self.assertFalse(receipt["selectionAuthorized"])
        self.assertFalse(receipt["renderingAuthorized"])
        self.assertEqual(set(receipt["contracts"]), {"generalMatching", "stageOrder", "entrypoints"})
        self.assertTrue(all(len(row["sha256"]) == 64 for row in receipt["contracts"].values()))

    def test_unknown_entrypoint_fails_closed(self):
        with self.assertRaisesRegex(subject.MatchingContractError, "unregistered"):
            subject.enforce_contracts("unregistered.build")

    def test_invalid_general_contract_fails_closed(self):
        contract = json.loads(subject.GENERAL_CONTRACT.read_text())
        broken = copy.deepcopy(contract)
        broken["runtime"]["storySpecificBranchesAllowed"] = True
        with self.assertRaisesRegex(subject.MatchingContractError, "permits"):
            subject._validate_general(broken)

    def test_review_rule_principles_fail_closed(self):
        contract = json.loads(subject.GENERAL_CONTRACT.read_text())
        broken = copy.deepcopy(contract)
        broken["reviewReconciliation"]["rules"]["incidentalNumbersDoNotCreateDataJobs"] = False
        with self.assertRaisesRegex(subject.MatchingContractError, "editor-review rule"):
            subject._validate_general(broken)

    def test_non_harness_entrypoint_cannot_request_production(self):
        with self.assertRaisesRegex(subject.MatchingContractError, "does not allow mode"):
            subject.enforce_contracts("storypackage_candidate_gallery.build", mode="production")

    def test_harness_receipt_is_mandatory_after_generality_passes(self):
        audit = matching_harness.build()
        receipt = audit["contractEnforcementReceipt"]
        self.assertTrue(receipt["enforced"])
        self.assertEqual(receipt["entrypoint"], "matching_harness.build")
        self.assertEqual(audit["firstBlockingStage"], "render_release_handoff")
        self.assertFalse(audit["continuation"]["continuationRequired"])
        self.assertFalse(audit["continuation"]["userInputRequired"])
        self.assertIsNone(audit["continuation"]["nextTaskId"])
        self.assertEqual(audit["continuation"]["currentBlocker"]["party"], "none")


if __name__ == "__main__":
    unittest.main()
