From:    codex
Date:    2026-09-20 13:17
Subject: Completed beat-to-visual review and Year Seventeen second opinion
Replies-to: HANDOFF-codex-second-brain.md

# Second opinion and completed beat-to-visual review

Read-only review of `~/timeline`, the Polish selection policy, and the completed editorial review in **Automate After Effects templates**. No model call, render, catalog edit, or selector change was made. The retrieval result and decision store were joined by beat ID and candidate ID; their recorded SHA-256 link matches. Decision store: `ae-template-automation/scene-library/approved/embedding-review-decisions.json`, last updated 2026-09-20 17:05 UTC. Frozen retrieval result: `ae-template-automation/selector-prototype/retrieval/beat-match-test-2026-09-20/embedding-beat-matches.json`.

## How the candidates were selected (the RAG pilot)

This was the **retrieval stage of a possible RAG workflow**, not a generated answer or production selector. The existing approved gallery and ingest-valid Google capability observations were consolidated without changing source descriptions. The index held 421 eligible AE scenes, infographic layouts, and spatial layouts. Forty narration beats supplied queries. The source export recorded 95 gallery cards, 375 AE scene records, and 208 Google observations; 101 of the 207 returned options carried a Google observation.

For each beat, the program first kept candidates with an existing, provenance-validated communication-job binding. It then ran the existing subject-capacity screen, placing feasible or unknown shapes ahead of outside-capacity shapes while retaining and flagging the latter. Within those bands it ranked by cosine similarity of **local** macOS NaturalLanguage English word embeddings. Candidate text combined title, scene description, use case/narration, encoding, and available Google capability fields. Query text combined the beat's job, narration, takeaway, `must_be_perceptible`, `must_be_true`, and entity count. The Swift adapter tokenized alphabetic words, took an IDF-weighted mean of 300-dimensional word vectors, and normalized the vectors. A score is therefore a lexical-semantic retrieval signal, not a fit probability. The selection kept the highest-ranking scene from each distinct template, excluded known prior per-beat rejections, and returned at most six options. Earlier picks were not directly boosted in ranking, but the job bindings themselves include earlier user picks, so the pilot is not an independent holdout. Negative `would_be_a_lie` constraints were displayed as review flags but **not** used in ranking or gating. Binding conditions were also displayed, not tested against the beat.

The local reviewer attached existing motion previews to all 207 options: 103 distinct MP4s from original AE scene excerpts or established infographic/spatial systems, with no missing media in the current review packet. It saved per-beat/per-candidate Approve or Deny decisions with revision checks, without authorizing a render. An attempted external OpenAI embedding call was rejected by automatic approval review because it would transmit non-public beat and catalog text; this pilot used only the local model. The local tokenizer discards digits and word order, a material limitation for years, thresholds, ratios, and “missing rather than zero” claims.

## Completed review and deny accounting

**Rule applied as requested:** a saved `editorial_deny` is an explicit denial. Every option without a saved `editorial_approve` is also counted as denied for this completed review, including options with no saved click. A beat with no approved scene clip is a denied beat. This inferred-deny category is kept separate from explicit human clicks. Zero beats had no retrieved clips or missing review media, so the no-clips branch of the rule adds no cases here.

| Measure | Result |
| --- | ---: |
| Beats / retrieved options | 40 / 207 |
| Saved human approvals | 66 (31.9% of options) |
| Saved explicit human denials | 5 |
| No saved approval, counted as denied under the requested rule | 136 |
| Total denied options under the rule | 141 (68.1%) |
| Beats with at least one approved clip | 32 |
| Beats denied because no clip was approved | 8: `02b`, `11a`, `23`, `27`, `28`, `29c`, `30a`, `30b` |
| Top-ranked candidate approved | 14 of 40 beats |
| Beats with fewer than six retrieved options | 13 |
| Beats with six editorial approvals | 1 (`02a`); these are still not six final validated choices |

The five explicit denials are both candidates for `02b` and three infographic candidates for `04`. All other nonapprovals below are **inferred denials under the user's accounting rule**, not recorded Deny clicks. Approval counts by visual system are 36 AE, 17 infographic, and 13 spatial. The 8 denied beats had 37 retrieved options in total: 2 explicit denials and 35 inferred denials.

### Beat-by-beat ledger

The `Approved candidate IDs` column is the complete positive set. Every other candidate in the frozen retrieval result is denied under the requested rule. `Explicit` counts saved Deny clicks; `Inferred` counts absent approvals.

