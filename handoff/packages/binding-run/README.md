# Binding run — handoff package

Assign every template in the approved corpus to the communication jobs it can serve. One
pass per template, reused on every future video and niche. This is the step that replaces a
hand-picked grammar with a traceable one.

## Why this exists

Claude built the grammar by reading template descriptions and picking, and by regex over
description text. The user reviewed the result and found most of it wrong. Those 73 bindings
are discarded. The rule now is that every binding comes from running this prompt, and carries
provenance, or it is invalid.

## Files

| file | what it is |
|---|---|
| `PROMPT-bind.md` | the judgment prompt — the artifact that decides |
| `bind.py` | runner: batches records, stamps provenance, resumable |
| `candidates.py` | deterministic pool loader, capacity, tolerance, scope filter |
| `preflight.py` | checks the pool before spending; `bind.py` refuses to run if it fails |
| `validate_bindings.py` | refuses any binding lacking provenance; exits non-zero |
| `measure.py` | payload measurement, imports nothing that runs |
| `run.py` | transport: Anthropic Messages API, reads the key from `.env`, tracks real usage |
| `JOBS.md` | the closed set of 20 communication jobs and how it was derived |

## Transport and key

`run.py` calls the Messages API directly, so this bills the API key and does not touch a
claude.ai subscription. The key lives in `~/timeline/.env` **spelled `ANTROPIC_API_KEY`,
missing the H**. The loader accepts either spelling; the official SDK would not find it.

Model is `claude-sonnet-5`. `run.USAGE` accumulates real input and output tokens per process,
and `run.spend()` converts to dollars.

## Inputs

- Pool: `<polish>/ae-template-automation/scene-library/approved/approved-list.json`,
  authoritative, 95 cards, 425 usable records.
- Enrichment: `description-inventory.json` and `approved/catalog.json` in the same tree.
- Scope restrictions are a hard pre-filter: two lyric templates and one timeline template are
  excluded unless the content class is passed.

## Rules the prompt enforces

- Judge the mechanic, never the sample. A demo filled with years is not time-only.
- Default to magnitude over tables. A table that only supports reading exact values serves
  lookup jobs, not gap or proportion jobs.
- Slot counts do not decide. ±33% is workable, scenes combine, native capacity can exceed the
  clip.
- A portrait slot does not require a picturable subject.
- Selection is not staging. Never refuse a job because the reveal is unverified.
- Absence of evidence is `unclear`, never `no`.

## Output contract

Every binding carries `provenance`: `promptSha`, `model`, `runId`, `verdict`, `mechanism`,
`evidence`. `evidence` must be a real quoted fragment from the record. No quote, no binding.
Run `validate_bindings.py` before anything downstream consumes the grammar.

## Measured payload

| scope | records | calls | in | out | total |
|---|---|---|---|---|---|
| full | 425 | 22 | 59k | 72k | 132k |
| pilot: data-capable + one per AE family | 107 | 6 | 20k | 18k | 38k |
| data-capable only | 58 | 3 | 13k | 10k | 23k |

Token counts are conservative estimates at 3.7 chars per token, measured from the real
prompt and the real records.

## Known issue with the full run

367 of 425 records are After Effects scenes across 49 families, and the families are heavily
duplicated: 56 photo-slideshow scenes, 38 intro-slideshow, 19 carousel. Binding every variant
costs the same as binding the 58 data-capable records that carry almost all the quantitative
jobs. The pilot exists because of this.

## Two gates, one before and one after

`preflight.py` runs first and `bind.py` will not proceed if it fails. It blocks on: duplicate
ids, a suspiciously small pool, **any record whose description fell back to `title`**, more
than 10% of descriptions under 40 characters, and records with no description, use-when or
encoding at all. It reports field coverage and, for every record, which source supplied its
description and avoid-when.

`validate_bindings.py` runs after and rejects any binding without provenance.

The first guards the input, the second guards the output. The failure they exist to catch is
the same one: thin input producing confident bindings that quote the thin input as evidence,
so nothing downstream notices.

Current state: preflight passes with one warning, 11 thin descriptions out of 425, mostly
`intro-slideshow` scenes labelled "Polaroid-style cutout explanation."

## The description fix — load-bearing, read this

`candidates.py` originally built each record from the description inventory, falling back to
the approved-list scene's `title`. That was wrong in two ways and it changes what the model
sees:

- `title` is a short label. `description` is the real thing. For one bar-chart scene the
  prompt was receiving "Five horizontal category bars" when the record actually says
  "Four-row horizontal bidirectional slider bar chart, two-category comparison, centered
  baseline, top title." The second sentence is the only reason that scene is recognisable as
  serving `inversion`. The first would never have produced that binding.
- `avoidWhen` was read only from the older catalog's selection contract, missing the field on
  approved-list scenes entirely. Records carrying avoid-when went from 185 to 312 once fixed.

The loader now prefers, in order: the approved-list scene's `description`, then the
inventory's, then the catalog's, and only then `title`. Avoid-when prefers the approved-list
scene's own field.

**If you run with an older `candidates.py`, the bindings will be wrong and will look fine.**
That is the dangerous part: the model returns confident answers from thin descriptions, with
evidence quoted from the thin description, so the provenance check still passes.

## Gotcha

`bind.py` runs `main()` under a `__name__` guard. An earlier version did not, and importing
it started a real run. Do not remove the guard.
