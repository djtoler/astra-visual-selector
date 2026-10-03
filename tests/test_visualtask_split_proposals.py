import copy
import json
import unittest
from pathlib import Path

from pipeline import visualtask_split_proposals as subject


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "semantic_split"


class ProviderIndependentSemanticSplitProposals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = {
            "story": FIXTURES / "story-package.json",
            "vocabulary": FIXTURES / "task-vocabulary.json",
            "roster": FIXTURES / "roster-context.json",
            "editor": FIXTURES / "editor-context.json",
        }
        cls.request = subject.prepare_request_from_files(
            cls.paths["story"], cls.paths["vocabulary"], cls.paths["roster"], cls.paths["editor"]
        )
        cls.response = subject.read(FIXTURES / "external-response.json")

    def test_unseen_story_external_response_passes(self):
        self.assertEqual(subject.validate_response(self.response, self.request), {
            "sourceBeats": 2,
            "keepSingle": 1,
            "proposedSplits": 1,
            "proposedTasks": 3,
            "humanApprovalPending": 2,
        })

    def test_request_is_deterministic_source_bound_and_provider_neutral(self):
        replay = subject.prepare_request_from_files(
            self.paths["story"], self.paths["vocabulary"], self.paths["roster"], self.paths["editor"]
        )
        self.assertEqual(subject.dumps(replay), subject.dumps(self.request))
        serialized = subject.dumps(self.request).lower()
        self.assertNotIn('"provider"', serialized)
        self.assertNotIn('"model"', serialized)
        self.assertEqual(set(self.request["sources"]), {
            "storyPackage", "taskVocabulary", "rosterContext", "editorContext",
        })

    def test_production_stage_contains_no_current_documentary_issue_ids(self):
        source = (ROOT / "pipeline" / "visualtask_split_proposals.py").read_text()
        for fixture_identifier in ("PI-05", "13-13a", "28-28", "year-seventeen"):
            self.assertNotIn(fixture_identifier, source)

    def test_split_spans_cover_every_source_character_exactly(self):
        story = subject.read(self.paths["story"])
        by_id = {row["id"]: row for row in story["beats"]}
        for proposal in self.response["beatProposals"]:
            text = by_id[proposal["sourceBeatId"]]["text"]
            self.assertEqual("".join(task["quote"] for task in proposal["tasks"]), text)

    def test_gap_or_overlap_fails_closed(self):
        broken = copy.deepcopy(self.response)
        broken["beatProposals"][0]["tasks"][1]["span"]["start"] += 1
        with self.assertRaisesRegex(ValueError, "exact, complete and nonoverlapping"):
            subject.validate_response(broken, self.request)

    def test_non_exact_quote_fails_closed(self):
        broken = copy.deepcopy(self.response)
        broken["beatProposals"][0]["tasks"][0]["quote"] = "Invented text."
        with self.assertRaisesRegex(ValueError, "exact source span"):
            subject.validate_response(broken, self.request)

    def test_missing_beat_fails_closed(self):
        broken = copy.deepcopy(self.response)
        broken["beatProposals"].pop()
        with self.assertRaisesRegex(ValueError, "assess every beat exactly once"):
            subject.validate_response(broken, self.request)

    def test_unknown_job_fails_closed(self):
        broken = copy.deepcopy(self.response)
        broken["beatProposals"][0]["tasks"][0]["visualJob"] = "invented_job"
        with self.assertRaisesRegex(ValueError, "unknown job or role"):
            subject.validate_response(broken, self.request)

    def test_out_of_beat_roster_reference_fails_closed(self):
        broken = copy.deepcopy(self.response)
        broken["beatProposals"][0]["tasks"][0]["entityRefs"] = ["aisha-patel"]
        with self.assertRaisesRegex(ValueError, "out-of-beat entityRefs"):
            subject.validate_response(broken, self.request)

    def test_lost_truth_or_requirement_fails_closed(self):
        broken = copy.deepcopy(self.response)
        broken["beatProposals"][0]["tasks"][1]["truthConstraintRefs"] = []
        with self.assertRaisesRegex(ValueError, "loses source truthConstraintRefs"):
            subject.validate_response(broken, self.request)

    def test_closed_schema_rejects_extra_fields(self):
        broken = copy.deepcopy(self.response)
        broken["beatProposals"][0]["tasks"][0]["confidence"] = 0.99
        with self.assertRaisesRegex(ValueError, "unsupported fields"):
            subject.validate_response(broken, self.request)
        schema = json.loads((ROOT / "grammar" / "semantic-split-proposal.schema.json").read_text())
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(schema["$defs"]["task"]["additionalProperties"])

    def test_response_cannot_invent_human_approval_or_activation(self):
        approved = copy.deepcopy(self.response)
        approved["humanApproval"] = {"status": "approved", "reviewer": "editor", "reviewedAt": "now"}
        with self.assertRaisesRegex(ValueError, "cannot invent human approval"):
            subject.validate_response(approved, self.request)
        active = copy.deepcopy(self.response)
        active["activationState"] = "active"
        with self.assertRaisesRegex(ValueError, "must remain review-only"):
            subject.validate_response(active, self.request)

    def test_stale_request_hash_fails_closed(self):
        broken = copy.deepcopy(self.response)
        broken["requestSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "request hash mismatch"):
            subject.validate_response(broken, self.request)

    def test_input_contract_is_closed_and_story_scoped(self):
        story = subject.read(self.paths["story"])
        vocabulary = subject.read(self.paths["vocabulary"])
        roster = subject.read(self.paths["roster"])
        editor = subject.read(self.paths["editor"])
        story["unknownField"] = True
        with self.assertRaisesRegex(ValueError, "unsupported fields"):
            subject.prepare_request(story, vocabulary, roster, editor)
        story.pop("unknownField")
        editor["storyId"] = "another-story"
        with self.assertRaisesRegex(ValueError, "another story"):
            subject.prepare_request(story, vocabulary, roster, editor)


if __name__ == "__main__":
    unittest.main()
