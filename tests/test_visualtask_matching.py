import copy
import json
import unittest
from pathlib import Path

from pipeline import visualtask_matching as subject


ROOT = Path(__file__).resolve().parents[1]


class VisualTaskMatching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = subject.build(source_beat="28-28")
        cls.by_id = {row["taskId"]: row for row in cls.artifact["tasks"]}

    def test_split_tasks_receive_independent_template_slates(self):
        setup = self.by_id["28-28.setup"]
        overlap = self.by_id["28-28.overlap"]
        self.assertEqual(setup["matchingJob"], "define_terms")
        self.assertEqual(overlap["matchingJob"], "intersection_of_sets")
        self.assertNotEqual(
            [row["candidateId"] for row in setup["templateCandidates"]],
            [row["candidateId"] for row in overlap["templateCandidates"]],
        )

    def test_split_tasks_receive_independent_media_results(self):
        self.assertEqual(self.by_id["28-28.setup"]["mediaCandidates"]["status"], "no_entity_media_demand")
        self.assertEqual(len(self.by_id["28-28.overlap"]["mediaCandidates"]["entities"]), 10)
        self.assertTrue(self.by_id["28-28.overlap"]["mediaCandidates"]["individualCandidateIds"])

    def test_every_candidate_has_task_level_provenance(self):
        for task in self.artifact["tasks"]:
            for candidate in task["templateCandidates"]:
                provenance = candidate["candidateMatchingProvenance"]
                self.assertEqual(provenance["scope"], "visual_task")
                self.assertEqual(provenance["taskId"], task["taskId"])

    def test_missing_task_provenance_fails_closed(self):
        broken = copy.deepcopy(self.artifact)
        del broken["tasks"][0]["templateCandidates"][0]["candidateMatchingProvenance"]
        with self.assertRaisesRegex(ValueError, "lacks VisualTask provenance"):
            subject.validate(broken, verify_sources=False)

    def test_written_artifact_replays(self):
        # Explicit editor-authorized migration; historical report stays immutable.
        from tests.astra_fixture_replay import replay
        replay()

    def test_versioned_fixture_rejects_inventory_and_input_mutations(self):
        from tests.astra_fixture_replay import DIRECTORY, replay
        manifest = json.loads((DIRECTORY / "manifest.json").read_text())
        for field in ("inventory", "boundRevisionFiles"):
            altered = copy.deepcopy(manifest)
            row = altered[field][0] if isinstance(altered[field], list) else altered[field]
            row["sha256"] = "0" * 64
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "digest"):
                replay(altered)

    def test_generic_legacy_binding_cannot_admit_incompatible_data_template(self):
        pool = {row["id"]: row for row in subject.C.load()}
        task = {
            "id": "new-story.statement", "job": "assert_without_data", "taskRole": "main",
            "quote": "The artist remains deeply misunderstood.", "entityCount": 1,
            "entities": {"displayEligible": ["artist"]}, "mustBePerceptible": [],
            "presentationOperations": ["concept_statement"], "templateAdmissions": [],
            "ignorePriorSelections": True, "candidateDisplayLimit": 50,
        }
        rows = subject.template_candidates(
            task, {"assert_without_data": [{"id": "3d-pie-chart-set--scene-003"}]},
            pool, exhaustive_families=True,
        )
        self.assertNotIn("3d-pie-chart-set--scene-003", {row["candidateId"] for row in rows})

    def test_subject_profile_uses_identity_capability_not_generic_documentary_word(self):
        pool = {row["id"]: row for row in subject.C.load()}
        task = {
            "id": "new-story.profile", "job": "introduce", "taskRole": "main",
            "quote": "Who is the artist?", "entityCount": 1,
            "entities": {"displayEligible": ["artist"]}, "mustBePerceptible": [],
            "presentationOperations": ["subject_profile"], "templateAdmissions": [],
            "ignorePriorSelections": True, "candidateDisplayLimit": 500,
        }
        rows = subject.template_candidates(task, {}, pool, exhaustive_families=True)
        ids = {row["candidateId"] for row in rows}
        self.assertIn("03-history-documentary-10-slides--scene-001", ids)
        self.assertNotIn("3d-pie-chart-set--scene-003", ids)
        self.assertTrue(all(
            row["bindingProvenance"]["source"] == "structured-presentation-contract"
            for row in rows
        ))

    def test_task_scoped_editor_admission_survives_family_diversification(self):
        pool = {row["id"]: row for row in subject.C.load()}
        task = {
            "id": "new-story.admission", "job": "assert_without_data", "taskRole": "main",
            "quote": "A statement.", "entityCount": 1,
            "entities": {"displayEligible": ["artist"]}, "mustBePerceptible": [],
            "presentationOperations": ["concept_statement"],
            "templateAdmissions": [{"id": "03-history-documentary-10-slides--scene-001", "source": "user"}],
            "ignorePriorSelections": True, "candidateDisplayLimit": 16,
        }
        rows = subject.template_candidates(task, {}, pool)
        self.assertIn("03-history-documentary-10-slides--scene-001", {row["candidateId"] for row in rows})

    def test_primary_operation_prevents_secondary_union_from_admitting_data_templates(self):
        pool = {row["id"]: row for row in subject.C.load(content_class="*")}
        task = {
            "id": "new-story.relationship", "job": "enumerate", "taskRole": "main",
            "quote": "The artist met his cousin at age 17.", "entityCount": 2,
            "entities": {"displayEligible": ["artist", "cousin"]}, "mustBePerceptible": [],
            "presentationOperations": ["relationship_intro", "data_explanation"],
            "primaryPresentationOperation": "relationship_intro", "templateAdmissions": [],
            "ignorePriorSelections": True, "candidateDisplayLimit": 500,
        }
        ids = {row["candidateId"] for row in subject.template_candidates(
            task, {}, pool, exhaustive_families=True)}
        self.assertNotIn("3d-pie-chart-set--scene-003", ids)
        self.assertNotIn("58_big_three_stat_rows", ids)
        self.assertIn("photo-slideshow-memories-envato--scene-001", ids)

    def test_scoped_lyrics_are_admitted_only_for_lyric_operation(self):
        pool = {row["id"]: row for row in subject.C.load(content_class="*")}
        base = {
            "id": "new-story.lyrics", "job": "present_evidence", "taskRole": "main",
            "quote": "The hook says the exact lyric.", "entityCount": 1,
            "entities": {"displayEligible": ["artist"]}, "mustBePerceptible": [],
            "templateAdmissions": [], "ignorePriorSelections": True,
            "candidateDisplayLimit": 500,
        }
        lyric_task = {**base, "presentationOperations": ["lyric_presentation"],
                      "primaryPresentationOperation": "lyric_presentation"}
        lyric_ids = {row["candidateId"] for row in subject.template_candidates(
            lyric_task, {}, pool, exhaustive_families=True)}
        self.assertIn("archive3-horizontal-music-players-with-lyric-vol-2--review-001", lyric_ids)
        statement_task = {**base, "id": "new-story.statement",
                          "presentationOperations": ["concept_statement"],
                          "primaryPresentationOperation": "concept_statement"}
        statement_ids = {row["candidateId"] for row in subject.template_candidates(
            statement_task, {}, pool, exhaustive_families=True)}
        self.assertFalse(lyric_ids & {candidate for candidate in statement_ids if "lyric" in candidate})

    def test_scoped_timelines_are_admitted_only_for_archival_progression(self):
        pool = {row["id"]: row for row in subject.C.load(content_class="*")}
        timeline_ids = {row["id"] for row in pool.values() if row.get("scope") == "timelines"}
        self.assertTrue(timeline_ids)
        base = {
            "job": "narrate_an_event", "taskRole": "main", "entityCount": 1,
            "entities": {"displayEligible": ["artist"]}, "mustBePerceptible": [],
            "templateAdmissions": [], "ignorePriorSelections": True,
            "candidateDisplayLimit": 500,
        }
        archival = {**base, "id": "new-story.archival", "quote": "Across the years.",
                    "presentationOperations": ["archival_progression"],
                    "primaryPresentationOperation": "archival_progression"}
        archival_ids = {row["candidateId"] for row in subject.template_candidates(
            archival, {}, pool, exhaustive_families=True)}
        self.assertTrue(archival_ids & timeline_ids)
        statement = {**base, "id": "new-story.statement", "quote": "A general claim.",
                     "presentationOperations": ["concept_statement"],
                     "primaryPresentationOperation": "concept_statement"}
        statement_ids = {row["candidateId"] for row in subject.template_candidates(
            statement, {}, pool, exhaustive_families=True)}
        self.assertFalse(statement_ids & timeline_ids)

    def test_explicit_non_template_route_returns_no_template_candidates(self):
        pool = {row["id"]: row for row in subject.C.load(content_class="*")}
        task = {
            "id": "new-story.question", "job": "pose_a_question", "taskRole": "main",
            "quote": "How could this happen?", "entityCount": 0,
            "entities": {"displayEligible": []}, "mustBePerceptible": [],
            "presentationOperations": ["rhetorical_question"],
            "primaryPresentationOperation": "rhetorical_question",
            "routeDisposition": {
                "templateEligible": False,
                "decisionEvidence": {
                    "authority": "human_editor", "scope": "exact_task",
                    "taskId": "new-story.question", "decision": "no_template",
                    "reviewState": "editor_reviewed",
                },
            },
        }
        self.assertEqual(subject.template_candidates(task, {}, pool), [])

    def test_unreviewed_non_template_route_fails_instead_of_hiding_candidates(self):
        pool = {row["id"]: row for row in subject.C.load(content_class="*")}
        task = {
            "id": "new-story.unreviewed-veto", "job": "pose_a_question",
            "taskRole": "main", "quote": "How could this happen?",
            "entityCount": 0, "entities": {"displayEligible": []},
            "mustBePerceptible": [], "presentationOperations": ["rhetorical_question"],
            "primaryPresentationOperation": "rhetorical_question",
            "routeDisposition": {"templateEligible": False},
        }
        with self.assertRaisesRegex(
                ValueError, "task-scoped editor-reviewed no-template evidence"):
            subject.template_candidates(task, {}, pool)

    def test_non_template_evidence_cannot_leak_from_another_task(self):
        task = {
            "id": "new-story.target",
            "routeDisposition": {
                "templateEligible": False,
                "decisionEvidence": {
                    "authority": "human_editor", "scope": "exact_task",
                    "taskId": "old-story.source", "decision": "no_template",
                    "reviewState": "editor_reviewed",
                },
            },
        }
        with self.assertRaisesRegex(ValueError, "task-scoped editor-reviewed"):
            subject._validate_route_disposition(task)

    def test_unreviewed_mixed_payload_fails_before_primary_only_admission(self):
        task = {
            "id": "new-story.mixed", "job": "assert_without_data",
            "presentationOperations": ["subject_profile", "data_explanation"],
            "primaryPresentationOperation": "subject_profile",
            "routeDisposition": {"templateEligible": True, "mixedPayloadReviewRequired": True},
        }
        with self.assertRaisesRegex(ValueError, "mixed payload requires task-scoped"):
            subject._validate_mixed_payload_disposition(task)

    def test_exact_mixed_payload_review_can_confirm_primary_operation(self):
        task = {
            "id": "new-story.mixed", "job": "assert_without_data",
            "presentationOperations": ["subject_profile", "data_explanation"],
            "primaryPresentationOperation": "subject_profile",
            "routeDisposition": {
                "templateEligible": True, "mixedPayloadReviewRequired": True,
                "mixedPayloadDecisionEvidence": {
                    "authority": "human_editor", "scope": "exact_task",
                    "taskId": "new-story.mixed", "reviewState": "editor_reviewed",
                    "decision": "primary_operation_confirmed",
                },
            },
        }
        subject._validate_mixed_payload_disposition(task)

    def test_mixed_payload_review_cannot_leak_from_another_task(self):
        task = {
            "id": "new-story.target",
            "routeDisposition": {
                "mixedPayloadReviewRequired": True,
                "mixedPayloadDecisionEvidence": {
                    "authority": "human_editor", "scope": "exact_task",
                    "taskId": "old-story.source", "reviewState": "editor_reviewed",
                    "decision": "split_complete",
                },
            },
        }
        with self.assertRaisesRegex(ValueError, "mixed payload requires task-scoped"):
            subject._validate_mixed_payload_disposition(task)

    def test_identity_transformation_rejects_quantitative_change_templates(self):
        pool = {row["id"]: row for row in subject.C.load(content_class="*")}
        task = {
            "id": "new-story.transformation", "job": "assert_without_data", "taskRole": "main",
            "quote": "Before we understand the star, meet his former self.", "entityCount": 1,
            "entities": {"displayEligible": ["artist"]}, "mustBePerceptible": [],
            "presentationOperations": ["transformation"],
            "primaryPresentationOperation": "transformation",
        }
        ids = {row["candidateId"] for row in subject.template_candidates(
            task, {}, pool, exhaustive_families=True)}
        self.assertNotIn("truth-cohort-attrition", ids)
        self.assertNotIn("26_mirrored_stat_compare", ids)

    def test_identity_profile_relationship_and_event_routes_reject_data_only_templates(self):
        pool = {row["id"]: row for row in subject.C.load(content_class="*")}
        base = {
            "job": "assert_without_data", "taskRole": "main",
            "entities": {"displayEligible": ["artist", "collaborator"]},
            "mustBePerceptible": [], "ignorePriorSelections": True,
            "candidateDisplayLimit": 500,
        }
        cases = (
            ("subject_profile", 1, "Meet the artist."),
            ("relationship_intro", 2, "The artist worked with a collaborator."),
            ("event_narration", 1, "The artist recorded the album."),
        )
        for operation, entity_count, quote in cases:
            task = {**base, "id": f"new-story.{operation}", "quote": quote,
                    "entityCount": entity_count,
                    "presentationOperations": [operation],
                    "primaryPresentationOperation": operation}
            ids = {row["candidateId"] for row in subject.template_candidates(
                task, {}, pool, exhaustive_families=True)}
            with self.subTest(operation=operation):
                self.assertTrue(ids)
                self.assertNotIn("3d-pie-chart-set--scene-003", ids)
                self.assertNotIn("truth-cohort-attrition", ids)


if __name__ == "__main__":
    unittest.main()
