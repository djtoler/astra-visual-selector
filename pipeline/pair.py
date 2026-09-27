#!/usr/bin/env python3
"""Beat + chosen template + chosen media -> which asset fills which slot.

THE MISSING JOIN. Measured 2026-09-26: 19 of 40 beats carry BOTH a template pick
and media picks, and nothing in the tree had ever put them together. shotlist.py
is template-only; build_media_review.py is media-only. The one artifact the whole
system exists to produce — this beat, this template, slot 3 gets this asset — did
not exist, so every fully-decided beat had nowhere to go.

IT PROPOSES. IT DOES NOT DECIDE. A proposal is arithmetic over what the template
declares (how many slots, how tight they crop, what kind they take) and what the
user already picked. The user pairs in the UI, their pairing outranks the
proposal, and the pairings become the evidence for rules that do not exist yet.
That order matters: the rules come from their choices, not the other way round.

RANKS, NEVER EXCLUDES, as everywhere else. An asset that fits no slot is reported
in `unplaced`, never dropped — and a template with more slots than the beat has
media reports a `shortfall` rather than padding.

    python3 pipeline/pair.py            propose, print a summary
    python3 pipeline/pair.py --write    write grammar/pairings.json
    python3 pipeline/pair.py --beat=15-15
"""
import json, pathlib, sys

P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P))
sys.path.insert(0, str(P.parent / "match-trial"))
import candidates as C
import media_candidates as M

OUT = P.parent / "grammar" / "pairings.json"
TPICKS = P.parent / "grammar" / "picks.json"
BRIEFS = P.parent / "grammar" / "media-briefs.json"


def template_picks(beat, raw=None):
    """Templates the user chose for a beat. ONE reader for picks.json's shape."""
    raw = raw if raw is not None else json.load(open(TPICKS))
    b = (raw.get("beats") or {}).get(beat) or {}
    out = []
    for k in ("selected", "picks", "selections", "chosen"):
        v = b.get(k)
        if isinstance(v, list):
            out += [x.get("id") if isinstance(x, dict) else x for x in v]
    seen, uniq = set(), []
    for t in out:
        if t and t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq


def slot_count(cap):
    """How many media wells. `media_slots` is the count; `slots_at_once` is how
    many are on screen together and is NOT a capacity (CLAUDE.md: only a SUBJECT
    axis answers how many things a template holds). Where media_slots is 0 the
    template holds no media and the beat needs none from it."""
    return int(cap.get("media_slots") or 0)


def fit(rec, wants):
    """0 right framing, 1 unknown, 2 wrong. Unknown sits in the MIDDLE — 436 of
    506 assets carry no framing tag, and ranking them last would hide most of the
    library behind a tag nobody has applied."""
    if not wants: return 0
    m = M.framing_matches(rec.get("framing"), wants)
    return 1 if m is None else (0 if m else 2)


def kfit(rec, kinds):
    if not kinds: return 0
    k = rec.get("kind") or M.kind_of(rec)
    if not k: return 1
    return 0 if k in kinds else 2


def propose(beat, tid, by_entity, order, pool, cap, _poolcache={}):
    """-> one slot per ENTITY, in the beat's order, then extras.

    A SLOT IS AN ENTITY, NOT A RANK. Beat 20-20 is "Travis Scott, sixty-seven
    billion. Kendrick, fifty-seven. Post Malone, fifty-six. Future, fifty-four"
    against a 5-slot bar list — the slot order IS the data order, and assigning
    by framing alone puts Kendrick's photo on Travis's bar. Picks already carry
    their entity in the tier key, so the mapping is free.

    A TEMPLATE WITH MORE SLOTS THAN ENTITIES IS RE-CUT, NOT SHORT. Standing rule:
    "an 8-slot template can be re-cut to 6 or 10, so declared capacity is a hint
    about scale, never a gate." Reporting a shortfall would invent a problem the
    user has already ruled is not one, so the surplus is reported as `recutTo`.
    """
    c = cap.get(tid) or {}
    if not _poolcache:
        _poolcache.update({r["id"]: r for r in C.load(content_class="*")})
    rec = _poolcache.get(tid, {})
    wants = M.framing_wanted(tid, rec.get("kind"))
    kinds = M.kind_wanted(tid, rec.get("kind"))
    n = slot_count(c)

    def best(cands, used):
        avail = [a for a in cands if a in pool and a not in used]
        if not avail: return None
        return sorted(avail, key=lambda a: (kfit(pool[a], kinds),
                                            fit(pool[a], wants),
                                            cands.index(a)))[0]

    slots, used = [], set()
    # one per entity first, in the order the beat names them
    for ent in order:
        if len(slots) >= n: break
        pick = best(by_entity.get(ent) or [], used)
        if pick: used.add(pick)
        r = pool.get(pick) or {}
        slots.append({"slot": len(slots) + 1, "forEntity": ent, "asset": pick,
                      "framing": r.get("framing"), "kind": r.get("kind"),
                      "fit": (None if not pick else
                              ["right framing", "framing unknown",
                               "wrong framing"][fit(r, wants)])})
    # then any remaining slots from whatever is left, entity unassigned
    rest = [a for v in by_entity.values() for a in v if a not in used]
    seen = set()
    rest = [a for a in rest if not (a in seen or seen.add(a))]
    while len(slots) < n:
        pick = best(rest, used)
        if pick is None: break
        used.add(pick)
        r = pool.get(pick) or {}
        slots.append({"slot": len(slots) + 1, "forEntity": None, "asset": pick,
                      "framing": r.get("framing"), "kind": r.get("kind"),
                      "fit": ["right framing", "framing unknown",
                              "wrong framing"][fit(r, wants)]})

    # ONE ASSET MAY FILL SEVERAL SLOTS. User on 25-25b, 2026-09-26: "j Cole in the
    # middle image and 2 instances of the mag cover on outside portraits... we need
    # some paring logic that can facilitate something like that." A test written
    # earlier the same day forbade it outright, which was my invention and not a
    # rule — grammar/MERGE.md already says the opposite: "fill unused slots with
    # declared loop repeats, never by inventing an entity."
    # DISTINCT FIRST, THEN REPEAT. Variety is still preferred, so a repeat only
    # appears once every distinct asset is placed, and it is MARKED so a reviewer
    # can see the difference between a library that is deep and one that is looping.
    # BOUNDED. First cut of this looped to fill any surplus and proposed
    # truth-population-field's 93 markers from 4 assets — 89 repeats, a 23x loop.
    # That is padding, and MERGE.md forbids padding in the same sentence that
    # permits repeats. A repeat may at most DOUBLE the distinct set: 2x reads as a
    # deliberate motif, 23x reads as nothing to show. Past that the honest answer
    # is a re-cut, which recutTo already reports.
    placed = [s for s in slots if s["asset"]]
    cap = len(slots) + len(placed)
    if placed and len(slots) < min(n, cap):
        i = 0
        while len(slots) < min(n, cap):
            src = placed[i % len(placed)]
            slots.append({"slot": len(slots) + 1, "forEntity": src["forEntity"],
                          "asset": src["asset"], "framing": src["framing"],
                          "kind": src["kind"], "fit": src["fit"], "repeat": True})
            i += 1
    everything = [a for v in by_entity.values() for a in v]
    seen = set()
    everything = [a for a in everything if not (a in seen or seen.add(a))]
    return {
        "templateId": tid, "mediaSlots": n,
        "slotsAtOnce": c.get("slots_at_once"), "structure": c.get("structure"),
        "wantsFraming": list(wants), "wantsKind": list(kinds),
        "slots": slots,
        "unplaced": [a for a in everything if a not in used],
        # surplus slots are a RE-CUT, not a shortfall — the user's standing rule
        "recutTo": (len(slots) if n and len(slots) < n else None),
        "repeats": sum(1 for s in slots if s.get("repeat")),
        "entitiesWithNoAsset": [e for e in order if not (by_entity.get(e) or [])],
    }


