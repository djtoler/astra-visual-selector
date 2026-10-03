# Typed data assignment consumer plan — 2026-10-01

## Scope and authority

The user explicitly authorized a deterministic consumer for the existing StoryPackage-to-data
handoff queue on 2026-10-01. The consumer may read the established StoryPackage and the existing
`hiphop_content_system/data` CSV snapshots. It may not parse numbers from narration as evidence,
invent missing values, modify source data, select a template or authorize a render.

## Required stages and acceptance checks

1. **Bind authoritative inputs**
   - Read the current 28-assignment handoff queue and the validated `year-seventeen@4` package.
   - Bind every consumed CSV and JSON input by path and SHA-256.
   - Fail when the queue/package identity differs or a declared source is absent.
2. **Reproduce typed values**
   - Run deterministic row filters, rankings, aggregates, ratios, differences, top-N operations,
     weighted cohort calculations and chart-streak calculations against the source snapshots.
   - Preserve exact values, units, basis/population, subject and transformation details.
   - Never use narration text as a numeric source and never treat missing data as zero.
3. **Reconcile each queued assignment**
   - Emit exactly one result for every queued task.
   - A result is `resolved`, `partial` or `blocked`; partial/blocked results carry typed gaps.
   - Every required encoding is either backed by at least one typed field or named in a gap.
4. **Validate receipts and stage state**
   - Reject stale source hashes, duplicate/missing task results, receipt-free resolved fields,
     unsupported statuses and any selection/render authorization.
   - `dataHandoffComplete` is true only when every assignment is fully resolved.
5. **Run downstream consumers**
   - Rebuild and validate the data-assignment artifact.
   - Rebuild and validate the matching harness using that artifact.
   - The harness must keep the data stage blocked while any typed gap remains and must never
     advance to production on a partial assignment set.

## Expected outcome

The system should immediately clear every value the current snapshots can prove, while reducing
the data blocker to an exact, source-specific residual gap list. This is a data-layer completion
step only; selection and rendering remain false.

## Execution evidence

- Stage 1: the built artifact binds the queue, `year-seventeen@4`, and four consumed CSV
  snapshots by path and SHA-256. The Spotify and cohort-membership hashes match the snapshots
  declared by the StoryPackage.
- Stage 2: the consumer emitted 79 typed fields from deterministic source operations. It does
  not inspect narration strings for numbers.
- Stage 3: all 28 queued task IDs appear exactly once and all 28 are resolved. Existing
  historical-corpus concentration and counterfactual outputs supplied the previously missing Biz
  Markie share and the approved rank-removal population. Jay-Z's historical-rate absence is a
  typed `unavailable`/null value backed by the coverage contract, not a numeric zero.
- Stage 4: focused tests cover exact values, every required encoding, stale-source rejection,
  residual gaps and authorization denial. The artifact validator passed.
- Stage 5: the matching harness consumed the new artifact and validated. Story and data handoff
  now pass in order; the first blocker advances to `template_media_feasibility`, with
  `productionAllowed`, selection and rendering all false.

The full legacy test discovery ran 655 tests and reported three failures and 17 errors unrelated
to this stage: stale/missing external `ae-template-automation/scene-library/approved/catalog.json`
bindings and an existing Cloudflare configuration-order assertion. The 26 data/StoryPackage/
harness tests directly covering this change all pass.
