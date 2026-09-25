# Niche grammar

> **All bindings must come from `pipeline/bind.py`.** Hand-picked bindings are invalid and
> `pipeline/validate_bindings.py` rejects them. The 73 bindings written on 2026-09-19 were
> hand-picked and have been discarded. See the HARD RULE in CLAUDE.md.

# Niche grammar v2 — after review

## The pattern in the rejections

Your words: "clear evidence of your over reliance on data infographics."

Every rejection is the same mistake. Given a job, I reach for a layout that **displays
values** over one that **encodes magnitude**. Tables and matrices over counters and bars.
Reading numbers over seeing size.

- `derived_quantity`: I offered a finals record table, a measurement panel and a portrait
  matrix against "seven hundred times a second." Three of four rejected. A counter was the
  obvious answer and I ranked it last.
- `one_vs_many_individually`: the three rejected are rank-context, similarity-score and
  endpoint-bar layouts. The four you left standing all encode the entity's own magnitude.
- `parallel_instances`: "showing this on a graph would work as well."
- Earlier, on features: "see a line significantly taller than the other communicates that
  more impactfully."

Same note four times. Default to magnitude, use a table only when the beat is genuinely a
lookup.

## Jobs settled

| job | state |
|---|---|
| `entity_vs_benchmark` | all confirmed |
| `locate_in_distribution` | all confirmed |
| `streak_over_time` | all confirmed |
| `parallel_instances` | confirmed, add graph-based options, avoid four near-identical cards |
| `proportion_of_cohort` | 30_dense_rank_bars, truth-population-field |
| `equivalence_restatement` | truth-ratio-days, approved and sufficient |
| `one_vs_many_individually` | keep 51, 52, 32, 41. 27 and 29 removed from the library as poor designs. 47 dropped on arity and comparison type: 35 entries against 4 peers, and a similarity score rather than each entity's own magnitude |
| `intersection_of_sets` | `truth-cohort-attrition`. Confirmed. Full cohort, progressive elimination, named survivors |
| `streak_over_time` | also served by `truth-cohort-attrition` in its as-sampled form |
| `one_vs_aggregate` | 34 (tweak one side to a single entity), plus truth-population-field, 53, 51, 46, 48 |

## Three holes I invented that were not holes

I called these gaps. They are not, and I found them by reading the cinematic 3D availability
field I had been ignoring. Five of the nine 3D layouts are approved and I only ever used
three of them.

- **`change_across_set`** — `truth-rank-fall`, "before-and-after rank-loss field", approved.
  That is passage 12 exactly: Ab-Soul falls twenty-eight places, Drake finishes where he
  started. I declared a hole while an approved layout named the job.
- **`one_vs_aggregate`** — six candidates once you added yours. Not a hole.
- **`equivalence_restatement`** — truth-ratio-days is approved, not reference-only. My note
  was wrong.

## Standing rules from review

**Sample content is not a constraint.** A template's semantics are the *mechanic*, not what
the sample happens to be filled with. `truth-cohort-attrition` cycles a year callout from 2009
to 2026 with artists falling away, and I read that as "time-based attrition, therefore not
set intersection." Wrong. The mechanic is: full cohort present, progressive elimination, named
survivors remain. That is exactly ninety-three artists, floor one, floor two, Drake and
Travis. The year axis is filler and everything is swappable.

This is the third time I have made this error. The height ruler's three subjects, the portrait
slots, now the year callout. Read the mechanic, never the sample.

**Aesthetic quality is invisible in the records and I cannot judge it.** Two rejections were
"ugly designs, they'll be removed." Nothing in a description, capacity or encoding field
carries this. It is a library hygiene pass, not a selection rule, and it is yours.

**A portrait slot never disqualifies a job whose categories are not picturable.** Fill the
slots with different images of the shared subject. The portrait carries subject identity, the
label carries the category. Six release types become six portraits of one artist, each
labelled. This reverses my rejection of `33_contract_portrait_grid`, which I killed on the
reasoning that a mixtape has no face. Wrong: the face is the artist's.

**Default to magnitude, not to tables.** A layout that shows size beats one that prints
values, unless the beat is genuinely a lookup.

## Still to source or build

**1. `inversion`** (renamed from `paired_values_by_group` on your instruction)
Assigned: **Infographic Bar Charts**, from Downloads. I cannot read that folder — macOS
returns "Operation not permitted" — and no pack by that name is on the drive. Two bar-chart
packs sit in `AE Templates/01 Data & Infographics` (`3d-bar-charts` and `3d-charts-v-2`) but
neither matches the name. Move it somewhere readable or confirm one of those two.

Two groups separated by which of a member's two values is larger, where the point is that the
relationship flips. Near-misses: `55_best_vs_value` and `kendrick-red-stage-clean`, but the
second is reference-only pending calibration, and neither shows the flip.

**2. `category_breakdown` — SOLVED, no build needed**
`36_four_portrait_cards` and `56_seven_artist_stat_lineup`, both within tolerance of six and
both usable once portraits are read as subject identity rather than category identity.
36 is the cleaner fit: equal image treatment, one value each, and its own avoid-list rules out
dense ranking and metric-driven scaling, which are exactly this job's prohibitions.
56 carries explicit rank fields, so check visually that it does not read as a ranking; its
avoid-list only forbids *automatically calculated* ranks, so the fields can go unused.

**3. `explain_the_encoding`**
A chart that teaches its own reading. Axis meaning, then one dot, then the full field. Once
per video, nothing in the library does it.

**Resolved.** `intersection_of_sets` uses `truth-cohort-attrition`. Nothing to build.

## Resolved: the three rejections

Not one rule. Two unrelated reasons, which is why I could not infer it.

- **27 and 29**: poor designs, being removed from the library. A quality judgment with no
  field behind it.
- **47**: arity and comparison type. Thirty-five entries against four peers, and it scores
  similarity rather than each entity's own magnitude.

Only the second is a selection rule. The first is library hygiene.
