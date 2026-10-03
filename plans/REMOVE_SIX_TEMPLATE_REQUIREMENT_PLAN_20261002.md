# Remove the six-template requirement — 2026-10-02

## New rule

There is no minimum template-choice count. Present every distinct valid existing-template option found for the scene, up to the review surface's practical display limit. A route with one or more valid options may proceed. Never pad with duplicates or custom work.

## Stages and acceptance checks

1. Update the project policy and workflow documentation so the prior six-choice rule is explicitly superseded.
2. Update the render gate to validate a non-empty deterministic existing-template slate rather than exactly six choices.
3. Update ordered route planning so template routes with one to five genuine choices are not converted to b-roll or deferred.
4. Update review UI/server validation to accept variable-length non-empty slates.
5. Rebuild route decisions, release preparation and the matching harness in dependency order.
6. Verify that beats 02b, 18 and 28-overlap are no longer blocked solely by choice count, while duplicate/custom padding and empty slates still fail.
7. Keep source-template provenance, supported-control checks, explicit user exclusions, asset rights, native fit, timing, transition and render-release gates unchanged.

No rendering or publishing is authorized by this change.

## Completion receipt

Completed 2026-10-02 in the required order. The policy version is now `existing-options-v3`; the selector and render gate require a non-empty deterministic existing-template slate; the ordered route, carried decisions, release preparation and harness were rebuilt. Current route counts are 32 template review, 9 in-beat b-roll, 0 deferred and 1 post-beat b-roll segment. Tasks `02-02b.currensy_catalog`, `18-18.main` and `28-28.overlap` now proceed with 4, 2 and 5 genuine choices respectively. Focused policy, selector, route, harness and review-server tests pass, including empty-slate, duplicate-padding and custom-padding rejection. Rendering and publishing remain unauthorized.
