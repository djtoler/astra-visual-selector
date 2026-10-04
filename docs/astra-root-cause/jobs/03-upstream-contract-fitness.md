# Job 3 — Story, Data and Media contract fitness

## One job

Determine whether Matching receives enough correct, typed and fresh upstream
information to derive the right visual job without inventing meaning or facts.

## Evaluate

- Entity, cohort, relationship and role representation.
- Values, units, relation participants, basis, source-row locator, display and
  rounding instructions, receipts and caveats.
- Evidence/document/quote/lyrics/artifact requirements.
- Media needs versus actual media availability and eligibility.
- Continuity, adjacency, withholding and recognizable identity requirements.
- Registry pins, package revisions, handoff receipts and stale-input behavior.

Use the editor evidence to identify cases where the desired candidate was absent
because upstream meaning/data/media was missing versus cases where upstream was
adequate and Matching failed.

## Required outputs

- `reports/astra-root-cause/03-upstream-contract-fitness.md`
- `reports/astra-root-cause/03-upstream-contract-fitness.json`

The JSON must contain a field-by-field sufficiency matrix and typed gaps assigned
to `story`, `data`, `media`, or `matching`. Include a minimal proposed contract
delta for each proven gap, but do not edit schemas.

## Acceptance

- No layer is blamed for data it does not own.
- Missing data is not treated as zero and missing media is not treated as
  candidate incompatibility.
- Every proposed field is justified by recurring evidence, not one story.

Stop after Job 3.
