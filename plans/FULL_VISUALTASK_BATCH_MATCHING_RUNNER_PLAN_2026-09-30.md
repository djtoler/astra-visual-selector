# Full VisualTask batch matching runner plan

Date: 2026-09-30
Status: implementation plan; review-only matching, no selection or rendering

## Boundary

Refactor the existing VisualTask template and Production Ready media consumers into one reusable batch entry point. The current documentary is a regression fixture only. Runtime code must accept any supported versioned StoryPackage, VisualTask artifact, and technical-requirements artifact without story IDs, beat IDs, issue IDs, or review prose in Python.

## Required stages and acceptance checks

1. **Validate and bind the versioned inputs.**
   - Accept a schema-versioned request naming a StoryPackage, VisualTask artifact, technical-requirements artifact, and template bindings.
   - Fail closed on unsupported versions, non-review-only inputs, duplicate tasks, task/requirement scope mismatch, or task-count mismatch.
   - Bind every source by path, size, and SHA-256.

2. **Match every VisualTask independently.**
   - Reuse the established template candidate consumer and Production Ready media resolver.
   - Process the complete VisualTask artifact in deterministic task order; do not filter to one source beat.
   - Preserve task-level candidate provenance and prevent media inheritance between sibling tasks.

3. **Keep template fit and media availability separate.**
   - Keep semantic retrieval as candidate discovery only. For every retrieved candidate, compare the exact task/candidate technical mapping and native capacity against the typed task requirements, timing plan, project availability evidence, and any exact editor-reviewed treatment assessment.
   - Emit deterministic candidate fit states (`native_fit`, `adapted_fit`, `conditional`, `incompatible`, or `unresolved`) without scores, ranking, selection, or rendering. Missing treatment-specific evidence remains `unresolved`; a diagnostic timing plan that still needs editorial pacing review remains `conditional`.
   - Aggregate the task verdict existentially without choosing a candidate: native fit if any exists, otherwise adapted fit if any exists, otherwise conditional if any exists, incompatible only if every retrieved candidate is incompatible, and unresolved otherwise.
   - Emit a `mediaResult.availabilityVerdict` based only on the typed media requirement and Production Ready lookup.
   - Preserve reviewed missing-media briefs as typed conditional gaps; never convert retrieval into approval, selection, pairing, or fillability.

4. **Produce a replayable review-only artifact.**
   - Keep `selectionAuthorized` and `renderingAuthorized` false.
   - Validate task coverage, independent provenance, allowed verdicts, typed conditional gaps, source freshness, and deterministic replay.

5. **Prove generality.**
   - Run the complete current documentary fixture through the same API.
   - Run an unrelated synthetic StoryPackage with different story/task IDs through the same API.
   - Assert that production Python contains no fixture story/task IDs and that both inputs require no source-code change.
   - Cover native, approved-adapted, conditional, incompatible, and unresolved candidate outcomes with deterministic synthetic evidence, while retaining the current 41-task fixture as a conservative regression.

## Explicitly out of scope

- Semantic splitting or VisualTask generation.
- Candidate selection, treatment approval, media pairing, activation, or rendering.
- Editing `media_workflows.md`, workflow review logs, live mappings, or global reports.
