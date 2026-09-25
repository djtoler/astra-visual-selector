# Vertical slice — five passages, end to end

Contract, retrieval, four-candidate slate, gates, decision. Nothing rendered.
Every timing value is measured from the aligned audio. Claims, media roles and
events are authored and marked as such in each contract's `provenance` block.

**Slate coverage 26/30. Desired outcome ranked first in 22/30.**

Rules: 10 from the project snapshot, 14 active local corrections (COR-0001-spatial-attrition, COR-0002-citation-policy, COR-0003-era-consistency-gate, COR-0004-change-budget-is-a-hint, COR-0005-portrait-legibility, COR-0006-intent-scoring-and-overview-route, COR-0007-scene-level-distinctness, COR-0008-defects-found-by-extending, COR-0009-per-shot-selection, COR-0010-defects-found-at-thirty, COR-0011-motion-profiles-adopted, COR-0012-schedule-replacement-is-the-mechanism, COR-0013-passage-28-allowed-kinds, COR-0014-measurement-was-the-problem). Maximum scope project; nothing is written to the project.

**Agreement with the prior selector: 20/30.** That compares against the literal candidate lists in `year-seventeen-30-selector-results.md` rather than a reading of each `desired` sentence. Neither number alone is the score: the user corrected the prior selector on several passages, so diverging from it is sometimes right.

| Passage | Job | Audio | Events resolved | Slate | Desired at | Decision |
|---|---|---|---|---|---|---|
| 01 Opening scale | quantify | 10.81s | 2/2 | 4 | 1 | blocked_missing_assets |
| 02 Named cover and catalog comparison | compare | 16.39s | 3/3 | 4 | not in slate | blocked_missing_assets |
| 03 Explaining a chart | quantify | 10.11s | 3/3 | 4 | 1 | blocked_missing_assets |
| 04 Comparison before reveal | compare | 11.52s | 4/4 | 4 | 1 | blocked_missing_assets |
| 05 Audience prediction prompt | introduce | 9.25s | 3/3 | 4 | 1 | require_user_review |
| 06 Date and career milestone | timeline | 7.03s | 2/2 | 4 | 2 | blocked_missing_assets |
| 07 Cultural analogy | sequence | 14.65s | 3/3 | 4 | 1 | blocked_missing_assets |
| 08 Competing explanations | sequence | 10.65s | 3/3 | 4 | 1 | blocked_missing_assets |
| 09 Several statistical examples | compare | 11.1s | 4/4 | 4 | 2 | blocked_missing_assets |
| 10 Question around unknown number | introduce | 5.69s | 2/2 | 4 | 1 | require_user_review |
| 11 Concentration reveal | compare | 10.94s | 3/3 | 4 | not in slate | blocked_missing_assets |
| 12 Before-and-after ranking test | rank | 20.31s | 6/6 | 4 | 1 | blocked_missing_assets |
| 13 Scale through comparison | quantify | 14.58s | 3/3 | 4 | not in slate | blocked_missing_assets |
| 14 Group-versus-group comparison | compare | 12.65s | 3/3 | 4 | 1 | blocked_missing_assets |
| 15 Artifact then action claim | evidence | 6.62s | 2/2 | 4 | 1 | blocked_missing_assets |
| 16 Historical cohorts | compare | 23.15s | 2/2 | 4 | 1 | blocked_script_conflict |
| 17 Methodology rule | evidence | 11.39s | 3/3 | 2 | 1 | auto_advance |
| 18 Class total | quantify | 14.25s | 3/3 | 4 | 1 | blocked_missing_assets |
| 19 One artist versus class | compare | 16.59s | 3/3 | 4 | 4 | blocked_missing_assets |
| 20 One slice versus full catalogs | compare | 23.73s | 4/4 | 4 | 1 | blocked_missing_assets |
| 21 Accusation tested with evidence | compare | 21.06s | 4/4 | 4 | 1 | blocked_missing_assets |
| 22 Result turns against subject | compare | 15.94s | 3/3 | 4 | 1 | blocked_missing_assets |
| 23 Archive-on-autoplay hypothesis | evidence | 20.89s | 3/3 | 4 | 1 | require_user_review |
| 24 Timeline prediction | timeline | 14.19s | 3/3 | 4 | 1 | blocked_missing_assets |
| 25 Longevity reveal | timeline | 13.06s | 2/2 | 4 | 1 | blocked_missing_assets |
| 26 Categorized achievements | rank | 21.1s | 3/3 | 4 | 4 | blocked_missing_assets |
| 27 Opposing artist archetypes | compare | 35.94s | 3/3 | 4 | 1 | blocked_missing_assets |
| 28 Overlap and spatial relationship | compare | 22.44s | 3/3 | 4 | not in slate | blocked_missing_assets |
| 29 Counterevidence and boundary | compare | 34.66s | 3/3 | 4 | 1 | blocked_script_conflict |
| 30 Measurement limitation | sequence | 20.19s | 3/3 | 4 | 1 | blocked_script_conflict |

## Passage 01 — Opening scale

> Seven hundred times a second. That's how often one rapper's catalog gets played on Spotify, and by the time the day closes out it comes to fifty-nine million.

**Job** quantify · **Takeaway** One rapper's catalog is played 700 times a second, which comes to 59 million a day.

**Audio** 0.0–10.81s (10.81s, alignment coverage 0.871) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Seven hundred times a second" | +0.0s | 1.0 | decisive |
| E2 | "fifty-nine million" | +9.34s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| play_rate_value | proof | exact_source_required | data_required | — |

### Candidates — 9 viable of 12, 3 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | after_effects | Counters · Counter 01 | rank (scene-level distinctness) | communicates_claim, decisive_events_alignable, schedule_replacement_unproven |
| 2 | after_effects | Counters · Counter 02 | rank (scene-level distinctness) | communicates_claim, decisive_events_alignable, schedule_replacement_unproven |
| 3 | after_effects | Counters · Counter 03 | rank (scene-level distinctness) | communicates_claim, decisive_events_alignable, schedule_replacement_unproven |
| 4 | after_effects | Counters · Counter 04 | rank (scene-level distinctness) | communicates_claim, decisive_events_alignable, schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| play_rate_value | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Verified values still required for: play_rate_value.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: communicates_claim, decisive_events_alignable, schedule_replacement_unproven.

**Ground truth** desired: _Accelerating counter for 700 plays per second, resolving to the 59 million daily total_ — in slate at rank 1. Recorded fallback: _none_.

## Passage 02 — Named cover and catalog comparison

