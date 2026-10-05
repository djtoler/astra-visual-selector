# Job 2 — Story beat, claim and visual-moment semantics

**Result: PASS** · Next job: `03-upstream-contract-fitness` (Claude Desktop, direct) · Blocker owner: `none`

Companion data: `reports/astra-root-cause/02-story-semantics.json` (23 structured spans, 12 findings, 9 principles, 7 recommendations, receipt).

## Execution receipt

| Field | Value | How determined |
| --- | --- | --- |
| Operator | `claude_desktop` | Stated by the invoking job prompt; required by `EXECUTION_POLICY.json` for this job. Not observable from inside the session. |
| Execution mode | `claude_cli_invoked_from_desktop` | Stated by the invoking prompt; Job 1's receipt records a pre-flight `claude -p --model claude-fable-5-1 --effort medium` returning that model and effort. Not observable from inside the session. |
| Executor / model | `claude-fable-5-1` | Read from this session's own system context, which names the model Fable 5.1 with exact ID `claude-fable-5-1`. |
| Model display name | Claude Fable 5.1 | Same source. |
| Reasoning effort | `medium` | Selected explicitly by the CLI effort flag per the invocation record and Job 1's pre-flight. Fable 5.1 defaults to High in Claude Code, so Medium is recorded as flag-selected, not assumed. The session context exposes a reduced effort setting but not the literal word "medium"; the label comes from the invocation record, not a runtime API. |
| Not exposed | CLI version; a runtime field naming the effort literally; whether this process is a CLI subprocess or a Desktop-backed cloud container. The session identifier visible here (`session_014CbgCFFrmJN4PKxJdBpZ7P`) equals the one in Job 1's receipt. That equality is reported, not interpreted (UE-11). |
| Environment | Cloud container. Audit repo `/home/user/astra-visual-selector`, branch `fable_analysis` at `b1bdecce…`. Story authority worktree `/home/user/story-pinned` at `d5117a6de0fd0c640a336c6f456946ec8b40f319`, verified with `git log`, never written. |
| Writes | Exactly two files: this report and its JSON twin. No git write command. No runtime, schema, grammar or evidence change. |

**Independence.** Local branches are `fable_analysis`, `main`, `origin/main` only. No fetch, checkout or network git command ran. The `matching-layer/` prefix in evidence paths and the `/Polish/matching-layer/` prefix inside current task-proposal `source.path` fields are directory names of the live checkout (Job 1) and were resolved by stripping them. No Astra Job 1–8 report, repair plan or post-baseline Matching commit was read. Contamination risk: none detected.

## 1. Definitions, from the artifacts

The acceptance check most likely to fail is conflation of beat, claim and VisualTask. These are the units as the schema, the two builders and the splitter actually define them.

**Beat.** Schema: `beats[]` with opaque `beatId`, `order`, `span` in code points into `script.text`, `narration`, `claimIds`, `claimCoverage`, optional `section`, `test`, `story`, `speaker`. No field says what a beat means. The tagged builder (`build_tagged_script.py:82-105`) makes one beat per `@role` tag line plus one paragraph. The Year Seventeen builder (`build_year_seventeen.py:22-43`) makes one beat per blank-line block under a `###` heading. Four other things are also called "beat" in this system:

| Unit called "beat" | Where | Count | Size |
| --- | --- | --- | --- |
| Caption chunk | `youtube_doc_analysis/transcripts/full/*.txt` | 30-second chunks | no punctuation, no speakers |
| Source narrative beat | `analysis_006.json`, `analysis_002.json` `story_beats[]` | 18 / 15 | 60–360 s, act-level |
| Legacy review beat | `grammar/beat-review-export-2026-09-27.json` | 40 | one to four sentences, older wording |
| Story beat | the three packages | 94 / 54 / 72 | a paragraph |
| Editor's "beat" | candidate reviews, e.g. `ev_0c2a0aba000bca29` "beat should be split into 2" | per task | a Matching task proposal |

These are not consistent, and the schema permits that. What makes it matter is `storypackage_splitter.py:456-489`: semantic units are derived **per Story beat** and never cross one unless a Story proposal does. Paragraphing decisions, made at caption cleaning for the biography and at writing for the other two, therefore cap every VisualTask.

