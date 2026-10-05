# Audit correction requests

This is the single canonical correction file for the `fable_analysis` audit.
Do not create separate correction-request files. Append each new request here,
preserve resolved history, and return this file's direct GitHub link whenever a
correction is added or updated.

An `ACTIVE` correction blocks the next numbered job. Claude Desktop must correct
only the named job, validate and publish the corrected artifacts, update that
entry to `RESOLVED` with the correction commit, return direct links, and stop.

## Job 6 — candidate pipeline, correction round 2

Status: **ACTIVE**

Opened after correction commit: `a25fbc7f0e2d4b266852127dc17f35dd65135246`

Target artifacts:

- `reports/astra-root-cause/06-candidate-pipeline.md`
- `reports/astra-root-cause/06-candidate-pipeline.json`

Correct Job 6 only. Do not start Job 7 and do not modify production code,
catalog records, grammar, evidence, gold references or earlier job outputs.

The first correction fixed the broad diagnosis, lineage coverage and route
scope, but it does not yet satisfy its own required validation.

### 1. Remove the stale contradictory display-loss result

The corrected JSON reports `failureClassificationCounts.display_loss` as absent
or zero and reclassifies the pie-chart case as `ordering_loss`. However,
`provenDisplayLoss` still types the same pie-chart case as `display_loss` and
calls it the cleanest end-to-end display-loss proof. This directly contradicts
the corrected Markdown, `orderingVersusDisplay`, `whatIsNotTheProblem` and the
failure counts.

Remove or replace the stale object and audit the entire JSON for superseded
pre-correction conclusions. Markdown and JSON must agree everywhere, not only
in newly appended correction fields.

### 2. Trace every ordering-loss case or mark it unresolved

Four findings are classified as `ordering_loss`, but only the pie-chart case
has the requested pre-cut position and ordering-signal trace. The other three
findings merely say that the requested families were outside the surviving
slots and then assert the ordering classification.

For each of all four findings—and each requested family grouped inside it—show:

- its position in the complete ordered family list;
- whether it failed the primary half, exploration half, or both;
- the task-specific ordering keys/signals that determined that position; and
- why the ordering itself was wrong, rather than merely observing that a later
  display limit omitted the lower-ranked row.

If the committed evidence cannot reconstruct those facts, classify that case
as unresolved. Do not generalize the pie-chart trace to the other cases.

Also replace the current circular definition of `display_loss`—"inside a
surviving slot and the cap removed it anyway"—because a row inside a surviving
slot is not removed by that cap. Define ordering and display divergence so both
are logically possible and non-overlapping, then re-evaluate the evidence
rather than defining `display_loss` out of existence.

### 3. Do not pass the wrong-variant validation without its required evidence

The correction request required every editor-named wrong-variant case to include
the displayed and requested variants' actual `_within_family` ordering keys and
a sibling-propagation trace. The corrected report analyzes one case and states
that `_encfit`, `_capfit` and `_rel` cannot be replayed from committed evidence.
It therefore cannot determine whether the earliest task-specific divergence was
missing task requirements, capability metadata, variant ranking or only sibling
propagation.

The dropped `_siblings` field is a proven general review-surface defect. It is
not, by itself, proof that sibling propagation was the earliest divergence for
the named task: the six-slot variant may already have outranked the two/three-slot
variants because the required slot demand was missing or misrepresented.

List every editor-named wrong-variant case found in the evidence. For each case,
either provide all actual ordering keys requested in round 1 and identify the
earliest supported divergence, or mark the task-specific cause unresolved. Keep
the general `_siblings` defect as a separate proven finding. If the keys remain
unavailable, mark that required validation `BLOCKED` or `UNRESOLVED`; do not
declare the complete corrected job `PASS` solely from the general defect.

### Required validation

1. Parse the corrected JSON successfully.
2. Assert no object still calls the pie-chart case `display_loss` while another
   calls it `ordering_loss`.
3. Assert every `ordering_loss` finding has its own ordered position, ordering
   signals and earliest-divergence basis; otherwise type it unresolved.
4. Assert the definitions of `ordering_loss` and `display_loss` are both
   logically reachable and non-overlapping.
5. Assert every editor-named wrong-variant case has actual per-variant ordering
   keys and a propagation trace, or an explicit unresolved result.
6. Keep the corrected lineage and B-roll-route scope from round 1 unchanged
   unless new evidence requires a cited correction.
