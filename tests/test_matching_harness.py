import copy
import json
import unittest

from pipeline import matching_harness as subject


class MatchingHarnessTests(unittest.TestCase):
    def test_contract_rejects_missing_or_reordered_stage(self):
        contract = subject.read(subject.DEFAULT_CONTRACT)
        broken = copy.deepcopy(contract)
        broken["stages"].pop(2)
        with self.assertRaisesRegex(ValueError, "missing or reordered"):
            subject.validate_contract(broken)

    def test_fixture_audit_exposes_current_first_blocker(self):
        audit = subject.build()
        self.assertEqual(audit["firstBlockingStage"], "general_matching_contract")
        self.assertFalse(audit["productionAllowed"])
        self.assertFalse(audit["selectionAuthorized"])

    def test_generality_is_the_first_required_stage(self):
        contract = subject.read(subject.DEFAULT_CONTRACT)
        self.assertEqual(contract["stages"][0]["id"], "general_matching_contract")
        audit = subject.build()
        self.assertEqual(audit["stageResults"][0]["id"], "general_matching_contract")
        self.assertEqual(audit["stageResults"][0]["status"], "blocked")
        self.assertIn("general_matching_objective_tasks_incomplete", {
            row["kind"] for row in audit["stageResults"][0]["gaps"]
        })

    def test_general_matching_receipt_uses_distinct_packages_and_neutral_runtime(self):
        audit = subject.build()
        general = audit["generalMatchingLayer"]
        self.assertEqual(general["productBoundary"], "any_validated_supported_storypackage")
        self.assertGreaterEqual(general["distinctPackages"], 4)
        self.assertGreaterEqual(general["regressionPackages"], 2)
        self.assertEqual(general["userSuppliedHeldOutPackages"], 1)
        self.assertEqual(general["runtimeSourceViolations"], [])
        self.assertTrue(all(row["uncoveredClaims"] == 0 for row in general["packages"]))
        self.assertTrue(general["structuredCapabilityAdmissionRequired"])
        self.assertFalse(general["legacyJobBindingCanAdmit"])
        self.assertFalse(general["selectionAuthorized"])
        self.assertFalse(general["renderingAuthorized"])

    def test_general_contract_rejects_story_specific_runtime_behavior(self):
        contract = subject.read(subject.DEFAULT_GENERAL_CONTRACT)
        broken = copy.deepcopy(contract)
        broken["runtime"]["priorStoryDecisionsCanAdmitCandidates"] = True
        with self.assertRaisesRegex(ValueError, "story-specific runtime behavior"):
            subject.validate_general_contract(broken)

    def test_story_data_media_and_sequence_are_separate_stages(self):
        audit = subject.build()
        states = {row["id"]: row for row in audit["stageResults"]}
        self.assertEqual(states["story_handoff"]["status"], "passed")
        self.assertIn("untasked_span", {gap["kind"] for gap in states["story_handoff"]["gaps"]})
        self.assertIn("focal_unknown", {gap["kind"] for gap in states["story_handoff"]["gaps"]})
        self.assertNotIn("missing_claim_links", {gap["kind"] for gap in states["story_handoff"]["gaps"]})
        gap = next(gap for gap in states["story_handoff"]["gaps"] if gap["kind"] == "focal_unknown")
        self.assertFalse(gap["blocking"])
        self.assertEqual(gap["deferredTo"], "template_media_feasibility")
        self.assertEqual(states["data_handoff"]["status"], "passed")
        self.assertEqual(states["data_handoff"]["gaps"], [])
        self.assertEqual(states["template_media_feasibility"]["status"], "passed")
        self.assertIn("preferred_media_unresolved_broll_fallback_available", {gap["kind"] for gap in states["template_media_feasibility"]["gaps"]})
        self.assertEqual(states["sequence_planning"]["status"], "passed")
        self.assertEqual(states["sequence_planning"]["gaps"], [])
        self.assertEqual(states["human_review"]["status"], "passed")
        self.assertEqual(states["human_review"]["gaps"], [])

    def test_production_cannot_pass_with_incomplete_receipts(self):
        audit = subject.build(mode="production")
        self.assertFalse(audit["productionAllowed"])
        self.assertEqual(audit["firstBlockingStage"], "general_matching_contract")

    def test_stale_source_fails_closed(self):
        audit = subject.build()
        audit["sources"]["contract"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "missing or stale"):
            subject.validate(audit)

    def test_storypackage_execution_plan_is_attached(self):
        audit = subject.build()
        self.assertEqual(audit["executionPlan"]["planId"], "general-storypackage-matching-layer")
        self.assertEqual(audit["executionPlan"]["nextTaskId"], "GML-14")
        self.assertEqual(audit["executionPlan"]["nextTaskOwner"], "matching")
        self.assertFalse(audit["executionPlan"]["continuationRequired"])
        self.assertTrue(audit["executionPlan"]["stopAllowed"])
        self.assertTrue(audit["executionPlan"]["userInputRequired"])
        self.assertEqual(audit["executionPlan"]["currentBlocker"]["party"], "you")
        self.assertIn("executionPlan", audit["sources"])

    def test_continuation_receipt_prevents_silent_stopping(self):
        audit = subject.build()
        self.assertTrue(audit["continuation"]["taskListReconciled"])
        self.assertTrue(audit["continuation"]["objectiveReconciled"])
        self.assertFalse(audit["continuation"]["continuationRequired"])
        self.assertTrue(audit["continuation"]["stopAllowed"])
        self.assertTrue(audit["continuation"]["userInputRequired"])
        self.assertEqual(audit["continuation"]["nextTaskId"], "GML-14")
        self.assertEqual(audit["continuation"]["currentBlocker"]["party"], "you")
        broken = copy.deepcopy(audit)
        broken["continuation"]["continuationRequired"] = True
        with self.assertRaisesRegex(ValueError, "continuation receipt is inconsistent"):
            subject.validate(broken, verify_sources=False)

    def test_incomplete_objective_without_user_input_requires_continuation(self):
        plan = subject.read(subject.DEFAULT_EXECUTION_PLAN)
        pending = copy.deepcopy(plan)
        pending["tasks"] = pending["tasks"][:14]
        pending["tasks"][-1]["status"] = "pending"
        pending["tasks"][-1]["userInputRequired"] = False
        summary = subject.execution_plan_summary(pending)
        self.assertTrue(summary["continuationRequired"])
        self.assertEqual(summary["currentBlocker"]["party"], "matching")
        self.assertFalse(summary["stopAllowed"])
        self.assertEqual(summary["nextTaskId"], "GML-14")

    def test_ready_system_work_prevents_an_unrelated_user_review_from_stopping_execution(self):
        plan = subject.read(subject.DEFAULT_EXECUTION_PLAN)
        active = copy.deepcopy(plan)
        active["tasks"][-2]["status"] = "pending"
        active["tasks"][-2]["receipt"] = None
        active["tasks"][-1]["status"] = "pending"
        active["tasks"][-1]["receipt"] = None
        summary = subject.execution_plan_summary(active)
        self.assertIn("GML-14", summary["readyTaskIds"])
        self.assertIn("GML-15", summary["readyNonUserTaskIds"])
        self.assertFalse(summary["userInputRequired"])
        self.assertTrue(summary["continuationRequired"])
        self.assertEqual(summary["currentBlocker"]["party"], "story")

    def test_only_ready_user_work_reports_you_as_the_current_blocker(self):
        plan = subject.read(subject.DEFAULT_EXECUTION_PLAN)
        waiting = copy.deepcopy(plan)
        waiting["tasks"] = waiting["tasks"][:14]
        summary = subject.execution_plan_summary(waiting)
        self.assertTrue(summary["userInputRequired"])
        self.assertEqual(summary["currentBlocker"]["party"], "you")
        self.assertTrue(summary["currentBlocker"]["userActionRequired"])

    def test_execution_plan_rejects_routine_task_stopping(self):
        plan = subject.read(subject.DEFAULT_EXECUTION_PLAN)
        broken = copy.deepcopy(plan)
        broken["executionPolicy"]["routineTaskCompletionAllowsStop"] = True
        with self.assertRaisesRegex(ValueError, "routine task"):
            subject.execution_plan_summary(broken)

    def test_complete_storypackage_receipts_cover_every_current_review_key(self):
        audit = subject.build()
        self.assertEqual(audit["storyHandoff"]["packageId"], "year-seventeen@7")
        self.assertEqual(audit["storyHandoff"]["requiredReviewKeys"], 40)
        self.assertEqual(audit["storyHandoff"]["coveredReviewKeys"], 40)
        self.assertEqual(audit["storyHandoff"]["uncoveredClaims"], 0)
        self.assertEqual(audit["storyHandoff"]["matchingHandoffTasks"], 41)
        self.assertEqual(audit["storyHandoff"]["matchingHandoffUnresolved"], 3)
        self.assertIn("storyPackageAdapter", audit["sources"])
        self.assertIn("storyTaskProposals", audit["sources"])
        self.assertIn("storyMatchingHandoff", audit["sources"])

    def test_data_handoff_queue_is_attached_and_limited_to_data_tasks(self):
        audit = subject.build()
        self.assertEqual(audit["dataHandoff"]["assignments"], 28)
        self.assertEqual(audit["dataHandoff"]["awaitingDataLayer"], 0)
        self.assertGreater(audit["dataHandoff"]["resolved"], 0)
        self.assertGreater(audit["dataHandoff"]["typedFields"], 0)
        self.assertEqual(audit["dataHandoff"]["typedGaps"], 0)
        self.assertTrue(audit["dataHandoff"]["complete"])
        self.assertIn("dataHandoffQueue", audit["sources"])
        self.assertIn("dataAssignments", audit["sources"])

    def test_full_batch_matching_is_attached_without_authorizing_selection(self):
        audit = subject.build()
        batch = audit["templateMediaFeasibility"]
        self.assertEqual(batch["visualTasks"], 41)
        self.assertEqual(batch["templateVerdicts"], {"conditional": 40, "incompatible": 1})
        self.assertEqual(batch["mediaVerdicts"], {"available": 7, "conditional": 1, "not_required": 30, "unavailable": 3})
        self.assertEqual(batch["candidateVerdicts"], {"conditional": 542, "incompatible": 70, "unresolved": 13})
        self.assertEqual(batch["mediaTasksNeedingResolution"], 4)
        self.assertFalse(batch["beatTemplateRequired"])
        self.assertTrue(batch["brollFallbackAlwaysAllowed"])
        self.assertEqual(batch["minimumTemplateChoiceCount"], 0)
        self.assertFalse(batch["emptyTemplateChoiceSetsBlocking"])
        self.assertEqual(batch["preferredMediaGapsBlocking"], 0)
        self.assertFalse(batch["selectionAuthorized"])
        self.assertFalse(batch["renderingAuthorized"])
        self.assertIn("fullVisualTaskBatchMatching", audit["sources"])

    def test_ordered_route_plan_completes_sequence_without_selecting(self):
        audit = subject.build()
        sequence = audit["sequencePlanning"]
        self.assertTrue(sequence["complete"])
        self.assertEqual(sequence["scenes"], 41)
        self.assertEqual(sequence["brollRoutes"] + sequence["templateReviewRoutes"] + sequence["deferredRoutes"], 41)
        self.assertEqual(sequence["postBeatBrollSegments"], 1)
        self.assertEqual(sequence["transitionsRequired"], 41)
        self.assertEqual(sequence["sequenceConflicts"], 0)
        self.assertFalse(sequence["selectionAuthorized"])
        self.assertFalse(sequence["renderingAuthorized"])
        self.assertIn("orderedVisualRoutePlan", audit["sources"])

    def test_prior_editor_choices_complete_human_review_without_rerender_authority(self):
        audit = subject.build()
        review = audit["humanReview"]
        self.assertTrue(review["complete"])
        self.assertEqual(review["templateReviewTasks"], 32)
        self.assertEqual(review["decisions"], 32)
        self.assertEqual(review["carriedPriorChoices"], 32)
        self.assertEqual(review["unresolved"], 0)
        self.assertFalse(review["renderingAuthorized"])
        self.assertIn("orderedVisualRouteDecisions", audit["sources"])

    def test_render_release_stage_reports_concrete_receipt_gaps(self):
        audit = subject.build()
        release = audit["renderRelease"]
        self.assertEqual(release["scenes"], 41)
        self.assertEqual(release["blocked"], 41)
        self.assertFalse(release["renderingAuthorized"])
        stage = next(row for row in audit["stageResults"] if row["id"] == "render_release_handoff")
        self.assertEqual(stage["status"], "blocked")
        self.assertEqual(stage["gaps"][0]["kind"], "render_release_receipts_incomplete")
        self.assertIn("renderReleasePreparation", audit["sources"])


if __name__ == "__main__":
    unittest.main()
