# Astra root-cause review evidence plan

## Objective

Freeze and normalize the editor's matching-related review history into one
self-contained, provider-neutral evidence package that Astra can use to trace
failures across Story, Data, Media and Matching. This step diagnoses inputs and
outputs; it does not tune the matcher, globalize story-specific preferences,
select templates or authorize rendering.

## Stage 1 — Freeze current editor state

- Read the active Jay-Z/Drake candidate-review artifact from the configured
  review service path.
- Preserve the complete decision objects, gallery hash, revisions and timestamps.
- Acceptance: the package count and SHA-256 match the on-disk review artifact,
  and every non-empty editor comment is represented.

## Stage 2 — Inventory active and abandoned evidence

- Search the active `matching-layer` worktree, the abandoned
  `astra-visual-selector` worktree and the established scene-review storage.
- Include candidate acceptability, beat reviews, route/B-roll rulings, treatment
  reviews, timing reviews, template-capability reviews, media/pairing notes and
  editor feedback.
- Hash every source. Byte-identical mirrors become source aliases instead of
  duplicated evidence.
- Acceptance: the manifest names every ingested source and every skipped or
  excluded class with a reason.

## Stage 3 — Normalize without interpreting

- Emit one record per human-authored decision or note.
- Keep verbatim text, source pointer, story/task/beat/candidate/template/entity
  identifiers where available, status, timestamp and authorization boundaries.
- Tag evidence domain and scope, but do not infer a reusable rule or assign a
  root cause.
- Acceptance: each normalized record resolves to a source file and JSON pointer;
  no model-generated review is labeled as editor evidence.

## Stage 4 — Add diagnostic context

- Join current candidate reviews to the matching gallery when possible so each
  note includes the narration/task requirements and candidate metadata that the
  editor saw.
- Preserve upstream Story/Data/Media gaps separately from Matching outcomes.
- Acceptance: unresolved joins are counted and surfaced; they are never silently
  discarded or guessed.

## Stage 5 — Validate and hand off

- Validate the package against a checked-in schema and invariant tests.
- Produce a short README explaining how Astra should use the evidence: diagnose
  the pipeline, distinguish scoped examples from reusable principles, and return
  proposed contract/component changes with cited evidence IDs.
- Acceptance: deterministic rebuild, stable source hashes, exact record counts,
  JSON Schema validation, duplicate accounting and zero selection/render authority.

## Deferred until evidence review

- No matcher, StoryPackage, Story, Data or Media contract changes.
- No new ranking or admission heuristics.
- No promotion of a comment into a global rule without explicit reconciliation.
