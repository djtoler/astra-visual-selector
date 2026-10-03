# Mandatory Matching Contract Enforcement Plan — 2026-10-03

## Objective

Make contract enforcement an unavoidable application-level precondition of every registered StoryPackage and matching-layer entry point. A report generated after the work is not sufficient; the entry point itself must fail before processing when its contracts are missing, invalid or stale.

## Required stages and acceptance checks

1. **Create one shared contract gate**
   - Load and validate the general matching contract, matching stage contract and registered-entrypoint contract.
   - Acceptance: invalid product boundaries, permissive story-specific behavior, missing stages or unauthorized selection/render settings raise before pipeline work begins.

2. **Register every supported entry point**
   - Cover StoryPackage adapter/splitter, Story/Data handoffs, candidate gallery, batch matching, route planning and harness build.
   - Acceptance: unknown entry points fail closed; the registry declares allowed review/production modes.

3. **Bind enforcement directly into builds**
   - Every registered `build` function must call the shared gate, not rely on a caller remembering to run the harness.
   - Acceptance: a static coverage test fails when a registered module lacks the exact gate call.

4. **Separate review execution from production promotion**
   - Review-only execution requires valid contracts and remains selection/render false. Production execution additionally requires a current harness audit with every stage passed.
   - Acceptance: the present missing untouched-package gate blocks production but does not erase diagnostic/calibration review work.

5. **Issue a durable enforcement receipt**
   - Return contract hashes, entry point, mode and authorization state from every gate call.
   - Acceptance: matching harness audit contains the receipt; review artifacts may expose the receipt without treating it as fit or selection evidence.

6. **Prevent bypass by omission**
   - Test registry/module parity, contract mutation, unknown entry points, review authorization and production fail-closed behavior.
   - Acceptance: all registered entry points and existing matching regressions pass.

## No-deviation assessment

This is application-level workflow enforcement. It does not add OS-level restrictions, select or modify templates, create a visual, or authorize rendering.
