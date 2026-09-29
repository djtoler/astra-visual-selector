import copy
import json
from pathlib import Path
import tempfile
import unittest

from pipeline import clip_technical_coverage as subject


ROOT = Path(__file__).resolve().parents[1]


class ClipTechnicalCoverage(unittest.TestCase):
    def setUp(self):
        self.ledger = subject.build_coverage()

    def test_union_covers_both_current_ae_catalogs(self):
        self.assertEqual(self.ledger["counts"]["clips"], 428)
        self.assertEqual(self.ledger["counts"]["families"], 40)
        self.assertEqual(
            self.ledger["counts"]["bySemanticCatalog"],
            {"approved_catalog": 185, "review_catalog": 243},
        )

    def test_every_clip_has_one_explicit_technical_state(self):
        self.assertEqual(
            sum(self.ledger["counts"]["byTechnicalState"].values()),
            self.ledger["counts"]["clips"],
        )
        self.assertNotIn(None, [row["technical"]["state"] for row in self.ledger["clips"]])
        self.assertEqual(self.ledger["counts"]["byTechnicalState"], {
            "mapped_composition_window_approximate": 5,
            "mapped_verified": 52,
            "mapped_verified_window": 17,
            "mapping_ambiguous": 2,
            "mapping_unverified": 333,
            "mogrt_not_aep": 5,
            "project_unlinked": 14,
        })

    def test_375_capability_pass_is_not_mistaken_for_catalog_scope(self):
        self.assertNotEqual(self.ledger["counts"]["clips"], 375)
        ids = {row["clipId"] for row in self.ledger["clips"]}
        self.assertIn("intro-slideshow-full-720p--scene-002", ids)
        self.assertIn("memories-photo-slideshow-creative-slides-envato--scene-001", ids)

    def test_pilot_rows_preserve_exact_composition_and_approximate_window(self):
        rows = {row["clipId"]: row for row in self.ledger["clips"]}
        row = rows["carousel-slideshow--review-005"]
        self.assertEqual(row["technical"]["state"], "mapped_composition_window_approximate")
        self.assertEqual(row["technical"]["composition"]["path"], "2.Final/Render 02")
        self.assertEqual(row["technical"]["window"]["startSeconds"], 24.02)

    def test_exact_window_rows_carry_clip_level_capacity(self):
        rows = {row["clipId"]: row for row in self.ledger["clips"]}
        row = rows["photo-slideshow-smooth-envato--scene-005"]
        self.assertEqual(row["technical"]["state"], "mapped_verified_window")
        self.assertEqual(row["technical"]["windowCapacity"]["absoluteMediaSlots"], 10)
        self.assertEqual(row["technical"]["windowCapacity"]["maxSimultaneouslyEnabledInputs"], 9)

    def test_unmapped_family_never_inherits_project_capacity(self):
        rows = [
            row for row in self.ledger["clips"]
            if row["technical"]["state"] in {"mapping_unverified", "project_unlinked"}
        ]
        self.assertTrue(rows)
        self.assertTrue(all(row["technical"]["composition"] is None for row in rows))

    def test_linked_clips_carry_hash_backed_project_status_without_capacity(self):
        rows = {row["clipId"]: row for row in self.ledger["clips"]}
        row = rows["scrolling-screen--review-002"]
        self.assertEqual(row["technical"]["state"], "mapping_unverified")
        self.assertEqual(row["technical"]["projectId"], "scrolling-screen-animations")
        self.assertEqual(len(row["technical"]["projectEvidence"]["sourceProjectSha256"]), 64)
        self.assertIsNone(row["technical"]["composition"])

    def test_exact_hash_reconciliation_links_minimalism_and_current_comparison_pack(self):
        rows = {row["clipId"]: row for row in self.ledger["clips"]}
        minimalism = rows["minimalism-slideshow--review-001"]
        comparison = rows["archive3-comparison-pack-ae--review-001"]
        self.assertEqual(minimalism["technical"]["projectId"], "slideshow")
        self.assertEqual(minimalism["technical"]["state"], "mapped_verified")
        self.assertEqual(
            minimalism["technical"]["projectEvidence"]["sourceProjectSha256"],
            "1da67cfa7485305b45de0be92026b7c02253c684880b8be277dfe7a55f43ab26",
        )
        self.assertEqual(comparison["technical"]["state"], "mapping_unverified")
        self.assertEqual(comparison["technical"]["projectId"], "comparison-pack")
        self.assertEqual(
            comparison["technical"]["projectEvidence"]["sourceProjectSha256"],
            "069b35bcf3611f52ca10b92728d0170ba079e2a03a948c102420cfc49c90f01f",
        )

    def test_family_link_with_wrong_project_hash_fails_closed(self):
        links = json.loads((ROOT / "grammar" / "ae-template-spec-links.json").read_text())
        links["links"][0]["sourceProjectSha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "links.json"
            path.write_text(json.dumps(links))
            with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                subject.build_coverage(spec_links_path=path)

    def test_mogrt_is_preserved_but_not_treated_as_aep(self):
        rows = [
            row for row in self.ledger["clips"]
            if row["familyId"] == "archive3-carousel-galleries-loop-animation-2"
        ]
        self.assertTrue(rows)
        self.assertTrue(all(row["technical"]["state"] == "mogrt_not_aep" for row in rows))
        self.assertTrue(all(row["availability"]["status"] == "excluded" for row in rows))

    def test_saved_report_matches_deterministic_build(self):
        saved = json.loads((ROOT / "reports/ae-clip-technical-coverage.json").read_text())
        self.assertEqual(subject.validate_coverage(saved), saved["counts"])

    def test_mutated_report_is_stale(self):
        broken = copy.deepcopy(self.ledger)
        broken["clips"][0]["semantic"]["description"] = "mutated"
        with self.assertRaisesRegex(ValueError, "stale|differs"):
            subject.validate_coverage(broken)


if __name__ == "__main__":
    unittest.main()
