# 0. Reconciliation after reading the project

Access to `~/Documents/ChatGPT/Polish` opened partway through this design phase. I had already built the method and the evidence synthesis from the four creator analyses and the template drive alone. This document records what the project files changed.

**The headline: the architecture holds, and more of it already exists than I assumed.** The approved catalog's own `selectionPrinciple` reads "Match the narration relationship and required assets to the template contract before considering surface style." That is the thesis of this design, already written down. What follows is where I was wrong, where the project and my evidence disagree, and what the project is actually missing.

---

## 1. One of my findings is overridden by a confirmed project rule

I reported, from the reference corpus, that `spatial_or_cinematic_3d` carries a proof role only 16% of the time and caps at four focal entities — and concluded it is an explanation device rather than a proof device.

`feedback-calibration.json` already contains the opposite rule, derived from your own corrections:

> **`spatial_relationship_first`** — For gap, distance, overlap, outlier, or falling-rank claims, retrieve spatial/3D candidates before ordinary comparison charts.

Your feedback says it five separate times. On case 02.02: *"this is a distance / space comparison and the visual should display that. 2 data points on one of the 3d scatter plot is perfect for this."* On 03.01 and 04.01: *"the 3d scatter plot is perfect for this. its perfect for communicating vast distances."*

**The project rule wins, and the disagreement is explainable rather than contradictory.** The reference corpus is three biographies and one data story. Biographies rarely make distance claims, so spatial treatment there is decorative and the 16% figure reflects that. Your documentary is built on distance, gap and rank-loss claims, where a spatial field *is* the proof. The corpus prior was measuring the wrong population.

This is exactly the failure mode the scoping machinery exists to prevent, and it is worth noting that it caught a mistake I made rather than one the system made. A cross-topic statistical prior is weaker evidence than a project rule supported by five of your own corrections.

**Correction applied:** the evidence synthesis now marks the spatial finding as reference-corpus-specific and subordinate to `spatial_relationship_first`.

---

## 2. Your documentary is not shaped like the exact-subject reference

The comparison artifact weights reference 1, the Future biography, highest because it shares subject matter. By editorial shape, the closest analogue is reference 2, the data-led one.

Across your 30 annotated passages:

| Job | Count |
|---|---|
| compare | 13 |
| quantify | 4 |
| timeline | 3 |
| sequence | 3 |
| evidence | 3 |
| rank | 2 |
| introduce | 2 |

Seventeen of thirty allow an infographic. Twelve name a chart presentation and five a scatter. That is a comparison-and-quantity documentary. The reference corpus is evidence-and-archival dominant, with 129 evidence units against 16 comparison units.

**Consequence:** the cadence and treatment priors drawn from references 1, 3 and 4 describe a different kind of film. The ones that still apply are the structural and timing findings — the readable hold floor, the change budget, the establish-then-land event offset, container capacity by entity count. The treatment-frequency findings mostly do not.

Reference 2's own numbers are the more relevant cadence prior for your film, and the chart-specific one holds everywhere: an infographic scene sits at 16 to 17 seconds in all four references.

---

## 3. Ten global rules already exist, and four were not in my design

`feedback-calibration.json` carries ten rules derived from your corrections. Six match what I proposed independently. Four are additions I did not have:

| Rule | What it adds |
|---|---|
| `four_distinct_options` | Four candidates must come from four different **template IDs**. A stricter and more checkable definition of "meaningfully different" than my "different visual strategy". |
| `include_infographic` | Always include at least one infographic candidate when infographics are allowed for the shot. A slate-composition constraint, not a ranking one. |
| `spatial_relationship_first` | Covered above. |
| `video_competes_with_stills` | When footage directly shows the named people, event or performance, it enters the slate rather than only stills being considered. |

The six that match: `separate_asset_retrieval` (score the template independently of whether the assets are the right people), `shot_decomposition`, `readability`, `focal_hierarchy`, `multi_asset_evidence`, `continuity`.

`separate_asset_retrieval` deserves a note. It is the same separation my back-test argues for, and your own feedback is the cleanest evidence for it. On case 09.01 you wrote *"good selections for templates. bad artists selections except latto."* On 02.01: *"Overall accurate templates selections, but poor asset..."* Template quality and asset quality came apart in your own review, repeatedly. That is the separation, observed rather than theorised.

