import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "docs" / "astra-root-cause"


class AstraRootCauseWorkflowTests(unittest.TestCase):
    def test_job_one_model_strategy_is_fail_closed(self):
        policy = json.loads((WORKFLOW / "EXECUTION_POLICY.json").read_text())
        job = policy["jobPolicies"]["01-system-map-and-evidence"]

        self.assertEqual(job["requiredModel"], "gpt-6-astra")
        self.assertEqual(job["requiredReasoningEffort"], "medium")
        self.assertEqual(job["escalation"]["allowedReasoningEfforts"], ["high", "ultra"])
        self.assertEqual(
            job["escalation"]["scope"],
            "single_narrow_architectural_question_only",
        )
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
        self.assertIn("gpt-6-astra", job)
        self.assertIn("medium", job.lower())
        self.assertIn("Do not rerun the complete job", job)


if __name__ == "__main__":
    unittest.main()
