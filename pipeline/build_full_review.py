#!/usr/bin/env python3
"""All 40 beats -> pipeline/ui13-review/. One beat a page, for a full re-review.

Script context, what is paired now, a 1-5 rating, every note the user has written
about the beat, and candidates to pair again.

THE BUG THIS SCRIPT EXISTS TO NOT REPEAT. The first build of this page was a
throwaway inline script, and it called resolve() WITHOUT the beat's `wants` and
`kinds`. It computed `wants` — and used it to badge each card as fitting or not —
then never passed it to the ranking. So beat 01-01 offered nine articles about
Drake and no photograph of him, while every card carried a fit badge measured
against a constraint the ordering had ignored. The user: "why are those the
canidates and not a image of drake?"
Measured across all 40 beats: person 416 -> 497, document 107 -> 59, artwork
50 -> 21. A throwaway script is how a defect gets no test and no second look.

    python3 pipeline/build_full_review.py
"""
import base64, glob, json, os, pathlib, re, shutil, subprocess, sys

P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P)); sys.path.insert(0, str(P.parent / "match-trial"))
import candidates as C, media_candidates as M, paths as PP

UI = P / "ui13-review"
CACHE = P / ".thumbcache"
PDB = next(iter(glob.glob(os.path.expanduser(
    "/private/tmp/claude-502/*/*/scratchpad/pdb/pairs")) or [""]), "")
WIDE, SECS, PER = 420, 5, 10


# The script and every beat's place in it now live in script_map, built against
# year-seventeen-script-v2.1.md. The user, 2026-09-26: "this is the script that
# should be used ... we can keep the beats the same but this scripts wordings
# helps me understand context. the other one was too choppy." v2.1 is the
# six-cycle version and carries a TEST QUESTION per cycle — what the cycle is
# trying to establish — which is the context a reviewer actually needs.
# Only 17 of 40 beats appear in it verbatim, so placement is a reviewable map
# (grammar/beat-script-map.json) with a user override file, not a live search.
import script_map as SM


