# Structured Candidate Retrieval Recalibration Plan — 2026-10-03

## Objective

Stop unrelated beats from receiving the same generic template slate. Retrieve existing-template candidates from each visual task's actual communication contract and the catalog's measured capabilities. Preserve editor feedback, prior choices, provenance, review-only state, and all render gates.

## Required stages and acceptance checks

1. **Freeze and diagnose the current result**
   - Measure repeated slates and candidate frequency before changing retrieval.
   - Acceptance: the saved diagnosis identifies the exact generic-term and unconditional legacy-binding paths responsible for repetition.

2. **Derive a template-neutral presentation contract per task**
   - Use the task's source text, entities, cohorts, typed values, obligations, and presentation operations.
   - Express communication needs such as subject cardinality, structure, staging, readable payload, data relations, and forbidden implications without naming a template family.
   - Acceptance: materially different Future opening moments have materially different contracts; the derivation contains no story IDs, artist names, or template IDs.

3. **Gate retrieval with structured catalog evidence**
   - Test catalog `capability` fields (`structure`, `staging`, `carries`, `readable`, slots, and `implies`) plus narrowly scoped descriptive evidence only where the catalog lacks a dedicated field.
   - Generic words such as `documentary`, `title`, `slideshow`, or `scene` cannot admit a candidate by themselves.
   - Acceptance: every returned card identifies the exact contract evidence that admitted it; `catalog-gap-clean` is not admitted to a generic concept statement by broad wording.

4. **Demote old job bindings to compatible evidence**
   - Prior job bindings may contribute a candidate only when that template also satisfies the current task contract. Story-specific past picks do not become cross-story approvals.
   - Acceptance: no unconditional union of every candidate under a broad legacy job remains.

5. **Preserve and reconcile human review evidence**
   - Back up the current two saved decisions before gallery regeneration.
   - Move the exact `catalog-gap-clean` note to the immediately preceding visual moment as editor-requested, unvalidated candidate feedback; do not convert it into acceptance or selection.
   - Acceptance: both decisions remain present after regeneration, their review and render authorization remain false, and the comment text is unchanged.

6. **Regenerate and compare the gallery**
   - Rebuild through the existing StoryPackage splitter and candidate-gallery pipeline.
   - Acceptance: source coverage stays complete; all cards remain retrieval-only; repeated slates are reported by presentation-contract group rather than hidden; no rendering occurs.

7. **Run regressions**
   - Exercise Future, Apollo, Year Seventeen, task-level provenance, review storage, and the known Future opening cases.
   - Acceptance: materially incompatible templates are absent; task-scoped admissions remain visible; selection/render authorization stays false; existing relevant tests pass or any unrelated stale test is named accurately.

## No-deviation assessment

This change remains inside the agreed matching layer. It does not edit a template, create a visual, select a candidate, or render anything.

## Audit against the original architecture and reference handoff

The original architecture was directionally sufficient about ownership and stage order: Story provides exact spans, claims, entities, obligations, continuity and presentation requirements; Matching evaluates VisualTasks against machine-readable template specs; template, media and pairing verdicts remain separate; retrieval never becomes selection.

Two failures produced the repeated slates:

1. **Specification gap:** the plan did not define an executable admission mapping between Story/VisualTask presentation requirements and the catalog's measured `capability` fields. It also did not explicitly forbid broad descriptive keywords or a shared legacy job from admitting a candidate.
2. **Implementation deviation:** the new-story gallery did not consume the full StoryPackage-derived handoff. It dropped typed values, cohorts, obligations and text/data presentation needs, then unconditionally unioned the old job-binding pool. It also published without a receipt proving the structured feasibility stage ran.

The StoryPackage 0.2 reference documents are not deficient at this boundary; the consumer under-used their fields. This recalibration closes the algorithm gap and binds the gallery to the missing structured-compatibility receipt.
