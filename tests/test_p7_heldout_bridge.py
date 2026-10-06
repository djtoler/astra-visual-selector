import unittest

from pipeline import p7_heldout_bridge as subject
from pipeline import p7_blind_review_packet as packet
from pipeline import visualtask_batch_matching as batch


class P7HeldoutBridgeTests(unittest.TestCase):
    def task(self, *, template_eligible=True):
        return {
            "id": "pkg.proposal.1", "job": "narrate_an_event", "taskRole": "main",
            "quote": "A source-exact claim.", "claimIds": ["c1"], "sourceBeatIds": ["b1"],
            "sourceBeats": [{"beatId": "b1"}], "claimSpans": [{"claimId": "c1"}],
            "presentationOperations": ["archival_progression"],
            "primaryPresentationOperation": "archival_progression",
            "primaryMeaning": {"operation": "archival_progression", "job": "narrate_an_event"},
            "requiredMeanings": ["archival_progression"],
            "routeDisposition": {"templateEligible": template_eligible, "brollFallbackAvailable": True,
                                 "selectionAuthorized": False, "renderingAuthorized": False},
            "obligations": [{"intent": "Keep the claim scoped", "wouldBeALie": ["Overclaim"],
                             "withheld": ["Unsupported detail"]}],
            "continuity": [{"groupId": "g1"}], "values": [], "cohortRefs": [],
            "entityRefs": [{"entity": "person:test", "display": "required"}],
            "mediaNeeds": [], "cohortMediaNeeds": [], "dataNeeds": {"values": [], "cohortRefs": []},
            "quoteRequirements": {"requiredText": [], "attribution": [], "speakers": [{"role": "narrator"}]},
            "mustBePerceptible": [], "entities": {"displayEligible": ["person:test"]},
            "entityCount": 1, "templateAdmissions": [], "selectionAuthorized": False,
            "renderingAuthorized": False, "taskContractReceipt": {"version": "matching-task-projection@1"},
        }

    def test_conversion_preserves_canonical_task_without_local_reconstruction(self):
        projection = {"tasks": [self.task()]}
        tasks, requirements, preserved = subject._convert_projection(projection)
        self.assertEqual(tasks["tasks"][0], projection["tasks"][0])
        self.assertEqual(preserved["pkg.proposal.1"]["routeDisposition"]["templateEligible"], True)
        self.assertEqual(requirements["tasks"][0]["timingRequirement"]["status"],
                         "unresolved_human_timing_evidence_required")

    def test_named_entity_does_not_fabricate_media_requirement(self):
        _, requirements, _ = subject._convert_projection({"tasks": [self.task()]})
        media = requirements["tasks"][0]["mediaRequirements"]
        self.assertEqual(media["status"], "not_required")
        self.assertEqual(media["requiredEntities"], [])
        self.assertEqual(media["availabilityStatus"], "not_required")

    def test_canonical_multi_beat_contract_supplies_primary_batch_linkage(self):
        self.assertEqual(batch._primary_source_beat_id(self.task()), "b1")
        self.assertEqual(batch._primary_source_beat_id({"sourceBeatId": "legacy", "sourceBeatIds": ["new"]}), "legacy")
        self.assertIsNone(batch._primary_source_beat_id({}))

    def test_blind_review_query_uses_semantics_not_subject_specific_rules(self):
        candidate = {"fitAssessment": {"evidence": {"taskContract": {
            "primaryPresentationOperation": "archival_progression",
            "presentationOperations": ["archival_progression", "identity_reveal"],
            "job": "narrate_an_event",
        }}}}
        text = packet._query({"quote": "A source-exact claim.", "templateResult": {"candidates": [candidate]}})
        self.assertIn("A source-exact claim.", text)
        self.assertIn("archival_progression", text)
        self.assertIn("narrate_an_event", text)


if __name__ == "__main__":
    unittest.main()
