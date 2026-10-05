import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "docs" / "astra-root-cause"


class FableRootCauseWorkflowTests(unittest.TestCase):
    def test_job_one_model_strategy_is_fail_closed(self):
        policy = json.loads((WORKFLOW / "EXECUTION_POLICY.json").read_text())
        job = policy["jobPolicies"]["01-system-map-and-evidence"]

        self.assertEqual(policy["auditBranch"], "fable_analysis")
        self.assertEqual(
            policy["matchingBaselineCommit"],
            "1276d0ca1daece81b5b7b38c8b5f5280046e5077",
        )
        self.assertEqual(job["requiredModel"], "fable")
        self.assertEqual(job["requiredModelDisplayName"], "Fable")
        self.assertEqual(job["requiredReasoningEffort"], "medium")
        self.assertTrue(job["resolvedModelIdMustBeRecorded"])
        self.assertFalse(job["publicModelIdVerified"])
        self.assertFalse(job["escalation"]["allowed"])
        self.assertTrue(job["escalation"]["requiresExplicitEditorInstruction"])
        self.assertFalse(job["escalation"]["wholeJobRerunAllowed"])
        self.assertTrue(job["receiptRequired"])

    def test_gold_references_exist_and_match_pinned_hashes(self):
        policy = json.loads((WORKFLOW / "EXECUTION_POLICY.json").read_text())

        self.assertEqual(len(policy["goldReferences"]), 2)
        for reference in policy["goldReferences"]:
            path = ROOT / reference["path"]
            self.assertTrue(path.is_file(), reference["path"])
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest, reference["sha256"])
            self.assertEqual(reference["designation"], "editor_perfect_reference")

    def test_job_one_prompt_requires_policy_and_gold_references(self):
        job = (WORKFLOW / "jobs" / "01-system-map-and-evidence.md").read_text()
        self.assertIn("EXECUTION_POLICY.json", job)
        self.assertIn("perfect reference", job.lower())
        self.assertIn("Fable", job)
        self.assertIn("medium", job.lower())
        self.assertIn("not change effort", job.lower())


if __name__ == "__main__":
    unittest.main()
