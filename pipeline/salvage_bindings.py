#!/usr/bin/env python3
"""Merge two binding runs per job, by rule, never by taste.

A rebind is not uniformly better or worse — the 2026-09-21 full rebind fixed four
starved jobs and flooded two others. Reverting wholesale throws away the fix; keeping
wholesale keeps the flood. So merge per job, on a stated criterion.

The criterion, applied mechanically, and each binding keeps its own provenance so the
audit trail survives the merge:

  REVERT a job when the new run FLOODS it — over FLOOD_PCT of the corpus when the old
         run was not. A job that matches most of the library has stopped selecting.
  REVERT a job when the new run COLLAPSED it — under half its former size, from a base
         of at least 4. A collapse is far more often a regression than a discovery.
  KEEP the new run otherwise.

This is a judgment about WHICH RUN to trust for a job, not about which template serves
it. No binding is invented, edited or hand-chosen here.

    python3 pipeline/salvage_bindings.py <old.json> <new.json> [--write]
"""
import json, pathlib, sys
P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P.parent / "match-trial"))
import candidates as C
OUT = P.parent / "grammar" / "bindings.json"
COLLAPSE_FLOOR = 4          # below this a drop is noise, not a collapse

def merge(old, new, corpus):
    out, log = {}, []
    for j in sorted(set(old) | set(new)):
        a, b = old.get(j, []), new.get(j, [])
        pa, pb = len(a) * 100 / corpus, len(b) * 100 / corpus
        if pb > C.FLOOD_PCT and pa <= C.FLOOD_PCT:
            out[j], why = a, f"new floods it ({pb:.0f}% of corpus)"
        elif len(a) >= COLLAPSE_FLOOR and len(b) < len(a) / 2:
            out[j], why = a, f"new collapsed it ({len(a)} -> {len(b)})"
        else:
            out[j], why = b, ""
        log.append((j, len(a), len(b), "OLD" if out[j] is a else "NEW", why))
    return out, log

def main(argv):
    if len(argv) < 3: print(__doc__); return 2
    old = json.load(open(argv[1])); new = json.load(open(argv[2]))
    corpus = len(C.load())
    out, log = merge(old, new, corpus)
    print(f"{'job':26s} {'old':>5s} {'new':>5s} {'kept':>5s}  reason")
    for j, a, b, k, why in log:
        print(f"{j:26s} {a:5d} {b:5d} {k:>5s}  {why}")
    rev = [j for j, _, _, k, _ in log if k == "OLD"]
    tot = sum(len(v) for v in out.values())
    print(f"\nkept NEW on {len(log)-len(rev)} jobs, reverted {len(rev)}: {rev}")
    print(f"bindings: old {sum(len(v) for v in old.values())} | "
          f"new {sum(len(v) for v in new.values())} | merged {tot}")
    import collections
    prov = collections.Counter(r["provenance"].get("promptSha")
                               for rows in out.values() for r in rows
                               if r["provenance"].get("source") != "user")
    print(f"provenance after merge, by prompt: {dict(prov)}")
    flooded = [j for j, rows in out.items() if len(rows) * 100 / corpus > C.FLOOD_PCT]
    print(f"still flooded: {flooded or 'none'}")
    if "--write" not in argv:
        print("\nnot written. Re-run with --write.")
        return 0
    OUT.write_text(json.dumps(out, indent=1))
    print(f"\nwrote {OUT}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
