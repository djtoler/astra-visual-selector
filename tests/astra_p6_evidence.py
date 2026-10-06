"""Strict P6 replay using accepted P5 ledgers and the existing review pipeline."""
import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from pipeline import visualtask_batch_matching as batch
from pipeline import storypackage_candidate_gallery as gallery
from pipeline import focused_review_queue as queue
from pipeline import focused_candidate_diversity as diversity
REPORTS=ROOT/'reports/astra-p6'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def persist(path,value,write):
    encoded=batch.dumps(value).encode()
    data=gzip.compress(encoded,mtime=0) if path.suffix=='.gz' else encoded
    if write:path.write_bytes(data)
    elif path.read_bytes()!=data:raise ValueError('P6 artifact does not replay byte-for-byte: '+path.name)
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'canonicalSha256':hashlib.sha256(encoded).hexdigest()}

def run(write=False):
    p5=ROOT/'reports/astra-p5'
    templates=json.loads((p5/'effective-template-pool.json').read_text())
    media=json.loads((p5/'effective-media-pool.json').read_text())
    results=[]
    with patch.object(batch.matching.C,'load',return_value=templates),patch.object(batch.matching.M,'load',return_value=media):
        for name in ('current','synthetic'):
            ledger_path=p5/(name+'-ledger.json.gz');ledger=gallery._ledger_read(ledger_path)
            ordering={'displayLimit':16,'candidateRelevance':{},'taskIds':[r['taskId'] for r in ledger['tasks']]}
            order_path=REPORTS/(name+'-ordering.json');persist(order_path,ordering,write)
            view=gallery.build(ledger_path=ledger_path,ordering_path=order_path)
            view_path=REPORTS/(name+'-gallery.json.gz');view_binding=persist(view_path,view,write)
            focused_queue=queue.build(view_path)
            queue_path=REPORTS/(name+'-focused-queue.json');queue_binding=persist(queue_path,focused_queue,write)
            focused=diversity.build(view_path,queue_path)
            focused_binding=persist(REPORTS/(name+'-focused-gallery.json.gz'),focused,write)
            original={r['taskId']:r for r in ledger['tasks']}
            assert all(r['templateResult']==original[r['taskId']]['templateResult'] for r in view['tasks'])
            assert all(r in view['tasks'] for r in focused['tasks'])
            represented=[t for r in focused_queue['representatives'] for t in r['representedTaskIds']]
            assert sorted(represented)==sorted(original)
            results.append({'fixture':name,'ledger':batch._source(ledger_path),'gallery':view_binding,
                'focusedQueue':queue_binding,'focusedGallery':focused_binding,
                'displayReceiptSha256':view['contractEnforcementReceipt']['candidateDisplay']['bodySha256'],
                'counts':view['counts'],'fullQueueTasks':len(view['tasks']),'sampledTasks':len(focused['tasks']),
                'fullQueueCoverage':True,'fullLedgerPreserved':True,'fitSemanticsUnchanged':True,
                'taskViewEvidence':[{'taskId':r['taskId'],'ledgerTaskSha256':r['ledgerTaskSha256'],'counts':r['counts'],
                     'orderedCandidateIds':r['orderedCandidateIds'],'displayedCandidateIds':[c['candidateId'] for c in r['candidates']],
                     'omittedCandidateIds':r['omittedCandidateIds'],'familyOrder':r['familyOrder']} for r in view['tasks']],
                'humanReviewed':False,'selectionAuthorized':False,'renderingAuthorized':False})
    summary={'stage':'P6','results':results,'persistedScorePolicy':'Explicit neutral scores (missing score = 0); no model execution or quality promotion',
             'next':'Independent editor review; P7 not started','currentBlocker':'you'}
    persist(REPORTS/'p6-complete-versus-bounded.json',summary,write)
    print(json.dumps({'result':'PASS','fixtures':len(results),'pool':sum(r['counts']['pool'] for r in results),
                     'eligible':sum(r['counts']['eligible'] for r in results),'unresolved':sum(r['counts']['unresolved'] for r in results),
                     'incompatible':sum(r['counts']['incompatible'] for r in results),'displayed':sum(r['counts']['displayed'] for r in results),
                     'fitSemanticsUnchanged':True,'humanReviewed':False,'P7Started':False}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');run(p.parse_args().write)
