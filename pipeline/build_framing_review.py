#!/usr/bin/env python3
"""Templates that hold media and have no framing rule -> pipeline/ui6-framing/.

WHY. grammar/framing-rules.json covers cinematic_3d and layered_scene, declared
from the user's words. after_effects and infographic templates are the majority
of what actually renders and have no rule, so every asset ranks the same for
them regardless of how the slot crops.

This cannot be inferred. Nothing in the capability measurement says how close a
media well crops — `media_slots: 30` says how many, never how tight. So the user
looks at the clip and says. LOG 0095.

Only templates the user has ALREADY CHOSEN on a beat, and only those that hold
media: a rule for a template nothing renders is drift.

    python3 pipeline/build_framing_review.py
"""
import base64, json, os, pathlib, shutil, subprocess, sys

P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P))
sys.path.insert(0, str(P.parent / "match-trial"))
import candidates as C
import media_candidates as M

BRIEFS = P.parent / "grammar" / "media-briefs.json"
UI = P / "ui6-framing"
WIDE, SECS = 640, 7


def main():
    pool = {r["id"]: r for r in C.load(content_class="*")}
    cap = C._capability()
    d = json.load(open(BRIEFS))
    used = {}
    for b in d["briefs"]:
        for t in (b.get("selectedTemplates") or []):
            used.setdefault(t["id"], []).append(b["brief"])

    cards = []
    for tid, beats in sorted(used.items()):
        rec, c = pool.get(tid) or {}, cap.get(tid) or {}
        if M.framing_wanted(tid, rec.get("kind")):
            continue                                   # already ruled on
        if not (c.get("media_slots") or 0):
            continue                                   # holds no media
        cards.append({
            "id": tid, "kind": rec.get("kind"),
            "beats": sorted(set(beats)),
            "mediaSlots": c.get("media_slots"),
            "slotsAtOnce": c.get("slots_at_once"),
            "structure": c.get("structure"),
            "asserts": c.get("asserts"),
            "title": rec.get("title"),
            "_clip": rec.get("clip"), "_still": c.get("still_path"),
        })

    (UI / "media").mkdir(parents=True, exist_ok=True)
    for f in (UI / "media").iterdir():
        f.unlink()

    thumbs, hasclip, missing = {}, {}, []
    for card in cards:
        tid = card["id"]
        clip = card.pop("_clip")
        still = card.pop("_still")
        src = clip if (clip and os.path.exists(clip)) else None
        if src:
            hasclip[tid] = True
            dst = UI / "media" / f"{tid}.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src,
                            "-t", str(SECS), "-vf", f"scale={WIDE}:-2", "-c:v", "libx264",
                            "-crf", "30", "-preset", "veryfast", "-movflags",
                            "+faststart", "-an", str(dst)], check=False)
            if not dst.exists():
                shutil.copy(src, dst)
        else:
            hasclip[tid] = False
        # a poster ALWAYS, from the clip or the still. CLAUDE.md: shrink the
        # asset, never drop the thing being reviewed.
        poster_src = src or (still if still and os.path.exists(still) else None)
        if poster_src:
            jpg = UI / f".{tid}.jpg"
            args = (["-ss", "0.5"] if src else []) + ["-i", poster_src]
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + args
                           + (["-frames:v", "1"] if src else [])
                           + ["-vf", f"scale={WIDE}:-2", str(jpg)], check=False)
            if jpg.exists():
                thumbs[tid] = ("data:image/jpeg;base64,"
                               + base64.b64encode(jpg.read_bytes()).decode())
                jpg.unlink()
        if tid not in thumbs:
            missing.append(tid)

    rules = json.load(open(P.parent / "grammar" / "framing-rules.json"))
    json.dump({"cards": cards, "thumbs": thumbs, "hasClip": hasclip,
               "scale": rules["_scale"],
               "alreadyRuled": rules["byKind"]},
              open(UI / "data.json", "w"))
    mb = (UI / "data.json").stat().st_size / 1e6
    vid = sum(f.stat().st_size for f in (UI / "media").iterdir()) / 1e6
    print(f"templates needing a rule {len(cards)} | clips {sum(hasclip.values())} | "
          f"stills {len(cards) - sum(hasclip.values())}")
    print(f"thumbs {len(thumbs)} | data.json {mb:.1f} MB | media {vid:.1f} MB | "
          f"total {mb + vid:.1f} MB of 64")
    if missing:
        print(f"NO POSTER for {len(missing)}: {missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
