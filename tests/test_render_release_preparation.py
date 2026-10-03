import copy
import unittest

from pipeline import render_release_preparation as subject


class RenderReleasePreparationTests(unittest.TestCase):
    def test_packet_covers_final_routes_without_authorizing_render(self):
        packet = subject.build()
        result = subject.validate(packet, verify_sources=False)
        self.assertEqual(result["scenes"], 41)
        self.assertEqual(packet["counts"]["templateRoutes"], 32)
        self.assertEqual(packet["counts"]["brollRoutes"], 9)
        self.assertEqual(packet["counts"]["deferredRoutes"], 0)
        self.assertEqual(packet["counts"]["postBeatBrollSegments"], 1)
        self.assertFalse(packet["renderingAuthorized"])
        self.assertFalse(packet["publishAuthorized"])

    def test_carries_the_recorded_template_choice(self):
        packet = subject.build()
        by_id = {row["taskId"]: row for row in packet["scenes"]}
        self.assertEqual(by_id["03-03.opening_chart"]["selectedTemplateId"], "truth-population-field")
        self.assertEqual(by_id["16-16.main"]["selectedTemplateId"],
                         "archive3-carousel-photo-logo-reveal-2026-09-13-12-24-28-utc--review-v2-001")

    def test_broll_is_valid_route_but_requires_exact_release_binding(self):
        packet = subject.build()
        row = next(row for row in packet["scenes"] if row["taskId"] == "05-05b.main")
        self.assertEqual(row["route"], "broll")
        self.assertIn("exact_broll_asset_binding_pending", {gap["kind"] for gap in row["blockers"]})
        self.assertNotIn("template_selection_missing", {gap["kind"] for gap in row["blockers"]})

    def test_existing_resolver_rank_is_carried_as_proposal_not_approval(self):
        packet = subject.build()
        by_id = {row["taskId"]: row for row in packet["scenes"]}
        self.assertEqual(by_id["01-01.subject"]["proposedAssetIds"], ["02fcf40be8477dbac2d6ad87"])
        self.assertEqual(by_id["01-01.subject"]["assetProposalStatus"],
                         "system_proposed_pending_editor")
        self.assertEqual(by_id["01-01.subject"]["boundAssetIds"], [])
        self.assertEqual(by_id["05-05b.main"]["assetProposalStatus"], "sourcing_required")

    def test_stale_source_fails_closed(self):
        packet = copy.deepcopy(subject.build())
        packet["sources"]["orderedVisualPlan"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "missing or stale"):
            subject.validate(packet)

    def test_beat_fifteen_broll_is_after_the_template_beat(self):
        packet = subject.build()
        row = next(row for row in packet["scenes"] if row["taskId"] == "15-15.main")
        self.assertEqual(row["route"], "template")
        self.assertEqual(row["supplementalBroll"]["placement"], "after_beat")

    def test_split_task_choice_is_validated_against_locked_route_slate(self):
        packet = subject.build()
        row = next(row for row in packet["scenes"] if row["taskId"] == "28-28.setup")
        self.assertEqual(row["selectedTemplateId"], "truth-cohort-attrition")
        self.assertNotIn("selected_template_not_in_locked_route_slate",
                         {gap["kind"] for gap in row["blockers"]})

    def test_confirmed_local_ae_mappings_are_source_bound_and_retired_family_is_absent(self):
        packet = subject.build()
        by_id = {row["taskId"]: row for row in packet["scenes"]}
        self.assertEqual(by_id["01-01.subject"]["timingPlan"]["durationEvidence"],
                         "editor_confirmed_original_aep_native_comparison")
        self.assertEqual(by_id["11-11a.main"]["timingPlan"]["durationEvidence"],
                         "editor_observed_approximate_active_motion_window")
        self.assertEqual(by_id["11-11a.main"]["timingPlan"]["activeMotionWindow"]["postWindowBehavior"],
                         "still_hold")
        self.assertLess(by_id["11-11a.main"]["timingPlan"]["speedPercent"], 150)
        self.assertEqual(by_id["12-12a.main"]["selectedTemplateId"], "truth-rank-fall")
        self.assertEqual(by_id["25-25a.main"]["selectedTemplateId"], "24_dense_vertical_bars")
        self.assertFalse(any(
            str(row.get("selectedTemplateId") or "").startswith("3dz-charts--")
            for row in packet["scenes"]
        ))
        all_blockers = {gap["kind"] for row in packet["scenes"] for gap in row["blockers"]}
        self.assertNotIn("selected_template_timing_deferred_until_use", all_blockers)


if __name__ == "__main__":
    unittest.main()
