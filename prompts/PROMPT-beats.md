You split one passage of documentary narration into beats and write the requirements a
visual must meet for each one.

## Input

Several passages, in order, each with its number. Passages before and after the set are given
as context only.

CONTEXT BEFORE: {before}
{passages}
CONTEXT AFTER: {after}

Neighbours matter. A beat's point often depends on the sentence after it, including the first
sentence of the next passage. Read across the set before deciding what any beat is doing. Do
not write requirements for the context passages.

## Split into beats

A beat is one shot. Split only when the picture must genuinely change, never because the
sentence moved on.

**The test: could one shot, allowed to develop over time, carry both parts?** A shot is not a
still. A counter ticks up. A chart builds. A list accumulates. A camera pushes in. If a single
developing shot holds the whole thought, it is one beat.

Three rules that follow:

- **Two consecutive parts with the same job and the same subject are one beat.** A rate and
  the total it reaches are one counter, not two shots. Teaching what a dot means and then
  where to start reading is one chart build, not two.
- **A setup and its payoff are one beat** when one treatment can hold both.
- **Split when the subject changes, the measure changes, or the job changes.** Those are
  reliable signals that the picture has to change.
- **Split identity from claim.** When a passage names or credentials someone before making a
  claim about them, that is two beats: the person, then the claim. "Curren$y was on the 2009
  XXL Freshman cover" is a portrait. "His whole catalog equals twenty-four days of this one"
  is a comparison. One shot cannot be both.

Default to one beat per passage. Two is common. Three needs a real reason, and you should be
able to name which of the three signals above forced each split.

## Per beat, emit

**job** — exactly one from this closed set:

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

If none fits, use `unclassified` and say why. Never invent a job name.

**entity_count** and **entity_kind** — how many things, and what kind of thing.

**takeaway** — what the viewer should come away with, as distinct from what the sentence
says. Not a mood. Something a visual can be judged against.

**must_be_true** — propositional facts that have to survive. Units, denominators, what a
number counts, which side is which.

**must_be_perceptible** — what the viewer has to *see* rather than read. A size difference, a
proportion, a reversal, an absence. Leave empty when the beat only needs its facts stated.

**would_be_a_lie** — the false implication a visual must not create.

## Rules

**Write only what the narration does not already say.** If the sentence states it plainly, it
does not go in the record. Empty fields are correct and common. Most beats have one or two
populated fields, not five.

**A prohibition names a false implication, never a visual family.** "Ranking them against each
other" is a prohibition. "No bar charts" is not. Bars, axes and magnitude are never forbidden
as such; implying a false relationship is.

**A perceptual requirement must be satisfiable by more than one mechanism.** "The size
difference must be visible" is a requirement. "Use a tall bar" is a preference. If only one
treatment could satisfy what you wrote, rewrite it or drop it.

**Never name a template, a family, a chart type or a tag.** Not in any field.

**Unstated is unknown.** If the narration does not say how two groups overlap, say the overlap
is unstated. Do not infer it, and do not let a visual imply it.

## Output

Return JSON only, no prose around it.

Return every passage in the set, in order.

```json
{"passages":[{"passage":"01","beats":[{
  "id":"01",
  "quote":"the exact words this beat covers",
  "job":"...",
  "entity_count":0,
  "entity_kind":"",
  "takeaway":"",
  "must_be_true":[],
  "must_be_perceptible":[],
  "would_be_a_lie":[],
  "unstated":[]
}]}]}
```
