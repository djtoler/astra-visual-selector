# Accelerated AE clip-to-composition completion plan

Date: 2026-09-29
Branch: `codex/treatment-requirements-review`
Status: proposed; execution requires explicit user approval

## Objective

Resolve every semantic AE preview clip to one explicit terminal state:

1. `mapped_verified` or `mapped_verified_window`, with an exact source-bound native composition and clip/window technical specification;
2. `mogrt_not_aep`, when the source is not an inspectable AEP and remains excluded;
3. `project_unlinked`, only after the local source search is exhausted and the missing link is named; or
4. `verification_blocked`, with the exact evidence still required.

No guessed mapping may inherit media-slot, simultaneous-input, text-field, duration, fillability, selection, or rendering claims.

## Baseline

The current coverage report contains 428 clips:

- 54 `mapped_verified`
- 17 `mapped_verified_window`
- 5 `mapped_composition_window_approximate`
- 333 `mapping_unverified`
- 5 `mogrt_not_aep`
- 14 `project_unlinked`

The completed calibration replayed 73 verified mappings. Generic ordinal, semantic-path, and single-output shortcuts produced nine false mappings among 33 proposals, so none is authorized for automatic verification.

## AWS decision gate

Do not begin in AWS. The immediate bottleneck is evidence reconciliation between Envato preview slices and native AE compositions, not final-frame rendering. Existing local semantic catalogs, verified anchors, source-bound technical reports, and native timelines must be exhausted first.

AWS becomes eligible only if the local evidence pass leaves at least 50 clips requiring native still/contact-sheet probes and the measured local queue would take more than four hours. Before cloud use, record setup time, package size, AE/plugin/font compatibility, licensing path, projected instance-hours, and projected cost. Cloud inspection must use the same source-bound scripts and receipts as local inspection; it cannot weaken verification.

Reason: EC2 Mac uses one bare-metal Mac per Dedicated Host and has a 24-hour minimum host allocation. A new AE environment would also need the application, matching version, fonts, plugins, source projects, and media. That setup is unlikely to beat the already working local AE installation for the first evidence pass.

## Required execution stages

### 1. Freeze and inventory

Regenerate the 428-clip coverage ledger from the existing semantic catalogs, family links, technical index, verified mapping sidecar, window-capacity reports, and source hashes. Group the 333 unresolved clips by project and by available evidence.

Acceptance:

- Counts reproduce the baseline before any promotion.
- Production mappings and semantic descriptions are unchanged.
- Every source is hash-bound.

### 2. Learn family-specific rules from verified anchors

Test family-specific rules rather than global shortcuts. Candidate rule types are:

- exact clip ordinal to native scene ordinal;
- a constant, family-specific ordinal offset;
- one verified final composition with exact native time-window propagation;
- an exact ordered master-timeline relationship; and
- an exact named-terminal composition relationship.

Use leave-one-out replay: hide each usable verified anchor, learn from the remaining anchors in that family, and predict the hidden mapping. A rule is eligible only with zero errors, at least two independent anchors, deterministic output, and no contradictory project structure.

Acceptance:

- A rule with any replay error is rejected for that family.
- Rules emit proposals first; they do not write production mappings.
- Evidence records the rule, anchors, source hashes, proposed composition, and alternatives.

### 3. Resolve the high-yield evidence batches

Process in this order:

1. Families with multiple anchors and a constant verified ordinal relationship.
2. Families whose reviewed clips are exact windows inside one verified final composition.
3. Families with an ordered native master timeline that can be reconciled to preview order and duration.
4. Remaining linked projects requiring visual confirmation.
5. The 14 `project_unlinked` clips, by searching the known local template roots and source hashes.

Each batch is regenerated, tested, committed, and pushed before the next batch. The unrelated untracked replacement-selection file remains excluded.

Acceptance:

- No batch is promoted solely from name similarity, numerical coincidence, confidence, or vector similarity.
- Each promoted mapping has independent native evidence beyond the rule that proposed it.
- Window-based templates receive window-specific technical facts; whole-composition capacity is never substituted for a scene window.

### 4. Native verification without full rendering

Use the existing local AE inspection system for unresolved proposals. Prefer, in order:

1. native master-timeline/layer evidence;
2. exact composition structure and timing;
3. a low-resolution still/contact sheet from the original template; and
4. the shortest gated native video probe only when motion is required to distinguish candidates.

This stage does not render replacement content and does not test treatment fit. It identifies the original native composition behind a preview slice.

Acceptance:

- Every visual probe preserves the original template and names its source composition.
- A still is not used when the distinction depends on motion.
- Ambiguous evidence stays blocked rather than being forced into a mapping.

### 5. Attach and validate technical capabilities

After composition identity is verified, regenerate exact duration, editable text, total media-input, and maximum-simultaneously-enabled-input facts from the source-bound native report. For master-composition clips, compute the exact reviewed window before deriving capacity.

Acceptance:

- Composition ID/path exists in the bound technical report.
- Source project hashes agree across mapping, project link, native report, and technical index.
- Calculated facts never depend on an Envato description or model inference.
- Existing capacity regression tests and new family-rule tests pass.

### 6. Completion audit

Regenerate the full coverage report and publish an exception ledger. Completion means every one of the 428 clips has one explicit terminal state; it does not mean relabeling unresolved clips as verified.

Acceptance:

- Zero silent `mapping_unverified` records.
- Every verified clip has usable clip/window technical facts.
- Every exception names the missing source or evidence and its impact on matching.
- The full test suite runs; unrelated failures are reported separately.
- Live matching consumes only verified technical records.

## User assistance

No input is needed during the non-AE evidence stages. During native verification, keep After Effects available on this Mac. If Adobe displays a modal license, conversion, missing-font, or missing-file dialog that automation cannot safely resolve, the user may need to choose the non-destructive option. Missing fonts are substituted and flagged under the existing policy; they do not disqualify a technical inspection.

## Commit policy

After execution approval, completed and tested batches will be committed and pushed continuously to `codex/treatment-requirements-review` without pausing for separate push permission. No merge to `main` is authorized.
