# Narration-to-contract derivation study

Paper study, no code and no model calls. Agreed as the next step in handoff messages 018
through 020. The question: can the fields that `facts-v2/contracts.py` hand-authors per
segment be derived generically instead?

Four segments. Two were assigned because they carry saved user reviews. Two were chosen
because they have no entry in `SPECS`, no extracted facts anywhere in the pilot, and no
saved review, so nothing about their answer exists to leak into the derivation.

| segment | status | why it is here |
|---|---|---|
| 13.01 | reviewed, authored | assigned; tests collection abundance |
| 13.02 | reviewed, authored | assigned; tests unlike units and unknown overlap |
| 17 | **unfamiliar** | a rule, not a quantity; tests a different kind of case |
| 27 | **unfamiliar** | surface-identical to segment 28; tests false-match resistance |

Provenance codes on every field below: **extraction** (present in the pilot's extracted
facts), **context** (elsewhere in the narration), **user-review** (only knowable from a saved
comment), **inference** (my judgment), **unknown** (not determinable).

I did not consult my own prior contracts for 17 or 27. They exist in this repo from an
earlier 30-passage run and reading them would have leaked answers into a study whose whole
point is whether the answer can be reconstructed.

---

## 13.01 — "He has thirty songs past a billion streams."

| field | value | provenance |
|---|---|---|
| sides | owner: one artist / counted items: songs / benchmark: 1B streams per song | extraction |
| subject identity | Drake, via segments 10 and 12 | context, already linked in `evidence` |
| measure | count of qualifying members | extraction |
| unit | songs | extraction |
| relation | entity-to-benchmark, applied distributively across a collection | extraction |
| item count | 30 | extraction |
| mandatory meaning | benchmark is per song, not per catalog; thirty counts songs, not streams; single subject | extraction, verbatim from `requiredMeaning` |
| **viewer objective** | thirty must read as *many*, not as a number | **context + inference** |
| scale requirement | none; but numerosity must be perceptible | inference |

Everything except the objective comes straight out of extraction. The authored `SPECS` entry
adds nothing that was not already there.

**Where the objective actually comes from.** Read alone, the sentence is a count. The
abundance reading comes from the next sentence in the same passage, where thirty-five of the
field have zero. The contrast is what makes thirty large. So the objective is recoverable, but
only at passage scope. Extraction that scopes a job to its own sentence cannot see it, and
that is a concrete, mechanical reason the v2 contract missed collection magnitude. It was not
a judgment failure.

**On scale.** Abundance needs perceptible *numerosity*, not a proportional axis. A scroll, a
field of thirty marks or a grid all satisfy it; a bar with a value label does not, and a
truthful proportional scale is not required. The current schema conflates these under one
`scaleRequirement`, and they are different demands.

---

## 13.02 — "Thirty-five of the ninety-three have zero. And eighty-one of the ninety-three don't have thirty billion."

| field | value | provenance |
|---|---|---|
| cohort | 93 rappers, opening chart, fixed denominator | extraction |
| subgroup A | 35 failing benchmark A | extraction |
| benchmark A | zero songs above 1B streams; unit is a per-artist count | extraction |
| subgroup B | 81 failing benchmark B | extraction |
| benchmark B | under 30B lifetime catalog streams; unit is streams | extraction |
| **units differ between A and B** | yes, explicitly | **extraction** |
| **overlap of A and B** | not stated | **unknown, and must stay unknown** |
| relation | two independent many-against-a-common-cohort counts, different measures | extraction |
| mandatory meaning | denominator is 93; "zero" means zero billion-stream songs; the 81 uses a different lifetime measure; both count rappers, not streams | extraction, verbatim |
| **viewer objective** | the shortfall must be *seen* as proportion, not read as two numbers | **see below** |

The unlike-units constraint Codex asked to preserve is already in the extracted
`requiredMeaning`, word for word. No authoring was needed for it. The overlap between the two
subgroups is absent from the narration, so any visual implying an intersection or a shared
axis would be inventing a fact.

**The objective is the honest problem here.** The user's saved comment is that tables are weak
"because the point is scale/gap." I can reach the same place by a general rule: *a count stated
as X of Y against a named fixed cohort has proportion as its point, and proportion is a
perceptual quantity*. That rule is not segment-specific and would apply anywhere.

But I derived it already knowing the answer, so this is not evidence that it works. It is a
hypothesis that happens to fit one case. The only real test is a segment whose ruling I have
never seen, which is why 17 and 27 are below.

---

## 17 — "One rule, applied to everybody. A record you lead, or share the lead on equally, counts in full. A feature or a remix verse counts at half."

No `SPECS` entry, no extracted facts, no saved review. Derived from narration alone.

