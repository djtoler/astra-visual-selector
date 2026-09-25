#!/usr/bin/env python3
"""Beats + grammar + word timing -> a shot list."""
import json, re, sys, pathlib, difflib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "match-trial"))
import candidates as C
P=pathlib.Path(__file__).resolve().parent
N="/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/narration-visual-annotations"
G="/Users/dwaynetoler/timeline/grammar/bindings.json"
PRIM="/Users/dwaynetoler/timeline/grammar/primaries.json"
CAPACITY = "--capacity" in sys.argv     # apply the beat's entity_count as a hard filter
# Slate size. Was 12. Dropped to 10 on 2026-09-21 once prior rejections stopped being
# re-shown: at 10 every one of the user's 61 selections is still reachable and the
# reviewer reads 29 fewer cards. 6 is more uniform still — 23 of 40 beats land exactly
# there, which is the shape the RAG review had — but it loses 4 picks.
SLATE_LIMIT = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--limit=")), 10))
RELEVANCE = "--relevance" in sys.argv   # load embedding scores from pgvector
ONLY_BEATS = next((a.split("=")[1].split(",") for a in sys.argv if a.startswith("--beats=")), None)

def _relevance_scores():
    """Cosine of each template against each beat, from the local pgvector store.
    Text never leaves the machine at query time; the vectors are already there."""
    import subprocess, math
    DB = ["docker","exec","-i","contradiction-pgvector","psql","-U","contradiction",
          "-d","beat_template_retrieval","-tA","-F","\t"]
    def grab(t,k):
        o=subprocess.run(DB+["-c",f"select {k}, embedding from {t};"],
                         capture_output=True,text=True).stdout.strip().split("\n")
        return {l.split("\t",1)[0]:[float(x) for x in l.split("\t",1)[1].strip("[]").split(",")]
                for l in o if l.strip()}
    tv,bv = grab("template_vectors_openai","template_id"), grab("beat_vectors_openai","beat_id")
    def cos(a,b):
        n=math.sqrt(sum(x*x for x in a))*math.sqrt(sum(y*y for y in b))
        return sum(x*y for x,y in zip(a,b))/n if n else 0.0
    return {bid: {tid: cos(q, v) for tid, v in tv.items()} for bid, q in bv.items()}
OUT = next((a.split("=")[1] for a in sys.argv if a.startswith("--out=")),
           "shotlist.capacity.json" if CAPACITY else "shotlist.json")

NUM={"one":"1","two":"2","three":"3","four":"4","five":"5","six":"6","seven":"7","eight":"8",
     "nine":"9","ten":"10","eleven":"11","twelve":"12","thirteen":"13","seventeen":"17",
     "eighteen":"18","twenty":"20","thirty":"30","forty":"40","fifty":"50","sixty":"60",
     "seventy":"70","eighty":"80","ninety":"90","hundred":"100","thousand":"1000",
     "million":"m","billion":"b","percent":"%"}
def norm(t):
    t=re.sub(r"[^\w\s%]"," ",t.lower())
    return [NUM.get(w,w) for w in t.split()]

def words():
    d=narration("year-seventeen-narration-whisper.json")
    return [w for s in d["segments"] for w in (s.get("words") or [])]

def place(beat_quote, win):
    """Best contiguous span of `win` matching the beat's quote."""
    q=norm(beat_quote)
    if not q or not win: return None
    wn=[norm(w["word"])[0] if norm(w["word"]) else "" for w in win]
    sm=difflib.SequenceMatcher(None, wn, q)
    blocks=[b for b in sm.get_matching_blocks() if b.size>0]
    if not blocks: return None
    lo=min(b.a for b in blocks); hi=max(b.a+b.size for b in blocks)
    return win[lo]["start"], win[min(hi,len(win))-1]["end"]

