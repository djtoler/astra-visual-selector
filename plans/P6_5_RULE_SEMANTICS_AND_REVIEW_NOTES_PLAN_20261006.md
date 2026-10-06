# P6.5 rule-semantics audit and diagnostic review notes

## Scope

Pause P7 acceptance. Audit the existing general matching rules before another
held-out run, and extend the established review UI/storage contract with one
task-level diagnostic note per template-selection page. Do not select a
template, validate native fit, render, or add story-specific candidate rules.

## Required stages and acceptance checks

1. **Inventory authoritative rules and consumers**
   - Map each policy/grammar rule to the code paths that admit, rank, suppress,
     flag, or preserve candidates.
   - Acceptance: every exclusionary runtime rule has a named owner, scope,
     authority, implementation site, and existing test reference.
2. **Audit semantics and scope**
   - Check modal collapse (`may/prefer` becoming `must/never`), task-to-global
     scope leakage, mixed-payload loss, unknown-to-rejection promotion, and
     ordering rules accidentally changing admission.
   - Acceptance: each rule has positive, negative, mixed, and unknown
     counterexamples or an explicit documented gap.
3. **Mutation and cross-story proof**
   - Exercise exclusionary boundaries by removing, reversing, broadening, and
     weakening their inputs across the two golden packages plus synthetic
     counterexamples. P7's Drake package is regression material after feedback.
   - Acceptance: unsafe mutations fail; valid alternatives remain discoverable;
     uncertainty remains unresolved rather than incompatible.
4. **Task-level diagnostic notes in the existing review UI**
   - Reuse `/api/future-match-gallery` and the existing revision-checked review
     file. Add one saved text note for the whole task/page, separate from the
     existing candidate status/comment fields.
   - Acceptance: notes survive reload, reject stale revisions, remain
     human-authored review evidence, and never authorize selection or rendering.
5. **Regression and restart decision**
   - Run focused UI/storage tests and the complete matching test suite.
   - Acceptance: publish an audit report and do not restart P7 until confirmed
     high-risk defects are fixed and the audit has no unresolved exclusionary
     ambiguity capable of silently suppressing candidates.

## No-deviation assessment

This work uses the existing matching contracts, test harness, review UI, API,
and storage artifact. It does not introduce another selector or review system.
