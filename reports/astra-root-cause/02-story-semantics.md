# Job 2 — Story semantics

**Audit status: PASS. Product defects found. Blocker owner: none.**

The architecture has the right separation of narrative context, claims and visual tasks. The implementation does not yet preserve that meaning consistently. Some defects are missing Story annotations; others occur after valid Story input reaches Matching. No runtime, schema, grammar or review implementation was changed.

Frozen Matching: `1276d0ca1daece81b5b7b38c8b5f5280046e5077`. Frozen Story: `d5117a6de0fd0c640a336c6f456946ec8b40f319`. Configured session: gpt-6-astra / medium; no escalation. Full coordinates, copied source fields, review pointers, hashes and execution receipt are in [the JSON report](02-story-semantics.json).

## Definitions and measured coverage

| Unit | Actual meaning |
|---|---|
| sourceTranscriptBeat | Timestamped transcription chunk, with broad narrative beats in separate structural analyses; neither is a shot or exact visual task. |
| authoredScriptBeat | Paragraph under a structural heading; tagged scripts additionally identify narrator, clip or quote. |
| packageBeat | Ordered, exact narration span containing claims and optional speaker/section context. It is a narrative container. |
| claim | Semantic/evidence unit in the contract, implemented primarily as punctuation-delimited sentence in these builders. A sentence is not guaranteed to be one atomic assertion. |
| VisualTask | Downstream visual communication unit, potentially spanning several claims or a subspan of one claim. Proposed task is not a selected template or render authorization. |

The formats are consistent only if these levels remain distinct. Both builders use sentence punctuation as a practical claim heuristic; neither guarantees one sentence is one atomic assertion. The Year Seventeen builder uses different punctuation handling from the tagged builder (including a J. exception), and the tagged builder protects quoted text from splitting. This is an authoring approximation, not a VisualTask contract.

| Package | Beats | Claims | Job proposals | Obligations | Continuity | Current tasks |
|---|---:|---:|---:|---:|---:|---:|
| year-seventeen@9 | 72 | 150 | 116 | 24 | 5 | 115 |
| future-volksgeist@5 | 94 | 502 | 20 | 42 | 2 | 310 |
| jayz-drake-settle-it@4 | 54 | 222 | 14 | 6 | 4 | 186 |

All three package scripts and every beat/claim span were checked exactly. Timing is absent in all three packages; no scene-duration conclusion is possible. The 21 cases below are a purposive sample (6 Year Seventeen, 9 Future, 6 Jay-Z/Drake), not a defect-rate estimate.

## Findings: observed facts and measured results

### F01 — The contract separates narrative and visual units correctly

**observed_fact; owner: story.** SPEC-0.2 and schema allow multiple visual jobs per claim, multi-claim jobs, obligations and continuity. The builders approximate claims with sentences and beats with paragraphs. They preserve text, but do not prove atomic meaning. The separate transcript analyses contain 18 Future and 15 NBA narrative beats, unlike 94 and 54 package paragraphs. These uses of beat are not interchangeable.

Cases: S02, S03, S06, S13, S14, S15. Evidence: `ev_c0014381cd5b341b`, `ev_197902cdbab5c967`, `ev_5b0549ebba618177`.

### F02 — Explicit subspan survives as metadata but not task text

**observed_fact; owner: matching.** task_from_claims computes exact_text from full claims unless task_text is supplied; the authored-proposal path supplies proposal_span but no task_text. A normal gated in-memory replay reproduces the rate task carrying the full claim. This is a downstream defect, not a reason to change Story claim boundaries.

Cases: S05. Evidence: `ev_76144b97f6b04467`.

### F03 — Shared subject and operation are insufficient merge criteria

**observed_fact; owner: matching.** _semantic_units merges under a 260-character limit using shared display entities and equal primary operations. It does not compare typed measurement units. The share and streams-per-track claims are distinct valid Story input but merge. Conversely _split_claim_segments only recognizes one not-just/but-also pivot, leaving other multi-moment sentences intact.

Cases: S08, S09, S17, S18. Evidence: `ev_c062fcf214353ca3`, `ev_032190ddc33477c4`, `ev_197e8df3cdb679e1`, `ev_0c2a0aba000bca29`.

### F04 — Meaning exists across fields, but is not consistently reconciled

**observed_fact; owner: story_and_matching.** Jay-Z/Drake comparison values and obligations explicitly carry both participants while the reviewed contract counts one entity. Future collective influence has only a Future entity ref and no group obligation. These are different failure locations: usable upstream information ignored versus missing upstream explicit requirements.

