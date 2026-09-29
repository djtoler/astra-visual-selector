import copy
import json
from pathlib import Path
import tempfile
import unittest

from pipeline import clip_mapping_calibration as subject


ROOT = Path(__file__).resolve().parents[1]


class ClipMappingCalibration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(subject.DEFAULT_REQUEST.read_text())
        cls.report = subject.build_report(cls.request)

    def test_predictor_sources_exclude_verified_answers(self):
        self.assertNotIn("verifiedMappings", self.request["predictorSources"])
        self.assertFalse(self.report["guardrails"]["predictorReadsVerifiedMappings"])

    def test_predictions_never_claim_verification(self):
        statuses = {
            row["status"] for row in self.report["prospective"]["predictions"]
        }
        self.assertLessEqual(statuses, {"proposed", "abstain"})

    def test_replay_catches_known_unsafe_structural_guesses(self):
        self.assertGreater(self.report["replay"]["errors"], 0)
        errors = {
            clip_id
            for metrics in self.report["replay"]["byEvidenceClass"].values()
            for clip_id in metrics["errors"]
        }
        self.assertIn("carousel--review-011", errors)

    def test_no_error_class_is_trusted(self):
        for name in self.report["decision"]["trustedEvidenceClasses"]:
            self.assertEqual(self.report["replay"]["byEvidenceClass"][name]["errors"], [])
            self.assertEqual(self.report["prospective"]["byEvidenceClass"][name]["errors"], [])

    def test_prospective_sample_is_cross_family_and_excludes_replay(self):
        sample = self.report["prospective"]["predictions"]
        self.assertEqual(len(sample), 30)
        self.assertGreaterEqual(len({row["familyId"] for row in sample}), 15)
        self.assertFalse(set(self.request["replaySceneIds"]) & {row["clipId"] for row in sample})
        self.assertFalse(set(self.request["prospectiveExcludedIds"]) & {row["clipId"] for row in sample})
        self.assertGreaterEqual(len(self.report["prospective"]["categoryCounts"]), 4)

    def test_prospective_predictions_are_locked_before_evaluation(self):
        predictions = [
            {
                key: value
                for key, value in row.items()
                if key not in {"category", "nativeTimelineEvaluation", "exactMatchWhenLabeled"}
            }
            for row in self.report["prospective"]["predictions"]
        ]
        import hashlib
        payload = json.dumps(
            predictions, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(
            hashlib.sha256(payload).hexdigest(),
            self.report["prospective"]["predictionLockSha256"],
        )

    def test_changed_source_hash_fails(self):
        broken = copy.deepcopy(self.request)
        broken["predictorSources"]["technicalIndex"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source changed"):
            subject.build_report(broken)

    def test_saved_report_is_deterministic(self):
        saved = json.loads(subject.DEFAULT_REPORT.read_text())
        self.assertEqual(subject.validate_report(saved, self.request)["replayTotal"], 73)
        self.assertEqual(subject.DEFAULT_REPORT.read_text(), subject.dumps(subject.build_report(self.request)))

    def test_production_mapping_sidecar_is_unchanged(self):
        source = self.request["evaluationSources"]["verifiedMappings"]
        self.assertEqual(subject._sha(subject._resolve(source["path"])), source["sha256"])


if __name__ == "__main__":
    unittest.main()
