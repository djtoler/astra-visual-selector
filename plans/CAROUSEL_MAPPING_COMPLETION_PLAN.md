# Carousel mapping completion plan

Date: 2026-09-30
Status: authorized by the editor

## Objective

Finish the remaining `carousel--review` and `carousel-slideshow` clip mappings using their existing source projects, publisher previews, registered scene clips, technical reports and gated native-test path. Do not redesign either template, replace sample media, or infer one-child-per-clip mappings where the native master combines several child compositions.

## Stage 1 — freeze and reconcile current evidence

- Bind both source AEPs, publisher previews, registered clips, existing native reports and existing Carousel Slideshow native-test renders by SHA-256.
- Reconcile every family clip exactly once, including excluded/pending records without changing availability.
- Acceptance: 19 unresolved Carousel clips and five approximate Carousel Slideshow clips are present; source hashes and media files exist; no verified sibling mapping is overwritten.

## Stage 2 — finish Carousel Slideshow from existing renders

- Reuse the three completed native renders for `2.Final/Render 01`, `Render 02` and `Render 03`; do not render them again.
- Align publisher clips to native time using frame-count, transition-event and motion-geometry evidence that does not depend on the differing placeholder images.
- Require a unique exact frame interval and visual checkpoint for every clip. If a clip remains ambiguous, preserve approximate status and name the conflicting intervals.
- Acceptance: each of five clips either has an exact 25-fps native interval with replayable evidence or a typed ambiguity; exact window capacity is measured only for exact intervals.

Result: clips 002 and 005 have editor-confirmed exact Render 02 windows. Clip 001 is a typed mixed-intro case followed by a Render 03 match. Clips 003 and 004 are verified Render 03 composition matches whose publisher timing cannot be represented by one constant native offset; both require a flagged post retime when selected. The editor review is complete at the approved family level, and no false exact windows are assigned.

## Stage 3 — finish Carousel against its native master

- Use the gated `native_template_test` route to render five 0.2-second low-resolution samples from the original source project's unmodified `Preview Composition`, centered in its five consecutive ten-second blocks. The attempted full 50-second pass was canceled after After Effects estimated more than six hours; preserve that canceled run as evidence and do not repeat it.
- Align all reviewed publisher clips to windows of that master. Because the master layers four native carousel compositions per interval, bind clips to exact master windows rather than forcing terminal-composition inheritance.
- Preserve `carousel--review-012` as superseded, `012a` as pending, and every other catalog availability decision independently from technical mapping.
- Acceptance: all five targeted samples decode and identify the native designs active in each master block; every clip then has a unique exact master window with measured recursive capacity or remains explicitly blocked with the competing windows and evidence.

Result: all five gated native samples completed and verify the original master’s five consecutive blocks covering Carousel 01–20. Per the editor-approved family-level route, the family is ready for matching without forcing every short publisher excerpt to an exact child now. The two prior exact anchors remain exact; clip `012` remains superseded and `012a` remains pending. Every other family member retains its reviewed availability, with exact child, capacity and narration timing required and flagged at use time. Evidence is frozen in `reports/carousel-family-readiness-20260930.json`; this disposition does not authorize rendering or final selection.

## Stage 4 — activate and verify

- Generate a deterministic source-bound batch, activate only exact mappings, rebuild window capacities and coverage, and retain all reports.
- Run focused mapping/coverage tests and the full regression suite.
- Acceptance: no heuristic score authorizes activation; saved reports rebuild identically; the gallery updates from the coverage ledger; no rendering is relabeled final selection.
