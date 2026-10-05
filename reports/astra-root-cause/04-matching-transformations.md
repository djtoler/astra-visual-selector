# Job 4 — Matching transformations and visual-job derivation

**Result: PASS** · Next job: `05-grammar-tags-capabilities` (Claude Desktop direct) · Blocker owner: `none`

> Meaning is lost in two places, and **neither is the one the symptom suggests.**
>
> The single-primary admission rule is sound and its mixed-payload route works. The damage is done earlier — by a grouping step that is never given the Story's own boundary evidence, and a keyword layer where **36% of tasks match nothing at all** and **61% of one family's hits rest on the word "was"**.

## Execution receipt

| Field | Value |
| --- | --- |
| Operator | Claude Desktop (`claude_desktop`) |
| Required / observed mode | `desktop_conversation` / `desktop_conversation` — origin `desktop_app`; no CLI subprocess |
| Resolved model | `claude-opus-5` (Opus 5) |
| Effort (observed) | `high` |
| Session | `session_014CbgCFFrmJN4PKxJdBpZ7P` |

Policy sets `recordResolvedModel: true` and names no required model, so none was assumed. Fable was not used — Job 4 is a direct Desktop job. **Independence:** no new fetch; no `matching-layer` ref read.

## Method — a real replay, not a reading

A harness imported the production module `pipeline/storypackage_splitter.py` and called its **real internals** over the committed adapter outputs for two packages, capturing every stage's input and output per unit.

**Fidelity check.** The harness replicates `build()`'s `materialize` test (lines 362–387) and its covered-claim exclusion, and reproduces production task counts **exactly**: 307 matching-derived units for `future-volksgeist` against 307 in the v13 artifact, and 185 for `jayz-drake` against 185. **492 units replayed.**

**Divergence oracle — Story's own evidence, not opinion.** A unit is divergent when it contradicts a Story artifact that was available at that stage: an obligation or continuity group whose enumerated claims the grouping split apart; a lane that contradicts the chosen operation; structured values present while the derived job is not value-bearing; three-plus operations with one kept; or ambiguous Story advice discarded. This keeps the audit story-neutral and avoids resting on the unattributed editor corpus (Job 3 UE-22).

**One harness bug, corrected.** A first run indexed advisory proposals by a `beatId` key that `jobProposals` do not carry, making every unit look matching-derived. That was a harness artefact, not a finding. Corrected by replicating `build()`'s real indexing via `claims[claimId]['beatId']`, after which counts matched production exactly and 27 units correctly showed a Story advisory job.

## Corpus measurements

| | |
| --- | --- |
| Units replayed | **492** (`future-volksgeist` 307, `jayz-drake` 185) |
| Outcome | 392 success / **100 failure** |
| First divergent stage | `_semantic_units` **43** · `_primary_operation` **33** · `_presentation_operations` **24** |
| Operations per unit | 1 → 355 · 2 → 99 · 3 → 27 · 4 → 9 · 5 → 2 |
| Final job | `assert_without_data` **220** · `narrate_an_event` **164** · `derived_quantity` 35 · `enumerate` 31 · `pose_a_question` 30 · `parallel_instances` 10 · `define_terms` 1 · `proportion_of_cohort` 1 |

**384 of 492 units (78%) receive either `assert_without_data` or `narrate_an_event`** — the two most generic labels in the vocabulary dominate the corpus.

## Stage-by-stage trace

### 1. Contract gate and adapter preservation — **LOSSLESS**

Claim-by-claim comparison of each package against its adapter output:

| Package | Claims in → out | Differences on text, span, lane, entityRefs, values, cohortRefs |
| --- | --- | --- |
| `future-volksgeist@5` | 502 → 502 | **0** |
| `jayz-drake-settle-it@4` | 222 → 222 | **0** (including all 50 value-bearing claims) |

Obligations 42/42 and 6/6, continuity 2/2 and 4/4, jobProposals 20/20 and 14/14 — all preserved.

**The adapter is not the divergent stage for any failure class.** This matters for attribution: Job 3's finding that the handoff schema cannot carry a magnitude is a *contract* gap, and it is **not** accompanied by an adapter that drops data it was given.

*Corrected intermediate reading:* one claim's key set suggested the adapter dropped `values` and `cohortRefs`. Wrong — that claim simply had neither. The per-claim comparison above shows zero loss.

### 2. `_split_claim_segments` and `_semantic_units` — **PRIMARY DEFECT SITE** (43 of 100 first divergences)

**One split rule exists.** `_split_claim_segments` (line 162) splits only on a comma followed by `but also` where `not just` appears earlier. Every other claim returns unchanged. No other scope expansion, contrast, enumeration or clause boundary can ever split a claim.

