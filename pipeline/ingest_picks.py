#!/usr/bin/env python3
"""Pick documents from the review UI -> grammar/picks.json.

The user's selections are the only evidence in this system that outranks the pipeline.
CLAUDE.md: "The only exceptions are a binding the user names directly, recorded with
source: 'user' and their words." This writes that record.

Two rules the user set on 2026-09-21, both applied here rather than in the UI:

  * A beat with NO selection means nothing shown was good enough. That is a finding
    about the library, not missing data, and it is recorded as `none_acceptable`.
  * On a beat WITH at least one selection, everything shown and not selected is
    REJECTED. The UI recorded no explicit rejects; they are derived here, and the
    derivation is only ever applied to beats the user actually judged.

    python3 pipeline/ingest_picks.py <pick-dir> [--write]
"""
import glob, json, os, pathlib, sys
P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P.parent / "match-trial"))
import candidates as C

OUT   = P.parent / "grammar" / "picks.json"
PASSES = P.parent / "grammar" / "passes"
FLAGS = P.parent / "grammar" / "beat-flags.json"
# The slate of record is the UI's OWN data file, not the live shotlist. The shotlist is
# regenerated constantly; the UI data is what was on screen when the human judged. Using
# the live shotlist silently rewrote `shown` and moved every metric (LOG 0035).
# --slate names the UI data file that was ON SCREEN for this pass. Pass 1 was judged
# in ui3-capacity; pass 2 in ui2, against a corpus 219 options wide. Hardcoding one of
# them would ingest a pass against a slate the reviewer never saw, which is exactly
# the LOG 0035 corruption in a new form.
SHOTS    = P / next((a.split("=")[1] for a in sys.argv if a.startswith("--slate=")),
                    "ui3-capacity/data.json")
SHOTS_ALT = P / "shotlist.capacity.json"
import datetime as _dt
SOURCE = {"source": "user",
          "collectedAt": next((a.split("=")[1] for a in sys.argv
                               if a.startswith("--collected=")),
                              _dt.date.today().isoformat()),
          "artifact": next((a.split("=")[1] for a in sys.argv
                            if a.startswith("--artifact=")), "unrecorded"),
          "slate": next((a.split("=")[1] for a in sys.argv
                         if a.startswith("--slate=")),
                        "ui3-capacity/data.json") + " (what was on screen)",
          "rule": "no selection = nothing was good enough; on a judged beat, "
                  "not selected = rejected",
          # Recorded on the PASS, because it is a statement about that sitting and
          # nothing else can reconstruct it later. Without this the derived
          # rejections on a zero-pick beat are indistinguishable from the silent
          # ones the rule exists to forbid. LOG 0080.
          "passedIsJudged": "--passed-is-judged" in sys.argv,
          "passedIsJudgedQuote": (
              "anything that got passed was a judgement not a unintentional skip. "
              "i selected what i wanted, commented when needed. everything else "
              "was of no value." if "--passed-is-judged" in sys.argv else None),
          "subsetOfSlate": "--subset" in sys.argv}

