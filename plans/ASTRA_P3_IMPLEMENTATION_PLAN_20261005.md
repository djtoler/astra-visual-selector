# P3 implementation and existing-system review

Authority: docs/p3-p4-gpt-6-1-sol-handoff/MASTER_PROMPT.md and AUTHORIZATION.json.
Start revision e8be1d6 includes verified P0-P2 5bff115. P3 depends on the exact
P2 receipt; P4 independently depends on P0. Both must pass before a separately
authorized P5. Only gpt-6.1-sol / medium is used.

Existing controls inventoried: StoryPackage 0.2 claim/proposal codepoint spans,
typed values (unit/label/entity/basis), representedBy and display restrictions;
storypackage_splitter's authored proposal and deterministic semantic-unit paths;
P2 canonical handoff projection and source-bound consumers; existing
visualtask_split_proposals closed v1 schema, source hashes, exact complete spans,
reference coverage and review-only flags; heldout_matching_integration's source
reference conversion; immutable Job 2/4/7 diagnostics and both gold exports.
No provider operation or unsupported schema is assumed. The existing v1 proposal
workflow is evaluated using its supported fixtures; it does not pretend to ingest
raw StoryPackage 0.2 or authorize semantic activation. Source facts stay in the
bound inputs/requirements, not in provider-authored takeaway text.

| Acceptance | Existing control / smallest repair | Executable evidence |
|---|---|---|
| Exact rate/value subspan | Materialize authored proposal.span from the bound script or exact covering claim slices; reject invalid ranges or inconsistent source | Frozen P0 rate assertion, P3 Unicode/gap/out-of-range mutations |
| Distinct participants | Count unique display entity IDs in operation/job inference | Duplicate-ref vs true multi-person positive/negative tests |
| Different units/roles do not merge | Existing typed value unit/label/basis/entity and representedBy signatures guard merge; retain coherent rank/cohort and same-payload keeps | Typed split/keep counterexamples and existing splitter suite |
| Lexical counterprobes | Word boundaries for headline; contextual event left; fans alone is not a quantified measure; authored structured job reconciles primary using existing operations | Existing headliner/left-floor/fans diagnostics and renamed subjects |
| Provider cannot mutate facts, select or activate | Reuse closed semantic-split v1 validation, exact quote and reference allocation guards | Existing v1 provider mutation suite plus P3 unknown/selection mutations |
| Meaning/rationale/unknowns survive | Existing claimSpans/values/refs/obligations/continuity and provenance.evidence; existing typed gap channel for unverified source facts; keep provider review-only | Projection/coverage/source mutation tests; shadow cross-story reports |

Baseline failure and controls are written before repair. P3 files and receipt are
separate from P4; parent integrates only stage-owned files. Relevant suites use
STORYPACKAGE_AUTHORITY_ROOT=../patterns-authority at d5117a6. No source/gold/
historical review or catalog observations are edited. P5/P6 failures remain.
Receipt namespace: reports/astra-p3-p4/p3-*. Each receipt binds code/input/output
hashes, exact commands/results, P2 dependency, unresolved states and rollback.

Workflow review: deterministic exact-source materialization and typed merge guards
implement the existing semantic-moment policy. No new renderer, provider runner,
source schema, registry, or semantic activation workflow is introduced. Missing
upstream annotations stay unresolved rather than becoming inferred facts.
