# Read-only VisualTask / AE technical-spec comparison

Date: 2026-09-27
Branch: `codex/visualtask-ae-spec-comparison`

## Objective

Test the next matching-layer step from `final_documentary_system_plan.md`: compare the reviewed VisualTasks with the measured After Effects technical-capacity data without changing the live slate, media, binding, pairing, selection, or rendering paths.

This is an evidence test, not activation. It must reveal which candidate decisions the existing data can support now and which fields or mappings are still missing.

## Real problem and baseline evidence

- The live match artifacts are beat-scoped while the pilot contains 41 VisualTasks from 40 beats, including two distinct tasks for beat `28-28`.
- The approved scene records still mark native composition mapping and verified capacity as unknown for reviewed Archive 3 scenes.
- The measured AE reports contain exact project/composition timing, media-input maxima, and text-field availability, but are not connected to approved scene IDs or VisualTasks.
- Therefore the current matcher can recommend an observed preview scene without showing whether its native composition can hold the task, and the measured reports cannot affect or explain a candidate decision.

## Required stages and acceptance checks

### 1. Freeze the comparison inputs

Bind the VisualTask artifact, current capacity slate, approved scene catalog, AE all-template summary, composition CSV, and text-field CSV by SHA-256. Reject changed inputs.

Acceptance: a stale or tampered input fails validation before a comparison is accepted.

### 2. Import a portable technical index

Derive a compact, repository-portable index from the frozen AE reports. Preserve project evidence status, source project hash, per-composition dimensions, duration, media capacity, simultaneous maxima, text availability, and unresolved counts. Do not copy machine-specific source paths as identifiers.

Acceptance: all 32 measured projects and all 3,926 measured compositions are represented, and summary counts reconcile to the frozen source reports.

### 3. Link only evidenced scene families

Create an explicit crosswalk from approved AE template-family IDs to measured project IDs. A family link does not claim an individual preview scene maps to a native composition. Duplicate/version choices must state why one project is selected.

Acceptance: unknown families remain unmapped; a bad project ID or duplicate family link fails.

### 4. Compare VisualTasks with the existing slate

Reuse the existing beat-level candidate slate as the baseline semantic candidate set. Join each candidate to its approved scene family and, where linked, to measured project capacity. Compare task identity demand with the maximum simultaneous visual-input capacity of that measured project.

Verdicts are deliberately limited:

- `project_capacity_conflict`: the task's identity demand exceeds every measured composition in the linked project.
- `project_capacity_possible`: project-level capacity is high enough, but exact scene/composition fit remains unverified.
- `project_capacity_unknown`: the family is linked, but the inspector did not verify enough replacement slots to treat zero or a lower bound as a hard maximum.
- `technical_spec_unmapped`: no reviewed family-to-project link exists.

No result may be labeled `fillable_now` until exact scene-to-composition mapping, required task fields, media-kind constraints, person/group eligibility, text limits, timing fit, and media availability are present.

Acceptance: all 41 VisualTasks receive a comparison row; the two `28-28` tasks remain separate; task-scoped identity demand is used rather than global documentary-subject inheritance.

### 5. Publish a before/after evidence report

Report baseline beat identity demand beside VisualTask identity demand, candidate coverage, project-level capacity conflicts/possibilities, unmapped candidates, and the exact missing fields that block final fillability.

Acceptance: the report explicitly states that it is review-only, does not authorize selection or rendering, and identifies the plan-line-107 gaps instead of guessing them.

### 6. Regression and omission checks

Start with a failing consumer test, then implement. Test deterministic output, source-hash rejection, crosswalk validation, split-task preservation, task-scoped identity counts, conservative verdicts, and unchanged live artifacts. Run the VisualTask and AE technical-spec suites as regressions.

Acceptance: focused and regression tests pass; hashes of live slate, bindings, media, and pairing artifacts are unchanged; no AE application, render, paid call, or source-template modification occurs.

## Explicit non-goals

- No live matcher activation or candidate reranking.
- No modification of approved scene records.
- No guessed preview-scene-to-native-composition mapping.
- No claim that project-level capacity proves a specific scene is fillable.
- No render, AE launch, template edit, media sourcing, or paid model call.

## Execution review

Executed in the required order on 2026-09-27:

| Stage | Evidence | Result |
|---|---|---|
| 1. Freeze inputs | The comparison records SHA-256 and byte size for VisualTasks, unchanged slate, approved catalog, crosswalk, technical index and legacy entity declaration; validator rejects stale sources. | Passed |
| 2. Import technical index | Frozen reports reconcile to 32 projects, 3,926 compositions and 3,078 text fields; per-composition timing, geometry, media maxima and text fields are preserved without absolute source paths. | Passed |
| 3. Link evidenced families | Thirteen family links carry written package/project evidence; unknown families remain unmapped; unknown project IDs fail closed. | Passed |
| 4. Compare tasks | All 41 VisualTasks receive a row over the unchanged 257 baseline candidates; beat 28 remains two distinct tasks with display demands 0 and 10. | Passed |
| 5. Publish evidence | The report finds 57 linked candidates, 200 unmapped, 47 project-capacity-possible and 10 capacity-unknown. It emits no `fillable_now`, selection approval or render approval. | Passed |
| 6. Regression and omission checks | Initial focused test failed with ImportError before implementation. After implementation: 10 comparison, 15 VisualTask and 13 AE inspection tests pass. Full suite ran 465 tests with the same unrelated Cloudflare-credential failure documented in no-drifting entry 0131. Protected live artifact hashes validate unchanged. | Passed for this change; unrelated environment failure retained |

No required stage was skipped or reordered. No AE application, render, paid call, source-template edit, live ranking, pairing or selection change occurred.
