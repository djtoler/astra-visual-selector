import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

from pipeline.matching_agent_config import resolve_profile
from pipeline.matching_agent_runner import AgentRunnerError, CodexCliRunner


class MatchingAgentRunnerTests(unittest.TestCase):
    def test_codex_cli_adapter_parses_only_schema_bound_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / "fake-codex"
            executable.write_text("""#!/usr/bin/env python3
import json, sys
args = sys.argv[1:]
out = args[args.index('--output-last-message') + 1]
prompt = sys.stdin.read()
task = prompt.split('taskId ', 1)[1].split(' ', 1)[0]
package = prompt.split('packageId ', 1)[1].split('.', 1)[0]
json.dump({'schemaVersion':'matching-agent-review@1','taskId':task,'packageId':package,'reviewSummary':'Bound review.','warnings':[],'typedGaps':[],'selectionAuthorized':False,'renderingAuthorized':False}, open(out, 'w'))
print(json.dumps({'thread_id':'thread-test','model':'gpt-test','usage':{'input_tokens':10,'output_tokens':4}}))
""")
            executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
            configuration = resolve_profile(environment={"MATCHING_OPENAI_MODEL": "gpt-test"})
            runner = CodexCliRunner(executable)
            task = {"taskId": "task-1", "_packageIdForRunner": "package-1", "timeoutClass": "short"}
            handle = runner.run(task, root, configuration)
            receipt = runner.collect(handle)
            self.assertEqual(receipt["review"]["packageId"], "package-1")
            self.assertEqual(receipt["servedModel"], "gpt-test")
            self.assertEqual(receipt["cost"], "unsupported")
            self.assertFalse(receipt["selectionAuthorized"])

    def test_steer_is_not_faked(self):
        runner = CodexCliRunner("codex")
        with self.assertRaisesRegex(AgentRunnerError, "does not declare"):
            runner.steer(None, "message")
