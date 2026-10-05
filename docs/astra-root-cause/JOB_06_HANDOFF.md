# Job 6 handoff — the round-2 correction is not published, and why

Written mid-correction, at the editor's request, to get the state into the repo
before work resumes. **Nothing incorrect has been pushed.** The published Job 6
artifacts in `reports/astra-root-cause/` are still the **round-1** versions,
unchanged by this session.

## Status

| Item | State |
| --- | --- |
| `06-candidate-pipeline.{md,json}` | **round 1**, as committed in `a25fbc7` — untouched |
| `CORRECTION_REQUESTS.md` Job 6 round 2 | still **ACTIVE** |
| Round-2 correction work | **done, then withdrawn before publication** |
| Replacement analysis | **derived and verified**, not yet written into the artifacts |
| Evidence for the replacement | `docs/astra-root-cause/job06-exploration-replay.json` (this commit) |
| Jobs 7 and 8 | awaiting an explicit editor execution selection (see below) |

## What happened

The round-2 correction was completed, validated against the request's eight
checks, and committed locally. While reconciling a numeric contradiction between
the two rounds — round 1 said **twelve** admitted families were at zero exposure
on the pie-chart task, round 2 said **14** — I went to recompute the figure and
found that **neither number is reproducible**.

The exposure figures underpinning *every* ordering conclusion in both rounds —
`exposure 24 slates`, `27th of 41 by ascending exposure`, `twelve admitted
families at zero`, `displayed exposures span 3 to 136` — do not come out of any
committed artifact, or any combination of them. I tested all 63 non-empty
combinations of the six `*candidate-gallery*.json` files; none reproduces the
published exposures. The numbers were hardcoded into the round-1 patch script
with no surviving derivation.

I reset the two local commits rather than push artifacts I knew to be wrong.

## What "exposure" actually is

`pipeline/focused_candidate_diversity.py:93-101`:

```python
exploration_pool.sort(key=lambda row: (
    exploration_frequency.get(matching.C._family(row["candidateId"]), 0),
    admitted_families.index(matching.C._family(row["candidateId"])),
))
exploration = exploration_pool[:8]
for row in exploration:
    family = matching.C._family(row["candidateId"])
    exploration_frequency[family] = exploration_frequency.get(family, 0) + 1
```

Three corrections follow, and all three invalidate published text:

1. **Exposure is `exploration_frequency`** — a counter that starts empty at the
   top of the run and increments **only** when a family is actually placed in an
   exploration slot. It is *not* "the number of final gallery slates the family
   appears in", which is the proxy both rounds reconstructed and the proxy the
   round-2 artifact would have described as a stated caveat.
2. **The review slate is `focusedReviewFamilies`** — 8 primary plus 8
   exploration — **not `displayedFamilies`**, the 16-family gallery cut. Both
   rounds measured the wrong set.
3. **The ordering basis IS reconstructable.** Both rounds claimed the ordering
   half could not be replayed. The exploration half replays **exactly** from the
   committed artifacts by iterating the diversity artifact's tasks in order and
   counting exploration placements. The primary eight are recorded too, as the
   gallery's first eight displayed candidates; what remains unreplayable is only
   *why* `C.diversify` ranked them so, which needs `_encfit`/`_capfit`/`_rel`.

## The replacement finding, derived and verified

Replayed exactly as the code does it. Full per-task output in
`job06-exploration-replay.json`.

**The exploration half's only discriminator among families tied on frequency is
`admitted_families.index(...)` — the family's position in the admitted list.**
That is an arbitrary positional signal, not an exposure signal. And the tie is
not an edge case; it is the normal case:

| | future-volksgeist | jayz-drake | combined |
| --- | --- | --- | --- |
| Focused tasks | 26 | 33 | 59 |
| **Exploration cutoff falls inside a frequency tie** | **26** | **32** | **58 of 59** |
| Median families tied at the cutoff | — | — | **22** (max 71) |
| Median excluded despite tying | — | — | **14** (max 63) |
| **Total family-exclusions decided by admission order** | — | — | **1,204** |

So on 58 of 59 focused tasks, which eight families get explored is settled by
where they happen to sit in the admitted list.

### The four traced cases, re-run on the real basis

| Case | Requested family | `exploration_frequency` before the task | Pool rank | Exploration picks' frequencies | Reading |
| --- | --- | --- | --- | --- | --- |
| `jd…p04-4-03` *(pie chart)* | `3d-pie-chart-set` | **1** | 17 of 33 | all **0** (nine families at 0) | **legitimately skipped** — the exploration half did exactly what it says |
| `fv…p07-1-06` | `14_quote_score_columns` | **2** | 9 of 27 | `[1,2,2,2,2,2,2,2]` | **tied at 2 with seven that were taken; excluded on position** |
| `jd…p02-3-02` | `25_career_value_list`, `27_rank_context_panel`, `38_matchup_win_list` | **0, 0, 0** | 11, 12, 21 of 61 | all **0** | **all three tied at 0; excluded on position** |
| `fv…p06-6-06` | `02-documentary-promo` / `intro-slideshow-full-720p` | **2 / 2** | 27, 32 of 42 | all **1** | legitimately skipped on frequency |
| | `18_cutout_intro` | **1** | 11 of 42 | all **1** | **tied at 1; excluded on position** |

## What this withdraws

Beyond the three round-2 items, all of which were correct:

