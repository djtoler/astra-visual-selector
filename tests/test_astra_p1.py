import copy
import json
from pathlib import Path
import tempfile
import unittest

from pipeline import matching_agent, storypackage_adapter as adapter
from pipeline import storypackage_data_assignment as data

ROOT = Path(__file__).resolve().parents[1]


class P1BindingTests(unittest.TestCase):
    def field_fixture(self, value=0):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        source = Path(folder.name) / "measurements.csv"
        source.write_text("artist,status,count\nExample,ok,0\n")
        field = {"fieldId": "count", "value": value, "unit": "count", "encodings": ["magnitude"],
                 "receipt": {"source": "measurements", "sourcePath": str(source),
                             "sourceSha256": data._sha(source), "selector": {"artist": "Example", "status": "ok"},
                             "columns": ["count"], "transform": "exact CSV numeric value"}}
        return {"packageId": "example@1", "sources": {"measurements": {"path": str(source), "sha256": data._sha(source)}},
                "assignments": [{"taskId": "t", "status": "resolved", "requiredEncodings": ["magnitude"],
                                 "typedFields": [field], "gaps": []}],
                "dataHandoffComplete": True, "counts": {}, "selectionAuthorized": False, "renderingAuthorized": False}

    def test_measured_zero_replays_from_source(self):
        result = data.validate(self.field_fixture())
        self.assertEqual(result["verifiedFields"], {"t": ["count"]})

    def test_changed_value_and_selector_fail(self):
        for mutation in ("value", "selector", "path", "source"):
            artifact = self.field_fixture()
            field = artifact["assignments"][0]["typedFields"][0]
            if mutation == "value": field["value"] = 1
            elif mutation == "selector": field["receipt"]["selector"]["artist"] = "Other"
            elif mutation == "path": field["receipt"]["sourcePath"] += ".other"
            else: field["receipt"]["source"] = "other"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                data.validate(artifact)

    def test_changed_source_bytes_fail(self):
        artifact = self.field_fixture()
        Path(artifact["sources"]["measurements"]["path"]).write_text("changed")
        with self.assertRaises(ValueError): data.validate(artifact)

    def test_unsupported_transform_is_readable_but_unresolved(self):
        artifact = self.field_fixture()
        artifact["assignments"][0]["typedFields"][0]["receipt"]["transform"] = "unknown upstream method"
        result = data.validate(artifact)
        self.assertEqual(result["verifiedFields"], {})
        self.assertTrue(result["unresolvedFields"])

    def test_file_presence_never_covers_other_tasks_or_fields(self):
        artifact = self.field_fixture()
        proposals = {"packageId": "example@1", "taskProposals": [
            {"taskProposalId": "t", "values": [{"label": "count", "value": 0, "unit": "count"}]},
            {"taskProposalId": "other", "values": [{"label": "count", "value": 0, "unit": "count"}]},
            {"taskProposalId": "missing", "values": [{"label": "other"}]}]}
        result = matching_agent._requirements(proposals, data_handoff=artifact)
        self.assertEqual([r["data"]["status"] for r in result["tasks"]], ["bound", "gap", "gap"])
        artifact["packageId"] = "foreign@1"
        result = matching_agent._requirements(proposals, data_handoff=artifact)
        self.assertTrue(all(r["data"]["status"] == "gap" for r in result["tasks"]))

    def test_stale_new_adapter_source_and_body_fail(self):
        from tests.test_storypackage_adapter import StoryPackageAdapterTests
        StoryPackageAdapterTests.setUpClass()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "package.json"
            path.write_bytes(StoryPackageAdapterTests.apollo.read_bytes())
            artifact = adapter.build(path, upstream_root=StoryPackageAdapterTests.upstream,
                                     checker_python=StoryPackageAdapterTests.python)
            self.assertEqual(adapter.validate(artifact)["status"], "verified")
            broken = copy.deepcopy(artifact)
            broken["claims"][0]["text"] = "changed"
            with self.assertRaises(ValueError): adapter.validate(broken)
            path.write_text("{}")
            with self.assertRaises(ValueError): adapter.validate(artifact)

    def test_receipt_omission_is_not_verified(self):
        artifact = json.loads((ROOT / "reports/storypackage-02-apollo-adapter.json").read_text())
        self.assertEqual(adapter.validate(artifact, source_path=ROOT / "reports/storypackage-02-apollo-adapter.json")["status"], "legacy_unresolved")
        artifact["storyHandoffReceipt"]["accepted"] = False
        with self.assertRaises(ValueError): adapter.validate(artifact)


if __name__ == "__main__": unittest.main()
