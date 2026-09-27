#!/usr/bin/env python3
"""Media briefs -> pipeline/ui5-media/{data.json,media/}. Deterministic, no model calls.

The review surface for media_candidates.py. Each brief resolves to a GROUP tier
(one asset showing every named entity) and an INDIVIDUAL tier (one each), and the
user judges both.

TWO VERDICTS, NOT ONE. A media card can be wrong in two different ways and they
carry different information:

    pick    this asset serves this slot            beat-scoped
    W       this is not that person or entity      ENTITY-scoped, forever

User 2026-09-22: "w means wrong person or entity, do the self correction." The
contains-match is deliberately loose, so contamination is expected — "jay"
matches Jay Rock under a Jay-Z brief. If W only hid it on this beat, the same
photo would come back on every other beat naming Jay-Z. Entity-scoped means one
press pays forever, which is what makes the loose match affordable.

QUEUE BEHIND THE GRID. A W removes the card and the next candidate takes its
place, so the grid stays full. SHOW is what is on screen; QUEUE is what backfills.

    python3 pipeline/build_media_review.py            build from grammar/media-briefs.json
    python3 pipeline/build_media_review.py --show=8 --queue=8
"""
import base64, json, pathlib, re, shutil, subprocess, sys

P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P))
import media_candidates as M

BRIEFS = P.parent / "grammar" / "media-briefs.json"
# Entities a beat's VISUAL needs that its TEXT does not name — a spatial scene
# plots people from the data, not from the sentence. LOG 0117.
BEAT_ENTITIES = P.parent / "grammar" / "beat-entities.json"
# Picks read back from the review. Every one is SHIPPED for its brief whatever the
# rotation does — a selection is a decision (LOG 0090).
PICKS = P.parent / "grammar" / "media-picks.json"
FLAGS = P.parent / "grammar" / "beat-flags.json"
BINDINGS = P.parent / "grammar" / "bindings.json"
TEMPLATE_CACHE = P / ".thumbcache"
UI = P / next((a.split("=")[1] for a in sys.argv if a.startswith("--out=")), "ui5-media")
SHOW = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--show=")), 16))
QUEUE = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--queue=")), 12))
WIDE, SECS = 560, 6
SEGMENT_FAMILIES_PER_PAGE = 2


def segment_family(brief):
    """Keep lettered sides of one numbered segment in one review unit."""
    m = re.match(r"^(\d+-\d+)", str(brief or ""))
    return m.group(1) if m else str(brief or "")


def binding_names():
    """Read labels from the existing selector bindings; do not invent UI names."""
    if not BINDINGS.exists():
        return {}
    out = {}
    def walk(x):
        if isinstance(x, dict):
            if x.get("id") and x.get("name"):
                out.setdefault(x["id"], x["name"])
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(json.load(open(BINDINGS)))
    return out


def media_direction(brief, flag):
    """Expose saved direction at the decision; never infer a new treatment."""
    parts = []
    kinds = flag.get("wantsMediaKind") or []
    if kinds:
        parts.append("Media kind: " + ", ".join(kinds))
    if flag.get("rawBroll"):
        parts.append("B-roll / sequence direction")
    why = flag.get("wantsMediaKindWhy") or flag.get("why")
    if why:
        parts.append(why)
    if not parts and brief.get("selectedTemplates"):
        parts.append("Use the selected template candidates shown with this side.")
    return " — ".join(parts)


