#!/usr/bin/env python3
import json, sys, pathlib, subprocess, re, time
P=pathlib.Path(__file__).resolve().parent
PROMPTS = P.parent / "prompts"
sys.path.insert(0,str(P)); sys.path.insert(0,str(P.parent/"match-trial"))
import run as R, candidates as C

BATCH=20
def cand_block(r):
    parts=[f'- id: {r["id"]}', f'  description: {r["description"] or "not recorded"}']
    if r.get("useWhen"): parts.append(f'  use when: {str(r["useWhen"])[:200]}')
    if r.get("encoding"): parts.append(f'  encoding: {str(r["encoding"])[:200]}')
    if r.get("narration"): parts.append(f'  suits: {"; ".join(map(str,r["narration"]))[:200]}')
    if r.get("avoid"): parts.append(f'  avoid: {"; ".join(map(str,r["avoid"]))[:200]}')
    if r.get("caveats"): parts.append(f'  caveats: {"; ".join(map(str,r["caveats"]))[:160]}')
    parts.append('  capacity: '+(", ".join(f"{k}={v}" for k,v in (r["axes"] or {}).items()) or "unknown"))
    return "\n".join(parts)

RESULTS=P/"rerun-results.json"

def ask_retry(prompt, tries=4):
    """Retry with backoff. A usage limit is transient, not a reason to lose a batch."""
    for k in range(tries):
        try:
            return R.ask(prompt, timeout=600)
        except Exception as e:
            if k == tries-1: raise
            wait = 60*(2**k)
            print(f"   retry {k+1}/{tries-1} in {wait}s ({str(e)[:60]})", flush=True)
            time.sleep(wait)

def main():
    recs=C.load(); beats=json.load(open(P.parent/"match-trial"/"beats.json"))
    tmpl=PROMPTS/"PROMPT-judge-batch.md".read_text()
    out=json.load(open(RESULTS)) if RESULTS.exists() else {}
    for b in beats:
        lo,hi=C.bounds(b["entityCount"])
        pool=[r for r,st,_ in C.shape(recs,b["entityCount"]) if st!="outside"]
        vs=out.get(b["id"], [])
        done={v.get("id") for v in vs}
        pool=[r for r in pool if r["id"] not in done]
        if not pool:
            print(f"[{b['id']}] already complete ({len(vs)} verdicts)", flush=True); continue
        print(f"[{b['id']}] {len(pool)} remaining, {-(-len(pool)//BATCH)} calls ({len(done)} already done)", flush=True)
        for i in range(0,len(pool),BATCH):
            chunk=pool[i:i+BATCH]
            p=R.fill(tmpl, quote=b["quote"], takeaway=b["takeaway"],
                     must_be_true=b["mustBeTrue"], would_be_a_lie=b["wouldBeALie"],
                     n=b["entityCount"], entity_kind=b["entityKind"], lo=lo, hi=hi,
                     candidates="\n".join(cand_block(r) for r in chunk))
            try:
                vs.extend(R.as_json(ask_retry(p))["verdicts"])
            except Exception as e:
                print(f"   batch {i//BATCH} failed: {str(e)[:120]}", flush=True)
            out[b["id"]]=vs
            json.dump(out, open(RESULTS,"w"), indent=1)
            print(f"   {min(i+BATCH,len(pool))}/{len(pool)}", flush=True)
        out[b["id"]]=vs
        json.dump(out, open(P/"rerun-results.json","w"), indent=1)
    print("done", flush=True)

if __name__ == "__main__":
    main()