| field | value | provenance |
|---|---|---|
| sides | category 1: lead or equal co-lead / category 2: feature or remix verse | inference from narration |
| measure | credit weight | inference |
| unit | fraction of one record | inference |
| values | 1.0 and 0.5 | inference, from "in full" and "at half" |
| relation | category-to-value mapping; **no entities and no comparison** | inference |
| item count | 2 categories | inference |
| mandatory meaning | the rule is universal; the second case is worth half the first | inference |
| **viewer objective** | the halving must be apparent | inference |
| scale requirement | proportional, because "half" is itself a proportional claim | inference |
| example artists | **unknown; none given** | unknown |

**Result: the objective is derivable, and I expected it not to be.** The word "half" is a
proportional claim, so a treatment that shows full against half truthfully satisfies the
narration and one that merely labels them is weaker. No user ruling was needed.

**Where this segment does fail closed, correctly.** The narration names no artist and gives no
example. Any illustrative instance would be invented content. The right outcome is to record
the example slot as unknown and require review, not to fill it. This is the fail-closed case
Codex described, and it sits in a different field than I predicted: the objective is clear
while the *content* is not.

Worth noting this segment has no entities at all. The entire v2 vocabulary is built around
typed sides with measures and counts. A rule statement fits none of it, and it is one of
thirty segments, so this category is not exotic.

---

## 27 — two archetypes, six artists, paired values

> The ones who carry their own records — Post Malone, forty-nine billion on his own songs
> against six as a guest. XXXTentacion, thirty-five and six. Kendrick, forty-one and sixteen.
> And the ones who live on other people's hooks. Ty Dolla $ign, five billion on his own
> records and twenty-two as a guest. Young Thug, eleven and twenty-one. 21 Savage, sixteen and
> twenty-three.

No `SPECS` entry, no extracted facts, no saved review.

| field | value | provenance |
|---|---|---|
| group A | "carry their own records": 3 artists | inference |
| group B | "live on other people's hooks": 3 artists | inference |
| per member | a pair, own streams and guest streams | inference |
| measure | streams | inference |
| unit | billions, **same unit on both sides** | inference |
| item count | 6 artists, 12 values | inference |
| relation | two groups distinguished by **the direction of a within-member inequality** | inference |
| **viewer objective** | the inequality must be seen to *flip* between the groups | inference |
| scale requirement | within-member proportion matters; absolute magnitudes do not | inference |
| ratio | **not stated; must not be computed** | unknown |

**This is the near-miss and it fails.** Surface shape is two groups, two values per member,
which is exactly segment 28's `two_threshold_groups`. It is not. There is no benchmark and no
threshold anywhere in this narration. The groups are defined by which of a member's two values
is larger.

The existing descriptor predicate maps two pairs with two values each onto
`two_threshold_groups`. That is the inference Codex already identified as wrong for 13.02, and
segment 27 shows it is not a one-off: the same predicate would misfire here, on a segment
nobody has reviewed, and pull in the pairwise-outcome layouts the user called horrible.

**The vocabulary has no term for this relation.** Neither `two_threshold_groups` nor
`paired_counts` nor `group-to-group` expresses "two groups separated by the sign of a
within-member comparison." This gap was invisible across all twelve authored jobs and appeared
immediately on the first unfamiliar segment, which is the argument for doing this study before
building anything.

---

## What the study shows

1. **Most of `SPECS` is redundant.** For 13.01 and 13.02, every field except the viewer
   objective is already in the extracted facts, including the unlike-units constraint. The
   hand-authoring was not supplying missing information, it was restating it.
2. **The objective needs passage scope, not sentence scope.** 13.01's abundance is only
   visible from the following sentence. This is mechanical and fixable.
3. **The objective is more derivable than I expected.** It fell out of the narration on 17 and
   27 without any ruling. On 13.02 a general proportion rule reproduces the user's ruling,
   though I cannot claim that as evidence since I knew the answer.
4. **Fail-closed lands on content, not objective.** Segment 17 has a clear objective and an
   unfillable example slot. Those are separate fields and the schema should let one be known
   while the other is not.
5. **Two gaps the authored twelve could not reveal.** A rule statement has no typed sides at
   all, and two groups can be separated by the direction of a within-member inequality with no
   threshold in sight. Both surfaced on the first two unfamiliar segments tried.
6. **The false pairwise predicate is general, not local.** It misfires on 27 as well as 13.02.

## What this does not show

The derivations for 17 and 27 are mine and unreviewed. They are hypotheses about what those
segments need, and the user has never ruled on either. Nothing here is validated until
someone who is not me checks them. The proportion rule in particular is fitted to a known
answer and should be treated as untested.