def build(pick_dir):
    docs = {os.path.basename(f)[:-5]: json.load(open(f))
            for f in sorted(glob.glob(os.path.join(pick_dir, "*.json")))}
    # hand-set flags, merged on top of anything the UI recorded. A flag can be set
    # without running a review pass, and survives a UI rebuild.
    manual = json.load(open(FLAGS)).get("beats", {}) if FLAGS.exists() else {}
    src = SHOTS if SHOTS.exists() else SHOTS_ALT
    raw = json.load(open(src))
    shots = {f"{s['passage']}-{s['beat']}": s
             for s in (raw["shots"] if isinstance(raw, dict) else raw)}
    print(f"slate of record: {src.relative_to(P.parent)}  "
          f"({sum(len(s['options']) for s in shots.values())} option slots)")
    # The pool lives in Codex's tree and can be unreadable. That must degrade to a
    # named, visible gap rather than a crash — an ingest that cannot verify ids is
    # still worth running, an ingest that dies takes the whole record with it.
    try:
        # content_class="*" — the SAME universe the slate was built from. Bare
        # load() hides the 9 scope-restricted templates, so validating against it
        # reported every scoped pick as "not in the pool" and refused the whole
        # ingest. The user picked a scoped timeline scene on two beats in pass 3.
        pool = {r["id"]: r for r in C.load(content_class="*")}
    except (PermissionError, FileNotFoundError) as e:
        pool = None
        print(f"WARN  pool unreadable ({type(e).__name__}); id membership NOT checked")

    beats, problems = {}, []
    for key, s in shots.items():
        d = docs.get(key, {})
        # A SIBLING IS SHOWN. The expander (LOG 0054) puts the rest of a family
        # behind a control on the scene that represents it — reachable and
        # selectable without spending a slate slot. Counting only `options` made
        # three of the user's pass-2 picks look like strays from outside the slate.
        # But a sibling is only shown if its parent was: it cannot be reached
        # otherwise, so the parent's presence is what admits it.
        shown = [o["id"] for o in s["options"]]
        shown += [i["id"] for o in s["options"] for i in (o.get("siblings") or [])]
        sel = [i for i in (d.get("sel") or []) if i in shown]
        stray = [i for i in (d.get("sel") or []) if i not in shown]
        if stray: problems.append(f"{key}: selected ids not in its slate: {stray}")
        beats[key] = {
            "beat": s["beat"], "passage": s["passage"], "job": s["job"],
            "quote": s["quote"],
            "shown": shown,
            "selected": sel,
            # derived, and ONLY where the user actually judged this beat
            # Derived rejection applies to what was ON SCREEN, not to siblings
            # behind an unopened expander. Deriving a rejection for a clip the user
            # never looked at would invent a judgment.
            "rejected": derive_rejections([o["id"] for o in s["options"]], sel),
            "noneAcceptable": not sel,
            "reviewed": key in docs,
            "rawBroll": bool(d.get("broll") or manual.get(key, {}).get("rawBroll")),
            # detection, not retrieval: this system's job is to say a beat wants a text
            # treatment, not to supply one. User ruling 2026-09-21.
            "needsTextTemplate": bool(d.get("needsText")
                                      or manual.get(key, {}).get("needsTextTemplate")),
            "note": (d.get("note") or "").strip() or None,
            "capacityImpossible": bool(s.get("floodNote") and
                                       "CAPACITY IMPOSSIBLE" in s["floodNote"]),
        }
    # A SUBSET pass carries only the beats it judged, so every manual flag on a
    # beat outside it is expected, not a typo. Checking unconditionally turned all
    # 40 flags into problems and blocked the write.
    if "--subset" not in sys.argv:
        for k in manual:
            if k not in beats: problems.append(f"beat-flags.json names unknown beat {k!r}")
    if pool is not None:
        for b in beats.values():
            for i in b["selected"] + b["rejected"]:
                if i not in pool: problems.append(f"{b['beat']}: {i} is not in the pool")
    return {"provenance": SOURCE, "beats": beats}, problems

def derive_rejections(shown, sel, passed_is_judged=None):
    """What was on screen and not chosen.

    With at least one pick, everything else shown is rejected — the user's rule
    from 2026-09-21, and not in dispute.

    With ZERO picks the default is to derive NOTHING. A zero is ambiguous: the
    user may have found the whole slate irrelevant, or never engaged with the
    beat, and manufacturing ten rejections from silence is not evidence.

    `passed_is_judged` collapses that ambiguity, and ONLY the user can set it.
    Pass 3, 2026-09-22: "anything that got passed was a judgement not a
    unintentional skip. i selected what i wanted, commented when needed.
    everything else was of no value." Per pass, never a default, never inferred
    from how the pass looks. LOG 0080.
    """
    if passed_is_judged is None:
        passed_is_judged = "--passed-is-judged" in sys.argv
    if not sel and not passed_is_judged:
        return []
    return [i for i in shown if i not in sel]


def carry_none_acceptable(fresh, prev, subset=None):
    """On a SUBSET pass, never re-derive noneAcceptable — carry the prior value.

    A pass that showed part of a beat's slate cannot observe that nothing in the
    whole slate was acceptable. ingest_picks derives noneAcceptable = not sel, and
    the merge below unions selections, rejections, shown and flags but NOT
    noneAcceptable — the new pass wins outright. So a subset pass with no pick on a
    served beat silently marks it unserved, and that field is what the standing
    rule "a beat with no selection is a finding" reads.

    Found on pass 3: beat 20-20, "something like that could've worked but whats
    here is fine". Served, picked nothing, would have been recorded as a gap.
    """
    if subset is None: subset = "--subset" in sys.argv
    if not subset: return fresh
    for k, v in fresh.items():
        old = prev.get(k)
        if old is not None and not v.get("selected"):
            v["noneAcceptable"] = bool(old.get("noneAcceptable"))
    return fresh


def merge_beats(fresh, prev):
    """Union this pass's beats onto the prior state and KEEP THE REST.

    picks.json is the current state across every pass, not a snapshot of the last
    one. A beat this pass did not judge keeps exactly what it had. Until
    2026-09-22 the loop walked only `fresh`, so a pass covering 8 of 40 beats
    wrote a picks.json with 8 beats: 103 selections became 21. Passes 1 and 2 both
    covered all 40, which is why it never fired. LOG 0079.

    A rejection does not expire — "not for this beat" stays true whether or not a
    later slate happened to show it again. A selection does not expire either: it
    is a permanent binding. The newest pass wins only on notes, which describe the
    beat rather than a verdict on a record.
    """
    out = dict(prev)                      # every prior beat survives by default
    for k, v in fresh.items():
        old_b = prev.get(k)
        if not old_b:
            out[k] = v
            continue
        v["selected"] = sorted(set(v["selected"]) | set(old_b.get("selected") or []))
        v["rejected"] = sorted((set(v["rejected"]) | set(old_b.get("rejected") or []))
                               - set(v["selected"]))
        v["shown"] = sorted(set(v["shown"]) | set(old_b.get("shown") or []))
        v["note"] = v["note"] or old_b.get("note")
        # A FLAG DOES NOT EXPIRE EITHER. rawBroll on 10-10 was set in pass 1; the
        # pass-2 UI recorded it false because the user did not re-tick a box, the
        # match-cut admission stopped firing, and a scene they had just SELECTED
        # fell out of the slate. A flag is a statement about the beat — "this
        # wants sourced footage" — not a verdict re-taken every pass. To clear
        # one, clear it in beat-flags.json.
        for f in ("rawBroll", "needsTextTemplate"):
            v[f] = bool(v.get(f)) or bool(old_b.get(f))
        out[k] = v
    return out