> Curren$y was on the 2009 XXL Freshman cover, and every song he has ever put on the platform — the mixtapes, the Jet Life run, the features, all of it stacked end to end — adds up to what this one catalog moves in twenty-four days.

**Job** compare · **Takeaway** Curren$y's entire catalog equals what this one catalog moves in 24 days.

**Audio** 10.81–27.2s (16.39s, alignment coverage 0.8889) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Curren$y was on the 2009 XXL Freshman cover" | +0.35s | 0.977 | decisive |
| E2 | "the mixtapes, the Jet Life run, the features" | +7.07s | 0.988 | supporting |
| E3 | "what this one catalog moves in twenty-four days" | +13.23s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| xxl_cover_2009 | proof | exact_source_required | partially_bound | Freshman, XXL |
| catalog_evidence | proof | exact_source_required | missing | a source for catalog_evidence |
| duration_ratio | proof | exact_source_required | data_required | — |

### Candidates — 54 viable of 85, 31 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | after_effects | Photo Slideshow — Memories · Scene 02 | approved family: two_person_portrait | no_unsupported_implication, decisive_events_alignable, asset_quality_sufficient, era_consistent |
| 2 | after_effects | Photo Slideshow — Smooth · Scene 06 | approved family: two_person_portrait | no_unsupported_implication, decisive_events_alignable, asset_quality_sufficient, era_consistent |
| 3 | after_effects | Memories Photo Slideshow — Creative Slides · Scene 08 | approved family: two_person_portrait | no_unsupported_implication, decisive_events_alignable, asset_quality_sufficient, era_consistent |
| 4 | infographic | Two-subject score comparison | rank | no_unsupported_implication, asset_quality_sufficient, era_consistent |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| xxl_cover_2009 | media_library | /Users/dwaynetoler/Media Library | editorial choice |
| catalog_evidence | unknown | NOT YET SOURCED | editorial choice |
| duration_ratio | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Unbound: Freshman, XXL, a source for catalog_evidence.
- Verified values still required for: duration_ratio.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: no_unsupported_implication, decisive_events_alignable, asset_quality_sufficient, era_consistent.

**Ground truth** desired: _2009 XXL Freshman cover inside an animation, followed by a 17-years-versus-24-days comparison_ — NOT IN SLATE. Recorded fallback: _artist portrait only_.

## Passage 03 — Explaining a chart

> Ninety-three rappers, one dot each. Higher dot, more plays per day. Start at the bottom.

**Job** quantify · **Takeaway** This chart holds 93 rappers, one dot each, and height means daily plays.

**Audio** 27.2–37.31s (10.11s, alignment coverage 0.875) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Ninety-three rappers, one dot each" | +0.4s | 1.0 | decisive |
| E2 | "Higher dot, more plays per day" | +5.44s | 1.0 | decisive |
| E3 | "Start at the bottom" | +8.78s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| population_values | proof | exact_source_required | data_required | — |
| axis_definition | context | exact_source_required | generated_or_authored | — |

### Candidates — 32 viable of 69, 37 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | cinematic_3d | Fixed-scale one-dot-per-entity population field | rank | schedule_replacement_unproven |
| 2 | infographic | Two-cohort ranked lists | rank | schedule_replacement_unproven |
| 3 | infographic | Contrasting ranked tables | rank | schedule_replacement_unproven |
| 4 | infographic | Two-panel trend comparison | rank | schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| population_values | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Verified values still required for: population_values.
- Winner has unresolved gates: schedule_replacement_unproven.

**Ground truth** desired: _Truthful fixed-scale 3D population field with one verified dot per rapper_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 04 — Comparison before reveal

> Near the top, Future. Travis Scott. Then one dot with open air under it. More than both of them added together.

**Job** compare · **Takeaway** One dot sits above Future and Travis Scott combined, with open air beneath it.

**Audio** 49.12–60.64s (11.52s, alignment coverage 1.0) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Near the top, Future" | +0.0s | 1.0 | decisive |
| E2 | "Travis Scott" | +3.3s | 1.0 | decisive |
| E3 | "Then one dot with open air under it" | +5.7s | 1.0 | decisive |
| E4 | "More than both of them added together" | +9.1s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| outlier_values | proof | exact_source_required | data_required | — |
| entity_portraits | identity | exact_event_or_entity_required | bound_local | — |

### Candidates — 36 viable of 69, 33 gate-rejected · spatial_relationship_first fired via **base** rule 1.1.0-local on above

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | cinematic_3d | Fixed-scale small-field outlier | spatial_relationship_first | schedule_replacement_unproven |
| 2 | infographic | Three multi-metric subject cards | rank | schedule_replacement_unproven |
| 3 | infographic | Three-row portrait metric table | rank | schedule_replacement_unproven |
| 4 | infographic | Full-body magnitude comparison | rank | schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| outlier_values | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Verified values still required for: outlier_values.
- Winner has unresolved gates: schedule_replacement_unproven.

**Ground truth** desired: _Truthful fixed-scale 3D outlier comparison for Drake, Future, and Travis Scott_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 05 — Audience prediction prompt

> A catalog pulling that much every day, in 2026, sitting on top of everybody. What year of his career is this? Pick a number.

**Job** introduce · **Takeaway** A question is posed about which career year this is, and the viewer should guess.

**Audio** 67.08–76.33s (9.25s, alignment coverage 1.0) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "sitting on top of everybody" | +4.2s | 1.0 | supporting |
| E2 | "What year of his career is this" | +6.09s | 1.0 | decisive |
| E3 | "Pick a number" | +8.36s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| subject_portrait | identity | exact_event_or_entity_required | bound_local | — |
| question_text | subject | exact_source_required | bound_local | — |

### Candidates — 90 viable of 123, 33 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | after_effects | History and Documentary — 10 slides · Scene 2 | approved family: single_portrait_with_side_text | decisive_events_alignable, schedule_replacement_unproven |
| 2 | after_effects | History Slideshow · Scene 08 | approved family: single_portrait_with_side_text | decisive_events_alignable, schedule_replacement_unproven |
| 3 | after_effects | Intro Slideshow · Scene 22 | approved family: single_portrait_with_side_text | decisive_events_alignable, schedule_replacement_unproven |
| 4 | infographic | Single-subject introduction | rank | schedule_replacement_unproven |

**Decision** `require_user_review` · confidence `uncalibrated_prior`

- Top two candidates are tied on every priority level.
- Winner has unresolved gates: decisive_events_alignable, schedule_replacement_unproven.