Cases: S07, S10, S11, S16. Evidence: `ev_945fc64c57b6bbfb`, `ev_5b014d59e8746769`, `ev_0125568cf745b6da`, `ev_ae89ed37733a21e4`.

### F05 — Six Year Seventeen obligations have no semantic payload beyond provenance

**measured_result; owner: story.** o-13-13b, o-14-14, o-21-21b, o-23-23, o-25-25a and o-29-29a contain only obligationId, claimIds and provenance. Their notes can be read by a person, but named requirement fields cannot enforce those notes. Other obligations correctly encode identity, withholding, text and perceptibility. Some requirements are independently represented in proposals, so this count is not six proven end-to-end failures.

Cases: S01, S04, S05, S06. Evidence: `ev_0183c99a16600ab0`, `ev_9b40f447c63fc883`, `ev_76144b97f6b04467`, `ev_5b0549ebba618177`.

### F06 — Readable evidence requirements are uneven

**observed_fact; owner: story_and_matching.** Future track-list inspection and Jay-Z fan allegations lack explicit evidence/perceptibility obligations. The reviewed galleries reduce them to item_sequence or data_explanation. Future v13 adds evidence_presentation, which is an observed improvement, not validation of readable evidence retrieval.

Cases: S12, S21. Evidence: `ev_063fd655708a1b49`, `ev_8d097d68699e413f`.

### F07 — Speaker boundaries are useful, while lane and route heuristics have limits

**observed_fact; owner: story_and_matching.** Future has 36 clip beats and 3 quote beats, preserved as 36 source-footage routes and 3 quote tasks. Six clip speakers remain unidentified (Job 1 checker). A quote containing a question still receives a rhetorical-question route with templateEligible:false in the current artifact despite its quote role; actual downstream impact is untested. Sentence-level lanes cannot separately describe metaphor and quantities inside one sentence, and source timestamps provide no duration fit.

Cases: S08, S13, S14, S15. Evidence: `ev_c062fcf214353ca3`.

### F08 — Current boundaries diverge from both frozen gold targets

**measured_result; owner: matching.** Outer-whitespace-normalized multiset comparison matches 113 Year Seventeen tasks (115 current, 116 gold) and 307 Future tasks (310 in each). Remaining differences include a wrong rate-task text, merged category setup, merged struggle passage and split outcome/catalyst passage. These counts measure effective boundaries only, not semantic accuracy or match quality.

Cases: S05. Evidence: pinned source and artifact comparison; no human inference required.

## Source and gold comparisons

The Future source transcript has coarse timestamped auto-caption chunks mixing narrator and archive speech. Its separate analysis has 18 narrative beats; the cleaned script has 94 tagged paragraphs. The Jay-Z/Drake script is an authored adaptation of the NBA ranking reference, whose analysis has 15 narrative beats; it is not a literal transcription of that video. Year Seventeen is compared with its exact authored script, review-linked jobs and editor-perfect task reference. No independent original frame-by-frame visual-job map was identified; its missing path is unknown and has not been invented.

Exact source transcript excerpts and offsets are preserved in JSON. Sponsor removal, punctuation and speaker tagging in the Future script are editorial transformations, not evidence of missing visual tasks. NBA identities and figures are not ground truth for the adapted rap script.

| Gold comparison | Current tasks | Gold tasks | Matching effective boundaries |
|---|---:|---:|---:|
| year-seventeen | 115 | 116 | 113 |
| future-volksgeist | 310 | 310 | 307 |

Comparison uses a multiset of claim IDs plus effective task text, trimming only outer whitespace and preserving duplicate tasks. Gold files without taskText use their exact proposalSpan, otherwise their joined claims. Both gold hashes match the designated immutable files; Job 1 established identical narration and claim spans across revisions.

- Year Seventeen: the short per-verse task has expanded to the full claim; two category-setup claims are now merged. These changes account for the effective-boundary differences.
- Future: the seven-years-of-failure statement and “No matter what he tried, he was stuck” are merged where gold keeps them separate; the forward-thinking-trap/outcome-and-Esco passage is split where gold combines it. Thus both over-merging and over-splitting occur relative to the reference.

Equal total task counts do not mean equal boundaries. Likewise, matching a gold boundary alone does not prove candidate quality. The Future gold retains the one-sentence craft/growth task, while `ev_c062fcf214353ca3` asks for several visual components for that narration. Both remain evidence: the gold retains its editor-perfect designation, and the scoped review remains an additional requirement to reconcile in Job 7. This audit does not silently replace either target.

## Representative spans

All offsets are Unicode code points into the exact package script, start-inclusive/end-exclusive. Each excerpt below is an exact claim span; the JSON also includes the full enclosing beat, proposal subspans and exact reviewed task quote. Intended moments are template-neutral interpretations grounded in the cited editor evidence, or explicitly source-based analysis where no editor evidence exists.

