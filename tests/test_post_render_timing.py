import unittest

from pipeline.post_render_timing import (
    DEFAULT_CATALOG,
    DEFAULT_COMPARISON,
    DEFAULT_MAPPINGS,
    DEFAULT_REVIEW_CATALOG,
    DEFAULT_TECHNICAL_INDEX,
    DEFAULT_WINDOWS,
    add_selected_route_plans,
    build_reviewed_contract_intake,
    calculate_plan,
    read,
)


def scene(duration=8.0, *, retime=True, boundary=True, added=False):
    return {"selectionContract": {
        "nativeDurationSeconds": duration,
        "retimeAllowed": retime,
        "transitionBoundaryVerified": boundary,
        "needsAddedTransition": added,
    }}


class PostRenderTimingTests(unittest.TestCase):
    def test_speed_up_matches_narration(self):
        plan = calculate_plan(scene(), 4.0)
        self.assertEqual(plan["direction"], "speed_up")
        self.assertEqual(plan["playbackRate"], 2.0)
        self.assertEqual(plan["calculatedOutputDurationSeconds"], 4.0)

    def test_slow_down_matches_narration(self):
        plan = calculate_plan(scene(), 16.0)
        self.assertEqual(plan["direction"], "slow_down")
        self.assertEqual(plan["playbackRate"], 0.5)

    def test_native_duration_is_unchanged(self):
        self.assertEqual(calculate_plan(scene(), 8.0)["direction"], "unchanged")

    def test_added_transition_is_preserved(self):
        self.assertEqual(calculate_plan(scene(added=True), 4.0)["endingTreatment"], "add_transition")

    def test_unknown_boundary_is_unresolved(self):
        self.assertEqual(calculate_plan(scene(boundary=False), 4.0)["status"], "unresolved_transition_boundary")

    def test_unapproved_retime_is_unresolved(self):
        self.assertEqual(calculate_plan(scene(retime=False), 4.0)["status"], "unresolved_post_retime_not_approved")

    def test_missing_contract_is_unresolved(self):
        self.assertEqual(calculate_plan({}, 4.0)["status"], "unresolved_missing_approved_native_duration")

    def test_arithmetic_never_claims_selection_or_rendering(self):
        plan = calculate_plan(scene(), 4.0)
        self.assertFalse(plan["selectionAuthorized"])
        self.assertFalse(plan["renderingAuthorized"])
        self.assertIn("editorial_pacing_review_required", plan["status"])

    def test_selected_routes_receive_source_appropriate_timing_dispositions(self):
        report = {"plans": [], "counts": {}}
        route_plan = {"scenes": [
            {"taskId": "static", "route": "template_review",
             "narrationSpan": {"durationSeconds": 4.0}},
            {"taskId": "cinematic", "route": "template_review",
             "narrationSpan": {"durationSeconds": 5.0}},
            {"taskId": "local", "route": "template_review",
             "narrationSpan": {"durationSeconds": 6.0}},
        ]}
        decisions = {"decisions": {
            "static": {"route": "template", "candidateId": "static-id"},
            "cinematic": {"route": "template", "candidateId": "cinematic-id"},
            "local": {"route": "template", "candidateId": "local-id"},
        }}
        catalog = {
            "afterEffects": [],
            "infographics": [{"template_id": "static-id"}],
            "cinematic3d": [{"layout_id": "cinematic-id", "native_duration_seconds": 10.0}],
            "layeredScenes": [],
        }
        result = add_selected_route_plans(
            report, route_plan, decisions, catalog,
            {"records": [{"id": "local-id"}]},
        )
        by_task = {row["taskId"]: row["plan"] for row in result["plans"]}
        self.assertEqual(by_task["static"]["status"], "structurally_feasible_static_hold")
        self.assertEqual(by_task["static"]["calculatedOutputDurationSeconds"], 4.0)
        self.assertEqual(by_task["cinematic"]["nativeSceneDurationSeconds"], 10.0)
        self.assertEqual(by_task["cinematic"]["endingTreatment"], "add_transition")
        self.assertEqual(by_task["local"]["status"],
                         "unresolved_missing_approved_native_duration")
        self.assertFalse(any(row["plan"]["renderingAuthorized"] for row in result["plans"]))