**Correction applied:** all four missing rules are now in the decision model, and the slate-construction section adopts your template-ID definition of distinctness.

---

## 4. The biggest real defect: three job vocabularies that do not map to each other

This is the most actionable thing I found, and it blocks deterministic matching today.

| Where | Field | Values |
|---|---|---|
| Your 30 cases | `input.job` | quantify, compare, introduce, timeline, sequence, rank, evidence — 7 |
| Approved scene catalog | `scene.function` | quantify, entity explanation, text description, paired presentation, date event, closing, title, entity reveal — 8, plus 73 of 185 scenes with no value |
| Reference analyses | `rhetoricalFunction` | 18 values |
| Infographic profiles | `intents` | compare, rank, overview, magnitude, multiple metrics, spotlight, history, lookup… 20-plus |
| Scatter profiles | `intents` | rank, magnitude, spotlight, overview, compare, distance, outlier, timeline, attrition, survival… |

Only `quantify` and `compare` appear in more than one vocabulary with the same meaning. The narration side and the catalog side are speaking different languages, which means the match between a passage's job and a scene's function currently cannot be computed — it has to be inferred each time.

**One crosswalk table fixes this**, and it is the highest-value single piece of work in the implementation plan.

---

## 5. The approved catalog is more complete than I assumed, and less populated than it looks

Real coverage, which supersedes my drive-only gap report:

| Kind | Approved |
|---|---|
| After Effects templates | 14 |
| After Effects scenes | 185 |
| Infographic profiles | 57 |
| Cinematic 3D layouts | 9 |
| B-roll retrieval profiles | 1 |

The infographic and scatter profiles are excellent. They carry capacity, data mapping, visual encoding, `avoid_when`, caveats, an input contract and an encoding audit. The scatter profiles go further and record implementation evidence down to source file and line numbers.

But the After Effects scene records are unevenly filled, and the missing fields are the ones a selector needs most:

| Field | Present on |
|---|---|
| `selectionContract` core | 185 of 185 |
| `function` | 112 |
| `assetPresentation` | 103 |
| `scriptMatching` (`appropriateNarration`, `avoidWhen`, `rationale`) | 72 |
| **`focalEntityCount`** | **14** |

`focalEntityCount` is the cleanest structural selector signal in the reference data — it is what decides whether a container can hold the passage at all — and it is populated on 7.6% of approved scenes. `scriptMatching` is what the reverse mapping reads, and it is on 39%.

**Correction applied:** my template capability schema is reframed as an *extension* to your existing `selectionContract` rather than a replacement. The genuinely missing fields are listed in section 7.

---

## 6. Two conflicts in the confirmed requirements

**Priority order versus highest-priority gate.** `04_priority_order` ranks factual accuracy first and spoken-word alignment third. `05_rejection_policy` then states `highestPriorityGate`: *"Important visual events must align with the relevant spoken phrases."*

I read these as compatible — alignment is the gate never to be traded away, while factual accuracy governs ranking among candidates that pass every gate. But they can also be read as contradicting, and the design behaves differently depending which reading is right. Worth one sentence from you.

**Evidence and citation policy is deferred.** `18_evidence_quality_and_citation_policy` is the only answer marked `confirmed: false`. My contract schema carries attribution and citation fields, and the capability schema has `supportsAttribution`. Those are provisional until that question is answered, and I have marked them as such rather than treating them as settled.

---

## 7. What the project is actually missing

Not template families. These four capability gaps block phrase-level determinism, and none of them requires buying anything.

**Internal event beats.** No scene record carries the times of its own reveals, highlights or camera moves, or whether each can be moved independently. Timing control today is whole-scene retime: `allowSpeedUp`, `allowSlowDown`, `outputDuration = nativeDuration / playbackRate`. That can fit a scene to a duration. It cannot land a highlight on a phrase. Since phrase alignment is your highest-priority gate, this is the gap that matters most.

