#!/usr/bin/env python3
"""Run PROMPT-classify-reference over a story-driven reference video's visual units.

THE TEST. Every beat in this system so far is data-driven — Year Seventeen is charts,
counts and comparisons. The whole premise is that the twenty jobs port across niches.
That has never been tested against STORY. This classifies units from a finished
story-driven documentary and counts how many the taxonomy can name.

    "Rap's Misunderstood Genius: The Story of Future", 46 min, 274 visual units,
    analysed by gemini-3.8-flash into narration + rhetorical function + visual job.

**A `job: null` answer is the finding, not a failure.** The prompt says so and the
reference channel's choices are correct by definition; we are measuring our taxonomy
against them, not the other way round.

    python3 pipeline/classify_story.py                 dry run — prints the batches
    python3 pipeline/classify_story.py --n=30          calibrate on a stratified 30
    python3 pipeline/classify_story.py --n=30 --write  calls the model

`--n` takes a STRATIFIED sample by rhetoricalFunction, not the first N. The units run
in timeline order, so the first 30 are the opening six minutes and would answer a
different question than the one being asked.

Output: grammar/story-classification.json. Every record carries the prompt sha, the
model and the run id, or it is not written — the same provenance contract as every
other judgment here. Valid records cache as they arrive, so a partial failure never
re-buys work that already succeeded.
"""
import json, pathlib, sys, time, hashlib, datetime, collections

P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P))
import run as R

PROMPT = P.parent / "prompts" / "PROMPT-classify-reference.md"
SRC = pathlib.Path("/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation"
                   "/video-understanding-test/creator-reference-pilot"
                   "/creator-reference-1-full.json")
OUT = P.parent / "grammar" / "story-classification.json"
CACHE = P.parent / "grammar" / ".story-cache.json"
WRITE = "--write" in sys.argv
N = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--n=")), None)
# Units are ~5x the input of a perceptible statement (511 vs 101 chars mean), so the
# batch is smaller. run.py raises on max_tokens rather than returning half a document.
BATCH = 4
MAXTOK = 16000

JOBS = {"one_vs_aggregate", "one_vs_many_individually", "entity_vs_benchmark",
        "proportion_of_cohort", "parallel_instances", "change_across_set",
        "members_then_total", "category_breakdown", "inversion",
        "intersection_of_sets", "streak_over_time", "equivalence_restatement",
        "derived_quantity", "locate_in_distribution", "explain_the_encoding",
        "pose_a_question", "enumerate", "define_terms", "narrate_an_event",
        "assert_without_data"}
MEDIA_KINDS = {"broll", "data_animation"}

# What the prompt's Input block asks for, mapped onto this reference's field names.
SEND = ("narrationCue", "narrationParaphrase", "rhetoricalFunction", "claimType",
        "viewerTakeaway", "visualJob", "entityRelationship", "focalEntityCount")


def units():
    """Every visual unit, reduced to the fields the prompt reads."""
    d = json.load(open(SRC))
    out = []
    for u in d["visualUnits"]:
        out.append({"row": u["unitId"],
                    "start": u.get("startSeconds"),
                    **{k: u.get(k) for k in SEND if u.get(k) is not None}})
    return out


