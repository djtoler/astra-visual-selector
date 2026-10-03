# Mandatory Matching Contract Enforcement Result — 2026-10-03

## Outcome

Contract checking now runs inside every registered StoryPackage and matching-layer build entry point. Running a module directly no longer avoids contract validation.

## Mandatory gate

The shared gate validates:

- the general matching-layer product boundary;
- the complete ordered harness-stage contract;
- the exact registered entrypoint list and permitted modes;
- disabled selection and rendering in review mode;
- the complete, current harness before any non-harness production entry point may run.

Unknown entry points and invalid or missing contracts fail before story/task processing begins. Each gate call returns a receipt bound to the three contract hashes. The harness validator rejects a missing or stale enforcement receipt.

## Registered coverage

- StoryPackage adapter and semantic splitter;
- Story-to-Matching and Story-to-Data handoffs;
- typed data assignment;
- structured candidate retrieval;
- per-task and full-batch matching;
- ordered route planning;
- held-out integration and matching-accuracy evaluation;
- harness build itself.

The registry coverage test inspects every registered source module and fails if its exact gate invocation is absent.

## Modes

- `review_only`: contracts are mandatory; selection and rendering remain false.
- `production`: requires the complete current harness. The generality gate now passes after `jayz-drake-settle-it@2`; production remains blocked by the separate render-release handoff.

## Verification

- Harness build and saved-audit validation passed.
- 74 mandatory-gate, harness, cross-story, StoryPackage, structured matching, data-handoff and held-out integration tests passed.
- The older declarative matching-accuracy batch remains independently fail-closed on pre-existing stale frozen source hashes; those hashes were not silently rebound.
- No template was selected, changed or rendered.
