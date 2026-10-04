import json
import tempfile
import unittest
from pathlib import Path

from pipeline.matching_agent_config import AgentConfigurationError, resolve_profile


class MatchingAgentConfigTests(unittest.TestCase):
    def test_default_openai_profile_resolves_and_is_digest_bound(self):
        first = resolve_profile(environment={})
        second = resolve_profile(environment={})
        self.assertEqual(first["configuredTuple"]["profileId"], "openai_gpt")
        self.assertEqual(first["configuredTuple"]["model"], "gpt-6-astra")
        self.assertEqual(first["configuredTupleSha256"], second["configuredTupleSha256"])
        self.assertFalse(first["selectionAuthorized"])
        self.assertFalse(first["renderingAuthorized"])

    def test_alternate_profile_resolves_without_domain_change(self):
        receipt = resolve_profile(
            profile_id="anthropic_challenger",
            environment={"MATCHING_ANTHROPIC_MODEL": "claude-test"},
        )
        self.assertEqual(receipt["configuredTuple"]["provider"], "anthropic")
        self.assertEqual(receipt["configuredTuple"]["runner"], "unavailable")

    def test_unresolved_required_variable_fails_closed(self):
        with self.assertRaisesRegex(AgentConfigurationError, "unresolved"):
            resolve_profile(profile_id="anthropic_challenger", environment={})

    def test_unknown_profile_key_fails_closed(self):
        source = json.loads(Path("config/matching-agent-profiles.yaml").read_text())
        source["profiles"]["openai_gpt"]["secret"] = "not-allowed"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.yaml"
            path.write_text(json.dumps(source))
            with self.assertRaisesRegex(AgentConfigurationError, "unknown"):
                resolve_profile(path, environment={})
