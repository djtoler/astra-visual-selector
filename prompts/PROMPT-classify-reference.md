# PROMPT-classify-reference

Classify a beat from a **reference video** — one the system is trying to mimic — into the
job taxonomy, **or say that no job fits and name what is missing.**

This is a test of the taxonomy, not of the beat. The reference channel's choices are
treated as correct by definition; we are measuring whether our twenty jobs can describe
them. **A "no job fits" answer is a finding, not a failure.** Do not stretch a job to
cover something it does not name.

## The twenty jobs

```
one_vs_aggregate            one thing against many treated as a single mass
one_vs_many_individually    one thing against several, each named
entity_vs_benchmark         a value or a count against a fixed bar
proportion_of_cohort        how much of a named fixed population qualifies
parallel_instances          the same measure across several, no winner implied
change_across_set           the same things measured at two or more times
members_then_total          parts shown, then summed
category_breakdown          one thing split into named categories
inversion                   a relation that reverses between two groups
intersection_of_sets        what two sets share
streak_over_time            an unbroken run
equivalence_restatement     the same quantity said a second way
derived_quantity            a figure computed from two others
locate_in_distribution      one thing placed in a field of many
explain_the_encoding        teach the viewer how to read the chart
pose_a_question             withhold, ask the viewer to commit
enumerate                   name a roster or list claims, no quantity
define_terms                state a rule, a weighting, or a period
narrate_an_event            something happened, once, at a time
assert_without_data         a norm, a hypothesis, or a limitation
```

## Rules

**One job, or none.** If two fit, pick the one doing the communicative work; name the
other in `also`. If none fits, set `job` to `null` and describe the missing job in
`missing_job` — in the same register as the list above, a relation not a chart type.

**Judge the beat, not the chart.** "Scatter plot" is a treatment. The job is what the
beat is asserting. A scatter and a leaderboard can serve the same job.

**Staging is not a job.** "Climax", "bait-and-switch", "ascending reveal" describe HOW a
visual unfolds. If that is the only thing distinguishing the beat, say so in
`staging_carries_it` and still give the underlying job.

**Footage or built.** Say whether this beat is served by sourced footage of its subject,
or by a graphic built from data. The reference calls these `broll` and `data_animation`.

## Input

```
NARRATION: {narration}
WHAT THE REFERENCE CHANNEL USED: {visual}
THEIR OWN DESCRIPTION OF ITS FUNCTION: {function}
THEIR CHART TYPE (may be blank): {chart}
THEIR REVEAL (may be blank): {reveal}
```

## Output

One JSON object per beat, in a `{"beats":[...]}` wrapper.

```json
{"row":"VTT-v3-003",
 "job":"locate_in_distribution",
 "also":null,
 "missing_job":null,
 "staging_carries_it":true,
 "media_kind":"data_animation",
 "evidence":"quote the phrase in their function or narration that decided it"}
```

`evidence` must quote their words, not paraphrase. If `job` is null, `missing_job` is
required and `evidence` must say what our twenty do not cover.
