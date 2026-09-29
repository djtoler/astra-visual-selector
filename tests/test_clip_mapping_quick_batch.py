import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "reports" / "clip-mapping-quick-batch-screen-mockup.json"


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class ScreenMockupQuickBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = load(EVIDENCE)
        cls.mappings = {
            row["sceneId"]: row
            for row in load(ROOT / "grammar" / "ae-scene-composition-mappings.json")["mappings"]
        }
        cls.technical = {
            row["id"]: row
            for row in load(ROOT / "grammar" / "ae-template-technical-index.json")["projects"]
        }

    def test_evidence_sources_are_hash_bound(self):
        for source in self.evidence["sources"].values():
            path = Path(source["path"])
            if not path.is_absolute():
                path = ROOT / path
            self.assertEqual(sha(path), source["sha256"])

    def test_five_preexisting_anchors_are_consecutive(self):
        self.assertEqual(
            [row["clipId"] for row in self.evidence["verifiedAnchors"]],
            [f"screen-mockup-rfx--review-{ordinal:03d}" for ordinal in range(2, 7)],
        )
        self.assertEqual(
            [row["compositionPath"] for row in self.evidence["verifiedAnchors"]],
            [f"03 Others/Final Scenes/Scene_{ordinal:02d}" for ordinal in range(2, 7)],
        )

    def test_native_master_contains_one_ordered_layer_per_scene(self):
        layers = self.evidence["nativeMaster"]["orderedSceneLayers"]
        self.assertEqual([row["ordinal"] for row in layers], list(range(1, 9)))
        self.assertEqual(
            [row["compositionPath"] for row in layers],
            [f"03 Others/Final Scenes/Scene_{ordinal:02d}" for ordinal in range(1, 9)],
        )
        starts = [row["startSeconds"] for row in layers]
        self.assertEqual(starts, sorted(starts))

    def test_promotions_match_registry_and_measured_capacity(self):
        project = self.technical["screen-mockup"]
        compositions = {row["id"]: row for row in project["compositions"]}
        for promoted in self.evidence["promotedMappings"]:
            mapping = self.mappings[promoted["clipId"]]
            composition = compositions[promoted["compositionId"]]
            self.assertEqual(mapping["status"], "verified")
            self.assertEqual(mapping["compositionId"], promoted["compositionId"])
            self.assertEqual(mapping["compositionPath"], promoted["compositionPath"])
            self.assertEqual(composition["path"], promoted["compositionPath"])
            self.assertEqual(
                composition["totalIndependentVisualMediaInputs"],
                promoted["absoluteMediaSlots"],
            )
            self.assertEqual(
                composition["maxSimultaneouslyEnabledRecursiveVisualInputs"],
                promoted["maxSimultaneouslyEnabledInputs"],
            )
            self.assertEqual(
                composition["recursiveEditableTextFields"],
                promoted["editableTextFields"],
            )


if __name__ == "__main__":
    unittest.main()
