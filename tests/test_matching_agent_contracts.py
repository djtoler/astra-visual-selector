import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pipeline.matching_agent_contracts import AgentContractError, preflight, validate_task_contract


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class MatchingAgentContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        for name in ("story.json", "roster.json", "catalog.json"):
            (self.repo / name).write_text(json.dumps({"name": name}))
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run([
            "git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
            "commit", "-qm", "fixture",
        ], cwd=self.repo, check=True)
        self.commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        self.output = self.root / "out"
        self.task = {
            "schemaVersion": "matching-agent-task@1", "taskId": "task-1", "objectiveId": "objective-1",
            "owner": "matching", "requestedBy": "test",
            "storyPackage": {
                "repositoryId": "test/story", "repositoryRoot": str(self.repo), "repositoryCommit": self.commit,
                "path": str(self.repo / "story.json"), "sha256": digest(self.repo / "story.json"),
                "authorityRoot": str(self.repo), "authorityCommit": self.commit, "checkerPython": sys.executable,
            },
            "entityRoster": {
                "repositoryId": "test/roster", "repositoryRoot": str(self.repo), "repositoryCommit": self.commit,
                "path": str(self.repo / "roster.json"), "sha256": digest(self.repo / "roster.json"), "version": "1",
            },
            "templateCatalog": {
                "repositoryId": "test/catalog", "repositoryRoot": str(self.repo), "repositoryCommit": self.commit,
                "path": str(self.repo / "catalog.json"), "sha256": digest(self.repo / "catalog.json"), "identity": "catalog@1",
            },
            "repositoryMappings": [],
            "output": {"schema": "matching-agent-receipt@1", "directory": str(self.output)},
            "dependencyReceiptIds": [], "dependencyReceipts": [],
            "profile": {
                "profileId": "openai_gpt", "promptVersion": "matching-agent-prompt@1",
                "toolPolicy": "matching-tools@1", "permissionPolicy": "matching-review-only@1",
                "evaluationProfile": "matching-cross-story@1",
            },
            "toolAllowList": ["read_matching_artifacts"], "mutationScope": [str(self.root)],
            "acceptanceChecks": ["exact-inputs"], "timeoutClass": "standard", "retryClass": "none",
            "userInput": {"allowed": False, "required": False},
            "selectionAuthorized": False, "renderingAuthorized": False,
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_contract_and_preflight_bind_exact_inputs(self):
        validate_task_contract(self.task)
        receipt = preflight(self.task)
        self.assertEqual(receipt["inputs"]["storyPackage"]["repositoryCommit"], self.commit)
        self.assertEqual(receipt["outputDirectory"], str(self.output.resolve()))

    def test_branch_name_cannot_replace_commit(self):
        self.task["storyPackage"]["repositoryCommit"] = "main"
        with self.assertRaisesRegex(AgentContractError, "exact commit"):
            validate_task_contract(self.task)

    def test_moved_repository_fails_closed(self):
        (self.repo / "next.txt").write_text("next")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run([
            "git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
            "commit", "-qm", "moved",
        ], cwd=self.repo, check=True)
        with self.assertRaisesRegex(AgentContractError, "repository moved"):
            preflight(self.task)

    def test_stale_dependency_receipt_fails_closed(self):
        receipt = self.repo / "receipt.json"
        receipt.write_text("{}")
        self.task["dependencyReceiptIds"] = ["dep-1"]
        self.task["dependencyReceipts"] = [{"id": "dep-1", "path": str(receipt), "sha256": "0" * 64}]
        with self.assertRaisesRegex(AgentContractError, "digest is stale"):
            preflight(self.task)

    def test_authorization_flags_fail_closed(self):
        self.task["renderingAuthorized"] = True
        with self.assertRaisesRegex(AgentContractError, "cannot authorize"):
            validate_task_contract(self.task)