| Beat | Options | Approved | Explicit | Inferred | Approved candidate IDs |
| --- | ---: | ---: | ---: | ---: | --- |
| `01` | 4 | 1 | 0 | 3 | `counters-envato--scene-001` |
| `02a` | 6 | 6 | 0 | 0 | `07-history-slideshow--scene-003`, `archive3-photo-slideshow-final--review-004`, `photo-slideshow--review-050b`, `history-slideshow-envato--scene-007`, `minimalism-slideshow--review-008`, `screen-mockup-rfx--review-008` |
| `02b` | 2 | 0 | 2 | 0 | **None — denied beat** |
| `03` | 2 | 1 | 0 | 1 | `truth-population-field` |
| `04` | 4 | 1 | 3 | 0 | `truth-population-field` |
| `05a` | 6 | 1 | 0 | 5 | `truth-population-field` |
| `05b` | 6 | 3 | 0 | 3 | `photo-slideshow--review-050b`, `story-on-photo-slideshow-envato--scene-004`, `07-history-slideshow--scene-018` |
| `06` | 6 | 1 | 0 | 5 | `intro-slideshow-full-720p--scene-040` |
| `07` | 6 | 4 | 0 | 2 | `intro-slideshow-full-720p--scene-036`, `archive3-gallery-pro-carousel-2026-09-11-10-23-37-utc--review-001`, `carousel--review-012b`, `photo-slideshow-memories-envato--scene-005` |
| `08` | 6 | 1 | 0 | 5 | `06_historical_winners_table` |
| `09` | 6 | 2 | 0 | 4 | `archive3-infographic-bar-charts--review-001`, `photo-slideshow-memories-envato--scene-003` |
| `10` | 6 | 1 | 0 | 5 | `text-list-carousel--review-001` |
| `11a` | 3 | 0 | 0 | 3 | **None — denied beat** |
| `11b` | 6 | 2 | 0 | 4 | `55_best_vs_value`, `45_two_metric_tables` |
| `12a` | 6 | 2 | 0 | 4 | `truth-rank-fall`, `truth-cohort-attrition` |
| `12b` | 6 | 1 | 0 | 5 | `truth-population-field` |
| `13a` | 6 | 3 | 0 | 3 | `truth-population-field`, `archive3-infographic-bar-charts--review-006`, `50_championship_odds_history` |
| `13b` | 6 | 2 | 0 | 4 | `truth-population-field`, `09_artist_field_grid` |
| `14` | 3 | 1 | 0 | 2 | `46_similarity_criteria_table` |
| `15` | 6 | 4 | 0 | 2 | `history-slideshow-envato--scene-011`, `07-history-slideshow--scene-009`, `minimalism-slideshow--review-008`, `memories-photo-slideshow-creative-slides-envato--scene-004` |
| `16` | 6 | 4 | 0 | 2 | `archive3-gallery-pro-carousel-2026-09-11-10-23-37-utc--review-001`, `archive3-carousel-photo-logo-reveal-2026-09-13-12-24-28-utc--review-v2-001`, `scrolling-screen--review-006`, `carousel-slideshow--review-001` |
| `17` | 6 | 1 | 0 | 5 | `text-list-carousel--review-001` |
| `18` | 3 | 1 | 0 | 2 | `57_three_playoff_run_cards` |
| `19` | 3 | 2 | 0 | 1 | `51_debut_leaderboard`, `53_lineup_rotation_columns` |
| `20` | 6 | 2 | 0 | 4 | `archive3-infographic-bar-charts--review-006`, `truth-small-outlier` |
| `21a` | 6 | 4 | 0 | 2 | `memories-photo-slideshow-creative-slides-envato--scene-006`, `36_four_portrait_cards`, `truth-small-outlier`, `photo-slideshow-memories-envato--scene-001` |
| `21b` | 5 | 3 | 0 | 2 | `counters-envato--scene-003`, `truth-ratio-days`, `archive3-number-count-pack-2026-09-13-15-09-11-utc--review-004` |
| `22` | 4 | 2 | 0 | 2 | `truth-population-field`, `51_debut_leaderboard` |
| `23` | 6 | 0 | 0 | 6 | **None — denied beat** |
| `24` | 6 | 1 | 0 | 5 | `scrolling-screen--review-004` |
| `25a` | 6 | 2 | 0 | 4 | `25_career_value_list`, `24_dense_vertical_bars` |
| `25b` | 6 | 2 | 0 | 4 | `photo-slideshow-memories-envato--scene-002`, `truth-population-field` |
| `26` | 4 | 2 | 0 | 2 | `53_lineup_rotation_columns`, `56_seven_artist_stat_lineup` |
| `27` | 4 | 0 | 0 | 4 | **None — denied beat** |
| `28` | 4 | 0 | 0 | 4 | **None — denied beat** |
| `29a` | 6 | 1 | 0 | 5 | `44_three_metric_tables` |
| `29b` | 6 | 2 | 0 | 4 | `carousel--review-001`, `57_three_playoff_run_cards` |
| `29c` | 6 | 0 | 0 | 6 | **None — denied beat** |
| `30a` | 6 | 0 | 0 | 6 | **None — denied beat** |
| `30b` | 6 | 0 | 0 | 6 | **None — denied beat** |

