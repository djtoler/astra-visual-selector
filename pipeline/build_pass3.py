#!/usr/bin/env python3
"""The unseen slice: every front card in the live slate the user has never been shown.

WHY THIS EXISTS. After pass 2 the slate looked complete — 36 of 40 beats served,
103 selections, every one reachable. It is not complete. 104 of the 281 front cards
in the live slate have never been on screen. They were bound to the beat's job the
whole time; the slate caps at SLATE_LIMIT with one scene per family, so the top
families held every slot until the user rejected them, and the next tier moved up.
Measured on beat 05-05a: 22 records bound, 10 shown, 13 rejected, and 6 of today's
10 have never been seen.

So a third pass is not a rerun. This builds a UI over ONLY the unseen cards, with
the user's existing pick alongside for comparison — the question on each beat is not
"choose one" but "does any of these beat what you already chose".

Reuses build_review's clip and still resolution rather than duplicating it; the
transcode budget follows CLAUDE.md: length, then width, never the clip or poster.
"""
import base64, json, pathlib, shutil, subprocess, sys

P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P))
sys.path.insert(0, str(P.parent / "match-trial"))
import build_review as BR
import candidates as C

UI = P / next((a.split("=")[1] for a in sys.argv if a.startswith("--out=")), "ui4-unseen")
SL = P / "shotlist.capacity.json"
PICKS = P.parent / "grammar" / "picks.json"


def unseen_by_beat():
    """(beat -> {quote, job, held, unseen[]}) for every beat with an unseen card.

    `held` is what the user already selected on this beat, so the card they are
    judging against is on screen rather than remembered.
    """
    shots = json.load(open(SL))
    picks = json.load(open(PICKS))["beats"]
    out = {}
    for s in shots:
        k = f"{s['passage']}-{s['beat']}"
        seen = set(picks.get(k, {}).get("shown") or [])
        new = [o for o in s["options"] if o["id"] not in seen]
        if not new:
            continue
        out[k] = {
            "beat": k,
            "job": s.get("job"),
            "quote": s.get("quote"),
            "note": (picks.get(k) or {}).get("note"),
            "held": list((picks.get(k) or {}).get("selected") or []),
            "requiredEncoding": s.get("requiredEncoding") or [],
            "unseen": [{"id": o["id"], "name": o.get("name"),
                        "verdict": o.get("verdict"), "mechanism": o.get("mechanism"),
                        "condition": o.get("condition")} for o in new],
        }
    return out


def main():
    beats = unseen_by_beat()
    need = sorted({o["id"] for b in beats.values() for o in b["unseen"]}
                  | {i for b in beats.values() for i in b["held"]})
    pool = {r["id"]: r for r in C.load(content_class="*")}

    (UI / "media").mkdir(parents=True, exist_ok=True)
    for f in (UI / "media").iterdir():
        f.unlink()

    thumbs, hasclip, missing = {}, {}, []
    for rid in need:
        src = BR.clip_path(rid, pool.get(rid, {}))
        hasclip[rid] = bool(src)
        if not src:
            still = BR.still_path(rid)
            if still:
                jpg = UI / f".{rid}.jpg"
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(still),
                                "-vf", "scale=356:-2", str(jpg)], check=False)
                if jpg.exists():
                    thumbs[rid] = ("data:image/jpeg;base64,"
                                   + base64.b64encode(jpg.read_bytes()).decode())
                    jpg.unlink()
                    continue
            missing.append(rid)
            continue
        dst = UI / "media" / f"{rid}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-t", "8",
                        "-vf", "scale=640:-2", "-c:v", "libx264", "-crf", "30",
                        "-preset", "veryfast", "-movflags", "+faststart", "-an", str(dst)],
                       check=False)
        if not dst.exists():
            shutil.copy(src, dst)
        jpg = UI / f".{rid}.jpg"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.5", "-i", str(src),
                        "-frames:v", "1", "-vf", "scale=356:-2", str(jpg)], check=False)
        if jpg.exists():
            thumbs[rid] = ("data:image/jpeg;base64,"
                           + base64.b64encode(jpg.read_bytes()).decode())
            jpg.unlink()

    json.dump({"beats": [beats[k] for k in sorted(beats)],
               "thumbs": thumbs, "hasClip": hasclip},
              open(UI / "data.json", "w"))
    mb = (UI / "data.json").stat().st_size / 1e6
    vid = sum(f.stat().st_size for f in (UI / "media").iterdir()) / 1e6
    ncards = sum(len(b["unseen"]) for b in beats.values())
    print(f"beats with unseen cards {len(beats)} | unseen cards {ncards} | "
          f"held picks shown alongside {len({i for b in beats.values() for i in b['held']})}")
    print(f"distinct media {len(need)} | clips {sum(hasclip.values())} | "
          f"thumbs {len(thumbs)} | data.json {mb:.1f} MB | media {vid:.1f} MB | "
          f"total {mb + vid:.1f} MB of 64")
    if mb + vid > 60:
        print("OVER THE PUBLISH CEILING — lower the clip length or width")
    if missing:
        print(f"no clip and no still for {len(missing)}: {missing[:6]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