### S01 — Curren$y catalog, not a default protagonist portrait

`year-seventeen@9` · `script/year-seventeen-script-v2.1.md`

Beat boundaries: `c1-provoke-2` [268, 498).

`c1-provoke-2.1` [268, 498):

> Curren$y was on the 2009 XXL Freshman cover, and every song he has ever put on the platform — the mixtapes, the Jet Life run, the features, all of it stacked end to end — adds up to what this one catalog moves in twenty-four days.

**Intended moments:** Establish Curren$y and his releases; communicate the catalog equivalence without revealing Drake.

**Observed:** Current Story explicitly marks Drake display:none and requests Curren$y artwork. The older complaint concerns wrong media, not a missing sentence boundary. The broad legacy p-01-01 also spans this claim and a previous beat, so overlapping proposals need reconciliation.

**Attribution:** Story successfully incorporates scoped editor correction; historical downstream media failure. Overlap is a remaining proposal-interpretation risk, not evidence that the current gallery repeats the old error.

**Evidence:** `ev_0183c99a16600ab0`. Source JSON pointers: /claims/1.

### S02 — One distribution needs multiple claims

`year-seventeen@9` · `script/year-seventeen-script-v2.1.md`

Beat boundaries: `c1-provoke-3` [500, 641).

`c1-provoke-3.1` [500, 560):

> Here are ninety-three rappers, with one dot for each artist.

`c1-provoke-3.2` [561, 620):

> The higher the dot, the more plays per day that artist has.

**Intended moments:** Present the 93-member cohort, then explain vertical position while retaining the same distribution.

**Observed:** Two separate claims carry the same cohort and an obligation for 93 individual marks/identities. This is a valid multi-claim visual moment.

**Attribution:** Valid Story input; historical media availability/eligibility failure belongs downstream.

**Evidence:** `ev_c0014381cd5b341b`. Source JSON pointers: /claims/2, /claims/3.

### S03 — Continuity across paragraph boundaries

`year-seventeen@9` · `script/year-seventeen-script-v2.1.md`

Beat boundaries: `c1-predict-1` [983, 1161).

`c1-predict-1.3` [1051, 1128):

> A catalog pulling that much every day in 2026 is sitting on top of everybody.

**Intended moments:** Carry the preceding chart and media into the statement about dominance.

**Observed:** The continuity group g-04-05a explicitly crosses Story beats and preserves the editor request. A paragraph boundary therefore cannot mandate a new scene.

**Attribution:** Story continuity success; downstream enforcement is not certified in Job 2.

**Evidence:** `ev_197902cdbab5c967`. Source JSON pointers: /claims/11.

### S04 — Thirty hit songs versus artists with zero

`year-seventeen@9` · `script/year-seventeen-script-v2.1.md`

Beat boundaries: `c2-reconcile-1` [3402, 3713).

`c2-reconcile-1.1` [3402, 3445):

> He has thirty songs past a billion streams.

`c2-reconcile-1.2` [3446, 3517):

> Thirty-five of the ninety-three rappers on the opening chart have zero.

**Intended moments:** Show the thirty qualifying songs; shift to the 35-of-93 artists with zero.

**Observed:** Sentence boundaries preserve two distinct subjects. Cohort refs and perceptibility requirements retain the second group, whose missing media caused the historical complaint.

**Attribution:** Valid Story distinctions; historical downstream media omission.

**Evidence:** `ev_9b40f447c63fc883`. Source JSON pointers: /claims/40, /claims/41.

### S05 — Total streams and per-verse rate

`year-seventeen@9` · `script/year-seventeen-script-v2.1.md`

Beat boundaries: `c3-reconcile-2` [6136, 6583).

`c3-reconcile-2.3` [6312, 6481):

> Drake has fewer guest verses than either of them but more feature streams than anyone, with forty-three billion in total and roughly two hundred forty million per verse.

**Intended moments:** Maintain comparison with Future and Travis; separately depict total feature streams and streams per verse.

**Observed:** Story provides an explicit 43-codepoint rate proposal at 6437. Current Matching retains that proposalSpan but emits the full 169-codepoint claim as taskText for the rate task. The gold effective subspan is only the rate phrase. The obligation o-21-21b contains the editor note only in provenance; contextual Future/Travis are absent from this claim entityRefs.

**Attribution:** Confirmed downstream subspan-text defect on valid Story span; separate upstream omission of contextual comparison identities and executable obligation content.

**Evidence:** `ev_76144b97f6b04467`. Source JSON pointers: /claims/76.

### S06 — Define thresholds before revealing their intersection

