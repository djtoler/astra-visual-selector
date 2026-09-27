#!/usr/bin/env python3
"""One file holding everything the 2026-09-26/27 beat review produced and stood on.

WHY. The review's own output lived in the artifact database — 31 records the user
typed into a published page — and nothing in the repo held it. Everything else it
depended on was spread across eighteen grammar sidecars, the shotlist, and the
built page data. A review nobody can reconstruct is a review that has to be redone.

    python3 pipeline/export_review.py [--review-dir DIR] [-o OUT]

--review-dir holds the artifact-db records, one JSON per beat, as written by
Artifact read_db. They are USER DATA: copied through verbatim, never rewritten.

The export also carries `issues_media_layer`, read from
grammar/issues_media_layer.json — twelve problems drawn from this review. They are
PLAUSIBLE, NOT VERIFIED: the measurements reproduce and the user's words are
verbatim, but the problem statements and the impact claims are Claude's analysis
and have not been through a versioned prompt.
"""
import argparse, glob, json, os, pathlib, sys

P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P)); sys.path.insert(0, str(P.parent / "match-trial"))
G = P.parent / "grammar"


def jload(p, default=None):
    try:
        with open(p) as fh: return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review-dir", default="")
    ap.add_argument("-o", "--out", default=str(G / "beat-review-export-2026-09-27.json"))
    a = ap.parse_args()

    import candidates as C, media_candidates as M, script_map as SM, paths as PP

    shots = {f"{x['passage']}-{x['beat']}": x
             for x in jload(P / "shotlist.capacity.json", [])}
    built = jload(P / "ui13-review" / "data.json", {"beats": []})
    bdata = {b["beat"]: b for b in built["beats"]}
    rejected = (jload(P / "ui13-review" / "rejected.json", {}) or {}).get("beats", {})
    bindings = jload(G / "bindings.json", {})
    picks = jload(G / "picks.json", {})
    mpicks = jload(G / "media-picks.json", {})
    pairings = jload(G / "pairings.json", {})
    briefs = {b["brief"]: b for b in (jload(G / "media-briefs.json", {}) or {}).get("briefs", [])}
    be = jload(G / "beat-entities.json", {})
    SC, maprows = SM.load()
    maprow = {r["beat"]: r for r in maprows}

    # the user's own review records, verbatim
    review = {}
    if a.review_dir:
        for f in sorted(glob.glob(os.path.join(a.review_dir, "**", "*.json"),
                                  recursive=True)):
            d = jload(f)
            if isinstance(d, dict) and d.get("data", {}).get("beat"):
                review[d["data"]["beat"]] = d["data"]
            elif isinstance(d, dict) and d.get("beat"):
                review[d["beat"]] = d

    pool, wrong = M.load(), M.corrections()
    tpool = {r["id"]: r for r in C.load(content_class="*")}
    cap = C._capability()
    tname = {}
    for job, lst in bindings.items():
        for t in lst: tname.setdefault(t["id"], t.get("name") or t["id"])

    # every asset the export mentions, with its tags — so a reader never has to
    # go back to the library to know what a candidate WAS
    assets = {}
    def note_asset(aid):
        if aid in assets or aid not in pool: return
        r = pool[aid]
        assets[aid] = {k: r.get(k) for k in
                       ("id", "entity", "kind", "framing", "media_type", "tags",
                        "title", "caption", "faces", "canonical_path", "display")
                       if k in r}
        # user_tags() rows are dicts carrying the user's own words; removed_tags()
        # is a set of strings. Sorting either blindly raises, and losing the words
        # would drop the evidence a user-named binding rests on.
        assets[aid]["userTags"] = M.user_tags().get(aid, [])
        assets[aid]["removedTags"] = sorted(M.removed_tags().get(aid, set()))

    beats = []
    for k in sorted(shots):
        s, b, mr = shots[k], bdata.get(k, {}), maprow.get(k, {})
        rv = review.get(k, {})
        brief = briefs.get(k, {})
        job = s["job"]
        bound = [{"id": t["id"], "name": t.get("name") or t["id"],
                  "verdict": (t.get("provenance") or {}).get("verdict"),
                  "mechanism": (t.get("provenance") or {}).get("mechanism"),
                  "condition": t.get("condition")}
                 for t in bindings.get(job, [])]
        offered = [{"id": t["id"], "name": tname.get(t["id"], t["id"]),
                    "slots": (cap.get(t["id"]) or {}).get("media_slots"),
                    "structure": (cap.get(t["id"]) or {}).get("structure"),
                    "mechanism": t.get("mechanism"),
                    "family": C._family(t["id"])}
                   for t in s.get("options", [])]
        sel = [t["id"] for t in (brief.get("selectedTemplates") or [])]
        rej = [{"id": t["id"], "name": t.get("name")} for t in rejected.get(k, [])]

        media_offered = []
        for m in b.get("media", []):
            note_asset(m["id"])
            media_offered.append({k2: m.get(k2) for k2 in
                                  ("id", "entity", "kind", "framing", "video",
                                   "picked", "fits")})
        broll_offered = []
        for m in b.get("broll", []):
            note_asset(m["id"])
            broll_offered.append({k2: m.get(k2) for k2 in
                                  ("id", "entity", "kind", "framing", "picked")})
        mp = {kk: v for kk, v in (mpicks.get("briefs") or {}).items()
              if kk.startswith(k + "::")}
        for v in mp.values():
            for aid in (v if isinstance(v, list) else []): note_asset(aid)
        for pr in (rv.get("pairs") or []):
            for aid in (pr.get("assets") or []): note_asset(aid)

        beats.append({
            "beat": k,
            "quote": s["quote"],
            "job": job,
            "entities": sorted(set((brief.get("entities") or []))
                               | set(((be.get("beats") or {}).get(k) or {}).get("entities") or [])
                               | ({(be.get("_subject") or {}).get("entity")}
                                  if (be.get("_subject") or {}).get("entity") else set())),
            "script": {"cycle": mr.get("cycle"), "section": mr.get("section"),
                       "testQuestion": mr.get("test"),
                       "overlap": mr.get("overlap"), "exact": mr.get("exact"),
                       "scriptSentence": mr.get("scriptSays"),
                       "window": SC.window(k)},
            "requirements": {"wants": b.get("wants") or [], "kinds": b.get("kinds") or []},
            "templates": {"boundToJob": bound, "offeredOnSlate": offered,
                          "selected": sel, "rejected": rej,
                          "counts": {"bound": len(bound), "offered": len(offered),
                                     "selected": len(sel), "rejected": len(rej)}},
            "media": {"offered": media_offered, "brollOffered": broll_offered,
                      "picksByEntity": mp},
            "pairings": {"proposed": (pairings.get("beats", {}).get(k) or {}).get("proposed", []),
                         "fromReview": rv.get("pairs") or []},
            # USER DATA, verbatim. rating, note, the source flags and the
            # no-eligible-b-roll verdict with the count that was on offer.
            "userReview": {kk: rv.get(kk) for kk in
                           ("rating", "note", "media", "broll", "noBroll",
                            "brollOffered", "updatedAt")} if rv else None,
            "priorNotes": b.get("history") or [],
        })

    out = {
        "_what": "Everything the 2026-09-26/27 beat review produced and stood on.",
        "_generatedAt": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ",
                                                   __import__("time").gmtime()),
        "_sources": {
            "script": "script/year-seventeen-script-v2.1.md",
            "beatScriptMap": "grammar/beat-script-map.json",
            "shotlist": "pipeline/shotlist.capacity.json",
            "bindings": "grammar/bindings.json",
            "builtPage": "pipeline/ui13-review/data.json",
            "reviewRecords": ("artifact db collection 'review' on "
                              "https://claude.ai/artifact/8jiDffop63tEGnbtKY1TGf"),
            "mediaSource": PP.source(),
            "polishMirror": str(PP.is_mirrored()),
        },
        "_counts": {
            "beats": len(beats),
            "beatsReviewedByUser": sum(1 for b in beats if b["userReview"]),
            "beatsRated": sum(1 for b in beats
                              if (b["userReview"] or {}).get("rating")),
            "beatsWithNotes": sum(1 for b in beats
                                  if (b["userReview"] or {}).get("note")),
            "beatsNoEligibleBroll": sum(1 for b in beats
                                        if (b["userReview"] or {}).get("noBroll")),
            "pairingsFromReview": sum(len(b["pairings"]["fromReview"]) for b in beats),
            "templatesSelected": sum(b["templates"]["counts"]["selected"] for b in beats),
            "templatesRejected": sum(b["templates"]["counts"]["rejected"] for b in beats),
            "assetsDescribed": len(assets),
            "issuesMediaLayer": len((jload(G / "issues_media_layer.json") or {})
                                    .get("issues") or []),
        },
        "grammar": {
            "jobs": {job: [t["id"] for t in lst] for job, lst in bindings.items()},
            "jobCounts": {job: len(lst) for job, lst in bindings.items()},
            "templatePicks": picks,
            "classTags": jload(G / "class-tags.json", {}),
            "framingRules": jload(G / "framing-rules.json", {}),
            "mediaKindRules": jload(G / "media-kind-rules.json", {}),
            "mediaTags": jload(G / "media-tags.json", {}),
            "mediaCorrections": jload(G / "media-corrections.json", {}),
            "approvedOverrides": jload(G / "approved-overrides.json", {}),
            "xxlCovers": jload(G / "xxl-covers.json", {}),
            "beatFlags": jload(G / "beat-flags.json", {}),
            "eligibilityOverrides": jload(G / "eligibility-overrides.json", {}),
        },
        "assets": assets,
        "beats": beats,
        # PLAUSIBLE, NOT VERIFIED. Read from its own sidecar rather than written
        # here, so the analysis is an editable artifact and this file stays
        # generated. CLAUDE.md: "Claude's own reading is not evidence." The
        # measurements in it are reproducible and the user's words are verbatim;
        # the problem statements, the ranking and the impact claims are analysis.
        "issues_media_layer": jload(G / "issues_media_layer.json"),
    }
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    c = out["_counts"]
    print(f"   {a.out}")
    print(f"   {os.path.getsize(a.out)/1e6:.2f} MB")
    for kk, v in c.items(): print(f"      {kk:24} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