**Ground truth** desired: _Slow single-artist portrait with question text_ — in slate at rank 1. Recorded fallback: _plain artist cutout_.

## Passage 06 — Date and career milestone

> So Far Gone came out in 2009. This chart covers the year that ends on its seventeenth anniversary.

**Job** timeline · **Takeaway** So Far Gone came out in 2009, and this chart covers the year ending on its seventeenth anniversary.

**Audio** 77.64–84.67s (7.03s, alignment coverage 0.9444) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "So Far Gone came out in 2009" | +0.46s | 1.0 | decisive |
| E2 | "the year that ends on its seventeenth anniversary" | +4.18s | 0.879 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| album_artwork | proof | exact_source_required | missing | So Far Gone |
| subject_cutout | identity | exact_event_or_entity_required | bound_local | — |
| career_clock | context | exact_source_required | data_required | — |

### Candidates — 34 viable of 60, 26 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Period-by-period leaders | rank | era_consistent, no_unsupported_implication, schedule_replacement_unproven |
| 2 | infographic | Hero with chronological ledger | rank | era_consistent, no_unsupported_implication, schedule_replacement_unproven |
| 3 | infographic | Long signed-value history with outlier | rank | era_consistent, no_unsupported_implication, schedule_replacement_unproven |
| 4 | infographic | Four-stage path and average | rank | era_consistent, no_unsupported_implication, schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| album_artwork | unknown | NOT YET SOURCED | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Unbound: So Far Gone.
- Verified values still required for: career_clock.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: era_consistent, no_unsupported_implication, schedule_replacement_unproven.

**Ground truth** desired: _Album cover plus artist cutout and a career-time visualization_ — in slate at rank 2. Recorded fallback: _album cover beside chart, otherwise review_.

## Passage 07 — Cultural analogy

> Year seventeen of a rap career is anniversary-tour territory. Deluxe reissues with three unreleased demos on the back. A festival slot at seven-forty, before the headliner.

**Job** sequence · **Takeaway** Year seventeen of a rap career normally means nostalgia, not dominance.

**Audio** 84.67–99.32s (14.65s, alignment coverage 0.8929) · **Strictest obligation** representative_media_allowed

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "anniversary-tour territory" | +2.81s | 1.0 | decisive |
| E2 | "Deluxe reissues with three unreleased demos" | +5.37s | 1.0 | supporting |
| E3 | "A festival slot at seven-forty" | +10.05s | 0.93 | supporting |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| veteran_examples | subject | exact_event_or_entity_required | missing | veteran rappers in year 17 or later |
| career_artifacts | context | representative_media_allowed | generated_or_authored | — |

### Candidates — 83 viable of 114, 31 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Full-body portraits inside magnitude bars | rank | no_unsupported_implication |
| 2 | infographic | Five portrait headline values | rank | no_unsupported_implication |
| 3 | cinematic_3d | Fixed-scale small-field outlier | rank | no_unsupported_implication |
| 4 | cinematic_3d | Before-and-after rank-loss field | rank | no_unsupported_implication |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Unbound: veteran rappers in year 17 or later.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: no_unsupported_implication.

**Ground truth** desired: _Several rappers in year 17 or later, plus performances or projects_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 08 — Competing explanations

> The explanations write themselves. Big back catalog. Half of it is other people's songs. Seventeen years to pile it up.

**Job** sequence · **Takeaway** Three obvious explanations present themselves: a big catalog, half of it features, and seventeen years to accumulate.

**Audio** 109.46–120.11s (10.65s, alignment coverage 0.9524) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Big back catalog" | +3.16s | 1.0 | decisive |
| E2 | "Half of it is other people's songs" | +5.6s | 1.0 | decisive |
| E3 | "Seventeen years to pile it up" | +8.0s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| catalog_breakdown | proof | exact_source_required | data_required | — |

### Candidates — 34 viable of 60, 26 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Two-cohort ranked lists | rank | schedule_replacement_unproven |
| 2 | infographic | Contrasting ranked tables | rank | schedule_replacement_unproven |
| 3 | infographic | Three group-achievement cards | rank | schedule_replacement_unproven |
| 4 | infographic | Four-stage path and average | rank | schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| catalog_breakdown | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Verified values still required for: catalog_breakdown.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: schedule_replacement_unproven.

**Ground truth** desired: _List-style catalog infographic, with features highlighted and 17-year framing_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 09 — Several statistical examples

> Latto's biggest is half of everything she's ever streamed. Jay Rock's is fifty-two percent. Ab-Soul's, seventy-one. Biz Markie, seventy-nine.

**Job** compare · **Takeaway** For most rappers, one song carries half or more of everything they have ever streamed.

**Audio** 141.22–152.32s (11.1s, alignment coverage 0.4074) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Latto's biggest is half of everything" | +0.46s | 0.972 | decisive |
| E2 | "Jay Rock's is fifty-two percent" | +3.86s | 0.903 | decisive |
| E3 | "Ab-Soul's, seventy-one" | +5.96s | 0.857 | decisive |
| E4 | "Biz Markie, seventy-nine" | +8.16s | 0.889 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| concentration_values | proof | exact_source_required | data_required | — |
| artist_portraits | identity | exact_event_or_entity_required | partially_bound | Biz Markie, Jay Rock, Latto |

### Candidates — 33 viable of 60, 27 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Subject ranking with peer context | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 2 | infographic | Four framed portrait values | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 3 | infographic | Full-body lineup with context figure | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 4 | infographic | Seven people-and-resources packages | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| concentration_values | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Unbound: Biz Markie, Jay Rock, Latto.
- Verified values still required for: concentration_values.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven.

**Ground truth** desired: _Repeatable artist-plus-catalog-distribution infographic_ — in slate at rank 2. Recorded fallback: _review_.

## Passage 10 — Question around unknown number

> You've got the shape now. Call it. What share of Drake's streams is his single biggest song?

**Job** introduce · **Takeaway** A question is posed and the viewer should guess before the answer arrives.

**Audio** 160.54–166.23s (5.69s, alignment coverage 0.9474) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Call it" | +1.68s | 1.0 | decisive |
| E2 | "What share of Drake's streams" | +2.88s | 0.982 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| subject_cutout | identity | exact_event_or_entity_required | bound_local | — |
| question_text | subject | exact_source_required | bound_local | — |

