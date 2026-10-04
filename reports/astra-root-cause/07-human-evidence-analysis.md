# Job 7 — Human evidence and reference evaluation

**PASS — evidence audit complete, with an explicit reference limitation.** The feedback points to several independent mechanisms: lost relationships, incorrect visual granularity, missing family exposure, media eligibility/supply, and unverified treatment timing. It does not support one universal “more templates” or “split more” fix. Positive examples show the system can return useful choices when meaning, treatment and assets align.

Matching production: `1276d0ca1daece81b5b7b38c8b5f5280046e5077`. Story: `d5117a6de0fd0c640a336c6f456946ec8b40f319`. No runtime rule, grammar, catalog, source review or gold file changed. No selection/rendering was authorized.

[Structured analysis](07-human-evidence-analysis.json) · [Complete evidence, contexts and reference comparisons](07-evidence-and-reference-details.json) · [Acceptance receipt](07-acceptance.json)

## Evidence accounting

All **439 normalized records** and every referenced source pointer were inspected and accounted for. The 24 canonical source hashes match. Authorship remains separate: **333 human, 74 recovered verbatim human, 32 derived from human**. The derived route-choice sentence is a summary, not a quotation by the editor. Source aliases do not add observations.

Evidence forms: 117 library-status-only records, 76 other status-only records, 191 comment-only/unreviewed records, 23 comments with statuses and 32 derived choices. Status is preserved independently from comment meaning. For example, `ev_394f04a8fb042538` rejects one candidate while praising the rest of its slate; `unreviewed` records often contain substantive comments. Neither field alone yields a task success rate.

The mechanism table below contains manually coded, nonexclusive evidence sets. **198 unique records** support the named mechanisms or positive/variant-request sets; the remaining **241** are explicitly retained in accounting categories rather than given an invented causal diagnosis. These include status-only decisions, derived choices, unresolved context, and other scoped observations. Every record has a category and its exact comment/status in the companion JSON. Counts are evidence counts, not independent failures, percentages of bad matches, or a held-out accuracy score.

## Mechanism taxonomy

| Mechanism | Records | Stage / owner | Proposed reusable principle | Counterexample |
|---|---:|---|---|---|
| semantic_granularity | 16 | Story claims → Matching task boundaries / story + matching | Split distinct visual obligations; keep a relation coherent when one treatment can express it. | `ev_9968d9e53524c9b1` |
| relationship_and_encoding | 39 | Story/Data relation → presentation contract / story + data + matching | Preserve participants, relation direction, reference group and quantitative encoding; a number alone is not the job. | `ev_0aca38d1b1fd04f1` |
| evidence_readability | 11 | Source meaning → readable evidence treatment / story + matching | Evidence requires the relevant source/words to be perceptible with appropriate dwell and attribution. | `ev_bfdc582e3d570f04` |
| family_admission_and_exposure | 16 | Capability admission → diversity/display / matching | Search relevant existing families by operation and preserve materially distinct treatments through review. | `ev_bddeca05ada71de3` |
| media_identity_and_supply | 24 | Registry/Media retrieval → candidate pairing / media + data + matching | Expose required subjects/artifacts and report missing supply independently of template quality. | `ev_e49e7876f1853753` |
| media_eligibility | 14 | Media kind/framing → native slot suitability / media + matching | Verify framing, identity and supported media kind for the chosen existing treatment; avoid global media bans. | `ev_032190ddc33477c4` |
| capacity_and_supported_adjustments | 12 | Treatment plan → native feasibility / matching | Evaluate existing variants and specifically permitted adjustments, then verify all named items, timing and readable dwell. | `ev_9968d9e53524c9b1` |
| continuity_and_context | 11 | Preserved sequence → task/scene continuity / story + matching | Bind carry-over and return-to-chart requirements to exact prior tasks and representations; do not infer antecedents from isolated comments. | `ev_0c2a0aba000bca29` |
| broll_and_no_template | 10 | Route choice → candidate review / matching + media | Keep b-roll/no-template valid while separately checking supply and any required text overlay. | `ev_9968d9e53524c9b1` |
| positive_matches | 19 | Cross-layer reviewed result / matching | Retain positive exemplars as well as failures; scoped success does not validate every stage or generalize a preferred family. | `ev_8d8f5e31713d758d` |
| intake_variant_requests | 25 | template intake/capability / matching | Record supported variant ranges with evidence; a request for more versions does not establish that versions already exist. | `ev_370b72a9900c6e92` |
| content_accuracy | 1 | Story/Data validation / story + data | Correct narrative facts through Story/Data evidence; good template selection does not validate script facts. | `ev_9968d9e53524c9b1` |
| scoped_intake_removal | 3 | catalog intake / matching | Respect explicit scoped intake removals; do not generalize a taste decision into a universal capability defect. | `ev_9968d9e53524c9b1` |

