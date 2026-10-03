# Render-release preparation plan — 2026-10-02

## Scope

Prepare an auditable handoff from the completed matching layer to render release. This work does **not** render, publish, fabricate approval, or replace any selected existing template.

## Required stages and acceptance checks

1. **Lock upstream inputs**
   - Record paths and SHA-256 hashes for the story handoff, ordered visual plan, editor decisions, data assignments, batch matching result, media-library snapshot, timing plans, and render policy.
   - Fail validation when any recorded input is missing or stale.

2. **Materialize every final route**
   - Produce exactly one release row for every ordered scene, in sequence order.
   - Carry the selected existing-template ID for every template route.
   - Keep b-roll routes as b-roll; do not silently substitute a template or custom visual.

3. **Bind available inputs without inventing editorial approval**
   - Attach typed story/data fields and their receipts.
   - Attach the exact production-ready media candidates and their local delivery paths when present.
   - Do not choose among multiple unreviewed media candidates or claim use rights that are not recorded.

4. **Attach timing and transition requirements**
   - Preserve each narration window.
   - Require post-render retiming for template routes and edit-to-span timing for b-roll routes.
   - Require the user-approved short editorial transition on every scene.

5. **Compute concrete render-release blockers**
   - Template routes block until candidate-specific native controls, slot mapping, text/data layout, and timing are verified for the selected child.
   - Media-demanding routes block until exact assets are bound and asset-use rights are recorded.
   - The full-export human-QC receipt remains pending until an export exists.
   - General b-roll fallback remains valid; absence of a template is never itself a blocker.

6. **Integrate with the matching harness**
   - Replace the generic render-release placeholder with counts and blocker details from the packet.
   - Keep `productionAllowed` and `renderingAuthorized` false until every required receipt is genuinely complete.

7. **Verify**
   - Add tests for route coverage, selection fidelity, stale-source rejection, b-roll fallback behavior, and fail-closed render authorization.
   - Run the targeted matching and release test suites.
   - Record and validate the exact workflow-review checkpoint for this turn.

## Expected output

- `reports/render-release-preparation.json`
- Updated `reports/matching-harness-audit.json`
- A precise list of remaining release blockers grouped by system work versus required human evidence.
