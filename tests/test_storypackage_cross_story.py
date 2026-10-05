import unittest
import copy
import json
from collections import Counter
import subprocess
import tempfile
from pathlib import Path

from pipeline import storypackage_adapter, storypackage_splitter


class StoryPackageCrossStoryAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[2]
        cls.upstream = cls.root / "patterns-storypackage-review"
        cls.examples = cls.upstream / "architecture/storypackage/examples"
        cls.python = Path("/Users/dwaynetoler/Documents/ChatGPT/Polish/person-cutout-system/image-tools/.venv-rembg/bin/python")

    def _run(self, filename, mappings=None):
        source = self.examples / filename
        adapted = storypackage_adapter.build(
            source, upstream_root=self.upstream, checker_python=self.python,
            repo_mappings=mappings,
        )
        return adapted, storypackage_splitter.build(adapted, source_path=source)

    def _assert_source_fact_contract(self, adapted, result):
        self.assertTrue(adapted["storyHandoffReceipt"]["accepted"])
        expected = Counter(row["claimId"] for row in adapted["claims"]
                           if row.get("status") == "unverified")
        actual = Counter(row["claim"] for row in result["gaps"]
                         if row["gap"] == "source_fact_unverified")
        self.assertEqual(actual, expected)
        self.assertEqual([row for row in result["gaps"]
                          if row["gap"] != "source_fact_unverified"], adapted["gaps"])
        self.assertEqual(result["counts"]["typedGaps"], len(result["gaps"]))
        self.assertEqual(result["counts"]["claims"], len(adapted["claims"]))
        self.assertEqual(result["counts"]["uncoveredClaims"], 0)
        covered = {cid for task in result["taskProposals"] for cid in task["claimIds"]}
        covered.update(cid for route in result["speakerRoutes"] for cid in route["claimIds"])
        self.assertEqual(covered, {row["claimId"] for row in adapted["claims"]})
        self.assertFalse(result["selectionAuthorized"])
        self.assertFalse(result["renderingAuthorized"])
        self.assertEqual(result["activationState"], "review_only_not_connected")

    def _pinned_astra_worktree(self, commit):
        temporary = tempfile.TemporaryDirectory()
        path = Path(temporary.name) / "astra"
        subprocess.run(
            ["git", "worktree", "add", "--detach", str(path), commit],
            cwd=self.root / "astra-visual-selector", check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        self.addCleanup(temporary.cleanup)
        self.addCleanup(
            subprocess.run,
            ["git", "worktree", "remove", "--force", str(path)],
            cwd=self.root / "astra-visual-selector", check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return path

    def test_apollo_and_year_seventeen_use_the_identical_path(self):
        apollo_adapter, apollo = self._run("apollo-collins-sample.storypackage-0.2.json")
        year_adapter, year = self._run(
            "year-seventeen-excerpt.storypackage-0.2.json",
            {
                "djtoler/astra-visual-selector": self._pinned_astra_worktree("da8b175"),
                "djtoler/automation-data": Path("/Users/dwaynetoler/yt001data"),
            },
        )
        self.assertEqual(apollo["counts"]["taskProposals"], 6)
        self.assertEqual(year["counts"]["taskProposals"], 5)
        self.assertEqual(apollo["counts"]["uncoveredClaims"], 0)
        self.assertEqual(year["counts"]["uncoveredClaims"], 0)
        self.assertEqual(apollo["counts"]["semanticDerivedTaskProposals"], 1)
        self.assertTrue(any(row["gap"] == "cohort_incomplete" for row in apollo["gaps"]))
        for adapted, result in ((apollo_adapter, apollo), (year_adapter, year)):
            self._assert_source_fact_contract(adapted, result)
            self.assertEqual(result["counts"]["claims"], 8)
            self.assertEqual(sum(row["gap"] == "source_fact_unverified"
                                 for row in result["gaps"]), 7)

    def test_supported_claim_and_status_counterexamples_use_accepted_sources(self):
        source = self.examples / "apollo-collins-sample.storypackage-0.2.json"
        original = json.loads(source.read_text())
        # a7 already has a source-authored receipt. Alter only its status in a
        # temporary package; structural acceptance is not factual verification.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "status-counterexample.json"
            for status in ("supported", "contested", "inferred", "unverified"):
                package = copy.deepcopy(original)
                target = next(row for row in package["claims"] if row["claimId"] == "a7")
                target["status"] = status
                path.write_text(json.dumps(package))
                adapted = storypackage_adapter.build(
                    path, upstream_root=self.upstream, checker_python=self.python)
                result = storypackage_splitter.build(adapted, source_path=path)
                with self.subTest(status=status):
                    self._assert_source_fact_contract(adapted, result)
                    unresolved = {row["claim"] for row in result["gaps"]
                                  if row["gap"] == "source_fact_unverified"}
                    self.assertEqual("a7" in unresolved, status == "unverified")
                    self.assertEqual(result["counts"]["taskProposals"], 6)
                    self.assertEqual(result["counts"]["semanticDerivedTaskProposals"], 1)
                    self.assertEqual(adapted["claims"], package["claims"])

    def test_unverified_gap_cannot_be_deleted_duplicated_or_reassigned(self):
        adapted, result = self._run("apollo-collins-sample.storypackage-0.2.json")
        self._assert_source_fact_contract(adapted, result)
        for mutation in ("delete", "duplicate", "reassign"):
            broken = copy.deepcopy(result)
            row = next(row for row in broken["gaps"] if row["gap"] == "source_fact_unverified")
            if mutation == "delete":
                broken["gaps"].remove(row)
            elif mutation == "duplicate":
                broken["gaps"].append(copy.deepcopy(row))
            else:
                row["claim"] = "a6"  # editorial claim has no unverified status
            broken["counts"]["typedGaps"] = len(broken["gaps"])
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                self._assert_source_fact_contract(adapted, broken)


if __name__ == "__main__":
    unittest.main()
