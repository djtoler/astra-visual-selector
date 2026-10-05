import copy
import json
from pathlib import Path
import tempfile
import unittest

from pipeline import storypackage_splitter as subject
from pipeline import visualtask_split_proposals as provider

ROOT = Path(__file__).resolve().parents[1]


def claim(cid, text, *, entity="person:example", values=None, cohort=None):
    return {"claimId": cid, "beatId": "beat", "text": text, "span": {"start": 0, "len": len(text)},
            "lane": "factual", "entityRefs": [{"entity": entity, "display": "required", "mentioned": True}],
            "values": values or [], "cohortRefs": cohort or []}


def units(rows):
    cursor = 0
    for row in rows:
        row["span"] = {"start": cursor, "len": len(row["text"])}
        cursor += len(row["text"]) + 1
    text = " ".join(r["text"] for r in rows)
    beat = {"beatId": "beat", "claimIds": [r["claimId"] for r in rows],
            "narration": text, "span": {"start": 0, "len": len(text)}}
    result = subject._semantic_units(beat=beat, claim_ids=beat["claimIds"], claims={r["claimId"]: r for r in rows})
    return result, text


class P3SemanticTests(unittest.TestCase):
    def test_exact_frozen_rate_span(self):
        path = ROOT / "reports/matching-agent-evaluation-20261004/year-seventeen-regression/10-storypackage-adapter.json"
        adapter = json.loads(path.read_text())
        result = subject.build(adapter, source_path=path)
        rate = next(r for r in result["taskProposals"] if r["jobProposalId"] == "p-21-21b-rate")
        span = rate["proposalSpan"]
        self.assertEqual(rate["taskText"], adapter["script"]["text"][span["start"]:span["start"] + span["len"]])

    def test_duplicate_identity_does_not_become_plural_or_comparison(self):
        rows = [claim("one", "Example did more than before."), claim("two", "Example did more than before.")]
        ops = subject._presentation_operations(text="Example did more than before.", claim_rows=rows)
        self.assertNotIn("comparison", ops)
        many = rows + [claim("three", "Example continues.")]
        self.assertNotIn("item_sequence", subject._presentation_operations(text="Example continues.", claim_rows=many))
        for row in rows: row["values"] = [{"value": 10, "unit": "streams", "label": "plays"}]
        self.assertEqual(subject._derived_job(text="Example improved.", claim_rows=rows, operations=["data_explanation"]), "derived_quantity")

    def test_true_distinct_participant_comparison_survives(self):
        rows = [claim("one", "Example has more than Peer."), claim("two", "Peer has less.", entity="person:peer")]
        self.assertIn("comparison", subject._presentation_operations(text=rows[0]["text"], claim_rows=rows))

    def test_units_and_measure_roles_split_with_exact_coverage(self):
        for second in ({"value": 10, "unit": "streams/track", "label": "per track"},
                       {"value": 10, "unit": "streams", "label": "features", "basis": "feature role"}):
            rows = [claim("one", "Example has 10 lead streams.", values=[{"value": 10, "unit": "streams", "label": "lead", "basis": "lead role"}]),
                    claim("two", "Example has 10 more streams.", values=[second])]
            result, text = units(rows)
            self.assertEqual(len(result), 2)
            self.assertEqual("".join(r["text"] for r in result), text)

    def test_coherent_rank_cohort_keeps_single(self):
        cohort = [{"cohort": "group", "version": 1, "display": "required"}]
        rows = [claim("one", "The group has 10 streams.", values=[{"value": 10, "unit": "streams", "label": "daily"}], cohort=cohort),
                claim("two", "The group has 20 streams.", values=[{"value": 20, "unit": "streams", "label": "daily"}], cohort=cohort)]
        result, text = units(rows)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["text"], text)

    def test_lexical_counterprobes(self):
        probes = json.loads((ROOT / "reports/astra-root-cause/04-diagnostic-probes.json").read_text())["probes"]
        for probe in probes:
            if probe.get("kind") != "diagnostic_word_substitution": continue
            before = probe["originalInput"]
            after = probe["changedInput"]
            for field in ("text", "claim_rows"): self.assertIn(field, before)
            self.assertEqual(subject._presentation_operations(**before), subject._presentation_operations(**after), probe["traceId"])

    def test_source_span_mutations_and_unicode(self):
        text = "α A measured rate is 10 per unit. β"
        row = claim("c", text)
        adapter = {"storyHandoffReceipt": {"accepted": True}, "selectionAuthorized": False, "renderingAuthorized": False,
                   "story": {"storyId": "synthetic"}, "packageId": "synthetic@1", "claims": [row],
                   "beats": [{"beatId": "beat", "claimIds": ["c"], "order": 1, "narration": text,
                              "span": {"start": 0, "len": len(text)}, "speaker": {"role": "narrator"}}],
                   "script": {"text": text}, "jobProposals": [{"proposalId": "rate", "job": "derived_quantity", "claimIds": ["c"],
                              "span": {"start": 2, "len": len(text) - 4}, "provenance": {"source": "user", "reviewState": "approved"}}]}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "adapter.json"; path.write_text(json.dumps(adapter))
            self.assertEqual(subject.build(adapter, source_path=path)["taskProposals"][0]["taskText"], text[2:-2])
            for span in ({"start": -1, "len": 1}, {"start": 0, "len": 1000}, {"start": True, "len": 2}):
                broken = copy.deepcopy(adapter); broken["jobProposals"][0]["span"] = span
                with self.subTest(span=span), self.assertRaises(ValueError): subject.build(broken, source_path=path)

    def test_provider_cannot_change_facts_select_or_erase_unknown(self):
        from tests.test_visualtask_split_proposals import ProviderIndependentSemanticSplitProposals as fixtures
        fixtures.setUpClass()
        for mutation in ("fact", "selection", "unknown"):
            response = copy.deepcopy(fixtures.response)
            task = response["beatProposals"][0]["tasks"][0]
            if mutation == "fact": task["quote"] += " Invented."
            elif mutation == "selection": task["templateId"] = "a selected template"
            else:
                for task in response["beatProposals"][0]["tasks"]: task["dataRequirementRefs"] = []
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): provider.validate_response(response, fixtures.request)

    def test_disjoint_representations_do_not_merge(self):
        rows = [claim("one", "Example has one role."), claim("two", "Example has another role.")]
        rows[0]["entityRefs"][0]["representedBy"] = ["media"]
        rows[1]["entityRefs"][0]["representedBy"] = ["text"]
        result, text = units(rows)
        self.assertEqual(len(result), 2)
        self.assertEqual("".join(r["text"] for r in result), text)

    def test_source_unknown_and_authored_relationship_survive(self):
        path = ROOT / "reports/matching-agent-evaluation-20261004/year-seventeen-regression/10-storypackage-adapter.json"
        adapter = json.loads(path.read_text())
        result = subject.build(adapter, source_path=path)
        unknown = {r["claimId"] for r in adapter["claims"] if r.get("status") == "unverified"}
        gaps = {r["claim"] for r in result["gaps"] if r["gap"] == "source_fact_unverified"}
        self.assertEqual(unknown, gaps)
        overlap = [r for r in result["taskProposals"] if r["job"] == "intersection_of_sets"]
        self.assertTrue(overlap)
        self.assertTrue(all(r["primaryPresentationOperation"] == "data_explanation" for r in overlap))
        self.assertFalse(result["selectionAuthorized"])
        self.assertFalse(result["renderingAuthorized"])

    def test_supported_provider_conversion_preserves_cohort_and_rationale(self):
        from pipeline import heldout_matching_integration as consumer
        from tests.test_visualtask_split_proposals import ProviderIndependentSemanticSplitProposals as fixtures
        fixtures.setUpClass()
        inputs = copy.deepcopy(fixtures.request["input"])
        inputs["rosterContext"]["cohorts"] = [{"id": "group", "version": "1", "label": "Source group", "memberEntityRefs": ["wetland-north"]}]
        inputs["storyPackage"]["beats"][0]["cohortRefs"] = ["group"]
        with tempfile.TemporaryDirectory() as folder:
            paths = {}
            for key, value in inputs.items():
                paths[key] = Path(folder) / (key + ".json")
                paths[key].write_text(provider.dumps(value))
            request = provider.prepare_request_from_files(paths["storyPackage"], paths["taskVocabulary"], paths["rosterContext"], paths["editorContext"])
            response = copy.deepcopy(fixtures.response)
            response["requestSha256"] = provider.sha256_bytes(provider.dumps(request).encode())
            proposed = response["beatProposals"][0]["tasks"][0]
            proposed["cohortRefs"] = ["group"]
            tasks, requirements, evidence = consumer._convert(request, response)
        self.assertEqual(tasks["tasks"][0]["entities"]["cohorts"], ["group"])
        provenance = tasks["tasks"][0]["semanticSplitProvenance"]
        self.assertEqual(provenance["reason"], proposed["reason"])
        self.assertEqual(provenance["rationale"], response["beatProposals"][0]["rationale"])
        self.assertEqual(evidence["requirementPreservation"]["preservedReferenceCounts"]["cohorts"], 1)


if __name__ == "__main__": unittest.main()