def drop_prior_rejections(beat, rows, picks, keep=frozenset()):
    """Never show a human an option they have already rejected FOR THIS BEAT.

    Measured 2026-09-21: 77 of 328 options in the live slate — 23% — were things the
    user rejected in review pass 1. Codex's RAG pilot excluded them by design, and
    that is the largest single reason its review felt better; the retrieval was not
    the difference.

    PER BEAT, not globally. A rejection means "not for this beat", not "never" — the
    same template is often right somewhere else. `picks.json` derives rejections only
    on beats the user actually judged, so an unjudged beat drops nothing.
    """
    key = f"{beat.get('_passage','')}-{beat['id']}"
    rejected = set((picks or {}).get(key, {}).get("rejected") or [])
    if not rejected: return rows, None
    kept = [r for r in rows if r["id"] not in rejected or r["id"] in keep]
    n = len(rows) - len(kept)
    if not n: return rows, None
    if not kept:
        return rows, (f"Every candidate here was rejected in an earlier pass. Showing "
                      f"them again rather than an empty slate.")
    note = f"{n} option(s) you rejected earlier are not shown again."
    back = [r["id"] for r in kept if r["id"] in rejected]
    if back:
        note += (f" {len(back)} you rejected IS shown, because you named it for this "
                 f"beat directly — a current instruction outranks a past verdict.")
    return kept, note

def admit_match_cuts(beat, rows, pool_index, picks):
    """A beat the user flagged as raw b-roll admits match-cut vessels regardless of
    what job they were bound to. ADMITS, never excludes, and only on a user-flagged
    beat — a user-named binding under the HARD RULE, not a hand-pick. See LOG 0030."""
    key = f"{beat.get('_passage','')}-{beat['id']}"
    rec = (picks or {}).get(key) or {}
    if not rec.get("rawBroll"): return rows, None
    have = {r["id"] for r in rows}
    extra = [{"id": r["id"], "name": r.get("description"),
              "provenance": {"source": "user", "verdict": "match-cut",
                             "reason": "beat flagged raw b-roll by the user; "
                                       "match-cut vessels admitted across jobs"}}
             for r in C.match_cut_pool(pool_index) if r["id"] not in have]
    if not extra: return rows, None
    return rows + extra, (f"Flagged raw b-roll, so {len(extra)} match-cut vessel(s) "
                          f"are admitted here regardless of job binding.")

def admit_user_named(beat, rows, pool_index):
    """A binding the user named directly — the standing exception to "the pipeline
    decides, not Claude".

    two-floors was BUILT for beat 28 and could never reach it: bindings.json was
    produced by a run that predates the record, so it is bound to no job at all. The
    handshake correctly reported "NEEDS AN ENCODING NOTHING HERE HAS: overlap" while
    the only record in the corpus carrying overlap sat unbound in the pool.

    ADMITS ONLY. It never removes, never reorders, and never writes into
    bindings.json, which belongs to the judgment prompt. An admitted record still
    has to survive capacity, encoding and diversity ranking like anything else.
    """
    import os
    f = "/Users/dwaynetoler/timeline/grammar/local-templates.json"
    if not os.path.exists(f): return rows, None
    spec = (json.load(open(f)).get("userBindings") or {}).get(
        f"{beat.get('_passage','')}-{beat['id']}")
    if not spec: return rows, None
    have = {r["id"] for r in rows}
    extra = [{"id": i, "name": (pool_index.get(i) or {}).get("description"),
              "provenance": {"source": "user", "verdict": "user-named",
                             "reason": spec["why"]}}
             for i in spec.get("admit") or []
             if i not in have and i in pool_index]
    if not extra: return rows, None
    return rows + extra, (f"{len(extra)} template(s) the user named for this beat "
                          f"directly, admitted regardless of job binding.")