### Candidates — 90 viable of 123, 33 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | after_effects | History and Documentary — 10 slides · Scene 2 | approved family: single_portrait_with_side_text | decisive_events_alignable, schedule_replacement_unproven |
| 2 | after_effects | History Slideshow · Scene 08 | approved family: single_portrait_with_side_text | decisive_events_alignable, schedule_replacement_unproven |
| 3 | after_effects | Intro Slideshow · Scene 22 | approved family: single_portrait_with_side_text | decisive_events_alignable, schedule_replacement_unproven |
| 4 | infographic | Single-subject introduction | rank | schedule_replacement_unproven |

**Decision** `require_user_review` · confidence `uncalibrated_prior`

- Top two candidates are tied on every priority level.
- Winner has unresolved gates: decisive_events_alignable, schedule_replacement_unproven.

**Ground truth** desired: _Artist cutout with the prediction question_ — in slate at rank 1. Recorded fallback: _none_.

## Passage 11 — Concentration reveal

> Three percent. His ten biggest songs together come to fifteen percent. The next-flattest catalog at anything close to this size is Future, at twenty-four.

**Job** compare · **Takeaway** His catalog is far flatter than anyone at his size; the nearest comparison is Future at 24 percent.

**Audio** 166.23–177.17s (10.94s, alignment coverage 0.7308) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Three percent" | +0.41s | 0.8 | decisive |
| E2 | "His ten biggest songs together come to fifteen percent" | +1.01s | 0.988 | decisive |
| E3 | "Future, at twenty-four" | +8.59s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| distribution_values | proof | exact_source_required | data_required | — |
| hero_portrait | identity | exact_event_or_entity_required | bound_local | — |
| hero_and_peer | identity | exact_event_or_entity_required | bound_local | — |
| comparison_values | comparison | exact_source_required | data_required | — |

### Candidates — 34 viable of 60, 26 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Single-subject annotated value | rank | schedule_replacement_unproven |
| 2 | infographic | Long signed-value history with outlier | rank | schedule_replacement_unproven |
| 3 | infographic | Period-by-period leaders | rank | schedule_replacement_unproven |
| 4 | infographic | Single-subject introduction | rank | schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| distribution_values | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Verified values still required for: distribution_values, comparison_values.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: schedule_replacement_unproven.

**Ground truth** desired: _Catalog percentage distribution or Drake-versus-Future comparison_ — NOT IN SLATE. Recorded fallback: _review_.

## Passage 12 — Before-and-after ranking test

> Ab-Soul falls twenty-eight places. Latto falls thirteen. Jay Rock, twelve. Macklemore keeps seventy-three percent of his streams and drops three spots. Drake loses four point four billion streams, keeps ninety-seven percent of his total, and finishes exactly where he started.

**Job** rank · **Takeaway** Everyone else falls. He does not move.

**Audio** 191.67–211.98s (20.31s, alignment coverage 0.5909) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Ab-Soul falls twenty-eight places" | +0.37s | 0.913 | decisive |
| E2 | "Latto falls thirteen" | +3.37s | 0.929 | decisive |
| E3 | "Jay Rock, twelve" | +4.97s | 0.9 | decisive |
| E4 | "Macklemore keeps seventy-three percent" | +7.07s | 0.927 | decisive |
| E5 | "loses four point four billion streams" | +12.15s | 0.98 | decisive |
| E6 | "finishes exactly where he started" | +18.15s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| rank_deltas | proof | exact_source_required | data_required | — |
| entity_portraits | identity | exact_event_or_entity_required | partially_bound | Jay Rock, Latto, Macklemore |

### Candidates — 35 viable of 69, 34 gate-rejected · spatial_relationship_first fired via **base** rule 1.1.0-local on drops, falls

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | cinematic_3d | Before-and-after rank-loss field | spatial_relationship_first | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 2 | infographic | Period-by-period leaders | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 3 | infographic | Full-body portraits inside magnitude bars | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 4 | infographic | Five portrait headline values | rank | no_unsupported_implication, asset_quality_sufficient |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| rank_deltas | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Unbound: Jay Rock, Latto, Macklemore.
- Verified values still required for: rank_deltas.
- Winner has unresolved gates: asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven.

**Ground truth** desired: _Truthful before-and-after rank-loss field with Drake nearly fixed while peers fall_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 13 — Scale through comparison

> He has thirty songs past a billion streams. Thirty-five of the ninety-three rappers on the opening chart have zero. And eighty-one of the ninety-three don't have thirty billion streams across everything they've ever recorded.

**Job** quantify · **Takeaway** Thirty of his songs passed a billion, while most of the field has nothing close.

**Audio** 211.98–226.56s (14.58s, alignment coverage 0.75) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "thirty songs past a billion streams" | +0.8s | 1.0 | decisive |
| E2 | "Thirty-five of the ninety-three" | +4.42s | 1.0 | decisive |
| E3 | "eighty-one of the ninety-three" | +9.14s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| field_grid | proof | exact_source_required | data_required | — |

### Candidates — 31 viable of 60, 29 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Two-cohort ranked lists | rank | schedule_replacement_unproven |
| 2 | infographic | Contrasting ranked tables | rank | schedule_replacement_unproven |
| 3 | infographic | Two-panel trend comparison | rank | schedule_replacement_unproven |
| 4 | infographic | Annotated outlier scatter | rank | schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| field_grid | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Verified values still required for: field_grid.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: schedule_replacement_unproven.

**Ground truth** desired: _Artist grid highlighting 35 of 93, then 81 of 93_ — NOT IN SLATE. Recorded fallback: _review_.

## Passage 14 — Group-versus-group comparison

> Take his ten biggest. Then take the single biggest song from each of the next five artists and add those five together. His ten win, twenty-one billion to fifteen.

**Job** compare · **Takeaway** Ten of his songs outweigh the best song of each of the next five artists combined.

**Audio** 234.56–247.21s (12.65s, alignment coverage 0.8333) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Take his ten biggest" | +0.26s | 1.0 | decisive |
| E2 | "the single biggest song from each of the next five" | +3.28s | 1.0 | decisive |
| E3 | "twenty-one billion to fifteen" | +9.64s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| his_ten | comparison | exact_source_required | data_required | — |
| their_five | comparison | exact_source_required | data_required | — |
| portraits | identity | exact_event_or_entity_required | partially_bound | next five artists (unnamed in narration) |

### Candidates — 32 viable of 60, 28 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Six portrait value cards | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 2 | infographic | Full-body lineup with context figure | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 3 | infographic | Seven people-and-resources packages | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 4 | infographic | Two-group bar comparison | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Unbound: next five artists (unnamed in narration).
- Verified values still required for: his_ten, their_five.
- Winner has unresolved gates: asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven.