**Text-slot capability.** Nothing records whether a scene can display a name, a date or an attribution. My parse of the drive found twelve projects with eight or more media slots and zero text slots, including the named carousel style reference at 26 media slots and none for text. A structurally perfect carousel that cannot say who anyone is will otherwise keep getting proposed.

**Reading load.** Your feedback on case 17.01 is precise: *"3rd is a horrible choice because the scene isnt made for reading, more for viewing. 1st two are just ok because the animation on them is a little too active for expecting the viewer to read rules."* The `readability` global rule captures the rejection but no scene record carries the motion-activity value that would let a checker apply it. It needs to be a field, not a judgement call.

**Evidence obligation ceiling.** No record states the strictest proof obligation a container can honour. A scene that crops, stylises or overlays evidence cannot serve `exact_source_required`, and nothing currently prevents proposing it.

---

## 8. Three integrity issues worth a look

**The colour-control exclusions can be predicted automatically.** You excluded `05-history` and `history-envato` because *"no exposed global dark-theme control has been verified."* My read-only parse of the `.aep` binaries confirms it directly: every `history-*` pack exposes zero After Effects Color Controls. The same parse covers all 180 project files on the drive and takes under a minute, so this exclusion class can be detected before a template is ever reviewed rather than after. Across the drive, only 53% of projects expose any colour control, and in the Documentary and Archival category just 2 of 12 do — neither of them a named style reference.

**Stale paths in the deferred review request.** `future_review_request` names `/Volumes/onn. Drive/AE Templates/01 Slideshows` and `02 Openers & Intros`. Neither exists. The drive was reorganised on 2026-08-31 and those are now `09 Slideshows` and `06 Openers & Intros`. The paths need updating before that review runs.

**Undocumented inventory.** The drive's `Archive 2` is not covered by its README and holds a `Comparisons 01` project plus a Documents & Screens group — YouTube UI, screen mockup, monitor and scrolling screen packs. Given that thirteen of your thirty passages are comparisons and the `two_dimensional_plot` family in the approved map is still empty, `Comparisons 01` is worth ten minutes in After Effects.

**One missing feedback record.** `feedback-calibration.json` expects 34 and has 33. `30.01` is absent — the passage whose own fallback reads *"hold for script clarification; the narration names only Jay-Z but the intended visual needs five historical artists."* That case is the clearest example in the set of the system correctly refusing to invent entities, so its feedback is worth recovering.

---

## 9. Image binding in the scatter layouts — accounted for

The scatter profile for the receding rank ladder records that its field cutouts were assigned by a seeded random shuffle from a general library, and states that "image slots are not identities."

**Clarified by the user: this is a known, deliberate state, not an open risk.** The images swap and map easily. The placeholder shuffle was scoping — it let the layout, encoding and camera logic be established without per-entity image work blocking them. Image binding is a solved step that happens when a scene is actually produced.

So the profile note describes the *shipped sample state*, not a capability limit of the layout. The only thing the selector needs to carry is the ordinary preflight it would apply to any container: confirm the bound assets are the named entities before a render is presented as identity evidence. That is the same check `separate_asset_retrieval` already implies for every template, and `cinematic-scatter/headshot-requirements.json` and `spatial-media-preflight.json` already exist to serve it.

I had written this up as a landmine. It is not one.

## What did not change

The stage order. Gates before ranking. Lexicographic priority. Media roles in the contract and filenames only in the candidate. Slate construction rather than top-N ranking. Confidence calibrated from your decisions rather than an invented threshold, with auto-advance off until then. The back-test numbers, which stand on their own and are now a regression fixture.

---

# Addendum, 2026-09-16: design approved, prototype authorized

`astra-selector-formula-inputs.json` moved to schemaVersion 2, status `design_approved_prototype_authorized`, with a new answer `23_prototype_capability_clarifications`. Combined with the user's ruling on the priority conflict, this changes five things.

## A. Timing outranks accuracy in ranking

**Ruling:** among candidates that clear every hard gate, the better-timed one wins. Answer 23 states the same: *"Timing, relevance and exact visual/text communication first; accurate asset selection remains necessary but is not the current research focus."*

The priority order for ranking becomes:

