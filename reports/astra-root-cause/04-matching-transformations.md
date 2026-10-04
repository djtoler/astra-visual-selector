# Job 4 — Matching transformations

**Audit status: PASS. Semantic defects found. Blocker owner: none.**

Fresh gated replays of all three pinned packages reproduce all 611 recorded task proposals exactly. The adapter preserves Story fields; meaning is lost later through boundary rules, lexical inference, participant counting, primary routing and requirement projection.31 tasks are traced through the six required stages, with both successful and failed examples.

Frozen Matching `1276d0ca1daece81b5b7b38c8b5f5280046e5077`; Story `d5117a6de0fd0c640a336c6f456946ec8b40f319`. Configured session gpt-6-astra / medium; no escalation. No runtime, schema or grammar edits.

## What changes meaning first

### F01 — Gate and adapter preserve inputs, not semantic correctness

All 11 inspected preserved fields compare equal on three fresh adapters. Gates validate contracts and stored harness policy, not a new per-task demonstration of meaning.611 task outputs exactly reproduce recorded public artifacts.

Traces: T01, T24, T29. Evidence: `ev_394f04a8fb042538`, `ev_c0014381cd5b341b`, `ev_0183c99a16600ab0`.

### F02 — Boundary logic loses distinct visual moments

The splitter recognizes a single not-just/but-also subclaim pivot and merges using character limit, shared refs and equal primary operation. Units, role transitions and multi-clause visual changes are not merge criteria. Explicit authored subspan text is also expanded.

Traces: T04, T05, T13, T16, T17, T23. Evidence: `ev_c062fcf214353ca3`, `ev_032190ddc33477c4`, `ev_755a18328ee44670`, `ev_197e8df3cdb679e1`, `ev_0c2a0aba000bca29`, `ev_76144b97f6b04467`.

### F03 — Keyword rules create false operations

fans→data, headline inside headliner→evidence, left floor→event, grew up→chronology. Controlled in-memory substitutions change operations without changing any runtime. These diagnose lexical dependence, not proposed script edits.

Traces: T20, T21, T22, T25, T27. Evidence: `ev_8d097d68699e413f`, `ev_60553fc81c4e442a`, `ev_d9088e29e1e0ae41`, `ev_4bad981eb189dc6f`, `ev_5b0549ebba618177`.

### F04 — Reference occurrences are confused with participant count

Two Drake refs across two claims trigger comparison/parallel_instances; three Jay-Z refs trigger item_sequence. Diagnostic deduplication removes those operations/jobs.

Traces: T16, T17. Evidence: `ev_197e8df3cdb679e1`, `ev_0c2a0aba000bca29`.

### F05 — Story job advice and inferred operations can disagree materially

Materialized define_terms/intersection_of_sets/attributed_quote labels survive, but the independent operation layer chooses data/event/question routes. Conversely enumerate with lyric_presentation can be a correct structured route. Labels alone are neither authority nor proof of loss.

Traces: T09, T26, T27, T28. Evidence: `ev_6c440a7b5cb840d4`, `ev_5b0549ebba618177`.

### F06 — Primary-only admission does not establish required secondary meaning

Six real-catalog predicate probes confirm admission only checks primary operation. Necessary multi-part requirements need splitting or a compatible combined treatment; adding every secondary family would admit unrelated meanings. Incidental secondary operations should remain incidental.

Traces: T06, T09, T13, T16, T17, T24. Evidence: `ev_5b014d59e8746769`, `ev_6c440a7b5cb840d4`, `ev_755a18328ee44670`, `ev_197e8df3cdb679e1`, `ev_0c2a0aba000bca29`, `ev_c0014381cd5b341b`.

### F07 — Propagation is often exact but requirements discard or over-broaden context

Entity/value/cohort/obligation/continuity copies equal their source intersections in every trace. Intersection copying can attach whole multi-claim obligations to a short task. Gallery projection omits continuity, and requirement flags ignore explicit mediaNeeds/cohort media demand.

