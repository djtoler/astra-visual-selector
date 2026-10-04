# Job 1 — System map and evidence integrity

## One job

Build a verified map of the current Story-to-Matching system and confirm the
review package can support root-cause analysis. Do not judge semantic quality or
propose a redesign yet.

## Inspect

- Every contract, implementation step and evidence artifact in
  `docs/astra-root-cause/REFERENCE_MANIFEST.md`.
- `reports/astra-matching-review-evidence-20261004.json` against its schema and
  every source hash/pointer available in the checkout.
- The actual executable call graph from entrypoint/contract gate through gallery
  and review reconciliation.

## Required outputs

- `reports/astra-root-cause/01-system-map.md`
- `reports/astra-root-cause/01-system-map.json`

The JSON must list each stage, owner, input contract, implementation file and
symbol, output artifact, validation, known bypass risk and downstream consumer.
It must separately map Story creation, Story validation, Matching adaptation,
semantic splitting, requirement derivation, admission, ordering, display and
human review.

## Acceptance

- Every stage resolves to actual code or is explicitly human/manual.
- All 12 current Jay-Z/Drake reviews and 48 current Future reviews are accounted
  for without treating the abandoned mirror as duplicate evidence.
- Machine evaluations are not labeled as editor feedback.
- Any missing org reference is precisely named.
- No production file is modified.

Stop after Job 1.
