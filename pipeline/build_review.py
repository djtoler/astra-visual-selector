#!/usr/bin/env python3
"""shotlist.json -> pipeline/ui2/{data.json,media/}. Deterministic, no model calls.

Thumbnails are inlined as base64 so the published artifact carries one file entry per
clip instead of two. Clips are copied only for ids that actually appear in a slate.
"""
import base64, json, pathlib, shutil, subprocess, sys
P    = pathlib.Path(__file__).resolve().parent
# ui3-capacity is FROZEN — it is the slate of record for review pass 1 and
# ingest_picks.py reads it to know what the human was shown. Never rebuild it.
# ui2 is the live review UI and is built from the capacity-RANKED slate, which leads
# with the best-fitting templates. Pass --plain for the unranked one.
CAP  = "--plain" not in sys.argv
# --slate and --out let an A/B arm be built without touching the live UI.
UI   = P / next((a.split("=")[1] for a in sys.argv if a.startswith("--out=")), "ui2")
SL   = P / next((a.split("=")[1] for a in sys.argv if a.startswith("--slate=")),
                "shotlist.capacity.json" if CAP else "shotlist.json")
sys.path.insert(0, str(P.parent / "match-trial"))
import candidates as C

# Infographics and 3D layouts render to their own output dir rather than carrying a
# `clip` field, so fall back to it by id before giving up on a preview.
IG = pathlib.Path("/Users/dwaynetoler/Documents/ChatGPT/Polish/infographic-template-system")
C3D = pathlib.Path("/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation"
                   "/scene-library/approved/previews/cinematic-3d")

def clip_path(rid, rec):
    c = rec.get("clip")
    if c and pathlib.Path(c).exists(): return pathlib.Path(c)
    for cand in (IG / "output" / f"{rid}.mp4", IG / "output" / f"{rid}-v2.mp4",
                 C3D / f"{rid}.mp4"):
        if cand.exists(): return cand
    return None

def still_path(rid):
    for cand in (IG / "profiles" / "previews" / f"{rid}.jpg",
                 IG / "output" / f"{rid}.png", IG / "output" / f"{rid}-v2.png",
                 C3D / f"{rid}.jpg"):
        if cand.exists(): return cand
    return None

def main():
    shots = json.load(open(SL))
    pool  = {r["id"]: r for r in C.load()}
    shown = {o["id"] for s in shots for o in s["options"]}
    # Siblings ride behind an expander on the chosen scene, so they cost no slate
    # slot — but they do cost media. 138 distinct, all with clips. Budgeted the way
    # CLAUDE.md orders it: clip LENGTH first, then width. Never the clip, never the
    # poster. A sibling is a second look at a family already on screen, so 5s at
    # 480 is enough to tell two scenes from one pack apart.
    sibs  = {i["id"] for s in shots for o in s["options"] for i in (o.get("siblings") or [])}
    sibs -= shown
    need  = sorted(shown | sibs)

    (UI / "media").mkdir(parents=True, exist_ok=True)
    for f in (UI / "media").iterdir(): f.unlink()

    thumbs, hasclip, missing = {}, {}, []
    for rid in need:
        src = clip_path(rid, pool.get(rid, {}))
        hasclip[rid] = bool(src)
        if not src:
            still = still_path(rid)
            if still:
                jpg = UI / f".{rid}.jpg"
                subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(still),
                                "-vf","scale=356:-2",str(jpg)], check=False)
                if jpg.exists():
                    thumbs[rid] = "data:image/jpeg;base64," + base64.b64encode(jpg.read_bytes()).decode()
                    jpg.unlink()
                    continue
            missing.append(rid); continue
        # Publish ceiling is 64 MB a version, so previews are transcoded, not copied:
        # 640 wide, no audio, first 8 seconds — enough to judge a treatment.
        dst = UI / "media" / f"{rid}.mp4"
        secs, wide = ("5", "480") if rid in sibs else ("8", "640")
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(src),"-t",secs,
                        "-vf",f"scale={wide}:-2","-c:v","libx264","-crf","30",
                        "-preset","veryfast","-movflags","+faststart","-an",str(dst)],
                       check=False)
        if not dst.exists():
            shutil.copy(src, dst)
        jpg = UI / f".{rid}.jpg"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.5", "-i", str(src),
                        "-frames:v", "1", "-vf", "scale=356:-2", str(jpg)], check=False)
        if jpg.exists():
            thumbs[rid] = "data:image/jpeg;base64," + base64.b64encode(jpg.read_bytes()).decode()
            jpg.unlink()

    json.dump({"shots": shots, "thumbs": thumbs, "hasClip": hasclip},
              open(UI / "data.json", "w"))
    mb  = (UI / "data.json").stat().st_size / 1e6
    vid = sum(f.stat().st_size for f in (UI / "media").iterdir()) / 1e6
    print(f"beats {len(shots)} | distinct options {len(need)} | clips {sum(hasclip.values())} "
          f"| thumbs {len(thumbs)} | data.json {mb:.1f} MB | media {vid:.1f} MB "
          f"| total {mb+vid:.1f} MB of 64")
    if mb + vid > 60: print("OVER THE PUBLISH CEILING — lower the clip length or width")
    if missing: print(f"no clip on disk for {len(missing)}: {missing[:6]}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
