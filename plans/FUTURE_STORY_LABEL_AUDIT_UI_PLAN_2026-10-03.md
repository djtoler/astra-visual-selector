# Future Story Label Audit UI Plan — 2026-10-03

## Objective

Extend the established Future matching review page with a read-only Story labels tab that distinguishes source-provenanced story-layer job proposals from narrator claims for which the story layer supplied no visual job.

This is an audit surface only. It does not change the StoryPackage, infer missing jobs, alter template bindings, validate candidate fit, authorize selection, or authorize rendering.

## Required stages and acceptance checks

1. **Load the already-bound source artifacts**
   - Reuse the adapter and task-proposal files already hash-bound to the candidate gallery.
   - Acceptance: the server continues to reject missing or stale source files.

2. **Expose an explicit story-layer audit**
   - Return all supplied job proposals, their exact claim IDs, claim text, and beat IDs.
   - Return the complete `p01-1` beat with all five claims and label each claim as supplied `pose_a_question` or `no visual job supplied`.
   - Acceptance: counts reconcile to 20 supplied job proposals, all 20 `pose_a_question`, and 328 uncovered narrator claims.

3. **Show the evidence in the existing review UI**
   - Add a read-only Story labels tab; retain the existing template, source-clip, and unresolved tabs.
   - Acceptance: the page visibly states that only 20 claims were labeled and 328 were not, and shows that only `p01-1.1` received `pose_a_question` within `p01-1`.

4. **Regression verification**
   - Run the existing label-server storage tests and a focused audit assertion.
   - Acceptance: existing review persistence remains passing and the audit data reconciles exactly.
