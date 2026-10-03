import copy
import unittest

from pipeline import ordered_visual_route_plan as subject


class OrderedVisualRoutePlanTests(unittest.TestCase):
    def test_builds_complete_ordered_plan_without_selecting(self):
        artifact = subject.build()
        counts = subject.validate(artifact, verify_sources=False)
        self.assertEqual(counts["scenes"], 41)
        self.assertEqual(counts["transitionsRequired"], 41)
        self.assertEqual(counts["sequenceConflicts"], 0)
        self.assertFalse(artifact["selectionAuthorized"])
        self.assertFalse(artifact["renderingAuthorized"])

    def test_every_template_route_has_nonempty_distinct_choices_and_preserves_prior_selection(self):
        artifact = subject.build()
        routes = [row for row in artifact["scenes"] if row["route"] == "template_review"]
        self.assertGreater(len(routes), 0)
        for row in routes:
            self.assertGreaterEqual(len(row["templateChoices"]), 1)
            self.assertLessEqual(len(row["templateChoices"]), subject.MAX_REVIEW_CHOICES)
            self.assertEqual(len(row["templateChoices"]), len({choice["candidateId"] for choice in row["templateChoices"]}))
            self.assertTrue(any(choice["priorEditorSelected"] for choice in row["templateChoices"]))

    def test_current_editorial_broll_corrections_override_older_flags(self):
        scenes = {row["taskId"]: row for row in subject.build()["scenes"]}
        self.assertEqual(scenes["01-01.subject"]["route"], "template_review")
        self.assertEqual(scenes["02-02b.currensy_catalog"]["route"], "template_review")
        self.assertEqual(scenes["05-05b.main"]["route"], "broll")
        self.assertEqual(scenes["15-15.main"]["postBeatBroll"]["placement"], "after_beat")
        self.assertEqual(scenes["18-18.main"]["routeReason"],
                         "current_editor_template_route")
        self.assertEqual(scenes["25-25a.main"]["route"], "template_review")
        self.assertEqual(scenes["28-28.overlap"]["route"], "template_review")
        self.assertEqual(scenes["30-30b.main"]["routeReason"], "current_editor_broll_ruling")

    def test_broll_route_never_carries_template_choice(self):
        for row in subject.build()["scenes"]:
            if row["route"] == "broll":
                self.assertEqual(row["templateChoices"], [])

    def test_retired_local_family_is_absent_and_next_prior_choices_survive(self):
        artifact = subject.build()
        choices = {
            row["taskId"]: [choice["candidateId"] for choice in row.get("templateChoices") or []]
            for row in artifact["scenes"]
        }
        self.assertFalse(any(
            candidate.startswith("3dz-charts--")
            for candidates in choices.values() for candidate in candidates
        ))
        self.assertEqual(choices["12-12a.main"][0], "truth-rank-fall")
        self.assertEqual(choices["25-25a.main"][0], "24_dense_vertical_bars")

    def test_validation_rejects_empty_template_slate(self):
        artifact = subject.build()
        row = next(row for row in artifact["scenes"] if row["route"] == "template_review")
        row["templateChoices"] = []
        with self.assertRaisesRegex(ValueError, "one or more distinct choices"):
            subject.validate(artifact, verify_sources=False)


if __name__ == "__main__":
    unittest.main()
