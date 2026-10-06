import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from pipeline import p7_quality_evaluation as subject


class P7EvaluationContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.thresholds = {
            "schemaVersion": "astra-p7-quality-thresholds@1",
            "baseCommit": "c4b5ce0e49952c2fdbb36f30af01f73ace62fc12",
            "heldOutPackageId": "heldout@1",
            "labelsMustPrecedeTuning": True,
            "gates": {
                "criticalPositiveCandidateRecall": 1.0,
                "overallPositiveCandidateRecallMinimum": 0.9,
                "hardConstraintNegativeRejection": 1.0,
                "noTemplateAndBrollRouteCorrectness": 1.0,
                "semanticFidelity": 1.0,
                "maximumUnsupportedNativeFitClaims": 0,
                "maximumHiddenValidatedAlternatives": 0,
                "maximumUnknownToExhaustedTransitions": 0,
            },
            "reviewEffort": {"mode": "measure_baseline_only", "improvementClaimAllowed": False,
                             "metrics": ["minutes", "cardsInspected", "unresolvedDecisions", "reopenedCases"]},
            "selectionAuthorized": False, "renderingAuthorized": False,
        }
        self.threshold_path = self.root / "thresholds.json"
        self.threshold_path.write_text(json.dumps(self.thresholds))
        self.package = self.root / "package.json"; self.package.write_text('{"packageId":"heldout@1"}')
        self.release = self.root / "release.json"; self.release.write_text('{"packageId":"heldout@1"}')
        self.p6 = self.root / "p6.json"; self.p6.write_text('{"stage":"P6"}')

    def tearDown(self):
        self.temp.cleanup()

    def test_pre_review_receipt_binds_inputs_and_blocks_promotion(self):
        receipt = subject.build_pre_review(self.threshold_path, self.package, self.release, self.p6)
        subject.validate_pre_review(receipt)
        self.assertEqual(receipt["status"], "pending_blind_editor_labels")
        self.assertFalse(receipt["migrationAuthorized"])
        self.assertFalse(receipt["selectionAuthorized"])
        self.assertFalse(receipt["renderingAuthorized"])

    def test_threshold_or_source_mutation_invalidates_receipt(self):
        receipt = subject.build_pre_review(self.threshold_path, self.package, self.release, self.p6)
        for mutation in ("threshold", "package", "release", "p6", "authorization", "status"):
            bad = copy.deepcopy(receipt)
            if mutation in {"threshold", "package", "release", "p6"}:
                bad["inputs"][mutation]["sha256"] = "0" * 64
            elif mutation == "authorization":
                bad["migrationAuthorized"] = True
            else:
                bad["status"] = "passed"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                subject.validate_pre_review(bad)

    def test_invalid_thresholds_fail_closed(self):
        for mutation in ("missing", "range", "boolean", "authority"):
            bad = copy.deepcopy(self.thresholds)
            if mutation == "missing": del bad["gates"]["semanticFidelity"]
            elif mutation == "range": bad["gates"]["overallPositiveCandidateRecallMinimum"] = 1.1
            elif mutation == "boolean": bad["labelsMustPrecedeTuning"] = False
            else: bad["selectionAuthorized"] = True
            self.threshold_path.write_text(json.dumps(bad))
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                subject.build_pre_review(self.threshold_path, self.package, self.release, self.p6)


if __name__ == "__main__":
    unittest.main()
