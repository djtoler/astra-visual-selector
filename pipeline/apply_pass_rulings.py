#!/usr/bin/env python3
"""Apply grammar/pass-rulings.json to grammar/picks.json.

A pass file is an immutable record of what the ingest produced. When the user
later tells us what a pass MEANT, that clarification cannot go in the pass file
and must not be guessed at ingest time. It goes here, with their words, and is
applied to picks.json -- the current merged state.

The only ruling so far: `passedIsJudged`. On passes 1 and 2 a beat with zero
picks recorded zero rejections, per the standing rule that an ambiguous zero must
never be read as rejecting everything. The user has said their zeros were never
ambiguous, so the cards shown on those beats are rejections and belong in the
record. 108 cards across 11 beats.

    python3 pipeline/apply_pass_rulings.py [--write]
"""
import json, pathlib, sys

P = pathlib.Path(__file__).resolve().parent
PICKS = P.parent / "grammar" / "picks.json"
PASSES = P.parent / "grammar" / "passes"
RULINGS = P.parent / "grammar" / "pass-rulings.json"


def passed_is_judged(picks, rulings, passes_dir):
    """Add, per beat, every card a named pass SHOWED and the user did not select.

    Reads `shown` from the pass file, which is the historical record of what was
    on screen -- never from a live slate, which drifts (LOG 0035). A card already
    selected on that beat is never rejected by this.
    """
    r = rulings.get("passedIsJudged")
    if not r:
        return picks, []
    added = []
    for name in r["_appliesTo"]:
        pf = passes_dir / name
        if not pf.exists():
            raise FileNotFoundError(f"pass-rulings names a pass that is not there: {name}")
        old = json.load(open(pf))["beats"]
        for k, v in old.items():
            if v.get("selected"):
                continue            # already handled by the normal derivation
            cur = picks.get(k)
            if cur is None:
                continue
            sel = set(cur.get("selected") or [])
            new = [i for i in v.get("shown") or []
                   if i not in sel and i not in set(cur.get("rejected") or [])]
            if not new:
                continue
            cur["rejected"] = sorted(set(cur.get("rejected") or []) | set(new))
            added.append((name, k, len(new)))
    return picks, added


def main(argv):
    picks = json.load(open(PICKS))
    rulings = json.load(open(RULINGS))
    before = sum(len(v.get("rejected") or []) for v in picks["beats"].values())
    picks["beats"], added = passed_is_judged(picks["beats"], rulings, PASSES)
    after = sum(len(v.get("rejected") or []) for v in picks["beats"].values())
    picks.setdefault("provenance", {})["rulingsApplied"] = {
        k: v.get("_quote") for k, v in rulings.items() if not k.startswith("_")}
    for name, k, n in added:
        print(f"   {name:24} {k:9} +{n} rejected")
    print(f"\nrejections {before} -> {after}  ({after - before} added across "
          f"{len({a[1] for a in added})} beat(s))")
    sel = sum(len(v.get("selected") or []) for v in picks["beats"].values())
    print(f"selections unchanged at {sel}; beats {len(picks['beats'])}")
    if "--write" not in argv:
        print("\nclean. Re-run with --write to save picks.json.")
        return 0
    PICKS.write_text(json.dumps(picks, indent=1))
    print(f"\nwrote {PICKS.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