## What I find in the completed review

1. **The score is not a selection rule.** Mean cosine similarity is 0.8703 for approved options and 0.8695 for options without a saved decision, effectively identical in this sample. The first-ranked option was approved on 14/40 beats. This is descriptive, not a formal held-out accuracy estimate, because bindings and prior picks influenced the candidate pool and the user did not record explicit clicks on every option.
2. **The broad `assert_without_data` job failed its actual scenes.** Beats `23`, `29c`, and `30a` each received six high-similarity candidates and zero approvals (18 inferred denials). The underlying claims differ: persistent old-catalog streams, a chart's inability to judge “best,” and missing pre-streaming data. This is direct review evidence for separating those visual operations rather than trusting the shared job label.
3. **Several other concrete gaps remain.** `02b` received two explicit denials for its 24-day equivalence; `11a` had no approved one-versus-aggregate treatment; `27` had no approved six-artist inversion; `28` had no approved two-threshold intersection; `30b` had no approved scope-definition clip. All eight beats need fresh candidate discovery and claim-specific review, not automatic reuse of the rejected slate.
4. **Capacity should remain a flag rather than a veto.** Ten approved options carry `outside` capacity flags. That is evidence that the screen is imperfect as a retrieval exclusion. Their native adjustments are still unverified, so the approvals do not prove render fit. Of 47 outside-capacity options, 10 were approved.
5. **Old-pick recall is a weak proxy for this review.** The pilot reported prior-pick overlap on 28/33 beats with prior picks, but `02b`, `11a`, and `28` retrieved prior picks and now have zero approvals; conversely, `02a` retrieved none of its old picks and the user approved all six new options. Judge future retrieval against the new explicit review ledger, while preserving the distinction between saved clicks and inferred denials.
6. **Editorial approval is not final template validation.** The review did not execute beat-specific false-implication checks, verify conditional bindings, native edit controls, readability, or phrase timing. Even `02a`'s six approvals do not meet the six distinct **validated** existing-template choices required by the Polish final-render gate. No render is authorized.

## The finding that precedes the four questions

The current slate builder cannot enforce the stated objective that no option communicate something false about a beat. `pipeline/shotlist.py` looks up candidates by the beat's job, admits flagged match cuts, routes spatial scenes, ranks declared capacity, and diversifies. It copies `must_be_true`, `must_be_perceptible`, `would_be_a_lie`, and `unstated` into the resulting shot record **after** the slate is chosen (lines 127–163). It also copies a binding's free-text `condition` into an option; no step evaluates that condition against the beat. In the current merged grammar, 41 of the 43 `assert_without_data` bindings are conditional. Their conditions do not gate display.

This is a mechanism-level gap, not a bad threshold. The offline binder sees generic jobs, not the specific beat. `30-30a` requires Jay-Z's missing measurement to read as absent rather than zero, but the slate path has no check for that distinction. No choice of 43 versus 254 job bindings can by itself satisfy the no-false-implication requirement.

## 1. Per-job merge

**Legitimate as a named, reversible rollback; not validated as a better grammar.** `pipeline/salvage_bindings.py` chose old versus new per job using flood and collapse cutoffs written after viewing this run. Its six tests show that this rule executes; they cannot show that a reverted job is more accurate. The merged 595 bindings contain 333 from the current prompt, 241 from two older prompts, and 21 user-sourced rows. Provenance is intact, but the rows do not share one interpretation of template adaptation.

The reported survival of all 61 user selections is a preservation check, not evidence that the model improved. `pipeline/bind.py::_user_named()` inserts earlier selections into each run, and `match-trial/candidates.py::diversify()` visits families with any earlier user pick first. The prior timeline review measured its earlier slate (33/40 beats served, 61/199 shown options accepted). The completed embedding-gallery review above judged a **different** 207-option retrieval set; it does not validate the new or merged timeline slates. The merged slate shows 328 option slots versus 259 before it; that is increased review load, not a measured quality gain.

