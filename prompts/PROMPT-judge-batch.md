You judge whether each template can carry one beat of documentary narration.

## The beat

NARRATION: {quote}
TAKEAWAY: {takeaway}
MUST BE TRUE: {must_be_true}
WOULD BE A LIE: {would_be_a_lie}
NEEDS: {n} {entity_kind}   (slot tolerance {lo}..{hi})

## Rules

**Judge the mechanic, never the sample.** A template's semantics are what it does to data, not
what its demo is filled with. A layout sampled with years is not time-only; one sampled with
athletes is not athletes-only.

**A prohibition names a false implication, not a visual family.** "Do not rank them" forbids
implying they compete. Bars, axes and magnitude are never forbidden as such.

**Default to magnitude over tables.** Showing size beats printing values unless the beat is
genuinely a lookup. A table that only supports reading exact values is a weaker fallback.

**Slot counts inside tolerance are not a defect.** Do not mention spare or missing slots.
Scenes from one template can combine. Native capacity can exceed what a clip shows.

**A portrait slot does not require the subject to be picturable.** Unpicturable categories take
different images of one shared subject; the label carries the category.

**Unknown capacity is not zero capacity.**

## Verdicts, first match wins

- `contradicted` — the record's own avoid-list or caveat rules it out. Quote the line. A
  limitation you infer is not a contradiction.
- `unresolved` — the record does not say enough. Name the unknown.
- `complete_fit` — everything in MUST BE TRUE survives and nothing implies the lie.
- `weaker_fallback` — communicates it without lying, but something in TAKEAWAY lands less well.

## Candidates

{candidates}

## Output

JSON only. One entry per candidate, same ids, no extras.

```json
{"verdicts":[{"id":"...","verdict":"...","mechanism":"three or four words","why":"one sentence","evidence":"quoted line or null"}]}
```

`mechanism` is required and must describe how it communicates, e.g. "labelled magnitude bars",
"equal portrait cards", "accumulating text rows", "held single number". Slates are filled by
distinct mechanism, so a vague value produces a redundant slate.
