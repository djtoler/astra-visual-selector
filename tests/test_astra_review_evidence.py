import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_astra_review_evidence", ROOT / "pipeline" / "build_astra_review_evidence.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class AstraReviewEvidenceTests(unittest.TestCase):
    def test_review_evidence_is_safe_and_deterministic(self):
        first = MODULE.build("2026-10-04T00:00:00+00:00")
        second = MODULE.build("2026-10-04T00:00:00+00:00")
        MODULE.validate(first)
        self.assertEqual(first, second)
        self.assertIs(first["selectionAuthorized"], False)
        self.assertIs(first["renderingAuthorized"], False)
        self.assertGreaterEqual(first["counts"]["uniqueRecords"], 400)

    def test_current_jayz_drake_reviews_are_preserved(self):
        package = MODULE.build("2026-10-04T00:00:00+00:00")
        current = [
            row for row in package["records"]
            if row.get("packageId") == "jayz-drake-settle-it@4"
            and row["evidenceType"] == "candidate_acceptability"
        ]
        self.assertEqual(len(current), 12)
        self.assertTrue(all(row["comment"] for row in current))

    def test_abandoned_repo_is_in_source_manifest(self):
        package = MODULE.build("2026-10-04T00:00:00+00:00")
        paths = [source["canonicalPath"] for source in package["sources"]]
        aliases = [alias for source in package["sources"] for alias in source["aliases"]]
        self.assertTrue(any(path.startswith("astra-visual-selector/") for path in paths + aliases))


if __name__ == "__main__":
    unittest.main()
