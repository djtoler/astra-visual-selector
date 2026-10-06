"""P6 uses the real P5 synthetic source/treatment controls, never mocked fit truth."""
import copy
import inspect
import os
import shutil
import subprocess
import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tests import test_astra_p5 as p5
from pipeline import visualtask_batch_matching as batch
from pipeline import storypackage_candidate_gallery as gallery
from pipeline import focused_review_queue as queue
from pipeline import focused_candidate_diversity as diversity
from pipeline import focused_review_reconciliation as feedback

class P6SharedLedgerTests(unittest.TestCase):
    save = p5.P5TreatmentReconciliation.save

    def setUp(self):
        p5.P5TreatmentReconciliation.setUp(self)
        self.pool.extend([{**copy.deepcopy(self.pool[1]),'id':'example-pack--scene-003'},
                          {**copy.deepcopy(self.pool[1]),'id':'other-pack--scene-001'}])
        self.values['bindings']={t['job']:[{'id':r['id']} for r in self.pool] for t in self.values['visualTasks']['tasks']}
        self.task_id=self.values['visualTasks']['tasks'][0]['id']
        exacts=[{'id':i+1,'path':'Control/'+str(i),'durationSeconds':2.0,'frameRate':30.0,
                 'maxSimultaneouslyEnabledDirectInputs':1,'maxSimultaneouslyEnabledRecursiveVisualInputs':1,
                 'maxSimultaneouslyEnabledRecursiveTextFields':0 if i==0 else 2} for i in range(len(self.pool))]
        sources={}
        for name,data in [('sceneMappings',{'mappings':[{'sceneId':r['id'],'projectId':'control','status':'verified','compositionId':e['id']} for r,e in zip(self.pool,exacts)]}),
                          ('technicalIndex',{'projects':[{'id':'control','compositions':exacts,'sourceUnchanged':True,'resultStatus':'two_pass_exact_agreement','sourceProjectSha256':'a'*64}]})]:
            path=self.root/(name+'.json');path.write_text(json.dumps(data));sources[name]=batch._source(path)
        self.save()
        sources.update(visualTasks=batch._source(self.root/'visualTasks.json'),taskRequirements=batch._source(self.root/'technicalRequirements.json'))
        self.values['technicalComparison']['sources']=sources
        self.values['technicalComparison']['tasks']=[{'taskId':self.task_id,'candidateComparisons':[
            {'candidateId':r['id'],'projectId':'control','compositionMappingStatus':'verified','projectEvidenceStatus':'two_pass_exact_agreement','exactComposition':e} for r,e in zip(self.pool[:3],exacts[:3])]}]
        self.save(); initial=batch.build(self.request)
        bindings={k:v for k,v in initial['sources'].items() if k not in {'request','treatmentAssessments'}}
        self.values['treatmentAssessments']['assessments']=[{'taskId':self.task_id,'candidateId':r['candidateId'],
            'reviewState':'editor_reviewed','decision':'approved_treatment_requirements','verdict':'native_fit','sources':bindings,
            'approvedAdjustments':[],'templateAssessment':{'satisfied':[{'requirement':d['requirementId'],'evidence':'Synthetic control'} for d in r['fitAssessment']['evidence']['requirements']]}}
            for r in initial['tasks'][0]['templateResult']['candidates'][1:3]]
        self.save(); self.ledger=batch.build(self.request)
        self.ledger_path=self.root/'ledger.json';self.ledger_path.write_text(batch.dumps(self.ledger))
        self.ordering={'displayLimit':1,'candidateRelevance':{self.task_id:{r['id']:0 for r in self.pool}},'taskIds':[t['taskId'] for t in self.ledger['tasks']], 'familyQuota':1}
        self.order_path=self.root/'ordering.json'; self.gallery_path=self.root/'gallery.json'

    def view(self):
        self.assertIn('ledger_path',inspect.signature(gallery.build).parameters,'P6 gallery must consume the shared ledger')
        self.order_path.write_text(batch.dumps(self.ordering))
        result=gallery.build(ledger_path=self.ledger_path,ordering_path=self.order_path)
        self.gallery_path.write_text(batch.dumps(result));return result

    def test_filters_before_score_and_keeps_overflow(self):
        self.ordering['candidateRelevance'][self.task_id][self.pool[0]['id']]=1e100
        v=self.view(); row=v['tasks'][0]
        self.assertEqual([c['candidateId'] for c in row['candidates']],[self.pool[1]['id']])
        self.assertEqual(row['omittedCandidateIds'],[self.pool[2]['id']])
        self.assertEqual(row['counts'],{'pool':4,'eligible':2,'incompatible':1,'unresolved':1,'displayed':1,'omitted':1})
        self.assertEqual(row['templateResult'],self.ledger['tasks'][0]['templateResult'])
        self.assertFalse(v['selectionAuthorized']);self.assertFalse(v['renderingAuthorized'])

    def test_family_quota_does_not_drop_valid_sibling(self):
        self.ordering['displayLimit']=20
        row=self.view()['tasks'][0]
        self.assertEqual(len(row['candidates']),2)
        self.assertEqual(len(row['variantGroups'][0]['members']),3)

    def test_unresolved_flags_and_provenance_round_trip(self):
        v=self.view(); row=v['tasks'][0]
        original=self.ledger['tasks'][0]['templateResult']['candidates'][-1]
        self.assertEqual(row['unresolvedCandidates'],[original])
        self.assertTrue(original['fitAssessment']['evidence']['nativeFitUnknown'])
        qpath=self.root/'queue.json';q=queue.build(self.gallery_path);qpath.write_text(batch.dumps(q))
        focused=diversity.build(self.gallery_path,qpath)
        selected=next(r for r in focused['tasks'] if r['taskId']==self.task_id)
        self.assertEqual(selected,row)
        self.assertFalse(q['humanReviewed']);self.assertEqual(q['ledgerTaskReferences'][self.task_id],batch._digest(self.ledger['tasks'][0]))

    def test_feedback_exact_identity_and_hash_bound(self):
        v=self.view(); q=queue.build(self.gallery_path);qpath=self.root/'queue.json';qpath.write_text(batch.dumps(q))
        decisions={t+'::'+c:{'id':t+'::'+c,'taskId':t,'candidateId':c,'status':'unreviewed','comment':'Needs inspection'}
                   for t,c in [(r['taskId'],(r['candidates'] or r['unresolvedCandidates'])[0]['candidateId']) for r in v['tasks'] if r['taskId'] in q['taskIds']]}
        review={'packageId':v['packageId'],'sourceGallerySha256':q['sourceGallerySha256'],'decisions':decisions,'selectionAuthorized':False,'renderingAuthorized':False}
        path=self.root/'review.json';path.write_text(batch.dumps(review))
        out=feedback.build(qpath,path,gallery_path=self.gallery_path)
        self.assertTrue(all(r['status']=='unreviewed' for r in out['tasks']))
        feedback.validate(out,qpath,path,gallery_path=self.gallery_path)
        tampered=copy.deepcopy(out);tampered['tasks'][0]['status']='acceptable'
        with self.assertRaises(ValueError):feedback.validate(tampered,qpath,path,gallery_path=self.gallery_path)
        extra=self.task_id+'::'+self.pool[2]['id']
        multi=copy.deepcopy(review);multi['decisions'][extra]={'id':extra,'taskId':self.task_id,'candidateId':self.pool[2]['id'],'status':'unreviewed','comment':''}
        path.write_text(batch.dumps(multi));roundtrip=feedback.build(qpath,path,gallery_path=self.gallery_path)
        self.assertFalse(roundtrip['humanReviewed'])
        self.assertEqual(len(roundtrip['tasks']),len(out['tasks'])+1)
        for mutation in ('hash','candidate','task','key','package','approval','incompatible'):
            bad=copy.deepcopy(review);key=next(iter(bad['decisions']))
            if mutation=='hash':bad['sourceGallerySha256']='0'*64
            elif mutation=='candidate':bad['decisions'][key]['candidateId']='invented'
            elif mutation=='task':bad['decisions'][key]['taskId']='invented'
            elif mutation=='key':bad['decisions'][key]['id']='invented'
            elif mutation=='package':bad['packageId']='invented'
            elif mutation=='approval':bad['selectionAuthorized']=True
            else:
                decision=bad['decisions'].pop(key);decision['candidateId']=self.pool[0]['id'];decision['id']=decision['taskId']+'::'+decision['candidateId'];bad['decisions'][decision['id']]=decision
            path.write_text(batch.dumps(bad))
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):feedback.build(qpath,path,gallery_path=self.gallery_path)

    def test_display_mutations_fail_even_when_rehashed(self):
        v=self.view()
        for mutation in ('route','catalog','row','score','limit','family','display','sequence','ledger'):
            bad=copy.deepcopy(v);row=bad['tasks'][0]
            if mutation=='route':row['templateResult']['candidates'][0]['fitAssessment']['evidence']['taskContract']['routeDisposition']={'templateEligible':False}
            elif mutation=='catalog':bad['consumerFingerprints']['templatePool']='0'*64
            elif mutation=='row':row['quote']='Invented'
            elif mutation=='score':row['candidateRelevance'][self.pool[1]['id']]=9
            elif mutation=='limit':row['displayLimit']=99
            elif mutation=='family':row['familyOrder'].reverse()
            elif mutation=='display':row['candidates']=[]
            elif mutation=='sequence':bad['reviewerSequence'].reverse()
            else:bad['sources']['ledger']['sha256']='0'*64
            bad['contractEnforcementReceipt']['candidateDisplay']['bodySha256']=gallery._display_digest(bad)
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):gallery.validate(bad)

    def test_persisted_order_input_and_ledger_freshness(self):
        v=self.view();self.ordering['displayLimit']=4;self.order_path.write_text(batch.dumps(self.ordering))
        with self.assertRaises(ValueError):gallery.validate(v)
        self.order_path.write_text(batch.dumps({**self.ordering,'displayLimit':1}))
        self.ledger_path.write_text('{}')
        with self.assertRaises(ValueError):gallery.validate(v)

    def test_ties_independent_of_input_candidate_order(self):
        first=self.view()
        # P5 replay forbids reordered truth, so stable tie behavior is directly
        # tested on the ordering helper while publication consumes exact P5 order.
        rows=self.ledger['tasks'][0]['templateResult']['candidates']
        a=gallery._review_order(rows,{})
        b=gallery._review_order(list(reversed(rows)),{})
        self.assertEqual(a,b)
        self.assertEqual(self.view(),first)

    def test_zero_limit_and_explicit_no_template_route(self):
        self.ordering['displayLimit']=0;v=self.view();self.assertFalse(v['tasks'][0]['candidates'])
        self.assertEqual(len(v['tasks'][0]['omittedCandidateIds']),2)
        task=self.values['visualTasks']['tasks'][0];task['routeDisposition']={'templateEligible':False,'route':'broll'}
        self.save();self.ledger=batch.build(self.request);self.ledger_path.write_text(batch.dumps(self.ledger))
        self.ordering['candidateRelevance'][self.task_id]={}
        row=self.view()['tasks'][0];self.assertEqual(row['counts']['pool'],0);self.assertFalse(row['candidates'])
        self.assertEqual(row['templateResult'],self.ledger['tasks'][0]['templateResult'])

    def test_one_verified_option_needs_no_padding_or_threshold(self):
        self.values['treatmentAssessments']['assessments']=self.values['treatmentAssessments']['assessments'][:1]
        self.save();self.ledger=batch.build(self.request);self.ledger_path.write_text(batch.dumps(self.ledger))
        self.ordering['displayLimit']=20
        self.ordering['candidateRelevance'][self.task_id][self.pool[1]['id']]=-1e99
        row=self.view()['tasks'][0]
        self.assertEqual(row['counts']['eligible'],1);self.assertEqual(row['candidateCount'],1)

    def test_bad_limits_scores_or_sequence_rejected(self):
        for mutation in ('negative','float','bool','nan','sequence'):
            with self.subTest(mutation=mutation):
                original=copy.deepcopy(self.ordering)
                if mutation=='negative':self.ordering['displayLimit']=-1
                elif mutation=='float':self.ordering['displayLimit']=1.5
                elif mutation=='bool':self.ordering['displayLimit']=True
                elif mutation=='nan':self.ordering['candidateRelevance'][self.task_id][self.pool[1]['id']]=float('nan')
                else:self.ordering['taskIds']=['invented']
                with self.assertRaises(ValueError):self.view()
                self.ordering=original

    def test_sampling_mutation_does_not_create_review_truth(self):
        self.view();q=queue.build(self.gallery_path)
        q['representatives'][0]['representedTaskIds'].append('invented')
        with self.assertRaises(ValueError):queue.validate(q,self.gallery_path)

