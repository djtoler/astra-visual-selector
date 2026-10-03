# Data assignments to batch matching plan — 2026-10-01

## Problem

The matching harness accepts the completed typed-data artifact, but the existing full VisualTask
batch matcher still reads `requiredTypedFields: null` from the older technical-requirements
artifact. Without a source-bound bridge, template feasibility incorrectly reports that all data
fields are missing even though data handoff is complete.

## Required stages and acceptance checks

1. Add the completed data-assignment artifact as an optional, hash-bound batch input.
2. Validate review-only authority, complete status, distinct task IDs, exact queued data-task
   coverage and selection/render denial.
3. Overlay each resolved task's typed fields onto its in-memory technical requirement; do not
   rewrite the authoritative requirements file or alter non-data tasks.
4. Run the established full VisualTask batch consumer and prove data-bearing tasks no longer emit
   the generic `task_required_data_fields` gap. Candidate-specific native encoding/readability/
   slot questions remain unresolved until exact treatment evidence exists.
5. Preserve deterministic replay, no selection and no rendering.

## Execution evidence

- The new test first failed because `dataAssignments` was not an allowed batch source.
- All 28 data-bearing task IDs now receive their resolved fields; non-data tasks are not falsely
  marked as missing data.
- Eleven full-batch tests pass. The actual 41-task batch artifact rebuilt and replay-validated.
- Current measured verdicts: template fit one conditional and 40 unresolved; media 22 available,
  17 not required, one conditional and one unavailable.
- The matching harness now binds this exact batch report and remains review-only.
