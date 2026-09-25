# 1. Current-state audit

What exists, what is reliable, what is incomplete, and what conflicts. Read [`00-reconciliation.md`](00-reconciliation.md) first if you want only the deltas.

## Sources inspected

| Source | Status |
|---|---|
| The four creator-reference analyses and the comparison artifact | Read in full. 628 units, 186 segment patterns. |
| `/Volumes/onn. Drive/AE Templates` | Read in full. 85 packs, 180 `.aep` files parsed read-only. |
| `astra-selector-formula-inputs.json` | Read. 21 of 22 answers confirmed. |
| The 30 selector cases, results and feedback calibration | Read in full. |
| Approved scene catalog, catalog policy, template family map | Read in full. |
| Infographic and cinematic-scatter profiles and rendering rules | Read in full. |

Documents-folder access was blocked for the first part of this design phase and opened partway through. Everything below reflects the full read.

---

## The reference corpus: two clean axes, five dirty ones

The 628 annotated units are high quality as description and half-finished as a feature set.

**Reliable as selector features.** `treatmentClasses` (13 values), `rhetoricalFunction` (18), `sourceSpecificity` (4), `editorialRole` (9).

**Not usable as recorded.** `claimType` (442 distinct values across 628 units), `mediaType` (425), `presentationFamily` (198), `entityRelationship` (580), `layout` (580).

`entityRelationship` and `layout` are effectively unique per unit. `presentationFamily` is worse than merely free: its most common values are treatment-class names, so the field drifted into duplicating `treatmentClasses` on some units and describing layout on others.

**The pattern layer has no join key.** 186 segment patterns are defined and no pattern id appears in more than one reference, so the `cross_topic` label on 111 of them was never validated against a second video. Units cite 609 distinct `reusablePatternIds`, of which 464 are never defined. The comparison artifact's eight headline patterns appear in no segment pattern and are cited by no unit — a summary with no traceable link to the evidence. The 16 derived clusters in `data/derived-contract-clusters.json` are a first replacement, each carrying its unit ids.

**One piece of the comparison artifact's guidance is wrong.** It attributes the data-led reference's long scenes to charts continuing to change internally. In the unit data *every* treatment in that reference runs long, including plain archival at 22.5s and plain b-roll at 22.0s, against an overall baseline of 19.1s versus 8.9 to 9.5 elsewhere. That is a creator cadence, not a chart effect. The real chart effect is different and more useful: infographic scenes sit at a 16 to 17 second median in all four references regardless of baseline.

---

## The project: mature, and unevenly populated

### Confirmed requirements

21 of 22 answers in the source-of-truth file are confirmed. The single unconfirmed one is `18_evidence_quality_and_citation_policy`, deferred by you. Any attribution or citation field in these schemas is therefore provisional.

Two readings conflict and need one sentence from you. `04_priority_order` ranks factual accuracy first and spoken-word alignment third. `05_rejection_policy` then names `highestPriorityGate` as *"Important visual events must align with the relevant spoken phrases."* I read those as compatible — alignment is the gate never traded away, factual accuracy governs ranking among candidates that pass every gate — but the design behaves differently under the other reading.

### Ground truth

Thirty annotated passages with narration text, desired outcome, shot decomposition and fallback. Thirty-three of an expected thirty-four feedback records; `30.01` is missing, which is unfortunate because that passage is the clearest refusal-to-invent case in the set.

Ten global rules already derived from your corrections. A deterministic baseline selector exists, has been run across all thirty cases, and produces scored, review-flagged candidate lists.

**The passages are comparison-dominant**: 13 compare, 4 quantify, 3 each timeline, sequence and evidence, 2 each rank and introduce. Seventeen of thirty allow an infographic. This is a data documentary, which makes reference 2 the closest editorial analogue rather than the exact-subject reference 1.

### Approved catalog

| Kind | Count |
|---|---|
| After Effects templates | 14 |
| After Effects scenes | 185 |
| Infographic profiles | 57 |
| Cinematic 3D layouts | 9 |
| B-roll retrieval profiles | 1 |

The infographic and scatter profiles are strong. They carry capacity, data mapping, visual encoding, `avoid_when`, caveats, an input contract and an encoding audit, and the scatter profiles cite source files and line numbers for their claims.

