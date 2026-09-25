#!/usr/bin/env python3
"""Cut the user's chosen holds out of a vendor demo reel as named library scenes.

`segment_reel.py` proposes candidates; this cuts the ones the user picked, at full
source quality, named `<pack>--scene-NNN` to match every other pack in the library.

The picks live in grammar/local-templates.json, which is also the pool sidecar — one
file, so a scene cannot exist as media without existing as a record.

    python3 pipeline/cut_scenes.py            report what would be cut
    python3 pipeline/cut_scenes.py --write    cut the media
"""
import json, pathlib, subprocess, sys

P = pathlib.Path(__file__).resolve().parent
SIDECAR = P.parent / "grammar" / "local-templates.json"
MEDIA = P.parent / "grammar" / "local-clips"
WRITE = "--write" in sys.argv


def cut(src, start, end, out):
    """Re-encode rather than stream-copy: -ss on a copy snaps to the nearest keyframe
    and these holds are 3-5s, so a 2s keyframe drift would take half the clip."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.2f}",
                    "-i", str(src), "-t", f"{end-start:.2f}", "-an",
                    "-c:v", "libx264", "-crf", "18", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)],
                   check=True)


def poster(src, at, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.2f}", "-i", str(src),
                    "-frames:v", "1", "-q:v", "3", str(out)], check=True)


def main():
    if not SIDECAR.exists():
        print(f"no {SIDECAR} — nothing to cut"); return 1
    doc = json.load(open(SIDECAR))
    recs = doc["records"]
    print(f"{len(recs)} scene(s) in the sidecar")
    if WRITE: MEDIA.mkdir(parents=True, exist_ok=True)
    for r in recs:
        src = pathlib.Path(r["sourceReel"])
        a, b = r["sourceSpan"]
        mp4 = MEDIA / f"{r['id']}.mp4"
        jpg = MEDIA / f"{r['id']}.jpg"
        print(f"  {r['id']:34} {a:6.2f}-{b:6.2f}s  ({b-a:.1f}s)  {src.parent.name[:28]}")
        if not WRITE: continue
        if not src.exists():
            print(f"      MISSING SOURCE {src}"); return 1
        cut(src, a, b, mp4); poster(src, (a + b) / 2, jpg)
    if not WRITE:
        print("\nreport only — re-run with --write to cut")
        return 0
    tot = sum(f.stat().st_size for f in MEDIA.iterdir())
    print(f"\nwrote {MEDIA}  {tot/1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
