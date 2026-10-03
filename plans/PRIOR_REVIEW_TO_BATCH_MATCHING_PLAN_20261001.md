# Consume prior editor selections in full-task matching

## Problem

The harness validates and attaches `reports/prior-editor-review-reconciliation.json`, but the
full VisualTask matcher reads only generic job bindings. A candidate the editor already selected
for an exact unsplit task can therefore disappear from that task's feasibility set.

## Stages and acceptance checks

1. Add the existing prior-review reconciliation artifact as an optional, hash-bound batch input.
2. Admit only rows whose state is `prior_selected` for that exact task. Never admit dismissed,
   none-acceptable, not-shown or split-task rows.
3. Route those rows through the existing `templateAdmissions` retrieval path and the unchanged
   technical/timing/treatment fit assessment. Prior selection preserves candidate discovery; it
   does not prove current compatibility, authorize selection or authorize rendering.
4. Prove with a failing-then-passing test that the prior-selected `02-02b` looped-slideshow family
   returns to the task while its dismissed carousel candidates do not receive prior-review
   admission provenance.
5. Rebuild and replay-validate the batch and harness, then report any measured shortage change.

No model API, new template, custom visual, render or fabricated editor decision is permitted.
