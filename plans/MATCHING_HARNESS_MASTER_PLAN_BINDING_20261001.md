# Matching harness binding to the final documentary system plan

Status: authorized implementation; universal workflow enforcement

## Authoritative inputs

- `content-project-mgr/final_documentary_system_plan.md` is the master architecture and stage order.
- `content-project-mgr/HANDOFF_data_matching_media.md` supplies the concrete data, matching and media mechanisms.
- Prior documentary review is regression evidence, never the product contract.

## Required stages and acceptance checks

1. **General matching contract** — prove the same runtime path accepts distinct StoryPackages, preserves complete narration routing, contains no fixture identifiers in reusable code, keeps feedback scoped and uses structured capability admission. Acceptance: this receipt is first and fail-closed; one completed documentary cannot satisfy it.
2. **Baseline and decision reconciliation** — bind the reviewed project, catalog, mappings and prior decisions as fixture-scoped evidence. Acceptance: selected, dismissed, none-acceptable and unshown states reproduce exactly; omissions fail closed; these decisions do not leak into another story.
3. **Story handoff gate** — require narration spans, claim links, visual intent, explicit/implied entities, cohort references, constraints and continuity on each VisualTask. Acceptance: factual tasks without claim IDs or unresolved entity references cannot enter production matching.
4. **Data handoff gate** — require stable entity/cohort IDs, claim receipts, metric method/caveats and exact typed data fields where a task uses data encodings. Acceptance: missing data blocks only the dependent task; mood/transition tasks without factual data remain eligible.
5. **Template and media feasibility** — apply hard native template requirements, then exact media availability, then pairing/presentation fit as separate verdicts. Acceptance: unfillable options carry typed media briefs; retrieval never becomes selection; prior dispositions remain preserved.
6. **Sequence planning** — reconcile continuity groups, consecutive multi-scene treatments, transitions, pacing, repeated-template cost and deliberate contrast. Acceptance: every scene has an ordered treatment and timing disposition; unresolved sequence conflicts block production publication.
7. **Human review and selection** — ask only about true editorial conflicts, split-task decisions, conditional treatments that automation cannot resolve, and final selection from the non-empty deterministic existing-template slate. Acceptance: previously settled decisions are not re-asked; every override is durable and scoped.
8. **Render/release handoff** — bind exact assets, rights/use decisions, script and VisualPlan versions, render receipts and full-export QC. Acceptance: missing upstream stage receipts, stale inputs or absent human approval block rendering/publication.

## Layer timing

- **Story requirements** apply when VisualTasks are created, before template retrieval.
- **Data requirements** apply before candidate feasibility; typed values are also checked again when fields are assigned.
- **Media requirements** apply twice: rough demand forecasting after outline approval and exact slot/availability checks after a candidate treatment is proposed.
- **Template requirements** apply during candidate feasibility before editor presentation.
- **Sequence requirements** apply after per-task candidate feasibility and before final selection/render.
- **Human review** applies only after automated evidence resolution has exhausted in-scope work.

## Modes

`evaluation_fixture` may run later stages to expose gaps while clearly blocked from production. `production` must pass every preceding stage in order; no waiver, score or UI label substitutes for a receipt.

## Execution persistence

The canonical task list is `plans/general-matching-layer-tasks.json`, and its objective is the reusable matcher—not completion of the current StoryPackage. The harness reconciles that objective and task list on every run, validates task owners, dependencies, user-input dispositions and receipts, and publishes a continuation receipt. Incomplete work with no genuine user-input dependency requires continued execution and names the next ready task. A routine task completion or status message is not a stopping condition. Stopping is permitted only when the objective is complete or when a specific user decision, authorization boundary or external user action is required.
