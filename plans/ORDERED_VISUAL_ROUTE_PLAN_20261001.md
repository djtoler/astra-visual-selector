# Ordered visual route plan

## Goal

Produce the sequence-planning receipt for all 41 current VisualTasks without selecting or rendering a template.

## Stages and acceptance checks

1. **Bind ordered inputs**
   - Hash-bind the current VisualTasks, technical requirements, full matching batch, prior editor review and timing-feasibility report.
   - Order tasks by exact narration start time and preserve the reviewed split-task order.

2. **Choose a route type**
   - Use b-roll when the prior editor explicitly requested b-roll, when the optional template route has fewer than six valid choices, or when no prior-selected candidate remains in the current conditional set.
   - Otherwise preserve the prior-selected candidates at the front of a six-distinct-choice template review set.
   - Never select a final template in this stage.

3. **Attach timing, continuity and transitions**
   - B-roll is cut to the narration span.
   - Template choices preserve native rendering and carry the existing post-render retime plan when available; missing candidate-specific timing remains a use-time review item, not a fabricated result.
   - Every task receives the user-required short editorial transition.
   - Preserve continuity groups and flag adjacent repeated template families for human review rather than silently changing them.

4. **Validate and connect**
   - Require exactly 41 unique ordered tasks with complete route, timing and transition dispositions.
   - Require exactly six distinct choices for every proposed template route.
   - Require b-roll fallback on every task.
   - Keep selection and rendering authorization false.
   - Make sequence planning pass only when the artifact validates and its bound sources are current.

5. **Regression verification**
   - Test ordering, route rules, prior-decision preservation, six-choice slates, b-roll fallback and authorization boundaries.
   - Rebuild and validate the matching harness after the new receipt is connected.

## Boundary

This stage proposes route types and review slates. Human review remains responsible for choosing a final template from a six-choice slate. Template-specific native checks still run at use time; b-roll still requires exact asset and rights binding before release.
