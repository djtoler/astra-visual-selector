# Matching Layer operating instructions

## Objective

Everything in this branch serves one reusable Matching layer that can accept any validated supported StoryPackage. Never optimize runtime behavior for the current story, subject, beat ID, or editor example.

## Execution harness

- Enforce `grammar/general-matching-layer-contract.json`, `grammar/matching-harness-stage-contract.json`, and `grammar/matching-entrypoint-contract.json` at every registered entry point.
- Reconcile `plans/general-matching-layer-tasks.json` and the general objective before every run.
- Continue authorized work until the objective is complete or a specific user decision, authorization boundary, or external user action is required.
- Every status report must name the current blocker as exactly one of: `you`, `data`, `story`, `matching`, or `none`.

## Ownership

- Story owns narration claims, semantic beat boundaries, intent, entities, relationships, continuity, and factual storytelling constraints.
- Data owns stable entity/cohort resolution, metrics, values, methods, caveats, and claim receipts.
- Media owns asset availability, provenance, rights, identity/framing metadata, and processing state.
- Matching owns template-neutral VisualTask consumption, structured candidate admission, template/media feasibility, sequence/timing/transition planning, and review receipts.

Story and Data may supply binding inputs; Matching decides whether a template can express them. Matching must not invent missing Story meaning, Data facts, or Media availability.

## Generality and evidence

- Prior editor choices are scoped evidence. They may validate, reject, or order candidates only for the same story/task unless an explicit reconciliation creates a reusable capability or presentation rule.
- A prior story's decisions cannot admit, suppress, or order candidates for a new story.
- Candidate admission requires structured capability compatibility. Legacy job labels alone cannot admit a template.
- All relevant approved template families must be considered by the visual job they can perform, regardless of category name.
- B-roll is always a valid fallback; no beat is required to use a template.

## Shared registry

Use `grammar/entity-roster-source.json` and the digest-pinned shared registry. Do not restore a second local entity authority. Preserve unresolved entities as typed gaps.

## Legacy branches

Claude-authored Matching implementation not demonstrably required by this branch is stale. Leave it unchanged and do not merge, refresh, or reconcile it merely because it exists. A retained legacy component must have an explicit executable or contract dependency and pass this branch's provider-independent tests.

## Render safety

This branch does not authorize rendering. Preserve existing template provenance and controls. Custom work requires complete evidence-backed exhaustion of existing options and explicit user approval.

## Claude Desktop and Fable CLI independent-audit branch

This `fable_analysis` branch is an independent audit rooted at Matching commit
`1276d0ca1daece81b5b7b38c8b5f5280046e5077`. Follow
`docs/astra-root-cause/MASTER_PROMPT.md` and its execution policy. Do not inspect,
merge or use Astra Job 1–8 outputs from the later `matching-layer` branch until
the independent Fable audit is complete. Preserve production code and evidence;
each numbered job publishes audit outputs only and stops for the editor. Claude
Desktop directly runs Jobs 1 and 3–6. For Job 2, Claude Desktop invokes Claude
Fable 5.1 through the Claude CLI at Medium. For Job 7 and separately for Job 8,
the editor must explicitly choose direct Desktop or Desktop-managed Fable CLI
at Medium; there is no default. A missing selection or wrong execution mode
must stop rather than taking another mode's job. Both modes commit and push each completed job to
`fable_analysis` and return direct GitHub links to their outputs.

Use `docs/astra-root-cause/CORRECTION_REQUESTS.md` as the only correction-request
file. An `ACTIVE` correction blocks the next job. Resolve it first, preserve the
entry as history, publish the correction and return that canonical file's link.
Never create a separate per-job correction file.