Traces: T15, T18, T24, T25, T30, T31. Evidence: `ev_ae89ed37733a21e4`, `ev_81a8bfc05956e7b1`, `ev_c0014381cd5b341b`, `ev_4bad981eb189dc6f`, `ev_197902cdbab5c967`, `ev_457bec72518e17bd`.

### F08 — No uncovered claims does not mean no semantic failures

All three replays report zero uncovered claims; Future retains43 typed gaps, while Year/Jay-Z report 0 splitter gaps despite traced semantic failures. The quote’s contradictory eligibility states are not emitted as a typed conflict.

Traces: T23, T24, T27, T28. Evidence: `ev_76144b97f6b04467`, `ev_c0014381cd5b341b`, `ev_5b0549ebba618177`.

## The six-stage trace

1. **Contract gate and adapter.** Actual authoritative checker and existing application gate ran for all three packages.11 preserved fields were equal to the source package. The contract gate verifies required policy/artifact structure; it does not establish semantic quality for each current task.
2. **Segmentation and grouping.** Story proposals may materialize directly when they have a span, multiple claims, multiple proposals/jobs, or cover a whole beat. Remaining narrator claims pass through `_split_claim_segments` and `_semantic_units`. The latter merges compatible-looking adjacent segments below 260 characters, or short question/setup pairs below 100. A single longer claim is not split by that 260-character limit.
3. **Operation inference and primary selection.** Keywords, value/cohort presence and reference counts generate operations. Priority and question/event exceptions select a primary. These operate independently of the Story job proposal; quoted questions can therefore receive a pure-question route.
4. **Legacy job label.** `_derived_job` uses a separate priority: question, cohort, values/reference count, item sequence, chronology/event, definition, then assert_without_data. An applicable single advisory Story job can replace that derived label. Materialized Story jobs and speaker-derived quotes retain their supplied labels. None of this means the inferred presentation operations express that job.
5. **Propagation.** All 31 traces preserve entity/value/cohort arrays and whole intersecting obligation/continuity records as the code specifies. Exact copying is useful but does not reconcile scope: a multi-claim obligation can attach all its requirements to each intersecting subtask.
6. **Requirements.** The gallery projects display-eligible entityRefs, values, cohortRefs and some obligation fields into a presentation contract; it omits continuity. `_requirements` derives Data/Media flags separately. Its media test ignores explicit mediaNeeds and cohort demand. Missing supply flags are not candidate incompatibility.

## Task results and earliest divergence

Every task below has exact source rows, segment/unit inputs and outputs, inferred operations, Story proposals, job provenance, propagation comparisons, requirements and scoped human evidence in [04-task-traces.json](04-task-traces.json). “None observed” is limited to the stated requirement, not a declaration of final visual fit.