`year-seventeen@9` · `script/year-seventeen-script-v2.1.md`

Beat boundaries: `c5-predict-1` [9522, 9688); `c5-predict-2` [9690, 9750); `c5-reveal-1` [9764, 9896).

`c5-predict-1.1` [9522, 9688):

> The test uses two floors that are fixed before the names are revealed: thirty billion streams from your own records and twenty billion as a feature on someone else's.

`c5-predict-2.1` [9690, 9750):

> Watch this one and count how many artists clear both floors.

`c5-reveal-1.1` [9764, 9827):

> Five artists clear the left floor, while seven clear the right.

`c5-reveal-1.2` [9828, 9896):

> When the panels come together, two names are standing in the middle.

**Intended moments:** Define the two thresholds without naming winners; separate the instruction; then show set overlap.

**Observed:** Authored proposals separate define_terms from the two reveal claims and preserve the later boundary ruling in provenance. needsOnScreenText is explicit. One legacy review key spans several Story beats and is not itself a scene boundary.

**Attribution:** Story boundary success; this does not certify data/visual fit.

**Evidence:** `ev_5b0549ebba618177`. Source JSON pointers: /claims/114, /claims/115, /claims/116, /claims/117.

### S07 — Influence extends across groups

`future-volksgeist@5` · `script/future-volksgeist-cleaned.md`

Beat boundaries: `p01-1` [119, 482).

`p01-1.4` [228, 382):

> He's the biggest influence for an entire generation of music artists — not just rap, but also the entire pop music industry started biting Future's sound.

**Intended moments:** Show Future as the influence source and the affected generation; expand scope from rap to pop.

**Observed:** The claim names a generation but entityRefs contain only Future and there is no group obligation. Matching splits at not just/but also yet the reviewed first task is milestone_reveal with entityCount=1. Splitting syntax did not recover the collective meaning.

**Attribution:** Upstream semantic annotation omission plus downstream reduction to single-person milestone; do not invent a closed membership list.

**Evidence:** `ev_945fc64c57b6bbfb`. Source JSON pointers: /claims/3.

Reviewed context: `reports/storypackage-02-future-volksgeist-v12-candidate-gallery.json`; use the Job 1 gallery-bound sidecar, not the canonical exporter’s substituted context.

### S08 — Craft, struggle and audience growth inside one sentence

`future-volksgeist@5` · `script/future-volksgeist-cleaned.md`

Beat boundaries: `p01-4` [800, 1580).

`p01-4.5` [1190, 1380):

> For Future, music is a science, and his understanding of people and business, learned over decades, has taken him from a struggling artist with 300 fans to over 50 million monthly listeners.

**Intended moments:** Establish craft/business understanding; transition from struggle to audience scale; depict growth with its stated units.

**Observed:** A 190-character sentence remains one reviewed task despite several visual moments. Story leaves the numeric quantities untyped and the whole mixed rhetorical/quantitative sentence factual-unverified. Matching labels it data_explanation without splitting these transitions.

**Attribution:** Story sentence heuristic and annotation limitation; downstream under-splitting independently evidenced by editor review. Factual-unverified does not establish truth.

**Evidence:** `ev_c062fcf214353ca3`. Source JSON pointers: /claims/11.

Reviewed context: `reports/storypackage-02-future-volksgeist-v12-candidate-gallery.json`; use the Job 1 gallery-bound sidecar, not the canonical exporter’s substituted context.

### S09 — Introduce a witness, then show interview behavior

`future-volksgeist@5` · `script/future-volksgeist-cleaned.md`

Beat boundaries: `p02-3` [1974, 2505).

`p02-3.3` [2198, 2446):

> Even a journalist like Elliott Wilson, who's known Future for a long time, says that generally he's funny and easy to talk with, but as soon as the recorded interview begins, something in him changes, and speaking with Future becomes a chess match.

**Intended moments:** Introduce Elliott Wilson and his connection to Future; show the interview behavior as evidence.

**Observed:** Both identities survive in Story and reviewed context, but the 248-character claim stays one evidence task. Editor asks for two visual components, which may occur sequentially within a treatment.

**Attribution:** Valid attribution text/identities; downstream visual-moment granularity is incomplete. Story could express sequence more explicitly but is not required to make a claim equal a shot.

**Evidence:** `ev_032190ddc33477c4`. Source JSON pointers: /claims/21.

Reviewed context: `reports/storypackage-02-future-volksgeist-v12-candidate-gallery.json`; use the Job 1 gallery-bound sidecar, not the canonical exporter’s substituted context.

### S10 — Family relationship preserved

`future-volksgeist@5` · `script/future-volksgeist-cleaned.md`