def admit_scoped(beat, rows, scoped_index, picks):
    """A beat that DECLARES a content class admits the templates scoped to it.

    SCOPE.md restricts three templates by content class — two to lyrics, one to
    timelines — on the user's instruction. `load()` admits a scoped template only when
    content_class matches, and nothing in the pipeline ever passed one, so all three
    were invisible by construction. A hard filter whose key is never turned is not a
    restriction, it is a deletion.

    They are also UNBOUND: bindings were built from a pool that excluded them, so no
    job points at them. Admission therefore works like admit_match_cuts — an explicit
    per-beat addition the user asked for, recorded `source: "user"`, not a job lookup.

    ADMITS ONLY. Never removes anything, and only where the user set the flag.
    """
    key = f"{beat.get('_passage','')}-{beat['id']}"
    want = (picks or {}).get(key, {}).get("contentClass") or []
    if not want: return rows, None
    have = {r["id"] for r in rows}
    extra = [{"id": r["id"], "name": r.get("description"),
              "provenance": {"source": "user", "verdict": "scoped",
                             "reason": f"beat declares content class {want}; "
                                       f"{r.get('scope')} template admitted"}}
             for r in scoped_index.values()
             if r.get("scope") in want and r["id"] not in have]
    if not extra: return rows, None
    return rows + extra, (f"Declared content class {', '.join(want)}, so "
                          f"{len(extra)} scoped template(s) are admitted here. They "
                          f"are bound to no job — this is the only route they have.")

def capacity_rank(beat, rows, pool_index):
    """Annotate each row with how well its DECLARED capacity fits the beat. Nothing is
    dropped.

    User ruling 2026-09-21 (FACTS 2.7): "slots should not be looked at as static. a 8
    slot template can be modified to be 10 or 6." Declared capacity is a hint about
    scale, never a gate. This used to DROP every record outside +/-33%, removing ~51
    options a pass on a constraint that does not exist.

    A match-cut vessel is not ranked at all: its slots hold sourced footage, not the
    beat's entities, so the beat's count says nothing about it.

    Returns (rows, note). Rows carry `_capfit`, consumed by diversify.
    """
    n = beat.get("entity_count")
    counts = {}
    for r in rows:
        if C.is_match_cut(r, pool_index) or (r.get("provenance") or {}).get("verdict") == "match-cut":
            fit = "footage"
        elif not isinstance(n, int) or n < 1:
            fit = "unknown"
        else:
            fit = C.shape([pool_index.get(r["id"], r)], n)[0][1]
        r["_capfit"] = fit
        counts[fit] = counts.get(fit, 0) + 1
    beyond = counts.get("outside", 0)
    if not beyond: return rows, None
    if beyond == len(rows):
        return rows, (f"Every option is beyond its declared capacity for {n} thing(s). "
                      f"Declared capacity is not a ceiling — each would need re-cutting.")
    return rows, (f"{beyond} of {len(rows)} are beyond their declared capacity for "
                  f"{n} thing(s); shown last, re-cuttable rather than excluded.")

PERCEPTIBLE = "/Users/dwaynetoler/timeline/grammar/perceptible.json"

def _perceptible():
    """What each beat needs the visual to ENCODE, in the template vocabulary.

    Produced by PROMPT-perceptible over must_be_perceptible. Returns
    {beat: {"carries": set, "readable": set, "missing": [...]}}.
    """
    import os
    if not os.path.exists(PERCEPTIBLE): return {}
    doc = json.load(open(PERCEPTIBLE))
    out = {}
    for r in doc["statements"].values():
        e = out.setdefault(r["beat"], {"carries": set(), "readable": set(),
                                       "missing": []})
        e["carries"].update(t for t in r["carries"] if t != "none")
        e["readable"].update(t for t in r["readable"] if t != "none")
        if r.get("missing"): e["missing"].append(r["missing"])
    return out