- **The pie chart is exonerated, for the third time and finally.** Round 1 typed
  it `display_loss`, then `ordering_loss`. Round 2 would have typed it
  `ordering_basis_unresolved` on a bogus proxy. On the real basis the
  exploration half **behaved correctly**: frequency 1 against nine families at 0.
- **The round-2 headline is withdrawn before publication.** "44 of 59 focused
  tasks display zero of the eight least-exposed admitted families" and
  "15 of 16 displayed families sit at the most-exposed end" were both computed
  against `displayedFamilies` using the wrong exposure measure.
- **"The ordering basis is unreconstructable" is withdrawn.** It reconstructs.
- **The exposure-proxy caveat is not a fix.** Round 2 would have published the
  bad numbers with a caveat saying exposure was a proxy. A stated caveat on a
  figure that reproduces from nothing is not a disclosure; the figure should
  have been recomputed or dropped.

## What still stands, unaffected

- `sibling_propagation_loss`: `_siblings` is computed at
  `match-trial/candidates.py:800` and dropped by `template_candidates()`,
  reaching no artifact. Proven, and scoped to a **general review-surface
  defect** — not the earliest divergence for any named task.
- **Round-2 required validation 5 stays `UNRESOLVED`.** The *within-family*
  keys `_encfit`/`_capfit`/`_rel` are genuinely recorded in no artifact. That is
  separate from the family-ordering replay, which does work. All 10
  editor-named wrong-variant cases remain enumerated with unresolved causes.
- The competing hypothesis on `p03-2-01` remains open: that task record carries
  no slot or capacity demand at all.
- Round-1 items 3 and 4 — lineage counts separated, b-roll routing withdrawn.

## Remaining work on Job 6

1. Rewrite `06-candidate-pipeline.json` and `.md` on the replayed basis: the
   positional-tiebreak finding as the systemic ordering result, the four cases
   re-typed, the exposure proxy and the "unreconstructable" claim withdrawn.
2. Re-run the request's eight validations.
3. Mark the round-2 entry `RESOLVED` in `CORRECTION_REQUESTS.md`.
4. Note in the artifact that the published round-1 figures were unreproducible
   and that a correction introduced its own unverified numbers.

Estimated 20–30 minutes. No further measurement is needed; the derivation above
is complete and its evidence is committed.

## Jobs 7 and 8 — blocked on an editor decision, not on funding

Commit `f307482` removed the mandated executor. Both jobs now carry
`selectionAuthority: "editor"`, `executionSelectionRequiredBeforeJob: true` and
`defaultExecution: null`, with two allowed executions each:

| `allowedExecutions` id | Mode | Model | Effort |
| --- | --- | --- | --- |
| `claude_desktop_direct` | `desktop_conversation` | resolved and recorded at run time | — |
| `claude_desktop_fable_cli_medium` | `claude_cli_invoked_from_desktop` | `claude-fable-5-1` | `medium` |

The same commit added the prohibition
`job_7_or_8_execution_without_explicit_editor_selection`, so **Job 7 cannot
start until you name one of those two ids.**

`claude_desktop_direct` is now a listed option, so running them as direct
Desktop jobs — as Jobs 1 and 3–6 were — needs no model substitution or
departure from policy.

**Cost record, kept because it is why the policy changed.** Usage credits are at
zero and the Job 2 Fable run is the reason. From that run's own transcript, at
the published rates: output 348,373 tokens at $50/MTok = **$17.42**; cache read
10,092,691 at $0.25/MTok = $2.52; input 2,028 at $10/MTok = $0.02; cache write
2,519,121 at a rate not published in the reference used. The floor on the first
three is **$19.96**, which alone exceeded the $12 added. The prompt made the run
expensive by design — 1.19 MB of evidence, ~780 KB of StoryPackages, schema and
builder read in full — and the cost was never estimated beforehand. That was a
pre-flight gap, not a surprise about the model. Any invocation from here will be
priced and the estimate stated before launch.

## Correction record across the audit

| Round | Job | What was wrong |
| --- | --- | --- |
| 1 | Job 3 | Gap owners used an out-of-vocabulary value; `G-05` proposed a name contradicting its own rationale; five deltas rested on single-story evidence |
| 2 | Job 4 | Four traces labelled failure with no supported divergence; the `concept_statement` fallback called a defect when the gold reference agrees 96–100%; the mixed-payload route said to work when its flag has zero read-sites; `taskId` used as a unique key when it is not |
| 3 | Job 6 | Ordering loss declared zero; the variant mechanism called arbitrary when an eight-key ranker exists; lineage task counts conflated with finding counts; b-roll routing concluded with no observed route |
| 4 | Job 6 again | A stale object still typed the pie chart `display_loss`; three of four ordering classifications asserted without a per-case trace; `display_loss` defined so it could never occur; the wrong-variant validation passed without its required keys |
| 5 | Job 6, self-caught | **The exposure measure itself was wrong and its figures reproduce from nothing.** Found while reconciling a twelve-versus-14 discrepancy between my own two rounds |

Themes worth watching in Jobs 7 and 8: **mixing measurements from one package
with conclusions about another**; **treating the existence of a mechanism as
evidence that it runs**; **asserting a classification from one trace and
generalising it without tracing the rest**; and now **carrying a figure forward
across rounds without re-deriving it, then disclosing it as a proxy instead of
recomputing it**. Round 5 is the one that matters most: a contradiction between
two of my own numbers was the only thing that surfaced it, and it had already
survived one full correction cycle and eight passing validations.
