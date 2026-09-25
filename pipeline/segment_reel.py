#!/usr/bin/env python3
"""Cut each vendor demo reel into candidate designs, for the user to pick from.

The reels have no hard cuts — designs dissolve over a continuous background — so
`select=gt(scene,0.35)` finds nothing. At 0.04 the animate-in and animate-out of each
lower third DO register, in bursts. A design is the QUIET GAP between two bursts:
the hold, where it sits fully on screen.

Nothing here judges a design. It finds where one is stable and cuts a clip. Which of
them are worth keeping is the user's pick.
"""
import subprocess, json, pathlib, sys

T = pathlib.Path("/Users/dwaynetoler/timeline/templates")
OUT = pathlib.Path("/Users/dwaynetoler/timeline/pipeline/lt-pick")
# name=path pairs on the command line override this default set.
REELS = [
 ("grunge-lower-thirds", T/"Lower Thirds/preview_540p_crf22_higher_quality-3.mp4"),
 ("glass-lower-thirds",  T/"glassmorphism-lower-thirds-for-after-effects-12-2026-09-13-10-56-24-utc/preview_540p_crf22_higher_quality-4.mp4"),
 ("paper-lower-thirds",  T/"paper-lower-thirds-ae-2026-09-11-13-29-15-utc/preview_540p_crf22_higher_quality-2.mp4"),
]
_args = [a for a in sys.argv[1:] if "=" in a]
if _args: REELS = [(a.split("=", 1)[0], pathlib.Path(a.split("=", 1)[1])) for a in _args]
# MIN_HOLD is TUNED PER REEL, not fixed. At a fixed 2.0s the grunge reel yielded 4
# candidates — two of them After Effects UI footage — and dropped its body-text block
# entirely, which is the one design most likely to serve a define_terms beat. The reels
# are cut at different tempos by different vendors; one threshold cannot fit all three.
# Target 8-12 candidates and let the threshold fall where it must.
TARGET = (8, 12)
CLIP_LEN = 4.0        # how much of the hold to cut

def transitions(path):
    r = subprocess.run(["ffmpeg","-v","error","-i",str(path),
                        "-vf","select='gt(scene,0.04)',metadata=print:file=-",
                        "-f","null","-"], capture_output=True, text=True)
    ts = [float(l.split("pts_time:")[1].split()[0])
          for l in r.stdout.splitlines() if "pts_time:" in l]
    return sorted(ts)

def duration(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","csv=p=0",str(path)], capture_output=True, text=True)
    return float(r.stdout.strip())

def holds(ts, dur, min_hold):
    """Quiet gaps between bursts of transition activity."""
    # collapse bursts: transitions within 0.75s of each other are one event
    burst, ev = [], []
    for t in ts:
        if burst and t - burst[-1] > 0.75:
            ev.append((burst[0], burst[-1])); burst = []
        burst.append(t)
    if burst: ev.append((burst[0], burst[-1]))
    out, prev_end = [], 0.0
    for a, b in ev:
        if a - prev_end >= min_hold: out.append((prev_end, a))
        prev_end = b
    if dur - prev_end >= min_hold: out.append((prev_end, dur))
    return out

def tune(ts, dur):
    """Lowest threshold in [0.6, 4.0] whose hold count lands in TARGET; else closest."""
    best, bestscore = 2.0, None
    for step in range(1, 35):
        mh = 0.6 + step * 0.1
        n = len(holds(ts, dur, mh))
        if TARGET[0] <= n <= TARGET[1]: return mh, n
        score = min(abs(n - TARGET[0]), abs(n - TARGET[1]))
        if bestscore is None or score < bestscore: best, bestscore = mh, score
    return best, len(holds(ts, dur, best))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"media").mkdir(exist_ok=True)
    cands = []
    for pack, path in REELS:
        dur = duration(path)
        ts = transitions(path)
        mh, _ = tune(ts, dur)
        hs = holds(ts, dur, mh)
        print(f"{pack:22} {dur:5.1f}s  min_hold {mh:.1f}s  {len(hs)} holds")
        for i, (a, b) in enumerate(hs, 1):
            mid = (a + b) / 2
            start = max(0.0, min(mid - CLIP_LEN/2, dur - CLIP_LEN))
            cid = f"{pack}--cand-{i:03d}"
            mp4 = OUT/"media"/f"{cid}.mp4"
            jpg = OUT/"media"/f"{cid}.jpg"
            subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{start:.2f}","-i",str(path),
                            "-t",f"{min(CLIP_LEN, b-a+1.0):.2f}","-an",
                            "-vf","scale=640:-2","-c:v","libx264","-crf","30",
                            "-preset","veryfast","-movflags","+faststart",str(mp4)],check=True)
            subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{mid:.2f}","-i",str(path),
                            "-frames:v","1","-vf","scale=640:-2","-q:v","6",str(jpg)],check=True)
            cands.append({"id": cid, "pack": pack, "n": i,
                          "hold": [round(a,2), round(b,2)], "at": round(mid,2),
                          "len": round(b-a,2),
                          "clip": f"media/{cid}.mp4", "poster": f"media/{cid}.jpg"})
    json.dump({"candidates": cands}, open(OUT/"data.json","w"), indent=1)
    mb = sum(f.stat().st_size for f in (OUT/"media").iterdir())/1e6
    print(f"\n{len(cands)} candidates, {mb:.1f} MB -> {OUT}")


if __name__ == "__main__":
    main()