def main(argv):
    if len(argv) < 2: print(__doc__); return 2
    data, problems = build(argv[1])
    b = data["beats"]
    sel = sum(len(x["selected"]) for x in b.values())
    rej = sum(len(x["rejected"]) for x in b.values())
    none = [k for k, x in b.items() if x["noneAcceptable"]]
    print(f"beats {len(b)}   reviewed {sum(1 for x in b.values() if x['reviewed'])}"
          f"   selected {sel}   rejected (derived) {rej}"
          f"   acceptance {sel*100//max(sel+rej,1)}%")
    print(f"nothing acceptable on {len(none)} beat(s): {sorted(none)}")
    print(f"raw b-roll flagged:   {sorted(k for k,x in b.items() if x['rawBroll'])}")
    print(f"needs text template:  {sorted(k for k,x in b.items() if x['needsTextTemplate'])}")
    print(f"notes recorded: {sum(1 for x in b.values() if x['note'])}")
    for p in problems: print(f"  PROBLEM  {p}")
    if problems:
        print("\nNOT WRITTEN.")
        return 1
    # A review pass is a HISTORICAL RECORD of what a human was shown and chose. The
    # slates change constantly; re-ingesting against new slates silently rewrites
    # `shown` and every metric whose denominator uses it. Found 2026-09-21: rejected
    # moved 138 -> 148 and assert_without_data 0/12 -> 0/36 with no human involved.
    # So: refuse to overwrite a pass whose `shown` no longer matches.
    #
    # A NEW PASS IS NOT DRIFT. The guard above compares against the most recent pass
    # file, which is right when re-ingesting THAT pass and wrong when recording a
    # different one: pass 2 was judged against a corpus 219 options wide and its
    # `shown` differs from pass 1 on all 40 beats, by design. --new-pass says so
    # explicitly, and it still refuses to touch the existing pass file — a new pass
    # is written under its own name and the old one is never rewritten.
    PASSES.mkdir(exist_ok=True)
    new_pass = "--new-pass" in sys.argv
    prior = sorted(PASSES.glob("pass-*.json"))
    if prior and not new_pass:
        old = json.load(open(prior[-1]))
        drift = [k for k, v in old["beats"].items()
                 if k in b and v["shown"] != b[k]["shown"]]
        if drift:
            print(f"\nREFUSED. {len(drift)} beat(s) were shown different options when this "
                  f"pass was judged than they are now, e.g. {drift[:3]}.")
            print(f"Overwriting would rewrite history and silently move every metric.")
            print(f"The pass of record stays at {prior[-1].name}. To record a NEW pass, "
                  f"re-run the review against the current slates.")
            return 1
    if "--write" not in argv:
        print(f"\nclean. Re-run with --write to save {OUT.name}.")
        return 0
    stamp = data["provenance"]["collectedAt"]
    pf = PASSES / f"pass-{stamp}.json"
    if pf.exists():
        print(f"\nREFUSED. {pf.name} already exists and a pass file is immutable. "
              f"Pass --collected=<date> to record this as a different pass.")
        return 1
    pf.write_text(json.dumps(data, indent=1))

    # picks.json is the CURRENT state, merged across every pass. A REJECTION does
    # not expire: "not for this beat" stays true whether or not a later slate
    # happened to show it again. A SELECTION does not expire either — it is a
    # permanent binding (CLAUDE.md). The newest pass wins only on flags and notes,
    # which describe the beat rather than a verdict on a record.
    merged = data
    if OUT.exists():
        prev = json.load(open(OUT))["beats"]
        # Before unioning anything: a subset pass may not claim noneAcceptable.
        carry_none_acceptable(merged["beats"], prev)
        merged["beats"] = merge_beats(merged["beats"], prev)
        merged["provenance"]["mergedFrom"] = sorted(
            p.name for p in PASSES.glob("pass-*.json"))
    OUT.write_text(json.dumps(merged, indent=1))
    sel = sum(len(x["selected"]) for x in merged["beats"].values())
    rej = sum(len(x["rejected"]) for x in merged["beats"].values())
    print(f"\nwrote immutable record {pf.relative_to(P.parent)}")
    print(f"wrote {OUT.name} MERGED across all passes: {sel} selected, {rej} rejected")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
