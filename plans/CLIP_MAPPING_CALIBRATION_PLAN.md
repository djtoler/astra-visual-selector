# Clip-to-composition bulk-mapping calibration plan

Date: 2026-09-29
Branch: `codex/treatment-requirements-review`
Status: authorized calibration; review-only and disconnected from live matching

## Objective

Test whether any deterministic evidence class can safely propose native composition mappings in bulk. The calibration must measure exact composition ID/path precision and abstention. It must not promote predictions into the registry, change matching behavior, select templates, or authorize rendering.

## Required stages and acceptance checks

### 1. Freeze inputs, hidden gold labels and a prospective sample

Bind the semantic catalogs, family-to-project links, portable technical index and the current 73 verified mapping records by hash. The predictor may use the first three inputs but must not read the verified mapping sidecar. Select a deterministic cross-family sample from currently `mapping_unverified` clips before scoring it.

Acceptance: prediction fails if a bound source changes; gold labels are loaded only by the scoring step; sample IDs are deterministic and contain no already verified mapping.

### 2. Implement conservative evidence classes

Generate ranked composition candidates from replayable structural evidence such as exact normalized scene/final names, unique final composition identity, exact ordinal correspondence and compatible duration/orientation. Every prediction must name its evidence class and alternatives. Weak semantic similarity cannot verify a mapping.

Acceptance: the predictor can emit `proposed` or `abstain` only. It cannot emit `verified`, capacity, fillability, selection or rendering authorization.

### 3. Replay against the 73-label reference set

Run the predictor without the answer file, then compare locked predictions with the verified sidecar. Report exact ID/path matches, errors, abstentions and per-evidence-class precision/coverage.

Acceptance: an evidence class is eligible for later automatic verification only when it has zero false mappings, at least three scored predictions and coverage across at least two template families. Coverage is secondary to precision.

### 4. Run a prospective cross-family sample

Lock predictions for at least 30 currently unverified clips across portrait slideshow, landscape/text slideshow, carousel, documentary/multi-scene and incompatible/static-only families. Independently review only the proposed subset against existing native timeline, exact structure, screenshots or the shortest gated probe necessary.

Acceptance: predictions are saved before verification; unverifiable cases remain abstentions; any false prospective mapping disqualifies that evidence class.

### 5. Publish the trust boundary

Save one deterministic report declaring which evidence classes, if any, are trusted, which remain proposal-only, exact replay/prospective metrics, and the next safe batch size.

Acceptance: two runs are byte-identical; the current mapping sidecar and live matching artifacts remain unchanged; no class with a false mapping is trusted.

## Non-goals

- Mapping all remaining clips during calibration.
- Treating project-level capacity as clip-level capacity.
- Using model confidence as authorization.
- Rendering complete compositions by default.
- Editing source templates or the approved semantic descriptions.

## Execution review — 2026-09-29

All required stages ran in order with no workflow deviation.

- Inputs and the 73 verified labels are hash-bound. The predictor cannot read the verified-label source, and the production mapping sidecar remained byte-identical.
- The predictor emitted only `proposed` or `abstain`. Prospective predictions were locked by a deterministic SHA-256 digest before native timeline evaluation.
- Replay: 73 clips, 33 proposals, 24 exact matches, 9 false mappings, 40 abstentions. Precision was 72.73% at 45.21% coverage.
- Every tested structural evidence class failed the zero-error gate: ordinal matching was 15/22, semantic-path matching was 1/2, and single-output matching was 8/9.
- Prospective sample: 30 currently unverified clips, 17 families and all five target categories. There were 12 proposals. Existing native master timelines independently labeled two; both contradicted the proposals. The remaining cases stayed unresolved and were not rendered because no evidence class remained eligible for trust.
- Decision: no evidence class is trusted, the next safe automatic batch size is zero, and bulk mapping remains proposal-only.
- Verification: 9 calibration tests and 48 focused related tests pass. The full suite ran 569 tests with 13 skips and one pre-existing unrelated Cloudflare-credentials failure in `test_push_needs_confirm_as_well`.
