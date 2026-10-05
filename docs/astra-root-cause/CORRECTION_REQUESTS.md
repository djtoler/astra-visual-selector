# Audit correction requests

This is the single canonical correction file for the `fable_analysis` audit.
Do not create separate correction-request files. Append each new request here,
preserve resolved history, and return this file's direct GitHub link whenever a
correction is added or updated.

An `ACTIVE` correction blocks the next numbered job. Claude Desktop must correct
only the named job, validate and publish the corrected artifacts, update that
entry to `RESOLVED` with the correction commit, return direct links, and stop.

## Job 6 — candidate pipeline

Status: **ACTIVE**

Opened after commit: `a898f8f6237402f4de80df25939e34556b92b515`

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
