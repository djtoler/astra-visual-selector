# Family-level feasibility fallback

## Problem

The full-task matcher retrieves existing catalog candidates that are absent from the older
task/candidate AE comparison slate. It currently labels every such pair with the generic gap
`exact_candidate_technical_comparison`, even though the approved catalog already carries
family-level simultaneous-slot and text-field capacities. This leaves use-time child checks
looking like missing family evidence and prevents the user's approved family-first workflow.

## Objective

Use existing catalog capability records as a review-only fallback when exact child evidence is
absent or deferred. Preserve exact evidence as higher authority. A fallback may return only
`conditional`, `incompatible`, or `unresolved`; it can never claim native fit, select, or render.

## Stages and acceptance checks

1. Prove the current matcher reports a generic missing-comparison gap for a catalog candidate
   with recorded family capacity.
2. Compare required text fields against the catalog's existing `text_slots`. A measured deficit
   is incompatible; sufficient family capacity remains conditional because native editability,
   exact child mapping, timing and treatment-specific field assignment are deferred until use.
3. Preserve required media kinds and unknown candidate-specific slot mappings as typed use-time
   conditions; never turn story focal counts into template slots.
4. Leave candidates without any usable catalog capability unresolved.
5. Rebuild and replay-validate the full batch and matching harness. Verify that exact evidence
   still takes precedence and that selection, treatment approval, rendering and production stay
   false.
