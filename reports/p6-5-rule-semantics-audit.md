# P6.5 matching rule-semantics audit

Status: **repairs completed; see `reports/p6-5-rule-repair-receipt.json`. P7 acceptance still requires a new untouched package.**

This audit examines the 6 review principles and 10 mandatory review rules in
`grammar/general-matching-layer-contract.json` against their enforcing code and
tests. It distinguishes declaration checks from behavioral enforcement.

## Root systemic finding

`matching_contract_gate.py` and `matching_harness.py` verify that every named
rule is present and `true`. They do not prove that runtime behavior preserves
the rule's modal meaning or scope. Therefore an implementation and its test can
agree on the same incorrect interpretation, as happened when “may use no
template” became “must use no template.” A declaration receipt is necessary,
but it is not a behavioral proof.

## Rule matrix

| Rule/principle | Runtime effect | Current proof | Risk | Verdict |
|---|---|---|---|---|
| examples require story-neutral reconciliation | governance; prevents fixture branches | runtime-ID scan and cross-story tests | medium | partial: no automatic scope proof for newly derived rules |
| visual job is not every narration detail | operation derivation and beat splitting | incidental-year, age/duration, plural tests | high | partial: mixed valid visual jobs lack a paired positive test |
| admission follows primary communication requirement | candidate-family admission | incidental-data negative test | high | partial: depends on splitter never leaving two material jobs together |
| capability evidence overrides historical popularity | admission/order boundary | prior-pick invariance tests | low | pass |
| non-template route may be better | route disposition | route planner distinctions | high | fail: generic `templateEligible:false` has no mandatory authority/provenance contract |
| human comments are evidence, not approval | review reconciliation | authorization assertions | low | pass |
| editor status and comment authority separated | review storage/reconciliation | status/comment and no-authorization tests | low | pass |
| primary operation controls admission | structured retrieval | negative union test | high | partial: no fail-closed mixed-payload handoff check |
| secondary operations cannot union admission | structured retrieval | incidental-data negative test | high | partial: legitimate secondary job can disappear if upstream split is wrong |
| incidental numbers do not create data jobs | semantic derivation | year, age, duration tests | low | pass |
| scoped families require matching operation | family suppression | lyric positive/negative test | medium | partial: timeline and other scoped families lack equivalent paired coverage |
| identity routes reject unrelated quantitative semantics | capability admission | transformation negative test | medium | partial: relationship/profile/event operations lack full positive/negative matrix |
| template capacity matches semantic/media demand | feasibility ledger | P4/P5 requirement mutation tests | medium | partial: admission may still show structurally plausible candidates before unresolved capacity is prominent to editor |
| B-roll fallback does not authorize media | route/requirements boundary | P2/P5 authorization tests | low | pass |
| pure rhetorical question may use no template | route disposition | question dual-route plus veto mutation tests | low after `0491c7b` | pass |
| comments never authorize selection/rendering | review artifacts | multiple authorization assertions | low | pass |

## Confirmed blocking defects

1. **Rule declarations are mistaken for behavioral enforcement.**
   The harness proves that a Boolean exists, not that code and tests implement
   its meaning. Each exclusionary rule needs an executable invariant and
   counterexample matrix.
2. **Generic route vetoes lack authority and scope.**
   Any task dictionary can currently set `templateEligible:false`; retrieval
   returns an empty slate without requiring task-scoped editor-reviewed
   evidence. The rhetorical-question invariant repairs one producer, not this
   general consumer boundary.
3. **Primary-only admission assumes perfect upstream splitting.**
   `mixedPayloadReviewRequired` is recorded but not enforced before retrieval.
   If two material visual jobs remain in one task, secondary candidates vanish
   even though the rule says mixed payloads should be split or reviewed.
4. **Counterexample coverage is asymmetric.**
   Several rules test only the unwanted admission case. They lack the paired
   example proving the same rule does not suppress a legitimate neighboring
   use case.

## High-risk but currently contained

- Historical “blank means rejected” evidence remains scoped to candidates
  actually shown in the exact prior review. New-story structured retrieval
  ignores global prior picks. Keep both invariants.
- Task-scoped editor admissions intentionally survive display diversification,
  but the canonical projection must continue rejecting foreign or reconstructed
  admissions.
- Unknown native capability remains unresolved rather than fit or incompatible
  in P5/P6. The UI should make that uncertainty more visible, but this is not
  currently an admission veto.

## Required repairs before P7 restarts

1. Require authority, exact-task scope, and provenance for every intentional
   no-template route; otherwise preserve template eligibility.
2. Fail closed when a task marked `mixedPayloadReviewRequired` contains multiple
   material operations without an exact split/review receipt.
3. Add a behavioral-rule receipt that binds each exclusionary rule to named
   positive, negative, mixed, unknown, and mutation tests—not just a Boolean.
4. Complete paired coverage for scoped timeline families and identity/data
   boundaries across profile, relationship, event, and transformation jobs.
5. Replay the repaired rules on both golden packages, retain Drake as regression
   evidence, then use a new untouched package for P7 acceptance.

All five repair actions are complete. Future and Year Seventeen were replayed
as calibration packages, and Drake was replayed as regression evidence. The
recorded Future boundary variance is not relabeled as exact golden equivalence.
Final P7 quality acceptance remains blocked only on a new untouched package.

No selection, fit validation, or rendering is authorized by this audit.