**The After Effects scene records are the weak side**, and the gaps are in the fields a selector needs most:

| Field | Present on 185 scenes |
|---|---|
| `selectionContract` core | 185 |
| `function` | 112 |
| `assetPresentation` | 103 |
| `scriptMatching` | 72 |
| `focalEntityCount` | **14** |

`focalEntityCount` decides whether a container can hold a passage at all and is populated on 7.6% of scenes. `scriptMatching` is what the reverse mapping reads and is on 39%.

Two families in the approved template map are empty and awaiting your selection: `two_dimensional_plot` and `three_dimensional_plot`.

---

## The conflict that blocks determinism

Three job vocabularies are in use and they do not map to one another.

| Where | Field | Values |
|---|---|---|
| The 30 cases | `input.job` | quantify, compare, introduce, timeline, sequence, rank, evidence |
| Approved scenes | `scene.function` | quantify, entity explanation, text description, paired presentation, date event, closing, title, entity reveal — plus 73 nulls |
| Reference analyses | `rhetoricalFunction` | 18 values |
| Infographic profiles | `intents` | 20-plus values |
| Scatter profiles | `intents` | rank, magnitude, distance, outlier, attrition, survival and others |

Only `quantify` and `compare` appear in more than one vocabulary meaning the same thing. Matching a passage's job to a scene's function cannot currently be computed. One crosswalk table resolves it, and it is the highest-value single task in the implementation plan.

---

## Template library: organised, and less adjustable than the approved adjustments assume

The drive has a maintained README indexing 85 packs. I re-parsed 180 project files directly and the index is accurate.

**Colour adjustment is listed as approved and is mostly unavailable.** Across 180 projects, 95 expose an After Effects Color Control.

| Category | Projects | Exposing a colour control |
|---|---|---|
| 04 Match Cuts | 31 | 31 |
| 01 Data & Infographics | 21 | 18 |
| 03 Documentary & Archival | 12 | **2** |

The category closest in subject to this documentary is the least recolourable, and **neither named style reference exposes a colour control**. The `history-and-documentary` pack exposes none across both projects. The `carousel-2026-09-11` pack exposes none, and also **zero text slots** against 26 media slots.

This corroborates a decision you already made manually. `approved-catalog-policy.json` excludes `05-history` and `history-envato` because *"no exposed global dark-theme control has been verified."* The `.aep` parse confirms it directly and covers the whole library in under a minute, so this exclusion class can be detected before review rather than after.

**Twelve projects have eight or more media slots and zero text slots.** They cannot carry a name, a date or an attribution. That is a legitimate capability limit, but nothing currently records it, so a structurally perfect carousel that cannot identify anyone will keep being proposed.

**`Archive 2` is undocumented.** The drive README does not cover it. It holds a `Comparisons 01` project and a Documents & Screens group — YouTube UI, screen mockup, monitor and scrolling screen packs. Given that 13 of 30 passages are comparisons, that `two_dimensional_plot` is empty, and that your feedback on passage 15 asks for document templates, both are worth inspecting.

**Stale paths.** `future_review_request` names `01 Slideshows` and `02 Openers & Intros`. Neither exists; the drive was reorganised on 2026-08-31 and they are now `09 Slideshows` and `06 Openers & Intros`.

---

## What is reliable, incomplete, conflicting

**Reliable.** The four controlled reference-corpus axes. The timing fields — 905 phrase-aligned events with 88.8% rated strong, 1000 timestamped internal changes. The confirmed requirements. The ten global rules. The infographic and scatter profiles. The two rendering-rules documents. The drive README and my re-parse of it.

**Incomplete.** Five free-text reference fields. The pattern layer. AE scene records on `focalEntityCount`, `scriptMatching`, `function` and `assetPresentation`. Both plot families in the template map. One feedback record. No internal event beats anywhere, which is what phrase alignment needs. No text-slot, motion-activity or evidence-obligation fields on any container.

**Conflicting.** The three job vocabularies. The priority-order versus highest-gate reading. The comparison artifact's cadence explanation against its own unit data. My corpus-derived spatial finding against your confirmed `spatial_relationship_first` rule, resolved in favour of the project rule in the reconciliation.
