import copy
import json
from pathlib import Path
import tempfile
import unittest

from pipeline import visualtask_ae_spec_comparison as subject


ROOT = Path(__file__).resolve().parents[1]


class VisualTaskAESpecComparison(unittest.TestCase):
    def test_consumer_exists(self):
        self.assertTrue(callable(subject.build_comparison))

    def test_imported_index_reconciles_every_measured_composition_and_text_field(self):
        index = json.loads((ROOT / "grammar" / "ae-template-technical-index.json").read_text())
        self.assertEqual(
            subject.validate_technical_index(index),
            {"projects": 32, "compositions": 3926, "textFields": 3078},
        )
        vertical = next(row for row in index["projects"] if row["id"] == "vertical-cinematic-24")
        self.assertEqual(vertical["projectSummary"]["verifiedIndependentVisualMediaInputs"], 11)
        self.assertEqual(vertical["projectSummary"]["editableTextFields"], 22)
        self.assertEqual(vertical["capacityEnvelope"]["maxSimultaneouslyEnabledRecursiveVisualInputs"], 2)
        main = next(row for row in vertical["compositions"] if row["path"] == "Main_comp/Main")
        self.assertEqual(main["durationSeconds"], 26.2)

    def test_comparison_keeps_all_visual_tasks_and_split_tasks_separate(self):
        result = subject.build_comparison()
        self.assertEqual(result["counts"]["sourceBeats"], 40)
        self.assertEqual(result["counts"]["visualTasks"], 41)
        self.assertEqual(result["counts"]["splitBeats"], 1)
        split = [row for row in result["tasks"] if row["sourceBeatId"] == "28-28"]
        self.assertEqual([row["taskId"] for row in split], ["28-28.setup", "28-28.overlap"])
        self.assertEqual([row["displayIdentityDemand"] for row in split], [0, 10])

    def test_task_scoped_entities_replace_global_subject_for_capacity_demand(self):
        result = subject.build_comparison()
        by_id = {row["taskId"]: row for row in result["tasks"]}
        opening = by_id["01-01.subject"]
        self.assertEqual(opening["legacyGlobalSubject"], "Drake")
        self.assertEqual(opening["displayEligibleIdentities"], [])
        self.assertEqual(opening["displayIdentityDemand"], 0)
        catalog = by_id["02-02b.currensy_catalog"]
        self.assertEqual(catalog["displayEligibleIdentities"], ["Curren$y"])
        self.assertNotIn("Drake", catalog["displayEligibleIdentities"])
        cohort = by_id["03-03.opening_chart"]
        self.assertEqual(cohort["displayIdentityDemand"], 93)
        self.assertEqual(cohort["displayEligibleIdentities"].count("Drake"), 1)

    def test_verdicts_are_conservative_and_never_claim_fillable_now(self):
        result = subject.build_comparison()
        self.assertEqual(result["activationState"], "review_only_not_connected")
        self.assertFalse(result["selectionAuthorized"])
        self.assertFalse(result["renderingAuthorized"])
        self.assertEqual(result["evidenceBoundary"]["fillableNowStatus"], "not_computable_until_treatment_requirements_are_reviewed")
        comparisons = [candidate for row in result["tasks"] for candidate in row["candidateComparisons"]]
        self.assertGreater(result["counts"]["mappedCandidates"], 0)
        self.assertGreater(result["counts"]["unmappedCandidates"], 0)
        self.assertNotIn("fillable_now", json.dumps(comparisons))
        mapped = [row for row in comparisons if row.get("projectId")]
        exact = [row for row in mapped if row.get("exactComposition")]
        unresolved = [row for row in mapped if row.get("mappingUnresolved")]
        self.assertTrue(all("exact_scene_to_native_composition_mapping" not in row["missingForFillableNow"] for row in exact))
        self.assertTrue(all("exact_scene_to_native_composition_mapping" in row["missingForFillableNow"] for row in unresolved))

    def test_identity_count_is_not_used_as_media_slot_demand(self):
        result = subject.build_comparison()
        task = next(row for row in result["tasks"] if row["taskId"] == "03-03.opening_chart")
        self.assertEqual(task["displayIdentityDemand"], 93)
        self.assertIsNone(task["technicalRequirements"]["mediaRequirements"]["requiredSlotCount"])
        comparisons = [candidate for row in result["tasks"] for candidate in row["candidateComparisons"]]
        self.assertFalse(any("capacity_possible" in row["verdict"] for row in comparisons))
        self.assertFalse(any("capacity_conflict" in row["verdict"] for row in comparisons))

    def test_exact_task_and_composition_produce_duration_observation_not_fit(self):
        result = subject.build_comparison()
        task = next(row for row in result["tasks"] if row["taskId"] == "02-02a.main")
        candidate = next(row for row in task["candidateComparisons"] if row["candidateId"] == "screen-mockup-rfx--review-002")
        self.assertEqual(task["technicalRequirements"]["timingRequirement"]["exactTaskAudioSpan"]["durationSeconds"], 3.1)
        self.assertEqual(candidate["timingObservation"]["taskAudioDurationSeconds"], 3.1)
        self.assertEqual(candidate["timingObservation"]["nativeCompositionDurationSeconds"], 8.008008008008009)
        self.assertTrue(candidate["timingObservation"]["nativeDurationCoversUnmodifiedTask"])
        self.assertNotIn("fit", candidate["verdict"])

    def test_split_task_timing_remains_unresolved_in_candidate_comparison(self):
        result = subject.build_comparison()
        task = next(row for row in result["tasks"] if row["taskId"] == "28-28.overlap")
        self.assertIsNone(task["technicalRequirements"]["timingRequirement"]["exactTaskAudioSpan"])
        self.assertTrue(all("timingObservation" not in row for row in task["candidateComparisons"]))

    def test_zero_verified_slots_remain_partial_not_a_false_conflict(self):
        result = subject.build_comparison()
        row = next(row for row in result["tasks"] if row["taskId"] == "02-02b.currensy_catalog")
        dropoff = next(
            candidate for candidate in row["candidateComparisons"]
            if candidate["candidateId"].startswith("archive3-dropoff-carousels")
        )
        self.assertEqual(dropoff["projectId"], "project")
        self.assertEqual(dropoff["verdict"], "exact_technical_evidence_partial")

    def test_bad_crosswalk_project_fails_closed(self):
        links = json.loads((ROOT / "grammar" / "ae-template-spec-links.json").read_text())
        links["links"][0]["projectId"] = "does-not-exist"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "links.json"
            path.write_text(json.dumps(links))
            with self.assertRaisesRegex(ValueError, "unknown measured project"):
                subject.build_comparison(links_path=path)

    def test_stale_source_hash_fails_consumer(self):
        artifact = subject.build_comparison()
        artifact["sources"]["specLinks"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source is missing or stale"):
            subject.validate_comparison(artifact)

    def test_duplicate_task_fails_consumer(self):
        artifact = subject.build_comparison()
        artifact["tasks"].append(copy.deepcopy(artifact["tasks"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate comparison task id"):
            subject.validate_comparison(artifact, verify_sources=False)

    def test_build_is_deterministic_and_written_artifact_is_consumable(self):
        first = subject.dumps(subject.build_comparison())
        second = subject.dumps(subject.build_comparison())
        self.assertEqual(first, second)
        written = json.loads((ROOT / "reports" / "visualtask-ae-spec-comparison.json").read_text())
        self.assertEqual(subject.validate_comparison(written), written["counts"])


if __name__ == "__main__":
    unittest.main()