1. Spoken-word and visual-event alignment
2. Exact narration claim communication
3. Factual accuracy
4. Media-to-container structural compatibility
5. Style consistency
6. Asset quality
7. Visual polish
8. Render speed and cost

**What did not move.** The hard gates are unchanged. Answer 23's `preserves` block keeps "No invented entities, data or relationships" and "Exact phrase-event timing and readable holds." So the system still cannot fabricate a person, a number or a relationship, and still cannot ship unreadable evidence. What moved is *asset-identity exactness*: a simple screenshot that communicates the point is acceptable, and hunting the perfect asset is not what this phase is optimising.

Resolves open issue 1.

## B. Duration is elastic, and the narration yields to evidence

**Ruling:** *"time can be extended for this. we dont have to fit a duration if the video evidence needs 5 extra seconds to complete him saying the proof. we arent trying to cram or stretch to fit a duration budget."*

This is the larger of the two changes, because my contract schema had duration as a constraint the visual had to fit inside. It is now an output.

- `acceptableDurationSeconds` is a descriptive expectation, never a budget. The corpus figures stay as reference points and stop being limits.
- A new `durationPolicy` block carries `evidenceMustComplete`, which defaults true. Truncating a proof to hit a target length is a failure, not a trade.
- `narrationYields` models the case the ruling describes: the narration pauses and source audio carries the proof. The unit runs long and the rest of the film moves later. That is expected, not a problem to solve.
- The 6.8-second internal change budget drops from a cap to a split hint, and does not apply while a unit is extended for evidence or carrying continuous testimony.

This also retires the exemption I had proposed for uncut testimony in open issue 3. Under an elastic policy it is not an exemption, it is the normal case.

It is worth noting the project already said this. Answer `14_scene_boundaries_and_visual_cadence` constrains the derived ranges as "subordinate to exact claim communication, phrase alignment, readability, and the needs of the individual passage." My schema over-constrained what the requirements had already made flexible.

## C. Independent event timing is confirmed, which downgrades the top gap

Answer 23 marks `independentTiming` as user-confirmed: *"Image, value or highlight can be scheduled to the relevant phrase. Actual event mappings must still be authored and checked."*

I had this as gap 1 and the highest-priority blocker. That was half right. The *capability* exists, so nothing needs building or buying. What is missing is the *data*: per-scene event times and movability are still unrecorded, and the mappings have to be authored and verified. It moves from a capability gap to an annotation task, which is a much cheaper problem.

Two further capabilities are confirmed. `questionToAnswer` allows a question state to hold before data populates, which is exactly what feedback 10.01 asked for. `counterCompositing` allows counter scenes to be background-removed, scaled and placed in front of or behind another scene, which routes around the counters template's lack of an image slot.

Two are tentative and need visual review before they can pass a gate: `flexibleCapacity` (how hiding unused slots actually looks) and `darkStyle` (how a restyled result actually looks).

## D. Three gaps close with prototype fallbacks

Answer 23 supplies fallbacks that make my gaps 2 and 4 non-blocking:

| Gap | Fallback |
|---|---|
| Document-native evidence container | A simple screenshot is accepted when it communicates the point |
| Low-motion readable text card | Simple words on a background are accepted; polish can follow |
| Carousel assets | Requested dynamically from the visual contract |

The named `sourceCollections` also cover them better than I reported. `Archive 2 / Lists & Titles / text-carousel` exposes **8 text slots and a colour control**, which serves passage 17's rules text and the list-shaped passages such as 26. `Documents & Screens / Screen_Mockup` and `Scrolling_Screen_Animations` cover the screenshot presentation. I had flagged the Documents & Screens group as worth inspecting; it is now named as an approved source.

## E. Authorization

| | |
|---|---|
| Prototype implementation | **Authorized** |
| Preview segmentation | **Authorized** |
| Production rendering | Not authorized, requires a separate instruction |
| Modifying original `.aep` files | Not authorized |

Scene work is scoped to cutting existing example videos, filtering useful scenes and explaining selection conditions, with source files and scene approvals preserved separately.

Two asset notes supersede earlier state: Future is already in the Media Library cutouts, which retires the old missing flag, and Post Malone will be added on request when a chosen plan needs him.