**Ground truth** desired: _One artist versus five artists, song lists, and 21B-versus-15B result_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 15 — Artifact then action claim

> In 2010, XXL offered him a spot on the Freshman cover. He turned it down.

**Job** evidence · **Takeaway** XXL offered him the 2010 Freshman cover and he refused it.

**Audio** 251.25–257.87s (6.62s, alignment coverage 1.0) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "XXL offered him a spot" | +1.85s | 1.0 | decisive |
| E2 | "He turned it down" | +5.25s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
Shot 02 holds 1.59s but refusal_proof needs 2.5s. **Extend by 0.91s; narration yields.**

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| xxl_cover_2010 | proof | exact_source_required | partially_bound | Freshman, XXL |
| refusal_proof | proof | exact_source_required | missing | a source for refusal_proof |

### Candidates — 83 viable of 116, 33 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | after_effects | Intro Slideshow · Scene 02 | approved family: magazine_or_document_presentation | no_unsupported_implication, decisive_events_alignable, asset_quality_sufficient, era_consistent |
| 2 | after_effects | History Slideshow · Scene 11 | approved family: magazine_or_document_presentation | no_unsupported_implication, decisive_events_alignable, asset_quality_sufficient, era_consistent |
| 3 | after_effects | The History · SEQ_8 | approved family: magazine_or_document_presentation | no_unsupported_implication, decisive_events_alignable, asset_quality_sufficient, era_consistent |
| 4 | infographic | Quotes with supporting score columns | rank | no_unsupported_implication, asset_quality_sufficient, era_consistent |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| xxl_cover_2010 | media_library | /Users/dwaynetoler/Media Library | editorial choice |
| refusal_proof | unknown | NOT YET SOURCED | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Unbound: Freshman, XXL, a source for refusal_proof.
- Shot 02 must extend 0.91s so refusal_proof can complete.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: no_unsupported_implication, decisive_events_alignable, asset_quality_sufficient, era_consistent.

**Ground truth** desired: _XXL cover, then screenshot or footage proving he turned it down_ — in slate at rank 1. Recorded fallback: _artist portrait, flagged for review_.

## Passage 16 — Historical cohorts

> The rappers on that cover, and on the one the year before, came up on the same clock he did. 2009: Kid Cudi, B.o.B, Wale, Curren$y. 2010: J. Cole, Nicki Minaj, Wiz Khalifa, Big Sean, Nipsey Hussle, Jay Rock, Freddie Gibbs.

**Job** compare · **Takeaway** The 2009 and 2010 Freshman classes came up on the same clock he did.

**Audio** 257.87–281.02s (23.15s, alignment coverage 0.907) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "2009: Kid Cudi, B.o.B, Wale, Curren$y" | +7.61s | 0.781 | decisive |
| E2 | "2010: J. Cole, Nicki Minaj, Wiz Khalifa" | +12.93s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| xxl_covers | proof | exact_source_required | partially_bound | Freshman, XXL |

### Candidates — 45 viable of 81, 36 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | after_effects | Intro Slideshow · Scene 02 | approved family: magazine_or_document_presentation | asset_quality_sufficient, decisive_events_alignable, era_consistent, no_unsupported_implication, schedule_replacement_unproven |
| 2 | after_effects | History Slideshow · Scene 11 | approved family: magazine_or_document_presentation | asset_quality_sufficient, decisive_events_alignable, era_consistent, no_unsupported_implication, schedule_replacement_unproven |
| 3 | after_effects | The History · SEQ_8 | approved family: magazine_or_document_presentation | asset_quality_sufficient, decisive_events_alignable, era_consistent, no_unsupported_implication, schedule_replacement_unproven |
| 4 | infographic | Two-panel trend comparison | rank | asset_quality_sufficient, era_consistent, no_unsupported_implication, schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| xxl_covers | media_library | /Users/dwaynetoler/Media Library | editorial choice |

**Decision** `blocked_script_conflict` · confidence `uncalibrated_prior`

- User recorded inaccurate information in this passage's text. Verify each named artist against the actual 2009 and 2010 covers before rendering.
- Unbound: Freshman, XXL.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: asset_quality_sufficient, decisive_events_alignable, era_consistent, no_unsupported_implication, schedule_replacement_unproven.

**Ground truth** desired: _2009 and 2010 XXL covers inside an AE scene_ — in slate at rank 1. Recorded fallback: _grouped artist cutouts_.

## Passage 17 — Methodology rule

> One rule, applied to everybody. A record you lead, or share the lead on equally, counts in full. A feature or a remix verse counts at half.

**Job** evidence · **Takeaway** One counting rule, applied to everyone: full credit for a lead, half for a feature.

**Audio** 284.24–295.63s (11.39s, alignment coverage 1.0) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "One rule, applied to everybody" | +0.38s | 1.0 | supporting |
| E2 | "counts in full" | +6.3s | 1.0 | decisive |
| E3 | "counts at half" | +10.08s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| rules_text | subject | exact_source_required | generated_or_authored | — |

### Candidates — 2 viable of 112, 110 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | direct | Low-motion text card | rank | none |
| 2 | direct | Evidence hold with highlight | rank | none |

**Decision** `auto_advance` · confidence `uncalibrated_prior`

- Only 2 meaningfully different valid treatments exist; the slate is not padded.

**Ground truth** desired: _Simple readable rules text_ — in slate at rank 1. Recorded fallback: _plain text card_.

## Passage 18 — Class total

> That's the 2010 class under the rule. Nicki at thirty billion. Cole at twenty-nine. Stack all seven end to end. Ninety-seven billion. Seven careers.

**Job** quantify · **Takeaway** The whole 2010 class together comes to 97 billion across seven careers.

**Audio** 295.63–309.88s (14.25s, alignment coverage 0.8148) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Nicki at thirty billion" | +3.23s | 1.0 | decisive |
| E2 | "Cole at twenty-nine" | +5.41s | 1.0 | decisive |
| E3 | "Ninety-seven billion" | +10.67s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| class_totals | proof | exact_source_required | data_required | — |
| class_portraits | identity | exact_event_or_entity_required | missing | the 2010 Freshman class |

### Candidates — 32 viable of 60, 28 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Hero-led seven-entry leaderboard | rank | no_unsupported_implication, schedule_replacement_unproven |
| 2 | infographic | Seven photo panels with metrics and ranks | rank | no_unsupported_implication, schedule_replacement_unproven |
| 3 | infographic | Long signed-value history with outlier | rank | no_unsupported_implication, schedule_replacement_unproven |
| 4 | infographic | Seven people-and-resources packages | rank | no_unsupported_implication, schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| class_totals | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Unbound: the 2010 Freshman class.
- Verified values still required for: class_totals.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: no_unsupported_implication, schedule_replacement_unproven.

