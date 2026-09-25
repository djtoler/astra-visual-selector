#!/usr/bin/env python3
"""Run PROMPT-perceptible over every must_be_perceptible statement in the beat set.

The beat half of the handshake. PROMPT-describe-clip already asked every measured clip
what relations it can make visible; this asks every beat what relations must be visible
for it to land, in the SAME closed vocabulary, so the two can finally be compared.

    python3 pipeline/classify_perceptible.py            dry run — prints the batches
    python3 pipeline/classify_perceptible.py --write    calls the model, writes output

Output: grammar/perceptible.json, keyed "<beat>#<statement_index>". Every record
carries the prompt sha, the model and the run id, or it is not written — same
provenance contract as every other judgment in this pipeline.

Batched because 39 statements in 39 calls is 39x the prompt tokens for no benefit. The
batch is capped so a truncated reply is impossible rather than merely unlikely; run.py
raises on max_tokens rather than handing back half a JSON document.
"""
import json, pathlib, sys, time, hashlib, datetime

P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P))
import run as R

PROMPT = P.parent / "prompts" / "PROMPT-perceptible.md"
BEATS = P / "beats-all.json"
OUT = P.parent / "grammar" / "perceptible.json"
WRITE = "--write" in sys.argv
# 8 truncated a reply at 8000 tokens on the first run and cost $0.52 for nothing.
# Each record is ~1000 output tokens once evidence spans are included.
BATCH = 5
MAXTOK = 16000
# Valid records are cached as they arrive. The all-or-nothing contract is about what
# gets WRITTEN, not about re-buying work that already succeeded: the first run lost 30
# good records to one truncated batch and one schema bug.
CACHE = P.parent / "grammar" / ".perceptible-cache.json"

CARRIES = {"magnitude", "share_of_whole", "rank", "change_over_time", "difference",
           "parity", "aggregate", "derivation", "membership", "overlap", "absence",
           "identity", "none"}
READABLE = {"label", "statement", "exact_value", "ordering", "proportion",
            "difference", "grouping", "position_in_sequence", "none"}
IMPLIES = {"ranking", "competition", "chronology", "causation", "completeness",
           "equality", "independence", "none"}


def statements():
    """Every must_be_perceptible statement, with the context the prompt asks for."""
    beats = json.load(open(BEATS))
    out = []
    for pid in sorted(beats):
        for b in beats[pid]:
            for i, s in enumerate(b.get("must_be_perceptible") or []):
                out.append({"beat": f"{pid}-{b['id']}", "statement_index": i,
                            "job": b.get("job", ""), "quote": b.get("quote", ""),
                            "statement": s})
    return out


def block(items):
    lines = []
    for it in items:
        lines.append(f"beat:      {it['beat']}")
        lines.append(f"job:       {it['job']}")
        lines.append(f"quote:     {it['quote']}")
        lines.append(f"statement: {it['statement']}")
        lines.append(f"statement_index: {it['statement_index']}")
        lines.append("")
    return "\n".join(lines)


def validate(rec, want):
    """Reject anything that would poison the handshake. Loudly, naming the record."""
    key = f"{rec.get('beat')}#{rec.get('statement_index')}"
    bad = []
    if rec.get("beat") != want["beat"] or rec.get("statement_index") != want["statement_index"]:
        bad.append(f"identity mismatch: got {key}, expected "
                   f"{want['beat']}#{want['statement_index']}")
    for field, vocab in (("carries", CARRIES), ("readable", READABLE),
                         ("must_not_imply", IMPLIES)):
        v = rec.get(field)
        if v is None:
            bad.append(f"{field} missing")
            continue
        if not isinstance(v, list):
            bad.append(f"{field} is not a list")
            continue
        for term in v:
            if term not in vocab: bad.append(f"{field}: '{term}' is not in the vocabulary")
    ev = rec.get("evidence") or {}
    # Keyed "field:term". `difference` is legal in BOTH carries and readable and means
    # different things in each; a flat dict keyed by term cannot hold both spans, and
    # on the first run that lost beat 27 and reported the same failure twice.
    for field in ("carries", "readable"):
        for term in (rec.get(field) or []):
            if term == "none": continue
            span = ev.get(f"{field}:{term}") or ev.get(term)
            if not span:
                bad.append(f"no evidence span for '{field}:{term}'")
            elif span.strip().lower() not in want["statement"].lower():
                # the span must be lifted from the statement, not paraphrased —
                # otherwise "evidence" is the model restating its own conclusion.
                bad.append(f"evidence for '{field}:{term}' is not a span of the "
                           f"statement: {span!r}")
    if not (rec.get("carries") or rec.get("readable")) and not rec.get("missing"):
        bad.append("nothing classified and no `missing` written — silence and "
                   "'no term fits' must not look the same")
    if rec.get("confidence") not in ("clear", "unclear"):
        bad.append(f"confidence {rec.get('confidence')!r} is not clear|unclear")
    return bad