def encoding_rank(beat, rows, pool_index, want):
    """THE HANDSHAKE. Rank each row by whether it can encode what the beat needs seen.

    This is the one thing nothing in the pipeline did. `must_be_perceptible` was
    copied into the shot record AFTER the slate was chosen and never read — Codex's
    mechanism gap. Both sides now speak one closed vocabulary, so they can be compared.

    RANKS, NEVER EXCLUDES, like every other signal here. A template that encodes
    nothing the beat needs may still be the right answer: the beat may be servable by
    a treatment the vocabulary cannot describe, the capability pass watched one clip,
    and for a spatial scene a missing term is weak evidence (TEMPLATE-FACTS 2.9).

    Rows gain `_encfit`, a count of REQUIRED terms the record does not carry. Lower is
    better. An unmeasured record scores worst-but-one rather than best, so silence
    never outranks a measured miss.

    Returns (rows, note). The note names any required encoding NOTHING in the slate
    can carry — the finding that turns a failed beat into a sourcing line.
    """
    req_c = want.get("carries") or set()
    req_r = want.get("readable") or set()
    if not (req_c or req_r):
        for r in rows: r["_encfit"] = 0
        return rows, None
    covered = set()
    for r in rows:
        cap = (pool_index.get(r["id"]) or {}).get("capability")
        if not cap:
            # measured miss and unmeasured must not look the same
            r["_encfit"] = len(req_c) + len(req_r) + 1
            continue
        has_c = set(cap.get("carries") or [])
        has_r = set(cap.get("readable") or [])
        covered |= (req_c & has_c) | (req_r & has_r)
        r["_encfit"] = len(req_c - has_c) + len(req_r - has_r)
    gap = sorted((req_c | req_r) - covered)
    if not gap: return rows, None
    # REPORT THE OBSERVATION, NOT THE CAUSE. "NOTHING HERE HAS" was read as a claim
    # about the corpus and was false: 48_playoff_path_summary is measured to carry
    # `aggregate`, was SHOWN on all five one_vs_aggregate beats, and the user
    # rejected it every time. The honest note distinguishes "not in this slate"
    # from "not in the library" — they call for opposite actions. LOG 0077.
    elsewhere = {}
    for term in gap:
        who = [rid for rid, r in pool_index.items()
               if term in set(((r.get("capability") or {}).get("carries") or []))
               or term in set(((r.get("capability") or {}).get("readable") or []))]
        if who: elsewhere[term] = who
    msg = (f"NO OPTION IN THIS SLATE IS MEASURED TO CARRY: {', '.join(gap)}. "
           f"Every option is ranked, none excluded.")
    for term, who in elsewhere.items():
        msg += (f" The corpus does carry {term}: {', '.join(sorted(who)[:3])}"
                f"{' and others' if len(who) > 3 else ''} — not shown here, so it was "
                f"either unbound to this job or already rejected on this beat.")
    if len(elsewhere) < len(gap):
        absent = [t for t in gap if t not in elsewhere]
        msg += (f" No record in the corpus is measured to carry {', '.join(absent)}; "
                f"that is unresolved, not a verdict on the library — "
                f"{sum(1 for r in pool_index.values() if not r.get('capability'))} "
                f"record(s) are still unmeasured.")
    return rows, msg

MIRROR = P.parent / "narration"

def narration(name):
    """Read a narration file, preferring a local mirror, and CACHE one on first read.

    The narration is on Codex's Documents path, whose read permission flaps. It never
    changes, so depending on that path every run is a hard dependency on an unstable
    thing for static data — the same defect as the enrichment files in LOG 0058,
    which could veto the whole pool. First successful read writes the mirror; every
    run after that is immune.
    """
    local = MIRROR / name
    if local.exists(): return json.load(open(local))
    data = json.load(open(N + "/" + name))          # raises if genuinely unreachable
    try:
        MIRROR.mkdir(exist_ok=True)
        json.dump(data, open(local, "w"))
    except OSError:
        pass                                        # a failed cache is not a failure
    return data

