import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "docs" / "astra-root-cause"


class FableRootCauseWorkflowTests(unittest.TestCase):
    def test_executor_matrix_is_fail_closed(self):
        policy = json.loads((WORKFLOW / "EXECUTION_POLICY.json").read_text())
        jobs = policy["jobPolicies"]

        self.assertEqual(policy["auditBranch"], "fable_analysis")
        self.assertEqual(
            policy["matchingBaselineCommit"],
            "1276d0ca1daece81b5b7b38c8b5f5280046e5077",
        )
        self.assertEqual(len(jobs), 8)
        desktop = {
            "01-system-map-and-evidence",
            "03-upstream-contract-fitness",
            "04-matching-transformations",
            "05-grammar-tags-capabilities",
            "06-candidate-pipeline",
        }
        fable = {
            "02-story-semantics",
            "07-human-evidence-and-reference-evaluation",
            "08-integrated-root-cause-and-redesign",
        }
        for name in desktop:
            self.assertEqual(jobs[name]["requiredOperator"], "claude_desktop")
            self.assertEqual(jobs[name]["requiredExecutionMode"], "desktop_conversation")
        for name in fable:
            self.assertEqual(jobs[name]["requiredOperator"], "claude_desktop")
            self.assertEqual(
                jobs[name]["requiredExecutionMode"],
                "claude_cli_invoked_from_desktop",
            )
            self.assertEqual(jobs[name]["requiredModel"], "claude-fable-5-1")
            self.assertEqual(jobs[name]["requiredReasoningEffort"], "medium")
        self.assertTrue(policy["defaultJobPolicy"]["pushRequired"])
        self.assertTrue(policy["defaultJobPolicy"]["directOutputLinksRequired"])
        self.assertTrue(policy["defaultJobPolicy"]["oneJobPerTurn"])
        corrections = policy["correctionPolicy"]
        self.assertEqual(
            corrections["canonicalFile"],
            "docs/astra-root-cause/CORRECTION_REQUESTS.md",
        )
        self.assertTrue(corrections["singleCorrectionFileRequired"])
        self.assertTrue(corrections["activeCorrectionBlocksNextJob"])
        self.assertTrue(corrections["directCorrectionFileLinkRequired"])

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
        self.assertIn("Claude Desktop", job)
        self.assertIn("do not", job.lower())

    def test_master_prompt_requires_publication_and_executor_switches(self):
        prompt = (WORKFLOW / "MASTER_PROMPT.md").read_text()
        self.assertIn("Claude Desktop is the operator", prompt)
        self.assertIn("For Jobs 2, 7 and 8, Claude Desktop must invoke the Claude CLI", prompt)
        self.assertIn("claude-fable-5-1", prompt)
        self.assertIn("direct clickable GitHub links", prompt)
        self.assertIn("Commit and push", prompt)

    def test_corrections_use_one_canonical_file(self):
        canonical = WORKFLOW / "CORRECTION_REQUESTS.md"
        self.assertTrue(canonical.is_file())
        statuses = re.findall(r"^Status: \*\*(ACTIVE|RESOLVED)\*\*", canonical.read_text(), re.MULTILINE)
        self.assertTrue(statuses)
        self.assertTrue(set(statuses) <= {"ACTIVE", "RESOLVED"})
        self.assertEqual(list(WORKFLOW.glob("*CORRECTION*.md")), [canonical])
        self.assertFalse((WORKFLOW / "JOB_03_CORRECTION_REQUEST.md").exists())
        prompt = (WORKFLOW / "MASTER_PROMPT.md").read_text()
        self.assertIn("An `ACTIVE` correction takes\npriority", prompt)
        self.assertIn("Never create another correction-request file", prompt)


if __name__ == "__main__":
    unittest.main()
