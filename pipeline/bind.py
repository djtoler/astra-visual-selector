#!/usr/bin/env python3
"""Build the grammar by running the pipeline. Never by hand.

Every binding it writes carries promptSha, model, runId, verdict, mechanism and evidence.
User-named bindings are preserved with source "user". Resumable.
"""
import json, sys, pathlib, hashlib, datetime, time
from concurrent.futures import ThreadPoolExecutor, as_completed
P = pathlib.Path(__file__).resolve().parent
PROMPTS = P.parent / "prompts"
sys.path.insert(0, str(P)); sys.path.insert(0, str(P.parent / "match-trial"))
import run as R, candidates as C, preflight

PROMPT   = PROMPTS / "PROMPT-bind.md"
RAW      = P / "bind-raw.json"
PARTS    = P / "bind-parts"   # one file per batch: no shared write, no race
WORKERS  = 6                  # rate limits allow far more; 6 keeps failures legible
OUT      = pathlib.Path("/Users/dwaynetoler/timeline/grammar/bindings.json")
BATCH    = 20

def _user_named():
    """Every binding the user established by selecting it in a review pass, plus any
    hand-listed below. A pick is the strongest evidence in the system and MUST survive
    a rerun — on 2026-09-21 a re-bind silently dropped
    archive3-carousel-flow-loops--review-001 from one_vs_many_individually, a binding
    the user had validated. See no-drifting LOG 0031."""
    f = pathlib.Path("/Users/dwaynetoler/timeline/grammar/picks.json")
    out = {k: list(v) for k, v in _HAND.items()}
    if f.exists():
        for b in json.load(open(f))["beats"].values():
            for i in b.get("selected") or []:
                out.setdefault(b["job"], [])
                if i not in out[b["job"]]: out[b["job"]].append(i)
    return out

