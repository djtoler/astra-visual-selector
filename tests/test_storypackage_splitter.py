import copy
import json
import unittest
from pathlib import Path

from pipeline import storypackage_splitter as subject


class StoryPackageSplitterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapter_path = Path(__file__).resolve().parents[1] / "reports/storypackage-02-apollo-adapter.json"
        cls.adapter = json.loads(cls.adapter_path.read_text())

    def test_one_claim_can_produce_multiple_task_proposals(self):
        artifact = subject.build(self.adapter, source_path=self.adapter_path)
        rows = [row for row in artifact["taskProposals"] if row["claimIds"] == ["a1"]]
        self.assertEqual({row["jobProposalId"] for row in rows}, {"pa1-1", "pa1-2"})
        self.assertEqual(len({row["taskProposalId"] for row in rows}), 2)

    def test_multiple_claims_can_share_one_task_proposal(self):
        artifact = subject.build(self.adapter, source_path=self.adapter_path)
        row = next(row for row in artifact["taskProposals"] if row["jobProposalId"] == "pa4")
        self.assertEqual(row["claimIds"], ["a4", "a5"])
        self.assertEqual(len(row["claimSpans"]), 2)

    def test_review_keys_survive_for_current_visualtask_reconciliation(self):
        artifact = subject.build(self.adapter, source_path=self.adapter_path)
        self.assertIn("reviewKeys", artifact["taskProposals"][0])

    def test_splitter_preserves_roles_obligations_and_gaps_without_activation(self):
        artifact = subject.build(self.adapter, source_path=self.adapter_path)
        pa2 = next(row for row in artifact["taskProposals"] if row["jobProposalId"] == "pa2")
        self.assertTrue(any(ref["display"] == "withheld" for ref in pa2["entityRefs"]))
        self.assertTrue(any(row["gap"] == "cohort_incomplete" for row in artifact["gaps"]))
        self.assertFalse(any(row["gap"] == "job_proposal_missing" for row in artifact["gaps"]))
        self.assertEqual(artifact["counts"]["uncoveredClaims"], 0)
        self.assertEqual(artifact["counts"]["semanticDerivedTaskProposals"], 1)
        self.assertEqual(artifact["activationState"], "review_only_not_connected")
        self.assertFalse(artifact["selectionAuthorized"])
        self.assertFalse(artifact["renderingAuthorized"])

    def test_unaccepted_adapter_is_rejected(self):
        broken = copy.deepcopy(self.adapter)
        broken["storyHandoffReceipt"]["accepted"] = False
        with self.assertRaisesRegex(ValueError, "accepted StoryPackage adapter receipt"):
            subject.build(broken, source_path=self.adapter_path)

    def test_speaker_roles_route_clips_and_quotes_without_illustrating_clip_claims(self):
        adapter = {
            "storyHandoffReceipt": {"accepted": True},
            "selectionAuthorized": False,
            "renderingAuthorized": False,
            "story": {"storyId": "speaker-test"},
            "packageId": "speaker-test@1",
            "claims": [
                {"claimId": "c1", "beatId": "b1", "span": {"start": 0, "len": 4}, "lane": "factual"},
                {"claimId": "c2", "beatId": "b2", "span": {"start": 4, "len": 4}, "lane": "factual"},
                {"claimId": "c3", "beatId": "b3", "span": {"start": 8, "len": 4}, "lane": "editorial"},
            ],
            "beats": [
                {"beatId": "b1", "order": 0, "claimIds": ["c1"], "speaker": {"role": "clip", "sourceTimestamp": "00:00:01"}},
                {"beatId": "b2", "order": 1, "claimIds": ["c2"], "speaker": {"role": "quote", "entity": "Person"}},
                {"beatId": "b3", "order": 2, "claimIds": ["c3"], "speaker": {"role": "narrator"}},
            ],
            "jobProposals": [],
            "obligations": [],
            "continuity": [],
            "gaps": [],
        }
        artifact = subject.build(adapter, source_path=self.adapter_path)
        self.assertEqual(artifact["counts"]["sourceClipRoutes"], 1)
        self.assertEqual(artifact["counts"]["quoteRoutes"], 1)
        self.assertEqual(artifact["counts"]["speakerDerivedTaskProposals"], 1)
        self.assertEqual(artifact["taskProposals"][0]["job"], "attributed_quote")
        self.assertFalse(next(row for row in artifact["speakerRoutes"] if row["role"] == "clip")["templateMatchingEligible"])
        derived = next(row for row in artifact["taskProposals"] if row["claimIds"] == ["c3"])
        self.assertTrue(derived["semanticDerived"])
        self.assertEqual(derived["jobProvenance"]["source"], "matching_semantic_splitter")
        self.assertEqual(artifact["counts"]["uncoveredClaims"], 0)

    def test_narrator_beat_splits_into_review_sized_semantic_moments(self):
        adapter = {
            "storyHandoffReceipt": {"accepted": True},
            "selectionAuthorized": False,
            "renderingAuthorized": False,
            "story": {"storyId": "semantic-moments"},
            "packageId": "semantic-moments@1",
            "claims": [
                {"claimId": "c1", "beatId": "b1", "span": {"start": 0, "len": 14}, "lane": "editorial", "text": "Who is Artist?", "entityRefs": [{"entity": "Artist", "display": "required"}]},
                {"claimId": "c2", "beatId": "b1", "span": {"start": 15, "len": 29}, "lane": "editorial", "text": "Well, you know who Artist is.", "entityRefs": [{"entity": "Artist", "display": "required"}]},
                {"claimId": "c3", "beatId": "b1", "span": {"start": 45, "len": 37}, "lane": "factual", "text": "They are the fifth most streamed act.", "entityRefs": [{"entity": "Artist", "display": "eligible"}]},
                {"claimId": "c4", "beatId": "b1", "span": {"start": 83, "len": 65}, "lane": "editorial", "text": "They influenced a generation — not just rap, but also all of pop.", "entityRefs": [{"entity": "Artist", "display": "required"}]},
                {"claimId": "c5", "beatId": "b1", "span": {"start": 149, "len": 43}, "lane": "editorial", "text": "But they remain the most misunderstood act.", "entityRefs": [{"entity": "Artist", "display": "eligible"}]},
            ],
            "beats": [{
                "beatId": "b1", "order": 0, "claimIds": ["c1", "c2", "c3", "c4", "c5"],
                "span": {"start": 0, "len": 192}, "speaker": {"role": "narrator"},
                "narration": "Who is Artist? Well, you know who Artist is. They are the fifth most streamed act. They influenced a generation — not just rap, but also all of pop. But they remain the most misunderstood act.",
            }],
            "jobProposals": [], "obligations": [], "continuity": [], "gaps": [],
        }
        artifact = subject.build(adapter, source_path=self.adapter_path)
        rows = artifact["taskProposals"]
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["claimIds"], ["c1", "c2"])
        self.assertEqual(rows[0]["taskText"].strip(), "Who is Artist? Well, you know who Artist is.")
        self.assertEqual(rows[3]["claimIds"], ["c4"])
        self.assertEqual(rows[3]["taskText"].strip(), "but also all of pop.")
        self.assertEqual("".join(row["taskText"] for row in rows), adapter["beats"][0]["narration"])
        self.assertEqual(artifact["counts"]["uncoveredClaims"], 0)

    def test_adjacent_claims_with_one_visual_payload_are_not_forced_into_one_task_each(self):
        adapter = {
            "storyHandoffReceipt": {"accepted": True}, "selectionAuthorized": False,
            "renderingAuthorized": False, "story": {"storyId": "same-payload"},
            "packageId": "same-payload@1",
            "claims": [
                {"claimId": "c1", "beatId": "b1", "span": {"start": 0, "len": 22}, "lane": "factual", "text": "Artist released Alpha.", "entityRefs": [{"entity": "Artist", "display": "required"}]},
                {"claimId": "c2", "beatId": "b1", "span": {"start": 23, "len": 21}, "lane": "factual", "text": "Artist released Beta.", "entityRefs": [{"entity": "Artist", "display": "required"}]},
            ],
            "beats": [{"beatId": "b1", "order": 0, "span": {"start": 0, "len": 44},
                       "claimIds": ["c1", "c2"], "speaker": {"role": "narrator"},
                       "narration": "Artist released Alpha. Artist released Beta."}],
            "jobProposals": [], "obligations": [], "continuity": [], "gaps": [],
        }
        artifact = subject.build(adapter, source_path=self.adapter_path)
        self.assertEqual(len(artifact["taskProposals"]), 1)
        self.assertEqual(artifact["taskProposals"][0]["claimIds"], ["c1", "c2"])
        self.assertTrue(artifact["granularityPolicy"]["claimBoundaryIsEvidenceNotTaskBoundary"])

    def test_future_opening_is_a_five_moment_system_regression(self):
        path = Path(__file__).resolve().parents[1] / "reports/storypackage-02-future-volksgeist-adapter.json"
        adapter = json.loads(path.read_text())
        artifact = subject.build(adapter, source_path=path)
        rows = [row for row in artifact["taskProposals"]
                if any(beat["beatId"] == "p01-1" for beat in row["sourceBeats"])]
        source = next(beat["narration"] for beat in adapter["beats"] if beat["beatId"] == "p01-1")
        self.assertEqual(len(rows), 5)
        self.assertEqual("".join(row["taskText"] for row in rows), source)
        self.assertTrue(all(row["semanticDerived"] for row in rows))

    def test_runtime_has_no_future_story_identifiers(self):
        source = Path(subject.__file__).read_text()
        for value in ("future-volksgeist", "p01-1", "Future"):
            self.assertNotIn(value, source)

    def test_year_alone_is_not_mislabeled_as_data_explanation(self):
        operations = subject._presentation_operations(
            text="His first song arrived in 2003.", claim_rows=[{"entityRefs": [], "values": [], "cohortRefs": []}],
        )
        self.assertIn("archival_progression", operations)
        self.assertNotIn("data_explanation", operations)

    def test_when_statement_is_not_mislabeled_as_rhetorical_question(self):
        operations = subject._presentation_operations(
            text="When he arrived, the room changed.", claim_rows=[{"entityRefs": [], "values": [], "cohortRefs": []}],
        )
        self.assertNotIn("rhetorical_question", operations)

    def test_plural_artifact_without_enumeration_is_not_an_item_sequence(self):
        operations = subject._presentation_operations(
            text="He does not just make entertaining songs.", claim_rows=[{"entityRefs": [], "values": [], "cohortRefs": []}],
        )
        self.assertNotIn("item_sequence", operations)


if __name__ == "__main__":
    unittest.main()