| Trace | Task | Result | First divergence |
|---|---|---|
| T01 | `future-volksgeist.proposal.matching-derived-p01-1-01` | success | none_observed |
| T02 | `future-volksgeist.proposal.matching-derived-p01-1-02` | partial | upstream_requirement_incomplete |
| T03 | `future-volksgeist.proposal.matching-derived-p01-1-03` | failure | stage3_operation_inference |
| T04 | `future-volksgeist.proposal.matching-derived-p01-4-05` | failure | stage2_semantic_units |
| T05 | `future-volksgeist.proposal.matching-derived-p02-3-03` | failure | stage2_semantic_units |
| T06 | `future-volksgeist.proposal.matching-derived-p03-2-01` | success | none_observed |
| T07 | `future-volksgeist.proposal.matching-derived-p06-2-01` | failure | stage3_operation_inference |
| T08 | `future-volksgeist.proposal.matching-derived-p11-3-01` | success_with_historical_failure | none_observed |
| T09 | `future-volksgeist.proposal.matching-derived-p06-1-10` | success | none_observed |
| T10 | `future-volksgeist.proposal.matching-derived-p06-1-11` | success | none_observed |
| T11 | `future-volksgeist.proposal.matching-derived-p02-12-01` | success | none_observed |
| T12 | `future-volksgeist.proposal.matching-derived-p02-14-01` | success | none_observed |
| T13 | `future-volksgeist.proposal.matching-derived-p13-1-07` | failure | stage2_semantic_units |
| T14 | `future-volksgeist.proposal.matching-derived-p03-13-01` | failure | stage3_operation_inference |
| T15 | `jayz-drake-settle-it.proposal.matching-derived-p02-2-03` | failure | stage3_operation_inference |
| T16 | `jayz-drake-settle-it.proposal.matching-derived-p04-4-03` | failure | stage2_semantic_units |
| T17 | `jayz-drake-settle-it.proposal.matching-derived-p05-2-03` | failure | stage2_semantic_units |
| T18 | `jayz-drake-settle-it.proposal.matching-derived-p05-2-05` | failure | stage3_operation_inference |
| T19 | `jayz-drake-settle-it.proposal.matching-derived-p04-2-01` | success | none_observed |
| T20 | `jayz-drake-settle-it.proposal.matching-derived-p01-3-05` | failure | stage3_operation_inference |
| T21 | `jayz-drake-settle-it.proposal.matching-derived-p02-3-02` | failure | stage3_operation_inference |
| T22 | `jayz-drake-settle-it.proposal.matching-derived-p02-4-03` | failure | stage3_operation_inference |
| T23 | `year-seventeen.proposal.p-21-21b-rate` | failure | stage2_authored_span_materialization |
| T24 | `year-seventeen.proposal.p-03-03` | failure | stage6_requirement_derivation |
| T25 | `year-seventeen.proposal.p-07-07` | failure | stage3_operation_inference |
| T26 | `year-seventeen.proposal.p-28-28-1` | failure | stage3_operation_inference |
| T27 | `year-seventeen.proposal.p-28-28-2` | failure | stage3_operation_inference |
| T28 | `future-volksgeist.proposal.speaker-quote-p02-13` | failure | stage3_primary_and_route |
| T29 | `year-seventeen.proposal.p-02-02b` | success_with_other_limitations | none_observed_for_reviewed_identity_constraint |
| T30 | `year-seventeen.proposal.p-05-05a` | failure | stage6_gallery_projection |
| T31 | `year-seventeen.proposal.p-29-29c` | failure | stage6_gallery_projection |

## Trace details

### T01 — Keep the identity question and immediate setup as one moment.

> Who is Future? Well, you know who Future is.

**First divergence:** none_observed. Question/setup merge preserves both claims; subject_profile takes precedence while Story pose_a_question advice remains a separate label.

**Operations:** subject_profile, rhetorical_question. **Primary:** subject_profile. **Emitted job:** pose_a_question. **Path:** matching_derived.

**Evidence:** `ev_394f04a8fb042538`.

### T02 — Communicate ordinal rank, not only a scalar number.

> He's the fifth most streamed music artist of the last 15 years.

**First divergence:** upstream_requirement_incomplete. Current operation is data_explanation, improving on historical milestone context. No typed rank value exists upstream. This replay alone does not establish which later capacity rule excluded rank-capable candidates.

**Operations:** milestone_reveal, data_explanation. **Primary:** data_explanation. **Emitted job:** assert_without_data. **Path:** matching_derived.

**Evidence:** `ev_8d8f5e31713d758d`.

### T03 — Show the affected generation and scope expansion.

> He's the biggest influence for an entire generation of music artists — not just rap,

**First divergence:** stage3_operation_inference. Stage2 splits not-just/but-also exactly, but biggest implies milestone_reveal and only Future is counted. Upstream also lacks an explicit group requirement; the source text still carries the collective meaning.

**Operations:** milestone_reveal. **Primary:** milestone_reveal. **Emitted job:** assert_without_data. **Path:** matching_derived.

**Evidence:** `ev_945fc64c57b6bbfb`.

### T04 — Separate craft/business setup from struggle and audience growth.

> For Future, music is a science, and his understanding of people and business, learned over decades, has taken him from a struggling artist with 300 fans to over 50 million monthly listeners.

**First divergence:** stage2_semantic_units. One190-character sentence remains one task; only not-just/but-also is recognized as an intra-claim pivot. Its science metaphor and growth are reduced to generic data_explanation.