Beat boundaries: `p03-2` [5292, 5954).

`p03-2.1` [5292, 5353):

> You just heard a quote from Rico Wade, Future's older cousin.

**Intended moments:** Introduce Rico Wade with Future and make the cousin relationship understandable.

**Observed:** Both entities and the relationship phrase survive. Reviewed primary operation is relationship_intro. The editor accepts relationship-capable choices and distinguishes slot/staging fit.

**Attribution:** Story and operation derivation success; candidate capacity/staging remains downstream.

**Evidence:** `ev_5b014d59e8746769`. Source JSON pointers: /claims/57.

Reviewed context: `reports/storypackage-02-future-volksgeist-v12-candidate-gallery.json`; use the Job 1 gallery-bound sidecar, not the canonical exporter’s substituted context.

### S11 — Collaboration on Racks

`future-volksgeist@5` · `script/future-volksgeist-cleaned.md`

Beat boundaries: `p06-2` [21312, 22439).

`p06-2.1` [21312, 21364):

> Before long, he got a feature on YC's track "Racks."

**Intended moments:** Connect Future and YC to the track as collaborators, using the track as the shared object.

**Observed:** Story preserves YC and implied Future, but reviewed operation is archival_progression. The editor describes a relationship around song artwork; before long is insufficient to define the visual job.

**Attribution:** Valid Story relationship language and identities; downstream operation loses the focal relation. No assertion that the schema requires a new relationship field.

**Evidence:** `ev_0125568cf745b6da`. Source JSON pointers: /claims/220.

Reviewed context: `reports/storypackage-02-future-volksgeist-v12-candidate-gallery.json`; use the Job 1 gallery-bound sidecar, not the canonical exporter’s substituted context.

### S12 — Track list as readable evidence

`future-volksgeist@5` · `script/future-volksgeist-cleaned.md`

Beat boundaries: `p11-3` [41447, 41994).

`p11-3.1` [41447, 41552):

> Looking through the track list, you can really see how influential Future became by releasing this album.

**Intended moments:** Let the viewer inspect the album track list to support the influence claim.

**Observed:** Reviewed context has item_sequence/milestone_reveal and no readable-text requirement; current v13 additionally carries evidence_presentation. Story has no document/text obligation on this claim. Both the historical omission and the later partial improvement are retained.

**Attribution:** Upstream missing perceptibility requirement plus historical downstream operation error; current operation presence alone does not prove adequate admission.

**Evidence:** `ev_063fd655708a1b49`. Source JSON pointers: /claims/422.

Reviewed context: `reports/storypackage-02-future-volksgeist-v12-candidate-gallery.json`; use the Job 1 gallery-bound sidecar, not the canonical exporter’s substituted context.

### S13 — Native speech stays native speech

`future-volksgeist@5` · `script/future-volksgeist-cleaned.md`

Beat boundaries: `p01-2` [506, 578).

`p01-2.1` [506, 578):

> Just stay focused, you know, because it's not an art if it's easy to do.

**Intended moments:** Play the source clip with correct speaker attribution.

**Observed:** The clip role, source timestamp and footage obligation distinguish speech from narrator claims. Factual-unverified here refers to attribution, not endorsement of everything said.

**Attribution:** Story speaker-role success; six unidentified speakers elsewhere remain explicit gaps, not automatic substitutions.

**Evidence:** Pinned Story speaker/claim/obligation fields and current task artifact; audit interpretation.. Source JSON pointers: /claims/5.

### S14 — One attributed quotation spans six claims

`future-volksgeist@5` · `script/future-volksgeist-cleaned.md`

Beat boundaries: `p02-13` [4713, 4988).

`p02-13.1` [4713, 4759):

> You come to this world and you make two lives.

`p02-13.2` [4760, 4805):

> You got to make the most of your second life.

`p02-13.3` [4806, 4847):

> I was born Nayvadius, but now I'm Future.

`p02-13.4` [4848, 4900):

> Should I dwell on what Nayvadius was supposed to be?

`p02-13.5` [4901, 4953):

> I get a chance to experience life as something else.

`p02-13.6` [4954, 4988):

> I wasn't supposed to be like this.

**Intended moments:** Present the quotation as a coherent attributed passage; internal questions remain the quoted speaker’s words.

**Observed:** Six sentence claims remain inside one quote beat with needsOnScreenText and attribution. Matching has one speaker-derived quote task. Its operation labels include a rhetorical question, so role must retain authority over treatment interpretation.

**Attribution:** Story and quote grouping success; operation/route interaction is a downstream risk for later audit, not a proven rendering failure.