**Claim.** Schema: the semantic and evidentiary unit, with `span`, `text` equal to the script at that span, `lane`, `entityRefs` (`mentioned`, `display`, `representedBy`), optional `values`, `cohortRefs`, `reviewKeys`, `unresolvedMentions`. Both builders cut claims at sentence punctuation (`build_tagged_script.py:83`, never inside a quotation; `build_year_seventeen.py:39`, except after "J."). Operationally, a claim is a sentence with a lane and entity roles. SPEC-0.2 states a package never makes one claim equal one VisualTask.

**VisualTask.** Absent from the Story schema by design. On the Matching side it is the review-only `taskProposal` built by `storypackage_splitter.task_from_claims` (lines 270-353): an exact span over one or more claims, `taskText`, lanes, entity and cohort refs, values, obligations and continuity attached by claim intersection, derived `presentationOperations`, a job label, and `activationState: proposal_requires_editor_review`. It is produced by materializing a Story proposal, per quote beat, or per narrator beat by `_semantic_units`. Clip beats become speaker routes, not tasks.

**jobProposal**, **obligation**, **continuity** are Story advice objects keyed by `claimIds` (schema `jobProposals[]`, `obligations[]`, `continuity[]`). A proposal may carry a sub-span inside one claim.

**Visual moment** is this report's analytical term: the smallest narration span one continuous on-screen treatment must communicate. Neither schema has it as a first-class object. The handoff's `media.focal` and the splitter's semantic unit are the nearest approximations.

## 2. What the packages and outputs measure

| | future-volksgeist@5 | jayz-drake-settle-it@4 | year-seventeen@9 |
| --- | --- | --- | --- |
| Builder | tagged | tagged | Year Seventeen-specific |
| Beats (narrator / clip / quote) | 94 (55 / 36 / 3) | 54 (54 / 0 / 0) | 72 (72 / 0 / 0) |
| Claims | 502 | 222 | 150 |
| Lanes factual / editorial / interpretive | 364 / 107 / 31 | 92 / 116 / 14 | 87 / 43 / 20 |
| Narrator beat length, median / max (code points) | 662 / 1619 | 218 / 644 | 143 / 677 |
| Claims per narrator beat, median / max | 6 / 16 | 4 / 9 | 2 / 6 |
| jobProposals | 20, all `pose_a_question` | 14, all `pose_a_question` | 116 (72 writer, 36 legacy model, 8 user) |
| Proposals with a sub-span | 0 | 0 | 1 |
| Obligations | 42 (39 builder-generated, 3 authored) | 6 | 24 (22 user notes, 6 of them empty shells) |
| `mustBeTrue` used | 0 | 0 | 0 |
| Continuity | 2 | 4 | 5 |
| Cohorts / claims with `values` | 0 / 0 | 1 / 50 | 3 / 0 |
| Timing | absent | absent | absent |