**Operations:** data_explanation. **Primary:** data_explanation. **Emitted job:** assert_without_data. **Path:** matching_derived.

**Evidence:** `ev_c062fcf214353ca3`.

### T05 — Introduce the witness and show the interview behavior.

> Even a journalist like Elliott Wilson, who's known Future for a long time, says that generally he's funny and easy to talk with, but as soon as the recorded interview begins, something in him changes, and speaking with Future becomes a chess match.

**First divergence:** stage2_semantic_units. The248-character sentence remains one task despite the editor’s two visual components. Both identities survive; evidence_presentation itself is appropriate but does not define the staged treatment.

**Operations:** evidence_presentation, event_narration. **Primary:** evidence_presentation. **Emitted job:** narrate_an_event. **Path:** matching_derived.

**Evidence:** `ev_032190ddc33477c4`.

### T06 — Introduce the cousin relationship without requiring a document merely because a quote is mentioned.

> You just heard a quote from Rico Wade, Future's older cousin.

**First divergence:** none_observed. Both identities and relationship_intro survive; selecting relationship as primary is consistent with the scoped editor intent. Incidental you-just-heard evidence must not trigger a broad family union.

**Operations:** relationship_intro, evidence_presentation. **Primary:** relationship_intro. **Emitted job:** assert_without_data. **Path:** matching_derived.

**Evidence:** `ev_5b014d59e8746769`.

### T07 — Connect Future and YC through their shared track.

> Before long, he got a feature on YC's track "Racks."

**First divergence:** stage3_operation_inference. Before long yields archival_progression; feature on is not a relationship trigger. Identities survive but the collaboration object/roles are not inferred.

**Operations:** archival_progression, event_narration. **Primary:** archival_progression. **Emitted job:** narrate_an_event. **Path:** matching_derived.

**Evidence:** `ev_0125568cf745b6da`.

### T08 — Display the readable track list as evidence.

> Looking through the track list, you can really see how influential Future became by releasing this album.

**First divergence:** none_observed. Current primary evidence_presentation and evidenceKind=document_screen correct the historical item_sequence primary. Missing explicit readability obligations remains upstream; native fit is not tested.

**Operations:** item_sequence, evidence_presentation, milestone_reveal, event_narration. **Primary:** evidence_presentation. **Emitted job:** enumerate. **Path:** matching_derived.

**Evidence:** `ev_063fd655708a1b49`.

### T09 — Prioritize readable lyrics for the hook passage.

> The song starts out with a spoken-word poem by Dungeon Family member Big Rube; then Future comes in with the hook: "The streets is where I got respect, that's where I got my stripes. And Wikipedia can't check that."

**First divergence:** none_observed. lyric_presentation wins over incidental Wikipedia/evidence/year-like operations. Legacy enumerate does not control this structured operation. The accepted scoped lyrics route is not a reason to union every secondary family.

**Operations:** lyric_presentation, item_sequence, archival_progression, evidence_presentation, event_narration. **Primary:** lyric_presentation. **Emitted job:** enumerate. **Path:** matching_derived.

**Evidence:** `ev_6c440a7b5cb840d4`.

### T10 — Represent the referenced mixtapes as multiple artifacts.

> These mixtapes aren't exactly amazing, but Future was definitely starting to figure out his formula.

**First divergence:** none_observed. These mixtapes triggers item_sequence; the scoped editorial need is retained. Full asset/title resolution is not proven.

**Operations:** item_sequence, event_narration. **Primary:** item_sequence. **Emitted job:** enumerate. **Path:** matching_derived.

**Evidence:** `ev_2794546a910cc39b`.

### T11 — Carry a question over subject imagery or footage.

> So why do we really want to know who Future is?

**First divergence:** none_observed. Pure rhetorical question gets an explicit overlay/non-template route; this aligns with the review. brollFallbackAvailable does not certify actual footage.

**Operations:** rhetorical_question. **Primary:** rhetorical_question. **Emitted job:** pose_a_question. **Path:** matching_derived.

**Evidence:** `ev_1474531742be97a8`.

