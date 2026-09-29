# Matching accuracy batch 01

Date: 2026-09-28  
Branch: `codex/treatment-requirements-review`

## Objective

Run one read-only, replayable matching-layer accuracy batch across five deliberately different cases. Use only existing VisualTasks, reviewed prose, current candidate slates, approved template records and saved media-review evidence. Do not change live picks, pairings, selection, rendering or source templates.

## Frozen cases

1. **Eleven-person carousel test:** `16-16.main` names eleven visible cohort members. For this test, at least one After Effects long-media-carousel scene must support an explicit treatment for all eleven using the actual media. The chosen native test used a fourteen-photo template, assigned all eleven unique people and intentionally filled the three surplus slots with specified repeats. The render and editor response—not `14 >= 11` arithmetic—determine whether that treatment works visually. This treatment is batch-specific, not a general 10+ routing rule. The separate global rule automatically adds every available spatial scene only at 20+ people.
2. **Split beat:** source beat `28-28` must remain two distinct VisualTasks: setup text and spatial overlap. A whole-beat candidate list must not erase that separation or invent per-task timing.
3. **Text-heavy/document treatment:** `17-17.main` with existing candidate `02-documentary-promo--scene-003`. The proposed treatment must communicate one universal rule plus the full-credit and half-credit definitions. Missing exact native text-field mapping must stay unresolved rather than becoming `fillable_now`.
4. **Actual footage required:** `01-01.subject`. The user's saved direction requires Drake performance footage. A counter, diagram or still cannot silently satisfy that requirement.
5. **Missing media must be conditional:** `15-15.main` with an authentic-event b-roll treatment for the 2010 XXL offer and refusal. The saved review says no available b-roll; the result must be `conditional` with a typed missing-media brief, not a filled or selected result.

## Required stages and acceptance checks

### 1. Bind existing evidence

Hash the VisualTask artifact, technical comparison, current capacity slate, full review export, matching issues, approved template list and local template registry.

Acceptance: a changed or missing bound input fails before evaluation; no source artifact is rewritten.

### 2. Evaluate the five cases independently

Read each case from its authoritative artifact and report observed behavior separately from the expected rule.

Acceptance: every case reports `pass` or `fail`, exact evidence, and exact missing requirements. One passing case cannot hide another failure.

### 3. Preserve review boundaries

Treatment details in this batch are proposals only. The evaluator cannot approve a treatment, select a template, authorize rendering or mutate the current slate.

Acceptance: the report declares `review_only_not_connected`; selection and rendering authorization remain false.

### 4. Prove the evaluator

Add focused tests for deterministic output, source-hash rejection, all-spatial enumeration, split-task preservation, unresolved text-field evidence, footage requirement detection and conditional missing-media behavior.

Acceptance: focused tests pass and two identical runs are byte-identical. Existing VisualTask, technical-spec and treatment-requirements tests remain green.

### 5. Publish the measured result

Write one report under `matching-accuracy/batch-001/`. The first run records failures as evidence; any later repair must be implemented generically, rebound to the same evidence, and replayed through the unchanged cases.

Acceptance: the report identifies the current pass/fail count and never claims that an unreviewed treatment is accurate or production-ready.

## Non-goals

- No LLM or paid call.
- No rendering or After Effects work.
- No live matching, ranking, pick, pairing or media change.
- No custom visual or template modification.
- No automatic approval of the five treatment proposals.

## Execution review

Completed on 2026-09-28 with no deviation from the saved stage order.

- Source binding: passed for all seven frozen input artifacts.
- Five-case evaluation: completed; all 5 now pass against the corrected matching rules.
- Review boundary: passed; the report remains `review_only_not_connected`, with selection and rendering authorization false.
- Focused and related verification: 50 VisualTask, technical-requirement, AE-spec and matching-accuracy tests passed, plus 5 live media-backed VisualTask matching tests passed with normal database access.
- Repeatability: two evaluator runs and the saved report were byte-identical (`sha256: 2a161a583bbbc785322e4069cba76d08b887401a1592b87dd98fdb6781602b7c`).
- Published result: `matching-accuracy/batch-001/report.json`.

The original 10+ spatial expectation was corrected after editor review: this case uses a capacity-qualified long-carousel After Effects template only as its specific test treatment. It does not establish a global long-carousel threshold. The separate matching rule automatically includes every available spatial scene at 20+ people while preserving other valid options.

The two measured media-contract gaps were then repaired generically. A versioned, source-bound VisualTask media-requirements input now carries reviewed media kinds, entities, content constraints and availability without hardcoding them in the evaluator. Known missing required media produces a `conditional` candidate result with the same typed missing-media brief, while preserving the candidate's separate AE technical-evidence state. This does not select a template, claim fillability or authorize rendering.

Post-audit correction: the saved batch report currently preserves only the capacity-qualified candidate assertion and therefore does not fully represent the purpose or outcome of the eleven-person native test. The durable result must bind the exact eleven unique identities, fourteen media assignments, three surplus-slot repeats, native render receipt and editor visual verdict. Until that correction is implemented, this case is incomplete as a matching-accuracy result even though the native render itself succeeded.
