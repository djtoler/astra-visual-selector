# Exhaustive family feasibility before shortage reporting

## Problem

The full-task feasibility runner asks the existing retrieval consumer for its ten-card review
slate and assesses only those cards. That slate is intentionally truncated and applies a
three-slideshow presentation cap. A task can therefore be reported below six conditionally
feasible families before every family already bound to its visual job has been reconciled.

## Objective

Keep the existing compact review-slate behavior for its current consumers, but let the batch
feasibility consumer assess one representative from every bound existing-template family before
it reports a six-choice shortage. This is review-only evidence; it cannot select or render.

## Stages and acceptance checks

1. Add an explicit exhaustive-family mode to the existing deterministic diversification path.
   Default callers retain the ten-card and slideshow-cap behavior.
2. The full-task feasibility runner uses exhaustive-family mode and assesses every returned
   family representative against story, text, data, media and timing requirements.
3. A test proves the previously truncated `define_terms` job exposes all bound families in the
   feasibility batch while the standard source-beat consumer remains capped.
4. Rebuild and replay-validate the batch and harness. Shortages are recalculated only from
   conditionally feasible families; no incompatible or unresolved candidate counts toward six.
5. Preserve source provenance, family uniqueness, use-time child validation, and false selection
   and rendering flags.
