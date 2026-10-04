# Job 3 — ordered upstream contract audit

Authorization: Job 3 only; stop before Job 4. Frozen production: Matching `1276d0ca1daece81b5b7b38c8b5f5280046e5077`, Story `d5117a6de0fd0c640a336c6f456946ec8b40f319`. Later commits publishing audit documentation do not change the production baseline.

1. Inspect contracts, actual consumers and pinned upstream artifacts. Acceptance: source inventory, pins, ownership and actual handoff paths identified.
2. Measure field coverage and freshness for Story, Data and Media. Acceptance: distinguish contract capability, populated inputs and consumed fields; missing is not zero; media requirements are not availability.
3. Reconcile editor cases across stories with upstream fields and downstream behavior. Acceptance: evidence IDs, reviewed contexts, explicit ownership and limits; no candidate incompatibility inferred from absent assets.
4. Run focused existing validation and stale/missing-input probes without production writes. Acceptance: actual fail-closed behavior and any holes recorded; no new schema or runtime implementation.
5. Publish Markdown/JSON reports with a field-by-field sufficiency matrix, typed owned gaps and minimal proposed deltas. Acceptance: each new field (if any) justified by recurring cross-story evidence, stage omission/reordering rejected, hashes and unchanged production verified, workflow checkpoint recorded.

The general matching task list is context, not authorization to implement its continuation: this audit is bounded by the root-cause job contract. No native rendering, media sourcing or factual invention.