def template_previews(raw_briefs):
    """The cache first, then the SOURCE clip. A poster is never dropped.

    The cache-only version emitted poster: None for 6 of 47 templates whose clip
    was sitting on disk the whole time, so beats 01-01, 06-06, 11-11a, 12-12a,
    21-21a, 24-24, 27-27 and 28-28 showed a black rectangle where the treatment
    should be. Its docstring called that "missing means missing, not fabricated",
    but extracting a real frame from the template's own clip fabricates nothing —
    CLAUDE.md is explicit that the poster is not a size lever and that a <video>
    without one "is a black rectangle until the viewer presses play, so a grid of
    them shows nothing and the page cannot be skimmed."

    A template with no clip and no still anywhere is genuinely missing, and this
    RETURNS it in `noPreview` instead of leaving a silent None — a non-match has
    to say something.
    """
    sys.path.insert(0, str(P.parent / "match-trial"))
    import candidates as C
    pool = {r["id"]: r for r in C.load(content_class="*")}
    cap = C._capability()
    ids = sorted({t["id"] for b in raw_briefs
                  for t in (b.get("selectedTemplates") or [])})
    names = binding_names()
    media_dir = UI / "template-media"
    media_dir.mkdir(parents=True, exist_ok=True)
    for f in media_dir.iterdir():
        if f.is_file():
            f.unlink()
    TEMPLATE_CACHE.mkdir(parents=True, exist_ok=True)
    out, recovered, none_at_all = {}, [], []
    for tid in ids:
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", tid)
        jpg = TEMPLATE_CACHE / f"{tid}.jpg"
        mp4 = TEMPLATE_CACHE / f"{tid}.mp4"
        item = {"label": names.get(tid, tid), "poster": None, "clip": None}
        src = (pool.get(tid) or {}).get("clip")
        src = src if (src and pathlib.Path(src).exists()) else None
        still = (cap.get(tid) or {}).get("still_path")
        still = still if (still and pathlib.Path(still).exists()) else None

        if not mp4.exists() and src:
            # transcode into the cache at review width, so the next build is free
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src,
                            "-t", str(SECS), "-vf", f"scale={WIDE}:-2",
                            "-c:v", "libx264", "-crf", "30", "-preset", "veryfast",
                            "-movflags", "+faststart", "-an", str(mp4)], check=False)
            if mp4.exists():
                recovered.append(("clip", tid))
        if not jpg.exists():
            for candidate in (mp4 if mp4.exists() else None, src, still):
                if candidate and thumb(pathlib.Path(candidate), jpg):
                    recovered.append(("poster", tid))
                    break
        if jpg.exists():
            item["poster"] = ("data:image/jpeg;base64," +
                              base64.b64encode(jpg.read_bytes()).decode())
        if mp4.exists():
            dst = media_dir / f"{safe}.mp4"
            shutil.copy2(mp4, dst)
            item["clip"] = f"template-media/{safe}.mp4"
        if not item["poster"]:
            none_at_all.append(tid)
        out[tid] = item
    if recovered:
        print(f"   recovered {sum(1 for k,_ in recovered if k=='poster')} poster(s) and "
              f"{sum(1 for k,_ in recovered if k=='clip')} clip(s) the cache was missing")
    if none_at_all:
        print(f"   NO PREVIEW POSSIBLE for {len(none_at_all)}: {none_at_all} "
              "(no clip and no still on disk — a sourcing gap, not a build failure)")
    return out


def thumb(src, dst_jpg):
    """A real frame, never a placeholder. CLAUDE.md: shrink the asset, never drop
    the poster."""
    if src.suffix.lower() in (".mp4", ".mov", ".m4v", ".webm"):
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.5", "-i", str(src),
               "-frames:v", "1", "-vf", f"scale={WIDE}:-2", str(dst_jpg)]
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
               "-vf", f"scale={WIDE}:-2", str(dst_jpg)]
    subprocess.run(cmd, check=False)
    return dst_jpg.exists()


