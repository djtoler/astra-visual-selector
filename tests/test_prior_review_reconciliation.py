import copy
import json
import tempfile
import unittest
from pathlib import Path

from pipeline import prior_review_reconciliation as subject


class PriorReviewReconciliationTests(unittest.TestCase):
    def test_current_document_preserves_review_counts_and_never_authorizes(self):
        artifact = subject.build()
        self.assertEqual(artifact["reviewedBeatCount"], 40)
        self.assertEqual(artifact["priorSelectedOptionCount"], 107)
        self.assertEqual(artifact["priorNoneAcceptableBeatCount"], 3)
        self.assertEqual(artifact["priorSelectionCoverage"], {
            "total": 107, "presentInCurrentComparison": 101, "absentFromCurrentComparison": 6,
        })
        self.assertFalse(artifact["selectionAuthorized"])
        self.assertFalse(artifact["renderingAuthorized"])

    def test_known_prior_selection_is_not_a_fresh_choice(self):
        artifact = subject.build()
        row = next(r for r in artifact["rows"] if r["taskId"] == "02-02a.main" and r["candidateId"] == "photo-slideshow-memories-envato--scene-010")
        self.assertEqual(row["state"], "prior_selected")
        self.assertNotIn(row, artifact["humanAttentionQueue"])

    def test_nonselected_shown_option_is_dismissed_not_unreviewed(self):
        artifact = subject.build()
        row = next(r for r in artifact["rows"] if r["taskId"] == "16-16.main" and r["candidateId"] == "archive3-gallery-pro-carousel-2026-09-11-10-23-37-utc--review-002")
        self.assertEqual(row["state"], "prior_dismissed")

    def test_missing_prior_selections_are_system_work_not_silently_dropped(self):
        artifact = subject.build()
        absent = [r for r in artifact["systemResolutionQueue"] if r["reason"] == "prior_selection_absent_from_current_comparison"]
        self.assertEqual(len(absent), 6)

    def test_split_tasks_never_inherit_source_beat_selection(self):
        review = {"grammar":{"templatePicks":{"beats":{"x":{"reviewed":True,"shown":["a"],"selected":["a"],"noneAcceptable":False}}}}}
        comparison = {"tasks":[
            {"taskId":"x.one","sourceBeatId":"x","candidateComparisons":[{"candidateId":"a","technicalEvidenceVerdict":"exact_technical_evidence_partial"}]},
            {"taskId":"x.two","sourceBeatId":"x","candidateComparisons":[{"candidateId":"a","technicalEvidenceVerdict":"exact_technical_evidence_partial"}]},
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            rp, cp = Path(tmp)/"r.json", Path(tmp)/"c.json"
            rp.write_text(json.dumps(review)); cp.write_text(json.dumps(comparison))
            artifact = subject.build(review_path=rp, comparison_path=cp)
        self.assertTrue(all(r["state"] == "split_task_requires_independent_review" for r in artifact["rows"]))
        self.assertEqual(len(artifact["humanAttentionQueue"]), 2)

    def test_stale_source_fails_closed(self):
        artifact = subject.build()
        artifact = copy.deepcopy(artifact)
        artifact["sources"]["priorReview"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "missing or stale"):
            subject.validate(artifact)

    def test_deterministic_and_written_artifact_replays(self):
        self.assertEqual(subject.dumps(subject.build()), subject.dumps(subject.build()))


if __name__ == "__main__":
    unittest.main()