**Ground truth** desired: _Artist list or table with totals and 97B emphasized_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 19 — One artist versus class

> Ninety-six and a half billion. His own records, nothing else, are the whole class. Seven rappers with everything they have ever made against one man with only the songs that carry his name first, and it comes down to a coin flip.

**Job** compare · **Takeaway** His lead records alone nearly equal seven whole careers.

**Audio** 330.38–346.97s (16.59s, alignment coverage 0.9535) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Ninety-six and a half billion" | +0.36s | 1.0 | decisive |
| E2 | "Seven rappers with everything they have ever made" | +6.5s | 1.0 | decisive |
| E3 | "it comes down to a coin flip" | +14.5s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| hero_total | proof | exact_source_required | data_required | — |
| class_totals | comparison | exact_source_required | data_required | — |
| hero_and_class | identity | exact_event_or_entity_required | partially_bound | the 2010 class, seven rappers |

### Candidates — 33 viable of 60, 27 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Eight portrait columns with paired counts | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 2 | infographic | Endpoint portraits on horizontal bars | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 3 | infographic | Two-group bar comparison | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 4 | infographic | Candidate scores with visible criteria | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| hero_total | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Unbound: the 2010 class, seven rappers.
- Verified values still required for: hero_total, class_totals.
- Winner has unresolved gates: asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven.

**Ground truth** desired: _Artist cutout, records list, and 96.5B headline value_ — in slate at rank 4. Recorded fallback: _review_.

## Passage 20 — One slice versus full catalogs

> That's the class. Now put the same slice against the names near the top of the opening chart, full catalogs, everything at full credit. Travis Scott, sixty-seven billion. Kendrick, fifty-seven. Post Malone, fifty-six. Future, fifty-four. The slice clears every one of them.

**Job** compare · **Takeaway** His lead-credit slice alone beats four full catalogs from the top of the chart.

**Audio** 346.97–370.7s (23.73s, alignment coverage 0.8298) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Travis Scott, sixty-seven billion" | +9.93s | 1.0 | decisive |
| E2 | "Kendrick, fifty-seven" | +13.67s | 1.0 | decisive |
| E3 | "Post Malone, fifty-six" | +16.09s | 1.0 | decisive |
| E4 | "The slice clears every one of them" | +21.51s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| catalog_totals | proof | exact_source_required | data_required | — |
| peer_portraits | identity | exact_event_or_entity_required | partially_bound | Post Malone |

### Candidates — 35 viable of 69, 34 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | cinematic_3d | Fixed-scale small-field outlier | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 2 | infographic | Five portrait headline values | rank | no_unsupported_implication, asset_quality_sufficient |
| 3 | infographic | Full-body portraits inside magnitude bars | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 4 | infographic | Full-body lineup with context figure | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| catalog_totals | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Unbound: Post Malone.
- Verified values still required for: catalog_totals.
- Winner has unresolved gates: asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven.

**Ground truth** desired: _One Drake slice versus four full catalogs, including a truthful 3D gap candidate_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 21 — Accusation tested with evidence

> He gets accused of living on features. He's done a hundred and eighty-one of them. Future has done two hundred thirty-two. Young Thug, three hundred and two. Fewer verses than either, more streams than anyone: forty-three billion, roughly two hundred forty million a verse.

**Job** compare · **Takeaway** He has fewer feature verses than his peers and far more streams from them.

**Audio** 398.22–419.28s (21.06s, alignment coverage 0.625) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "He's done a hundred and eighty-one of them" | +2.78s | 0.714 | decisive |
| E2 | "Future has done two hundred thirty-two" | +5.48s | 1.0 | decisive |
| E3 | "Young Thug, three hundred and two" | +8.3s | 0.824 | decisive |
| E4 | "forty-three billion" | +15.98s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| feature_counts | proof | exact_source_required | data_required | — |
| three_portraits | identity | exact_event_or_entity_required | bound_local | — |

### Candidates — 36 viable of 92, 56 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Three multi-metric subject cards | rank | schedule_replacement_unproven |
| 2 | infographic | Three-row portrait metric table | rank | schedule_replacement_unproven |
| 3 | infographic | Full-body magnitude comparison | rank | schedule_replacement_unproven |
| 4 | infographic | Three group-achievement cards | rank | schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| feature_counts | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Verified values still required for: feature_counts.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: schedule_replacement_unproven.

**Ground truth** desired: _Three-artist infographic or three-slot AE portrait scene with nearby values_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 22 — Result turns against subject

> There's one place the comparison turns on him. Add the 2009 class to the 2010 class, eleven rappers under the rule, and together they edge him by about three percent. Eleven careers to one, and it's close.

**Job** compare · **Takeaway** Both Freshman classes combined only just edge past him.

**Audio** 426.37–442.31s (15.94s, alignment coverage 0.8974) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "eleven rappers under the rule" | +6.75s | 1.0 | decisive |
| E2 | "they edge him by about three percent" | +9.07s | 0.98 | decisive |
| E3 | "Eleven careers to one, and it's close" | +11.65s | 0.933 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| combined_totals | proof | exact_source_required | data_required | — |
| eleven_portraits | identity | exact_event_or_entity_required | partially_bound | the combined 2009 and 2010 classes, eleven rappers |

### Candidates — 32 viable of 60, 28 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Portrait metric matrix | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 2 | infographic | Two-lane event timeline | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 3 | infographic | Seven pairwise outcomes with hero | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 4 | infographic | Period-by-period leaders | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| combined_totals | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Unbound: the combined 2009 and 2010 classes, eleven rappers.
- Verified values still required for: combined_totals.
- Winner has unresolved gates: asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven.

**Ground truth** desired: _One individual versus the combined 2009 and 2010 classes_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 23 — Archive-on-autoplay hypothesis

> A song from 2015 streams in 2026 without the artist lifting a finger. Music has no body that gives out. So the top of the daily chart in year seventeen could be a very large archive on autoplay while the man himself stopped mattering somewhere around Views.

**Job** evidence · **Takeaway** A 2015 song still streams in 2026 without the artist doing anything, so the chart may be an archive on autoplay.

