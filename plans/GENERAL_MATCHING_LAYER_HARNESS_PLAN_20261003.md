# General Matching Layer Harness Plan — 2026-10-03

## Objective

Make the matching harness enforce one reusable StoryPackage-to-visual-routing system. Current-document work may supply tests, review evidence and calibration findings, but it must never become the runtime product boundary or silently introduce story-, subject-, artist-, beat- or package-specific matching behavior.

## Required stages and acceptance checks

1. **Declare the product boundary**
   - Add a machine-readable general-matching contract whose input is any validated supported StoryPackage.
   - Acceptance: the contract forbids runtime story identifiers, prior-story decisions admitting or ordering candidates, and unreconciled task feedback becoming a global rule.

2. **Make generality the first harness gate**
   - Insert a `general_matching_contract` stage before documentary baseline reconciliation.
   - Acceptance: a missing, stale or failed generality receipt becomes the first blocking stage; later fixture stages cannot hide it.

3. **Prove the same path across packages**
   - Bind Apollo, Year Seventeen and Future adapter/task receipts as regression/calibration evidence. Future is not held out after being used to tune semantic splitting and retrieval.
   - Acceptance: package IDs are distinct, adapters and tasks agree, every narrator claim is routed, and selection/rendering remain false.

4. **Require a genuinely untouched acceptance package**
   - Run a later user-supplied StoryPackage that was not used to write or tune the current rules.
   - Acceptance: the first run uses the same adapter, splitter, handoffs and retrieval path with complete routing and no story-specific code change. Until then, the harness reports `general_matching_contract` as its first blocker.

5. **Prove runtime neutrality**
   - Check the generic StoryPackage adapter, semantic splitter, structured matcher and candidate-gallery source for fixture package IDs.
   - Acceptance: generic runtime modules contain no Apollo, Year Seventeen, Future or known fixture-beat identifiers.

6. **Enforce evidence scope**
   - Keep editor notes, prior selections, admissions, B-roll rulings and exceptions scoped to their exact story/task unless a separate reconciliation produces reusable capability evidence.
   - Acceptance: the structured gallery states that legacy job bindings cannot admit candidates; task-scoped admissions remain visibly task-scoped and unvalidated.

7. **Update Story/Matching responsibilities**
   - Story owns exact meaning, spans, entities, cohorts, values, obligations and continuity. Matching owns generic semantic moment derivation, structured capability admission, candidate ordering, media pairing and sequence routing.
   - Acceptance: neither layer selects templates for a named story in reusable runtime code.

8. **Regression and fail-closed verification**
   - Extend harness tests for stage order, package independence, source neutrality and evidence scoping.
   - Acceptance: the harness and cross-story suites pass; corrupting any generality invariant blocks the harness.

9. **Mandatory continuation and objective reconciliation**
   - Reconcile the canonical general-matcher objective and task list before every harness run. Every task declares its owner, dependencies, user-input requirement, status and completion receipt.
   - Acceptance: while any objective task remains and no explicit user decision, authorization boundary or external user action is required, the harness emits `continuationRequired: true`, names the next ready task and blocks the general-matching stage. Completing one routine task or reporting status cannot authorize a stop. The harness may emit `stopAllowed: true` only when the objective is complete or a task explicitly requires user input. Every receipt also names the current dependency owner as `you`, `data`, `story`, `matching` or `none`; a ready non-user task takes precedence over an unrelated user-review wait.

## No-deviation assessment

This is a harness and matching-system correction. It does not select a template, modify a template, create a visual or authorize rendering.
