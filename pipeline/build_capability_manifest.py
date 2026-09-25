#!/usr/bin/env python3
"""Build the capability-pass manifest for Codex.

    python3 pipeline/build_capability_manifest.py <outfile.json>

Why this is a script and not a paste-in.

I hand-rolled this manifest four times in one session and the fourth produced a
defect Codex caught on preflight: it listed seven `text-list-carousel` scenes the
user had REMOVED from the corpus. They were still in capability.json — correctly,
as history — and the builder read capability.json directly. The receiver validates
against `set(C.load()) | set(C.local_pending())`, so the run would have spent money
on seven clips whose results could never be ingested.

THE RULE THIS ENFORCES: a manifest may only name an id the receiver can accept.
It is checked here, at the point of construction, rather than trusted.
"""
import json, os, sys, pathlib, hashlib, collections

P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P.parent / "match-trial"))
import candidates as C

PROMPT = P.parent / "prompts" / "PROMPT-describe-clip.md"
CAP = P.parent / "grammar" / "capability.json"
LOCAL = P.parent / "grammar" / "local-templates.json"
PREV_SHA = "d58028d6ad18e58aa0d6b5fcf7a8075a82e33da191af2bff71262e97c66b09b3"


# The eight beats whose requirement no record can currently serve, and the encoding
# each needs. Derived from grammar/perceptible.json; listed here so the targeted
# scope is auditable rather than recomputed differently each time.
GAP_BEATS = {"04-04": "aggregate", "13-13a": "aggregate", "18-18": "aggregate",
             "22-22": "aggregate", "01-01": "derivation", "21-21b": "derivation",
             "28-28": "overlap", "30-30a": "absence"}


def gap_scope():
    """Only records that could ever serve the eight gap beats.

    The widened vocabulary (LOG 0068) means any record MIGHT now carry one of the
    three temporal relations — but measuring one that is bound to none of these
    jobs answers no open question. 200 records was "where the terms could appear";
    this is "where it would change a decision".
    """
    g = json.load(open(P.parent / "grammar" / "bindings.json"))
    shots = {f"{x['passage']}-{x['beat']}": x
             for x in json.load(open(P / "shotlist.capacity.json"))}
    ids = set()
    for b in GAP_BEATS:
        ids |= {r["id"] for r in (g.get(shots[b]["job"]) or [])}
    # every spatial and the hero: a relation performed over time is likeliest there,
    # and four of them have never been measured at all
    ids |= {r["id"] for r in C.load(content_class="*")
            if r.get("kind") in ("cinematic_3d", "layered_scene")}
    return ids


def still_of(rid):
    """A frame that already exists for a record with no clip."""
    sys.path.insert(0, str(P))
    import build_review
    try:
        st = build_review.still_path(rid)
    except Exception:
        return None
    return str(st) if st and os.path.exists(st) else None


def gap_coverage(rows, png):
    """How much of each gap beat's bound set this run can actually reach.

    Coverage is UNEVEN and the averages hide it: beat 30a's whole bound set of 42
    has clips, while 04 and 22 have five of six bound records with NO CLIP — they
    are unrendered infographics. A run cannot answer a question about records it
    cannot watch, and saying so before the spend is the point of this block.
    """
    g = json.load(open(P.parent / "grammar" / "bindings.json"))
    shots = {f"{x['passage']}-{x['beat']}": x
             for x in json.load(open(P / "shotlist.capacity.json"))}
    named = {r["id"] for r in rows} | {r["id"] for r in png}
    out = {}
    for b, enc in GAP_BEATS.items():
        bound = {r["id"] for r in (g.get(shots[b]["job"]) or [])}
        out[b] = {"needs": enc, "bound": len(bound),
                  "inThisRun": len(bound & named),
                  "noClipSoUnanswerable": len(bound - named)}
    return out


