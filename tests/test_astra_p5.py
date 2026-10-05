"""P5 contract tests use existing batch fixtures and synthetic catalog controls."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from pipeline import visualtask_batch_matching as batch
from pipeline import visualtask_matching as matching

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / 'tests/fixtures/visualtask_batch_matching'

class P5TreatmentReconciliation(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        request = json.loads((FIX / 'synthetic-request.json').read_text())
        self.values = {}
        for key, path in request['sources'].items():
            self.values[key] = json.loads((FIX / path).resolve().read_text())
        task = self.values['visualTasks']['tasks'][0]
        task.update(presentationOperations=['concept_statement', 'data_explanation'],
                    primaryPresentationOperation='concept_statement',
                    requiredMeanings=['concept_statement', 'data_explanation'],
                    obligations=[{'intent':'Explain the specific work', 'mustBePerceptible':['A named work']}],
                    mediaNeeds=[{'work':'A named work', 'framing':'complete', 'aspect':'16:9', 'cutout':False, 'static':True}])
        text = self.values['technicalRequirements']['tasks'][0]['textRequirements']
        text['minimumDwellSeconds'] = 2
        self.pool = [{ 'id':'example-pack--scene-001', 'description':'single statement',
                       'capability':{'structure':'single','carries':[],'readable':['statement'],
                                     'text_slots':0,'media_slots':1}},
                     { 'id':'example-pack--scene-002', 'description':'alternate statement',
                       'capability':{'structure':'single','carries':[],'readable':['statement'],
                                     'text_slots':2,'media_slots':1}}]
        self.values['bindings'] = {t['job']:[{'id':r['id']} for r in self.pool]
                                   for t in self.values['visualTasks']['tasks']}
        request['sources'] = {key:key+'.json' for key in self.values}
        self.request = self.root/'request.json'
        self.request.write_text(json.dumps(request))
        self.save()
        self.addCleanup(patch.stopall)
        patch.object(matching.C, 'load', return_value=self.pool).start()
        self.media_pool={}
        patch.object(matching.M, 'load', return_value=self.media_pool).start()

    def save(self):
        for key,value in self.values.items():
            (self.root/(key+'.json')).write_text(json.dumps(value))

    def build(self):
        return batch.build(self.request)

    def ledger(self, artifact):
        rows = artifact['tasks'][0]['templateResult']['candidates']
        self.assertEqual({r['candidateId'] for r in rows},{r['id'] for r in self.pool})
        evidence=rows[0]['fitAssessment']['evidence']
        self.assertTrue(evidence.get('requirements'), 'missing requirement reconciliation')
        return rows, evidence

    def test_all_variants_precede_family_reduction(self):
        with patch.object(matching.C,'diversify', wraps=matching.C.diversify) as reducer:
            artifact=self.build()
        self.ledger(artifact)
        reducer.assert_not_called()

    def test_every_duty_is_explicit_and_secondary_cannot_admit_fit(self):
        rows, evidence=self.ledger(self.build())
        duties=evidence['requirements']
        self.assertTrue(all(r['status'] in {'supported','conflict','unknown'} for r in duties))
        self.assertTrue(any(r['value']=='data_explanation' and r['status']!='supported' for r in duties))
        self.assertTrue(all(r['fitAssessment']['verdict']!='native_fit' for r in rows))

    def test_named_work_slot_framing_and_dwell_are_bound(self):
        _, evidence=self.ledger(self.build())
        values=json.dumps(evidence['requirements'])
        for word in ('A named work','framing','aspect','cutout','static','requiredSlotCount','minimumDwellSeconds'):
            self.assertIn(word,values)
        self.assertIn('permittedAdjustmentPlan',evidence)

    def test_missing_assets_do_not_become_template_conflicts(self):
        artifact=self.build(); self.ledger(artifact)
        host=artifact['tasks'][1]
        self.assertEqual(host['mediaResult']['availabilityVerdict'],'unavailable')
        self.assertTrue(host['mediaResult']['gaps'])
        self.assertTrue(all(c['fitAssessment']['verdict']=='unresolved'
                            for c in host['templateResult']['candidates']))

    def test_native_unknown_never_exhausts_or_authorizes(self):
        artifact=self.build(); rows,_=self.ledger(artifact)
        self.assertTrue(all(r['fitAssessment']['verdict']=='unresolved' for r in rows))
        self.assertFalse(artifact['selectionAuthorized']); self.assertFalse(artifact['renderingAuthorized'])
        self.assertFalse(artifact.get('fitValidated',False))

    def test_omitted_duty_or_mutated_adjustment_blocks_publication(self):
        original=self.build(); self.ledger(original)
        for change in ('duty','adjustment'):
            broken=copy.deepcopy(original)
            evidence=broken['tasks'][0]['templateResult']['candidates'][0]['fitAssessment']['evidence']
            if change=='duty': evidence['requirements'].pop()
            else: evidence['permittedAdjustmentPlan']['approvedAdjustments']=['custom_rebuild']
            with self.subTest(change=change), self.assertRaises(ValueError):
                batch.validate(broken,verify_sources=False)

    def test_missing_or_reordered_receipt_blocks_publication(self):
        original=self.build(); self.ledger(original)
        for change in ('missing','order','truncation'):
            broken=copy.deepcopy(original)
            receipt=broken['contractEnforcementReceipt'].get('candidateReconciliation')
            self.assertIsNotNone(receipt)
            if change=='missing': del broken['contractEnforcementReceipt']['candidateReconciliation']
            elif change=='order': receipt['stages'].reverse()
            else: broken['tasks'][0]['templateResult']['candidates'].pop()
            with self.subTest(change=change),self.assertRaises(ValueError): batch.validate(broken,verify_sources=False)

    def test_ledger_cannot_be_relabelled_as_validated_fit_choices(self):
        artifact=self.build(); self.ledger(artifact)
        artifact['fitValidated']=True
        with self.assertRaisesRegex(ValueError,'cannot certify'):
            batch.validate(artifact,verify_sources=False)

    def test_stale_task_treatment_data_media_and_mapping_block_publication(self):
        original=self.build(); self.ledger(original)
        for key in ('visualTasks','treatmentAssessments','technicalRequirements','technicalComparison','bindings'):
            path=self.root/(key+'.json'); old=path.read_text()
            path.write_text(old+' ')
            with self.subTest(source=key),self.assertRaises(ValueError): batch.validate(original)
            path.write_text(old)
        self.pool[1]['capability']['text_slots']=100
        with self.assertRaises(ValueError): batch.validate(original)

    def test_rehashed_duty_omission_still_fails_coverage(self):
        artifact=self.build(); self.ledger(artifact)
        artifact['tasks'][0]['templateResult']['candidates'][0]['fitAssessment']['evidence']['requirements'].pop()
        artifact['contractEnforcementReceipt']['candidateReconciliation']['bodySha256']=batch._digest(batch._reconciliation_body(artifact))
        with self.assertRaisesRegex(ValueError,'duty/source coverage'):
            batch.validate(artifact,verify_sources=False)

    def test_current_native_capacity_conflict_does_not_suppress_supported_sibling(self):
        task_id=self.values['visualTasks']['tasks'][0]['id']
        exacts=[]
        for index,record in enumerate(self.pool):
            exacts.append({'id':index+1,'path':'Synthetic/Statement '+str(index), 'durationSeconds':2.0,
                           'frameRate':30.0,'maxSimultaneouslyEnabledDirectInputs':1,
                           'maxSimultaneouslyEnabledRecursiveVisualInputs':1,
                           'maxSimultaneouslyEnabledRecursiveTextFields':index*2})
        mappings={'mappings':[{'sceneId':r['id'],'projectId':'synthetic-project','status':'verified',
                              'compositionId':e['id']} for r,e in zip(self.pool,exacts)]}
        native={'projects':[{'id':'synthetic-project','compositions':exacts,'sourceUnchanged':True,
                             'resultStatus':'two_pass_exact_agreement','sourceProjectSha256':'a'*64}]}
        sources={}
        for name,data in (('sceneMappings',mappings),('technicalIndex',native)):
            path=self.root/(name+'.json'); path.write_text(json.dumps(data))
            sources[name]=batch._source(path)
        sources['visualTasks']=batch._source(self.root/'visualTasks.json')
        sources['taskRequirements']=batch._source(self.root/'technicalRequirements.json')
        self.values['technicalComparison']['sources']=sources
        self.values['technicalComparison']['tasks']=[{'taskId':task_id,'candidateComparisons':[
            {'candidateId':record['id'],'projectId':'synthetic-project','compositionMappingStatus':'verified',
             'projectEvidenceStatus':'two_pass_exact_agreement','exactComposition':exact}
            for record,exact in zip(self.pool,exacts)]}]
        self.save(); artifact=self.build(); rows,_=self.ledger(artifact)
        first,second=[r['fitAssessment'] for r in rows]
        self.assertEqual(first['verdict'],'incompatible')
        self.assertTrue(any(r['requirementId']=='textRequirements.requiredFieldCount' and r['status']=='conflict'
                            for r in first['evidence']['requirements']))
        self.assertEqual(second['verdict'],'unresolved')
        self.assertTrue(any(r['requirementId']=='textRequirements.requiredFieldCount' and r['status']=='supported'
                            for r in second['evidence']['requirements']))
        # A complete, source-bound synthetic treatment can support the sibling.
        # This is a validator control, not a native-quality claim about real media.
        bindings={k:v for k,v in artifact['sources'].items() if k not in {'request','treatmentAssessments'}}
        duties=second['evidence']['requirements']
        self.values['treatmentAssessments']['assessments']=[{'taskId':task_id,'candidateId':self.pool[1]['id'],
            'reviewState':'editor_reviewed','decision':'approved_treatment_requirements','verdict':'native_fit',
            'sources':bindings,'approvedAdjustments':[], 'templateAssessment':{'satisfied':[
                {'requirement':r['requirementId'],'evidence':'Synthetic source-bound control for '+r['requirementId']} for r in duties]}}]
        self.save(); approved=self.build()
        assessed={r['candidateId']:r['fitAssessment'] for r in approved['tasks'][0]['templateResult']['candidates']}
        self.assertEqual(assessed[self.pool[1]['id']]['verdict'],'native_fit')
        self.assertEqual(assessed[self.pool[0]['id']]['verdict'],'incompatible')
        self.assertFalse(approved['selectionAuthorized']); self.assertFalse(approved['renderingAuthorized'])
        self.values['treatmentAssessments']['assessments'][0]['sources']['technicalRequirements']['sha256']='0'*64
        self.save(); unbound=self.build()
        self.assertEqual(unbound['tasks'][0]['templateResult']['candidates'][1]['fitAssessment']['verdict'],'unresolved')
        # Changing the measured source, even while retaining the comparison, must
        # invalidate publication and return unknown in a fresh reconciliation.
        path=self.root/'technicalIndex.json'; path.write_text('{}')
        with self.assertRaises(ValueError): batch.validate(artifact)
        fresh=self.build(); self.assertTrue(all(r['fitAssessment']['evidence']['nativeFitUnknown']
                                               for r in fresh['tasks'][0]['templateResult']['candidates']))

    def test_canonical_projection_is_not_locally_reconstructed(self):
        from tests.test_astra_p2 import P2ProjectionTests
        projected=next(row for row in P2ProjectionTests().projection()['tasks'] if row['routeDisposition']['templateEligible'])
        catalog=json.loads((ROOT/'reports/astra-p5/effective-template-pool.json').read_text())
        contract=matching.presentation_contract(projected)
        self.pool[:]=[row for row in catalog if matching._supports_operation(projected['primaryPresentationOperation'],row,contract)][:2]
        self.assertTrue(self.pool)
        self.values['visualTasks']['tasks'][0]=projected
        self.values['technicalRequirements']['tasks'][0]['taskId']=projected['id']
        self.values['technicalComparison']['tasks']=[]
        self.values['treatmentAssessments']['assessments']=[]
        self.save(); artifact=self.build()
        self.assertTrue(artifact['tasks'][0]['templateResult']['candidates'])
        for row in artifact['tasks'][0]['templateResult']['candidates']:
            self.assertEqual(row['fitAssessment']['evidence']['taskContract']['taskContractReceipt'], projected['taskContractReceipt'])
        self.values['visualTasks']['tasks'][0]['quote']='Invented meaning'
        self.save()
        with self.assertRaises(ValueError): self.build()

    def test_data_value_and_nested_source_mutations_fail_closed(self):
        from pipeline.storypackage_data_assignment import _field_digest
        measured=self.root/'measured.csv'; measured.write_text('item,amount\nexample,0\n')
        source=batch._source(measured)
        field={'fieldId':'measured-zero','value':0,'unit':'units','encodings':['exact'],
               'receipt':{'source':'measured','sourcePath':source['path'],'sourceSha256':source['sha256'],
                          'selector':{'item':'example'},'columns':['amount'],'transform':'exact CSV numeric value'}}
        field['fieldSha256']=_field_digest(field)
        tid=self.values['visualTasks']['tasks'][0]['id']
        self.values['technicalRequirements']['tasks'][0]['dataRequirements']['requiredEncodings']=['exact']
        self.values['technicalRequirements']['tasks'][0]['dataRequirements']['status']='required'
        self.values['dataAssignments']={'schemaVersion':1,'dataHandoffComplete':True,'selectionAuthorized':False,
            'renderingAuthorized':False,'sources':{'measured':source},
            'assignments':[{'taskId':tid,'status':'resolved','gaps':[],'typedFields':[field]}]}
        request=json.loads(self.request.read_text());request['sources']['dataAssignments']='dataAssignments.json'
        self.request.write_text(json.dumps(request)); self.save()
        artifact=self.build(); self.ledger(artifact)
        field['value']=1; self.save()
        with self.assertRaises(ValueError): self.build()
        field['value']=0; self.save(); measured.write_text('item,amount\nexample,9\n')
        with self.assertRaises(ValueError): batch.validate(artifact)

    def test_media_body_mutation_invalidates_even_when_asset_ids_do_not_change(self):
        asset=next(iter(json.loads((ROOT/'reports/astra-p5/effective-media-pool.json').read_text()).values()))
        self.media_pool[asset['id']]=asset
        artifact=self.build(); self.ledger(artifact)
        self.media_pool[asset['id']]['framing']='changed source metadata'
        with self.assertRaises(ValueError): batch.validate(artifact)

    def test_existing_technical_index_shape_is_consumed_without_a_replacement_schema(self):
        comparison=json.loads((ROOT/'reports/visualtask-ae-spec-comparison.json').read_text())
        # Exercise the real measured-index shape with its missing optional window
        # and spec dependencies removed. This is a parser control, not evidence
        # that those removed dependencies are resolved for publication.
        for key in ('sceneWindowCapacities','specLinks'):
            comparison['sources'].pop(key,None)
        task_sources={'visualTasks':batch._source(ROOT/'grammar/visual-tasks.json'),
                      'technicalRequirements':batch._source(ROOT/'grammar/visual-task-technical-requirements.json')}
        indexed=batch._comparison_index(comparison,task_sources)
        self.assertTrue(indexed)
        self.assertTrue(all(type(row['nativeSourceVerified']) is bool for row in indexed.values()))

    def test_stale_native_mapping_remains_unknown(self):
        original=self.build(); self.ledger(original)
        self.values['technicalComparison']['sources']={'sceneMappings':{'path':str(self.root/'absent.json'),'sha256':'0'*64}}
        self.save(); artifact=self.build(); rows,_=self.ledger(artifact)
        self.assertTrue(all(r['fitAssessment']['verdict']=='unresolved' for r in rows))

if __name__=='__main__': unittest.main()
