#!/usr/bin/env python3
"""Validate and merge capability records from the video-understanding pass.

Input: the JSON objects produced by prompts/PROMPT-describe-clip.md — one per clip,
either as a JSON array, one object per line, or a directory of .json files.

Output: grammar/capability.json, a sidecar keyed by record id. A SIDECAR, because
approved-list.json lives in Codex's tree and this side never writes there.

Nothing is merged until every record validates. A partial ingest of a 216-record run
is worse than none: it leaves the pool in a state nobody can reason about.

    python3 pipeline/ingest_capability.py <file-or-dir>            validate, report
    python3 pipeline/ingest_capability.py <file-or-dir> --write    also merge
"""
import json, pathlib, sys
P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P.parent / "match-trial"))
import candidates as C

OUT = P.parent / "grammar" / "capability.json"

STRUCTURE = {"single","pair","list","grid","grouped_clusters","axis_plot","nested","sequence"}
STAGING   = {"all_at_once","builds_up","reveals_in_turn","accumulates_to_total","unknown"}
CARRIES   = {"magnitude","share_of_whole","rank","change_over_time","difference","parity",
             "aggregate","derivation","membership","overlap","absence","identity","none"}
READABLE  = {"label","statement","exact_value","ordering","proportion","difference",
             "grouping","position_in_sequence","none"}
IMPLIES   = {"ranking","competition","chronology","causation","completeness","equality",
             "independence","none"}
INTS      = ("slots_at_once","slots_total","text_slots","media_slots")


def validate(rec, known_ids):
    """Every way one record can be wrong. Returns a list of plain-English problems."""
    e = []
    rid = rec.get("id")
    if not rid:               return ["no id"]
    if rid not in known_ids:  e.append(f"id is not in the pool")

    for f in INTS:
        v = rec.get(f)
        if not isinstance(v, int) or isinstance(v, bool): e.append(f"{f} is not a whole number")
        elif v < 0:                                       e.append(f"{f} is negative")
    if "growable" not in rec:
        e.append("growable is missing")
    elif not (isinstance(rec["growable"], bool) or rec["growable"] is None):
        # null is a real answer: a sequence that may or may not continue past the clip
        # is genuinely unknown, and a forced guess is worse than saying so
        e.append("growable is not true, false or null")

    a, t = rec.get("slots_at_once"), rec.get("slots_total")
    if isinstance(a, int) and isinstance(t, int) and t < a:
        e.append(f"slots_total {t} is less than slots_at_once {a}")

    if rec.get("structure") not in STRUCTURE: e.append(f"structure {rec.get('structure')!r} not in the vocabulary")
    if rec.get("staging")   not in STAGING:   e.append(f"staging {rec.get('staging')!r} not in the vocabulary")

    for f, allowed in (("carries",CARRIES),("readable",READABLE),("implies",IMPLIES)):
        v = rec.get(f)
        if not isinstance(v, list): e.append(f"{f} is not a list"); continue
        if not v:                   e.append(f"{f} is empty — use ['none'], so silence and 'nothing' differ")
        bad = [x for x in v if x not in allowed]
        if bad:                     e.append(f"{f} has unknown value(s) {bad}")
        if "none" in v and len(v) > 1: e.append(f"{f} mixes 'none' with real values")

    s = rec.get("asserts")
    if not isinstance(s, str) or not s.strip(): e.append("asserts is empty")
    elif len(s.split()) > 25:                   e.append(f"asserts is {len(s.split())} words, over the 25 limit")

    if not isinstance(rec.get("unclear"), list): e.append("unclear is not a list")
    return e


def conflicts(rec, pool):
    """Where the model's slot count disagrees with a capacity the record already
    declared. Never auto-resolved — a disagreement usually means one side is counting
    something other than subject slots, which is exactly LOG 0013."""
    old = C.subject_axes(pool[rec["id"]]) if rec["id"] in pool else {}
    if not old: return None
    declared = max(old.values())
    got = rec.get("slots_at_once")
    if not isinstance(got, int) or got == declared: return None
    lo, hi = C.bounds(declared)
    return {"id": rec["id"], "declared": old, "model": got,
            "severity": "minor" if lo <= got <= hi else "MAJOR"}