**Evidence:** Pinned Story speaker/claim/obligation fields and current task artifact; audit interpretation.. Source JSON pointers: /claims/48, /claims/49, /claims/50, /claims/51, /claims/52, /claims/53.

### S15 — Large paragraph is context, not a single scene

`future-volksgeist@5` · `script/future-volksgeist-cleaned.md`

Beat boundaries: `p04-9` [14186, 15805).

`p04-9.1` [14186, 14322):

> Some of you might not even believe me when I say that Future's favorite song of all time is "I Will Always Love You" by Whitney Houston.

`p04-9.2` [14323, 14411):

> He's talked about always being drawn to melodies that are simple yet deep and affecting.

`p04-9.3` [14412, 14526):

> In one of his later songs, he had the line, "All this pain, I can't even rap it, sometimes I feel I want to sing."

`p04-9.4` [14527, 14626):

> Learning this about Future's backstory completely changed the way I see his techniques as a rapper.

`p04-9.5` [14627, 14784):

> Knowing that his signature melodic rap style wasn't born as a calculated business move to be trendy or to innovate music, it becomes a pretty powerful story.

`p04-9.6` [14785, 14915):

> His style began as the human impulse to sing comforting melodies to himself through his struggles, ever since he was a kid, alone.

`p04-9.7` [14916, 14954):

> It makes Future make a lot more sense.

`p04-9.8` [14955, 15091):

> But as we know, it took Future a long time to merge these ideas effectively with his own voice and find the confidence to become a star.

`p04-9.9` [15092, 15155):

> His first ever song was from 2003, called "Belly of the Beast."

`p04-9.10` [15156, 15167):

> Yes — 2003.

`p04-9.11` [15168, 15325):

> And it's kind of shocking that all the way back then in 2003, Future, who used to go by Meathead when he was rapping, sounded almost exactly like André 3000.

`p04-9.12` [15326, 15576):

> And as he kept practicing, some of the Dungeon Family members he was around noticed that he was getting good at coming up with hooks and melodies, and in 2004 he had his first songwriting credit, for the hook on the Ludacris song "Blueberry Yum Yum."

`p04-9.13` [15577, 15710):

> Yeah, that's right — Future, one of the most popular rappers alive in 2024, has been working in the music industry for over 20 years.

`p04-9.14` [15711, 15805):

> If you're 20 or 21 years old watching this video, Future's music career is older than you are.

**Intended moments:** Preserve the paragraph’s narrative argument while deriving separate moments for its successive events and interpretation.

**Observed:** The largest Future beat holds 14 claims and 1,619 codepoints. Its size is valid as narrative context; it becomes oversized only if used directly as a visual task or review card. Matching already derives several tasks from it.

**Attribution:** No Story schema violation; blanket paragraph-to-scene use would be downstream misuse. Duration fit is unknown because timing is absent.

**Evidence:** Pinned Story speaker/claim/obligation fields and current task artifact; audit interpretation.. Source JSON pointers: /claims/148, /claims/149, /claims/150, /claims/151, /claims/152, /claims/153, /claims/154, /claims/155, /claims/156, /claims/157, /claims/158, /claims/159, /claims/160, /claims/161.

### S16 — Two artists even when only one is named

`jayz-drake-settle-it@4` · `script/jayz-drake-settle-it-v2.md`

Beat boundaries: `p02-2` [1934, 2242).

`p02-2.3` [2113, 2164):

> Count only studio albums, and Jay-Z leads, 11 to 9.

**Intended moments:** Compare Jay-Z and Drake under the studio-only rule, preserving the earlier all-types comparison context.

**Observed:** Story values explicitly name both artists and o-formula-flip states both winners/counting rules. entityRefs only explicitly name Jay-Z. Reviewed contract entityCount=1 and operation=data_explanation fail to reflect the implicit opponent.

**Attribution:** Valid semantic input exists in values and obligations; downstream cross-field reconciliation failure. Story could also add implied Drake for consistency.

**Evidence:** `ev_ae89ed37733a21e4`. Source JSON pointers: /claims/33.

Reviewed context: `reports/storypackage-02-jayz-drake-settle-it-v13-candidate-gallery.json`; use the Job 1 gallery-bound sidecar, not the canonical exporter’s substituted context.

### S17 — Percentage share and average are different moments

`jayz-drake-settle-it@4` · `script/jayz-drake-settle-it-v2.md`

Beat boundaries: `p04-4` [4725, 5043).

`p04-4.3` [4837, 4887):

> Drake's five biggest make up less than 10% of his.

`p04-4.4` [4888, 4943):

> Drake's catalog averages 253 million streams per track.

**Intended moments:** Depict top-five share of the catalog; then depict average streams per track.

