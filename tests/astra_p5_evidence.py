"""Replay P5 evidence through the existing batch runner with pinned effective pools.

No provider, relevance model, native renderer or selection operation is invoked.
Compressed JSON is transport only; validation consumes the original batch object.
"""
import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline import visualtask_batch_matching as batch
REPORTS = ROOT/'reports/astra-p5'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def run(write=False):
    templates=json.loads((REPORTS/'effective-template-pool.json').read_text())
    media=json.loads((REPORTS/'effective-media-pool.json').read_text())
    outcomes=[]
    with patch.object(batch.matching.C,'load',return_value=templates), patch.object(batch.matching.M,'load',return_value=media):
        for name in ('current','synthetic'):
            request=ROOT/'tests/fixtures/visualtask_batch_matching'/(name+'-request.json')
            artifact=batch.build(request)
            batch.validate(artifact)
            encoded=batch.dumps(artifact).encode()
            path=REPORTS/(name+'-ledger.json.gz')
            if write: path.write_bytes(gzip.compress(encoded,mtime=0))
            else:
                if gzip.decompress(path.read_bytes()) != encoded:
                    raise ValueError('P5 ledger does not replay from pinned inputs: '+name)
            baseline=json.loads((REPORTS/(name+'-baseline.json')).read_text())
            before={r['taskId']:r for r in baseline['tasks']}
            tasks=[]
            for row in artifact['tasks']:
                old=before[row['taskId']]['templateResult']
                new=row['templateResult']; candidates=new['candidates']
                tasks.append({'taskId':row['taskId'], 'baselineCandidates':len(old['candidates']),
                              'reconciledVariants':len(candidates),
                              'retainedBaselineCandidates':sorted(set(c['candidateId'] for c in old['candidates']) & set(c['candidateId'] for c in candidates)),
                              'baselineVerdict':old['fitVerdict'],'newVerdict':new['fitVerdict'],
                              'unknownRequirements':sum(d['status']=='unknown' for c in candidates for d in c['fitAssessment']['evidence']['requirements']),
                              'mediaVerdictUnchanged':row['mediaResult']==before[row['taskId']]['mediaResult']})
            outcomes.append({'fixture':name,'input':batch._source(request),'ledger':{'path':path.relative_to(ROOT).as_posix(),
                             'sha256':sha(path),'uncompressedSha256':hashlib.sha256(encoded).hexdigest()},
                             'counts':artifact['counts'],'tasks':tasks,
                             'reconciliationReceipt':artifact['contractEnforcementReceipt']['candidateReconciliation']['bodySha256'],
                             'nativeFitClaims':sum(c['fitAssessment']['verdict'] in {'native_fit','adapted_fit'} for r in artifact['tasks'] for c in r['templateResult']['candidates']),
                             'selectionAuthorized':False,'renderingAuthorized':False})
    result={'stage':'P5','schemaVersion':'astra-outcome-diff@1', 'results':outcomes,
            'effectivePoolBindings':[batch._source(REPORTS/name) for name in ('effective-template-pool.json','effective-media-pool.json')],
            'scope':'Existing batch ledger completeness and deterministic replay; no semantic or native quality promotion',
            'next':'Editor review; P6 not started','currentBlocker':'you'}
    if write: (REPORTS/'p5-outcome-diff.json').write_text(batch.dumps(result))
    else:
        if json.loads((REPORTS/'p5-outcome-diff.json').read_text())!=result:
            raise ValueError('P5 outcome summary does not replay')
    print(json.dumps({'result':'PASS','fixtures':len(outcomes),'variants':sum(t['reconciledVariants'] for r in outcomes for t in r['tasks']),
                      'nativeFitClaims':sum(r['nativeFitClaims'] for r in outcomes)}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--write',action='store_true')
    run(parser.parse_args().write)
