# Declarative matching-accuracy evaluator plan

Date: 2026-09-30
Status: implementation plan; review-only evaluation

## Boundary

Replace the evaluator's five documentary-specific code branches with a generic assertion engine. Documentary IDs and expected values remain only in versioned fixture requests and frozen observations. Add an unrelated held-out StoryPackage harness whose unavailable upstream stages remain explicitly pending.

## Stages and acceptance checks

1. **Define the declarative request.**
   - Each source is path/hash bound and may be required or explicitly pending.
   - Each case declares a source record, expected label, and generic assertions.
   - No case ID, beat ID, candidate ID, or review phrase appears in evaluator Python.

2. **Implement generic record resolution and assertions.**
   - Resolve object/list paths and optional equality filters without domain-specific branches.
   - Support only closed, tested operators: equality, inequality, membership, truth, falsehood, length bounds, and distinctness.
   - Unknown operators, ambiguous paths, malformed assertions, and stale required sources fail closed.

3. **Preserve review-only boundaries.**
   - Output keeps selection and rendering authorization false.
   - A case with an unavailable optional source is `pending`, not pass or fail.
   - Summary reports pass, fail, and pending separately; pending prevents an all-passed claim.

4. **Convert existing evidence into fixture data.**
   - Reuse the frozen five-case report as observations.
   - Express all five expected outcomes as data assertions in the batch request.
   - Preserve the existing report fields needed by current regression tests.

5. **Add the unrelated held-out harness.**
   - Bind an unrelated versioned StoryPackage.
   - Declare semantic-split and template-fit cases against optional future outputs.
   - Verify the harness runs today with those cases pending and can score later without evaluator-code changes.

6. **Test and verify.**
   - Existing five cases pass via the generic engine.
   - Stale sources and invalid operators fail closed.
   - Production evaluator contains no documentary/held-out fixture identifiers.
   - Evaluation is deterministic and performs no matching, selection, or rendering.