7. Make Markdown and JSON agree on result status, measurements,
   classifications, unresolved evidence and acceptance verdicts.
8. Confirm the correction diff modifies only the two Job 6 artifacts and this
   canonical correction file.

Commit and push the corrected Job 6 artifacts to `fable_analysis`. Update this
entry to `RESOLVED` with the correction commit and links, then provide direct
GitHub links to the corrected Markdown, JSON, this correction file and the
commit. State the next job and blocker owner, and stop before Job 7.

---

## Job 6 — candidate pipeline

Status: **RESOLVED**

Opened after commit: `a898f8f6237402f4de80df25939e34556b92b515`
Resolved by commit: `a25fbc7f0e2d4b266852127dc17f35dd65135246`

The correction:

- separated ordering from the display cap and reclassified every loss: the
  pie-chart case failed BOTH halves of the
  `eight_primary_plus_eight_least_exposed` strategy (exposure 24 slates, 27th of
  41 by ascending exposure, against twelve admitted families at zero), so its
  first divergence is ordering, not the cap; all four previously-typed
  `display_loss` findings became `ordering_loss` and `display_loss` is now 0 as
  a first divergence;
- rewrote the variant mechanism after opening `match-trial/candidates.py`, a
  module the published job never read: `_within_family` ranks on eight keys and
  only the final id tiebreak is arbitrary, `FAM_MAX=1` is an intentional
  review-budget policy, and the proven defect is `sibling_propagation_loss` —
  `_siblings` is computed at line 800 and dropped by `template_candidates()`,
  reaching no artifact. The code comment at lines 795-799 already recorded 429
  hidden siblings across 40 beats and the editor saying "right family, wrong
  scene" twice. Proven on p03-2-01, where a 6-slot grid was shown and 3-slot and
  2-slot variants exist in the same 38-variant family;
- reported 21 incomplete lineage TASKS separately from 1 `lineage_incomplete`
  FINDING, attempted reconstruction and found it unavailable from committed
  artifacts, and excluded the 21 from conclusions requiring admission, hidden
  family or first-divergence evidence;
- withdrew the b-roll routing conclusion: `ordered-visual-route-plan.json`
  covers only the 41 Year Seventeen tasks and 0 of 59 reviewed tasks, so none of
  the 16 b-roll-request tasks has an observed route, and the published route
  counts of 64 and 18 were double-counted against an actual 32 and 9;
- additionally corrected the acceptance basis for historical editor choice:
  prior picks do not admit a candidate but are the FIRST sort key inside a
  family, on by default.

Resolved outputs:

- `reports/astra-root-cause/06-candidate-pipeline.md`
- `reports/astra-root-cause/06-candidate-pipeline.json`

Original request retained below for history.

Target artifacts:

- `reports/astra-root-cause/06-candidate-pipeline.md`
- `reports/astra-root-cause/06-candidate-pipeline.json`

Correct Job 6 only. Do not start Job 7 and do not modify production code,
catalog records, grammar, evidence, gold references or earlier job outputs.

### 1. Separate ordering loss from the display cap

The current report concludes that ordering caused no loss because display uses a
fixed count rather than a score cut. That is not sufficient: the fixed 16-family
cut is applied **after an explicit ordering strategy**, and that ordering decides
which admitted families survive.

Trace the ordering of each editor-requested family used as a loss example,
including the pie-chart case, through:

- the gallery's family order;
- the first eight primary candidates;
- the exploration ordering based on prior exposure and admitted-family order;
- the final 16-family cut.

For each lost family, identify its pre-cut position, the ordering signals that
put it there, and the first stage at which it became unavailable to the editor.
Classify `ordering_loss` and `display_loss` as distinct, non-overlapping first
divergences. Do not claim zero ordering loss merely because the order is an
explicit strategy rather than a scalar score.

### 2. Correct the variant-selection mechanism

The report calls the displayed family representative arbitrary and says there is
no mechanism to choose the right variant. The existing `C.diversify()` path does
rank variants inside a family using encoding fit, capacity fit, task/global
selection signals where enabled, relevance, motion availability and only then a
stable ID tiebreak. It also computes `_siblings`, but
`visualtask_matching.template_candidates()` omits `_siblings` from the returned
candidate row, so downstream review cannot inspect them.

For every editor-named wrong-variant case:

1. replay `_within_family` ordering with the exact task and candidate records;
2. record every ordering key for the displayed and requested variants;
3. identify whether the earliest failure is missing task requirements,
   inaccurate capability metadata, variant ranking, sibling propagation, or
   review-surface display;
