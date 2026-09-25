#!/usr/bin/env python3
"""bindings.json -> pipeline/clusters-ui/data.json. Deterministic, no model calls.

One entry per job: the derived mechanism clusters, their members, and the clip for each
record. Clips are inlined as base64 because 420 of them would blow the artifact's 255-file
limit; they are small (320px, 4s, silent) so the page stays light. Every clip also carries a real
frame from itself as a poster — a video with no poster is a black rectangle until played,
which makes a grid of them unskimmable. A record with no render
on disk falls back to a still and is marked `stillOnly`, never passed off as a clip.
"""
import base64, json, pathlib, subprocess, sys
P  = pathlib.Path(__file__).resolve().parent
UI = P / "clusters-ui"
sys.path.insert(0, str(P.parent / "match-trial"))
import candidates as C
from build_review import clip_path, still_path

def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()

def media(rid, rec, cache):
    """(clipDataUri, posterDataUri). A clip always gets a poster. Where no render exists,
    the poster is the only thing there is and the record is marked stillOnly."""
    mp4 = clip_path(rid, rec)
    if mp4:
        out = cache / f"{rid}.mp4"
        if not out.exists():
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-t", "4",
                            "-vf", "scale=320:-2", "-c:v", "libx264", "-crf", "34",
                            "-preset", "veryfast", "-an", "-movflags", "+faststart",
                            str(out)], check=False)
        jpg = cache / f"{rid}.jpg"
        if not jpg.exists():
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.5", "-i", str(mp4),
                            "-frames:v", "1", "-vf", "scale=320:-2", "-q:v", "6",
                            str(jpg)], check=False)
        if out.exists():
            return b64(out, "video/mp4"), (b64(jpg, "image/jpeg") if jpg.exists() else None)
    still = still_path(rid)
    if not still: return None, None
    jpg = cache / f"{rid}.jpg"
    if not jpg.exists():
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(still),
                        "-vf", "scale=400:-2", str(jpg)], check=False)
    return None, (b64(jpg, "image/jpeg") if jpg.exists() else None)

def main():
    bindings = json.load(open(P.parent / "grammar" / "bindings.json"))
    pool  = {r["id"]: r for r in C.load()}
    UI.mkdir(exist_ok=True)
    cache = P / ".thumbcache"; cache.mkdir(exist_ok=True)

    clips, posters, jobs = {}, {}, {}
    for job, rows in sorted(bindings.items()):
        idx = C.cluster_index(rows, job=job)
        clusters = {}
        for r in rows: clusters.setdefault(idx[r["id"]], []).append(r["id"])
        recs = {}
        for r in rows:
            rid = r["id"]
            p = r.get("provenance") or {}
            recs[rid] = {"family": C._family(rid), "name": r.get("name"),
                         "mech": p.get("mechanism"), "verdict": p.get("verdict"),
                         "evidence": p.get("evidence"), "condition": r.get("condition"),
                         "band": C.capacity_band(r, pool)}
            if rid not in posters and rid not in clips:
                clip, poster = media(rid, pool.get(rid, {}), cache)
                if clip:   clips[rid] = clip
                if poster: posters[rid] = poster
            recs[rid]["stillOnly"] = rid not in clips
        jobs[job] = {"clusters": {k: sorted(v) for k, v in sorted(clusters.items())},
                     "records": recs}

    json.dump({"jobs": jobs, "clips": clips, "posters": posters}, open(UI / "data.json", "w"))
    n = sum(len(j["records"]) for j in jobs.values())
    mb = (UI / "data.json").stat().st_size / 1e6
    print(f"jobs {len(jobs)} | bindings {n} | distinct records {len(set().union(*[set(j['records']) for j in jobs.values()]))} "
          f"| clusters {sum(len(j['clusters']) for j in jobs.values())} "
          f"| clips {len(clips)} | still-only {len(posters)-len([k for k in posters if k in clips])} "
          f"| data.json {mb:.1f} MB of 16")
    if mb > 15: print("OVER THE data.json CEILING — lower the clip width or length")
    return 0

if __name__ == "__main__":
    sys.exit(main())