**Audio** 457.37–478.26s (20.89s, alignment coverage 0.7872) · **Strictest obligation** exact_event_or_entity_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "A song from 2015 streams in 2026" | +0.39s | 1.0 | decisive |
| E2 | "a very large archive on autoplay" | +14.35s | 0.871 | decisive |
| E3 | "stopped mattering somewhere around Views" | +18.13s | 1.0 | supporting |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| song_2015_footage | subject | exact_event_or_entity_required | bound_local | — |
| hypothesis_text | context | exact_source_required | generated_or_authored | — |

### Candidates — 46 viable of 46, 0 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | after_effects | Documentary Promo · Scene 02 | rank | decisive_events_alignable, schedule_replacement_unproven |
| 2 | after_effects | History and Documentary — 10 slides · Scene 1 | rank | decisive_events_alignable, schedule_replacement_unproven |
| 3 | after_effects | History and Documentary — 20 slides · Scene 16 | rank | decisive_events_alignable, schedule_replacement_unproven |
| 4 | after_effects | Memories Photo Slideshow — Creative Slides · Scene 02 | rank | decisive_events_alignable, schedule_replacement_unproven |

**Decision** `require_user_review` · confidence `uncalibrated_prior`

- Top two candidates are tied on every priority level.
- Winner has unresolved gates: decisive_events_alignable, schedule_replacement_unproven.

**Ground truth** desired: _Relevant 2015 music-video footage inside the animation with text overlay_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 24 — Timeline prediction

> If he'd gone quiet there's one place it shows up first. New records either chart or they don't. Seventeen years since So Far Gone. Pick the year the ticks stop lighting.

**Job** timeline · **Takeaway** Almost everyone present at the start is gone seventeen years later, and he is not.

**Audio** 480.7–494.89s (14.19s, alignment coverage 0.9706) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "New records either chart or they don't" | +5.08s | 1.0 | decisive |
| E2 | "Seventeen years since So Far Gone" | +8.44s | 1.0 | decisive |
| E3 | "Pick the year the ticks stop lighting" | +11.38s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| cohort_roster | proof | exact_source_required | data_required | — |
| cohort_portraits | identity | exact_event_or_entity_required | partially_bound | the 2009 starting cohort |
| year_anchor | chronology | exact_source_required | generated_or_authored | — |

### Candidates — 36 viable of 69, 33 gate-rejected · spatial_relationship_first fired via **overlay** rule 1.1.0-local on survivors, thins

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | cinematic_3d | Cohort attrition to named survivors | spatial_relationship_first | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 2 | infographic | Portrait metric matrix | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 3 | infographic | Two-lane event timeline | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 4 | infographic | Period-by-period leaders | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| cohort_roster | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Unbound: the 2009 starting cohort.
- Verified values still required for: cohort_roster.
- Winner has unresolved gates: asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven.

**Ground truth** desired: _Cohort attrition timeline with the starting field visible and only verified survivors remaining_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 25 — Longevity reveal

> They don't stop. Eighteen straight years with something on a US chart, and one other rapper in the set has that streak — J. Cole, off the cover he turned down.

**Job** timeline · **Takeaway** He has eighteen straight charting years, and only J. Cole matches it.

**Audio** 494.89–507.95s (13.06s, alignment coverage 0.9677) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Eighteen straight years with something on a US chart" | +2.17s | 1.0 | decisive |
| E2 | "J. Cole, off the cover he turned down" | +9.47s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| streak_timeline | proof | exact_source_required | data_required | — |
| two_artists | identity | exact_event_or_entity_required | bound_local | — |

### Candidates — 37 viable of 126, 89 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Two-panel trend comparison | rank | none |
| 2 | infographic | Long bar history with threshold | rank | none |
| 3 | infographic | Period-by-period leaders | rank | none |
| 4 | infographic | Round-by-round scorecard | rank | none |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| streak_timeline | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Verified values still required for: streak_timeline.
- Top two candidates are tied on every priority level.

**Ground truth** desired: _Continue timeline, then show Drake and J. Cole together_ — in slate at rank 1. Recorded fallback: _two-person comparison plot_.

## Passage 26 — Categorized achievements

> Number one as a lead single. Eleven times. Number one as an album. Nine. Number one as somebody else's guest. Four. Number one as a mixtape. Three. Number one as a joint album. Two. Number one as a compilation. One.

**Job** rank · **Takeaway** He has number ones in six separate categories, leading each.

**Audio** 510.94–532.04s (21.1s, alignment coverage 0.8293) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Number one as a lead single. Eleven times" | +0.6s | 1.0 | decisive |
| E2 | "Number one as an album. Nine" | +4.72s | 0.955 | decisive |
| E3 | "Number one as a compilation. One" | +17.48s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| category_records | proof | exact_source_required | data_required | — |

### Candidates — 34 viable of 60, 26 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Period-by-period leaders | rank | schedule_replacement_unproven |
| 2 | infographic | Annotated outlier scatter | rank | schedule_replacement_unproven |
| 3 | infographic | Two-cohort ranked lists | rank | schedule_replacement_unproven |
| 4 | infographic | Recognition ledger and value profile | rank | schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| category_records | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Verified values still required for: category_records.
- Winner has unresolved gates: schedule_replacement_unproven.

**Ground truth** desired: _Multiple category tables with the subject leading each category_ — in slate at rank 4. Recorded fallback: _review_.

## Passage 27 — Opposing artist archetypes

> The ones who carry their own records — Post Malone, forty-nine billion on his own songs against six as a guest. XXXTentacion, thirty-five and six. Kendrick, forty-one and sixteen. And the ones who live on other people's hooks. Ty Dolla $ign, five billion on his own records and twenty-two as a guest. Young Thug, eleven and twenty-one. 21 Savage, sixteen and twenty-three.

**Job** compare · **Takeaway** Some artists carry their own records and others live on other people's, and the split is stark.

**Audio** 567.21–603.15s (35.94s, alignment coverage 0.7206) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Post Malone, forty-nine billion on his own songs" | +3.43s | 1.0 | decisive |
| E2 | "And the ones who live on other people's hooks" | +18.55s | 1.0 | decisive |
| E3 | "21 Savage, sixteen and twenty-three" | +31.69s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| paired_values | proof | exact_source_required | data_required | — |
| six_portraits | identity | exact_event_or_entity_required | partially_bound | Post Malone, Ty Dolla $ign, XXXTentacion |

### Candidates — 32 viable of 60, 28 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | infographic | Six portrait value cards | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 2 | infographic | Full-body lineup with context figure | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 3 | infographic | Seven people-and-resources packages | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |
| 4 | infographic | Two-group bar comparison | rank | asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| paired_values | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Unbound: Post Malone, Ty Dolla $ign, XXXTentacion.
- Verified values still required for: paired_values.
- Winner has unresolved gates: asset_quality_sufficient, no_unsupported_implication, schedule_replacement_unproven.

