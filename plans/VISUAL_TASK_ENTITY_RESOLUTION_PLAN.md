# VisualTask and task-scoped entity-resolution pilot

Date: 2026-09-27

## Objective

Create a derived, reviewable VisualTask layer for the existing Year Seventeen pilot so matching no longer assumes one communication job or one globally inherited documentary subject per beat. Preserve the existing beats, picks, review notes, media decisions, bindings, and pairings unchanged.

This implements the first dependency in `final_documentary_system_plan.md`'s matching layer: match VisualTasks rather than whole beats, resolve implied subjects in context, expand versioned cohorts, and never merge the documentary subject into every task by default.

## Evidence that this is the next real problem

- `grammar/issues_matching_layer.json` PI-01 measures Drake being injected into 36 of 40 beats where the beat text does not name him, producing 367 of 708 media candidates and all candidates on 13 beats.
- PI-02 measures 11 cohort references that do not expand to the people the visual must represent.
- PI-05 records eight beats where the user assigned different sentences to different templates, while the current representation allows one job per beat.
- `grammar/beat-entities.json` currently expresses the documentary subject as `appliesTo: every beat`.

## Consumer

The immediate consumer is a validator/report command in this change. Existing slate, media, and pairing stages do not consume the pilot automatically yet; that prevents an unreviewed representation from silently changing current results. A later explicitly planned migration can make the reviewed VisualTask artifact an input to those stages.

## Required stages and acceptance checks

### 1. Freeze source evidence

Read existing beats, narration timing, task overrides, cohort definitions, and source hashes. Reject unknown beat IDs, duplicate task IDs, spans outside the source beat, invalid entity names, missing cohort versions, and changes to hashed source files.

Acceptance: invalid fixtures fail before any artifact is written.

### 2. Build one default task per beat

Copy each beat's exact quote, job, truth/perception obligations, entity count, and source identity into a derived task. Extract explicitly named entities through the existing deterministic gazetteer. Do not inherit the documentary subject.

Acceptance: the default build produces one task for every source beat and zero task receives Drake merely because he is the documentary subject.

### 3. Apply source-bound task overrides

Allow an override to split one beat into multiple tasks, narrow each task to an exact source span, declare implied entities with provenance, attach versioned cohorts, and group consecutive tasks for continuity. Overrides may only use existing jobs and roster entities.

Acceptance:

- `01-01` resolves Drake as an implied subject with recorded evidence.
- `02-02b` resolves Curren$y and does not inherit Drake.
- `03-03` attaches the versioned 93-artist opening-chart cohort and includes Drake as one cohort member rather than as a global subject.
- `28-28` is represented by distinct setup-text and spatial-comparison tasks.

### 4. Preserve uncertainty

Ambiguous names, unknown names, unresolved pronouns, missing cohort membership, and task/entity-count mismatches remain explicit issues. They are never guessed away.

Acceptance: a synthetic unresolved subject remains unresolved and does not become Drake.

### 5. Produce and consume the artifact

Write `grammar/visual-tasks.json` deterministically and validate it by reading it back through a separate consumer. The consumer reports task, split-beat, implied-entity, cohort, unresolved, and issue counts.

Acceptance: two builds are byte-identical; the consumer accepts the real artifact; a tampered artifact fails.

### 6. Regression and omission checks

Run the focused VisualTask tests, the AE technical-spec tests, and the repository test suite. Record any unrelated pre-existing environmental failure separately. Verify that the implementation does not write to beats, picks, bindings, media picks, pairings, or review exports.

Acceptance: focused tests pass and source hashes remain unchanged.

## Explicit non-goals

- No paid model call or reclassification.
- No template rebinding or slate regeneration.
- No automatic migration of existing picks or pairings.
- No AE inspection run, rendering, or source-template modification.
- No import of capacity results into matching yet.
- No claim that every cohort or implied subject in the full script is resolved by this pilot.

## Execution review

Executed in the required order on 2026-09-27:

| Stage | Evidence | Result |
|---|---|---|
| 1. Freeze source evidence | Artifact binds SHA-256 values for beats, timing, roster, overrides and cohorts; tests reject stale hashes, unknown entities, missing cohort versions and invalid spans. | Passed |
| 2. Build default tasks | `pipeline.visual_tasks build` read all 40 source beats and produced one default task wherever no override exists. | Passed |
| 3. Apply overrides | Output contains the approved 01-01, 02-02b, 03-03 and split 28-28 cases. | Passed |
| 4. Preserve uncertainty | 02-02b retains the withheld comparison-catalog identity; a synthetic unresolved subject remains unresolved and is not guessed as Drake. | Passed |
| 5. Produce and consume | Builder wrote 41 tasks; the separate validator replayed the artifact byte-for-byte from its bound sources. Duplicate IDs and tampered content fail. | Passed |
| 6. Regression and omission checks | 15 focused tests and 13 AE-tool tests pass. Full suite ran 455 tests: 441 passed, 13 skipped, and one pre-existing environment-dependent R2 test failed because absent Cloudflare credentials make preflight stop before its expected `--confirm` message. | Passed for this change; unrelated environment failure retained |

No required stage was skipped or reordered. No paid call, template binding, slate build, media pairing, AE inspection, or render ran.