def build(scope=None):
    sha = hashlib.sha256(PROMPT.read_bytes()).hexdigest()
    cap = json.load(open(CAP))
    pool = {r["id"]: r for r in C.load()}
    local = {r["id"]: r for r in json.load(open(LOCAL))["records"]}

    # THE GUARD. Exactly the union ingest_capability.py validates against.
    known = set(pool) | set(C.local_pending())

    stale = {i for i, r in cap.items()
             if (r.get("text_slots") or 0) >= 1
             and (r.get("readable") or ["none"]) == ["none"]}
    provisional = {i for i, r in cap.items() if r.get("source") == "claude-visual"}
    unmeasured = set(pool) - set(cap)
    pending = set(C.local_pending())

    if scope == "gap":
        wanted = gap_scope() | unmeasured | pending
    else:
        wanted = stale | provisional | unmeasured | pending
    # Removed records stay in capability.json as HISTORY and must never be re-bought.
    dropped = sorted(wanted - known)
    wanted &= known

    ovr = set(C.eligibility_overrides())

    def clip_of(i):
        if i in local: return local[i].get("clip")
        return (cap.get(i) or {}).get("clip_path") or (pool.get(i) or {}).get("clip")

    rows, png, noclip = [], [], []
    for i in sorted(wanted):
        r = local.get(i, {})
        why = ("re-measure: provisional, read by Claude not measured" if i in provisional
               else "re-measure: readable vocabulary" if i in stale
               else "new: calibrated spatial layout" if i in ovr
               else f"new: user pack ({r['userIntent']})" if r.get("userIntent")
               else "new: user-specified span" if i in local
               # a record already measured, re-run because the VOCABULARY widened.
               # Without this case it fell through to "never measured", which is
               # false and would have told Codex 64 measured records had no prior.
               else "re-measure: widened vocabulary" if i in cap
               else "never measured")
        e = {"id": i, "clip": clip_of(i), "why": why}
        if r.get("userIntent"): e["userIntentDoNotUse"] = r["userIntent"]
        if r.get("profile"): e["profile"] = r["profile"]
        if e["clip"] and os.path.exists(e["clip"]): rows.append(e)
        else:
            # NO CLIP IS NOT NO ASSET. 46 infographics have never been measured at
            # all — no carries, no readable, nothing — because the pass is a video
            # pass and they have no video. They are not marginal: 83 bindings, 27
            # beats, 19 of the user's own selections. Every supply figure quoted
            # before 2026-09-22 silently excluded them, so "aggregate is zero across
            # 396 records" was a statement about a corpus they were not in.
            # They all have stills. A still answers most of the vocabulary.
            st = still_of(i)
            if st: png.append({"id": i, "still": st, "why": why})
            else: noclip.append(i)

    return {
      "purpose": "Re-measure under the changed prompt, plus everything unmeasured.",
      "prompt": str(PROMPT.resolve()), "promptSha256": sha,
      "previousPromptSha256": PREV_SHA,
      "whatChanged": (
        "THE HEADLINE: a relation now counts whether it is shown in ONE FRAME or "
        "ACROSS THE CLIP. Every `carries` definition used to read as a claim about a "
        "single frame while everything temporal lived in `staging`, so a relation the "
        "clip PERFORMS was recorded by neither field. Across 396 records and three "
        "versions of this prompt, `overlap`, `aggregate` and `absence` were each "
        "assigned ZERO times — while nine records were staged accumulates_to_total "
        "and a scene built expressly to show an intersection came back as "
        "`difference`. A term never once used is more likely inoperable than "
        "universally absent. So: if the clip ENDS somewhere, judge what it ends on. "
        "If groups reduce, if parts gather, if an item leaves, that is the relation, "
        "and record the matching `staging` too.\n"
        "  overlap   ... OR across the clip as two sets reducing until only the "
        "members common to both remain\n"
        "  aggregate ... OR across the clip as items gathering, stacking or summing "
        "into a single figure\n"
        "  absence   ... or shown by an item leaving and not being replaced\n"
        "TWO TERMS ADDED: carries `parity` (two or more things read as THE SAME, "
        "deliberately equal, not merely unranked) and implies `independence` (a "
        "layout suggesting two figures are unrelated facts side by side).\n"
        "EARLIER, still in force: `readable` gained `label` and `statement`."),
      "gapBeatCoverage": gap_coverage(rows, png),
      "whyThisScope": (
        "Not every record — only those that could serve the eight beats whose "
        "requirement nothing currently meets: 04, 13a, 18, 22 need `aggregate`; 01 "
        "and 21b need `derivation`; 28 needs `overlap`; 30a needs `absence`. "
        "Measuring a record bound to none of their jobs answers no open question."),
      "model": "gemini-3.8-flash",
      "IMPORTANT_provisional": (
        f"{len(provisional & wanted)} records carry source:\"claude-visual\", "
        "provisional:true. Claude read them from 4fps frame grids at the user's "
        "explicit direction because this run had not happened yet. THEY ARE NOT "
        "MEASUREMENTS and your result replaces them outright — do not treat them as "
        "a prior, do not try to agree with them. If your reading differs, yours is "
        "the one that counts."),
      "IMPORTANT_userIntent": (
        "Some entries carry `userIntentDoNotUse` — the user's label for the pack: "
        "OVERLAP, DERIVATION, LISTS, BAR CHART OPTION. It records what they REACHED "
        "FOR the pack to do and is NOT evidence. Four `carries` values are at or "
        "near zero across the corpus and eight beats demand them, so there is real "
        "pressure to find them. Do not find them because a label says so. A clip "
        "that does not carry `overlap` must come back without it — one pack labelled "
        "OVERLAP already turned out to carry share_of_whole instead."),
      "removedFromScope": {
        "why": ("Ids present in capability.json but NOT in "
                "set(C.load()) | set(C.local_pending()). The user removed these "
                "records from the corpus; their capability records remain as "
                "history and must never be re-bought. Excluded at build time — "
                "your 030 preflight caught this when it was not."),
        "count": len(dropped), "ids": dropped},
      "deliverTo": "/Users/dwaynetoler/timeline/handoff/inbox/",
      "ingest": "python3 pipeline/ingest_capability.py <file> --write",
      "costNote": (
        f"~${len(rows)*1.947/167:.2f} for {len(rows)} clips at the measured round-2 "
        f"rate. The {len(png)} stills are a single image each against ~2,600 video "
        f"tokens per clip, so they should land near ${len(png)*0.003:.2f} — but that "
        f"is EXTRAPOLATED, not measured, because no still has ever been run through "
        f"this prompt. Please report the actual split."),
      "stills": {
        "instruction": (
          "THESE HAVE NO CLIP, ONLY A STILL. Judge exactly what one frame shows and "
          "no more. Most of the vocabulary is answerable from a still: whether size "
          "encodes magnitude, whether parts read as portions of a whole, whether a "
          "shared baseline makes heights comparable, what text is on screen. "
          "WHAT YOU CANNOT SEE, SAY SO: `staging` is unknowable from one frame — "
          "return \"unknown\" — and the across-the-clip forms of aggregate, overlap "
          "and absence cannot be judged, so record those ONLY if the single frame "
          "shows them. A chart displaying parts inside a visible total carries "
          "aggregate in one frame; a chart that animates the pooling does not show "
          "that here. Add \"still_only\" to `unclear` on every one of these."),
        "whyTheyMatter": (
          "Never measured, any of them — no carries, no readable, no slot counts. "
          "Not marginal: 83 bindings across 16 jobs, 77 option slots across 27 "
          "beats, and 19 of the user's own selections. They reached candidate pools "
          "through bind.py, which reads the prose description, while the capability "
          "pass never asked them anything. Every supply figure quoted before "
          "2026-09-22 excluded them silently."),
        "count": len(png), "records": png},
      "cannotRun": {"count": len(noclip), "why": "unrendered infographics",
                    "ids": noclip},
      "count": len(rows), "clips": rows}


def main():
    if len(sys.argv) < 2: print(__doc__); return 2
    scope = "gap" if "--gap" in sys.argv else None
    doc = build(scope)
    known = {r["id"] for r in C.load()} | set(C.local_pending())
    bad = [c["id"] for c in doc["clips"] if c["id"] not in known]
    assert not bad, f"manifest names ids the receiver will refuse: {bad}"
    missing = [c["id"] for c in doc["clips"] if not os.path.exists(c["clip"])]
    assert not missing, f"manifest names clips that do not exist: {missing}"
    pathlib.Path(sys.argv[1]).write_text(json.dumps(doc, indent=2))
    print(f"{doc['count']} clips   stills {doc['stills']['count']}   "
          f"cannotRun {doc['cannotRun']['count']}   {doc['costNote']}")
    print(f"excluded as removed-from-corpus: {doc['removedFromScope']['count']}")
    for k, v in collections.Counter(c["why"] for c in doc["clips"]).most_common():
        print(f"   {v:4}  {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
