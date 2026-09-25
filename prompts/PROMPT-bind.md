You decide which communication jobs a template can serve. One pass per template, reusable
across every video. You are not choosing for a specific beat.

## The jobs

one_vs_aggregate            one entity against a summed group
one_vs_many_individually    one entity against several named peers, not summed
entity_vs_benchmark         a value or a count against a fixed bar
proportion_of_cohort        how much of a named fixed population qualifies
parallel_instances          the same measure on several entities, each its own denominator
change_across_set           before and after position across a set
members_then_total          show the members, then their sum
category_breakdown          independent counts by type, summing to a total
inversion                   two groups split by which of a member's two values is larger
intersection_of_sets        who clears two separate thresholds
streak_over_time            unbroken presence across a span
equivalence_restatement     one entity's total restated in another's units
derived_quantity            a rate, or a total built from a rate
locate_in_distribution      where one item sits among many
explain_the_encoding        teach the viewer how to read the chart
pose_a_question             withhold, ask the viewer to commit
enumerate                   name a roster or list claims, no quantity
define_terms                state a rule, a weighting, or a period
narrate_an_event            something happened, once, at a time
assert_without_data         a norm, a hypothesis, or a limitation

## Rules

**Judge the mechanic, never the sample.** A template's semantics are what it does to its
contents, not what its demo is filled with. A layout sampled with years is not time-only.
One sampled with athletes is not athletes-only. A year callout is filler;
full-cohort-then-survivors is a mechanic.

**A slot can hold sourced footage, not only the beat's data.** A media well takes whatever
is put in it: a chart value, a portrait, a photograph, an archive clip, a screenshot of a
headline. So a template with several media wells that reveals them in turn can carry a beat
that has no data at all — by SHOWING its subject rather than MEASURING it. A claim about
what late-career artists do is served by a vessel that holds a run of footage of them doing
it.

This matters most for `assert_without_data`, which by definition has no quantity to encode.
Do not read that job as unservable. Ask instead: could a sequence of sourced shots make this
assertion land? If yes, a vessel that holds such a sequence serves it.

**But showing is not measuring.** This does not make every many-slot template serve every
job. A vessel serves a job when the job's communicative work can be done by showing. It does
NOT serve a job whose work is comparing sizes, ordering, or making a proportion legible —
a roster of photographs cannot show that one number exceeds another. Where a job needs a
quantity to be perceptible, a vessel that only shows identity still fails it.

**A template is a starting point, not a finished thing.** Nothing you are shown is what
will be on screen. **The chosen template is re-cut, recoloured, retyped and rendered to
fit the beat, AFTER selection.** So the question is never "does this already communicate
the job". It is: **can this be MADE to communicate the job.**

Specifically, and settled — do not treat any of these as constraints:
- **Slot counts are not static.** An eight-slot template can be re-cut to six or ten.
  A declared capacity is a hint about scale, never a ceiling.
- **Colour and type always change.** Every template can take new colours and new fonts.
- **Any template rendered from data can show change over time**, by being rendered at one
  moment and again at another. Do not refuse a time-based job because a still shows one
  state.
- **All media is swappable, text will fit, timing is elastic, and editability is settled.**
  Never raise these.

**But modification changes the DRESSING, never the MECHANIC.** This is the limit, and it
matters more than everything above. Re-cutting a bar chart to six bars leaves a bar chart;
it does not become a scatter. Recolouring a portrait grid leaves a portrait grid; it does
not learn to encode magnitude. What a treatment does to its contents — what it makes
visible as size, position, grouping or sequence — is fixed and is the only thing you are
judging. Scale, colour, type, data and slot count are adjustable. The encoding is not.

So: say `yes` when the mechanic fits the job and only the dressing is wrong. Say `no` when
the mechanic itself cannot do the job's work, however it is dressed.

**Default to magnitude over tables.** A treatment that shows size serves quantitative jobs
better than one that prints values. A table that only supports reading exact values serves
`enumerate` and lookup, not a job about a gap or a proportion.

**Slot counts do not decide.** Capacity within about a third either way is workable, scenes
from one template can combine, and native capacity can exceed what a clip shows. Do not
refuse a job over arity.

**A portrait slot does not require a picturable subject.** Unpicturable categories take
different images of one shared subject; labels carry the category.

**Selection is not staging.** Whether a chart builds in stages or a list accumulates is an
editing decision downstream. Never refuse a job because the reveal is unverified.

**Absence of evidence is not evidence of absence.** If the record does not say, the job is
`unclear`, never `no`.

## The template

ID: {id}
DESCRIPTION: {description}
USE WHEN: {useWhen}
AVOID WHEN: {avoidWhen}
ENCODING: {encoding}
SUITS NARRATION LIKE: {narration}
CAVEATS: {caveats}
CAPACITY: {axes}

## Output

JSON only. List every job this template can serve. Omit jobs it cannot. Most templates serve
one to three jobs; a few serve none.

```json
{"id":"...","serves":[
  {"job":"...","confidence":"clear|conditional",
   "mechanism":"three or four words for how it communicates",
   "evidence":"a line quoted from the record above that supports this",
   "condition":"only when confidence is conditional; what must hold"}
]}
```

`evidence` must be a real quoted fragment from the record. If you cannot quote one, do not
list the job. `mechanism` drives slate diversity, so make it specific: "labelled magnitude
bars", "equal portrait cards", "accumulating text rows", "held single number".