class P6ProcessReplayTests(unittest.TestCase):
    def test_identical_canonical_display_and_queue_across_roots_and_processes(self):
        self.assertIn('ledger_path',inspect.signature(gallery.build).parameters)
        runtime = Path(__file__).resolve().parents[1]
        program = """
import gzip,json,sys
from pathlib import Path
from unittest.mock import patch
from pipeline import visualtask_batch_matching as b
from pipeline import storypackage_candidate_gallery as g
from pipeline import focused_review_queue as q
root,runtime=map(Path,sys.argv[1:])
reports=runtime/'reports/astra-p5'
templates=json.loads((reports/'effective-template-pool.json').read_text())
media=json.loads((reports/'effective-media-pool.json').read_text())
with patch.object(b,'ROOT',root),patch.object(b.matching.C,'load',return_value=templates),patch.object(b.matching.M,'load',return_value=media):
    ledger=b.build(root/'tests/fixtures/visualtask_batch_matching/synthetic-request.json')
    (root/'ledger.json').write_text(b.dumps(ledger))
    (root/'ordering.json').write_text(b.dumps({'displayLimit':5,'candidateRelevance':{},'taskIds':[r['taskId'] for r in ledger['tasks']]}))
    view=g.build(ledger_path=root/'ledger.json',ordering_path=root/'ordering.json')
    g.validate(view)
    (root/'gallery.json').write_text(b.dumps(view))
    focused=q.build(root/'gallery.json')
    print(json.dumps({'ledger':b._digest(ledger),'gallery':b._digest(view),'queue':b._digest(focused),'receipt':view['contractEnforcementReceipt']['candidateDisplay']['bodySha256']}))
"""
        with tempfile.TemporaryDirectory() as folder:
            results=[]
            for name in ('first-checkout','second-checkout'):
                root=Path(folder)/name;root.mkdir()
                shutil.copytree(runtime/'tests/fixtures/visualtask_batch_matching',root/'tests/fixtures/visualtask_batch_matching')
                shutil.copytree(runtime/'grammar',root/'grammar')
                result=subprocess.check_output([sys.executable,'-c',program,str(root),str(runtime)],cwd=root,
                    env={**os.environ,'PYTHONPATH':str(runtime)},text=True)
                results.append(json.loads(result))
            self.assertEqual(results[0],results[1])