**Ground truth** desired: _Artist table with lead-song and guest-song data beside portraits_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 28 — Overlap and spatial relationship

> Two floors, fixed before the names go in. Thirty billion on your own records. Twenty billion on everyone else's. Five clear the left floor. Seven clear the right. Panels come together and two names are standing in the middle. Drake. And Travis Scott.

**Job** compare · **Takeaway** Two thresholds are set in advance, and only two names clear both.

**Audio** 613.89–636.33s (22.44s, alignment coverage 0.9216) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Two floors, fixed before the names go in" | +0.53s | 1.0 | decisive |
| E2 | "Five clear the left floor. Seven clear the right" | +12.77s | 1.0 | decisive |
| E3 | "Drake. And Travis Scott" | +20.59s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| threshold_field | proof | exact_source_required | data_required | — |
| overlap_pair | identity | exact_event_or_entity_required | bound_local | — |

### Candidates — 36 viable of 69, 33 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | cinematic_3d | Fixed-scale one-dot-per-entity population field | rank | density_acceptable, schedule_replacement_unproven |
| 2 | infographic | Portrait metric matrix | rank | schedule_replacement_unproven |
| 3 | infographic | Two-panel trend comparison | rank | schedule_replacement_unproven |
| 4 | infographic | Annotated outlier scatter | rank | schedule_replacement_unproven |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| threshold_field | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_missing_assets` · confidence `uncalibrated_prior`

- Verified values still required for: threshold_field.
- Winner has unresolved gates: density_acceptable, schedule_replacement_unproven.

**Ground truth** desired: _Threshold overview followed by a nonnumeric two-person portrait comparison_ — NOT IN SLATE. Recorded fallback: _review_.

## Passage 29 — Counterevidence and boundary

> Lil Baby is certifying his own records at a faster yearly clip than Drake has averaged across the whole run — about twenty-two million units a year against twenty and a half. Kendrick, Post Malone and Travis Scott have each put five lead singles at number one. Best rapper alive is an argument, and this chart can't referee it. It counts plays. That's the whole job.

**Job** compare · **Takeaway** Others beat him on specific measures, and this chart cannot settle who is best.

**Audio** 689.02–723.68s (34.66s, alignment coverage 0.9468) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "Lil Baby is certifying his own records at a faster yearly clip" | +0.46s | 1.0 | decisive |
| E2 | "about twenty-two million units a year against twenty and a half" | +6.94s | 1.0 | decisive |
| E3 | "this chart can't referee it" | +29.52s | 1.0 | decisive |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| lil_baby_portrait | identity | exact_event_or_entity_required | bound_local | — |
| relationship_footage | subject | exact_event_or_entity_required | partially_bound | Post Malone |
| comparison_values | proof | exact_source_required | data_required | — |

### Candidates — 53 viable of 86, 33 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | after_effects | History and Documentary — 10 slides · Scene 2 | approved family: single_portrait_with_side_text | decisive_events_alignable |
| 2 | after_effects | History Slideshow · Scene 08 | approved family: single_portrait_with_side_text | decisive_events_alignable |
| 3 | after_effects | Intro Slideshow · Scene 22 | approved family: single_portrait_with_side_text | decisive_events_alignable |
| 4 | infographic | One subject across two conditions | rank | none |

### Evidence sources recorded

Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.

| Role | Provenance | Source | On-screen credit |
|---|---|---|---|
| comparison_values | unknown | verified dataset, not yet bound | editorial choice |

**Decision** `blocked_script_conflict` · confidence `uncalibrated_prior`

- User recorded 'not clear on what this is or means' against this passage's second shot. Clarify what the second shot is meant to show before rendering.
- Unbound: Post Malone.
- Verified values still required for: comparison_values.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: decisive_events_alignable.

**Ground truth** desired: _Lil Baby portrait, Drake and Lil Baby relationship footage, then a two-person comparison graphic_ — in slate at rank 1. Recorded fallback: _review_.

## Passage 30 — Measurement limitation

> And the rappers this should really be measured against — the ones whose seventeenth year happened before streaming counted anything — can't go on this chart at all. There's no daily meter for Jay-Z's year seventeen. So *unprecedented* only reaches back as far as the streaming era, and that's as far as I'm taking it.

**Job** sequence · **Takeaway** Pre-streaming careers cannot be measured, so the claim is bounded to the streaming era.

**Audio** 784.17–804.36s (20.19s, alignment coverage 0.9153) · **Strictest obligation** exact_source_required

### Phrase-aligned events

| Event | Trigger phrase | Measured offset | Match | Criticality |
|---|---|---|---|---|
| E1 | "can't go on this chart at all" | +7.03s | 1.0 | decisive |
| E2 | "no daily meter for Jay-Z's year seventeen" | +10.81s | 0.939 | decisive |
| E3 | "that's as far as I'm taking it" | +18.57s | 1.0 | supporting |

**Duration policy** elastic, evidence must complete. 
No extension required.

### Media roles

| Role | Editorial role | Specificity | Status | Missing |
|---|---|---|---|---|
| named_historical_artist | subject | exact_event_or_entity_required | bound_local | — |

### Candidates — 51 viable of 110, 59 gate-rejected

| Rank | Kind | Container | Placed by | Unresolved gates |
|---|---|---|---|---|
| 1 | after_effects | Documentary Promo · Scene 02 | rank | decisive_events_alignable, schedule_replacement_unproven |
| 2 | after_effects | History and Documentary — 10 slides · Scene 1 | rank | decisive_events_alignable, schedule_replacement_unproven |
| 3 | after_effects | History and Documentary — 20 slides · Scene 16 | rank | decisive_events_alignable, schedule_replacement_unproven |
| 4 | infographic | Period-by-period leaders | rank | schedule_replacement_unproven |

**Decision** `blocked_script_conflict` · confidence `uncalibrated_prior`

- The recorded desired outcome asks for a five-slot scene using named historical artists. The narration names one. Hold for script clarification. Either the script names four more artists or the visual drops to one.
- Top two candidates are tied on every priority level.
- Winner has unresolved gates: decisive_events_alignable, schedule_replacement_unproven.

**Ground truth** desired: _Five-slot AE scene or five continuous portrait shots using named historical artists_ — in slate at rank 1. Recorded fallback: _hold for script clarification; the narration names only Jay-Z but the intended visual needs five historical artists_.