def load_input(path):
    p = pathlib.Path(path)
    if p.is_dir():
        return [json.loads(f.read_text()) for f in sorted(p.glob("*.json"))]
    text = p.read_text().strip()
    if text.startswith("["): return json.loads(text)
    return [json.loads(ln) for ln in text.splitlines() if ln.strip()]


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    recs = load_input(argv[1])
    pool = {r["id"]: r for r in C.load()}
    # BOOTSTRAP. A local sidecar template is deliberately held OUT of the pool until
    # it has a capability record — an unmeasured record has no description and
    # PROMPT-bind cannot judge one (LOG 0049). But this validator gated on the pool,
    # so those records could never receive their FIRST record: held out for lacking
    # a measurement, and unable to be measured for being held out. Codex found the
    # deadlock reading handoff 025, before any paid call.
    # Ingest accepts a sidecar id. SELECTION still does not — _local() is untouched
    # and keeps the gate. The two questions are different: "may this be written?" and
    # "may this be chosen?"
    ids  = set(pool) | set(C.local_pending())

    seen, dupes, bad = set(), [], []
    for r in recs:
        rid = r.get("id")
        if rid in seen: dupes.append(rid)
        seen.add(rid)
        errs = validate(r, ids)
        if errs: bad.append((rid, errs))

    print(f"records in: {len(recs)}   unique ids: {len(seen)}   invalid: {len(bad)}")
    if dupes: print(f"FAIL  duplicate ids: {sorted(set(dupes))[:8]}")
    for rid, errs in bad[:20]:
        print(f"  {str(rid)[:44]:46s} {'; '.join(errs)}")
    if len(bad) > 20: print(f"  ... and {len(bad)-20} more")

    cf = [c for c in (conflicts(r, pool) for r in recs if not validate(r, ids)) if c]
    major = [c for c in cf if c["severity"] == "MAJOR"]
    if cf:
        print(f"\nslot count disagrees with a declared capacity on {len(cf)} record(s), "
              f"{len(major)} of them beyond tolerance. Not auto-resolved:")
        for c in (major + [x for x in cf if x not in major])[:12]:
            print(f"  {c['severity']:5s} {c['id'][:40]:42s} declared {c['declared']}  model says {c['model']}")

    print("\n--- every `asserts` line, for a human to scan for the sample trap ---")
    print("    (a subject noun here means the model described the demo, not the mechanic)")
    for r in recs[:40]:
        print(f"  {str(r.get('id'))[:40]:42s} {r.get('asserts','')}")
    if len(recs) > 40: print(f"  ... and {len(recs)-40} more")

    # GROUPED BY VALUE, not listed per record. A flag the model raises on every clip
    # is one fact about the corpus, not N facts about N clips; printing it N times is
    # what makes a queue look like noise. See no-drifting LOG 0025.
    import collections
    byval = collections.defaultdict(list)
    for r in recs:
        for u in (r.get("unclear") or []): byval[u].append(r["id"])
    if byval:
        print(f"\nunclear flags, grouped ({len(byval)} distinct):")
        for u, who in sorted(byval.items(), key=lambda kv: -len(kv[1])):
            if len(who) == len(recs):
                print(f"  {len(who):4d}  {u}   — every record; a property of the corpus, "
                      f"not a per-clip to-do")
            elif len(who) > 6:
                print(f"  {len(who):4d}  {u}   e.g. {who[0][:36]}")
            else:
                print(f"  {len(who):4d}  {u}")
                for i in who: print(f"          {i}")

    if bad or dupes:
        print("\nNOT WRITTEN. Fix the invalid records and re-run; a partial merge of a "
              "large run leaves the pool in a state nobody can reason about.")
        return 1
    if "--write" not in argv:
        print(f"\nvalid. Re-run with --write to merge into {OUT.name}.")
        return 0

    existing = json.loads(OUT.read_text()) if OUT.exists() else {}
    existing.update({r["id"]: r for r in recs})
    OUT.write_text(json.dumps(existing, indent=1, sort_keys=True))
    print(f"\nwrote {len(recs)} record(s); {OUT.name} now holds {len(existing)} of "
          f"{len(pool)} pool records.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