def sample(items, n):
    """A stratified sample by rhetoricalFunction, in proportion, order preserved.

    The units are in timeline order. Taking the first n would sample the opening of
    one documentary and answer "does the taxonomy cover an introduction", which is
    not the question. 18 rhetorical functions appear across 274 units; this keeps
    their proportions so a function that is 24% of the reference is 24% of the test.
    """
    if not n or n >= len(items):
        return items
    by = collections.defaultdict(list)
    for it in items:
        by[it.get("rhetoricalFunction") or "unknown"].append(it)
    quota, taken = {}, []
    for k, v in by.items():
        quota[k] = max(1, round(n * len(v) / len(items)))
    # trim or pad to exactly n, largest groups first so rounding never starves a
    # rare function out of the sample entirely
    order = sorted(by, key=lambda k: -len(by[k]))
    while sum(quota.values()) > n:
        for k in order:
            if quota[k] > 1 and sum(quota.values()) > n: quota[k] -= 1
    while sum(quota.values()) < n:
        for k in order:
            if quota[k] < len(by[k]) and sum(quota.values()) < n: quota[k] += 1
    for k in by:
        step = max(1, len(by[k]) // quota[k])
        taken += by[k][::step][:quota[k]]
    return sorted(taken, key=lambda x: x["start"] or 0)


def block(items):
    lines = []
    for it in items:
        lines.append(f"row:      {it['row']}")
        lines.append(f"NARRATION: {it.get('narrationCue', '')}")
        lines.append(f"  (paraphrase) {it.get('narrationParaphrase', '')}")
        lines.append(f"WHAT THE REFERENCE CHANNEL USED: {it.get('visualJob', '')}")
        lines.append(f"THEIR OWN DESCRIPTION OF ITS FUNCTION: "
                     f"{it.get('rhetoricalFunction', '')} / {it.get('claimType', '')}"
                     f" — {it.get('viewerTakeaway', '')}")
        lines.append(f"THEIR CHART TYPE (may be blank): "
                     f"{it.get('entityRelationship', '')}")
        lines.append(f"THEIR REVEAL (may be blank): ")
        lines.append(f"focal entities: {it.get('focalEntityCount', '')}")
        lines.append("")
    return "\n".join(lines)


def parse(reply):
    """Every shape this prompt's reply legitimately takes.

    PROMPT-classify-reference.md specifies a `{"beats":[...]}` wrapper. The first
    runner appended "Output one JSON object per line" on top of it, so the model
    obeyed whichever it preferred; when it obeyed the PROMPT, the bare line
    `{"beats": [` reached json.loads and raised at char 10, and three whole
    batches — 10 of 30 records — were thrown away. The instruction is now aligned
    with the prompt, and this accepts both anyway: a parser that only handles the
    shape we asked for last is the same defect waiting on the next prompt edit.
    """
    t = reply.strip()
    if t.startswith("```"):
        t = "\n".join(l for l in t.splitlines() if not l.strip().startswith("```"))
    t = t.strip()
    for attempt in (t, t[t.find("{"):t.rfind("}") + 1] if "{" in t else ""):
        if not attempt: continue
        try:
            d = json.loads(attempt)
        except json.JSONDecodeError:
            continue
        if isinstance(d, dict) and isinstance(d.get("beats"), list): return d["beats"]
        if isinstance(d, list): return d
        if isinstance(d, dict) and d.get("row"): return [d]
    out = []
    for line in t.splitlines():
        line = line.strip().rstrip(",").strip("`")
        if not line.startswith("{"): continue
        try: out.append(json.loads(line))
        except json.JSONDecodeError: pass
    return out


def validate(rec, want):
    """Reject anything that would make the result unreadable as a taxonomy test."""
    bad = []
    if rec.get("row") != want["row"]:
        bad.append(f"identity mismatch: got {rec.get('row')}, expected {want['row']}")
    job = rec.get("job")
    if job is not None and job not in JOBS:
        bad.append(f"job '{job}' is not one of the twenty")
    if rec.get("also") not in (None, "") and rec.get("also") not in JOBS:
        bad.append(f"also '{rec.get('also')}' is not one of the twenty")
    # THE FINDING THIS RUN EXISTS FOR. A null job with no missing_job is the model
    # shrugging, and it is indistinguishable in the output from a job that genuinely
    # has no name. The whole point is to read the second kind.
    if job is None and not (rec.get("missing_job") or "").strip():
        bad.append("job is null and missing_job is empty — 'no job fits' must say "
                   "WHAT is missing or it is not a finding")
    if rec.get("media_kind") not in MEDIA_KINDS:
        bad.append(f"media_kind {rec.get('media_kind')!r} is not broll|data_animation")
    if not isinstance(rec.get("staging_carries_it"), bool):
        bad.append("staging_carries_it is not a boolean")
    ev = (rec.get("evidence") or "").strip()
    if not ev:
        bad.append("no evidence")
    else:
        # the prompt says evidence QUOTES their words. Check it actually appears in
        # what we sent, so "evidence" cannot be the model restating its conclusion.
        # Against the LITERAL TEXT SENT, not the atomic fields. block() composes
        # "rhetoricalFunction / claimType — viewerTakeaway" into one line; five
        # records were rejected for quoting exactly that, which is the model doing
        # what it was told while the checker looked somewhere else.
        hay = block([want]).lower()
        if ev.strip('"').lower()[:40] not in hay:
            bad.append(f"evidence is not a span of their words: {ev[:60]!r}")
    return bad


def main():
    if not SRC.exists():
        print(f"reference not found: {SRC}")
        return 1
    allu = units()
    items = sample(allu, N)
    sha = hashlib.sha256(PROMPT.read_bytes()).hexdigest()[:12]
    batches = [items[i:i + BATCH] for i in range(0, len(items), BATCH)]

    dist = collections.Counter(i.get("rhetoricalFunction") for i in items)
    full = collections.Counter(i.get("rhetoricalFunction") for i in allu)
    print(f"reference: {SRC.name}")
    print(f"{len(allu)} visual units total; classifying {len(items)} "
          f"in {len(batches)} batches of <= {BATCH}")
    print(f"prompt {PROMPT.name} sha {sha}   model {R.MODEL}")
    print(f"\nstratification by rhetoricalFunction (sample vs full set):")
    for k, n in dist.most_common():
        print(f"   {str(k)[:26]:28} {n:3}   of {full[k]:3} "
              f"({100*n//max(full[k],1)}%)")

    if not WRITE:
        chars = sum(len(block([i])) for i in items)
        print(f"\nDRY RUN — no model call, no spend.")
        print(f"input to send: ~{chars:,} chars (~{chars//4:,} tokens) plus the "
              f"{len(PROMPT.read_text())//4:,}-token prompt x {len(batches)} batches")
        print(f"\nfirst batch:\n{block(batches[0])[:700]}")
        print(f"\nRe-run with --write to spend.")
        return 0

    tmpl = PROMPT.read_text()
    runid = f"story-{datetime.datetime.now():%Y%m%dT%H%M%S}"
    records, failures = {}, []
    cached_at_start = 0
    if CACHE.exists():
        cached = json.load(open(CACHE))
        records = {k: v for k, v in cached.items()
                   if (v.get("provenance") or {}).get("promptSha") == sha}
        cached_at_start = len(records)
        if records: print(f"\nreusing {len(records)} cached records from this sha")
    todo = [i for i in items if i["row"] not in records]
    batches = [todo[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    if not todo:
        print("every unit is already cached — nothing to buy")

    for n, batch in enumerate(batches, 1):
        # No output instruction here: the prompt file already specifies the
        # wrapper, and stating a second, different one is what lost three batches.
        prompt = (f"{tmpl}\n\n---\n\nClassify each of the following {len(batch)} "
                  f"beats.\n\n{block(batch)}")
        try:
            reply = R.ask(prompt, max_tokens=MAXTOK)
        except RuntimeError as e:
            failures.append(f"batch {n}: {e}")
            print(f"  batch {n}/{len(batches)}  FAILED: {e}")
            continue
        got = parse(reply)
        if not got:
            failures.append(f"batch {n}: nothing parseable in the reply")
        if len(got) != len(batch):
            failures.append(f"batch {n}: asked for {len(batch)}, got {len(got)}")
        by = {g.get("row"): g for g in got}
        for want in batch:
            rec = by.get(want["row"])
            if rec is None:
                failures.append(f"{want['row']}: no record returned")
                continue
            bad = validate(rec, want)
            if bad:
                failures.extend(f"{want['row']}: {b}" for b in bad)
                continue
            rec["narrationCue"] = want.get("narrationCue")
            rec["rhetoricalFunction"] = want.get("rhetoricalFunction")
            rec["startSeconds"] = want.get("start")
            rec["provenance"] = {"promptSha": sha, "model": R.MODEL, "runId": runid,
                                 "source": "pipeline", "reference": SRC.name}
            records[want["row"]] = rec
        CACHE.write_text(json.dumps(records, indent=1))
        print(f"  batch {n}/{len(batches)}  {len(got)} back, {len(records)} valid   "
              f"${R.spend():.3f}  (cached)")
        time.sleep(0.4)

    print(f"\ncalls {R.USAGE['calls']}  in {R.USAGE['in']:,}  out {R.USAGE['out']:,}  "
          f"${R.spend():.3f}")
    # Divide by what this run BOUGHT, not by what is in the dict — the dict
    # includes cached records from earlier runs, and on the calibration re-run
    # that reported $0.0033/unit when the true rate was $0.0083. A per-unit cost
    # is the anchor for every later spend decision; getting it wrong here is the
    # measured-or-estimated rule broken at the point it matters most.
    bought = len(records) - cached_at_start
    if bought > 0:
        print(f"MEASURED THIS RUN: ${R.spend()/bought:.4f} per unit over {bought} "
              f"bought ({len(records)-bought} came from cache)")
    print(f"   remaining unclassified: {len(allu)-len(records)}")
    print(f"valid records: {len(records)} of {len(items)}")

    if failures:
        print(f"\n{len(failures)} PROBLEM(S) — nothing is written on a partial run:")
        for f in failures[:25]: print(f"  {f}")
        if len(failures) > 25: print(f"  ... and {len(failures)-25} more")
        print(f"\nNOT WRITTEN. {len(records)} valid records cached in {CACHE.name}; "
              f"a re-run buys only the {len(items)-len(records)} missing.")
        return 1

    # THE ANSWER
    named = [r for r in records.values() if r.get("job")]
    unnamed = [r for r in records.values() if not r.get("job")]
    print(f"\n{'='*66}\nDOES THE TAXONOMY HOLD FOR STORY?")
    print(f"   named by one of the twenty : {len(named)} of {len(records)} "
          f"({100*len(named)//max(len(records),1)}%)")
    print(f"   no job fits                : {len(unnamed)}")
    for r in unnamed:
        print(f"      {r['row']}  missing: {r.get('missing_job')}")
        print(f"         evidence: {(r.get('evidence') or '')[:90]}")
    jc = collections.Counter(r["job"] for r in named)
    print(f"\n   jobs used: {len(jc)} of 20")
    for j, n in jc.most_common(): print(f"      {j:26} {n}")
    unused = sorted(JOBS - set(jc))
    print(f"   never used ({len(unused)}): {', '.join(unused)}")
    mk = collections.Counter(r["media_kind"] for r in records.values())
    print(f"\n   media kind: {dict(mk)}")

    OUT.write_text(json.dumps(
        {"provenance": {"promptSha": sha, "model": R.MODEL, "runId": runid,
                        "reference": SRC.name, "referenceTitle": json.load(open(SRC))
                        .get("referenceTitle"),
                        "sampledFrom": len(allu), "classified": len(records),
                        "stratifiedBy": "rhetoricalFunction",
                        "generatedAt": datetime.datetime.now().isoformat()},
         "units": records}, indent=1))
    print(f"\nwrote {OUT}")
    CACHE.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
