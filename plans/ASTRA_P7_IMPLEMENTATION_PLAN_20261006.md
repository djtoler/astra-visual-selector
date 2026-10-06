# P7 — source-neutral quality evaluation and controlled migration

Authority: `plans/ASTRA_MATCHING_REBUILD_PLAN.md`, user approval on 2026-10-06. Base commit: `c4b5ce0`, the accepted P6 completion boundary. Accuracy and quality take priority over speed.

## No-deviation assessment

The preliminary Drake GOAT run on `matching-layer` commit `e9cd802` is diagnostic only. It used the general Matching-agent discovery path, not the repaired P5 reconciled-ledger → P6 ordering path, so it cannot serve as P7 acceptance evidence. It collected no editor labels, changed no matching rule, and authorized no migration. P7 regenerates all held-out evidence from this isolated P6 checkout.

## Required stages and acceptance checks

1. **Freeze evaluation contract before held-out exposure.** Persist thresholds, metrics, package/release/catalog/registry hashes, P6 commit, baseline commit and prohibited tuning inputs.
   - Check: mutation of any threshold or input invalidates the evaluation receipt.
2. **Reproduce P0–P6 and frozen calibration controls.** Run stage verifiers, P5 replay, P6 replay, full suite and omission/mutation controls.
   - Check: no expected failure is relabeled as a pass; immutable evidence remains unchanged.
3. **Materialize the untouched package through the repaired path.** Adapt/split Drake GOAT, project it into the canonical task contract, then run complete P5 treatment reconciliation and P6 ordering without prior-story choices or held-out labels.
   - Check: every narration claim has a typed route; every candidate variant is preserved before display reduction; Data/Media/native unknowns remain unknown; no direct discovery-gallery output substitutes for the P5/P6 ledger.
4. **Create a blind, hash-bound editor review packet using the existing review UI/storage.** Do not reveal baseline-versus-repaired identity or metrics while labeling.
   - Check: labels bind exact task/candidate/treatment rows; positive, negative, conditional and no-template judgments are supported; saved feedback cannot authorize selection/rendering.
5. **Compute frozen metrics after review.** Report discovery, admission, reconciled and displayed recall separately; rejection, family/variant coverage, no-template correctness, semantic fidelity, native-evidence integrity and review effort.
   - Check: denominators and unresolved native fit remain explicit; no hidden alternatives or invented time savings.
6. **Controlled migration decision.** Compare repaired path with the frozen baseline and emit an explicit go/no-go proposal.
   - Check: promotion requires every hard gate and agreed held-out threshold; otherwise remain shadow-only with rollback and invalidated downstream receipts.

## Boundaries

- No rendering, template creation, catalog redesign, story-specific matching rules or prior-story admission.
- The exact Story authority commit may be added to the existing allow-list only after its checker passes.
- Do not tune from Drake GOAT before labels are frozen. After its labels are used, Drake GOAT becomes regression material and another untouched package is required for later tuning acceptance.
- Preserve the preliminary run only as provenance; never merge its outcomes into P7 metrics.

## Current execution status — 2026-10-06

- Stages 1–3 passed on `drake-goat@1`: 104 projected tasks reached the repaired P5 ledger; 9,612 discovered variants were retained; 17 explicit non-template tasks received no candidates; all 9,612 candidate fits remained unresolved and zero were promoted or displayed.
- The existing ledger-mode focused-candidate artifact was not usable as an editor packet because it copied all 9,612 unresolved variants. That output is excluded from acceptance evidence rather than being relabeled as a focused review.
- A source-neutral, hash-bound blind packet now shows one exact representative per distinct admitted family, ordered only after P5 admission. Batch 0 contains 20 tasks, 64 candidate cards and four no-template rows; the full ledger and omitted-family identities remain referenced.
- Stage 4 is pending editor labels. Stages 5–6 have not started. No migration, selection or rendering is authorized.