def intake_fixture(*, mapping_status="verified", observed=8.0, project_hash="abc"):
    review = {"scenes": [{
        "id": "review-001",
        "sourceId": "family",
        "sourceSha256": "preview-hash",
        "availabilityStatus": "available_for_use",
        "boundaryReview": {"status": "usable_scene"},
        "transitionReviewNeeded": False,
        "needsTransition": True,
    }]}
    mappings = {"mappings": [{
        "sceneId": "review-001",
        "projectId": "project",
        "status": mapping_status,
        "compositionId": 7,
        "compositionPath": "Final/Scene",
    }]}
    windows = {"windows": [{
        "sceneId": "review-001",
        "projectId": "project",
        "compositionId": 7,
        "compositionPath": "Final/Scene",
        "startSeconds": 2.0,
        "endSeconds": 5.0,
    }]}
    index = {"projects": [{
        "id": "project",
        "sourceUnchanged": True,
        "sourceProjectName": "Project.aep",
        "sourceProjectSha256": project_hash,
        "compositions": [{"id": 7, "path": "Final/Scene", "durationSeconds": 8.0}],
    }]}
    return ({"review-001": {observed}}, set(), review, mappings, windows, index)


class ReviewedNativeDurationContractIntakeTests(unittest.TestCase):
    def test_verified_composition_uses_measured_native_duration(self):
        result = build_reviewed_contract_intake(*intake_fixture())
        self.assertEqual(result["counts"], {"targetUniqueScenes": 1, "resolved": 1, "unresolved": 0})
        row = result["rows"][0]
        self.assertEqual(row["contract"]["nativeDurationSeconds"], 8.0)
        self.assertEqual(row["evidence"]["duration"]["kind"], "verified_native_composition")
        self.assertTrue(row["contract"]["needsAddedTransition"])
        self.assertFalse(row["contract"]["selectionAuthorized"])

    def test_verified_window_uses_exact_window_duration(self):
        result = build_reviewed_contract_intake(*intake_fixture(mapping_status="verified_window", observed=3.0))
        row = result["rows"][0]
        self.assertEqual(row["contract"]["nativeDurationSeconds"], 3.0)
        self.assertEqual(row["evidence"]["duration"]["kind"], "verified_native_window")

    def test_unverified_mapping_remains_unresolved(self):
        args = list(intake_fixture())
        args[3]["mappings"][0]["status"] = "unreviewed"
        result = build_reviewed_contract_intake(*args)
        self.assertEqual(result["counts"]["unresolved"], 1)
        self.assertIn("native_mapping_not_verified", result["rows"][0]["reasons"])

    def test_conflicting_saved_duration_remains_unresolved(self):
        result = build_reviewed_contract_intake(*intake_fixture(observed=7.5))
        self.assertEqual(result["counts"]["unresolved"], 1)
        self.assertIn("comparison_native_duration_mismatch", result["rows"][0]["reasons"])

    def test_missing_source_hash_remains_unresolved(self):
        result = build_reviewed_contract_intake(*intake_fixture(project_hash=""))
        self.assertEqual(result["counts"]["unresolved"], 1)
        self.assertIn("technical_project_not_source_bound", result["rows"][0]["reasons"])

    def test_current_75_placement_gaps_resolve_39_and_flag_one_unreviewed_scene(self):
        catalog = read(DEFAULT_CATALOG)
        comparison = read(DEFAULT_COMPARISON)
        approved = {
            scene["id"]
            for template in catalog["afterEffects"]
            for scene in template["scenes"]
        }
        observations = {}
        missing_placements = 0
        for task in comparison["tasks"]:
            for candidate in task.get("candidateComparisons", []):
                timing = candidate.get("timingObservation")
                if timing and candidate["candidateId"] not in approved:
                    missing_placements += 1
                    observations.setdefault(candidate["candidateId"], set()).add(
                        float(timing["nativeCompositionDurationSeconds"])
                    )
        result = build_reviewed_contract_intake(
            observations,
            approved,
            read(DEFAULT_REVIEW_CATALOG),
            read(DEFAULT_MAPPINGS),
            read(DEFAULT_WINDOWS),
            read(DEFAULT_TECHNICAL_INDEX),
        )
        self.assertEqual(missing_placements, 75)
        self.assertEqual(result["counts"], {"targetUniqueScenes": 40, "resolved": 39, "unresolved": 1})
        unresolved = [row for row in result["rows"] if row["status"] == "unresolved"]
        self.assertEqual(unresolved, [{
            "sceneId": "circle-list-infographic--scene-001",
            "status": "unresolved",
            "reasons": ["missing_review_scene"],
        }])


if __name__ == "__main__":
    unittest.main()