**Grouping is driven by the keyword label.** `_semantic_units` merges adjacent segments when `same_payload` holds, whose decisive term is `_primary_operation(prior) == _primary_operation(current)` (line 215). The entity term accepts a shared display entity **or both units having none** (line 218), so entity-less claims merge freely to the 260-character cap.

**The structural proof.** The signature is:

```python
def _semantic_units(*, beat, claim_ids, claims)
```

Obligations and continuity are **never passed in**, so grouping provably cannot consider them. They are attached *afterwards* by set intersection against already-fixed `claim_ids` (lines 334–338, 438–439). This is the airtight form of Job 2's observation.

**Measured consequence — 20 obligation splits, 26 continuity splits.** The worst case is stark: continuity group `g-head-to-head` enumerates **14 claims**, and the grouping emitted **14 separate single-claim units**. The Story said these belong together; Matching produced fourteen unrelated tasks.

Equally telling, obligation `o-formula-flip` enumerates the two claims that carry the *entire* editorial point — the same count computed two ways:

> "Count every album that went to number one on the Billboard 200, including collaborations and mixtapes…"
> "Count only studio albums, and Jay-Z leads, 11 to 9."

They became two unconnected tasks. The point *is* the flip, and the flip is what was lost.

**Fields never read anywhere in the transformation path:** `showTogether`, `focal`, `continuityGroupIds`, `mustBeTrue`.

### 3. Operation inference and primary priority — **PRIMARY DEFECT SITE** (24 first divergences)

`_presentation_operations` is **entirely hardcoded substring matching** over lowered text: 13 families, ~120 literal terms. From the claim rows it reads only `entityRefs`, `values` and `cohortRefs`. It never reads `lane` — **although `lane` is present on every claim row it receives**.

**Precision, measured:**

| Operation | Units fired | Fired *only* on a generic term | Top triggers |
| --- | --- | --- | --- |
| `event_narration` | 160 | **99 (61%)** | `"was "` **95**, `"got "` 19, `"came "` 17 |
| `archival_progression` | 82 | 34 (41%) | `"in 20"` 21, `"after "` 17, `"then "` 11 |
| `milestone_reveal` | 51 | 15 (29%) | `"number one"` 19, `"biggest"` 9, `"ready"` 7 |

The single substring `"was "` accounts for 95 firings. That is grammar, not a visual signal.

**A concrete bug — substring matching without word boundaries.** The `milestone_reveal` term list contains the bare substring `"ready"`. Of its 7 firings, **5 match inside the word "already"** and the word "ready" never occurs:

> "Pick the weights, and you've **already** picked the winner." → labelled `milestone_reveal`

Affected: `matching-derived-p07-1-06`, `-p02-3-06`, `-p02-4-05`, `-p08-3-03`, `-p12-1-02`.

**The total-fallback measurement.** **177 of 492 units (36%) fire no keyword at all**, fall through to `concept_statement` (line 110), and *every one* then receives `assert_without_data`. Over a third of all tasks carry the semantic-null job purely because no hardcoded term matched. This is the mechanism behind Job 2's observation about that label's dominance — and the direct reason candidate retrieval has nothing to work with for those tasks.

**Lane contradiction — 25 units.** Story lane `editorial`, primary operation `data_explanation` or `comparison`. The clearest pair:

> "Jay-Z fans say streaming rigged the numbers."
> "Drake fans say the numbers are the numbers."

Both lane `editorial`, both routed `data_explanation`, both given `assert_without_data`. These are attributed opinions, and the lane said so.

### 4. Derived legacy job labels — **DERIVATIVE**

`_derived_job` is a short priority ladder over the operation set plus values, cohorts and entity counts. It adds no new keyword surface beyond a four-term `define_terms` test, so its output is almost entirely determined by whether the keyword layer fired.

**Value-blindness: tested and NOT confirmed.** Every unit carrying structured Story values received a value-bearing job; **zero** units with values fell through to a non-value job. The value branches work where values exist — they are simply unreachable for `future-volksgeist`, whose package carries no values at all. That is a Story authoring gap already owned as **Job 3 G-05**, and Matching must not be blamed for it.

### 5. Entity, value, cohort, obligation and continuity propagation — **PROPAGATION SOUND, CONSUMPTION PARTIAL**

Propagation into the task row is faithful. Downstream, `presentation_contract` **does** consume obligations, deriving `needsOnScreenText`, `wouldBeALie` and `mustBePerceptible` from them (`visualtask_matching.py:60-66, 88-91`), and consumes `values`/`cohortRefs` for its quantitative test.

**This refines Job 2 rather than repeating it.** Obligations are *not* globally ignored by Matching — they shape the presentation contract. What they never shape is the **grouping that decides what a task is**, because `_semantic_units` is not given them. `lane`, by contrast, is handed to the inference function and read by nothing.

