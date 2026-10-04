# Job 4 — Matching transformations and visual-job derivation

## One job

Audit how the current Matching code turns a validated StoryPackage into review
tasks and a template-neutral visual job.

## Trace step by step

1. Contract gate and adapter preservation.
2. `_split_claim_segments` and `_semantic_units`.
3. Presentation-operation inference and primary-operation priority.
4. Derived legacy job labels.
5. Entity, value, cohort, obligation and continuity propagation.
6. Requirement derivation and unresolved-gap behavior.

For every reviewed failure class, identify the earliest transformation where the
correct meaning was lost. Evaluate hard-coded keywords, priority ordering,
multi-operation handling, rhetorical questions, non-quantitative claims,
relationships, evidence requests, plural artifacts and comparisons.

## Required outputs

- `reports/astra-root-cause/04-matching-transformations.md`
- `reports/astra-root-cause/04-matching-transformations.json`

Include replayable input/output traces for at least 20 tasks, with successful and
failed examples. Each trace must name the first divergent stage.

## Acceptance

- The audit distinguishes Story-provided `jobProposals` from Matching-derived
  presentation operations.
- It tests whether one primary operation suppresses necessary meaning without
  proposing an unrelated-family union.
- No code changes are made.

Stop after Job 4.
