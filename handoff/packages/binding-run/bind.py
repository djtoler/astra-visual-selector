#!/usr/bin/env python3
"""Build the grammar by running the pipeline. Never by hand.

Every binding it writes carries promptSha, model, runId, verdict, mechanism and evidence.
User-named bindings are preserved with source "user". Resumable.
"""
import json, sys, pathlib, hashlib, datetime, time
P = pathlib.Path(__file__).resolve().parent
PROMPTS = P.parent / "prompts"
sys.path.insert(0, str(P)); sys.path.insert(0, str(P.parent / "match-trial"))
import run as R, candidates as C, preflight

PROMPT   = PROMPTS / "PROMPT-bind.md"
RAW      = P / "bind-raw.json"
OUT      = pathlib.Path("/Users/dwaynetoler/timeline/grammar/bindings.json")
BATCH    = 20

# bindings the user named directly; these survive any rerun
USER_NAMED = {
 "one_vs_aggregate": ["51_debut_leaderboard","46_similarity_criteria_table","48_playoff_path_summary",
                      "truth-population-field","53_lineup_rotation_columns"],
 "category_breakdown": ["36_four_portrait_cards","56_seven_artist_stat_lineup"],
 "intersection_of_sets": ["truth-cohort-attrition"],
 "inversion": [],
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()[:12]

def block(r):
    L=[f'ID: {r["id"]}', f'DESCRIPTION: {r.get("description") or "not recorded"}']
    for label,k in (("USE WHEN","useWhen"),("AVOID WHEN","avoid"),("ENCODING","encoding"),
                    ("SUITS NARRATION LIKE","narration"),("CAVEATS","caveats")):
        v=r.get(k)
        if v: L.append(f'{label}: {("; ".join(map(str,v)) if isinstance(v,list) else str(v))[:260]}')
    L.append("CAPACITY: "+(", ".join(f"{k}={v}" for k,v in (r.get("axes") or {}).items()) or "unknown"))
    return "\n".join(L)

def main():
    if preflight.main(verbose=True):
        print("\nbind.py refuses to run on a pool that fails preflight.")
        raise SystemExit(1)
    print()
    runId = datetime.datetime.now().strftime("bind-%Y%m%dT%H%M")
    psha  = sha(PROMPT)
    tmpl  = PROMPT.read_text()
    pool  = C.load()
    raw   = json.load(open(RAW)) if RAW.exists() else {}
    todo  = [r for r in pool if r["id"] not in raw]
    print(f"pool {len(pool)} | already judged {len(raw)} | to judge {len(todo)} | "
          f"{-(-len(todo)//BATCH)} calls | prompt {psha} | run {runId}", flush=True)

    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i+BATCH]
        body  = "\n\n".join(block(r) for r in chunk)
        p = tmpl.replace("## The template\n\nID: {id}\nDESCRIPTION: {description}\nUSE WHEN: {useWhen}\n"
                         "AVOID WHEN: {avoidWhen}\nENCODING: {encoding}\nSUITS NARRATION LIKE: {narration}\n"
                         "CAVEATS: {caveats}\nCAPACITY: {axes}",
                         "## The templates\n\nJudge each one. Return one object per template.\n\n"+body)
        p = p.replace('```json\n{"id":"...","serves":[',
                      'Return {"templates":[ ... ]} where each entry is:\n```json\n{"id":"...","serves":[')
        try:
            got = R.as_json(R.ask(p, timeout=900))
            for t in got.get("templates", got.get("results", [])):
                raw[t["id"]] = t.get("serves", [])
        except Exception as e:
            print(f"   batch {i//BATCH} failed: {str(e)[:140]}", flush=True)
        json.dump(raw, open(RAW,"w"), indent=1)
        print(f"   {min(i+BATCH,len(todo))}/{len(todo)}", flush=True)

    # assemble the grammar, provenance on every entry
    byid = {r["id"]: r for r in pool}
    g = {}
    for tid, serves in raw.items():
        r = byid.get(tid)
        if not r: continue
        for s in serves or []:
            job = s.get("job")
            if not job: continue
            g.setdefault(job, []).append({
              "id": tid, "name": r.get("description"),
              "enc": str(r.get("encoding") or "")[:150],
              "cap": ", ".join(f"{k}={v}" for k,v in list((r.get("axes") or {}).items())[:3]),
              "condition": s.get("condition"),
              "provenance": {"source":"pipeline","promptSha":psha,"model":R.MODEL,"runId":runId,
                             "verdict": s.get("confidence","clear"),
                             "mechanism": s.get("mechanism"), "evidence": s.get("evidence")},
              "styleAdaptation": {"status":"unassessed",
                 "exposes": {"infographic":["glow","motion","background","media"],
                             "cinematic_3d":["background","media"],
                             "after_effects":["typeface","background","media"]}.get(r["kind"],[]),
                 "needs":{}, "notes":""}})
    for job, ids in USER_NAMED.items():
        have = {x["id"] for x in g.get(job,[])}
        for tid in ids:
            if tid in have: continue
            r = byid.get(tid)
            if not r: continue
            g.setdefault(job,[]).append({
              "id":tid,"name":r.get("description"),
              "enc":str(r.get("encoding") or "")[:150],
              "cap":", ".join(f"{k}={v}" for k,v in list((r.get("axes") or {}).items())[:3]),
              "provenance":{"source":"user","namedAt":"2026-09-18"},
              "styleAdaptation":{"status":"unassessed","exposes":[],"needs":{},"notes":"user-named"}})
    json.dump(g, open(OUT,"w"), indent=1)
    print(f"\njobs {len(g)} | bindings {sum(len(v) for v in g.values())} -> {OUT}")
    for j,v in sorted(g.items()): print(f"  {j:26} {len(v)}")

if __name__ == "__main__":
    main()
