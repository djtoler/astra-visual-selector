import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pipeline.matching_agent import run_task
from pipeline.matching_agent_runner import AgentRunnerError


class FakeRunner:
    def __init__(self, fail=False):
        self.fail = fail

    def capabilities(self):
        return {
            "schemaVersion": "matching-agent-capability-manifest@1", "runner": "FakeRunner",
            "operations": {"run": True, "status": False, "steer": False, "cancel": False, "collect": True},
            "servedModelTelemetry": "reported_when_available", "costTelemetry": "unsupported",
            "selectionAuthorized": False, "renderingAuthorized": False,
        }

    def run(self, task, workspace, profile):
        return {"task": task, "profile": profile}

    def collect(self, handle):
        if self.fail:
            raise AgentRunnerError("provider failed")
        return {
            "schemaVersion": "matching-agent-runner-receipt@1", "runId": "fake", "status": "passed",
            "review": {
                "schemaVersion": "matching-agent-review@1", "taskId": handle["task"]["taskId"],
                "packageId": handle["task"]["_packageIdForRunner"], "reviewSummary": "Review complete.",
                "warnings": [], "typedGaps": [], "selectionAuthorized": False, "renderingAuthorized": False,
            },
            "provider": "openai", "configuredModel": "gpt-6-astra", "servedModel": "gpt-test",
            "transport": "cli", "reasoningEffort": "high", "providerSessionId": "fake-session",
            "startedAt": "start", "endedAt": "end", "wallTimeSeconds": 0.1,
            "usage": "unavailable", "cost": "unsupported", "selectionAuthorized": False,
            "renderingAuthorized": False,
        }


class MatchingAgentCommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.output = self.root / "output"
        self.task = {
            "schemaVersion": "matching-agent-task@1", "taskId": "task-1", "objectiveId": "objective-1",
            "owner": "matching", "requestedBy": "test",
            "storyPackage": {
                "repositoryId": "story/repo", "repositoryRoot": "/story", "repositoryCommit": "1" * 40,
                "path": "/story/package.json", "sha256": "2" * 64,
                "authorityRoot": "/story", "authorityCommit": "1" * 40, "checkerPython": "/python",
            },
            "entityRoster": {
                "repositoryId": "djtoler/entity_roster", "repositoryRoot": "/roster", "repositoryCommit": "3" * 40,
                "path": "/roster/entity-roster.json", "sha256": "4" * 64, "version": "12",
            },
            "templateCatalog": {
                "repositoryId": "catalog/repo", "repositoryRoot": "/catalog", "repositoryCommit": "5" * 40,
                "path": "/catalog/approved-list.json", "sha256": "6" * 64, "identity": "approved@1",
            },
            "output": {"schema": "matching-agent-receipt@1", "directory": str(self.output)},
            "dependencyReceiptIds": [], "dependencyReceipts": [],
            "profile": {
                "profileId": "openai_gpt", "promptVersion": "matching-agent-prompt@1",
                "toolPolicy": "matching-tools@1", "permissionPolicy": "matching-review-only@1",
                "evaluationProfile": "matching-cross-story@1",
            },
            "toolAllowList": ["read_matching_artifacts"], "mutationScope": [str(self.root)],
            "acceptanceChecks": ["complete-routing"], "timeoutClass": "standard", "retryClass": "none",
            "userInput": {"allowed": False, "required": False},
            "selectionAuthorized": False, "renderingAuthorized": False,
        }
        self.task_path = self.root / "task.json"
        self.task_path.write_text(json.dumps(self.task))
        self.preflight = {
            "schemaVersion": "matching-agent-preflight@1", "taskId": "task-1",
            "inputs": {
                "storyPackage": {**self.task["storyPackage"], "path": "/story/package.json", "authorityRoot": "/story", "checkerPython": "/python"},
                "entityRoster": {**self.task["entityRoster"], "path": "/roster/entity-roster.json"},
                "templateCatalog": {**self.task["templateCatalog"], "path": "/catalog/approved-list.json"},
                "dependencyReceipts": [],
            },
            "outputDirectory": str(self.output), "dependencyReceiptIds": [],
            "selectionAuthorized": False, "renderingAuthorized": False,
        }
        self.adapter = {
            "packageId": "package-1", "entityRegistry": {"snapshot": {
                "repo": "djtoler/entity_roster", "commit": "3" * 40, "sha256": "4" * 64,
            }},
            "storyHandoffReceipt": {"accepted": True}, "selectionAuthorized": False,
            "renderingAuthorized": False, "claims": [], "beats": [], "story": {"storyId": "story-1"},
        }
        self.proposals = {
            "packageId": "package-1", "activationState": "review_only_not_connected",
            "taskProposals": [{
                "taskProposalId": "proposal-1", "claimIds": ["claim-1"], "values": [], "cohortRefs": [],
                "entityRefs": [], "primaryPresentationOperation": "concept_statement",
            }],
            "speakerRoutes": [], "counts": {"claims": 1, "taskProposals": 1, "uncoveredClaims": 0},
            "selectionAuthorized": False, "renderingAuthorized": False,
        }
        self.gallery = {
            "packageId": "package-1", "tasks": [{
                "taskId": "proposal-1", "sourceBeatIds": ["beat-1"], "candidates": [{"id": "template-1"}],
                "routeDisposition": {"templateEligible": True},
            }], "clipRoutes": [],
            "counts": {"candidateCards": 1, "tasksWithoutCandidates": 0},
            "selectionAuthorized": False, "renderingAuthorized": False,
        }
        self.harness = {
            "generalMatchingLayer": {"complete": True}, "firstBlockingStage": "render_release_handoff",
            "selectionAuthorized": False, "renderingAuthorized": False,
        }

    def tearDown(self):
        self.temp.cleanup()

    def patches(self):
        return (
            mock.patch("pipeline.matching_agent.preflight", return_value=self.preflight),
            mock.patch("pipeline.matching_agent.storypackage_adapter.build", return_value=self.adapter),
            mock.patch("pipeline.matching_agent.storypackage_splitter.build", return_value=self.proposals),
            mock.patch("pipeline.matching_agent.storypackage_candidate_gallery.build", return_value=self.gallery),
            mock.patch("pipeline.matching_agent.matching_harness.build", return_value=self.harness),
            mock.patch("pipeline.matching_agent.matching_harness.validate", return_value={}),
        )

    def test_public_command_writes_complete_review_artifacts(self):
        patches = self.patches()
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
            receipt = run_task(self.task_path, runner=FakeRunner())
        self.assertEqual(receipt["status"], "passed")
        self.assertEqual(receipt["currentBlocker"]["party"], "none")
        self.assertFalse(receipt["selectionAuthorized"])
        self.assertFalse(receipt["renderingAuthorized"])
        for name in (
            "00-preflight.json", "10-storypackage-adapter.json", "20-visualtask-proposals.json",
            "30-data-media-requirements.json", "40-candidate-admissions.json",
            "50-ordered-review-route.json", "60-matching-harness-audit.json",
            "90-candidate-review.json", "matching-agent-receipt.json",
        ):
            self.assertTrue((self.output / name).is_file(), name)

    def test_provider_failure_preserves_partial_artifacts_and_failed_receipt(self):
        patches = self.patches()
        with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
            with self.assertRaises(AgentRunnerError):
                run_task(self.task_path, runner=FakeRunner(fail=True))
        receipt = json.loads((self.output / "matching-agent-receipt.json").read_text())
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(receipt["currentBlocker"]["party"], "matching")
        self.assertTrue((self.output / "40-candidate-admissions.json").is_file())
        self.assertFalse(receipt["selectionAuthorized"])