Matching-side, for location only (judgment is Job 4's): the Year Seventeen gold reference materializes all 116 Story proposals one to one; the baseline output demotes 12 to advisory and re-derives 11 units with jobs preserved. The biography gold and baseline both hold 310 tasks, and the claim ids, spans, text and lanes are byte-identical between package files @3 and @5, yet two beats are grouped differently and 26 tasks change job label. Equal counts hide this (F-10, S23).

Splitter inputs that never affect a boundary, verified in code: `lane` (copied only, line 321), `obligations` and `continuity` (attached after grouping, lines 334-339), `values[].entity` and `values[].label` (participants counted from `entityRefs` only, lines 94 and 115-126), and `jobProposals[].span` outside materialized proposals. The only intra-claim split rule is ", but also" preceded by "not just" (lines 162-182).

## 3. The missing "org" mapping, as it bears on this job

The transcript-to-beat mapping Job 1 named is absent and was not reconstructed. Consequences here: for the biography, every sentence and paragraph boundary was created during caption cleaning (`script/future-volksgeist-cleaning-log.md`: punctuation and sentence boundaries "added throughout"), so no claim boundary can be traced to the source. For the debate story the script is original and the source is a structural reference only. For Year Seventeen, 21 of the 40 legacy review beats quote wording that differs from script v2.1 (overlap down to 0.632 on 08-08), and the join file the builder used, `grammar/beat-script-map.json`, is absent from this checkout (UE-10). Editor notes reached through `reviewKeys` were written against narration that is not the narration now bound to those claims. This bounds how exactly a note can be re-applied; it does not invalidate the notes.

## 4. The spans

Each span gives the locator, the current beat boundary, the current claim boundary, the intended moments, the observation, and an attribution label: **story** (a Story-authoring failure), **matching** (a valid Story input later mishandled by Matching), **both** (separable shares), **success**, or **undetermined** with what would settle it. Evidence IDs are from `reports/astra-matching-review-evidence-20261004.json`; the 49 `matching_output_feedback` records are corroborated human prose whose source file is unreachable here (Job 1 UE-02) and are marked "unverifiable source" where cited.

### Year Seventeen (9 spans)

**S01 · Opening rate sentence · success.** Script line 7; claim `c1-provoke-1.1`, span 117+149, the whole beat. The subject is `mentioned: false, display: withheld` with user provenance; obligation `o-01-01` carries footage need, withheld identity and a `wouldBeALie`. One moment, exactly expressed. The only caveat is that legacy proposal `p-01-01` spans this claim and the next beat's claim, so the gold task text runs two sentences the editor reviewed separately. Evidence: `ev_3447807f4da0b6f6`.

**S02 · Credential plus equivalence in one sentence · story.** Script line 9; claim `c1-provoke-2.1`, span 268+230. One sentence holds two moments (the cover; the whole catalog against a 24-day slice). Three proposals point at the whole claim with no sub-span (`p-01-01`, `p-02-02a`, `p-02-02b`), so the gold reference materializes three overlapping tasks with the same text. The handoff does cut the claim into two sub-spans, so the moments exist only downstream of the package. The entity role is a success: the subject is `display: none` here, which is what the editor asked for. Evidence: `ev_0183c99a16600ab0`, `ev_ab29a46767509923`, `ev_ffebfa36b44ada64` (unverifiable source).

**S03 · The 93-mark chart · success.** Script line 11; claims `c1-provoke-3.1`–`3.3`. Cohort `chart-93` is replayable and complete, `recognizableIdentityCount` is 93, `mediaNeeds.person.count` is 93, and continuity `g-opening-chart` and `g-chart-return` are `required`. This is the structural precondition for the editor's "20 or more identities plus comparative intent means every spatial family" rule. Story supplies the count; whether admission honoured it is Jobs 5 and 6. Evidence: `ev_c0014381cd5b341b`, `ev_6fc95a5580186e72`.

**S04 · Runner-up flatness · both.** Script line 61; claim `c2-reveal-2.2`, span 2822+83. Obligation `o-11-11b` says "two entities, one against the other", but the claim's `entityRefs` hold only the named runner-up: no pronoun cue fired and the claim is not in the forced list. Matching's comparison operation needs two display-eligible refs (`storypackage_splitter.py:94`), so the comparison is invisible. Story's implied-partner table is incomplete; Matching never reads `mustBePerceptible`. Either fix alone surfaces it. Evidence: `ev_fbb42c911ffa7f42`, `ev_9ed54960c6c899fc`.

**S05 · Two clauses, two treatments · story.** Script line 71; claim `c2-reconcile-1.3`, span 3518+195. The editor paired each clause with a different treatment. The proposal covers the whole claim; obligation `o-13-13b` is an empty shell whose only content is the quoted note in `provenance.evidence`. The handoff cuts the first clause and logs the second as `u-13-13b-second-clause`, "has no VisualTask". The schema supports sub-spans; the builder used one, by hand, elsewhere. Evidence: `ev_de6a6bbf9fb0ee07`, `ev_9b40f447c63fc883`.

**S06 · Seven careers stacked · story.** Script lines 89–93; claims `c3-provoke-3.3`, `c3-provoke-4.1`–`4.2`, `c3-provoke-5.1`. Three Story artefacts disagree on one moment. Proposal `p-18-18` includes the half-credit rule sentence from the previous paragraph and excludes the total sentence; obligation `o-18-18` (identity count 7) excludes the rule and includes the total; the handoff task follows the obligation. The cause is the script revision: the legacy beat quoted one paragraph that v2.1 split into two plus the rule, and the `reviewKeys` join inherited that. The gold task for `p-18-18` carries the join artefact. Evidence: `ev_ffa432faa3017e77`, `ev_600a5daa0a58bf97`.

**S07 · Two floors, then the overlap · success with a caveat.** Script lines 176–184; claims `c5-predict-1.1`, `c5-predict-2.1`, `c5-reveal-1.1`–`1.2`, `c5-reveal-2.1`. A user-approved split with a dated ruling that keeps the instruction sentence out of the overlap. This is the package at its most precise. Residual: package proposal `p-28-28-2` excludes the names sentence while handoff task `28-28.overlap` includes it (UE-09), and the approved timing boundary `ev_0ef11e34ab9fe948` quotes older wording. Evidence also: `ev_5b0549ebba618177`, `ev_021919c932e157f2` (unverifiable source).

**S08 · Footage, then a timeline, labelled as a question · story.** Script lines 137–139; claims `c4-predict-1.1`, `1.2`, `c4-predict-2.1` across two beats. One proposal, `pose_a_question`, covers all three; obligation `o-24-24` encodes two media needs by prose position ("for the first sentence"; artwork count 8). A consumer honouring the proposal sees a question; one honouring the obligation sees a timeline. Evidence: `ev_65fa5e81c76d4c01`, `ev_3fe0c804e39ff085`.

**S09 · Six artists, two kinds, twelve numbers · story.** Script lines 170–172; the longest Year Seventeen beat `c5-provoke-1` (677 code points, 6 claims). Proposal `p-27-27` (`inversion`) spans five claims; the sentence that states the categorization and the two that name the kinds sit in other proposals. The package carries no `values` at all; the twelve numbers are prose. The handoff later binds all twelve with roles and `showTogether` pairs, which is the structure the editor described ("2 sets of artists with opposing data points") and the package omits. Evidence: `ev_84d8227c5595ac1a`, `ev_607fb53976686bf6` (unverifiable source).

### Jay-Z / Drake (6 spans)

**S10 · The streak · matching.** Script line 77; beat `p05-2`, eight claims, obligation `o-streak` over `p05-2.2`–`2.8` with intent, three `mustBePerceptible` items and `mediaNeeds.artwork.count: 13`. The obligation defines two moments: two early misses, then eleven in a row. The splitter never reads obligations when grouping and produced six tasks by sentence heuristics, grouping the two peaks with the start of the run and isolating the rest. The editor then asked, task by task, for a pair of cards, a split, and a timeline or long carousel: the obligation's structure rediscovered by hand. Evidence: `ev_b28174f436fb78aa`, `ev_0c2a0aba000bca29`, `ev_de698031ae7624db`, `ev_81a8bfc05956e7b1`.

**S11 · Share versus average · matching.** Script line 66; claims `p04-4.2`–`4.5`. Four supported claims whose `values[].label` names the metric: two share a share label, two share an average label. The splitter merged `4.3` with `4.4` (same entity, same operation, under the 260-code-point cap) and left the pairs' partners alone, so one task mixed two metrics for one entity. The value label that distinguishes the pairs is never compared. Evidence: `ev_197e8df3cdb679e1`.

**S12 · Eleven to nine · both.** Script line 26; claims `p02-2.2`, `p02-2.3`. Each sentence names one entity but its `values` name both, and obligation `o-formula-flip` requires both scores visible together. Participants are counted from `entityRefs`, so no comparison was derived and a single-subject counter was offered. Story's implied-ref table lacks the partner; Matching ignores `values[].entity` and the obligation set. The editor's note names the chain: "something off between beats, beat/visual job splitting, visual job understanding and the available grammar/tags". Evidence: `ev_ae89ed37733a21e4`.

**S13 · Editorial sentences with number words · matching.** Script lines 29 and 12; claims `p02-3.2`, `p01-3.6`, both `editorial`. The operation detector keys on "number one" and "numbers" and emitted `data_explanation`, so numeric treatments were admitted for opinion sentences. The lane was right and was never consulted. Evidence: `ev_60553fc81c4e442a`, `ev_8d097d68699e413f`.

**S14 · Thirteenth of thirty-one · success.** Script line 60; claim `p04-2.1` with a value, a named subject and cohort `scale-31` (complete, replayed). The sentence stayed whole and derived `proportion_of_cohort`; the editor confirmed it has a single job. The remaining complaint (spatial families absent) is admission. Evidence: `ev_9968d9e53524c9b1`.

**S15 · Alternating head-to-head sentences · matching.** Script line 40; claims `p03-2.1`–`2.5`, continuity `g-head-to-head` (template_family, preferred) over 14 Part 3 claims. Adjacent sentences alternate entity, so none merged; five single-sentence tasks resulted and the continuity group was attached to each afterward. The editor's acceptance of a lone counter on the first sentence is scoped to that candidate and does not override the Story's continuity preference. Evidence: `ev_0aca38d1b1fd04f1`.

### Future (8 spans)

**S16 · The opening paragraph · both.** Script line 6; beat `p01-1`, five claims. Successes: the splitter's question-setup rule merged the question and its answer into one unit the editor praised, and the "not just … but also" rule split claim `1.4` into two source-exact segments. Defects: "fifth most streamed" is prose only (no value, no basis), so a counter was offered and rejected for not showing rank; "an entire generation of music artists" is an unenumerated group this package cannot express (zero cohorts), so single-person treatments were offered. Evidence: `ev_394f04a8fb042538`, `ev_8d8f5e31713d758d`, `ev_945fc64c57b6bbfb`.

**S17 · One sentence, three jobs · matching.** Script line 15; claim `p01-4.5`, span 1190+191. The editor enumerated three visual jobs (a thesis, a transformation, a magnitude change from 300 to 50 million). The sentence is a valid claim under the contract; moment discovery inside it is Matching's declared responsibility, and the splitter's one split rule and its verb-list transformation detector do not fire on "has taken him from … to". Story could add values for the two numbers as an enrichment. Evidence: `ev_c062fcf214353ca3`.

**S18 · The source channel's sign-off · story.** Script line 15 last sentence and line 309; claims `p01-4.7`, `p13-4.1`. Obligation `o-source-signoff` says the production replaces these lines, but the schema has no narration disposition, so they are ordinary claims and Matching built tasks and galleries for them. The editor's instruction was to skip. Evidence: `ev_7058ede7e45b1b58`.

**S19 · Narration that hands off to a clip · both, mostly success.** Script lines 26–29; beat `p02-3` then clip beat `p02-4`. The editor's instruction that b-roll of the subject speaking "would follow" is exactly what the next Story beat encodes as `speaker.role: clip`, and Matching routed it as source footage outside template matching with a typed end-timing gap. Within the paragraph, one sentence again holds two parts (a new person, then an interview context), and "all of his interviews" is a multiple the package cannot express. Evidence: `ev_51312a34468c7c4d`, `ev_032190ddc33477c4`, `ev_2801e7ff3abddf95`.

**S20 · A quoted hook, then "these mixtapes" · story.** Script line 169; claims `p06-1.10`, `p06-1.11`. Quoted text inside a narrator sentence produces no `needsOnScreenText` (only quote-role beats do, `build_tagged_script.py:247-251`), although the splitter did detect a lyric operation. "These mixtapes" refers to works, which are outside the registry, so nothing structural says "several items". Evidence: `ev_6c440a7b5cb840d4`, `ev_2794546a910cc39b`.

**S21 · The unnamed Canadian act · success.** Script line 189; claim `p07-1.5`, span 25936+120. An implied person with image eligible and caption withheld (`o-drake-unnamed`); the editor accepted single-subject cards and explicitly did not want a multi-entity treatment. Evidence: `ev_bddeca05ada71de3`.

**S22 · A 320-code-point sentence in a 1,397-code-point beat · matching.** Script line 300; claim `p13-1.9`. Three moments in one sentence; the editor assigned the third to b-roll. Beat size did not cause the defect, but an oversized paragraph offers no structure between paragraph and sentence. Evidence: `ev_755a18328ee44670`.

**S23 · Grouping drift on unchanged input · undetermined.** Script lines 137 and 264; claims `p05-1.2`/`1.3` and `p10-6.5`/`1.6`. The gold reference and the baseline group these oppositely, and 26 further tasks change job label, with identical Story claims. No editor evidence covers these beats. What would settle it: the splitter revision that produced the gold, or an editor ruling. Handed to Job 4 (UE-08).

## 5. Findings

Each finding states its attribution.

**F-01 · Five meanings of "beat"; the Story paragraph is the one Matching treats as a wall.** *both.* Story paragraphs are authored with no stated visual rule and vary 4.6× in median length across stories; Matching never crosses one. Spans S06, S10, S16, S22.

**F-02 · Claim equals sentence; a sentence is neither the moment nor a reliable fraction of one.** *both.* Sentences hold two or three moments (S05, S16, S17, S19, S22) and moments span several sentences (S10, S11, S15). The contract already says claims are not tasks. What is missing on both sides is a first-class moment boundary: sub-span and cross-claim proposals are schema-legal but the general builder authors neither; Matching's intra-claim split is one pattern and its merge key is shared entity under a length cap.

**F-03 · Obligations and continuity are boundary evidence that Matching attaches after grouping.** *matching.* Every obligation and continuity group names a claim set. `_semantic_units` never sees them. S10, S12, S15.

**F-04 · Lanes are never consumed by Matching.** *matching.* The lane heuristics are adequate in the sampled spans; the splitter copies the lane and never conditions on it. S13.

**F-05 · Participants are counted from `entityRefs` alone.** *both.* Values' entities and the implied comparison partner are invisible to derivation; the merge key is shared entity rather than shared metric. S04, S11, S12, S15.

**F-06 · jobProposals are advisory, incomplete, and speak the legacy matcher's vocabulary.** *story.* Two packages propose only questions, which the splitter derives anyway. The third proposes 116, of which 36 are legacy model labels and 32 are the null job. Proposal boundaries disagree with obligations (S06, S08) and overlap (S02). The Year Seventeen gold reference is a one-to-one materialization of these proposals, so its job derivation is the Story's labels. The 8 user-ruled proposals are the most precise units in the system (S07).

**F-07 · Obligations are exact where fielded and empty where a note was only quoted.** *story.* `mustBeTrue` is used 0 times in 72 obligations; `contentClass` 0 times; six Year Seventeen obligations are shells; counts are prose where the schema offers `mediaNeeds.count`, `recognizableIdentityCount` or an unenumerated cohort; quoted lyrics get no text obligation (S20); replaced narration has no disposition (S18). Where fields are used (S01, S03, S10, S21) they are precise and user-provenanced.

**F-08 · The entity model covers people and groups; works and unenumerated groups cannot be expressed.** *story, with a Data dependency.* "These mixtapes", "all of his interviews", "an entire generation", "13 album covers" have no structural handle. The registry is Data-owned, but the schema's unenumerated cohort and `mediaNeeds.count` exist today and were unused. S16, S19, S20, S10.

**F-09 · Derivation is unverifiable against sources, and Year Seventeen evidence was written against different wording.** *undetermined.* See section 3. What would settle it: the org mapping and the absent beat-script map (UE-10).

**F-10 · Matching granularity drifted between the gold runs and the baseline on unchanged Story input.** *undetermined, Job 4.* 12 proposals demoted in one story; 2 beats regrouped and 26 labels changed in another, at equal counts. Not a Story failure.

**F-11 · The three packages are not produced the same way.** *story.* Two builders, values in one package, cohorts 0/1/3, reviewKeys in one, a hand-authored handoff for one keyed to Matching pilot task ids. UE-03 is a sequencing dependency: the two newer handovers ask Matching for VisualTasks before a handoff can be written. Fitness is Job 3's question.

**F-12 · Speaker roles are a success end to end.** *success.* Clip and quote beats carry the right obligations; Matching routes them correctly and emits typed gaps (36 clip end-timing, 6 unidentified speakers, 1 missing quote source). S19.

## 6. Story-neutral principles

Each names the reference it draws on; absence of a field in the Year Seventeen reference is not read as a choice (Job 1 AF-07).

- **P-1** A visual moment is the unit of treatment, a claim the unit of evidence, a beat the unit of narration; each layer carries its own and names the mapping. (Future reference `granularityPolicy`; Year Seventeen handoff tasks.)
- **P-2** Any Story object that enumerates a claim set is boundary evidence and is consulted before text heuristics. (Year Seventeen reference: user split proposals.)
- **P-3** Comparison participants are the union of mentioned, implied, value and cohort entities; adjacent sentences merge on shared metric or moment, never on shared entity alone. (Editor evidence; neither reference shows it.)
- **P-4** Every spoken number exists as a structured value with entity, basis and label in every package. (Debate package values; Year Seventeen handoff anchors.)
- **P-5** Groups treated as a visual multiple, including works, carry a typed count even when membership is unknown. (Year Seventeen handoff `focal_unknown`.)
- **P-6** Lane is a routing signal: editorial and interpretive sentences default to text, question or b-roll unless an obligation says otherwise. (Editor evidence.)
- **P-7** Narration to be replaced or omitted is marked in the package. (Schema gap.)
- **P-8** Job labels are advisory operations; boundaries and requirements are the binding advice; a user ruling outranks a legacy label. (Year Seventeen reference: 8 user proposals versus 32 null jobs.)
- **P-9** Evidence written against one wording is scoped to that wording. (Timing boundary `ev_0ef11e34ab9fe948`.)

## 7. Recommendations (template-neutral, for later jobs; nothing changed here)

| | Owner | What |
| --- | --- | --- |
| R-1 | story | A first-class moment boundary: generalize proposals (or add `moments[]`) to carry exact spans across one or more claims with optional job and provenance; have both builders accept an authored moment table. |
| R-2 | matching | Consume obligation and continuity claim sets, value labels and entities, and lane as grouping evidence before keyword heuristics; never split a claim set an obligation names unless a Story proposal does. |
| R-3 | story | Values for every spoken number in every package; unenumerated cohorts with `expectedCount`; `mediaNeeds.count` for works in multiples; `needsOnScreenText` for quoted text inside narrator claims. |
| R-4 | story | Replace obligation shells with fields; keep the quoted note in provenance. |
| R-5 | story | A narration disposition (render, replace, omit) with provenance. |
| R-6 | story | Record the script wording hash each review note was written against; re-affirm on re-worded sentences. |
| R-7 | matching | Report grouping and label diffs between runs on identical Story input, not only counts. |

## 8. Unresolved evidence carried forward

| ID | Item | Owner | Hand to |
| --- | --- | --- | --- |
| UE-08 | Which splitter revision produced each gold reference; biography gold and baseline differ on 2 beats and 26 labels with identical Story claims | matching | Job 4 |
| UE-09 | Year Seventeen: proposal `p-28-28-2` excludes the names sentence, handoff task includes it; proposal `p-18-18` and obligation `o-18-18` draw opposite boundaries | story | Job 3 |
| UE-10 | `grammar/beat-script-map.json` (builder line 78) absent from this checkout; 21 of 40 legacy beats inexact against script v2.1 | story | Jobs 3 and 7 |
| UE-11 | Session identifier equals Job 1's; execution mode recorded from the invocation, not a runtime field | you | editor, if material |
| UE-03 | Only one story has a committed handoff; the handoff builder is story-specific | story | Job 3 |

## 9. Acceptance

| Check | Verdict |
| --- | --- |
| Beat, claim and VisualTask never conflated | **PASS** — defined from schema, builders and splitter in section 1; every span separates beat boundary, claim boundary and intended moments; the editor's use of "beat" for a task is named, not adopted |
| Every finding distinguishes Story-authoring failure from valid input mishandled by Matching | **PASS** — every span and finding carries `story`, `matching`, `both`, `success` or `undetermined`, and each `undetermined` states what would settle it |
| No runtime or schema change | **PASS** — only the two report files written; Story worktree untouched; no git write command |
| At least 15 spans across all three stories | **PASS** — 23 spans: 9, 6, 8 |
| Receipt names operator, mode, executor, model, display name and effort with provenance | **PASS** — unexposed values listed, none invented |

**PASS** · Next job: `03-upstream-contract-fitness` · Blocker owner: `none`

Stopping after Job 2. Claude Desktop publishes these two files after verifying the acceptance checks.
