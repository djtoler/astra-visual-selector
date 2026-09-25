# Media review context and paging plan — 2026-09-25

## Problem

The media review renders each lettered beat side as an isolated brief. A reviewer on
`02-02a` cannot see that `02-02b` is a separate media decision with a slideshow of
mixtape covers, Jet Life material and features. The same page also renders all briefs
at once and names selected templates without showing their existing previews.

## Consumer

`pipeline/ui5-media/index.html` consumes `pipeline/ui5-media/data.json`. The user's
card clicks write beat-scoped media picks; global wrong-person corrections remain a
separate action.

## Required stages and acceptance checks

1. **Bind beat sides.** Derive a stable segment-family key and carry every sibling
   side's quote, declared media direction and selected templates into each brief.
   Acceptance: `02-02a` names `02-02b`, and the sibling direction includes the saved
   mixtape/Jet Life/features instruction.
2. **Reuse existing template previews.** Copy only already-available cached template
   clips and posters into the review bundle; do not create replacement visuals.
   Acceptance: every selected template with an existing cached poster is represented
   in `templatePreviews`, clips retain posters, and missing previews remain labeled.
3. **Page by complete segment family.** Render two numbered segment families at a
   time, keeping lettered sides together. Acceptance: `02-02a` and `02-02b` cannot be
   split across pages; next/previous navigation changes no saved decision.
4. **Show the context beside compact media.** Lay each beat out as a two-column row:
   narration and side-specific intent on the left, compact candidate grids on the
   right. Put an even smaller template-preview grid above the media grid. Display a
   clear companion-side panel with its different quote/media intent. Acceptance: the
   browser consumer renders `.brieflayout`, `.template-grid`, companion context and
   page controls from the built data; mobile collapses to one column.
5. **Regression and consumer run.** Prove the new tests fail before implementation,
   rebuild the real bundle, run the full pipeline suite, then inspect the served page.

No template is selected, rendered or modified by this work. The review only exposes
already-saved candidate choices and already-existing preview assets.
