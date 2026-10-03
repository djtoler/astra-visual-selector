# Post-render narration timing feasibility plan

Date: 2026-09-30
Status: authorized by the editor

## Objective

Determine whether an already approved template scene can be conformed to an exact narration duration after its native render, including whether its ending can be used directly or needs an added transition. Reuse the approved scene timing contracts and existing VisualTask timing comparison. Do not retime inside After Effects, invent a playback-rate quality threshold, modify a template, or authorize selection/rendering.

## Required stages and acceptance checks

### 1. Bind existing evidence

- Bind the approved scene catalog and the VisualTask/AE comparison by SHA-256.
- Acceptance: every evaluated row has an exact task-audio duration and an approved scene timing contract; absent evidence remains unresolved.

### 2. Calculate the post-render plan

- Use `playbackRate = approvedNativeSceneDuration / narrationDuration` and `outputDuration = approvedNativeSceneDuration / playbackRate`.
- Preserve the native render and describe only a derivative operation.
- Acceptance: output duration reproduces narration duration within one millisecond; the calculation never changes the source template.

### 3. Detect ending/outro handling

- Read `transitionBoundaryVerified` and `needsAddedTransition` from the approved scene contract.
- Acceptance: a verified boundary yields either `native_boundary` or `add_transition`; an unknown boundary remains `unresolved_transition_boundary` and cannot be called feasible.

### 4. Preserve editorial quality review

- Do not infer that an extreme speed change is visually acceptable merely because duration arithmetic works.
- Acceptance: every calculated plan is `structurally_feasible_editorial_pacing_review_required`; no fillability, selection or rendering verdict is emitted.

### 5. Verify and publish the diagnostic

- Add deterministic tests for direct duration, speed-up, slow-down, added-transition, unknown-boundary and missing-contract cases.
- Generate a source-bound report over current exact timing observations.
- Acceptance: tests pass, report rebuilds identically, and protected matching/rendering artifacts are not activated.
