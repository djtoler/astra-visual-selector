import unittest
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
        return storypackage_splitter.build(adapted, source_path=source)

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
        apollo = self._run("apollo-collins-sample.storypackage-0.2.json")
        year = self._run(
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
        self.assertEqual(year["gaps"], [])


if __name__ == "__main__":
    unittest.main()
