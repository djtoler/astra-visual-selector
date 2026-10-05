"""Frozen audit assertions. P3–P6 assertions remain deliberately unrepaired.

Run this file with ASTRA_TEST_RUNTIME_ROOT pointing at the pinned baseline to
prove failures independently of the implementation checkout. No model runs.
"""
import collections
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

EVIDENCE_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = Path(os.environ.get("ASTRA_TEST_RUNTIME_ROOT", EVIDENCE_ROOT)).resolve()
sys.path.insert(0, str(RUNTIME_ROOT))
from pipeline import matching_agent, storypackage_splitter, storypackage_data_assignment
from pipeline import focused_candidate_diversity, storypackage_candidate_gallery
from pipeline import visualtask_matching as matching
from pipeline import build_astra_review_evidence


def read(relative):
    return json.loads((EVIDENCE_ROOT / relative).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_calibration(manifest):
    if manifest.get("schemaVersion") != "astra-calibration@1":
        raise ValueError("unsupported calibration version")
    if not manifest.get("sources") or not manifest.get("evidence"):
        raise ValueError("calibration evidence omitted")
    for source in manifest["sources"]:
        if digest(EVIDENCE_ROOT / source["path"]) != source["sha256"]:
            raise ValueError("calibration source digest changed")
    evidence = read("reports/astra-matching-review-evidence-20261004.json")
    build_astra_review_evidence.validate(evidence)
    by_id = {row["evidenceId"]: row for row in evidence["records"]}
    if {row["evidenceId"] for row in manifest["evidence"]} != set(by_id):
        raise ValueError("calibration evidence omitted or added")
    for row in manifest["evidence"]:
        original = by_id[row["evidenceId"]]
        encoded = json.dumps(original, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        if row["recordSha256"] != hashlib.sha256(encoded).hexdigest():
            raise ValueError("calibration context digest changed")
        if any(row.get(key) != original[key] for key in ("authorship", "scope", "sourceRefs")):
            raise ValueError("calibration author/source scope changed")


def rebased_gallery(stem):
    gallery = read(f"reports/storypackage-02-{stem}-candidate-gallery.json")
    for source in gallery["sources"].values():
        old = source["path"]
        for folder in ("reports", "grammar"):
            marker = f"/{folder}/"
            if marker in old:
                source["path"] = str(EVIDENCE_ROOT / folder / old.split(marker, 1)[1])
                break
        if digest(source["path"]) != source["sha256"]:
            raise ValueError("frozen gallery source digest mismatch")
    return gallery


class P0CalibrationControls(unittest.TestCase):
    def test_calibration_integrity_and_negative_mutations(self):
        manifest = read("reports/astra-p0-p2/calibration-manifest.json")
        validate_calibration(manifest)
        for mutation in ("digest", "scope", "context", "omission"):
            altered = copy.deepcopy(manifest)
            if mutation == "digest":
                altered["sources"][0]["sha256"] = "0" * 64
            elif mutation == "scope":
                altered["evidence"][0]["scope"] = "global"
            elif mutation == "context":
                altered["evidence"][0]["recordSha256"] = "0" * 64
            else:
                altered["evidence"].pop()
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_calibration(altered)

    def test_handoff_and_gold_hashes(self):
        manifest = read("docs/p0-p2-gpt-6-1-sol-handoff/HANDOFF_MANIFEST.json")
        policy = read("docs/astra-root-cause/EXECUTION_POLICY.json")
        for source in manifest["authoritativeFiles"] + policy["goldReferences"]:
            self.assertEqual(digest(EVIDENCE_ROOT / source["path"]), source["sha256"], source["path"])

    def test_evidence_omission_fails_existing_validator(self):
        evidence = read("reports/astra-matching-review-evidence-20261004.json")
        build_astra_review_evidence.validate(evidence)
        evidence["records"][0]["sourceRefs"] = []
        with self.assertRaises(AssertionError):
            build_astra_review_evidence.validate(evidence)

    def test_exploration_tie_core_is_independently_reproduced(self):
        total = ties = 0
        for stem in ("future-volksgeist-v12", "jayz-drake-settle-it-v13"):
            artifact = read(f"reports/storypackage-02-{stem}-focused-candidate-diversity.json")
            frequencies = collections.Counter()
            for row in artifact["tasks"]:
                primary = row["displayedFamilies"][:8]
                pool = [family for family in row["displayedFamilies"] + row["hiddenAdmittedFamilies"]
                        if family not in primary]
                # Intentional empty routes can have fewer than eight primaries.
                exploration = row["focusedReviewFamilies"][len(primary):]
                if exploration:
                    cutoff = frequencies[exploration[-1]]
                    tied = sum(frequencies[family] == cutoff for family in pool)
                    taken = sum(frequencies[family] == cutoff for family in exploration)
                    ties += tied > taken
                frequencies.update(exploration)
                total += 1
        self.assertEqual((total, ties), (59, 58))


class P1BaselineFailures(unittest.TestCase):
    def test_hashed_empty_presence_cannot_erase_73_104_gaps(self):
        from tests.test_matching_agent_contracts import MatchingAgentContractTests
        from pipeline.matching_agent_contracts import preflight
        fixture = MatchingAgentContractTests()
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        for label in ("dataHandoff", "mediaHandoff"):
            path = fixture.root / f"{label}.json"
            path.write_text("{}")
            fixture.task[label] = {"path": str(path), "sha256": digest(path)}
        checked = preflight(fixture.task)
        proposals = read("reports/matching-agent-evaluation-20261004/jayz-drake-heldout/20-visualtask-proposals.json")
        result = matching_agent._requirements(
            proposals, data_bound="dataHandoff" in checked["inputs"],
            media_bound="mediaHandoff" in checked["inputs"])
        self.assertEqual(result["counts"]["dataRequired"], 73)
        self.assertEqual(result["counts"]["mediaRequired"], 104)
        self.assertEqual(result["counts"]["typedGaps"], 177,
                         "file presence is not task-and-field coverage")

    def test_stale_adapter_receipt_fails_closed(self):
        path = EVIDENCE_ROOT / "reports/matching-agent-evaluation-20261004/jayz-drake-heldout/10-storypackage-adapter.json"
        adapter = json.loads(path.read_text())
        adapter["storyHandoffReceipt"]["packageSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "stale|digest|source|receipt"):
            storypackage_splitter.build(adapter, source_path=path)

    def test_mutated_adapter_body_fails_closed(self):
        path = EVIDENCE_ROOT / "reports/matching-agent-evaluation-20261004/jayz-drake-heldout/10-storypackage-adapter.json"
        adapter = json.loads(path.read_text())
        adapter["claims"][0]["text"] += " invented"
        with self.assertRaisesRegex(ValueError, "stale|digest|source|receipt"):
            storypackage_splitter.build(adapter, source_path=path)

    def test_field_digest_must_match_top_level_source(self):
        artifact = read("reports/storypackage-02-data-assignments.json")
        artifact["assignments"][0]["typedFields"][0]["receipt"]["sourceSha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source|digest|receipt"):
            storypackage_data_assignment.validate(artifact, verify_sources=False)

    def test_typed_absence_cannot_become_zero(self):
        artifact = read("reports/storypackage-02-data-assignments.json")
        field = next(field for row in artifact["assignments"] for field in row["typedFields"]
                     if isinstance(field["value"], dict) and field["value"].get("availability") == "unavailable")
        field["value"] = 0
        with self.assertRaisesRegex(ValueError, "value|absence|receipt|source"):
            storypackage_data_assignment.validate(artifact, verify_sources=False)


class P2BaselineFailures(unittest.TestCase):
    def test_all_twelve_route_ineligible_tasks_stay_empty_in_focused_review(self):
        gallery = rebased_gallery("jayz-drake-settle-it-v13")
        ids = [row["taskId"] for row in gallery["tasks"]
               if (row.get("routeDisposition") or {}).get("templateEligible") is False]
        self.assertEqual(len(ids), 12)
        queue = {"packageId": gallery["packageId"], "taskIds": ids,
                 "selectionAuthorized": False, "renderingAuthorized": False}
        with tempfile.TemporaryDirectory() as raw:
            g, q = Path(raw) / "gallery.json", Path(raw) / "queue.json"
            g.write_text(json.dumps(gallery)); q.write_text(json.dumps(queue))
            result = focused_candidate_diversity.build(g, q)
        self.assertTrue(all(not row["focusedReviewCandidates"] for row in result["tasks"]),
                        "focused reconstruction discarded the intentional no-template route")

    def test_task_contract_fields_survive_gallery(self):
        gallery = rebased_gallery("jayz-drake-settle-it-v13")
        proposals_path = Path(gallery["sources"]["taskProposals"]["path"])
        proposals = json.loads(proposals_path.read_text())
        with patch.object(storypackage_candidate_gallery, "_local_relevance",
                          return_value=([{}] * len(proposals["taskProposals"]),
                                        {"scope": "audit_test_no_model_execution"})):
            result = storypackage_candidate_gallery.build(
                proposals_path=proposals_path,
                adapter_path=Path(gallery["sources"]["adapter"]["path"]))
        rows = {row["taskId"]: row for row in result["tasks"]}
        for proposal in proposals["taskProposals"]:
            task = rows[proposal["taskProposalId"]]
            for field in ("obligations", "continuity", "values", "cohortRefs", "entityRefs"):
                self.assertEqual(task.get(field), proposal.get(field, []),
                                 f"gallery loses source contract field {field}")


class LaterStageBaselineFailures(unittest.TestCase):
    def test_p6_exploration_is_invariant_to_tied_admitted_position(self):
        gallery = rebased_gallery("future-volksgeist-v12")
        queue = read("reports/storypackage-02-future-volksgeist-v12-focused-review-queue.json")
        queue["taskIds"] = queue["taskIds"][:1]
        actual_candidates = matching.template_candidates
        with tempfile.TemporaryDirectory() as raw:
            g, q = Path(raw) / "gallery.json", Path(raw) / "queue.json"
            g.write_text(json.dumps(gallery)); q.write_text(json.dumps(queue))
            first = focused_candidate_diversity.build(g, q)
            def reverse_admitted(*args, **kwargs):
                return list(reversed(actual_candidates(*args, **kwargs)))
            with patch.object(matching, "template_candidates", side_effect=reverse_admitted):
                second = focused_candidate_diversity.build(g, q)
        self.assertEqual(set(first["tasks"][0]["focusedReviewFamilies"]),
                         set(second["tasks"][0]["focusedReviewFamilies"]),
                         "tied families are chosen by admitted-list position")

    def test_p3_rate_subspan_materializes_exact_text(self):
        path = EVIDENCE_ROOT / "reports/matching-agent-evaluation-20261004/year-seventeen-regression/10-storypackage-adapter.json"
        adapter = json.loads(path.read_text())
        output = storypackage_splitter.build(adapter, source_path=path)
        row = next(row for row in output["taskProposals"] if row["jobProposalId"] == "p-21-21b-rate")
        claim = next(claim for claim in adapter["claims"] if claim["claimId"] == row["claimIds"][0])
        start = row["proposalSpan"]["start"] - claim["span"]["start"]
        expected = claim["text"][start:start + row["proposalSpan"]["len"]]
        self.assertEqual(row["taskText"], expected, "authored rate subspan expanded to the whole claim")

    def test_p4_timeline_scope_matches_chronological_operation(self):
        pool = {row["id"]: row for row in matching.C.load(content_class="*")}
        task = {"id": "regression.timeline", "job": "narrate_an_event", "taskRole": "main",
                "quote": "A chronological history.", "entityCount": 1,
                "presentationOperations": ["archival_progression"],
                "primaryPresentationOperation": "archival_progression",
                "ignorePriorSelections": True}
        rows = matching.template_candidates(task, {}, pool, exhaustive_families=True)
        self.assertTrue(any("search-bar-business-timeline" in row["candidateId"] for row in rows),
                        "timeline scope is rejected before ordering")

    def test_p5_sibling_variants_remain_available_for_fit(self):
        trace = read("reports/astra-root-cause/06-candidate-lineages.json")["traces"][0]
        pool = {row["id"]: row for row in matching.C.load(content_class="*")}
        result = matching.template_candidates(trace["replayInput"], {}, pool, exhaustive_families=True)
        self.assertTrue(any(row.get("siblings") or row.get("_siblings") for row in result),
                        "family representatives serialize no sibling alternatives")


# These target assertions are frozen failures, not stage-completion claims.
# Promote the P1/P2 classes only after the corresponding repair is verified.
# ASTRA_BASELINE_PROBE=1 executes raw assertions to reproduce the failing baseline.
if os.environ.get("ASTRA_BASELINE_PROBE") != "1":
    repaired = set(os.environ.get("ASTRA_REPAIRED_STAGES", "").split(","))
    for stage in ("P1", "P2"):
        receipt_path = RUNTIME_ROOT / f"reports/astra-p0-p2/{stage.lower()}-receipt.json"
        if receipt_path.is_file() and json.loads(receipt_path.read_text()).get("status") == "complete":
            repaired.add(stage)
    for cls in (P1BaselineFailures, P2BaselineFailures, LaterStageBaselineFailures):
        if (cls is P1BaselineFailures and "P1" in repaired) or (cls is P2BaselineFailures and "P2" in repaired):
            continue
        for name in unittest.defaultTestLoader.getTestCaseNames(cls):
            setattr(cls, name, unittest.expectedFailure(getattr(cls, name)))
    del cls, name


if __name__ == "__main__":
    import argparse
    import subprocess
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--record", type=Path)
    args, remaining = parser.parse_known_args()
    if args.record:
        class RecordingResult(unittest.TextTestResult):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.rows = []

            def addSuccess(self, test):
                super().addSuccess(test)
                self.rows.append({"testId": test.id(), "outcome": "pass"})

            def addFailure(self, test, err):
                super().addFailure(test, err)
                self.rows.append({"testId": test.id(), "outcome": "assertion_failure", "reason": str(err[1])})

            def addError(self, test, err):
                super().addError(test, err)
                self.rows.append({"testId": test.id(), "outcome": "error", "reason": str(err[1])})

            def addExpectedFailure(self, test, err):
                super().addExpectedFailure(test, err)
                self.rows.append({"testId": test.id(), "outcome": "pending_failure", "reason": str(err[1])})

        runner = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult)
        program = unittest.main(argv=[sys.argv[0], *remaining], testRunner=runner, exit=False)
        result = program.result
        artifact = {
            "schemaVersion": "astra-baseline-outcomes@1",
            "runtimeCommit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=RUNTIME_ROOT, text=True).strip(),
            "command": "ASTRA_BASELINE_PROBE=1 ASTRA_TEST_RUNTIME_ROOT=../matching-frozen python3 tests/test_astra_p0_p2.py --record reports/astra-p0-p2/p0-baseline-outcomes.json",
            "tests": result.rows,
            "counts": {"run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors), "expectedFailures": len(result.expectedFailures)},
            "testsSha256": digest(Path(__file__)),
            "modelExecution": False,
        }
        args.record.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
        sys.exit(0 if result.wasSuccessful() else 1)
    unittest.main(argv=[sys.argv[0], *remaining])
