# Candidate judgment prompt

Stage 2. Stage 1 is `candidates.py`: it reads the template description inventory, matches
every capacity axis a record declares, and keeps anything inside ±33% of the beat's count
(6 → 4..8), plus everything whose capacity is unknown. Stage 1 never rejects.

This prompt runs once per surviving candidate, against one beat. It does not rank and does
not choose. It classifies with evidence, and a later step fills the slate.

---

You are judging whether one template can carry one beat of documentary narration.

## The beat

NARRATION: {quote}
TAKEAWAY: {takeaway}
MUST BE TRUE: {must_be_true}
WOULD BE A LIE: {would_be_a_lie}
ENTITY COUNT: {n} {entity_kind}

## The candidate

ID: {id}
DESCRIPTION: {description}
SUITS NARRATION LIKE: {appropriate_narration}
AVOID WHEN: {avoid_when}
CAVEATS: {caveats}
ENCODING: {encoding}
CAPACITY: {axes}  (beat needs {n}; tolerance {lo}..{hi})

## How to judge

Work through these in order and stop at the first that applies.

1. **Contradicted.** Something the record itself states rules this out. An avoid-when that
   matches this beat's situation, or a caveat naming a limitation the beat depends on. Quote
   the exact line. A limitation you infer from the description is not a contradiction; it is
   unresolved.

2. **Unresolved.** The record does not say enough. Missing capacity, no text or value slots
   recorded, a thumbnail-only description. Name the specific unknown. Absence of evidence is
   never a contradiction.

3. **Complete fit.** Every part of MUST BE TRUE survives in this treatment, and nothing in
   WOULD BE A LIE is implied. Say which line of the record carries each requirement.

4. **Weaker fallback.** It communicates the beat without lying, but something in TAKEAWAY
   lands less well than another mechanism would. Say what is lost.

## Rules that decide most cases

**A prohibition names a false implication, never a visual family.** "Would be a lie: ranking
them against each other" forbids a treatment that says these four compete. It does not forbid
charts, bars, axes or magnitude. Ask whether THIS template would imply the false thing, not
whether it belongs to a family that sometimes does.

**Two quantities that must not share one axis may still each be encoded as magnitude.** Two
separately labelled scales are not one shared scale. When the beat says a figure is
load-bearing, a treatment that shows its size beats a treatment that prints it as text, and
printing it as text is the weaker option rather than the safe one.

**Capacity inside tolerance is not a defect.** Templates are pre-rendered and a slot count
within ±33% is workable. Do not mention spare or missing slots unless the mismatch falls
outside tolerance, and then flag it for review rather than rejecting.

**Scenes from one template may combine.** A clipped scene carrying one slot is not limited to
one slot when its siblings can run in sequence. Judge the template's combined capacity where
the beat wants an accumulating list.

**Judge the mechanic, never the sample content.** A template's semantics are what it does
structurally, not what the demo happens to be filled with. A layout whose sample cycles years
is not therefore time-only; a layout sampled with three athletes is not therefore limited to
athletes. Ask what the treatment *does* to data, then ask whether this beat needs that.

**A portrait slot is not a requirement that the category be picturable.** When the things
being labelled have no face — release types, award categories, years — the slots take
different images of the shared subject and the labels carry the category. Never reject a
layout because its subject matter cannot be photographed.

**Default to magnitude over tables.** A treatment that shows size communicates better than one
that prints values. Reach for a table only when the beat is genuinely a lookup.

**Unknown capacity is not zero capacity.** Say what would have to be checked.

## Output

```json
{
  "id": "...",
  "verdict": "complete_fit | weaker_fallback | contradicted | unresolved",
  "mechanism": "how it communicates, in three or four words, e.g. labelled magnitude bars,
                equal portrait cards, accumulating text rows, held single number",
  "why": "one or two sentences addressed to an editor",
  "evidence": ["exact lines quoted from the record"],
  "unknowns": ["what a human must still verify"],
  "capacity_flag": null
}
```

`mechanism` is required and is not decoration. The slate is filled by distinct mechanism
before a second instance of any mechanism, so a vague value produces a redundant slate.