def main(argv):
    only = next((a.split("=")[1] for a in argv if a.startswith("--beat=")), None)
    write = "--write" in argv
    pool = M.load()
    cap = C._capability()
    raw = json.load(open(TPICKS))
    briefs = {b["brief"]: b for b in json.load(open(BRIEFS))["briefs"]}
    picks = M.picked()
    by_beat = {}
    for k, v in picks.items():
        by_beat.setdefault(k.split("::", 1)[0], []).extend(v)

    prev = json.load(open(OUT)) if OUT.exists() else {}
    out = {
        "_note": "Which asset fills which slot, per beat, per chosen template. "
                 "`proposed` is arithmetic over what the template declares and "
                 "what the user picked. `user` is what the user paired in the UI "
                 "and OUTRANKS the proposal — same standing as a pick.",
        "_rule": "Proposes, never decides. An asset that fits no slot is reported "
                 "in `unplaced`, never dropped; a template with more slots than "
                 "the beat has media reports a shortfall rather than padding.",
        "user": prev.get("user") or {},
        "beats": {},
    }
    ready = short = nomedia = 0
    for name in sorted(set(briefs) | set(raw.get("beats") or {})):
        tids = template_picks(name, raw)
        assets = by_beat.get(name) or []
        if not tids and not assets:
            continue
        by_ent = {}
        for k, v in picks.items():
            br, tier = k.split("::", 1)
            if br != name or not tier.startswith("e:"): continue
            by_ent.setdefault(tier[2:], []).extend(v)
        grp = picks.get(name + "::group") or []
        if grp: by_ent.setdefault("(group)", []).extend(grp)
        order = ((briefs.get(name) or {}).get("entities") or []) + \
                (["(group)"] if grp else [])
        props = [propose(name, t, by_ent, order, pool, cap) for t in tids]
        holding = [p for p in props if p["mediaSlots"]]
        if holding and assets:
            ready += 1
            short += sum(1 for p in holding if p["recutTo"])
        if holding and not assets:
            nomedia += 1
        out["beats"][name] = {
            "quote": (briefs.get(name) or {}).get("quote"),
            "entities": (briefs.get(name) or {}).get("entities") or [],
            "pickedAssets": assets,
            "proposed": props,
        }
    if only:
        b = out["beats"].get(only)
        print(json.dumps(b, indent=1, ensure_ascii=False) if b else f"no beat {only}")
        return 0
    print(f"   beats with a template and media   : {ready}")
    print(f"   beats whose templates want media but have none: {nomedia}")
    print(f"   templates needing a re-cut        : {short}")
    tot = sum(len(p["slots"]) for b in out["beats"].values() for p in b["proposed"])
    filled = sum(1 for b in out["beats"].values() for p in b["proposed"]
                 for s in p["slots"] if s["asset"])
    print(f"   slots across every chosen template: {tot}, of which {filled} "
          f"get an asset ({tot - filled} empty)")
    if not write:
        print("\n   DRY RUN — nothing written. Re-run with --write.")
        return 0
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"\n   wrote {OUT.relative_to(P.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