Each JSON taxonomy row lists every counted evidence ID. A counterexample limits overgeneralization: single-subject counters can work for a subject-and-number task, while a counter alone fails a rank-with-context task; a carousel can work for plural playlists and be irrelevant for a single-person beat. The taxonomy is a proposal for later evaluation, not a runtime rule.

## Balanced success and failure set

| Dimension | Positive/scoped success | Failure or limiting case | Interpretation |
|---|---|---|---|
| Story coherent task | `ev_9968d9e53524c9b1` | `ev_0c2a0aba000bca29` | Keep rank-and-cohort relationship together versus split distinct ranking moments. |
| Data/encoding | `ev_7f4a926a6afacecf` | `ev_8d8f5e31713d758d` | People plus their data points work; a naked counter does not establish ordinal rank. |
| Media supply | `ev_e49e7876f1853753` | `ev_53a6dbe5c20666fa` | Later media availability succeeds where earlier supply was missing; this is temporal evidence. |
| Media versus template independence | `ev_84d8227c5595ac1a` | `ev_0183c99a16600ab0` | First praises media while rejecting pairing; second praises templates while rejecting media. Neither is end-to-end success. |
| Matching retrieval | `ev_394f04a8fb042538` | `ev_de698031ae7624db` | Strong opening alternatives versus missing timeline alternatives. |
| Reusable family capability | `ev_d9088e29e1e0ae41` | `ev_1ca1664c3d191497` | Carousel works for plural playlists; repeated carousel appearances can be irrelevant elsewhere. |
| Native treatment conditions | `ev_b52e97e354dd311a` | `ev_5d60ed543cb6a6c2` | Specific cover/zoom post treatment approved; capacity accepted but variable timing remains conditional. |
| Route fidelity | `ev_805456ee8bf50f03` | `ev_2ab63ad9958fa8b2` | No-template b-roll direction is a valid target; irrelevant template slate is a failure. B-roll supply not certified. |

These eight contrasts deliberately include partial success and conditional approval. In `ev_84d8227c5595ac1a`, media is praised while template pairing fails; in `ev_0183c99a16600ab0`, templates are praised while media fails. The timing-conditioned carousel is not counted as native success. “This should be b-roll” establishes the correct route target, not successful media delivery. Data-related positive evidence establishes that the visual relationship can work, not that unverified numerical facts have been fact-checked.

## Contextual comments and review order

The audit flagged 17 explicit contextual-reference records. Four resolve from preserved current review order; two identify the preceding beat in the ordered Year Seventeen export. Eleven remain unresolved or only partially interpretable. Latest saved timestamps are not treated as a complete click/navigation log.

