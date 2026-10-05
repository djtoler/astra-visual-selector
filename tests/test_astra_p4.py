"""P4 uses existing records only; no model, native render, or control inference."""
import copy
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from pipeline import visualtask_matching as matching
from pipeline import visualtask_batch_matching as batch

ROOT = Path(__file__).resolve().parents[1]

class P4CapabilityRepairs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool = {r['id']: r for r in matching.C.load(content_class='*')}

    def test_timeline_scope_is_chronology_only(self):
        records = [r for r in self.pool.values() if r.get('scope') == 'timelines']
        self.assertEqual(len(records), 2)
        contract = {'hasTypedValues': False}
        for record in records:
            self.assertTrue(matching._supports_operation('archival_progression', record, contract))
            for operation in matching.OPERATION_PRIORITY:
                if operation != 'archival_progression':
                    self.assertIsNone(matching._supports_operation(operation, record, contract))
            self.assertEqual(record['scope'], 'timelines')

    def test_corrections_do_not_mutate_observations_and_flag_contradiction(self):
        raw = {'demo': {'carries': ['identity'], 'staging': 'all_at_once', 'unclear': ['native_editability']}}
        original = copy.deepcopy(raw)
        result = matching.C.apply_capability_corrections(raw, {'demo': {'add': {'carries': ['absence']}, 'notCorrected': 'staging contradiction: reduction has no vocabulary'}})
        self.assertEqual(raw, original)
        self.assertIn('staging contradiction: reduction has no vocabulary', result['demo']['unclear'])
        self.assertEqual(result['demo']['staging'], 'all_at_once')

    def test_observed_declared_and_scope_sources_stay_distinct(self):
        raw = json.loads((ROOT / 'grammar/capability.json').read_text())
        record = self.pool['base-single-billboard']
        self.assertEqual(record['sources']['observedCapability']['sha256'], hashlib.sha256((ROOT / 'grammar/capability.json').read_bytes()).hexdigest())
        self.assertEqual(record['sources']['declaredCapacity']['axes'], {'heroes': 3, 'entities': 10})
        self.assertEqual(record['capability']['structure'], raw[record['id']]['structure'])
        self.assertEqual(record['sources']['verifiedControls'], 'unresolved')

    def test_missing_spatial_and_lyric_capabilities_stay_unknown(self):
        spatials = [r for r in self.pool.values() if r['id'] in {'catalog-gap-clean', 'topographic-cloud', 'hologram-stage', 'kendrick-red-stage-clean'}]
        self.assertEqual(len(spatials), 4)
        lyrics = [r for r in self.pool.values() if r.get('scope') == 'lyrics']
        self.assertEqual(len(lyrics), 7)
        for record in spatials + lyrics:
            self.assertIsNone(record['capability'])
        for record in spatials:
            self.assertIsNone(matching._supports_operation('comparison', record, {'hasTypedValues': False}))
        for record in lyrics:
            evidence = matching._supports_operation('lyric_presentation', record, {})
            self.assertIn('capability:unresolved', evidence)

    def test_effective_payload_cannot_invent_observed_source(self):
        effective = matching.C._capability()
        effective['catalog-gap-clean'] = {'structure': 'pair', 'carries': ['identity'], 'media_slots': 2}
        with patch.object(matching.C, '_capability', return_value=effective):
            record = next(r for r in matching.C.load(content_class='*') if r['id'] == 'catalog-gap-clean')
        self.assertIsNotNone(record['capability'])
        self.assertIsNone(record['sources']['observedCapability'])
        self.assertEqual(record['sources']['verifiedControls'], 'unresolved')

    def test_numeric_text_discovery_does_not_prove_qualitative_controls(self):
        record = copy.deepcopy(next(r for r in self.pool.values() if 'dropoff-carousels' in r['id'] and r['id'].endswith('review-002')))
        evidence = matching._supports_operation('relationship_intro', record, {'hasTypedValues': False})
        self.assertTrue(evidence)
        self.assertIn('numeric_text_controls:unresolved', evidence)
        record['capability']['carries'].append('magnitude')
        self.assertIsNone(matching._supports_operation('relationship_intro', record, {'hasTypedValues': False}))

    def test_qualitative_controls_and_staging_cannot_be_claimed_fit(self):
        requirements = {'mediaRequirements': {'requiredSlotCount': 0}, 'textRequirements': {'requiredFieldCount': 0}, 'dataRequirements': {}}
        comparison = {'compositionMappingStatus': 'verified', 'exactComposition': {'durationSeconds': 3}}
        candidate = {'candidateId': 'c', 'bindingProvenance': {'evidence': ['numeric_text_controls:unresolved']}}
        treatment = {'reviewState': 'editor_reviewed', 'verdict': 'native_fit'}
        result = batch._candidate_fit({}, requirements, candidate, comparison, None, treatment, {'capability': {}})
        self.assertEqual(result['verdict'], 'unresolved')
        candidate['bindingProvenance']['evidence'] = []
        result = batch._candidate_fit({}, requirements, candidate, comparison, None, treatment, {'capability': {'unclear': ['staging contradiction']}})
        self.assertEqual(result['verdict'], 'unresolved')
        self.assertFalse(treatment.get('renderingAuthorized', False))

    def test_stale_mapping_invalidates_fit_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'mapping.json'
            path.write_text('{}')
            artifact = {'sources': {'sceneMappings': {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}}, 'tasks': [{'taskId': 't', 'candidateComparisons': [{'candidateId': 'c', 'compositionMappingStatus': 'verified', 'exactComposition': {'durationSeconds': 3}}]}]}
            self.assertEqual(batch._comparison_index(artifact)[('t', 'c')]['compositionMappingStatus'], 'verified')
            path.write_text('{"changed":true}')
            stale = batch._comparison_index(artifact)[('t', 'c')]
            self.assertEqual(stale['projectEvidenceStatus'], 'stale_native_mapping_evidence')
            result = batch._candidate_fit({}, {}, {'candidateId': 'c'}, stale, None,
                                          {'reviewState': 'editor_reviewed', 'verdict': 'native_fit'}, None)
            self.assertEqual(result['verdict'], 'unresolved')
            self.assertEqual(artifact['tasks'][0]['candidateComparisons'][0]['compositionMappingStatus'], 'verified')

if __name__ == '__main__':
    unittest.main()