**Observed:** Story separates claims and types values as share versus streams/track. Matching merges them into one task, although the editor requires separation. Shared identity and operation do not establish shared visual meaning.

**Attribution:** Confirmed downstream over-merging of valid distinct Story claims.

**Evidence:** `ev_197e8df3cdb679e1`. Source JSON pointers: /claims/82, /claims/83.

Reviewed context: `reports/storypackage-02-jayz-drake-settle-it-v13-candidate-gallery.json`; use the Job 1 gallery-bound sidecar, not the canonical exporter’s substituted context.

### S18 — Early misses followed by a winning streak

`jayz-drake-settle-it@4` · `script/jayz-drake-settle-it-v2.md`

Beat boundaries: `p05-2` [5381, 5749).

`p05-2.3` [5439, 5469):

> Reasonable Doubt peaked at 23.

`p05-2.4` [5470, 5497):

> In My Lifetime peaked at 3.

`p05-2.5` [5498, 5572):

> Then, starting in 1998, every studio album he released went to number one.

**Intended moments:** Show the two early album peaks together; transition into the subsequent number-one streak.

**Observed:** Three claims become one task across the transition Then, starting in 1998. The broad o-streak is attached intact, but it does not express moment-specific subsets.

**Attribution:** Downstream over-merging across a semantic transition; upstream broad obligation can be refined without changing the claim contract.

**Evidence:** `ev_0c2a0aba000bca29`. Source JSON pointers: /claims/94, /claims/95, /claims/96.

Reviewed context: `reports/storypackage-02-jayz-drake-settle-it-v13-candidate-gallery.json`; use the Job 1 gallery-bound sidecar, not the canonical exporter’s substituted context.

### S19 — Eleven albums across nineteen years

`jayz-drake-settle-it@4` · `script/jayz-drake-settle-it-v2.md`

Beat boundaries: `p05-2` [5381, 5749).

`p05-2.7` [5689, 5726):

> Eleven in a row, over nineteen years.

**Intended moments:** Make the repeated eleven successes and elapsed time perceptible together.

**Observed:** Story carries the streak obligation with eleven consecutive #1s and the 1998–2017 span. The reviewed task is derived_quantity/data_explanation; editor identifies a valid sequence treatment.

**Attribution:** Story temporal/repetition intent survives; downstream generic job label understates it. Accepted candidate is a local success, not proof of complete retrieval.

**Evidence:** `ev_81a8bfc05956e7b1`. Source JSON pointers: /claims/98.

Reviewed context: `reports/storypackage-02-jayz-drake-settle-it-v13-candidate-gallery.json`; use the Job 1 gallery-bound sidecar, not the canonical exporter’s substituted context.

### S20 — Rank within a cohort is one coherent job

`jayz-drake-settle-it@4` · `script/jayz-drake-settle-it-v2.md`

Beat boundaries: `p04-2` [4286, 4507).

`p04-2.1` [4286, 4356):

> Out of the 31 artists we measured, Jay-Z ranks 13th in career streams.

**Intended moments:** Locate Jay-Z at rank 13 within the measured cohort, with surrounding context.

**Observed:** Rank value, cohort reference and identity are all supplied. Editor explicitly says this should remain a single task and accepts choices that communicate the relation.

**Attribution:** Valid Story and coherent current boundary; do not split merely because identity, cohort and data coexist.

**Evidence:** `ev_9968d9e53524c9b1`. Source JSON pointers: /claims/72.

Reviewed context: `reports/storypackage-02-jayz-drake-settle-it-v13-candidate-gallery.json`; use the Job 1 gallery-bound sidecar, not the canonical exporter’s substituted context.

### S21 — A claim about fans needs evidence, not numeric graphics

`jayz-drake-settle-it@4` · `script/jayz-drake-settle-it-v2.md`

Beat boundaries: `p01-3` [614, 1062).

`p01-3.6` [904, 948):

> Jay-Z fans say streaming rigged the numbers.

**Intended moments:** Show attributable examples supporting the allegation that fans say streaming rigged the numbers.

**Observed:** The reviewed quote is a non-numeric editorial claim. Story has no evidence/media obligation on it. Matching uses data_explanation: lexical terms fans and numbers-related context are not evidence of a quantitative payload.

**Attribution:** Upstream missing evidence requirement; downstream keyword-based misclassification. The editorial lane does not remove the need to substantiate an attributed allegation.

**Evidence:** `ev_8d097d68699e413f`. Source JSON pointers: /claims/13.

Reviewed context: `reports/storypackage-02-jayz-drake-settle-it-v13-candidate-gallery.json`; use the Job 1 gallery-bound sidecar, not the canonical exporter’s substituted context.