- `ev_abbda4e266fb6ee1` follows `ev_945fc64c57b6bbfb` in both saved review order and gallery task order: “same as last beat” inherits the scoped collective-artist concern, not a global ban on single portraits.
- `ev_1ca1664c3d191497` follows the familial-relationship review `ev_5b014d59e8746769`; its explicit infographic reference has a preserved antecedent.
- `ev_2717f824af0316f0` says “last review”; its prior saved review is the p03-2-03 record, even though the preceding full-gallery task is p03-2-04. Those orders are not conflated.
- `ev_686fd44338f49f3c` follows the no-template/text-overlay review. `ev_4bcb609716da7182` is **not** automatically chained to it: prior reviewed task and prior full-gallery task differ.
- `ev_197902cdbab5c967` and `ev_dd68a69dcf401ec9` identify preceding beats from the ordered original export; the full predecessor record is saved. A predecessor beat is not permission to guess a selected asset.
- The abandoned Future “previous beat” records and vague “last few reviews”/media-title references remain unresolved where a uniquely bound antecedent is absent. Their explicit standalone content may still be used.

## Contradictions, qualifications and supersessions

- **status_comment_scope:** rejected is the selected bad candidate; comment praises the rest of the slate. Do not label the whole task failed from status alone. Evidence: `ev_394f04a8fb042538`.
- **same_task_different_candidate:** Same Future task has favorable and unfavorable reviews for different candidates. Neither overwrites the other. Evidence: `ev_02f2640e521e014b`, `ev_acd365cc2cc1e56a`.
- **time_dependent_supply:** Earlier Post Malone unavailable; later explicitly available. Preserve dates and source context, not a timeless media ban. Evidence: `ev_53a6dbe5c20666fa`, `ev_e49e7876f1853753`.
- **later_treatment_qualification:** The general idea of combining native clips or using long carousel is qualified by later exact sequence/pacing checks. Capacity approval is not readable timing approval. Evidence: `ev_07c2c481d856e094`, `ev_370b72a9900c6e92`, `ev_5d60ed543cb6a6c2`.
- **later_story_override:** Current Year Seventeen claim c1-provoke-1.1 carries user-approved 2026-10-02 keep-him-hidden provenance. Earlier Drake performance b-roll is not authority to reveal him at this point. Evidence: `ev_3447807f4da0b6f6`.
- **historical_policy_superseded:** Earlier request for four options and an infographic is not current universal selection policy. Current workspace policy permits one or more validated choices and preserves scene-specific exclusions. No count or infographic quota is promoted. Evidence: `ev_1cd2e0e9bcee5abf`.
- **ambiguous_verbatim_wording:** Text says videos/full images “do go” then “only quarter and headshot”; preserve verbatim ambiguity. Other explicit ineligibility notes are supporting context, not permission to silently rewrite the quote. Evidence: `ev_a971f08bc790bcac`, `ev_8bb091c6c8097e80`.
- **gold_target_vs_later_refinement:** Gold remains editor-designated perfect reference. Later scoped feedback can refine treatment interpretation; differences in legacy labels are not automatically regressions. No audit inference supersedes the designation. Evidence: `ev_2794546a910cc39b`, `ev_0c2a0aba000bca29`.

No contradiction is resolved by dropping inconvenient feedback. Later explicit decisions, changed media availability, different candidates, and different task scopes are separate explanations. Requests for additional versions do not prove those versions exist. Earlier four-choice and infographic preferences do not override the current existing-template policy.

## Gold-reference comparison

The editor-designated perfect references remain the positive target. Their SHA-256 digests match the manifest. Original adapter source hashes are verified, and script bytes match the pinned current StoryPackages; narration changes therefore do not explain the measured task-boundary differences. Registry names becoming stable IDs are not counted as semantic failures.

| Reference | Gold tasks | Current tasks | Exact effective boundary/text matches | Other measured differences |
|---|---:|---:|---:|---|
| Future @2 → @5 | 310 | 310 | 307 | Among aligned tasks, 26 legacy job labels and 85 operation lists differ. |
| Year Seventeen @7 → @9 | 116 | 115 | 113 | Among aligned tasks, 10 proposal spans and 6 cohort references differ; all 113 gain operation/speaker-derived fields relative to the older format. |

