# Exact preview-scene to native-composition mapping test

Date: 2026-09-27
Branch: `codex/visualtask-ae-spec-comparison`

## Objective

Resolve the 24 unique preview scenes already linked to measured AE projects to exact native composition IDs and paths wherever the existing reviewed scene record and source-bound technical report establish a unique match. Preserve ambiguity instead of inferring a mapping from family membership alone.

## Required stages and acceptance checks

### 1. Freeze the 24-scene scope

Derive the unique scene IDs from the existing read-only VisualTask/AE comparison and bind that report, approved catalog, technical index, and family links by hash.

Acceptance: scope is exactly the currently measured 24 unique scenes across 11 families; an out-of-scope or unknown scene fails.

### 2. Reconcile reviewed preview evidence with native composition identities

For each scene, compare its reviewed title, description, sequence position, dimensions/orientation, and duration with exact composition IDs, paths, dimensions, durations, input capacity, and text fields. Record the evidence rule used.

Acceptance: a verified mapping must identify exactly one existing composition in the linked project. Ordinal-only or visual-similarity-only guesses remain unresolved unless the project naming and reviewed sequence together make the identity unique.

### 3. Encode mappings separately

Store mappings in a dedicated sidecar rather than editing the approved catalog. Each record must be `verified` or `unresolved`; verified records require project ID, composition ID/path, and evidence. Unresolved records require the remaining ambiguity.

Acceptance: duplicate scenes, unknown projects/compositions, path/ID disagreement, or a verified record without evidence fails.

### 4. Use exact composition capacity where verified

Update only the read-only comparison consumer. Verified scenes use their exact composition’s dimensions, duration, media maxima, and text fields. Unresolved scenes retain conservative project-level results.

Acceptance: the report distinguishes exact-composition evidence from project envelopes and still cannot emit `fillable_now` while other required matching fields are missing.

### 5. Test and report coverage honestly

Start with a failing mapping-consumer test. Test valid and invalid mappings, exact metric selection, unresolved preservation, determinism, source hashes, and unchanged protected live artifacts. Run existing comparison, VisualTask, and AE inspection regressions.

Acceptance: report the exact number mapped and unresolved. No AE launch, render, catalog mutation, live slate change, paid call, or template edit occurs in this pass.

## Execution review

Executed in order on 2026-09-27:

| Stage | Evidence | Result |
|---|---|---|
| 1. Freeze scope | The saved comparison at commit `6b3215c` identified 24 unique measured AE scenes across 11 families; the mapping sidecar records that commit and report hash, and validation re-derives the exact scene set from current bound inputs. | Passed |
| 2. Reconcile identities | Master preview timelines provided direct native layer intervals for Screen Mockup, Scrolling Screen, Text List Carousel and Photo Slideshow. Unique final-composition names/structure resolved Carousel Flow, Carousel Photo Logo Reveal, Looped Slideshow, one Gallery Pro and one Carousel Slideshow scene. Numbered ten-second package sequence resolved two Dropoff scenes. | Passed where evidenced; four ambiguities retained |
| 3. Encode separately | `grammar/ae-scene-composition-mappings.json` contains exactly 24 records: 20 verified and four unresolved with explicit candidate compositions and reasons. The approved catalog remains unchanged. | Passed |
| 4. Consume exact capacity | Verified candidates now expose exact composition dimensions, duration, total/simultaneous inputs, recursive media slots and recursive text-field identities. Unresolved candidates retain project envelopes. | Passed |
| 5. Test and report | Focused mapping/comparison suite passes 18 tests, VisualTask regressions pass 15, and AE technical-spec regressions pass 13. The full suite ran 473 tests: 459 passed, 13 skipped, and the same pre-existing Cloudflare credentials test failed because preflight stops before its expected `--confirm` message. The rebuilt report still denies selection, rendering and `fillable_now`. | Passed with one pre-existing environment-dependent failure |

No required stage was skipped or reordered. No AE application, render, paid call, source-template edit, approved-catalog mutation, live ranking, pairing or selection change occurred.
