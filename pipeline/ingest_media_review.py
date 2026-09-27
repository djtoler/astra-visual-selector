#!/usr/bin/env python3
"""Artifact review state -> grammar/media-picks.json + media-corrections.json.

WHY A SCRIPT AND NOT A HAND EDIT. The last hand-merge of a picks file dropped 32
beats silently (LOG 0031 on the template side, 0090 on the media side): the write
replaced the file instead of merging into it, and nothing noticed until the slate
stopped showing a validated pick. So this MERGES, refuses to shrink, and prints
the before and after of every count it touches.

WHAT IT DERIVES. On a brief the user judged, anything SHOWN and not selected is
rejected — explicit rejection is not required. Derived only where at least one
pick exists on that brief: a brief with zero picks means nothing shown was good
enough, which is `noneAcceptable`, a finding about the library rather than a
rejection of every card (standing rule, LOG 0090).

    python3 pipeline/ingest_media_review.py <harvest.json>           dry run
    python3 pipeline/ingest_media_review.py <harvest.json> --write   apply
"""
import copy, datetime, json, pathlib, sys

P = pathlib.Path(__file__).resolve().parent
PICKS = P.parent / "grammar" / "media-picks.json"
WRONG = P.parent / "grammar" / "media-corrections.json"
SLATE = P / "ui5-media" / "data.json"
ART = "https://claude.ai/artifact/GPKqCV8VTbWSpN6DxoXhLy"


def main(argv):
    src = next((a for a in argv[1:] if not a.startswith("--")), None)
    if not src:
        print(__doc__)
        return 2
    write = "--write" in argv
    h = json.load(open(src))
    slate = json.load(open(SLATE))
    prev = json.load(open(PICKS))
    out = copy.deepcopy(prev)

    shown = {}
    for b in slate["briefs"]:
        shown[f"{b['brief']}::group"] = [c["id"] for c in b["group"]]
        for e, v in b["individual"].items():
            shown[f"{b['brief']}::e:{e}"] = [c["id"] for c in v]

    picks = h["picks"]
    briefs_with_a_pick = {k.split("::", 1)[0] for k in picks}
    touched, new_tiers, rej_added = 0, 0, 0
    for b in slate["briefs"]:
        name = b["brief"]
        rec = out["briefs"].setdefault(name, {
            "brief": name, "job": b.get("job"), "quote": b.get("quote"),
            "entities": b.get("entities") or [], "gaps": b.get("gaps") or [],
            "tiers": {}})
        rec["gaps"] = b.get("gaps") or []
        tiers = ["group"] + [f"e:{e}" for e in b["entities"]]
        for tier in tiers:
            key = f"{name}::{tier}"
            sel = list(picks.get(key) or [])
            was = rec["tiers"].get(tier)
            if was is None:
                new_tiers += 1
            t = rec["tiers"].setdefault(tier, {"shown": [], "selected": [],
                                               "rejected": []})
            t["shown"] = shown.get(key, [])
            t["selected"] = sel
            if name in briefs_with_a_pick:
                # shown and not selected == rejected, on a brief they judged
                rej = [i for i in t["shown"] if i not in sel]
                before = len(t.get("rejected") or [])
                t["rejected"] = sorted(set((t.get("rejected") or [])) | set(rej))
                rej_added += len(t["rejected"]) - before
                t.pop("noneAcceptable", None)
            elif t["shown"]:
                # nothing on this brief was good enough — a FINDING, not a
                # rejection of every card
                t["noneAcceptable"] = True
            touched += 1
        n = h["notes"].get(name)
        if n:
            if n.get("note"): rec["note"] = n["note"]
            if n.get("entityNotes"): rec["entityNotes"] = n["entityNotes"]

    # ORPHAN TIERS. The artifact database never deletes a document, so a tier
    # whose entity label has since changed keeps its picks forever — 09-09::e:Jay
    # and 12-12a::e:Jay survive from before the gazetteer resolved `Jay` to
    # `Jay Rock`. Dropping them silently is the defect; so is resurrecting a label
    # the slate no longer uses. An orphan is ACCEPTABLE only when its picks are
    # already recorded under another tier of the SAME brief, and it is a hard stop
    # otherwise.
    valid = set()
    for b_ in slate["briefs"]:
        valid.add(f"{b_['brief']}::group")
        for e in b_["entities"]:
            valid.add(f"{b_['brief']}::e:{e}")
    orphans, unsafe = {}, {}
    for key, ids in picks.items():
        if key in valid:
            continue
        name = key.split("::", 1)[0]
        covered = set()
        for t in (out["briefs"].get(name, {}).get("tiers") or {}).values():
            covered |= set(t.get("selected") or [])
        missing = [i for i in ids if i not in covered]
        (unsafe if missing else orphans)[key] = missing or ids
    if orphans:
        print(f"   orphan tiers ignored (already covered on the same brief): "
              f"{len(orphans)}")
        for k, v in sorted(orphans.items()):
            print(f"     {k:26} {len(v)} pick(s), all present under another tier")
    if unsafe:
        print(f"\n   REFUSING: {len(unsafe)} tier(s) hold picks recorded NOWHERE else:")
        for k, v in sorted(unsafe.items()):
            print(f"     {k:26} {[i[:12] for i in v]}")
        print("   Losing these is the exact defect this script exists to prevent.")
        return 1

    out["provenance"] = dict(prev.get("provenance") or {})
    out["provenance"].update({
        "source": "user", "artifact": ART,
        "lastIngestedAt": datetime.datetime.now().strftime("%Y-%m-%d"),
        "slate": "pipeline/ui5-media/data.json (what was on screen)"})

    # --- corrections: MERGE, never replace ---
    w = json.load(open(WRONG))
    have = {(x["assetId"], x["entity"]) for x in w["wrong"]}
    incoming = {(a, e) for a, e in h["wrong"]}
    added = sorted(incoming - have)
    merged = sorted(have | incoming)
    w2 = dict(w)
    w2["wrong"] = [{"assetId": a, "entity": e} for a, e in merged]
    w2["_count"] = len(merged)
    w2["_lastIngestedAt"] = datetime.datetime.now().strftime("%Y-%m-%d")

    def cnt(d):
        return sum(len(t.get("selected") or [])
                   for b in d["briefs"].values() for t in b["tiers"].values())
    print(f"   briefs      {len(prev['briefs'])} -> {len(out['briefs'])}")
    print(f"   tiers        touched {touched}, new {new_tiers}")
    print(f"   selections  {cnt(prev)} -> {cnt(out)}")
    print(f"   rejections   +{rej_added} derived from what was shown and not picked")
    na = sum(1 for b in out["briefs"].values() for t in b["tiers"].values()
             if t.get("noneAcceptable"))
    print(f"   noneAcceptable tiers: {na}")
    print(f"   notes        {sum(1 for b in out['briefs'].values() if b.get('note'))} brief-level, "
          f"{sum(len(b.get('entityNotes') or {}) for b in out['briefs'].values())} entity-level")
    print(f"   corrections {len(have)} -> {len(merged)}  (+{len(added)})")

    if len(out["briefs"]) < len(prev["briefs"]) or cnt(out) < cnt(prev):
        print("\n   REFUSING: this write would LOSE briefs or selections. "
              "That is the defect this script exists to prevent.")
        return 1
    if not write:
        print("\n   DRY RUN — nothing written. Re-run with --write.")
        return 0
    PICKS.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    WRONG.write_text(json.dumps(w2, indent=1, ensure_ascii=False))
    print(f"\n   wrote {PICKS.name} and {WRONG.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
