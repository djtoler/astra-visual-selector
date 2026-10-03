# B-roll fallback harness correction

## Decision

A narration beat does not require a template. B-roll is always an allowed fallback route. The six-choice requirement applies only when the matching system proposes using an existing template; it is not a beat-level completion requirement.

## Required stages and acceptance checks

1. **Policy and contract correction**
   - Record the decision in `media_workflows.md`.
   - Preserve the six-distinct-template gate for any template route.
   - State in the matching stage contract that b-roll is an allowed fallback.

2. **Harness correction**
   - Treat fewer than six template candidates as an informational template-route limitation.
   - Treat unavailable preferred/source-specific media as a quality gap when a b-roll route remains available.
   - Pass template/media feasibility when every beat has either a viable template route or the standing b-roll fallback.
   - Keep selection and rendering unauthorized.

3. **Shortage-view correction**
   - Relabel limited template coverage and preferred-media gaps as nonblocking fallback information.
   - Show that b-roll remains available on every affected beat.
   - Do not imply that a template must be found.

4. **Verification**
   - Add regression assertions for the fallback policy and the corrected first blocking stage.
   - Rebuild and validate the harness and shortage artifact.
   - Run the matching-harness and shortage-view tests.
   - Record and verify the exact workflow review checkpoint.

## Boundaries

- No template is selected or rendered by this correction.
- B-roll fallback does not authorize a custom visual.
- If a template is later selected, six distinct validated existing-template choices are still required before final selection/rendering.
