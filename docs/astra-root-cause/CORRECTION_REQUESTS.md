# Audit correction requests

This is the single canonical correction file for the `fable_analysis` audit.
Do not create separate correction-request files. Append each new request here,
preserve resolved history, and return this file's direct GitHub link whenever a
correction is added or updated.

An `ACTIVE` correction blocks the next numbered job. Claude Desktop must correct
only the named job, validate and publish the corrected artifacts, update that
entry to `RESOLVED` with the correction commit, return direct links, and stop.

## Job 4 — matching transformations

Status: **ACTIVE**  
Opened after commit: `032981c5ac12aa705d3fe11366f9acb7f8f93a73`  
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