def narration_seconds():
    """Total narration length, read from the timing file rather than hardcoded.

    823.5 was a literal in the run summary and the narration is 480.9s. It reported
    coverage as 53% when it is 91%, and the wrong figure was quoted as an open gap for
    a whole session before anyone divided it out.
    """
    t = narration("year-seventeen-narration-timing.json")
    return sum(p["durationSeconds"] for p in t["passages"])

def route_spatial(beat, bound, pool_index):
    """A beat naming more things than any flat template can hold ADMITS spatial scenes
    and RANKS them first. It never excludes the rest.

    User ruling 2026-09-20 set the 20-slot threshold. Until 2026-09-21 this read it as
    a hard filter and returned the spatial rows alone: beat 13a (93 entities) came back
    with a single option and the note "routed to spatial scenes only". The user's
    verdict on that slate: "this shouldnt be a rule! spatial templates can do any
    number of things. we said this already."

    They are right, and the rule they are citing is the one in CLAUDE.md: a slot count
    RANKS, it never disqualifies, because a template can be re-cut and rendering
    happens after selection. This was the last surviving hard capacity gate in the
    pipeline; every other one was converted on 2026-09-21 and this one was missed.

    No ordering code is needed here. capacity_rank() runs first and annotates a spatial
    scene `unlimited` (FIT 0) and a 93-entity-vs-8-slot flat template `outside` (FIT 3),
    and diversify() visits families in fit order. Deleting the filter is the whole fix.

    Returns (rows, note). The MAY NEED TEMPLATE SOURCE signal survives: it is a
    sourcing finding, and it now ADDS the unbound spatial scenes rather than replacing
    what was bound.
    """
    n = beat.get("entity_count")
    if not C.needs_spatial(n): return bound, None
    spatial = [r for r in bound if C.is_spatial(pool_index.get(r["id"], r))]
    if spatial:
        return bound, (f"{n} entities. Spatial scenes hold any number of things, so the "
                       f"{len(spatial)} bound here rank first; the flat templates are "
                       f"still shown and would need a re-cut to hold {n}.")
    have = {r["id"] for r in bound}
    allsp = [{"id": r["id"], "name": r.get("description"),
              "provenance": {"source": "spatial-route", "verdict": "unbound"}}
             for r in pool_index.values() if C.is_spatial(r) and r["id"] not in have]
    return allsp + bound, (
        f"MAY NEED TEMPLATE SOURCE — {n} entities and no spatial scene is bound to this "
        f"job. Adding all {len(allsp)} spatial scenes unbound; none has been judged for "
        f"it. The {len(bound)} bound flat template(s) follow, and would need a re-cut.")

