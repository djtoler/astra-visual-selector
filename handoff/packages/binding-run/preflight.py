#!/usr/bin/env python3
"""Check the pool before spending money on it.

The failure this guards against: thin or mis-sourced input produces confident bindings that
quote the thin input as evidence, so the provenance validator passes and the grammar is
quietly wrong. Run this before bind.py. Exits non-zero on a blocking problem.
"""
import sys, json, pathlib
from collections import Counter
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "match-trial"))
import candidates as C

MIN_DESC   = 40     # shorter than this cannot carry a mechanic
MAX_TITLE_FALLBACK = 0    # a title is a label, never a description
MAX_THIN_PCT = 10   # refuse if more than this share is thin

def main(verbose=True):
    pool = C.load()
    n = len(pool)
    fail, warn = [], []

    # 1. pool sanity
    ids = [r["id"] for r in pool]
    dupes = [k for k,v in Counter(ids).items() if v > 1]
    if dupes: fail.append(f"{len(dupes)} duplicate ids, e.g. {dupes[:3]}")
    if n < 50: fail.append(f"pool is only {n} records — loader is probably filtering wrongly")

    # 2. field provenance — a title fallback means the real description was missed
    src = Counter(r["sources"]["description"] for r in pool)
    tf = src.get("title-fallback", 0)
    if tf > MAX_TITLE_FALLBACK:
        fail.append(f"{tf} records fell back to `title` for their description. "
                    "Titles are labels. Fix the loader before running.")

    # 3. description quality
    thin = [r for r in pool if len(str(r.get("description") or "")) < MIN_DESC]
    if len(thin)*100/n > MAX_THIN_PCT:
        fail.append(f"{len(thin)}/{n} descriptions under {MIN_DESC} chars "
                    f"({len(thin)*100//n}%, limit {MAX_THIN_PCT}%)")
    elif thin:
        warn.append(f"{len(thin)} thin descriptions — these will bind weakly")

    # 4. records with no usable signal at all
    blind = [r for r in pool if not r.get("description") and not r.get("useWhen")
                              and not r.get("encoding")]
    if blind: fail.append(f"{len(blind)} records carry no description, use-when or encoding")

    # 5. coverage, reported not enforced
    cov = {f: sum(1 for r in pool if r.get(f) not in (None,"",[],{}))
           for f in ("description","useWhen","avoid","encoding","narration","caveats","axes")}

    if verbose:
        print(f"pool: {n} records")
        print("\nfield coverage")
        for f,c in cov.items(): print(f"   {f:12} {c:>4}/{n}  {100*c//n:>3}%")
        print("\ndescription source")
        for k,v in src.most_common(): print(f"   {str(k):16} {v:>4}")
        print("\navoid-when source")
        for k,v in Counter(r['sources']['avoid'] for r in pool).most_common():
            print(f"   {str(k):16} {v:>4}")
        if thin:
            print(f"\nthin descriptions ({len(thin)}), these bind weakly:")
            for r in sorted(thin, key=lambda x: len(str(x.get('description') or '')))[:8]:
                print(f"   {r['id'][:44]:44} {str(r.get('description'))[:46]}")
        for w in warn: print(f"\nWARN  {w}")
        for f in fail: print(f"\nBLOCK {f}")
        print("\n" + ("BLOCKED — fix the input before spending." if fail else "preflight passed."))
    return 1 if fail else 0

if __name__ == "__main__":
    sys.exit(main())
