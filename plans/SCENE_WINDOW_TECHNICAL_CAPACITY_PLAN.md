# Scene-window technical capacity plan

Date: 2026-09-28
Branch: `codex/treatment-requirements-review`
Activation: inspection and review only; no selection or rendering authorization

## Objective

Measure what a reviewed preview clip can hold during its own native time window instead of assigning the capacity of an entire parent composition. Preserve unresolved status whenever the preview-to-native time transform or the identity of editable media inputs is not proven.

## Stage 1: close narrow legacy-slot classification gaps

Extend the existing technical pass only for composition paths that explicitly identify editable media, including `Edit Media`, `Edit/Media`, and numbered media compositions directly under `Edit Comps/Scene` structures. Ordinary footage remains unresolved.

Acceptance:

- legacy edit-media paths are recognized by narrow path-and-name rules;
- generic `Media 01` compositions outside an edit structure remain excluded;
- capacity remains source-bound and does not infer editability from file type alone;
- unit tests cover both admission and rejection.

## Stage 2: add deterministic window measurement

Expose the already-derived activation intervals for recursive media inputs and editable text fields. Add a reusable measurement function that clips those intervals to a declared composition window and reports:

- window duration;
- total distinct editable media inputs exposed in the window;
- maximum simultaneously enabled media inputs;
- exact editable text fields exposed in the window;
- maximum simultaneously enabled text fields.

Acceptance:

- window bounds must fall inside the measured composition;
- boundary-touching intervals do not count as overlap;
- the result is deterministic from one native report, composition and window;
- no AE launch or render is required.

## Stage 3: bind reviewed clips to exact windows

Create a source-hashed, review-only window-capacity artifact. Promote a mapping to `verified_window` only when the native parent, local start/end transform, and editable-slot classification are all proven. Keep the seven Intro Slideshow slices unresolved because their 154.48-second rendered preview does not map directly to the measured 75.03-second Main composition. Keep any other slice unresolved if the technical pass still cannot establish exact editable inputs.

Acceptance:

- every promoted row identifies one measured composition by project, ID and path;
- every promoted row has an in-bounds exact window and a source-hashed capacity record;
- approximate or unknown time transforms cannot enter exact capacity;
- the Moving Contact Sheets `v3-003a` parent is corrected from SCENE 03 to SCENE 04 even if its final window capacity remains unresolved.

## Stage 4: integrate without activating matching

Teach the coverage ledger and VisualTask comparison to distinguish whole-composition verification from exact window verification. Rebuild derived reports and run focused and full regression tests.

Acceptance:

- exact window capacity removes the missing scene-to-native technical mapping only for verified windows;
- unresolved and ambiguous scenes remain fail-closed;
- report counts reconcile and saved reports reproduce deterministically;
- protected live selection, pairing, media-pick and shotlist artifacts do not change.
