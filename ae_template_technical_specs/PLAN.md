# After Effects template capacity lab

Date: 2026-09-27  
Status: technical measurement complete and frozen for all 32 current source projects; two composition-level accuracy pilots complete (Carousel Photo Logo Reveal and randomly selected Text List Carousel)

## Exact objective

Use two independent technical passes only to examine the existing After Effects templates and report exactly what every composition can hold technically.

The three required headline measurements are:

1. **Media inputs** — total independent media inputs and the maximum simultaneously enabled media inputs, reported per composition and per project.
2. **Exact text-field availability** — every editable native text field, with its exact composition/layer identity and technical behavior.
3. **Exact composition durations** — the native duration and work-area duration for every composition.

The work ends with a standalone capacity dataset and a separate accuracy report. It does not update, merge into, or drive any catalog, selector, scene matching, ranking, approval, or rendering system.

## Isolation boundary

- Existing `.aep` and `.aepx` projects are read-only inputs.
- Envato preview videos are not required inputs.
- Existing pipeline code is read-only reference material.
- All scripts, temporary project copies, logs, inspection output, test renders, and reports live under `ae-template-capacity-lab/`.
- No output is written beside a source template.
- No source template is saved, converted, repaired, renamed, or modified.
- No existing catalog, selector, prompt, inspection script, or rendering script is modified.

## Pass 1 — static project extraction

Parse each project without rendering and record every project item, composition, layer, nested relationship, text field, media source, timing range, keyframe, expression, controller, and dependency that the file parser can expose.

This pass produces a fast independent structural inventory. Any unsupported, ambiguous, or parser-incomplete field remains unresolved for Pass 2; it is never guessed.

## Pass 2 — native After Effects inspection

Open a temporary copy of each project through an isolated inspection script and record, per composition:

- composition size, frame rate, duration, and work area;
- editable text layers and their native type, bounds, keys, and expressions;
- distinct footage inputs and where each is reused;
- still, video, audio, precomposition, camera, light, shape, and adjustment layers;
- total media inputs, maximum simultaneously enabled inputs, and sequential inputs;
- nested compositions without double-counting the same underlying input;
- layer in/out ranges, time remapping, keyframes, and expression bindings;
- exposed controllers and effects;
- missing fonts, missing footage, third-party effects, and compatibility failures.

This pass uses After Effects as the native authority but does not render or export video. It compares its observations with Pass 1 and retains disagreements explicitly.

### Absolute maximum media-slot rule

Media capacity is a count of independent media inputs, not a raw AV-layer count. The extractor must:

- expand nested precompositions;
- distinguish independent sources from repeated uses of the same source;
- count separate placeholder instances when each can accept different media;
- avoid double-counting one input reused in multiple layers or nested compositions;
- retain disabled or alternate-state inputs in the structural maximum when they are genuine independent inputs;
- report direct media inputs and recursively resolved leaf-media inputs separately;
- report total independent inputs separately from the maximum simultaneously enabled inputs;
- calculate the simultaneous maximum across the composition timeline using layer enabled state and active in/out intervals;
- report direct-layer and recursively expanded simultaneous counts separately so nesting is never hidden;
- flag a slot as unresolved rather than count it when replacement independence cannot be proven from the native project.

### Exact text-field rule

For every native text field, record the project item, full composition path, layer index, layer name, point-text or paragraph-text type, current text, bounds, enabled state, timing range, keyframes, expressions, font, and any controller binding. Repeated use of one underlying text control is one independent field plus its use sites. Text baked into footage is not an editable text field.

### Exact duration rule

For every composition, record duration, frame rate, frame count, work-area start, work-area duration, and nested use sites. Values are read from the native project and preserved without rounding; human-readable seconds are derived from those native values.

The report distinguishes facts from unresolved questions. A layer's existence does not automatically mean it is safely replaceable. A text layer does not have a proven character limit unless that limit is actually tested.

## Standalone capacity record

Each project and composition receives a source-bound record containing:

- stable project, folder, composition, and layer identities;
- `direct_media_inputs` and `recursive_leaf_media_inputs`;
- `total_independent_media_inputs`;
- `max_simultaneously_enabled_direct_inputs`;
- `max_simultaneously_enabled_recursive_inputs`;
- `exact_text_fields`;
- `composition_duration`, `composition_frame_count`, and `work_area_duration`;
- `parser_observation` and `native_ae_observation`;
- `verified_capacity`: fields on which the two technical passes agree;
- `unresolved`: anything requiring a controlled native test;
- source project hash, AE version, parser version, and extraction version.

No record replaces an existing description or capability file.

## Execution order

1. Build a canonical source inventory, excluding autosaves, duplicate-review copies, converted siblings, and working copies unless one is the only usable source.
2. Hash every source before inspection.
3. Run both passes on a small representative pilot.
4. Confirm the source hashes did not change and review the pilot output.
5. Run the two passes over the canonical inventory, resumably.
6. Freeze the measurement output.
7. Perform the accuracy test separately.

## Separate accuracy test

After measurement is complete, freeze a stratified sample and manually verify it in After Effects. Test:

- text-field counts;
- distinct media-input counts;
- simultaneous and sequential visible counts;
- nested-input deduplication;
- keys, expressions, and time-remap detection;
- missing dependencies;
- false claims that a native layer is a safely replaceable slot;
- missed slots and ambiguous cases.

Report false positives, false negatives, disagreements, and unresolved cases by field. Do not silently correct the frozen measurement while scoring it. Any extractor correction creates a new version and is retested on the same sample.

## Final outputs

- canonical source inventory;
- raw static-parser reports;
- raw native AE inspection reports;
- standalone per-project/per-composition capacity dataset;
- unresolved-case list;
- separate accuracy report;
- proof that all original source hashes remained unchanged.

## Explicit non-goals

- no merge;
- no selector or Astra work;
- no scene-to-template matching;
- no template registry update;
- no modification of existing AE projects or pipeline code;
- no responsive-template engineering;
- no content injection;
- no production render;
- no Envato-preview analysis requirement;
- no template selection or six-choice review.