**Resolves Job 3 UE-14:** `showTogether`, `continuityGroupIds` and `focal` are consumed **nowhere** — zero occurrences in both the splitter and the adapter. `continuity` is consumed, but as a flat claim-id list attached after grouping, never as grouped `continuityGroupIds`.

### 6. Requirement derivation and unresolved-gap behavior — **THE PROMISED ROUTE EXISTS AND FIRES**

`routeDisposition` is emitted per task, with `mixedPayloadReviewRequired` set by `len(presentation_operations) > 1` (line 302). Measured over `future-volksgeist` v13: **95 of 310** tasks carry it true, and **all 24** tasks with three-plus operations carry it (22 template-eligible, 2 routed to b-roll/cutout with text overlay).

Unresolved spans are reported rather than silently dropped: `build()` tracks covered claims and emits `uncoveredClaims`. Nothing observed fabricates a task to fill a gap.

## The primary-operation suppression test

The acceptance criterion requires testing whether one primary operation suppresses necessary meaning — **without** proposing an unrelated-family union.

**What the code does.** `visualtask_matching.py:207` iterates `enumerate([contract["primaryOperation"]])` — a single-element list. Only the primary admits candidates; the full list is used only for a `_rel` precedence weight.

**The code's own stated rationale** (lines 203–206):

> *"Secondary operations explain the task, but unioning every operation turns an incidental year or phrase into permission for unrelated families. One primary communication requirement controls admission; alternatives for mixed payloads are represented as route/split review, not a broad union."*

**Test result: suppression is NOT silent, and the restriction is empirically justified.**

1. The full `presentationOperations` list is preserved in the published artifact — **310 of 310 tasks carry it in both the editor-designated gold reference and current v13 output**. Nothing is discarded at the artifact level; `primaryPresentationOperation` is an *addition*, consistent with Job 1 AF-08.
2. The author's reason is **confirmed by measurement**, not taken on trust. An incidental phrase really does grant family permission: 61% of `event_narration` firings rest only on a generic term, 95 of them on `"was "`. A union over inferred operations would admit unrelated families on exactly that noise.
3. The promised alternative **is implemented and fires** — all 24 three-plus-operation tasks carry `mixedPayloadReviewRequired: true`.

**Where meaning is nevertheless lost:**

- **Priority inversion, not suppression.** `OPERATION_PRIORITY` is a fixed global tuple, so the winner is whichever family sits highest in it, not whichever the sentence is about. Trace `matching-derived-p02-14-01`: *"So before we can understand Future, we have to meet Nayvadius."* infers `transformation`, `subject_profile`, `archival_progression`; `transformation` wins on priority while the sentence's actual visual job is **meeting a person**.
- **Review-queue dilution** — the real cost of low precision. 95 of 310 tasks (31%) are flagged for mixed-payload review, and a large share of those flags come from the weak keywords above. A review route that fires on a third of all tasks, much of it on the substring `"was "`, cannot function as a selective signal.

**Proposals — no union, and the single-primary rule is endorsed.** Both change input quality and boundary evidence, not admission arity:

| ID | Target | Change |
| --- | --- | --- |
| **P4-1** | `_presentation_operations` | Match on word boundaries rather than bare substrings; remove or qualify generic grammatical terms (`"was "`, `"then "`, `"ready"`, `"the top"`…). Raises precision, making `mixedPayloadReviewRequired` selective instead of a 31% blanket. **Does not widen admission.** |
| **P4-2** | `_semantic_units` signature and call site | Pass obligations and continuity in, and treat a group's enumerated claim set as a boundary constraint. Addresses the 43 first divergences directly, including the 14-way fragmentation of `g-head-to-head`. **The data already exists** and is already attached afterwards — this passes it one stage earlier, so it needs no new contract field. |

## Story `jobProposals` vs Matching-derived operations

They are different objects. A Story `jobProposal` is **authored** (`claimIds`, `job`, `proposalId`, `provenance`). A presentation operation is **inferred** inside Matching by keyword matching. They meet at exactly one line — `storypackage_splitter.py:469-470`, where a single unambiguous advisory job replaces the keyword-derived job.

**Measured fate of all 34 authored proposals:**

| Package | In package | Materialized as own task | Demoted to advisory |
| --- | --- | --- | --- |
| `future-volksgeist` | 20 | **0** | 20 |
| `jayz-drake` | 14 | **1** | 13 |

Corroborated in production: `future-volksgeist` v13 has 307 of 310 tasks with provenance `matching_semantic_split` (the other 3 are `validated_speaker_role`, not job proposals); `jayz-drake` v13 has 185 of 186, with 1 `story_writer`.

**The decisive measurement.** 27 units received their job from a Story advisory proposal. In **0 of those 27** did the advisory job differ from the keyword-derived job. The override is a **no-op** on the current corpus.

