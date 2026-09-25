#!/usr/bin/env python3
"""Measure the binding payload. Imports nothing that runs."""
import sys, pathlib, re
from collections import Counter
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "match-trial"))
import candidates as C
P = pathlib.Path(__file__).resolve().parent
PROMPTS = P.parent / "prompts"

def block(r):
    L=[f'ID: {r["id"]}', f'DESCRIPTION: {r.get("description") or "not recorded"}']
    for label,k in (("USE WHEN","useWhen"),("AVOID WHEN","avoid"),("ENCODING","encoding"),
                    ("SUITS NARRATION LIKE","narration"),("CAVEATS","caveats")):
        v=r.get(k)
        if v: L.append(f'{label}: {("; ".join(map(str,v)) if isinstance(v,list) else str(v))[:260]}')
    L.append("CAPACITY: "+(", ".join(f"{k}={v}" for k,v in (r.get("axes") or {}).items()) or "unknown"))
    return "\n".join(L)

tok = lambda s: len(s)/3.7      # conservative chars-per-token for structured English
pool = C.load()
tmpl = PROMPTS/"PROMPT-bind.md".read_text()
pt   = tok(tmpl)
bt   = {r["id"]: tok(block(r)) for r in pool}

def fam(r):
    if r["kind"]!="after_effects": return r["kind"].upper()
    return re.sub(r'--(review|scene)-\d+\w*$','',r["id"])

def cost(records, batch=20, out_per=170):
    n=len(records); calls=-(-n//batch)
    inp=sum(pt + sum(bt[r["id"]] for r in records[i:i+batch]) for i in range(0,n,batch))
    return n, calls, inp, n*out_per

print(f"{'scope':38} {'recs':>5} {'calls':>6} {'in tok':>10} {'out tok':>9} {'total':>10}")
def row(label, recs, batch=20):
    n,c,i,o = cost(recs,batch)
    print(f"{label:38} {n:>5} {c:>6} {i:>10,.0f} {o:>9,.0f} {i+o:>10,.0f}")

row("FULL — every record", pool)
data=[r for r in pool if r["kind"] in ("infographic","cinematic_3d")]
row("data-capable only (infographic + 3D)", data)
seen=set(); pilot=[]
for r in pool:
    f=fam(r)
    if r["kind"] in ("infographic","cinematic_3d") or f not in seen:
        pilot.append(r); seen.add(f)
row("PILOT — data + 1 per AE family", pilot)
print()
print("AE families and their scene counts (the duplication):")
c=Counter(fam(r) for r in pool if r["kind"]=="after_effects")
for k,v in c.most_common(8): print(f"   {v:>4}  {k}")
print(f"   {len(c)} AE families, {sum(c.values())} AE scenes")