An exact boundary match is measured by claim IDs plus effective text (taskText, otherwise the exact proposal span, otherwise joined claims), with multiplicity preserved. It is not a quality percentage. Field additions and legacy-label changes are reported, not automatically scored as errors. The complete changed fields and unmatched task payloads are in the details file.

**Boundary regressions against the designated target:** Future merges the seven-years-of-failure statement with “No matter what he tried, he was stuck,” where gold keeps separate moments; it splits the forward-thinking-trap/outcome-and-Esco passage that gold combines. Year Seventeen expands the separate “roughly two hundred forty million per verse” presentation into the whole claim and combines the album-artist/feature-artist distinction with the following spectrum statement. Both over-merging and over-splitting are present.

**Meaning and downstream matchability:** Preserving a quote task’s boundary and attributed_quote label does not suffice if current routing suppresses template retrieval despite its text/attribution obligation (Job 4 T28). Conversely, the current enumerate label for plural mixtapes is consistent with the editor’s carousel rationale (`ev_2794546a910cc39b`) even though it differs from the older legacy job. That is evidence to reconcile with the gold target, not authority to declare every old label immutable or silently downgrade the reference. Primary relationships, required words/participants, and valid treatment alternatives are the evaluation units.

## Original/reference mappings and historical evaluations

The exact **30 Year Seventeen dictated/editor-corrected passage-to-visual-job cases** exist in `ae-template-automation/narration-visual-annotations/year-seventeen-30-selector-cases.json`. All 30 are retained and joined to current claims through explicit reviewKeys, then to current tasks. They include the cover-then-time-comparison treatment, providing an older visual-job mapping without pretending the narration is unchanged. These are selection/evaluation cases, not observed shots from an original reference video.

The pinned original transcript analyses contain **15 NBA-reference narrative beats and 18 Future narrative beats**. Their input-quality fields describe segment-level transcription, not frame-level visual observations. Future’s cleaned/tagged script has 94 package beats; Jay-Z/Drake’s 54-beat script adapts the NBA argument structure and must not inherit NBA entities or figures as factual ground truth. Existing legacy analyses, handovers, transcripts and source manifests were followed; none establishes the exact original-video visual map.

Historical evaluation, facts-pilot, facts-v2 and retrieval-example slates were also inspected and saved as context. Feedback keys/numbered options do not pin those artifact digests; current copies cannot guarantee the identical option order shown at the time. Number-only comments therefore do not acquire invented exact template IDs. This limitation is separate from the 60 current records whose exact gallery contexts are bound by the Job 1 sidecar.

The earlier matching-accuracy batch reports five passing fixtures. Its declarative request copies frozen observations; it is useful regression evidence, not five fresh human approvals. The wetland held-out report has five passes and one pending human-approval case; all three template fits are unresolved. Calling that end-to-end matching success would exceed its evidence. Jay-Z/Drake now has editor feedback and cannot serve as a future untouched quality holdout.

## Remaining reference question

If a separate “org” mapping exists, the smallest needed input is **its repo path or link**, containing original-video timestamps/narration spans and the observed on-screen visual treatment for the passages intended as visual ground truth. This was asked during the audit. The supplied transcripts and structural analyses cannot establish unseen frames. Exact original-video visual fidelity remains unverified; analysis of all 439 records and both designated gold references is complete.

## Acceptance

The existing normalized-evidence validator, source-pointer checks, 24 canonical source digests, gold digests, exact script alignment, complete 439-record accounting and review-context provenance are checked. Ordered stage receipts and omission/reordering rejection are saved in the acceptance file. No production code was modified and no comment became a runtime rule.

**Next job: `08-integrated-root-cause-and-redesign.md`. Blocker owner: `none` for the completed audit; the optional exact original-visual-map comparison needs a source location from `you`. Job 8 has not started.**