4. verify whether `_siblings` survives each downstream artifact and reaches the
   UI data;
5. revise `variant_collapse` so it describes the proven mechanism rather than
   treating every one-variant-per-family slate as a failure.

One representative per family may be an intentional review-budget policy. The
failure is proven only where a materially better variant existed and the system
could not rank or expose it for the task.

### 3. Complete or strictly scope the candidate lineages

The required output calls for a complete lineage for every reviewed task used.
The report uses 59 reviewed tasks but states that 21 lack admitted/hidden family
sets. Only one finding is counted as `lineage_incomplete`, which obscures the
task-level coverage gap.

Use the existing read-only pipeline against the pinned inputs to reconstruct the
missing exhaustive lineages where reproducible. Label reconstructed lineage
separately from committed historical lineage and verify its input digests. If an
exact lineage cannot be reproduced, mark that task incomplete and exclude it
from conclusions requiring admission, hidden-family or first-divergence evidence.

Report both:

- the number of incomplete **tasks**; and
- the number of `lineage_incomplete` **findings**.

Do not use one count as if it represented the other.

### 4. Test B-roll/no-template routing per reviewed task

`brollFallbackAvailable: true` and the existence of 18 B-roll routes prove that
the route exists globally. They do not prove that the 16 reviewed tasks where
the editor requested B-roll or no template were actually routed correctly.

Join each of those reviewed tasks to its route decision and report:

- actual route;
- whether template candidates were still displayed;
- whether B-roll was merely available or actually selected as the route;
- the first divergence for every mismatch.

Only conclude `forced_template` is unsupported if all relevant reviewed tasks
were correctly routed, or explicitly scope the conclusion to the subset with
complete route evidence. A fallback flag cannot substitute for an observed
route outcome.

### Required validation

1. Parse the corrected JSON successfully.
2. Keep retrieval, admission, feasibility, routing, family ordering, variant
   ordering and display as separate lineage stages.
3. Assert every classified loss has one earliest divergent stage and does not
   double-count ordering and display.
4. Assert every wrong-variant claim includes the displayed and requested
   variants' actual within-family ordering keys and sibling propagation trace.
5. Report complete and incomplete lineage task counts separately from finding
   counts; exclude incomplete tasks from unsupported downstream conclusions.
6. Verify the actual route for every reviewed B-roll/no-template task used in a
   routing conclusion.
7. Make Markdown and JSON agree on measurements, scopes, classifications and
   acceptance verdicts.
8. Confirm the correction diff modifies only the two Job 6 artifacts and this
   canonical correction file.

Commit and push the corrected Job 6 artifacts to `fable_analysis`. Update this
entry to `RESOLVED` with the correction commit and links, then provide direct
GitHub links to the corrected Markdown, JSON, this correction file and the
commit. State the next job and blocker owner, and stop before Job 7.

---

## Job 4 — matching transformations

Status: **RESOLVED**  
Opened after commit: `032981c5ac12aa705d3fe11366f9acb7f8f93a73`  
Resolved by commit: `f2399468bdd9f255f9153a670c693a4929fb8227`

The correction:

- re-diagnosed every replayed unit against a named oracle, so no trace is
  labeled `failure` without a supported divergence and a named first divergent
  stage; the four disputed traces resolved as two reclassified `success` (the
  gold reference makes the same call) and two kept `failure` with a gold and a
  lexical oracle;
- withdrew the characterization of the `concept_statement` /
  `assert_without_data` fallback as a defect, after measuring that the gold
  reference assigns the same operation set in 103 of 107 cases and the same job
  in 107 of 107;
- traced `mixedPayloadReviewRequired` to 1 write-site and 0 read-sites, found no
  `split` route in the produced vocabulary and the split module unwired, and
  therefore withdrew the conclusion that route/split handling works and the
  endorsement of the single-primary rule, recording handling unresolved as
  UE-26;
- revised P4-2 to separate same-task evidence from linked-task evidence using
  the `scope`, `strength` and `mustBePerceptible` fields, and reported both
  required counterexamples: all 6 continuity groups classify as
  `link_separate_tasks` with task counts preserved, and of 42 multi-claim
  obligations only 4 carry same-task evidence, one of which is capped rather
  than joined;
- additionally withdrew the 26 continuity-split divergences and fixed
  non-unique trace identifiers, `taskId` not being unique across packages.

