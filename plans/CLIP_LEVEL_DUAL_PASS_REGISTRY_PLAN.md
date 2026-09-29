# Clip-level dual-pass template registry completion plan

Date: 2026-09-28
Branch: `codex/treatment-requirements-review`
Status: proposed next matching-layer prerequisite; no selection or rendering authorized

## Objective

Complete the existing dual-pass registry at the unit the matcher selects: every preview scene `clipId`. Preserve the existing semantic descriptions and existing technical measurements. Join them only through exact source-project and native-scene evidence.

Current measured baseline (corrected 2026-09-28):

- 40 After Effects catalog families across the union of the current approved catalog and intake review catalog.
- 428 unique preview scene clips: 185 approved-catalog scenes plus 243 intake-review scenes.
- The earlier 375 figure measured clips that received a capability-model label (208 + 167); it was not the complete current AE catalog and must not be used as the coverage denominator.
- 32 technically inspected source projects.
- 3,926 measured native compositions.
- 3,078 indexed native text fields.
- 14 catalog families currently linked to measured projects, covering 161 clips.
- 27 clips currently included in the exact composition-mapping artifact: 23 verified and four unresolved.

## Required stages and acceptance checks

### 1. Produce the complete coverage ledger

Enumerate all 428 AE `clipId` records. For each, record its family, source preview, source timestamps, source AE project status, technical-project link status and scene-mapping status. Preserve explicitly excluded and pending scenes in the ledger with their availability state; do not silently drop them from technical accounting.

Acceptance:

- Exactly 428 unique AE clip IDs appear once.
- Counts reconcile to both current semantic catalogs: 185 approved scenes and 243 intake-review scenes.
- Every clip has one typed state: `mapped_verified`, `mapping_ambiguous`, `project_unlinked`, `native_source_missing`, `native_incompatible_but_static_measured`, `mogrt_not_aep`, or another explicitly defined evidence state.
- No clip inherits a project's capacity merely because its family name resembles the project.

### 2. Link every family to technical source evidence

Use existing source paths, package names, project hashes and the completed 32-project inspection reports to link catalog families to measured projects. Locate existing unlinked source projects before declaring them missing. Preserve multiple-version relationships such as AE24/AE26 siblings.

Acceptance:

- Every one of the 40 AE families has either a hash-backed project link or a precise unavailable-source reason.
- A MOGRT, custom renderer or non-AEP family is labeled accurately and is not assigned AEP capacity.
- No new inspection is run when a matching frozen report already exists.

### 3. Map every preview slice to its native scene

Map each `clipId` to its exact native composition. Because a clip is a slice from a preview rather than a full template render, also record whether it represents the complete composition, a native subrange/scene, or an editorial preview excerpt whose native time correspondence remains unresolved.

Use, in order:

1. existing verified preview timelines, exact layer in/out points and native composition sequencing;
2. frame-rate and duration arithmetic to calculate candidate native windows from known anchors—for example, a 6.5-second pre-logo clip ending at a native 30.52-second logo entry yields an approximate 24.02–30.52-second window;
3. exact scene/composition names, numbered order, source timestamps and transition structure;
4. existing native renders or screenshots;
5. only for remaining visual ambiguity, a gated short native still/contact-sheet or narrowly targeted motion probe using the original template.

Arithmetic identifies duration and candidate offsets but does not manufacture a visual anchor. Keep its result `approximate` until native timeline or visual evidence verifies the anchor. Do not render a complete native composition when a static or short targeted window can answer the remaining question.

Acceptance:

- Every clip has one mapping record.
- A verified mapping cites replayable evidence.
- Ambiguous candidates remain listed rather than guessed.
- No full replacement-content render is required merely to establish a name/order mapping.
- Full-composition native renders are not the default mapping tool; any exception identifies the question that shorter evidence could not answer.

### 4. Derive the clip-level technical record

Join the mapped native evidence to each semantic `clipId`. Record:

- native project hash and composition ID/path;
- mapping scope: complete composition, native subrange or unresolved excerpt;
- total independent media inputs;
- maximum simultaneously enabled media inputs;
- exact media input IDs/paths and kinds;
- exact editable text fields and maximum simultaneously enabled text fields;
- composition and work-area duration;
- resolution and frame rate;
- unresolved technical claims and source/version compatibility.

When a verified native subrange changes which inputs or text fields apply, derive capacity for that window instead of copying the full composition maximum.

Acceptance:

