# VisualTask technical-requirements comparison test

Date: 2026-09-28
Branch: `codex/visualtask-ae-spec-comparison`

## Objective

Encode the task-side technical requirements that are already explicit in the current VisualTask and baseline shot records, then compare them with exact native AE composition measurements. Do not infer treatment-specific media-slot demand, media kinds, on-screen text, or timing-adjustment permission where the current artifacts do not define them.

This implements the next matching-layer step in `final_documentary_system_plan.md`: machine-readable template requirements and honest `fillable_now`/conditional boundaries. It remains a read-only test and does not activate a slate or render.

## Required stages and acceptance checks

### 1. Freeze the task and timing sources

Bind the 41 VisualTasks and their 40 baseline source-beat records by hash.

Acceptance: every VisualTask resolves to exactly one baseline source beat; duplicate or missing records fail.

### 2. Encode only source-supported task requirements

Preserve each task's visual intent, display-eligible identities, truth constraints, perceptibility constraints, prohibited implications, and existing required encoding labels. A task that is the sole VisualTask for a source beat receives that beat's exact saved start, end, and duration. Split tasks remain timing-unresolved unless a separately saved exact split exists.

Acceptance: all 41 tasks are present. Known and unknown fields are distinguished explicitly. Display identities are never re-labelled as media slots.

### 3. Keep treatment-dependent requirements unresolved

Record media-slot count, media kinds, person/group eligibility, on-screen text-field count, exact text strings, and typed data values as unresolved because the current VisualTask does not assign them to a specific treatment.

Acceptance: no default, estimate, or semantic guess fills these fields. Split-task encoding requirements remain source-beat context, not falsely task-allocated.

### 4. Compare exact timing without declaring fit

Where both an exact task span and exact native composition exist, report native duration, required audio duration, their difference, and whether the unmodified native duration covers the audio span. Keep timing fit unresolved because no approved looping, trimming, speed, freeze, or extension policy is encoded.

Acceptance: the comparison exposes an observation only. It cannot emit `fillable_now`, `conditional`, selection, or rendering authorization.

### 5. Prove the prior slot-demand shortcut is gone

Start with a failing test requiring a durable task-requirements consumer and forbidding identity count from being treated as required media-slot count. Test source binding, split-task handling, exact timing observations, stale input failure, deterministic replay, and protected live artifacts.

Acceptance: focused tests and existing VisualTask/AE regressions pass. No AE launch, render, paid call, source-template edit, approved-catalog mutation, live ranking, pairing, or selection change occurs.

## Execution review

Executed in order on 2026-09-28:

| Stage | Evidence | Result |
|---|---|---|
| 1. Freeze sources | The requirements artifact binds the 41-task VisualTask artifact and 40-row baseline slate by path, hash and byte count; its consumer replays from those inputs. | Passed |
| 2. Encode supported requirements | All 41 tasks preserve intent and semantic constraints. The 39 unsplit tasks use their exact saved source-beat spans; both beat-28 split tasks remain unresolved. | Passed |
| 3. Preserve treatment-dependent unknowns | All 41 tasks retain null media-slot, media-kind, person/group, text-field and typed-data requirements. Existing encoding categories are exact only for unsplit tasks. | Passed |
| 4. Compare timing without fit claims | Forty-seven exact-composition candidate placements have timing observations: native duration covers the unmodified task span in 41 and is shorter in six. Every observation explicitly remains non-authorizing because no duration-adjustment policy is encoded. | Passed |
| 5. Prove shortcut removal | The new requirements suite initially failed because its consumer did not exist; comparison tests then failed until identity-to-slot verdicts were removed. Focused requirements, comparison and mapping suites pass 29 tests; VisualTask regressions add 15 and AE pass reconciliation adds two. The full suite ran 484 tests: 470 passed, 13 skipped, and the same pre-existing Cloudflare-credentials test failed because preflight stops before its expected `--confirm` message. | Passed with one pre-existing environment-dependent failure |

No required stage was skipped or reordered. No AE application, render, paid call, source-template edit, approved-catalog mutation, live ranking, pairing, or selection change occurred.
