# PROMPT-perceptible

Translate a beat's **`must_be_perceptible`** statements — free prose written by the beat
extractor — into the **same closed vocabulary the templates were measured in**, or say
that no term fits and name what is missing.

This is one half of a handshake. `PROMPT-describe-clip` asked, of every clip: *what
relations can this make visible in its form?* and recorded the answer as `carries` and
`readable`. This prompt asks, of every beat: *what relations must be visible for this
beat to land?* Only when both sides speak the same vocabulary can anything compare them.

**A "nothing fits" answer is a finding, not a failure.** It means the beat needs an
encoding the system has no word for, which is a gap in the vocabulary or in the library
and must be visible as such. Do not stretch a term to cover something it does not name.

## The vocabulary

Identical to `PROMPT-describe-clip`, deliberately. Do not add to it, do not rename, do
not invent a compound.

### `carries` — the relation is in the VISUAL FORM

A viewer could still see it with every label stripped off.

A relation counts whether the visual shows it in ONE FRAME or performs it ACROSS
THE CLIP. A beat that needs two groups to narrow to their shared members needs
`overlap` however the visual gets there.

```
magnitude          size differences are visible as size
share_of_whole     a part reads as a proportion of a total
rank               who is ahead is visible — comparative, not arrival order
change_over_time   movement between states is visible
difference         a gap between two things is visible as a gap
parity             two or more things read as THE SAME — deliberately equal, not
                   merely unranked
aggregate          several things pool into one — as parts in a total, or as items
                   gathering into a single figure
derivation         one value is visibly computed from another
membership         belonging to a group is visible
overlap            the intersection of two sets is visible — both sets shown with
                   their shared members in the crossing, or sets reducing until only
                   the common members remain
absence            something reads as MISSING, distinct from a zero — a gap, an empty
                   slot, a break in a run, or an item leaving and not replaced
identity           who or what a subject is, is visible
none               presentation only, carries no relation
```

`parity` and the widened `aggregate`, `overlap` and `absence` were added 2026-09-21.
Beat 29b's requirement — "The three values must read as equal to one another, not
ranked above or below each other" — could not be expressed at all: every term named
a difference, an order, a part or a change, and none named sameness.

### `readable` — the viewer gets it by READING

```
label                a short name or title — the text says WHO or WHAT
statement            a phrase or sentence read as a claim, question, rule, definition
exact_value  ordering  proportion  difference  grouping  position_in_sequence  none
```

`label` and `statement` were added 2026-09-21. Every other value is a DATA relation
read from text, so a beat that needs a sentence on screen had no way to say so. A beat
that must state a rule needs `statement`; a beat that must name who is on screen needs
`label`. They are not interchangeable.

## Rules

**The distinction between the two fields is the whole point.** A statement that says a
figure must be *legible*, *stated*, *printed* or *labelled* is `readable`. A statement
that says something must *read as*, *appear as*, *be visible as* or *stand out* is
`carries`. Where the prose demands both, record both — that is common and correct.

> "The four percentages must be distinguishable as separate, escalating values
> (50, 52, 71, 79), each anchored to its own artist."

The escalation must be seen (`carries`), the four numbers are named and must be
attributable (`readable: exact_value`, `carries: identity`). Three terms, all real.

**A negation is a requirement, not a term.** "…not as two disconnected numbers", "…not
as a zero", "…not one ranked list" tells you what must NOT read. Record the positive
requirement in `carries`/`readable`, and put the thing that must not happen in
`must_not_imply`, using the `implies` vocabulary: `ranking` `competition` `chronology`
`causation` `completeness` `equality` `independence` `none`. Half these statements carry a negation and
it is usually the sharper half of the sentence.

**Do not infer from the job.** You are given the beat's job for context only. A
`one_vs_aggregate` beat does not automatically require `aggregate` — read what the
statement actually demands. If the statement is about size and never about pooling, it
is `magnitude`, not `aggregate`.

**Do not infer from the quote.** The quote is context. The statement is the requirement.
A number appearing in the narration does not make the beat need `exact_value`; only a
statement that the number must be readable does.

**One statement at a time.** Each statement gets its own classification. A beat with two
statements gets two records. Do not merge them; they often demand different things, and
a template that satisfies one and not the other is exactly what the handshake must catch.

**When nothing fits**, set `carries` and `readable` to `[]` and write `missing` — one
phrase in the same register as the vocabulary above, describing the relation that has no
term. Example register: "a quantity restated in another entity's units", "a scope
limitation on a claim". Not a chart type.

## Evidence is required

Every term is justified by a span **lifted verbatim from the statement**, not
paraphrased. A term with no span is not a classification, it is an opinion, and the
validator drops the record.

**Evidence keys are `field:term`, not `term`.** `difference` is a legal value of BOTH
`carries` and `readable` and they mean different things — a visible gap versus a
printed delta. A flat dict keyed by term cannot hold both spans, so key every entry
`carries:difference`, `readable:exact_value`, and so on. One key per term per field,
always, even when the term appears in only one field.

## Output

One JSON object per statement, one per line, no prose around it.

```json
{
  "beat": "09-09",
  "statement_index": 0,
  "carries": ["magnitude", "identity"],
  "readable": ["exact_value"],
  "must_not_imply": [],
  "evidence": {
    "carries:magnitude": "distinguishable as separate, escalating values",
    "carries:identity": "each anchored to its own artist",
    "readable:exact_value": "(50, 52, 71, 79)"
  },
  "missing": null,
  "confidence": "clear"
}
```

`confidence` is `clear` or `unclear`. Use `unclear` when the prose is ambiguous enough
that a different reader would plausibly choose different terms, and say why in
`unclear_why`. An `unclear` record is kept and flagged, never discarded — the count of
them measures how well the extractor's prose and this vocabulary fit each other.

## Input

```
beat:      <passage-beat>
job:       <job name, context only>
quote:     <the narration, context only>
statement: <one must_be_perceptible statement>
```
