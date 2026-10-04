# Job 6 — Candidate admission, diversity, ordering and display

## One job

Identify precisely where good candidates disappear and weak/repeated candidates
enter or dominate the slate.

## Evaluate separately

1. Eligibility and scope filtering.
2. Structured capability admission.
3. Feasibility and unresolved native fit.
4. B-roll/no-template routing.
5. Family/variant deduplication and diversity.
6. Relevance ordering.
7. Candidate display limits and focused-review sampling.

For every reviewed task used, produce the complete candidate lineage: eligible
catalog families, admitted candidates, rejected reasons, ordered rows, displayed
rows and editor response. Locate expected slideshow, portrait/documentary intro,
comparison, screen/document, timeline and evidence families when the editor
called for them.

## Required outputs

- `reports/astra-root-cause/06-candidate-pipeline.md`
- `reports/astra-root-cause/06-candidate-pipeline.json`

The JSON must classify each failure as `not_in_catalog`, `metadata_gap`,
`contract_gap`, `admission_error`, `feasibility_unknown`, `ordering_loss`,
`display_loss`, `family_duplication`, `forced_template`, or another explicitly
defined type.

## Acceptance

- Retrieval, admission, ordering and display are never collapsed into one score.
- Historical editor choice does not admit a new-story candidate.
- “No template” remains a valid correct outcome.
- No code changes are made.

Stop after Job 6.
