# Review-rule principles harness plan

Status: completed and validated on 2026-10-04. This update makes the completed editor-review findings and
their reusable reasoning mandatory harness inputs. It must not encode Future,
its beat IDs, or any reviewed candidate as a runtime exception.

## Required stages and acceptance checks

1. **Declare the principles separately from examples.** Add a machine-readable
   review-reconciliation section to the general matching contract.
   - Check: the contract distinguishes scoped editor evidence, reusable
     reconciliation, admission rules, and selection/render authority.
2. **Enforce concrete reusable rules.** Require one primary presentation
   operation for admission; prevent secondary-operation union admission;
   reject incidental-number data inference; gate scoped families by operation;
   preserve honest non-template/B-roll routes; and constrain identity routes by
   semantic and media demand rather than slot count alone.
   - Check: mutating any required rule makes the contract gate and harness fail.
3. **Bind the policy into harness stages and receipts.** Require the policy at
   general-contract, feasibility, and human-review stages and expose a
   hash-bound review-rule receipt in the harness audit.
   - Check: the audit reports every enforced principle and keeps selection and
     rendering false.
4. **Regenerate and regress.** Rebuild affected review-only receipts, run
   focused matcher tests, contract/harness tests, and cross-story regressions.
   - Check: runtime contains no fixture identifiers; all relevant suites pass;
     any unrelated external pin failure is reported without weakening a gate.
5. **Publish only from the active branch.** Mark the task complete, rebuild the
   harness audit, commit and push to `matching-layer`.
   - Check: clean worktree and remote commit; current blocker is reported.

## Underlying principles

- Examples teach the system only through explicit story-neutral reconciliation.
- A narration detail is not automatically the visual job.
- Candidate admission follows what must be communicated, not every concept or
  number mentioned in the sentence.
- Existing template scope and capability evidence are authoritative; names and
  repeated historical popularity are not.
- A good non-template route is better than a forced weak template.
- Human comments are evidence, never implicit approval or render authority.
