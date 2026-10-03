import json
import tempfile
import unittest
from pathlib import Path

from pipeline import heldout_matching_integration as subject
from pipeline import matching_accuracy_batch
from pipeline import visualtask_batch_matching


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "semantic_split"


class HeldOutMatchingIntegration(unittest.TestCase):
    def build(self, output_dir: Path):
        return subject.build(
            story_path=FIXTURES / "story-package.json",
            vocabulary_path=FIXTURES / "task-vocabulary.json",
            roster_path=FIXTURES / "roster-context.json",
            editor_context_path=FIXTURES / "editor-context.json",
            response_path=FIXTURES / "external-response.json",
            bindings_path=ROOT / "grammar" / "bindings.json",
            output_dir=output_dir,
        )

    def test_actual_split_output_feeds_every_task_to_batch_matcher(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            evidence = self.build(output)
            matched = json.loads((output / "template-fit-output.json").read_text())
            self.assertEqual(evidence["split"]["proposedTasks"], 3)
            self.assertEqual(matched["counts"]["visualTasks"], 3)
            self.assertEqual(evidence["templateFit"]["tasksWithVerdict"], 3)
            self.assertEqual(evidence["mediaAvailability"]["tasksWithVerdict"], 3)
            visualtask_batch_matching.validate(matched)

    def test_all_semantic_requirements_survive_conversion(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence = self.build(Path(directory))
            requirements = evidence["requirements"]
            self.assertEqual(requirements["lostReferenceCount"], 0)
            self.assertEqual(requirements["sourceReferenceCounts"], requirements["preservedReferenceCounts"])

    def test_unsupported_typed_media_kinds_become_explicit_gaps(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            self.build(output)
            matched = json.loads((output / "template-fit-output.json").read_text())
            typed = [
                gap
                for row in matched["tasks"]
                for gap in row["mediaResult"]["gaps"]
                if gap.get("type") == "production_ready_media_kind"
            ]
            self.assertTrue(typed)
            self.assertTrue(all(gap["status"] == "missing" for gap in typed))
            self.assertTrue(all(row["mediaResult"]["availabilityVerdict"] == "unavailable" for row in matched["tasks"]))

    def test_conditional_gap_category_is_honestly_not_applicable(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence = self.build(Path(directory))
            self.assertEqual(evidence["conditionalGap"], {
                "reviewedMissingMediaBriefs": 0,
                "conditionalMediaVerdicts": 0,
                "status": "not_applicable_no_reviewed_missing_media_briefs",
            })

    def test_saved_heldout_report_has_only_human_review_pending(self):
        request = json.loads((ROOT / "matching-accuracy" / "held-out-001" / "request.json").read_text())
        report = matching_accuracy_batch.evaluate(request)
        self.assertEqual(report["summary"], {
            "total": 6, "passed": 5, "failed": 0, "pending": 1, "allPassed": False
        })
        pending = [row for row in report["cases"] if row["status"] == "pending"]
        self.assertEqual([row["id"] for row in pending], ["heldout-human-approval"])

    def test_runtime_contains_no_heldout_story_identifiers(self):
        source = (ROOT / "pipeline" / "heldout_matching_integration.py").read_text()
        for identifier in ("wetland-restoration", "restoration-progress", "aisha-patel"):
            self.assertNotIn(identifier, source)


if __name__ == "__main__":
    unittest.main()
