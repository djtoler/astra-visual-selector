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

# Only the description-length rule is configurable. Everything else below is a fixed
# structural check and takes no exceptions.
THIN = json.load(open(pathlib.Path(__file__).resolve().parent / "rules.json"))["thin_description"]
MIN_DESC, MAX_THIN_PCT = THIN["min_chars"], THIN["max_pct"]

def exempt(rec):
    """The description-length rule holds unless a title in `exceptions` matches this record."""
    ex = THIN.get("exceptions") or []
    if not ex: return False
    # CONTAINS, not exact. An exception names a family the way a person would —
    # "intro-slideshow", not "intro-slideshow-full-720p" — and forcing the full id is
    # rigidity for its own sake. The real defect in LOG 0018 was never the substring:
    # it was that a non-match said NOTHING. check_exceptions() now fails loudly when an
    # exception matches no record, so a typo cannot silently disable a rule and a
    # human-scale name still works.
    hay = f'{C._family(rec.get("id",""))} {rec.get("template") or ""}'.lower()
    return any(t.lower() in hay for t in ex)

def check_exceptions(pool):
    """An exception that matches no record is a typo that silently disables a rule.
    Fail on it. Found 2026-09-20: tightening the match from substring to family-exact
    quietly killed the user's "intro-slideshow" exception, and thin descriptions went
    from 3 to 11 with nothing reporting why. See no-drifting LOG 0018."""
    hay = " ".join(f'{C._family(r)} {r.get("template") or ""}' for r in pool).lower()
    return [t for t in (THIN.get("exceptions") or []) if t.lower() not in hay]

def main(verbose=True):
    pool = C.load()
    dead = check_exceptions(pool)
    if dead:
        print(f"FAIL  exception(s) matching no template family: {dead}")
        print(f"      an exception that matches nothing silently disables its rule.")
        return 1
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
    if tf:
        fail.append(f"{tf} records fell back to `title` for their description. "
                    "Titles are labels. Fix the loader before running.")

    # 3. description length — the one configurable rule
    gov = [r for r in pool if not exempt(r)]
    exempted = n - len(gov)
    thin = [r for r in gov if len(str(r.get("description") or "")) < MIN_DESC]
    pct = len(thin)*100/len(gov) if gov else 0
    if pct > MAX_THIN_PCT:
        fail.append(f"{len(thin)}/{len(gov)} governed descriptions under {MIN_DESC} chars "
                    f"({pct:.0f}%, limit {MAX_THIN_PCT}%)")
    elif thin:
        warn.append(f"{len(thin)} thin descriptions — these will bind weakly")
    if exempted:
        warn.append(f"{exempted} records exempt from thin_description via "
                    f"exceptions {THIN['exceptions']}")

    # 4. records with no usable signal at all
    blind = [r for r in pool
             if not r.get("description") and not r.get("useWhen") and not r.get("encoding")]
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