### T12 — Communicate a transition from the public identity to the former self.

> So before we can understand Future, we have to meet Nayvadius.

**First divergence:** none_observed. Transformation is correctly primary despite legacy narrate_an_event and the secondary temporal/profile cues.

**Operations:** transformation, subject_profile, archival_progression. **Primary:** transformation. **Emitted job:** narrate_an_event. **Path:** matching_derived.

**Evidence:** `ev_54ae21917a62a9ee`.

### T13 — Separate collaboration phases, writing for others and years of struggle.

> He spent years in the Dungeon with his cousin Rico Wade, studying songwriting and studying melodies to find out what works, without getting anything out of it for himself — working with André 3000 as a teenager, writing for other artists, and even struggling for years to get put on in the industry without any success.

**First divergence:** stage2_semantic_units. One long claim remains one task; relationship_intro can describe one part but does not represent all distinct moments requested by the editor.

**Operations:** relationship_intro, item_sequence. **Primary:** relationship_intro. **Emitted job:** enumerate. **Path:** matching_derived.

**Evidence:** `ev_755a18328ee44670`.

### T14 — Show a human interaction and naming event.

> Everyone else there was about 10 years older than him, and the story goes that at one point a Dungeon Family member called G-Rock offhandedly said, "Man, you're the future."

**First divergence:** stage3_operation_inference. Three display refs automatically trigger item_sequence; it outranks event_narration although the refs are context, not a requested enumeration.

**Operations:** item_sequence, event_narration. **Primary:** item_sequence. **Emitted job:** enumerate. **Path:** matching_derived.

**Evidence:** `ev_2ab63ad9958fa8b2`.

### T15 — Compare Jay-Z against implied Drake under the studio-only rule.

> Count only studio albums, and Jay-Z leads, 11 to 9.

**First divergence:** stage3_operation_inference. Value records contain both artists, but comparison requires at least two display refs and a limited lexical cue. Later gallery projection counts one. Upstream omission of the implied entityRef is not absence of the underlying data.

**Operations:** data_explanation. **Primary:** data_explanation. **Emitted job:** derived_quantity. **Path:** matching_derived.

**Evidence:** `ev_ae89ed37733a21e4`.

### T16 — Separate share of catalog from average streams per track.

> Drake's five biggest make up less than 10% of his. Drake's catalog averages 253 million streams per track.

**First divergence:** stage2_semantic_units. Same primary plus shared entity merges different measurement units. The merged repeated Drake refs then falsely satisfy two-participant comparison and parallel_instances conditions.

**Operations:** milestone_reveal, data_explanation, comparison. **Primary:** comparison. **Emitted job:** parallel_instances. **Path:** matching_derived.

**Evidence:** `ev_197e8df3cdb679e1`.

### T17 — Show two early misses, then transition to the number-one streak.

> Reasonable Doubt peaked at 23. In My Lifetime peaked at 3. Then, starting in 1998, every studio album he released went to number one.

**First divergence:** stage2_semantic_units. Same-primary merging crosses Then and combines three claims. Three Jay-Z refs then imply item_sequence; different temporal/measurement phases are not reconciled.

**Operations:** item_sequence, archival_progression, milestone_reveal, data_explanation, event_narration. **Primary:** data_explanation. **Emitted job:** parallel_instances. **Path:** matching_derived.

**Evidence:** `ev_0c2a0aba000bca29`.

### T18 — Represent eleven consecutive outcomes over nineteen years.

> Eleven in a row, over nineteen years.

**First divergence:** stage3_operation_inference. Typed count/time values survive, as does o-streak, but the temporal sequence is reduced to data_explanation. No rule recognizes in-a-row duration semantics from the existing obligation.

**Operations:** data_explanation. **Primary:** data_explanation. **Emitted job:** derived_quantity. **Path:** matching_derived.

**Evidence:** `ev_81a8bfc05956e7b1`.

### T19 — Keep rank within a cohort as one coherent task.

> Out of the 31 artists we measured, Jay-Z ranks 13th in career streams.