def main():
    beats=json.load(open(P/"beats-all.json"))
    grammar=json.load(open(G))
    # A primary exists only where the user has chosen one. While discovering the grammar this
    # is empty, so every beat emits its full option set and nothing is pre-picked. Choosing by
    # list order is not a choice; it is the alphabetical-tiebreak failure in another form.
    primaries=json.load(open(PRIM)).get("primaries", {})
    pool_index={r["id"]: r for r in C.load()}
    # scoped templates, kept OUT of pool_index so they cannot leak into an
    # undeclared beat, and available to admit_scoped for beats that ask
    scoped_index={r["id"]: r for r in C.load(content_class="*")
                  if r.get("scope") and r["id"] not in pool_index}
    pk=pathlib.Path(P.parent/"grammar"/"picks.json")
    picks=json.load(open(pk))["beats"] if pk.exists() else {}
    # beat-flags.json says of itself: "editable by hand and merged into
    # grammar/picks.json at ingest. Separate from the review UI so a flag can be set
    # WITHOUT running a review pass." It only merged at ingest, and ingest needs a
    # pass directory — so the stated intent was not achieved and a hand-set flag did
    # nothing until the next review. Overlaid here, where it is read.
    fl=pathlib.Path(P.parent/"grammar"/"beat-flags.json")
    if fl.exists():
        for k, v in (json.load(open(fl)).get("beats") or {}).items():
            rec = picks.setdefault(k, {})
            for f in ("rawBroll", "needsTextTemplate"):
                if v.get(f): rec[f] = True
            if v.get("contentClass"): rec["contentClass"] = v["contentClass"]
    corpus=len(pool_index)
    timing={p["passageId"]:p for p in narration("year-seventeen-narration-timing.json")["passages"]}
    W=words()
    rel = _relevance_scores() if RELEVANCE else {}
    perceptible = _perceptible()
    shots=[]
    for pid in sorted(beats):
        t=timing.get(pid)
        win=[w for w in W if t and t["startSeconds"]-0.3 <= w["start"] <= t["endSeconds"]+0.3] if t else []
        bs=beats[pid]
        for i,b in enumerate(bs):
            if ONLY_BEATS and b["id"] not in ONLY_BEATS: continue
            span=place(b["quote"], win)
            if span is None and t:  # fall back to an even split of the passage
                d=(t["endSeconds"]-t["startSeconds"])/len(bs)
                span=(t["startSeconds"]+i*d, t["startSeconds"]+(i+1)*d)
            bound=grammar.get(b["job"]) or []
            b["_passage"]=pid
            # ADMISSIONS FIRST, THEN THE REJECTION FILTER. The other order let an
            # admission re-add what the user had already rejected: beat 02b is
            # flagged raw b-roll, the match-cut admission put back 24 vessels, and
            # 8 of them were things the user had turned down on that very beat.
            # A rejection means "not for this beat" and an admission does not
            # overrule it — except a binding the USER NAMED for this beat, which is
            # a current instruction rather than a past verdict.
            bound, mc_note = admit_match_cuts(b, bound, pool_index, picks)
            bound, sc_note = admit_scoped(b, bound, scoped_index, picks)
            bound, un_note = admit_user_named(b, bound, pool_index)
            named = {r["id"] for r in bound
                     if (r.get("provenance") or {}).get("verdict") == "user-named"}
            bound, rej_note = drop_prior_rejections(b, bound, picks, keep=named)
            for r in bound: r["_rel"] = rel.get(b["id"], {}).get(r["id"])
            routed, route_note = route_spatial(b, bound, pool_index)
            cap_note = None
            if CAPACITY: routed, cap_note = capacity_rank(b, routed, pool_index)
            # THE HANDSHAKE, after capacity so both annotations exist, and ahead of
            # diversify, which is where the cut actually happens.
            routed, enc_note = encoding_rank(b, routed, pool_index,
                                             perceptible.get(f"{pid}-{b['id']}", {}))
            # The family count BEFORE any beat-specific removal. Only this can
            # support a claim about the library; `routed` is post-rejection. LOG 0077.
            bound_fams = len({(pool_index.get(r["id"]) or {}).get("template")
                              for r in grammar.get(b["job"], [])
                              if r["id"] in pool_index} - {None})
            slate, flooded, note = C.diversify(routed, limit=SLATE_LIMIT, corpus_size=corpus,
                                               pool_index=pool_index,
                                               bound_families=bound_fams)
            for extra in (rej_note, mc_note, sc_note, un_note, route_note, cap_note, enc_note):
                if extra: note = f"{extra} {note or ''}".strip()
            chosen=primaries.get(b["job"])
            primary=next((r for r in bound if r["id"]==chosen), None) if chosen else None
            shots.append({
              "passage":pid,"beat":b["id"],"job":b["job"],
              "start":round(span[0],2) if span else None,
              "end":round(span[1],2) if span else None,
              "duration":round(span[1]-span[0],2) if span else None,
              "quote":b["quote"],
              "treatment":primary["id"] if primary else None,
              "treatmentName":primary.get("name") if primary else None,
              "primarySource":"user" if primary else None,
              "options":[{"id":r["id"],"name":r.get("name"),"condition":r.get("condition"),
                          "siblings":[{"id":i,
                                       "band":C.capacity_band({"id":i}, pool_index),
                                       "name":(pool_index.get(i) or {}).get("description")}
                                      for i in (r.get("_siblings") or [])],
                          "mechanism":(r.get("provenance") or {}).get("mechanism"),
                          "verdict":(r.get("provenance") or {}).get("verdict"),
                          "band":C.capacity_band(r, {**pool_index, **scoped_index}),
                          "evidence":(r.get("provenance") or {}).get("evidence")} for r in slate],
              "optionsTotal":len(bound),
              "flooded":flooded,
              "spatialRoute":C.needs_spatial(b.get("entity_count")),
              "needsTemplateSource":bool(route_note and route_note.startswith("MAY NEED")),
              "needsEncoding":bool(enc_note),
              "requiredEncoding":sorted((perceptible.get(f"{pid}-{b['id']}", {})
                                         .get("carries") or set())),
              "floodNote":note,
              "condition":(primary or {}).get("condition"),
              "takeaway":b.get("takeaway"),
              "mustBeTrue":b.get("must_be_true") or [],
              "mustBePerceptible":b.get("must_be_perceptible") or [],
              "wouldBeALie":b.get("would_be_a_lie") or [],
              "unstated":b.get("unstated") or []})
    flag_timing(shots)
    json.dump(shots, open(P/OUT,"w"), indent=1)
    return shots

