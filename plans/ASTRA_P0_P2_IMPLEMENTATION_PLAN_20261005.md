# Authorized P0–P2 implementation plan

Scope authority: `docs/p0-p2-gpt-6-1-sol-handoff/HANDOFF_MANIFEST.json`.
Session configuration verified from the current turn record: gpt-6.1-sol / medium.
No other model execution, external provider call, rendering, catalog change,
semantic splitting change or ordering change is permitted.

## Preflight and existing-system inventory

- Clean `matching-layer` checkout begins at `309c2b38fcec8bd723b29d10b426ba280191f2a3`.
  Packet parent `5083ba40702181c8c8fa7b53b80d4c009a2aa728` and frozen production
  `1276d0ca1daece81b5b7b38c8b5f5280046e5077` are present. All 14 handoff hashes
  match; Job 3/6 source inventories also match their pinned bytes.
- Story is an isolated checkout at `d5117a6de0fd0c640a336c6f456946ec8b40f319`.
  Set `STORYPACKAGE_AUTHORITY_ROOT` for existing tests. The original dirty Polish
  checkout is read-only and remains untouched. A Unicode-normalization checkout
  issue was corrected only in the newly fetched checkout; leftover bytes were
  preserved outside it.
- Existing `unittest` suites, normalized evidence validation and exact-context
  sidecars supply the test/evidence harness. Reuse `tests/test_matching_agent_contracts.py`
  for immutable input preflight fixtures, `tests/test_storypackage_data_assignment.py`
  for typed-field mutations, and splitter/gallery/focused-review tests for consumers.
- Reuse `matching_agent_contracts.preflight`, `storypackage_adapter.build`,
  `storypackage_splitter.build`, `storypackage_data_assignment.validate`,
  `storypackage_matching_handoff`, `visualtask_requirements`,
  `visualtask_matching.presentation_contract/template_candidates`,
  `storypackage_candidate_gallery.build` and `focused_candidate_diversity.build`.
  Their registered contract gates remain in place.
- The richer upstream matching handoff expresses text, focal counts, caveats and
  media needs, but its only audited instance is an older package revision.
  It cannot be repinned or copied as current task coverage. Data assignments
  already express selectors, columns, transforms and typed absence. The general
  path currently treats optional file presence as coverage. Media inventory and
  delivery validators express provenance/lifecycle, not general task coverage.
- Existing gallery/focused code duplicates task projection. Reuse the existing
  handoff module and proposal fields for a versioned shared projection; do not
  create another architecture. Retain legacy artifact readers with unresolved
  status. Unknown transformations/supply cannot become verified bindings.

## Executable stage map

Receipts and calibration/diff outputs go in `reports/astra-p0-p2/`, alongside
immutable audit evidence. Regression tests use the existing unittest harness.
Every receipt records commands/results, exact input/output digests, versions,
unresolved states, upstream receipt digest and rollback. A stage cannot pass on
an omitted, mutated or failed predecessor. Preserve all frozen audit/gold bytes.

| Stage / acceptance | Existing component | Executable check | Receipt evidence |
|---|---|---|---|
| P0 exact sources, evidence IDs, author scope, catalog | audit manifests, normalized evidence validator, context sidecar, C.load | `test_calibration_integrity`; digest/context/omission mutations | calibration manifest, source inventory, P0 receipt |
| P0 empty coverage | preflight + `_requirements` | hashed `{}` Data/Media regression; audited 73/104 demand counts | baseline outcomes and diff |
| P0 stale source/adapter/body | adapter receipt + splitter/gallery | stale digest, mutated body and omitted receipt regressions | baseline failure reasons |
| P0 routes and field loss | gallery + focused consumer + richer handoff | all 12 audited route tasks; obligations, continuity, quote, needs and admissions propagation | baseline consumer outcomes |
| P0 subspan/scope/variant | splitter, scope predicate, family diversification | exact rate-subspan, timeline scope, suppressed sibling fixtures | preserved failures pending P3/P4/P5 |
| P0 exploration tie | focused diversity, frozen reviewed queues | replay 59 distinct tasks, confirm 58 cutoff ties and admitted-position sensitivity | tie fixture pending P6; no ordering repair |
| P1 hashed-empty and task coverage | preflight/requirements, assignment validator, delivery validator | empty/foreign package/foreign task/missing field handoffs remain typed gaps | P1 outcomes bind P0 |
| P1 field source/receipt/value freshness | existing assignment source receipts | field digest mismatch, wrong source locator, stale bytes, value mutation, unavailable-to-zero rejection | negative mutation results |
| P1 measured zero and legacy | existing selector/column/transform controls | valid measured-zero positive; supported old formats readable but unverified content unresolved | explicit binding/gap states |
| P1 source/adapter freshness | adapter fields and immutable receipts | stale input/body/receipt rejection at consumption boundaries | source/output hashes |
| P2 shared contract/version/source | existing matching handoff module + proposal fields | requirements/gallery/focused identical projection; missing/stale/omitted/mutated projection and reconstruction rejection | P2 outcomes bind P1 |
| P2 route retention/reason | template candidate route gate + route-plan consumer | 12 empty routes; distinguish intentional route, discovery gap and feasibility unknown | consumer diff |
| P2 quote/question | explicit obligations and source speaker fields | exact required quote text and attribution survive; explicit duties resolve rhetorical heuristic conflict | source-bound projection |
| P2 Media/cohort demand | obligations.mediaNeeds and cohort representedBy | required needs survive each consumer | projection + typed gaps |
| P2 prior-story exclusion | ignorePriorSelections + task-scoped admissions | foreign package/source admission rejection; prior picks cannot change slate/order | mutation results |

## Order, testing and boundaries

1. P0: add assertions/fixtures first. Run them against a separate frozen Matching
   checkout and save actual failures, not historical PASS labels. Validate
   calibration mutations and immutable inputs; run relevant existing suites;
   commit/push P0 separately only when its complete gate passes.
2. P1: strengthen existing content/freshness validators and consumer binding
   policy. Run the P0 regressions assigned to P1, legitimate-zero positives and
   mutation controls; then the complete relevant contract/Data/adapter suite.
   Commit/push separately after receipt verification.
3. P2: shadow the canonical projection against old consumers, migrate all three
   together, then retire duplicate projection code. Run route/quote/media/
   admissions/source-binding tests and the complete relevant gallery/focused/
   requirements suite. Commit/push separately and stop for editor review.

Use saved audit scores when ordering context is needed; do not invoke the local
embedding model under this session's model restriction. An unavailable original
input or unsupported required control is a named blocker, never permission to
reconstruct evidence or widen an upstream schema. Exact schema/operation
extensions beyond the authorized stage outputs require a concrete gap review.

Rollback uses stage commits in reverse order and invalidates dependent receipts.
It never restores false verified coverage or overrides corrected route gates.
P3 subspan semantics, P4 scope/capability, P5 variant/treatment fit and P6 ordering
remain frozen regression cases; passing P0–P2 will not claim they are repaired.

Workflow review: the decisions above are already covered by `media_workflows.md`
and its P0–P2 authorization. No reusable workflow change is introduced.
