# Astra matching root-cause handoff

## Assignment

Audit the general StoryPackage-to-template matching system end to end. The
editor reports that repeated or irrelevant templates are appearing, obvious
alternatives are absent, task meaning or granularity may be wrong, and upstream
Story/Data/Media inputs may not be giving Matching what it needs. Diagnose the
cause before proposing a redesign.

Use `reports/astra-matching-review-evidence-20261004.json` as the canonical
editor-evidence package. Validate it with
`grammar/astra-review-evidence.schema.json`. Every conclusion must cite one or
more `evidenceId` values and the relevant runtime artifact or code path.

## Evidence summary

- 439 unique normalized records from 24 unique source artifacts.
- 12 current `jayz-drake-settle-it@4` candidate reviews.
- 48 `future-volksgeist@5` candidate reviews, plus three preserved historical
  Future review records from the abandoned implementation.
- 31 recovered beat-review records.
- Earlier matching-output feedback, route decisions, media eligibility notes,
  template/media pairing notes, template capability reviews, treatment review,
  and timing reviews.
- Byte-identical active/abandoned copies are represented as source aliases,
  not duplicated observations.

The package deliberately excludes model judgments, workflow checkpoint logs,
and inventories without editor decisions. Those may be inspected as separate
system evidence, but must not be attributed to the editor.

## Required audit trace

For representative failures and successes, trace the same claim through:

1. StoryPackage narration, beat/claim boundaries, semantics, relationships,
   entities, continuity and authored constraints.
2. Story/Data/Media contract validation and freshness receipts.
3. Matching adapter and semantic task granularity.
4. Template-neutral presentation operation and task requirements.
5. Candidate admission against structured template capabilities.
6. Family coverage, exclusions, feasibility and B-roll fallback.
7. Candidate ordering and review-display limits.
8. The exact candidate slate and editor evidence.

Do not collapse retrieval, ordering and display into one diagnosis. A good
candidate may be absent because it was never admitted, admitted but ordered
below the display limit, excluded by stale capability data, blocked by a bad
task contract, or hidden by family duplication. Identify which stage failed.

## Questions the audit must answer

- Are Story's semantic units coherent visual moments, or are they too broad,
  too small, mislabeled or missing necessary relationships and obligations?
- Are Data values, relation participants, basis/source locators, display
  instructions and receipts complete enough for deterministic task derivation?
- Are Media availability and eligibility constraints represented without
  contaminating template selection?
- Does Matching derive the correct primary presentation operation and retain
  secondary meaning without unioning unrelated families?
- Does the capability registry describe what every approved family can
  communicate, including slot ranges and permitted adjustments?
- Are duplicate families or variants crowding out materially different valid
  choices?
- Are prior editor choices correctly scoped as evidence rather than silently
  admitting or suppressing candidates in another story?
- Is B-roll retained as a valid route instead of forcing a weak template?
- Which failure classes are systematic, and which are story/task-specific?

## Required deliverables

1. A stage-by-stage failure matrix with counts and cited evidence IDs.
2. At least one traced success and one traced failure for each affected layer.
3. A root-cause ranking that separates observed facts from hypotheses.
4. Proposed contract changes for Story, Data, Media and Matching, with owner,
   migration impact and validation fixture for each change.
5. A proposed Matching redesign only after the current failure path is proven.
6. A regression/evaluation plan using Year Seventeen and Future as calibration,
   Jay-Z/Drake as current reviewed evidence, and a future untouched package for
   held-out acceptance.
7. A list of questions that truly require the editor; do not use the editor to
   resolve code, contract or evidence issues the system can determine.

## Safety and scope

- This package is diagnostic evidence, not template selection or render approval.
- Keep story/task-specific preferences scoped unless reconciliation proves a
  reusable capability or presentation principle.
- Do not patch the matcher while auditing. Preserve the failing artifacts first.
- Do not use subject names, package IDs or reviewed beat IDs in runtime rules.
- Keep provider-specific reasoning behind the same provider-neutral contracts.

## Rebuild

From the `matching-layer` worktree:

```text
python3 pipeline/build_astra_review_evidence.py \
  --output reports/astra-matching-review-evidence-20261004.json
```

The exporter preserves source hashes, aliases, JSON pointers and authorization
boundaries. It is deterministic when `--generated-at` is fixed.