Keep the merge clearly labeled provisional if it is needed to avoid losing known options. Do not present 595, no-flood, or pick reachability as proof of precision. Compare proposed changes against a fresh, held-out beat review before promoting one grammar.

## 2. Dressing versus mechanic

The distinction catches some real category errors: changing colors or media cannot turn an identity sequence into a magnitude comparison. It is insufficient as the whole guard. A source-footage sequence might illustrate a hypothetical claim, but footage alone does not establish that the claim is typical; a graphic might show a missing observation only if the replacement treatment preserves the difference between missing and zero.

For each proposed binding, require a **constructive treatment account**: which existing visual relationship carries the claim; which supported content, timing, and presentation controls change; what evidence supplies the content; and which implication the result must avoid. If any needed adjustment is unverified, mark that fit unresolved. This is a proposed criterion for review, not a new permission to rebuild a template. The Polish `render_policy/README.md` still requires evidence for supported edits before final selection or rendering.

## 3. `assert_without_data`

It is a coherent narration label but too broad to be the sole selection key. The three actual beats are different visual jobs:

- `23-23`: a **hypothesis** that old-catalog streams could persist without current relevance.
- `29-29c`: a **scope limitation**: play counts do not decide who is the best rapper.
- `30-30a`: a **missing-data comparison**: pre-streaming artists cannot be placed on the chart, and missing must not read as zero.

The prior timeline slate served none of these (0/12 shown options accepted). The newer embedding review gave each six candidates and again yielded zero approvals (0/18 under the completed-review rule). User notes ask for match-cut footage on `29-29c` and `30-30a`, while `23-23` has no selected treatment. The current `assert_without_data` bucket hides these distinctions. Keep it as a speech-act tag if useful, but give the selector a beat-specific visual operation or typed modifiers before treating it as a production job. Splitting or adding modifiers is a design proposal for the user, not an implemented rule.

## 4. Flooding

Detect a flood at binding time; do not cap the binder at 40%. A broad job can genuinely admit many treatments, and a quota would force arbitrary omissions. A distribution shift should pause promotion and prompt inspection of the added rows, their conditions, mechanism families, and resulting beat slates. The 40% threshold is an anomaly flag, not a truth test. The decisive measure is whether reviewed beats receive usable, non-misleading choices with tolerable slate size.

## Additional patterns caught outside the four questions

1. **A safety property is being reported as evidence of model quality.** User-picked candidates are injected and prioritized by code, so their continued reachability does not evaluate the new binder. `validate_bindings.py` checks presence of provenance fields; it does not test current-prompt agreement or semantic fit.
2. **The guiding document is stale.** `SYSTEM.md` still says 662 bindings, describes the old hard capacity filter, and says the render-after-selection premise is absent from the binder. The live state is 595 merged bindings and `capacity_rank()`. Its stage map is therefore unreliable at precisely the moment the handoff says to read it first.
3. **The final-render policy is unresolved in the timeline notes.** `CLAUDE.md` says one primary per job replaces per-scene slates and “resolves” the six-choice conflict. The Polish `render_policy/README.md` and `AGENTS.md` still require six distinct validated existing-template choices per scene for final work. A grammar binding or user pick cannot silently replace that gate. Discovery and final render should be stated as separate stages until the user explicitly changes the policy.
4. **The objective exceeds current beat coverage.** `SYSTEM.md` reports beats for 435 of 804 seconds. That is acknowledged as a discovery pilot, but the present system cannot yet be treated as a hands-off full-video path.

## Recommended next move

Before another paid binding run, preserve this frozen 40-beat ledger as the evaluation target and make a read-only reconciliation table for the eight denied beats, starting with the three `assert_without_data` beats. For each, show its required visual operation and forbidden implication; what the old, new, and merged binding pools would offer; and whether each condition can actually be met with supported template controls. Treat the 136 inferred denials as negatives **for this completed review** while retaining their provenance as absent clicks, so a later evaluation can distinguish them from the five explicit denials. Show the user the proposed job/modifier changes before treating them as approved policy. After a decision, update the versioned prompt and executable beat-to-candidate check, then test against held-out reviewed beats. Do not use binding count, cosine similarity, or preserved picks as a substitute for that evaluation.