**First divergence:** none_observed. Identity, typed rank and cohort survive; one task remains. Generic data_explanation does not itself prove the reviewed candidate failures, which require later capability/admission audit.

**Operations:** item_sequence, data_explanation. **Primary:** data_explanation. **Emitted job:** proportion_of_cohort. **Path:** matching_derived.

**Evidence:** `ev_9968d9e53524c9b1`.

### T20 — Substantiate an attributed non-quantitative allegation.

> Jay-Z fans say streaming rigged the numbers.

**First divergence:** stage3_operation_inference. The substring fans triggers data_explanation with no values/cohort. Upstream evidence obligation is missing, but calling this a quantitative requirement is a downstream error.

**Operations:** data_explanation. **Primary:** data_explanation. **Emitted job:** assert_without_data. **Path:** matching_derived.

**Evidence:** `ev_8d097d68699e413f`.

### T21 — Present an evaluative question about weighting albums versus singles.

> Somebody has to decide what a number one album is worth next to a number one single.

**First divergence:** stage3_operation_inference. Number one triggers milestone/data operations despite an editorial evaluation rather than a measurement. No question mark means rhetorical_question is not inferred.

**Operations:** milestone_reveal, data_explanation. **Primary:** data_explanation. **Emitted job:** assert_without_data. **Path:** matching_derived.

**Evidence:** `ev_60553fc81c4e442a`.

### T22 — Represent playlists and an album as a container of singles.

> If you grew up on playlists, a song that runs the world for a whole summer feels like the ultimate achievement, and albums feel like a container for singles.

**First divergence:** stage3_operation_inference. Grew up triggers archival_progression. The limited plural list does not recognize this contextual artifact relationship.

**Operations:** archival_progression. **Primary:** archival_progression. **Emitted job:** narrate_an_event. **Path:** matching_derived.

**Evidence:** `ev_d9088e29e1e0ae41`.

### T23 — Make a separate rate task for the approved short subspan.

> Drake has fewer guest verses than either of them but more feature streams than anyone, with forty-three billion in total and roughly two hundred forty million per verse.

**First divergence:** stage2_authored_span_materialization. The valid43-codepoint proposalSpan is retained but taskText is the full169-codepoint claim. task_from_claims does not slice proposal_span when no task_text is supplied.

**Operations:** data_explanation. **Primary:** data_explanation. **Emitted job:** derived_quantity. **Path:** materialized_story_proposal.

**Evidence:** `ev_76144b97f6b04467`.

### T24 — Retain the93-person distribution and its media needs.

> Here are ninety-three rappers, with one dot for each artist. The higher the dot, the more plays per day that artist has.

**First divergence:** stage6_requirement_derivation. The two claims and cohort/obligation are preserved and correctly kept together. _requirements ignores cohortRefs/mediaNeeds when deciding media required, so the explicit93-person demand disappears from that status.

**Operations:** item_sequence, data_explanation. **Primary:** data_explanation. **Emitted job:** explain_the_encoding. **Path:** materialized_story_proposal.

**Evidence:** `ev_c0014381cd5b341b`.

### T25 — Show reissue packaging and an early festival slot.

> Year seventeen of a rap career is usually anniversary-tour territory, with deluxe reissues carrying three unreleased demos on the back and a festival slot at seven-forty, before the headliner.

**First divergence:** stage3_operation_inference. Headline is matched inside headliner, producing evidence_presentation. At stage6 the explicit artwork/footage obligation is also ignored by the media-needed classifier.

**Operations:** archival_progression, evidence_presentation. **Primary:** evidence_presentation. **Emitted job:** enumerate. **Path:** materialized_story_proposal.

**Evidence:** `ev_4bad981eb189dc6f`.

### T26 — Define the two thresholds in text before showing overlap.

> The test uses two floors that are fixed before the names are revealed: thirty billion streams from your own records and twenty billion as a feature on someone else's.

**First divergence:** stage3_operation_inference. Story define_terms proposal and needsOnScreenText survive, but streams/billion produce data_explanation independently of that intent. Primary admission does not enforce the surviving text requirement.