**And it is structural, not luck.** Every `jobProposal` in both packages proposes `pose_a_question`. `_derived_job` returns `pose_a_question` whenever `rhetorical_question` is in the operation set, which fires on the presence of `?`. Story proposes a question job for question sentences; the keyword layer independently detects the question mark; they always agree. **Story's advice carries no information the keyword layer does not already have.**

So the visual job in current output is, with one exception in one package, a Matching-derived keyword artefact. Story's proposals are not *overridden by a competing judgment* — they are **structurally redundant as authored**.

*Attribution:* shared in cause, separable in ownership. That 33 of 34 are demoted is a **Matching** rule (the `materialize` test). That they carry only `pose_a_question` is a **Story** authoring choice. Neither layer alone produces the outcome.

## Failure class → earliest divergent transformation

| Failure class | Earliest divergent stage | Count | Attribution |
| --- | --- | --- | --- |
| A comparison or head-to-head fragmented into unrelated single-fact tasks | `_semantic_units` | 26 | matching |
| An editorial point depending on two claims split apart | `_semantic_units` | 20 | matching |
| An opinion sentence treated as a data presentation | `_presentation_operations` | 25 | matching |
| A task carries no usable visual job at all | `_presentation_operations` | 177 units | matching |
| A unit labelled with a family the sentence doesn't support | `_presentation_operations` | measured as precision | matching |
| A mixed-payload sentence resolves to the wrong valid family | `_primary_operation` | 33 | matching |
| **A quantitative claim unmatchable for want of a magnitude** | **upstream of Matching** | **0** | **story** (Job 3 G-05) |

That last row matters. The adapter preserves values losslessly and `_derived_job` uses them correctly wherever they exist. **Matching must not be blamed for this class.**

## Replayable traces

**31 traces provided** against a minimum of 20 — 9 successes, 22 failures, spanning both replayed packages and all three observed divergent stages plus non-divergent cases. Each carries its input, per-stage outputs B through F, its divergences, and its `firstDivergentStage`, with replay instructions. Because the harness reproduces production counts exactly, the traces are **faithful rather than illustrative**. Full detail in the JSON under `replayableTraces.traces`.

## Resolved from prior jobs

| ID | Status | Finding |
| --- | --- | --- |
| **UE-14** | **RESOLVED** | `showTogether`, `focal`, `continuityGroupIds`, `mustBeTrue` — zero occurrences in splitter and adapter; consumed nowhere |
| UE-18 | partially advanced, **still held** | Matching provably cannot derive relation sides (`comparison` rests on a term list plus `len(refs) >= 2`), but this adds *mechanism*, not cross-story recurrence — Job 3's demotion stands |
| UE-20 | **reframed** | The adjacency need is a *grouping* problem, not a contract problem. Continuity groups already enumerate what belongs together; the defect is that grouping never receives them (P4-2). No new contract field required |
| UE-08 | **advanced** | Operations per task, gold vs current: gold `{1:269, 2:32, 3:7, 4:2}`; current `{1:215, 2:71, 3:17, 4:6, 5:1}`. The current keyword set fires materially more often — evidence about trigger behaviour, not revision identity |

## Unresolved evidence carried forward

| ID | Item | Owner | Hand to |
| --- | --- | --- | --- |
| UE-23 | `OPERATION_PRIORITY` is a fixed global tuple with no stated derivation | matching | Job 5 |
| UE-24 | The ~120 literal terms have no recorded provenance, limiting how confidently the list can be pruned | matching | Job 7 |
| UE-25 | `year-seventeen` has no committed adapter output here, so its path could not be replayed | matching | Job 6 |

## Acceptance

| Check | Verdict |
| --- | --- |
| Distinguishes Story `jobProposals` from Matching-derived operations | **PASS** — separated as objects, meeting point named at one line, fate of all 34 proposals measured and corroborated against production provenance; decisive 0-of-27 override measurement with its structural reason |
| Tests whether one primary operation suppresses necessary meaning, without proposing an unrelated-family union | **PASS** — test performed and reported against the hypothesis: suppression is **not** silent. Full list survives 310/310 in gold *and* current; the code's rationale independently confirmed by the 61% weak-keyword measurement; route/split alternative verified firing on all 24 cases. Two residual losses named. **No union proposed**; single-primary rule explicitly endorsed |
| Replayable traces for ≥20 tasks, successes and failures, each naming the first divergent stage | **PASS** — 31 traces, harness reproduces production counts exactly (307 / 185) |
| No code changes | **PASS** — harness lives outside the repo and imports read-only; all proposals labelled proposal-only; only the two Job 4 reports created; Story worktree clean at `d5117a6d` |

Stopping after Job 4.