def main():
    items = statements()
    sha = hashlib.sha256(PROMPT.read_bytes()).hexdigest()[:12]
    batches = [items[i:i + BATCH] for i in range(0, len(items), BATCH)]
    print(f"{len(items)} statements across {len({i['beat'] for i in items})} beats, "
          f"{len(batches)} batches of <= {BATCH}")
    print(f"prompt {PROMPT.name} sha {sha}   model {R.MODEL}")
    if not WRITE:
        print("\nDRY RUN — no model call, no spend. Re-run with --write.")
        print(f"\nfirst batch:\n{block(batches[0])[:600]}")
        return

    tmpl = PROMPT.read_text()
    runid = f"perceptible-{datetime.datetime.now():%Y%m%dT%H%M%S}"
    records, failures = {}, []
    if CACHE.exists():
        cached = json.load(open(CACHE))
        # only reuse records produced by THIS prompt version
        records = {k: v for k, v in cached.items()
                   if (v.get("provenance") or {}).get("promptSha") == sha}
        if records: print(f"reusing {len(records)} cached records from this prompt sha")
    todo = [i for i in items
            if f"{i['beat']}#{i['statement_index']}" not in records]
    batches = [todo[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    if not todo:
        print("every statement is already cached — nothing to buy")
    else:
        print(f"{len(todo)} still to classify, {len(batches)} batches")
    for n, batch in enumerate(batches, 1):
        prompt = (f"{tmpl}\n\n---\n\nClassify each of the following "
                  f"{len(batch)} statements. Output one JSON object per line, "
                  f"nothing else.\n\n{block(batch)}")
        try:
            reply = R.ask(prompt, max_tokens=MAXTOK)
        except RuntimeError as e:
            failures.append(f"batch {n}: {e}")
            print(f"  batch {n}/{len(batches)}  FAILED: {e}")
            continue
        got = []
        for line in reply.splitlines():
            line = line.strip().strip("`")
            if not line.startswith("{"): continue
            try: got.append(json.loads(line))
            except json.JSONDecodeError as e: failures.append(f"batch {n}: bad JSON: {e}")
        if len(got) != len(batch):
            failures.append(f"batch {n}: asked for {len(batch)} records, got {len(got)}")
        by = {(g.get("beat"), g.get("statement_index")): g for g in got}
        for want in batch:
            rec = by.get((want["beat"], want["statement_index"]))
            if rec is None:
                failures.append(f"{want['beat']}#{want['statement_index']}: no record returned")
                continue
            bad = validate(rec, want)
            if bad:
                failures.extend(f"{want['beat']}#{want['statement_index']}: {b}" for b in bad)
                continue
            rec["statement"] = want["statement"]
            rec["job"] = want["job"]
            rec["provenance"] = {"promptSha": sha, "model": R.MODEL, "runId": runid,
                                 "source": "pipeline"}
            records[f"{want['beat']}#{want['statement_index']}"] = rec
        CACHE.write_text(json.dumps(records, indent=1))
        print(f"  batch {n}/{len(batches)}  {len(got)} back, "
              f"{len(records)} valid so far   ${R.spend():.3f}  (cached)")
        time.sleep(0.4)

    print(f"\ncalls {R.USAGE['calls']}  in {R.USAGE['in']:,}  out {R.USAGE['out']:,}  "
          f"${R.spend():.3f}")
    print(f"valid records: {len(records)} of {len(items)}")
    if failures:
        print(f"\n{len(failures)} PROBLEM(S) — nothing is written on a partial run:")
        for f in failures[:25]: print(f"  {f}")
        if len(failures) > 25: print(f"  ... and {len(failures)-25} more")
        # All-or-nothing, same contract as ingest_capability.py. A half-classified
        # beat set is worse than none: the handshake would silently skip the beats
        # that failed, and those are the interesting ones.
        print(f"\nNOT WRITTEN. {len(records)} valid records are cached in "
              f"{CACHE.name}; a re-run buys only the {len(items)-len(records)} missing.")
        return 1
    OUT.write_text(json.dumps({"provenance": {"promptSha": sha, "model": R.MODEL,
                                              "runId": runid,
                                              "generatedAt": datetime.datetime.now().isoformat()},
                               "statements": records}, indent=1))
    print(f"wrote {OUT}")
    CACHE.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