## Interpretation and recommendations

The main architectural pressure is incomplete semantic interpretation between validated Story input and visual task formation, rather than the absence of a beat/claim distinction. provisional; Jobs 3-7 must test contract fitness and the rest of Matching before integrated redesign.

Legacy job labels can obscure the relation or staging the viewer must understand. supported limitation, not proof every use of those labels is wrong.

1. Preserve the beat/claim/VisualTask distinction and exact source spans; use narrative beats for context, not automatic scene sizing. (proposed for later integration; no implementation authorized here)
2. Evaluate moment boundaries by changes in subject, relation, evidence object, measurement/basis and reveal intent. Permit multiple claims per coherent moment and multiple moments within a claim. (template-neutral principle, not a new hardcoded splitter rule)
3. Reconcile meaning across entityRefs, typed values, cohortRefs, obligations and continuity before reducing presentation requirements. Preserve unknown group membership as unresolved rather than inventing identities. (proposed for later audit integration)
4. Express required editor semantics in obligation/proposal fields, retaining the original note as provenance. Do not assume provenance text is an executable constraint. (proposed; no schema change demonstrated necessary)
5. Retain speaker-role authority and source attribution, and flag absent timing separately from semantic validity. (proposed verification focus)
6. Keep the two editor-perfect targets immutable and separately preserve later scoped review requests. Reconcile overlapping target expectations in Job 7 before claiming global evaluation success. (evaluation follow-up, no new approval or redefinition)

Job proposals are useful advice: Year Seventeen supplies authored multi-claim and subclaim examples; Future and Jay-Z/Drake chiefly supply question proposals and leave much more interpretation to Matching. assert_without_data or derived_quantity cannot substitute for subject, relation, evidence, staging or measurement semantics. Low proposal counts are not themselves a schema defect, because advice is optional.

Identity and withholding are explicit in several Year Seventeen cases; relationship language survives in Future; data values and source receipts are stronger in Jay-Z/Drake; continuity can cross paragraphs. These successes argue for preserving the existing contract while locating failures. Missing semantic payloads and mixed sentence lanes show where authoring remains incomplete. No general redesign is approved by these observations.

## Code and artifact citations

- [architecture/storypackage/SPEC-0.2.md](https://github.com/djtoler/patterns/blob/d5117a6de0fd0c640a336c6f456946ec8b40f319/architecture/storypackage/SPEC-0.2.md): Major differences from 0.1, claims, jobProposals, obligations, continuity.
- [architecture/storypackage/storypackage-0.2.schema.json](https://github.com/djtoler/patterns/blob/d5117a6de0fd0c640a336c6f456946ec8b40f319/architecture/storypackage/storypackage-0.2.schema.json): /properties/beats, /properties/claims, /properties/jobProposals, /properties/obligations, /properties/continuity.
- [architecture/storypackage/tools/build_tagged_script.py](https://github.com/djtoler/patterns/blob/d5117a6de0fd0c640a336c6f456946ec8b40f319/architecture/storypackage/tools/build_tagged_script.py): module-level TAG/SENT segmentation, lane_for, named_in, CLAIM_DATA, module-level clip/quote obligation construction.
- [architecture/storypackage/tools/build_year_seventeen.py](https://github.com/djtoler/patterns/blob/d5117a6de0fd0c640a336c6f456946ec8b40f319/architecture/storypackage/tools/build_year_seventeen.py): segment, legacy review-to-claim mapping, DRAKE_DISPLAY, props, obl, cont.
- [pipeline/storypackage_splitter.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/storypackage_splitter.py): _presentation_operations, _primary_operation, _split_claim_segments, _semantic_units, build.task_from_claims, build materialize branch.

For each case, JSON includes exact package pointers, current Matching tasks, source requirements and evidenceId/sourceRef joins. Historical Year Seventeen media complaints establish the original problem; they do not prove current media retrieval still fails. Future reviewed v12 contexts are kept separate from current v13 outputs.

## Acceptance and scope

Acceptance checks: at least 15 exact spans across all three stories; beat/claim/task distinctions; attribution for every finding; existing evidence IDs; exact source hashes and offsets; ordered stage receipts; omission rejection; focused gated replay of the subspan defect; unchanged frozen production. Machine results are in [02-acceptance.json](02-acceptance.json). No new template, selection, render, runtime patch or schema change.

Limitations: no native visual inspection or duration fit; no independent original visual-job map; proposed intended moments are not editorial approvals. All substantive workflow recommendations remain proposals pending the later audit.

**PASS — Job 2 complete. Exact next job: `03-upstream-contract-fitness.md`. Blocker owner: `none`. Job 3 has not started.**
