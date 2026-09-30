import copy
import json
from pathlib import Path
import unittest

from pipeline import family_mapping_rules as subject


ROOT = Path(__file__).resolve().parents[1]


class FamilyMappingRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(subject.DEFAULT_REQUEST.read_text())
        cls.report = subject.build_report(cls.request)

    def test_batch_has_zero_rule_or_native_structure_errors(self):
        self.assertEqual(self.report["summary"], {
            "families": 4,
            "anchors": 11,
            "proposals": 24,
            "leaveOneOutErrors": 0,
            "nativeStructureErrors": 0,
        })

    def test_proposals_never_claim_final_verification(self):
        self.assertEqual({row["status"] for row in self.report["proposals"]}, {"proposed_verified"})

    def test_saved_report_is_deterministic(self):
        saved = json.loads(subject.DEFAULT_REPORT.read_text())
        self.assertEqual(subject.validate_report(saved, self.request), self.report["summary"])
        self.assertEqual(subject.DEFAULT_REPORT.read_text(), subject.dumps(subject.build_report(self.request)))

    def test_changed_native_source_hash_fails(self):
        broken = copy.deepcopy(self.request)
        broken["sources"]["documentaryNative"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "bound source changed"):
            subject.build_report(broken)

    def test_changed_anchor_fails(self):
        broken = copy.deepcopy(self.request)
        broken["families"][0]["anchors"][0]["compositionId"] = -1
        with self.assertRaisesRegex(ValueError, "anchor changed or missing"):
            subject.build_report(broken)

    def test_promoted_targets_match_registry_when_present(self):
        registry = {
            row["sceneId"]: row
            for row in json.loads((ROOT / self.request["registryPath"]).read_text())["mappings"]
        }
        for proposal in self.report["proposals"]:
            current = registry.get(proposal["clipId"])
            if current is None:
                continue
            self.assertEqual(current["status"], "verified")
            self.assertEqual(current["projectId"], proposal["projectId"])
            self.assertEqual(current["compositionId"], proposal["compositionId"])
            self.assertEqual(current["compositionPath"], proposal["compositionPath"])


class ExactTerminalSetRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_path = ROOT / "clip-mapping-batches" / "batch-007" / "request.json"
        cls.report_path = ROOT / "reports" / "clip-mapping-batch-007.json"
        cls.request = json.loads(cls.request_path.read_text())
        cls.report = subject.build_report(cls.request)

    def test_batch_uses_complete_source_bound_terminal_sets(self):
        self.assertEqual(self.report["summary"], {
            "families": 2,
            "anchors": 5,
            "proposals": 8,
            "leaveOneOutErrors": 0,
            "nativeStructureErrors": 0,
        })
        self.assertEqual(
            {row["rule"]["nativeEvidence"]["mode"] for row in self.report["families"]},
            {"exact_terminal_set"},
        )

    def test_saved_exact_terminal_report_is_deterministic(self):
        saved = json.loads(self.report_path.read_text())
        self.assertEqual(subject.validate_report(saved, self.request), self.report["summary"])
        self.assertEqual(self.report_path.read_text(), subject.dumps(self.report))

    def test_incomplete_terminal_scope_fails_closed(self):
        broken = copy.deepcopy(self.request)
        broken["families"][0]["targetClipIds"].pop()
        with self.assertRaisesRegex(ValueError, "batch does not cover exact terminal set"):
            subject.build_report(broken)

    def test_changed_terminal_set_fails_closed(self):
        broken = copy.deepcopy(self.request)
        broken["families"][0]["expectedTerminalOrdinals"].append(10)
        with self.assertRaisesRegex(ValueError, "technical index terminal set changed"):
            subject.build_report(broken)


class ExplicitTerminalSetRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_path = ROOT / "clip-mapping-batches" / "batch-008" / "request.json"
        cls.report_path = ROOT / "reports" / "clip-mapping-batch-008.json"
        cls.request = json.loads(cls.request_path.read_text())
        cls.report = subject.build_report(cls.request)

    def test_batch_covers_complete_explicit_terminal_sets(self):
        self.assertEqual(self.report["summary"], {
            "families": 3,
            "anchors": 8,
            "proposals": 11,
            "leaveOneOutErrors": 0,
            "nativeStructureErrors": 0,
        })
        self.assertEqual(
            {row["rule"]["nativeEvidence"]["mode"] for row in self.report["families"]},
            {"explicit_terminal_set"},
        )

    def test_saved_explicit_terminal_report_is_deterministic(self):
        saved = json.loads(self.report_path.read_text())
        self.assertEqual(subject.validate_report(saved, self.request), self.report["summary"])
        self.assertEqual(self.report_path.read_text(), subject.dumps(self.report))

    def test_incomplete_explicit_scope_fails_closed(self):
        broken = copy.deepcopy(self.request)
        broken["families"][0]["targetClipIds"].pop()
        with self.assertRaisesRegex(ValueError, "batch does not cover exact semantic terminal set"):
            subject.build_report(broken)

    def test_changed_explicit_terminal_set_fails_closed(self):
        broken = copy.deepcopy(self.request)
        broken["families"][0]["terminalBindings"][0]["compositionId"] = -1
        with self.assertRaisesRegex(ValueError, "technical index explicit terminal set changed"):
            subject.build_report(broken)


if __name__ == "__main__":
    unittest.main()
