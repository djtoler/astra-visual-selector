# VisualTask split detection and independent matching plan

Status: authorized on `codex/treatment-requirements-review`; review-only pilot until the editor accepts the results.

## Required stages and acceptance checks

1. Detect visual-task boundaries after beat extraction.
   - A proposal may keep one task or split a beat into two or more exact, non-overlapping narration spans.
   - Every task must have one visual job, one takeaway, and an exact quote from the source beat.
   - A split is proposed when one developing treatment cannot communicate all required visual jobs; sentence boundaries alone never force a split.
   - Semantic split decisions are model/editor judgments, not people-count, punctuation, duration, or template-capacity heuristics.
2. Review proposed splits.
   - Existing beat facts and prohibitions are preserved.
   - Proposed split boundaries and per-task visual jobs remain review-only until approved by the editor.
   - Rejected or unresolved splits stay as one beat for live matching; no timing is invented.
3. Bind exact timing.
   - Approved quote boundaries bind to measured narration alignment.
   - Task spans must be contiguous, ordered, inside the source-beat speech span, and replayable from source hashes.
4. Match templates independently per VisualTask.
   - Each task queries the existing template bindings using its reviewed visual job and its own identities, count, perceptibility constraints, timing, exclusions, and prior task-scoped decisions.
   - Every candidate records `scope: visual_task` provenance and the exact requirement evidence that admitted it.
   - Candidates may appear in more than one task only through independent evidence; copying the source-beat slate is forbidden.
5. Match media independently per VisualTask.
   - Each task queries the existing Production Ready media resolver using only that task’s identities, quote, required media kind, and candidate-treatment needs.
   - Empty entity/media demand is an explicit result, not permission to inherit sibling media.
   - Group and individual tiers, evidence source, gaps, and missing-media briefs remain separate per task.
6. Preserve continuity without merging decisions.
   - Sibling tasks retain `sourceBeatId`, ordinal, timing adjacency, and optional continuity group.
   - Continuity may influence presentation review but cannot merge candidate pools or approvals.
7. Validate and test omission.
   - A two-task beat must produce two template slates and two media results.
   - Omitting split approval, exact timing, task job, or task-level provenance must fail closed or remain unresolved.
   - No output authorizes selection or rendering.

## Pilot acceptance case

Beat `28-28` must produce:

- `28-28.setup`: threshold/rule setup, no inherited person-media demand;
- `28-28.overlap`: two-set overlap reveal, ten resolved people for independent media retrieval;
- separate template candidates with VisualTask-level provenance;
- separate media results;
- the reviewed 626.66-second boundary preserved exactly.