- Every verified clip record carries both its unchanged semantic description and exact technical evidence.
- Project-level envelopes are never presented as clip-level capacity.
- Text and media field counts replay against the frozen technical index.

### 5. Validate registry completeness and accuracy

Add deterministic checks for catalog coverage, unique IDs, source hashes, mapping evidence, count reconciliation and prohibited project-level fallback. Review a cross-family sample including portrait slideshow, landscape slideshow with text, carousel, documentary scene, long multi-scene template and one incompatible/static-only project.

Acceptance:

- Zero missing clip IDs.
- Zero silent mappings.
- Two identical builds are byte-identical.
- Sampled records agree with their preview descriptions and native project evidence.
- Unresolved records remain unavailable for `fillable_now` until their mapping is verified.

### 6. Publish the merged registry for matching

Expose one versioned registry artifact keyed by `clipId`. Matching reads this artifact instead of independently joining the preview catalog, family links and project-level index.

Acceptance:

- Given a `clipId`, one lookup returns semantic mechanics, native capacity, mapping status and provenance.
- Existing matching behavior is not silently changed during registry construction.
- Selection and rendering remain separately gated.

## Explicit non-goals

- Rewriting the existing semantic prompts or descriptions.
- Re-inspecting all 32 projects without a source-hash reason.
- Treating composition capacity as visual-fit approval.
- Rendering replacement content for every clip.
- Selecting templates or changing current beat pairings.

## Pilot execution checkpoint — Carousel Slideshow

The five-clip Carousel Slideshow pilot is implemented in `reports/carousel-slideshow-clip-native-pilot.json`. All five clips now bind to exact measured native compositions; all five time windows remain labeled approximate because the distributed AEP contains gray placeholders rather than the Envato preview's sample photos. The pilot deliberately keeps window-specific focal-slot exposure unresolved instead of presenting the full composition's enabled-slot count as perceptible on-screen capacity.

Three gated native placeholder renders verified the distinct composition mechanics and passed complete decoding. The Render 02 full pass took 2,638.666 seconds and established that full-composition rendering is an inefficient default for mapping. The plan now requires timeline/frame arithmetic first and only the shortest targeted native probe needed for remaining visual ambiguity.

The clip-level validator rejects missing clips, duplicate IDs, stale technical-index bindings, composition ID/path mismatches, project-envelope substitution, invalid window durations, missing exposure status, incomplete native-render evidence and inconsistent frame math. The pilot/alignment/existing mapping and comparison suites pass 30 tests. This pilot remains review-only and does not activate matching or authorize production rendering.

## Existing-inspection family reconciliation checkpoint

The 27 previously unlinked families were checked against all 32 frozen technical projects using source AEP SHA-256 as the authorization boundary. `minimalism-slideshow` is an exact match to the measured `slideshow` project (`1da67cfa…4ab26`), so its 13 clips now carry project evidence; the three clips currently used by the comparison slate map to the project's sole 60-second final composition. The similarly named Archive 3 Comparison Pack was not linked: its current `Comparison Pack.aep` hash differs from the measured `Comparisons 01.aep`, so name and visual resemblance are insufficient evidence. No other unlinked review-catalog source AEP matched any frozen technical-project hash. This checkpoint required no AE launch or render.

## Registry-gap technical inspection and linking checkpoint

The remaining source-bound registry gap was processed through the existing dual-pass capacity lab without rendering. Twenty-four exact source AEPs completed static parsing and native AE inspection with exact agreement after two evidence-preserving fixes: AE folder-segment whitespace is normalized only for reconciliation, and sub-frame floating-point boundary noise is excluded from simultaneous-activation peaks. The frozen batch covers 1,482 compositions and 951 editable text fields; all source hashes remained unchanged.

The portable technical index now contains 56 distinct source projects, 5,408 compositions and 4,029 editable text fields. A cross-batch filename collision between two different `Photo Slideshow.aep` sources is preserved with the deterministic project ID `photo-slideshow-17f1e9a2`; neither source overwrites the other. Twenty-four catalog families are now bound by exact source SHA-256. The 46 newly linked scenes present in the current VisualTask comparison are explicitly `unreviewed` at the clip-to-composition stage, distinct from four reviewed-but-ambiguous mappings and 23 verified mappings. Project envelopes remain evidence only and cannot authorize fillability.

`history-slideshow-envato` remains the sole project-unlinked family (14 clips) because the saved intake note labels its relationship to `07-history-slideshow` as probable but unconfirmed. No name-based or preview-based substitution was made. The five-case matching accuracy batch still passes after rebuilding its source-bound report.
