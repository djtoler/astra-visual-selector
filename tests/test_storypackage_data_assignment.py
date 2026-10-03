import copy
import json
import tempfile
import unittest
from pathlib import Path

from pipeline import storypackage_data_assignment as subject


class StoryPackageDataAssignmentTests(unittest.TestCase):
    def test_every_queue_assignment_receives_a_typed_result(self):
        artifact = subject.build()
        queue = json.loads(subject.DEFAULT_QUEUE.read_text())
        self.assertEqual(len(artifact["assignments"]), 28)
        self.assertEqual(
            {row["taskId"] for row in artifact["assignments"]},
            {row["taskId"] for row in queue["assignments"]},
        )
        self.assertTrue(all(row["status"] in {"resolved", "partial", "blocked"} for row in artifact["assignments"]))
        self.assertTrue(all(row["typedFields"] or row["gaps"] for row in artifact["assignments"]))
        for row in artifact["assignments"]:
            covered = {encoding for field in row["typedFields"] for encoding in field["encodings"]}
            covered.update(encoding for gap in row["gaps"] for encoding in gap["encodings"])
            self.assertTrue(set(row["requiredEncodings"]).issubset(covered), row["taskId"])

    def test_reproduces_key_values_without_reading_numbers_from_narration(self):
        artifact = subject.build()
        by_task = {row["taskId"]: row for row in artifact["assignments"]}
        fields = {row["fieldId"]: row for row in by_task["01-01.subject"]["typedFields"]}
        self.assertEqual(fields["drake.daily_streams"]["value"], 58525904)
        self.assertAlmostEqual(fields["drake.streams_per_second"]["value"], 677.3831481481481)
        shares = {row["fieldId"]: row for row in by_task["11-11a.main"]["typedFields"]}
        self.assertAlmostEqual(shares["drake.top_song_share"]["value"], 0.031670127618631)
        self.assertAlmostEqual(shares["drake.top_10_share"]["value"], 0.15119603068872545)
        combined = {row["fieldId"]: row for row in by_task["22-22.main"]["typedFields"]}
        self.assertAlmostEqual(combined["xxl_2009_2010.weighted_total"]["value"], 121979432135.5)
        self.assertAlmostEqual(combined["xxl_2009_2010.edge_over_drake"]["value"], 0.03158447177815549)
        self.assertTrue(all(field["receipt"]["sourceSha256"] for row in artifact["assignments"] for field in row["typedFields"]))

    def test_established_derived_outputs_are_reused_and_absence_is_not_zero(self):
        artifact = subject.build()
        by_task = {row["taskId"]: row for row in artifact["assignments"]}
        biz = by_task["09-09.main"]
        self.assertEqual(biz["status"], "resolved")
        biz_field = next(field for field in biz["typedFields"] if field.get("subject") == "Biz Markie")
        self.assertEqual(biz_field["value"], 0.793137)
        self.assertEqual(biz_field["receipt"]["source"], "catalogConcentration")
        ranks = by_task["12-12a.main"]
        self.assertEqual(ranks["status"], "resolved")
        rank_fields = {field["subject"]: field for field in ranks["typedFields"]}
        self.assertEqual(rank_fields["Ab-Soul"]["value"]["rankDrop"], 28)
        self.assertEqual(rank_fields["Latto"]["value"]["rankDrop"], 13)
        self.assertEqual(rank_fields["Jay Rock"]["value"]["rankDrop"], 12)
        self.assertEqual(rank_fields["Ab-Soul"]["receipt"]["source"], "counterfactualRankings")
        historical = by_task["30-30a.main"]
        self.assertEqual(historical["status"], "resolved")
        self.assertEqual(historical["typedFields"][0]["value"]["availability"], "unavailable")
        self.assertIsNone(historical["typedFields"][0]["value"]["value"])

    def test_source_hash_tampering_fails_validation(self):
        artifact = subject.build()
        broken = copy.deepcopy(artifact)
        broken["sources"]["spotifyStreams"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source receipt is stale"):
            subject.validate(broken)

    def test_complete_data_never_authorizes_selection_or_rendering(self):
        artifact = subject.build()
        self.assertTrue(artifact["dataHandoffComplete"])
        self.assertEqual(artifact["counts"]["typedGaps"], 0)
        self.assertFalse(artifact["selectionAuthorized"])
        self.assertFalse(artifact["renderingAuthorized"])


if __name__ == "__main__":
    unittest.main()
