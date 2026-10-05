# P3/P4 correction requests

## CR-01 — reconcile P3 unresolved-fact migration with cross-story acceptance

**Status:** required before P5 authorization  
**Owner:** matching  
**Scope:** one P3 follow-up correction; P3/P4 do not require a full redo

### Independent finding

The P3 and P4 stage verifiers pass, and the authorized 179-test stage suite
passes with the two intended P5/P6 expected failures. The complete repository
suite does not pass:

```text
ASTRA_REPAIRED_STAGES=P3,P4 \
STORYPACKAGE_AUTHORITY_ROOT=/private/tmp/patterns-agent-authority-d511-20261004 \
SHARED_ENTITY_ROSTER_PATH=/Users/dwaynetoler/Documents/ChatGPT/Polish/entity_roster/entity-roster.json \
python3 -m unittest discover -s tests

Ran 258 tests
FAILED (failures=1, expected failures=2)
```

Failing test:

```text
tests.test_storypackage_cross_story.StoryPackageCrossStoryAcceptanceTests.
test_apollo_and_year_seventeen_use_the_identical_path
```

The P3 splitter now adds seven `source_fact_unverified` records to the Year
Seventeen excerpt's top-level `gaps`, while the existing cross-story acceptance
test requires `year["gaps"] == []`.

### Required correction

Reconcile the contract explicitly; do not merely delete or skip the failing
test.

1. Determine and document whether `gaps` is the established container for
   unresolved source-fact verification or whether it means structural/coverage
   failure only.
2. If P3 intentionally broadens the established `gaps` contract, migrate the
   cross-story acceptance test to assert the exact general behavior:
   - all and only claims whose accepted adapter status is `unverified` receive
     `source_fact_unverified`;
   - Apollo and Year Seventeen still use the identical general pipeline;
   - task, claim and uncovered-claim invariants remain unchanged;
   - the new state does not authorize selection/rendering and cannot be treated
     as factual verification.
3. If `gaps` is reserved for structural/coverage failures, retain the unresolved
   source-fact state through the existing appropriate unresolved-status field
   instead and restore the cross-story assertion without suppressing evidence.
4. Add a mutation/counterexample proving a supported/verified source claim does
   not receive this unresolved state and an unverified claim cannot silently
   lose it.
5. Update the P3 receipt and combined outcome summary with the chosen contract
   migration and exact hashes. Preserve P0-P2/P4 receipts and immutable evidence.

### Acceptance

- `python3 tests/verify_astra_stage.py P3` passes.
- `python3 tests/verify_astra_stage.py P4` passes.
- The focused P3/P4 suite still passes with only the two P5/P6 expected failures.
- Full discovery passes: 258 tests, zero unexpected failures/errors, two expected
  failures (or the exact increased test count after adding the counterexample).
- No package ID, subject name or fixture-specific exception enters production
  logic.
- No P5 implementation begins in this correction commit.

After CR-01 passes and is independently verified, P3/P4 may be accepted and P5
may be considered at the next editor checkpoint.
