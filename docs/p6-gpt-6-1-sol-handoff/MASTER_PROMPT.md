# Master prompt — implement Astra P6 with GPT-6.1 Sol

```text
Continue the general Matching-layer repair on:

Repository: https://github.com/djtoler/astra-visual-selector
Branch: matching-layer
Independently verified P5/CR-01 head: 3e0b60502d0e1d10b14ce70e978171c249b21337

EDITOR AUTHORIZATION

On 2026-10-05, after independent verification of P5 and CR-01, the editor
explicitly approved P6 implementation. This authorization is limited to P6:
ordering and review sampling from the shared reconciled P5 ledger. P7,
rendering, template creation, catalog redesign, external provider/API spend and
unsupported schema extensions remain unauthorized.

PRECONDITIONS

1. Pull the latest matching-layer branch and verify HEAD includes 3e0b605.
2. Read AGENTS.md and media_workflows.md completely.
3. Read plans/ASTRA_MATCHING_REBUILD_PLAN.md, especially P6.
4. Read the P5 plan, receipt, CR-01 request and correction evidence; verify the
   P0-P5 stage receipts and strict P5 replay from this checkout.
5. Rerun the focused P5/batch/P4 tests and complete suite using the pinned Story
   authority and shared entity roster paths. Preserve the one frozen P6 failure
   before changing production code.
6. Inventory the existing relevance, family grouping, variant grouping, review
   sampling, gallery construction, review persistence and display-receipt paths.
   Reuse them; do not build a parallel matcher or replacement review UI.
7. Save a stage-mapped P6 implementation plan before editing production code.

P6 OBJECTIVE

Apply deterministic ordering, bounded display and focused review sampling only
after P5 semantic and treatment reconciliation. Every displayed row and sampled
task must reference the same immutable shared ledger. Preserve complete access
to eligible, unresolved and omitted variants and make all display loss visible.

REQUIRED BEHAVIOR

- Read candidate eligibility, fit state, duties, variants, lineage and source
  bindings from the reconciled P5 ledger. Do not reconstruct tasks, candidates
  or fit assessments in the UI or sampling path.
- Exclude incompatible candidates before scoring and ordering. A relevance
  score, perturbation, family quota or historical popularity cannot admit one.
- Never use confidence, probability or score thresholds to authorize selection
  or rendering. P6 orders review evidence; it does not approve candidates.
- Deterministically order the remaining reviewable candidates from persisted
  inputs. Define stable tie-breakers so identical inputs reproduce the exact
  order across processes and checkout roots.
- Display every distinct verified eligible option up to the explicit review
  limit. Do not pad, impose a minimum template count or hide a valid alternative
  merely to increase family variety.
- Preserve native-unknown and unresolved records with their exact flags. They
  must remain accessible and visibly distinct from verified eligible options;
  they cannot be relabeled rejected, exhausted or approved.
- Group materially related variants for exploration only after every distinct
  variant has been reconciled. An incompatible representative cannot suppress a
  viable or untested sibling. Variant groups retain member-level provenance.
- Expose total pool size, eligible/incompatible/unresolved counts, displayed and
  omitted counts, rejection reasons, family order, variant-group membership and
  the remaining full ledger.
- Focused sampling must reference the same task IDs, ledger rows and hashes as
  the complete queue. It must not reconstruct or silently mark tasks reviewed.
- Bind the pool, order, display rows, reviewer sequence and gallery/review
  persistence to an immutable display receipt. Saved feedback must round-trip
  only against the exact receipt/gallery hash and task/candidate identity.
- Existing editor comments remain scoped evidence, not general approval or
  ordering permission. No subject, package, beat or prior choice may enter
  general production logic.
- Preserve the deliberate no-template/B-roll route. Empty eligible display is
  allowed and is not a shortage or permission for custom work.

TEST-FIRST ACCEPTANCE

Write and demonstrate failing regression/mutation tests before the repair. At
minimum prove:

1. The frozen focused-exploration cutoff-tie failure from P0 now resolves
   deterministically without fixture-specific logic.
2. Identical persisted ledger, scores and limits reproduce byte-identical order,
   displayed rows and display receipt across processes and checkout roots.
3. Score perturbation, extreme scores and family quotas cannot admit an
   incompatible candidate.
4. No valid eligible candidate is silently lost before the explicit display
   limit; overflow remains enumerated and accessible.
5. A viable or unresolved sibling survives an incompatible representative and
   remains inspectable with member-level provenance.
6. Native-unknown/unresolved records retain their state through ordering,
   grouping, sampling and review persistence.
7. Focused samples trace to the same full-queue ledger rows and do not create a
   second task/candidate truth or infer human review.
8. Tampering with task route, catalog/version hash, ledger row, score input,
   limit, family order, displayed row, reviewer sequence or feedback identity
   invalidates the display receipt or saved-review round trip.
9. One to many valid candidates and a zero-template/B-roll route are preserved;
   there is no minimum count, padding or score-based authorization.
10. No package ID, subject name, beat ID or prior editor selection enters
    general production logic.

IMPLEMENTATION AND DELIVERY

- Make the smallest repair inside existing supported components and review UI.
- Do not change P5 candidate membership, fit semantics, treatment evidence or
  native/adapted-fit claims merely to make P6 pass.
- If existing representations cannot express the display receipt or ledger
  references, document every exhausted option and the smallest versioned schema
  delta first. Do not implement that delta without separate editor approval.
- Do not perform native renders, alter templates or invent capability evidence.
- Run focused P6 tests, strict P5 evidence replay, every P0-P6 stage verifier and
  the complete repository suite.
- Preserve immutable source/gold/historical evidence and any remaining P7
  expected failures.
- Produce a machine-readable P6 receipt binding the accepted P5 receipt, exact
  inputs, source/catalog/code revisions, outputs, commands/results, unresolved
  states, complete-versus-bounded view evidence and rollback.
- Prove deterministic display replay from a clean independent worktree.
- Commit and push P6 separately with direct links to the plan, receipt, tests and
  principal ordering/display artifacts.
- Report what is next and identify the blocker as `you`, `story`, `data`,
  `media`, `matching` or `none`.

NON-NEGOTIABLE BOUNDARY

No P7 quality evaluation/promotion, rendering, AE/RLIS work, custom visuals, new
templates, catalog redesign or external model execution. Do not weaken P0-P5,
drop P5 ledger rows, hide overflow, convert unknown to rejection, infer editor
approval, or let ranking authorize selection/rendering.

STOP CONDITION

After P6 passes, push its receipt and deterministic complete-versus-bounded-view
evidence, then stop for editor review. Do not begin P7.
```
