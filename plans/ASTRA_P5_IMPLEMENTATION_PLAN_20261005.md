# P5 implementation using the existing batch reconciliation system

Authority: docs/p5-gpt-6-1-sol-handoff/MASTER_PROMPT.md and AUTHORIZATION.json.
Base 9136651 includes independently accepted P3/P4/CR-01 606bef3. P5 only;
GPT-6.1 Sol medium. Stop before P6. No provider, native rendering or custom build.

Existing systems examined: visualtask_matching.template_candidates and its
primary-operation admission; match-trial/candidates.py diversify and _siblings;
visualtask_batch_matching._candidate_fit, comparison/timing/assessment indexes,
_media_result, build/validate and source replay; P2 canonical task projection;
storypackage_data_assignment.validate and field receipts; Data handoff validators;
Production Ready media resolver and typed shortages; native scene mappings,
technical index, optional window capacities/spec links; pilot treatment
capacity-comparison's templateAssessment.satisfied/notRequiredOfTemplate/
missingOrUnverified and approvedAdjustments; unvalidated candidate gallery,
focused queue and prior-review scope. Jobs 3 G06, 4 F06, 5 G05-08/G05-10,
6 C06-02/C06-03/C06-06, and Job 7 capacity/readability/media contrasts establish
the late fit boundary and loss of distinct siblings. Source/gold remain immutable.

The current batch output and treatment inputs are open Python dictionaries with
existing evidence, gaps, templateAssessment and contractEnforcementReceipt
containers; there is no closed replacement ledger schema to introduce. Reuse
those containers under a versioned consumer policy. No source schema delta is
needed. The original gallery remains explicitly unvalidated discovery. It does
not receive P6 ordering/sampling changes. Broad discovery cannot certify fit.

| Required behavior | Existing control / repair | Test-first evidence |
|---|---|---|
| Every variant before reduction | Preserve returned sibling IDs; add full-variant retrieval mode that bypasses diversify, used by batch | Rejected representative + untested sibling; diversify must not run |
| Full requirement ledger | Per-candidate fitAssessment.evidence contains exact task/requirements, duty-by-duty supported/conflict/unknown, and permitted adjustment plan | Duty omission, secondary-only mismatch, named works/slots/framing/dwell |
| No unsupported promotion | Reuse exact fit check, require fresh native mappings and bound reviewed treatment; unresolved facts stay unknown | Native unknown and stale mapping/treatment/Data/Media counterexamples |
| Asset truth stays separate | Existing mediaResult and sourcing gaps; template ledger records media-kind/slot constraints separately | Missing asset does not become template conflict |
| Validated publication fails closed | Existing batch validate/replay plus receipt in contractEnforcementReceipt; exact stage order, full discovery, task/ledger/pool hashes | Missing/stale receipt, truncation, reordered stages, duty deletion |
| Preserve discovery | Full candidate records retained, including unresolved/conflicting variants and admission provenance; content fingerprints replace ID-only fingerprints | Catalog body mutation, source replay and family count changes |

P0-P4 verifiers and 260-test discovery pass before editing (two P5/P6 expected
failures). Save failing P5 tests and frozen target before production changes.
New namespace reports/astra-p5 preserves all old receipt-bound logs. Full suite
must pass with only P6 expected failure. Receipt binds P3 and P4, pinned source
and catalog/code inputs, logs, ledgers and baseline/new differences. Missing
native evidence, source facts and task-bound media stay explicit review blockers;
ledger completeness is not factual verification or native quality acceptance.
Rollback: revert P5 consumers/tests; invalidate reconciled publication, retain
full discovery and prior source-bound evidence. P6 remains unauthorized.

## Final migration and validation

Batch reconciliation uses full variants and never calls family diversification.
The established compact retrieval/gallery remains explicitly unvalidated discovery;
P6 has not connected ordering, sampling or display to the ledger. It cannot be
relabelled as validated fit. The P5 batch validator requires its complete receipt
and exact stage order; source replay is mandatory for validated publication.
`verify_sources=False` is internal structural validation, not publication approval.

Existing measured-index projects use `id`, `resultStatus`, `sourceUnchanged` and
`sourceProjectSha256`. Whole-composition comparisons must replay the exact mapping
and measured composition fields and bind current tasks/requirements. Missing or
stale optional native dependencies and window-only controls stay unresolved.
Treatments reuse `sources`, `approvedAdjustments` and `templateAssessment.satisfied`
with exact duty pointers. Bare reviewed verdicts cannot satisfy unaccounted duties.
Only source-bound approved timing methods become permitted adjustments; all other
adjustments stay unresolved. Native as-is is evaluated without inferring permission.
Source-declared unknown quantities, unverified Data and unknown asset availability
cannot be resolved by a template assessment. Candidate scope is an explicit duty;
legacy job heuristics cannot manufacture a scope conflict for missing Story meaning.

Six prior batch assertions were migrated after their failures were recorded in
p5-integration-probe.log: conditional family/unknown native summaries become
unresolved, a deliberate mismatched aggregate mutation now requests native_fit,
and the 17-family regression retains all 37 candidate variants. Original fixtures,
P0-P4 receipts and original bound logs remain unchanged. No assertion is skipped.
The frozen P5 sibling target passes; P6's ordering counterexample still fails as
expected. New tests include true numeric zero, nested Data source/value mutations,
Media body mutations with stable IDs, canonical P2 task receipt preservation,
actual native-index parser controls, scope/context/hash coverage, and a complete
bound synthetic positive sibling treatment alongside an exact capacity negative.
These controlled positives do not certify the real native catalog.

Final full discovery: 276 tests, zero unexpected failures/errors, one expected P6
failure. Focused P5/batch/P4: 42 tests pass. All P0-P4 verifiers pass. The existing
batch runner replays 1,540 variants (1,466 current; 74 synthetic), preserving all
661 prior candidate representatives and exactly the same Media results. Real
native_fit/adapted_fit claims: zero. Complete JSON ledger artifacts are gzip
transport with deterministic timestamps; the evidence helper decompresses and
validates the original batch objects and exact byte replay using pinned pools.

Workflow review: existing ownership, source binding, review-only and unresolved
native-fit rules already cover this repair; no workflow-memory or source-schema
change is required. Publication integrity is tested; semantic/native quality and
editorial approval remain separate. Next: editor review. P6 is not started.
