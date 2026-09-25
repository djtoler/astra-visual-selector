# Astra narration-to-visual selector — design package

Design phase only. Nothing here implements the production system, touches an After Effects project, renders anything, or downloads a template. The Google video-understanding study was not rerun.

**Status: awaiting review and approval before implementation.**

## Read in this order

| | Document | What it covers |
|---|---|---|
| 0 | [`00-reconciliation.md`](00-reconciliation.md) | **Start here.** What changed once the project files became readable, including one of my findings your rules override. |
| 1 | [`01-current-state-audit.md`](01-current-state-audit.md) | What exists, what is reliable, what conflicts. |
| 2 | [`02-decision-method.md`](02-decision-method.md) | The full sequence in plain language, no jargon. |
| 3 | [`03-decision-model.md`](03-decision-model.md) | Stages, gates, your ten global rules, priority handling, confidence, escalation. |
| 4 | [`04-evidence-synthesis.md`](04-evidence-synthesis.md) | What the 628 annotated units show, tiered by how far each finding travels. |
| 5 | [`05-demonstrations.md`](05-demonstrations.md) | The method on six of your thirty passages, each checked against what you actually said. |
| 6 | [`06-coverage-and-gaps.md`](06-coverage-and-gaps.md) | Coverage against the approved catalog. The gaps are fields, not template families. |
| 7 | [`07-evaluation-plan.md`](07-evaluation-plan.md) | Seven test suites, all with fixtures that now exist. |
| 8 | [`08-implementation-plan.md`](08-implementation-plan.md) | Ten stages. Stage 0 is done; the rest await approval. |
| 9 | [`09-open-issues.md`](09-open-issues.md) | What needs your judgement. |
| 10 | [`10-full-run-review.md`](10-full-run-review.md) | **The full run.** All thirty passages end to end, the four misses, and the ten defects extending the sample exposed. |

## Prototype

Working, authorized, and self-contained. `prototype/run_slice.py` runs all thirty passages: contract, retrieval, per-shot slates, gates, decision. It writes thirty JSON files and a readable report to `prototype/out/`. Rules resolve from `rules/base-rules.snapshot.json` plus `rules/local-overlay.json`; nothing is written to the project and no rule is global scope.

## Schemas

| File | Deliverable |
|---|---|
| [`schemas/visual-contract.schema.json`](schemas/visual-contract.schema.json) | Timed visual contract |
| [`schemas/template-capability.schema.json`](schemas/template-capability.schema.json) | An **extension** to your existing `selectionContract`, adding only what nothing currently records |
| [`schemas/style-profile.schema.json`](schemas/style-profile.schema.json) | Dark cinematic profile, to be populated from your two rendering-rules documents |
| [`schemas/candidate-output.schema.json`](schemas/candidate-output.schema.json) | Four ranked treatments, winner, reasoning, flags |
| [`schemas/correction-record.schema.json`](schemas/correction-record.schema.json) | Correction capture, scoping, promotion, rollback |

Filled examples for the contract and candidate slate are in [`examples/`](examples/).

## Data

| File | Contents |
|---|---|
| `data/derived-priors.json` | Durations, readable holds, entity capacity, evidence obligations, change budgets, recomputed from 628 units |
| `data/backtest-results.json` | Leave-one-reference-out results and the ambiguity ceiling |
| `data/derived-contract-clusters.json` | 16 clusters with unit ids attached, replacing the unjoined pattern layer |
| `data/template-capability-scan-raw.json` | Slot, colour-control and comp structure parsed from 180 `.aep` files |

## Four things to know before reading

**Narration does not determine treatment, and the numbers say so clearly.** Two passages with an identical narration contract land on the same treatment 44.9% of the time, against a 34.2% chance rate. Knowing which media exist raises it to 67.7%. This is the empirical case for the architecture you already specified, and it means retrieval quality matters more to output than scoring does.

**A four-candidate slate cannot be the top four scores.** Every ranking tested was worse than always proposing the four most common treatments once past the second candidate. The slate has to be constructed, which your `four_distinct_options` rule already says better than my original wording did.

**Your rules corrected one of my findings.** I concluded from the reference corpus that spatial treatment rarely proves anything. Your `spatial_relationship_first` rule says the opposite for gap, distance and rank-loss claims, and you are right — the corpus is three biographies, which rarely make distance claims. Details in the reconciliation.

**The gaps are not template families.** They are four capability fields nothing currently records — internal event beats, text-slot capability, motion activity, evidence obligation ceiling — plus one vocabulary crosswalk. No purchase is recommended.