def main():
    d = json.load(open(BRIEFS))
    raw_briefs = d["briefs"]
    pool = M.load()
    wrong = M.corrections()
    briefs, need = [], set()
    # What each entity has already shown on an EARLIER brief. Drake appears on
    # four briefs and gave the identical top-8 all four times; this is what stops
    # the fourth being the first again.
    # WHEN each entity last saw an asset, not merely whether. The narration runs 804
    # seconds and every beat carries a start time, so an asset shown at 0:20 is cool
    # again by 3:20 rather than demoted for the rest of the video. LOG 0126.
    seen_for = {}
    shown_at = {}
    times = {}
    _sl = P / "shotlist.capacity.json"
    if _sl.exists():
        for x in json.load(open(_sl)):
            if x.get("start") is not None:
                times[f"{x['passage']}-{x['beat']}"] = x["start"]
    picked = M.picked()
    # A PICK THAT CANNOT SHIP IS RECORDED, NEVER DROPPED. Two shapes, and the
    # second was being lost silently until 2026-09-26:
    #   the asset left the pool, so nothing can show it;
    #   the asset is in the pool but its TIER no longer exists. A group tier asks
    #     for one asset carrying every entity on the beat. 28-28 now names ten
    #     artists because a spatial scene plots from the data (LOG 0117), so no
    #     single photograph can serve it and the tier is meaningless for that beat.
    #     The pick was made against a slate that offered a Travis-Scott-only photo
    #     as a Drake-and-Travis group asset, which was itself the defect fixed in
    #     LOG 0104.
    displaced = []
    for key, ids in sorted(picked.items()):
        brief, tier = key.split("::", 1)
        for aid in ids:
            if aid not in pool:
                displaced.append({"brief": brief, "tier": tier, "assetId": aid,
                                  "reason": "not_in_production_ready"})
    # The BEAT's own declared media kind. Not extracted — measured attempts to
    # extract it failed (LOG 0098), so the user declares it in the file that
    # already holds per-beat declarations.
    flags = (json.load(open(FLAGS)).get("beats") or {}) if FLAGS.exists() else {}

    raw_by_family = {}
    for raw in raw_briefs:
        raw_by_family.setdefault(segment_family(raw.get("brief")), []).append(raw)

    _be = json.load(open(BEAT_ENTITIES)) if BEAT_ENTITIES.exists() else {}
    extra = _be.get("beats") or {}
    SUBJECT = _be.get("_subject") or {}
    for b in raw_briefs:
        # UNION, never replace: the text's own entities always survive.
        more = (extra.get(b["brief"]) or {}).get("entities") or []
        # THE SUBJECT IS ON EVERY BEAT. A single-subject documentary compares
        # everything against its subject, and 12 of the 18 beats that never named
        # Drake reach him by pronoun or implication, which no gazetteer resolves.
        # Declared, not extracted — see grammar/beat-entities.json _subject.
        subj = (SUBJECT or {}).get("entity")
        if subj: more = list(more) + [subj]
        if more:
            b["entities"] = sorted(set(b["entities"]) | set(more))
        # FRAMING COMES FROM THE TEMPLATE THE USER CHOSE. A spatial node wants a
        # tight crop and a hero billboard wants half-body or wider; the same
        # entity needs different assets depending on what is rendering it.
        # Where a beat carries several chosen templates the wants are UNIONED —
        # each is a legitimate destination, so an asset that suits any of them
        # is useful. LOG 0094.
        wants = tuple(sorted({f for t in (b.get("selectedTemplates") or [])
                              for f in M.framing_wanted(t["id"], t.get("kind"))}))
        # A beat's OWN declaration wins outright: the template says what its slots
        # can take, the user says what this beat should show, and the second is
        # the more specific statement. Where the beat is silent, the template
        # decides.
        declared = (flags.get(b["brief"]) or {}).get("wantsMediaKind") or []
        kinds = tuple(declared) if declared else tuple(sorted(
            {k for t in (b.get("selectedTemplates") or [])
             for k in M.kind_wanted(t["id"], t.get("kind"))}))
        # The beat's own words rank what its entity match returns. LOG 0113.
        r = M.resolve(b["entities"], pool=pool, wrong=wrong, wants=wants,
                      kinds=kinds, quote=b.get("quote") or "")
        now = times.get(b["brief"])
        def pack(recs, entity, tier):
            used = seen_for.setdefault(entity, set())
            hist = shown_at.setdefault(entity, {})
            pin = set(picked.get(b["brief"] + "::" + tier) or [])
            recs = M.spread(recs, SHOW + QUEUE, used=used, pin=pin,
                            history=hist, now=now)
            used.update(x["id"] for x in recs[:SHOW])
            if now is not None:
                for x in recs[:SHOW]:
                    hist.setdefault(x["id"], []).append(now)
            out = []
            for rec in recs:
                out.append({"id": rec["id"], "entity": entity,
                            "mediaType": rec["media_type"],
                            "framing": rec["framing"],
                            "hasCutout": rec["has_cutout"],
                            "shownAs": ("cutout" if rec["has_cutout"] else
                                        ("preview" if rec.get("display") != rec["path"]
                                         else "original")),
                            "why": M._why(rec, entity),
                            "fit": (0 if not wants else
                                    (0 if rec.get("framing") in wants else
                                     (1 if not rec.get("framing") else 2))),
                            "kind": rec.get("kind")})
                need.add(rec["id"])
            return out
        family = segment_family(b.get("brief"))
        paired = []
        for other in raw_by_family.get(family, []):
            if other.get("brief") == b.get("brief"):
                continue
            paired.append({
                "brief": other.get("brief"), "quote": other.get("quote"),
                "job": other.get("job"),
                "mediaDirection": media_direction(
                    other, flags.get(other.get("brief")) or {}),
                "templates": other.get("selectedTemplates") or [],
            })
        briefs.append({
            "brief": b["brief"], "beat": b.get("beat"), "job": b.get("job"),
            "quote": b.get("quote"), "role": b.get("role"),
            "segmentFamily": family,
            "mediaDirection": media_direction(b, flags.get(b["brief"]) or {}),
            "pairedSides": paired,
            # User note on 11-11b: "it would be good to know which template
            # options were selected so I can match them with assets." The data
            # was already in picks.json and the grid simply never showed it.
            "templates": b.get("selectedTemplates") or [],
            "wantsFraming": list(wants),
            "wantsKind": list(kinds),
            "kindFrom": ("beat" if declared else ("template" if kinds else None)),
            "entities": r["entities"],
            "slotsNeeded": r["slotsNeeded"],
            "gaps": r["gaps"],
            "group": pack(r["group"], r["entities"][0] if r["entities"] else "", "group"),
            "individual": {e: pack(v, e, "e:" + e) for e, v in r["individual"].items()},
        })

    shipped = set()
    for b_ in briefs:
        for c in b_["group"]:
            shipped.add((b_["brief"], "group", c["id"]))
        for e, v in b_["individual"].items():
            for c in v:
                shipped.add((b_["brief"], "e:" + e, c["id"]))
    known = {(d["brief"], d["tier"], d["assetId"]) for d in displaced}
    by_brief = {b_["brief"]: b_ for b_ in briefs}
    for key, ids in sorted(picked.items()):
        brief, tier = key.split("::", 1)
        if brief not in by_brief: continue
        for aid in ids:
            if (brief, tier, aid) in shipped or (brief, tier, aid) in known:
                continue
            b_ = by_brief[brief]
            if tier == "group" and not b_["group"]:
                why = ("group_tier_not_applicable: this beat names "
                       f"{len(b_['entities'])} entities and no single asset can "
                       "carry them all")
            elif tier.startswith("e:") and tier[2:] not in b_["individual"]:
                why = f"entity_no_longer_on_this_beat: {tier[2:]}"
            else:
                why = "no_longer_matches_this_entity"
            displaced.append({"brief": brief, "tier": tier, "assetId": aid,
                              "reason": why})

    (UI / "media").mkdir(parents=True, exist_ok=True)
    for f in (UI / "media").iterdir():
        f.unlink()

    thumbs, hasclip, missing = {}, {}, []
    for aid in sorted(need):
        rec = pool[aid]
        # The PROCESSED file, where one exists — a cutout is what actually gets
        # placed, and judging the raw import means judging something that will
        # never be used. LOG 0093.
        src = pathlib.Path(rec.get("display") or rec["path"])
        if not src.exists():
            missing.append(aid)
            continue
        is_vid = rec["media_type"] == "video"
        hasclip[aid] = is_vid
        if is_vid:
            dst = UI / "media" / f"{aid}.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                            "-t", str(SECS), "-vf", f"scale={WIDE}:-2", "-c:v", "libx264",
                            "-crf", "30", "-preset", "veryfast", "-movflags",
                            "+faststart", "-an", str(dst)], check=False)
            if not dst.exists():
                shutil.copy(src, dst)
        jpg = UI / f".{aid}.jpg"
        if thumb(src, jpg):
            thumbs[aid] = "data:image/jpeg;base64," + base64.b64encode(jpg.read_bytes()).decode()
            jpg.unlink()
        elif not is_vid:
            missing.append(aid)

    previews = template_previews(raw_briefs)
    json.dump({"briefs": briefs, "thumbs": thumbs, "hasClip": hasclip,
               "templatePreviews": previews,
               "segmentFamiliesPerPage": SEGMENT_FAMILIES_PER_PAGE,
               "displacedPicks": displaced,
               "show": SHOW, "queue": QUEUE,
               "library": {"assets": len(pool), "corrections": len(wrong)}},
              open(UI / "data.json", "w"))
    mb = (UI / "data.json").stat().st_size / 1e6
    vid = sum(f.stat().st_size for f in (UI / "media").iterdir()) / 1e6
    cards = sum(len(b["group"]) + sum(len(v) for v in b["individual"].values())
                for b in briefs)
    print(f"briefs {len(briefs)} | distinct assets {len(need)} | card slots {cards}")
    print(f"gaps: {sorted({g for b in briefs for g in b['gaps']}) or 'none'}")
    print(f"prior picks requiring replacement: {len(displaced)}")
    print(f"thumbs {len(thumbs)} | clips {sum(hasclip.values())} | "
          f"data.json {mb:.1f} MB | media {vid:.1f} MB | total {mb + vid:.1f} MB of 64")
    if missing:
        print(f"no readable file for {len(missing)}: {missing[:5]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