**Operations:** archival_progression, data_explanation. **Primary:** data_explanation. **Emitted job:** define_terms. **Path:** materialized_story_proposal.

**Evidence:** `ev_5b0549ebba618177`.

### T27 — Show set intersection of the two threshold populations.

> Five artists clear the left floor, while seven clear the right. When the panels come together, two names are standing in the middle.

**First divergence:** stage3_operation_inference. Story intersection_of_sets survives as a label; left in left floor is interpreted as an event verb. No typed values/cohort accompany the claim, but the authored job explicitly states the relation and is not reconciled.

**Operations:** event_narration. **Primary:** event_narration. **Emitted job:** intersection_of_sets. **Path:** materialized_story_proposal.

**Evidence:** `ev_5b0549ebba618177`.

### T28 — Keep an attributed quotation as a quoted passage, including its internal question.

> You come to this world and you make two lives. You got to make the most of your second life. I was born Nayvadius, but now I'm Future. Should I dwell on what Nayvadius was supposed to be? I get a chance to experience life as something else. I wasn't supposed to be like this.

**First divergence:** stage3_primary_and_route. Grouping and attributed_quote label succeed. The internal question selects rhetorical_question and templateEligible:false; speakerRoutes simultaneously says attributed_quote_template and eligible:true. The template consumer obeys the false task route.

**Operations:** rhetorical_question, event_narration. **Primary:** rhetorical_question. **Emitted job:** attributed_quote. **Path:** speaker_derived.

**Evidence:** Pinned quotation role/obligation and deterministic route conflict; no editor ruling invented..

### T29 — Exclude Drake imagery and focus on Curren$y artwork.

> Curren$y was on the 2009 XXL Freshman cover, and every song he has ever put on the platform — the mixtapes, the Jet Life run, the features, all of it stacked end to end — adds up to what this one catalog moves in twenty-four days.

**First divergence:** none_observed_for_reviewed_identity_constraint. Required Curren$y and display:none Drake survive; gallery display identities correctly exclude Drake. This does not validate the equivalence job, which independently reduces to event_narration, or live media selection.

**Operations:** event_narration. **Primary:** event_narration. **Emitted job:** equivalence_restatement. **Path:** materialized_story_proposal.

**Evidence:** `ev_0183c99a16600ab0`.

### T30 — Carry the prior scene’s media/template through the continuing dominance claim.

> A catalog pulling that much every day in 2026 is sitting on top of everybody.

**First divergence:** stage6_gallery_projection. Continuity survives in the splitter task but is absent from the gallery input/output contract; the reviewed gallery path cannot enforce that invariant from this projection alone. Separate downstream sequence handling remains untested.

**Operations:** archival_progression, data_explanation. **Primary:** data_explanation. **Emitted job:** locate_in_distribution. **Path:** materialized_story_proposal.

**Evidence:** `ev_197902cdbab5c967`.

### T31 — Return to the mandatory opening chart.

> The title of best rapper alive is an argument, and this chart can't referee it. The chart counts plays, and that is its whole job.

**First divergence:** stage6_gallery_projection. Required continuity is preserved in the task but not forwarded by the gallery projection. The generic concept_statement operation cannot express the required chart identity. No claim that another consumer could not use the preserved task continuity.

**Operations:** concept_statement. **Primary:** concept_statement. **Emitted job:** assert_without_data. **Path:** materialized_story_proposal.

**Evidence:** `ev_457bec72518e17bd`.

## Primary-operation test: no unrelated-family union

The existing `_presentation_candidates` evaluates only the primary operation. Six probes use actual catalog records and existing predicates. They are diagnostic calls, not new retrieval policy, selections or native-fit approvals.

| Trace | Primary | Primary-admitted records | Records lacking support for at least one secondary predicate |
|---|---|---:|---:|
| T06 | relationship_intro | 150 | 142 |
| T09 | lyric_presentation | 7 | 7 |
| T13 | relationship_intro | 150 | 13 |
| T16 | comparison | 61 | 61 |
| T17 | data_explanation | 133 | 133 |
| T24 | data_explanation | 133 | 91 |

