# P6.5 matching-rule repair summary

Status: **repairs complete; P7 acceptance still requires a new untouched package.**

## Root-cause repairs

- Generic discourse words no longer fabricate archival, event, or milestone jobs. Temporal routes now require an actual temporal anchor or event.
- A question no longer becomes a no-template route from semantics alone. Only exact-task, editor-reviewed evidence may suppress every template.
- A task explicitly marked as unresolved mixed payload now fails before primary-only candidate admission unless an exact-task editor review confirms a primary operation or records that splitting is complete.
- Quantitative questions retain their data-presentation requirement instead of being flattened into generic rhetorical-question matching.
- Every exclusionary matching rule is bound to named positive, negative, mixed, unknown, scope-mutation, and modal-reversal tests through `grammar/matching-rule-behavior-contract.json`.
- Timeline and identity/data boundaries now have paired admission and rejection coverage.

## Replay results

| Package | Claims | Tasks | Uncovered claims | Unresolved mixed payloads | Unauthenticated template vetoes |
|---|---:|---:|---:|---:|---:|
| Future calibration | 502 | 300 | 0 | 0 | 0 |
| Year Seventeen calibration | 150 | 115 | 0 | 0 | 0 |
| Drake regression | 162 | 96 | 0 | 0 | 0 |

Year Seventeen retains all 115 v12 reference task IDs. Future retains 298 of 310 historical reference task IDs; the 12 removed IDs and two new IDs are boundary changes caused by removing false event/archival semantics, while all 502 claims remain source-covered. This variance is recorded rather than described as exact golden equivalence.

The repaired Drake regression replay preserves 9,728 candidate variants with zero semantic-contract losses. Each of the four `p01-1` tasks now has a 99-candidate pool across 22 reviewable families, with four family-distinct cards in the blind review packet. No candidate was manually inserted.

## Verification

The full repository suite passes: **311/311**. Frozen P0 evidence remains unchanged; the new behavior contract is an additional hash-bound runtime contract.

No template selection, fit validation, migration, or rendering is authorized by this receipt.