# bindings the user named directly in conversation; these survive any rerun
_HAND = {
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
    # The capability record, where the video pass measured one. This is information the
    # first binding run never had: what the clip ENCODES in its form versus what it
    # PRINTS as text, how many media wells it holds, and how its items arrive. Without
    # it a re-bind sees the same description and reaches the same answer.
    c = r.get("capability")
    if c:
        L.append(f'MEASURED FROM THE CLIP: holds {c.get("slots_at_once")} subject(s) at '
                 f'once, {c.get("slots_total")} in total, across {c.get("media_slots")} '
                 f'media well(s) and {c.get("text_slots")} text field(s); arranged as '
                 f'{c.get("structure")}; they arrive {c.get("staging")}.')
        L.append(f'ENCODES IN ITS FORM: {", ".join(c.get("carries") or ["none"])}')
        L.append(f'READABLE AS TEXT: {", ".join(c.get("readable") or ["none"])}')
        L.append(f'UNAVOIDABLY IMPLIES: {", ".join(c.get("implies") or ["none"])}')
        if c.get("asserts"): L.append(f'ASSERTS: {c["asserts"]}')
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
    only = None
    if "--only" in sys.argv:
        only = set(json.load(open(sys.argv[sys.argv.index("--only")+1])))
        print(f"--only: re-judging {len(only)} named record(s); the cache is not consulted")
    todo  = [r for r in pool if r["id"] in only] if only else \
            [r for r in pool if r["id"] not in raw]
    print(f"pool {len(pool)} | already judged {len(raw)} | to judge {len(todo)} | "
          f"{-(-len(todo)//BATCH)} calls | prompt {psha} | run {runId}", flush=True)

    PARTS.mkdir(exist_ok=True)
    def do_batch(k, chunk):
        part = PARTS / f"{runId}-{k:03d}.json"
        if part.exists(): return k, "cached"
        body = "\n\n".join(block(r) for r in chunk)
        p = tmpl.replace("## The template\n\nID: {id}\nDESCRIPTION: {description}\nUSE WHEN: {useWhen}\n"
                         "AVOID WHEN: {avoidWhen}\nENCODING: {encoding}\nSUITS NARRATION LIKE: {narration}\n"
                         "CAVEATS: {caveats}\nCAPACITY: {axes}",
                         "## The templates\n\nJudge each one. Return one object per template.\n\n"+body)
        p = p.replace('```json\n{"id":"...","serves":[',
                      'Return {"templates":[ ... ]} where each entry is:\n```json\n{"id":"...","serves":[')
        for attempt in range(3):
            try:
                got = R.as_json(R.ask(p, timeout=900))
                out = {t["id"]: {"serves": t.get("serves", []),
                                 "runId": runId, "promptSha": psha, "model": R.MODEL}
                       for t in got.get("templates", got.get("results", []))}
                part.write_text(json.dumps(out, indent=1))   # atomic per batch
                return k, f"{len(out)} records"
            except Exception as e:
                if attempt == 2: return k, f"FAILED {str(e)[:110]}"
                time.sleep(20*(attempt+1))
        return k, "FAILED"

    batches = [(k, todo[i:i+BATCH]) for k,i in enumerate(range(0, len(todo), BATCH))]
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(do_batch, k, c): k for k,c in batches}
        for f in as_completed(futs):
            k, msg = f.result(); done += 1
            print(f"   [{done}/{len(batches)}] batch {k:>3}: {msg}", flush=True)

    for part in sorted(PARTS.glob(f"{runId}-*.json")):
        raw.update(json.loads(part.read_text()))
    json.dump(raw, open(RAW,"w"), indent=1)
    print(f"\n   merged {len(raw)} template judgments | "
          f"{R.USAGE['calls']} calls, ${R.spend():.2f} billed, "
          f"{R.USAGE['truncated']} truncated", flush=True)

    # assemble the grammar, provenance on every entry
    #
    # A PARTIAL RUN MUST STAY PARTIAL. `--only` judged 19 records on 2026-09-22 and
    # then rebuilt the grammar from all 440 judgments in bind-raw.json, silently
    # undoing salvage_bindings.py: assert_without_data went 42 -> 257 (59% of the
    # corpus, the exact flood the salvage exists to revert), narrate_an_event
    # 132 -> 218, while parallel_instances collapsed 50 -> 23 and inversion 11 -> 2.
    # 289 bindings changed on a run that judged nineteen records.
    # With --only, the existing grammar is the base and only the named ids are
    # merged into it.
    byid = {r["id"]: r for r in pool}
    g = {}
    base = json.load(open(OUT)) if (only and OUT.exists()) else {}
    if base:
        g = {j: [r for r in rows if r["id"] not in only] for j, rows in base.items()}
        print(f"   --only: keeping the existing grammar as the base "
              f"({sum(len(v) for v in base.values())} bindings) and merging only the "
              f"{len(only)} named record(s)")
    scope = only if only else set(raw)
    for tid, entry in raw.items():
        if tid not in scope: continue
        r = byid.get(tid)
        if not r: continue
        # entries written before 2026-09-21 are a bare list with no per-record
        # provenance. Stamping THIS run's id onto them would claim a judgment that
        # never happened, so they are marked as what they are.
        if isinstance(entry, list):
            serves, prov = entry, {"runId": "bind-20260919T2252", "promptSha": "2e441f794dba",
                                   "model": R.MODEL}
        else:
            serves = entry.get("serves") or []
            prov = {"runId": entry.get("runId"), "promptSha": entry.get("promptSha"),
                    "model": entry.get("model") or R.MODEL}
        for s in serves or []:
            job = s.get("job")
            if not job: continue
            g.setdefault(job, []).append({
              "id": tid, "name": r.get("description"),
              "enc": str(r.get("encoding") or "")[:150],
              "cap": ", ".join(f"{k}={v}" for k,v in list((r.get("axes") or {}).items())[:3]),
              "condition": s.get("condition"),
              "provenance": {"source":"pipeline","promptSha":prov["promptSha"],
                             "model":prov["model"],"runId":prov["runId"],
                             "verdict": s.get("confidence","clear"),
                             "mechanism": s.get("mechanism"), "evidence": s.get("evidence")},
              "styleAdaptation": {"status":"unassessed",
                 "exposes": {"infographic":["glow","motion","background","media"],
                             "cinematic_3d":["background","media"],
                             "after_effects":["typeface","background","media"]}.get(r["kind"],[]),
                 "needs":{}, "notes":""}})
    for job, ids in _user_named().items():
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