def flag_timing(shots):
    """Quote-to-timing placement spans first-match to last-match, so a stray match at
    either edge stretches a beat over its neighbour. Measured 2026-09-20: 1 overlap and
    1 span of 35s against a 9.9s median. Raising the minimum block size to 2 does not
    fix it, so the mechanism is not a single stray word and the placement is left alone.
    Flag it rather than emit a wrong number silently. See no-drifting LOG 0015."""
    placed=sorted([s for s in shots if s.get("start") is not None], key=lambda s:s["start"])
    for s in shots: s["timingFlags"]=[]
    for a,b in zip(placed, placed[1:]):
        if a["end"] > b["start"] + 0.01:
            a["timingFlags"].append(f"span overlaps the next beat ({b['beat']}) by "
                                    f"{a['end']-b['start']:.1f}s")
            b["timingFlags"].append(f"start is inside the previous beat ({a['beat']})")
    d=sorted(s["duration"] for s in placed if s.get("duration"))
    if d:
        med=d[len(d)//2]
        for s in placed:
            if s.get("duration") and s["duration"] > max(25.0, med*3):
                s["timingFlags"].append(f"span {s['duration']:.0f}s is over 3x the "
                                        f"{med:.0f}s median — placement may have stretched")

if __name__=="__main__":
    s=main()
    noopt=[x for x in s if not x["options"]]
    picked=[x for x in s if x["treatment"]]
    print(f"shots: {len(s)}   with options: {len(s)-len(noopt)}   primary chosen: {len(picked)}")
    print(f"mean options shown: {sum(len(x['options']) for x in s)/len(s):.1f}"
          f"   (mean bound: {sum(x['optionsTotal'] for x in s)/len(s):.0f})")
    fl=[x for x in s if x.get("flooded")]
    if fl: print(f"flooded jobs: {sorted({x['job'] for x in fl})}")
    if noopt: print("  jobs with no options:", sorted({x['job'] for x in noopt}))
    tot=sum(x["duration"] or 0 for x in s)
    # 823.5 was hardcoded here and is wrong: the narration is 480.9s. It made coverage
    # read 53% when it is 91%, and it was quoted as a gap for a whole session. A total
    # that can drift from its source belongs to its source.
    narration=narration_seconds()
    print(f"covered: {tot:.0f}s of {narration:.0f}s ({tot*100/narration:.0f}%)"
          f"   mean shot {tot/len(s):.1f}s")
