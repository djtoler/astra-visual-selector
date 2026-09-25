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
import base64, json, pathlib, shutil, subprocess, sys

P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P))
import media_candidates as M

BRIEFS = P.parent / "grammar" / "media-briefs.json"
# Picks read back from the review. Every one is SHIPPED for its brief whatever the
# rotation does — a selection is a decision (LOG 0090).
PICKS = P.parent / "grammar" / "media-picks.json"
FLAGS = P.parent / "grammar" / "beat-flags.json"
UI = P / next((a.split("=")[1] for a in sys.argv if a.startswith("--out=")), "ui5-media")
SHOW = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--show=")), 16))
QUEUE = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--queue=")), 12))
WIDE, SECS = 560, 6


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
    pool = M.load()
    wrong = M.corrections()
    briefs, need = [], set()
    # What each entity has already shown on an EARLIER brief. Drake appears on
    # four briefs and gave the identical top-8 all four times; this is what stops
    # the fourth being the first again.
    seen_for = {}
    picked = M.picked()
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

    for b in d["briefs"]:
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
        r = M.resolve(b["entities"], pool=pool, wrong=wrong, wants=wants, kinds=kinds)
        def pack(recs, entity, tier):
            used = seen_for.setdefault(entity, set())
            pin = set(picked.get(b["brief"] + "::" + tier) or [])
            recs = M.spread(recs, SHOW + QUEUE, used=used, pin=pin)
            used.update(x["id"] for x in recs[:SHOW])
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
        briefs.append({
            "brief": b["brief"], "beat": b.get("beat"), "job": b.get("job"),
            "quote": b.get("quote"), "role": b.get("role"),
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

    json.dump({"briefs": briefs, "thumbs": thumbs, "hasClip": hasclip,
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