def main():
    (UI / "t").mkdir(parents=True, exist_ok=True)
    for f in (UI / "t").iterdir(): f.unlink()
    CACHE.mkdir(exist_ok=True)
    pool, wrong = M.load(), M.corrections()
    tpool = {r["id"]: r for r in C.load(content_class="*")}
    cap = C._capability()
    g = json.load(open(P.parent / "grammar" / "bindings.json"))
    names = {}
    for job, lst in g.items():
        for t in lst: names.setdefault(t["id"], t.get("name") or t["id"])
    shots = {f"{x['passage']}-{x['beat']}": x
             for x in json.load(open(P / "shotlist.capacity.json"))}
    SC, _maprows = SM.load()
    briefs = {b["brief"]: b for b in json.load(open(P.parent / "grammar" / "media-briefs.json"))["briefs"]}
    be = json.load(open(P.parent / "grammar" / "beat-entities.json"))
    subj = (be.get("_subject") or {}).get("entity")
    tpicks = json.load(open(P.parent / "grammar" / "picks.json")).get("beats") or {}
    mpicks = M.picked()
    pairings = json.load(open(P.parent / "grammar" / "pairings.json"))
    mp = json.load(open(P.parent / "grammar" / "media-picks.json"))["briefs"]

    hist = {}
    for f in sorted(glob.glob(f"{PDB}/*.json")) if PDB else []:
        d = json.load(open(f))
        if (d.get("note") or "").strip():
            hist.setdefault(d["beat"], []).append(
                {"where": "pairing page", "when": (d.get("updatedAt") or "")[:10],
                 "text": d["note"].strip()})
    pn = P.parent / "grammar" / "pairing-notes.json"
    if pn.exists() and not PDB:
        for r in json.load(open(pn))["beats"]:
            if r.get("note"):
                hist.setdefault(r["beat"], []).append(
                    {"where": "pairing page", "when": (r.get("updatedAt") or "")[:10],
                     "text": r["note"]})
    for name, rec in mp.items():
        if (rec.get("note") or "").strip():
            hist.setdefault(name, []).append({"where": "media review",
                                              "when": "2026-09-25", "text": rec["note"].strip()})
        for k2, v in (rec.get("entityNotes") or {}).items():
            if v.strip():
                hist.setdefault(name, []).append({"where": f"media review · {k2}",
                                                  "when": "2026-09-25", "text": v.strip()})

    posters, clips, thumbs, bclips = {}, {}, {}, {}

    def prep_broll_clip(aid):
        """B-ROLL IS MOTION. A still of a clip says almost nothing about whether the
        footage serves a beat, and this whole section exists to judge footage. Only
        31 distinct videos across all 40 beats, so they all fit."""
        if aid in bclips: return
        r = pool[aid]; src = r.get("display") or r["path"]
        dst = UI / "t" / f"b_{aid[:16]}.mp4"
        if os.path.exists(src) and not dst.exists():
            subprocess.run(["ffmpeg","-y","-loglevel","error","-i",src,"-t","6",
                            "-vf","scale=360:-2","-c:v","libx264","-crf","34","-preset",
                            "veryfast","-movflags","+faststart","-an",str(dst)], check=False)
        bclips[aid] = f"t/b_{aid[:16]}.mp4" if dst.exists() else None

    def prep_t(tid):
        if tid in posters: return
        mp4, jpg = CACHE / f"{tid}.mp4", CACHE / f"{tid}.jpg"
        src = (tpool.get(tid) or {}).get("clip")
        if not mp4.exists() and src and os.path.exists(src):
            subprocess.run(["ffmpeg","-y","-loglevel","error","-i",src,"-t",str(SECS),
                            "-vf",f"scale={WIDE}:-2","-c:v","libx264","-crf","33","-preset",
                            "veryfast","-movflags","+faststart","-an",str(mp4)], check=False)
        if not jpg.exists():
            for c2 in (mp4 if mp4.exists() else None, src, (cap.get(tid) or {}).get("still_path")):
                if c2 and os.path.exists(c2):
                    isv = str(c2).lower().endswith((".mp4",".mov",".m4v",".webm"))
                    subprocess.run(["ffmpeg","-y","-loglevel","error"]
                                   + (["-ss","0.5"] if isv else []) + ["-i",str(c2)]
                                   + (["-frames:v","1"] if isv else [])
                                   + ["-vf",f"scale={WIDE}:-2",str(jpg)], check=False)
                    if jpg.exists(): break
        if mp4.exists():
            shutil.copy2(mp4, UI / "t" / f"{tid}.mp4"); clips[tid] = f"t/{tid}.mp4"
        posters[tid] = ("data:image/jpeg;base64," + base64.b64encode(jpg.read_bytes()).decode()
                        if jpg.exists() else None)

    def prep_m(aid):
        if aid in thumbs: return
        r = pool[aid]; src = r.get("display") or r["path"]
        if not os.path.exists(src): thumbs[aid] = None; return
        isv = r["media_type"] == "video"
        out = UI / f".{aid[:12]}.jpg"
        subprocess.run(["ffmpeg","-y","-loglevel","error"] + (["-ss","0.5"] if isv else [])
                       + ["-i",src] + (["-frames:v","1"] if isv else [])
                       + ["-vf","scale=200:-2","-q:v","7",str(out)], check=False)
        thumbs[aid] = ("data:image/jpeg;base64," + base64.b64encode(out.read_bytes()).decode()
                       if out.exists() else None)
        if out.exists(): out.unlink()

    def tsel(k):
        x = tpicks.get(k) or {}
        o = []
        for key in ("selected","picks","selections","chosen"):
            v = x.get(key)
            if isinstance(v, list): o += [y.get("id") if isinstance(y, dict) else y for y in v]
        return [t for t in o if t]

    beats = []
    for k in sorted(shots):
        s = shots[k]; b = briefs.get(k) or {}
        win = SC.window(k)
        ents = sorted(set(b.get("entities") or [])
                      | set((be.get("beats", {}).get(k) or {}).get("entities") or [])
                      | ({subj} if subj else set()))
        # THE FIX: the beat's own framing and kind wants reach the ranking, not
        # only the badge on the card.
        wants = tuple(sorted({f for t in (b.get("selectedTemplates") or [])
                              for f in M.framing_wanted(t["id"], t.get("kind"))}))
        kinds = tuple(sorted({kk for t in (b.get("selectedTemplates") or [])
                              for kk in M.kind_wanted(t["id"], t.get("kind"))}))
        tops = [o["id"] for o in s["options"][:PER]]
        picked_t = set(tsel(k))
        for t in list(picked_t) + tops: prep_t(t)
        media = []
        for e in ents:
            got = M.resolve([e], pool=pool, wrong=wrong, wants=wants, kinds=kinds,
                            quote=b.get("quote", ""))["individual"].get(e, [])
            keep = set(mpicks.get(f"{k}::e:{e}") or [])
            ids = [c2["id"] for c2 in got if c2["id"] in keep] + \
                  [c2["id"] for c2 in got if c2["id"] not in keep][:PER]
            for aid in ids:
                prep_m(aid); r = pool[aid]
                fm = M.framing_matches(r.get("framing"), wants) if wants else True
                media.append({"id": aid, "entity": e, "video": r["media_type"] == "video",
                              "framing": r.get("framing"), "kind": r.get("kind"),
                              "picked": aid in keep,
                              "fits": None if fm is None else bool(fm)})
        # B-ROLL, fetched separately and video-only. User 2026-09-26: "allow b-roll
        # to be used as addition to template/media or in place of media... fetch
        # videos that can match the beat... it'll be sparse starting off but it'll
        # inform media gaps and what / how to source."
        # Framing is NOT applied here: a framing tag describes a still crop, and
        # asking a clip to be a headshot would empty an already thin set. Measured:
        # every beat has at least 5, the median is 5, the most is 37.
        broll = []
        seen_b = set()
        for e in ents:
            for c2 in M.resolve([e], pool=pool, wrong=wrong, media_type="video",
                                kinds=kinds, quote=b.get("quote", ""))["individual"].get(e, [])[:PER]:
                if c2["id"] in seen_b: continue
                seen_b.add(c2["id"]); prep_m(c2["id"]); prep_broll_clip(c2["id"])
                r = pool[c2["id"]]
                broll.append({"id": c2["id"], "entity": e, "video": True,
                              "clip": bclips.get(c2["id"]),
                              "framing": r.get("framing"), "kind": r.get("kind"),
                              "picked": c2["id"] in set(mpicks.get(f"{k}::e:{e}") or []),
                              "fits": None})
        pb = pairings["beats"].get(k) or {}
        beats.append({
            "beat": k, "job": s["job"], "quote": s["quote"],
            # THE PAGE RENDERS CONTIGUOUS SCRIPT. before + mid + after is a real
            # substring of the narration; hlStart/hlLen say where this beat's own
            # words sit inside mid. The previous shape emitted before/after around
            # the beat and let the page splice `quote` between them, which dropped
            # text whenever the quote was not exactly the script's words — on
            # 02-02a it dropped the second half of a shared sentence and the page
            # jumped from the Freshman cover to the ninety-three rappers.
            "script": win, "entities": ents,
            "place": dict(SC.where(k), n=sorted(shots).index(k) + 1,
                          of=len(shots),
                          overlap=SC.rows[k]["overlap"],
                          scriptSays=(None if SC.rows[k]["exact"] else SC.says(k))),
            "wants": list(wants), "kinds": list(kinds),
            "templates": [{"id": t, "name": names.get(t, t), "clip": clips.get(t),
                           "poster": posters.get(t), "picked": t in picked_t,
                           "slots": (cap.get(t) or {}).get("media_slots"),
                           "structure": (cap.get(t) or {}).get("structure"),
                           "mechanism": next((o.get("mechanism") for o in s["options"]
                                              if o["id"] == t), None)}
                          for t in dict.fromkeys(list(picked_t) + tops)],
            "media": media, "broll": broll,
            "paired": [{"templateId": p["templateId"],
                        "slots": [x["asset"] for x in p.get("slots", []) if x["asset"]]}
                       for p in pb.get("proposed", []) if any(x["asset"] for x in p.get("slots", []))],
            "history": hist.get(k, []),
            "counts": {"bound": len(g.get(s["job"]) or []), "shown": len(s["options"])},
        })
    json.dump({"beats": beats, "thumbs": thumbs}, open(UI / "data.json", "w"))
    import collections
    kinds_shown = collections.Counter(m["kind"] for b in beats for m in b["media"])
    bn = [len(b["broll"]) for b in beats]
    print(f"   b-roll per beat: min {min(bn)} median {sorted(bn)[len(bn)//2]} max {max(bn)}"
          f" | beats with none: {sum(1 for x in bn if not x)}")
    mb = (UI / "data.json").stat().st_size / 1e6
    vid = sum(f.stat().st_size for f in (UI / "t").iterdir()) / 1e6
    print(f"   beats {len(beats)} | templates {len(posters)} ({len(clips)} clips) | "
          f"media {len(thumbs)}")
    print(f"   kinds on offer: {dict(kinds_shown)}")
    print(f"   b-roll clips {sum(1 for v in bclips.values() if v)} of {len(bclips)}")
    print(f"   data.json {mb:.1f} MB | clips {vid:.1f} MB | "
          f"files {2+len(list((UI/'t').iterdir()))} of 255")
    return 0


if __name__ == "__main__":
    sys.exit(main())