Resolved outputs:

- `reports/astra-root-cause/04-matching-transformations.md`
- `reports/astra-root-cause/04-matching-transformations.json`

Original request retained below for history.

Target artifacts:

- `reports/astra-root-cause/04-matching-transformations.md`
- `reports/astra-root-cause/04-matching-transformations.json`

Correct Job 4 only. Do not start Job 5 and do not modify production code,
schemas, grammar, evidence, gold references or earlier job outputs.

### 1. Four failed traces have no divergence

These traces are labeled `failure` while carrying an empty `divergences` list
and `firstDivergentStage: null`:

- `matching-derived-p02-3-06`
- `matching-derived-p01-1-04`
- `matching-derived-p01-1-05`
- `matching-derived-p01-4-02`

For each trace, either supply evidence for a real divergence and name its first
divergent stage, or reclassify it as `success` or `unresolved`. Update every
aggregate count, rate, finding and acceptance statement affected by the change.
Do not treat a keyword fallback as failure without a Story, gold-reference,
editor-evidence or downstream-behavior oracle.

In particular, `concept_statement` / `assert_without_data` may be generic or
low-specificity, but it is not automatically unusable. Reserve that conclusion
for cases where the audit proves harmful downstream behavior.

### 2. The primary-operation suppression test is incomplete

The report proves that secondary operations remain in the task artifact and
that `mixedPayloadReviewRequired` is emitted. It does not prove that any
downstream route/split consumer acts on that flag, surfaces an actionable choice
or prevents necessary candidate families from being suppressed.

Trace the flag through every downstream consumer available at this baseline and
report the observable outcome. If there is no effective consumer or the outcome
cannot be demonstrated, mark handling as unresolved and withdraw the conclusion
that the route “works” or that the single-primary rule is fully endorsed. A
stored list or review flag is not implementation of route/split handling.

Do not solve this by unioning every inferred operation. Evaluate whether a
coherent task split, corrected primary selection or another existing route can
preserve necessary meaning without candidate explosion.

### 3. P4-2 must not make groups automatically atomic

Obligations and continuity are boundary evidence, not proof that every listed
claim belongs in one VisualTask. A continuity group can intentionally link
several separate tasks, and one obligation can span several visual moments.

Revise P4-2 so it:

- consults obligation and continuity membership before grouping;
- distinguishes `same task` evidence from `linked tasks` evidence;
- preserves coherent visual-moment boundaries;
- records why a group is split or joined;
- does not force a 14-claim template-family continuity group into one oversized
  task.

Test the revised proposal against at least one multi-task continuity group and
one obligation that spans multiple moments. Report the counterexample results.

### Required validation

1. Parse the corrected JSON successfully.
2. Assert every failed trace has a non-empty supported divergence and a named
   `firstDivergentStage`; otherwise it is not labeled failure.
3. Recompute all corpus and trace counts from the corrected trace set.
4. Identify the actual downstream consumers of `mixedPayloadReviewRequired`
   and distinguish flag emission from effective route/split behavior.
5. Confirm P4-2 distinguishes atomic boundaries from cross-task continuity and
   passes the two required counterexamples.
6. Make Markdown and JSON agree on evidence, conclusions, proposals and the
   acceptance verdict.
7. Confirm the correction diff modifies only the two Job 4 artifacts and any
   necessary Job 4 receipt/status metadata.

Commit and push the corrected Job 4 artifacts to `fable_analysis`. Update this
entry to `RESOLVED` with the correction commit and links, then provide direct
GitHub links to the corrected Markdown, JSON, this correction file and the
commit. State the next job and blocker owner, and stop before Job 5.

---

## Job 3 — upstream contract fitness

Status: **RESOLVED**  
Opened after commit: `409f8295bdfd35d48604feecd9877df3143ac8cf`  
Resolved by commit: `c8d4191bcb8c5f8c6ca82db267c310dcf564e030`

The correction:

- replaced out-of-vocabulary `shared` gap owners with one accountable owner and
  explicit supporting owners;
- standardized G-05 on Story's canonical `value` name;
- demoted unsupported rounding and other single-story deltas to unresolved
  hypotheses;
- re-ran the acceptance checks and changed only the two Job 3 artifacts.

Resolved outputs:

- `reports/astra-root-cause/03-upstream-contract-fitness.md`
- `reports/astra-root-cause/03-upstream-contract-fitness.json`
