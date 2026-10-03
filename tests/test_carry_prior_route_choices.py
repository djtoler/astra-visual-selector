import copy
import unittest

from pipeline import carry_prior_route_choices as subject


class CarryPriorRouteChoicesTests(unittest.TestCase):
    def test_carries_all_prior_choices_without_render_authorization(self):
        artifact = subject.build()
        self.assertEqual(subject.validate(artifact), {
            "templateReviewTasks": 32, "carriedPriorChoices": 32, "unresolved": 0,
        })
        self.assertFalse(artifact["renderingAuthorized"])
        self.assertTrue(artifact["selectionAuthorizedForRecordedTasks"])

    def test_uses_first_surviving_prior_choice_in_preserved_order(self):
        artifact = subject.build()
        self.assertEqual(artifact["decisions"]["05-05a.main"]["candidateId"], "truth-population-field")
        self.assertEqual(artifact["decisions"]["16-16.main"]["candidateId"],
                         "archive3-carousel-photo-logo-reveal-2026-09-13-12-24-28-utc--review-v2-001")

    def test_validation_rejects_substituted_choice(self):
        artifact = subject.build()
        artifact = copy.deepcopy(artifact)
        artifact["decisions"]["03-03.opening_chart"]["candidateId"] = "made-up"
        with self.assertRaisesRegex(ValueError, "first surviving prior"):
            subject.validate(artifact)


if __name__ == "__main__":
    unittest.main()
