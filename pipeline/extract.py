#!/usr/bin/env python3
"""Batched beat extraction. Usage: extract.py <first> <last>   (1-indexed passage numbers)"""
import json, sys, pathlib
P=pathlib.Path(__file__).resolve().parent
PROMPTS = P.parent / "prompts"
sys.path.insert(0,str(P))
import run as R
N="/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/narration-visual-annotations/year-seventeen-30-passages.md"
OUT=P/"beats-all.json"

def passages():
    return [l[2:].strip() for l in open(N) if l.startswith("> ")]

def main(a,b):
    q=passages()
    block="\n".join(f'PASSAGE {i+1:02d}: {q[i]}' for i in range(a-1,b))
    before = q[a-2] if a>=2 else "(none, this is the opening)"
    after  = q[b] if b < len(q) else "(none, this is the end)"
    tmpl=PROMPTS/"PROMPT-beats.md".read_text()
    txt=R.ask(R.fill(tmpl, passages=block, before=before, after=after), timeout=900)
    got=R.as_json(txt)["passages"]
    prev=json.load(open(OUT)) if OUT.exists() else {}
    for pg in got: prev[pg["passage"]]=pg["beats"]
    json.dump(prev, open(OUT,"w"), indent=1)
    return got

if __name__=="__main__":
    g=main(int(sys.argv[1]), int(sys.argv[2]))
    for pg in g:
        print(f'\n--- passage {pg["passage"]} : {len(pg["beats"])} beat(s) ---')
        for b in pg["beats"]:
            print(f'  [{b["id"]}] {b["job"]}  n={b.get("entity_count")} {b.get("entity_kind","")}')
            print(f'      quote: {b["quote"][:96]}')
            if b.get("takeaway"): print(f'      takeaway: {b["takeaway"][:110]}')
            if b.get("must_be_perceptible"): print(f'      perceptible: {"; ".join(b["must_be_perceptible"])[:110]}')
            if b.get("would_be_a_lie"): print(f'      lie: {"; ".join(b["would_be_a_lie"])[:110]}')