These counts alone do not label candidates invalid: secondary cues can be incidental. T06 correctly prioritizes a cousin relationship over “you just heard”; T09 correctly prioritizes lyrics over Wikipedia mentioned inside the lyric. In contrast, T13’s distinct work/struggle moments and T17’s early peaks/streak require boundary or combined-treatment reconciliation. Keeping every operation in metadata does not prove those requirements are checked. The proposed direction is correct primary selection plus explicit reconciliation of required additional meaning, not unioning all families.

## Controlled diagnostics

- `headliner` → `closing performer` removes evidence_presentation in T25: `headline` was a substring trigger.
- `left floor` → `first floor` removes event_narration in T27: a spatial descriptor was treated as an event verb.
- `fans` → `listeners` removes data_explanation in T20 despite neither phrase supplying a number.
- `grew up` → `listened` removes archival_progression in T22, isolating the temporal keyword trigger.
- Deduplicating entity references across T16’s two claims removes comparison/parallel_instances; doing so across T17 removes item_sequence/parallel_instances. The original source fields were not changed.
- T28 retains attributed_quote while its task route says templateEligible:false; the actual template_candidates function returns early on that route. The speaker route’s contrary eligible:true declaration does not repair it.

These changed inputs are diagnostic contrasts, not proposed edits to narration or valid replacement packages. Full exact before/after inputs and outputs are in [04-diagnostic-probes.json](04-diagnostic-probes.json).

## Replay and acceptance

Use Matching at the frozen production commit and Story at the pinned authority commit. Run the existing adapter with the pinned entity_roster and automation-data repositories and a Python environment with jsonschema; pass its output to the existing splitter. The task-trace artifact records package paths/digests, checker receipts, all compared output counts and function invocations. Every trace includes the exact arguments for segmentation, inference, job derivation and presentation_contract replay. Temporary adapter paths in receipts describe this audit run; source package digests are the portable identity.

The stage6 gallery projection input was assembled from the inspected gallery mapping and passed to the real presentation_contract function. Full gallery embeddings/diversification were not rerun and are not claimed as newly validated. Recorded reviewed galleries remain separately labeled, including Futurev12 versus current replay.

38 existing tests passed (`test_storypackage_splitter`, `test_visualtask_matching`, `test_matching_contract_gate`). Existing unclosed file/database ResourceWarnings occurred without test failures. Acceptance additionally checks31 trace records, exact replays, stage inputs/outputs, evidence IDs, earliest-divergence labels, omission/reorder rejection, hashes and unchanged runtime. See [04-acceptance.json](04-acceptance.json).

## Sources and interpretation

- [pipeline/matching_contract_gate.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/matching_contract_gate.py)
- [pipeline/storypackage_adapter.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/storypackage_adapter.py)
- [pipeline/storypackage_splitter.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/storypackage_splitter.py)
- [pipeline/visualtask_matching.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/visualtask_matching.py)
- [pipeline/storypackage_candidate_gallery.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/storypackage_candidate_gallery.py)
- [pipeline/matching_agent.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/matching_agent.py)
- [pipeline/visualtask_requirements.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/visualtask_requirements.py)
- [grammar/general-matching-layer-contract.json](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/grammar/general-matching-layer-contract.json)
- [grammar/matching-harness-stage-contract.json](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/grammar/matching-harness-stage-contract.json)
- [grammar/matching-entrypoint-contract.json](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/grammar/matching-entrypoint-contract.json)
- [plans/general-matching-layer-tasks.json](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/plans/general-matching-layer-tasks.json)

Observed facts and measurements above are distinct from the recommendation: reconcile meaning before prioritizing operations, count distinct participants, preserve approved subspans, and carry necessary constraints into their consumers. This is not an approved redesign. Candidate family coverage, native feasibility and ranking remain for subsequent jobs. Historical missing-media or wrong-pairing reviews do not alone prove a splitter failure.

**PASS — Job 4 complete. Exact next job: `05-grammar-tags-capabilities.md`. Blocker owner: `none`. Job 5 has not started.**
