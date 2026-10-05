# Job 4 — Matching transformations and visual-job derivation

**Result: PASS** (corrected after editor review, round 1) · Next job: `05-grammar-tags-capabilities` · Blocker owner: `none`

> **Corrected.** The primary defect site is the hardcoded operation inference, **not** the grouping step, and the promised mixed-payload route **does not exist**.
>
> Measured against the editor's own perfect reference, the operation layer agrees on **71%** of operation sets and **90%** of jobs — so the fallback it was accused of overusing is mostly right. What is wrong: **87** operation-set disagreements, **6** operations fired on substrings that are not words, **7** co-perceptibility requirements split apart, and a mixed-payload flag that **nothing reads**.

## Corrections applied

`docs/astra-root-cause/CORRECTION_REQUESTS.md` (opened after `032981c`) is **accepted in full. All three findings were correct** — and applying them exposed two further defects of my own.

| | Request | Action | Verdict |
| --- | --- | --- | --- |
| **C4-1** | Four traces labeled `failure` with empty `divergences` and null `firstDivergentStage` | Every trace re-diagnosed against a **named oracle**; no trace can be `failure` without a supported divergence. Resolutions below. All aggregates recomputed. | corrected |
| **C4-2** | Don't treat a keyword fallback as failure without an oracle; `concept_statement`/`assert_without_data` is not automatically unusable | **Withdrawn, and the measurement reversed.** The gold reference assigns `concept_statement` alone to **103 of 107** such tasks (96%) and the **same job to 107/107**. | conclusion withdrawn |
| **C4-3** | The suppression test proved the flag is *emitted*, not that any consumer acts on it | **Traced and withdrawn.** `mixedPayloadReviewRequired` has **1 write-site and 0 read-sites**. No split route exists. Endorsement withdrawn; recorded unresolved as **UE-26**. | conclusion withdrawn |
| **C4-4** | P4-2 must not make obligation and continuity groups automatically atomic | **Accepted — the original P4-2 was wrong exactly as described.** Revised to separate same-task from linked-task evidence; both counterexamples run and reported. | corrected |
| **C4-5** | *Not raised — found while applying the above* | The **26 continuity-split divergences are withdrawn in full**; the 20 obligation splits reduce to **7**. | beyond request |
| **C4-6** | *Not raised — found while applying the above* | **`taskId` is not unique across packages.** Both packages emit `matching-derived-p01-4-02`. Trace identifiers were ambiguous and a lookup silently collapsed two units. Now keyed `story::taskId` with uniqueness asserted over all 492. | beyond request |

### The four disputed traces

| Trace | Resolution | Oracle |
| --- | --- | --- |
| `jayz-drake::matching-derived-p02-3-06` | **stays failure** → `_presentation_operations` | the text itself — `milestone_reveal` fired on the bare substring `"ready"`, which occurs only inside *"already"* |
| `future-volksgeist::matching-derived-p01-1-04` | **reclassified success** | gold reference assigns the identical operation set and job |
| `future-volksgeist::matching-derived-p01-1-05` | **reclassified success** | gold reference assigns the identical operation set and job |
| `future-volksgeist::matching-derived-p01-4-02` | **stays failure** → `_presentation_operations` | gold `['data_explanation']` vs current `['concept_statement']` |

The fifth row of the trace set is `jayz-drake::matching-derived-p01-4-02` — *a different unit with the same `taskId`*, and a success. It is included deliberately to make the C4-6 defect visible.

## Execution receipt

| Field | Value |
| --- | --- |
| Operator | Claude Desktop (`claude_desktop`) |
| Required / observed mode | `desktop_conversation` / `desktop_conversation` — origin `desktop_app`, no CLI subprocess |
| Resolved model | `claude-opus-5` (Opus 5) · effort `high` |
| Session | `session_014CbgCFFrmJN4PKxJdBpZ7P` · correction round 1 |

Fable was not used — Job 4 is a direct Desktop job. **Independence:** no `matching-layer` ref fetched or read.

## Method — oracles, corrected

A harness imported `pipeline/storypackage_splitter.py` and called its **real internals** over the committed adapter outputs, reproducing production counts **exactly** (307 and 185; **492 units**).

**Four oracles, each named per divergence.** No trace is `failure` without a supported divergence:

1. **The editor-designated gold reference** — available for **306 of 492** units; a differing operation set or job is a divergence.
2. **Story same-task evidence** — an obligation listing ≥2 `mustBePerceptible` facts across >1 claim, whose claims grouping split.
3. **The text itself** — an operation fired on a bare substring that never occurs as a word.
4. Nothing else.

**Deliberately not oracles.** A keyword fallback is not failure. The unattributed editor corpus (Job 3 UE-22) is used nowhere. Continuity groups, shared-resource obligations, multi-operation primary selection and editorial-lane tension are recorded as **informational, explicitly not failures**, because no oracle establishes the chosen behaviour is wrong.

## Corpus measurements

| | |
| --- | --- |
| Units replayed | **492** (unique trace keys: 492) |
| Gold oracle available for | 306 |
| Outcome | 393 success / **99 failure** |
| **First divergent stage** | `_presentation_operations` **92** · `_semantic_units` **7** |
| Divergence kinds | operation-set vs gold **87** · job vs gold **28** · same-task obligation split **7** · lexical false positive **6** |
| Informational (not failures) | multi-operation primary selection 38 · linked-task continuity group 29 · editorial lane with data operation 25 · shared-resource obligation 13 |

**Change from the published version:** first divergent stage was reported as `_semantic_units` 43 / `_primary_operation` 33 / `_presentation_operations` 24. **The primary defect site moves from grouping to operation inference**, because the continuity oracle was withdrawn and the gold-reference oracle was added.

## Agreement with the editor's perfect reference

Across 309 shared task ids (`future-volksgeist`):

| Measure | Agreement |
| --- | --- |
| Operation sets | **221 / 309 (71%)** |
| Jobs | **281 / 309 (90%)** |
| `concept_statement`-only class — operation sets | **103 / 107 (96%)** |
| `concept_statement`-only class — jobs | **107 / 107 (100%)** |

The 4 disagreements in the fallback class all assign `data_explanation` instead.

**This is the measurement that withdrew my published characterisation of the fallback as a defect.** I had framed 177 units as carrying a semantic-null job "purely because no keyword matched", which implied harm the evidence does not support. The perfect reference makes the same call almost always. Only the 4 gold-disagreeing cases are now counted, and **no harmful downstream behaviour is claimed for this class anywhere**.

## Stage-by-stage

**1. Contract gate and adapter — LOSSLESS** (unchanged). 502 → 502 and 222 → 222 claims, **zero** differences on text, span, lane, entityRefs, values or cohortRefs. Obligations, continuity and jobProposals all preserved. Whatever is lost later was present and correct here.

**2. `_split_claim_segments` and `_semantic_units` — CONTRIBUTING, 7 of 99** (revised down from 43). One split rule exists: `", but also"` preceded by `"not just"`. Grouping is keyed on the derived operation label, and the structural proof stands — the signature `(*, beat, claim_ids, claims)` means obligations and continuity are **never passed in**, so grouping cannot consider them.

The surviving measured consequence is narrower and better founded: **7 units split a same-task obligation**. The clearest remains `o-formula-flip`, whose two claims state the same chart history producing two different winners under two counting rules, with 3 `mustBePerceptible` facts — they must be co-perceptible for the point to land, and grouping emitted them as two tasks.

**The 26 continuity splits are withdrawn in full.** No continuity group in either package asserts same-task membership.

**3. Operation inference — PRIMARY DEFECT SITE, 92 of 99.** Entirely hardcoded substring matching; reads only `entityRefs`, `values`, `cohortRefs`. Never reads `lane`, though `lane` is on every claim row it receives.

| Operation | Fired | Only on a generic term | Top triggers |
| --- | --- | --- | --- |
| `event_narration` | 160 | **99 (61%)** | `"was "` **95** |
| `archival_progression` | 82 | 34 (41%) | `"in 20"` 21, `"after "` 17 |
| `milestone_reveal` | 51 | 15 (29%) | `"number one"` 19, `"ready"` 7 |

**6 lexical false positives proven from the text itself** — the bare term `"ready"` matches inside *"already"* in 5 of its 7 firings:

> "Pick the weights, and you've **already** picked the winner." → labelled `milestone_reveal`

**4. Derived job labels — DERIVATIVE.** 28 jobs disagree with the gold. Value blindness remains **tested and not confirmed**: zero units carrying structured values received a non-value job, so that failure class is upstream (Job 3 G-05) and **Matching is not at fault**.

**5. Propagation sound, consumption partial.** `presentation_contract` *does* consume obligations (`needsOnScreenText`, `wouldBeALie`, `mustBePerceptible`). What obligations never shape is the **grouping**. **Resolves Job 3 UE-14:** `showTogether`, `focal`, `continuityGroupIds`, `mustBeTrue` — zero occurrences, consumed nowhere.

## The suppression test, completed through the consumers

My published report stopped at flag emission. Traced properly:

| Field | Write-sites | **Read-sites in code** | Observable outcome |
| --- | --- | --- | --- |
| `mixedPayloadReviewRequired` | 1 (`splitter.py:302`) | **0** | **none** — appears only in output artifacts |
| `preferredTreatment` | 1 | **0** | **none** |
| `templateEligible` | 1 | 3 | consumed — suppresses candidacy, routes to b-roll |
| `brollFallbackAvailable` | 1 | 9 | consumed |

**Route vocabulary actually produced:** `template_review` 64, `broll` 18, **`split` 0**.

`matching_agent._route_plan` sets the route from `templateEligible` and candidate presence alone, so **a mixed-payload task receives exactly the same route as any other task**. A split module exists (`visualtask_split_proposals.py`) but reads neither the flag nor `presentationOperations`, is ungated and undeclared (Job 1 AF-03), is imported only by the held-out evaluation path, and has produced **no committed artifact**.

**Conclusion withdrawn.** The flag is written and never read. The promised route/split alternative does not exist at this baseline, so single-primary admission suppresses secondary operations **with no effective mitigation**. My statements that the route "works" and that the rule is "fully endorsed" are withdrawn. Whether necessary meaning is thereby lost **cannot be demonstrated** here — there is no consumer whose behaviour could be observed. Recorded unresolved as **UE-26**.

**What is still true:** the full `presentationOperations` list is preserved in 310/310 tasks in both gold and current output, so nothing is discarded at the artifact level. And the risk the code comment names is real and measured — a union over inferred operations would admit unrelated families on generic-term noise.

**Alternatives evaluated** (no union proposed, per the request):

| Option | Verdict |
| --- | --- |
| Union every inferred operation | **rejected** — candidate explosion on measured noise, no precision gain |
| **Corrected primary selection** | **most promising**, dependent on P4-1. `OPERATION_PRIORITY` is a fixed global tuple (UE-23); raise precision first, then evaluate order against the gold's operation sets, which already disagree on 88 of 309 |
| An existing route | **not available** — no split route exists to route into |
| Implement the promised split route | **out of scope for Jobs 1–7** — a repair, not a finding; recorded for Job 8 |

## P4-2, revised

**Supersedes** the published P4-2, which treated any obligation or continuity group as proof of single-task membership. The discriminating data was already in the adapter rows and my original proposal ignored it.

Continuity rows carry **`scope`** and **`strength`**. The six groups across both packages use `template_family`, `template`, `visual_grammar` and `subject_framing`, all at `strength: preferred`, and **not one asserts single-task membership**. `g-head-to-head`'s invariant reads *"one consistent two-column head-to-head treatment **for every raw count**"* — explicitly many tasks sharing one family.

The revised rule classifies rather than collapses:

- **(a) same-task evidence** — an obligation listing ≥2 `mustBePerceptible` facts across >1 claim → candidates for one task
- **(b) linked-tasks evidence** — a continuity group, identified by `scope`/`strength`, asserting treatment consistency across separate moments → emit `linkedTaskGroup`, **do not join**
- **(c) shared-resource evidence** — an obligation spanning moments with <2 `mustBePerceptible` facts, e.g. one source clip → annotate, do not join
- **(d)** record the reason for every join *and* every split
- **(e)** a join stays subject to the existing coherent-moment payload cap; where it would be exceeded, emit a **linked task set carrying the co-perceptibility note**, not one oversized task

### Counterexample 1 — multi-task continuity groups

| Group | Claims | Current units | Scope | Original P4-2 | Revised P4-2 | Tasks preserved |
| --- | --- | --- | --- | --- | --- | --- |
| `g-head-to-head` | 14 | 14 | `template_family` | join into **one** task — **wrong, oversized** | `link_separate_tasks` | **14** |
| `g-scoreboard-recap` | 6 | 4 | `template` | join 6 across two script parts | `link_separate_tasks` | 4 |
| `g-who-is-future` | 4 | 4 | `subject_framing` | join opening and close | `link_separate_tasks` | 4 |
| `g-streak` | 3 | 3 | `template` | join | `link_separate_tasks` | 3 |

All **6** groups classify as `link_separate_tasks`, **0** as join. Task counts preserved exactly; no group collapsed.

### Counterexample 2 — obligations spanning multiple moments

| Obligation | Claims | `mustBePerceptible` | Revised P4-2 |
| --- | --- | --- | --- |
| `o-formula-flip` | 2 | 3 | `join_same_task` — the flip must read |
| `o-umbrella` | 2 | 0 | `link_shared_resource` |
| `o-clip-p02-6` | 4 | 0 | `link_shared_resource` — one clip heard across moments |
| `o-streak` | 7 | 3 | `join_same_task`, **but capped** by clause (e) |

Of 42 multi-claim obligations, only **4** carry same-task evidence; **38** are shared-resource links.

`o-streak` is the honest limit of the rule and I state it rather than hide it: a 7-claim join across 5 units would itself risk the oversized task the request warns against, so clause (e) applies and the correct output is a linked set, not one task.

**Verdict:** both counterexamples pass. The revised rule preserves every coherent visual-moment boundary, forces no group into an oversized task, records a reason for every decision, and bounds its one aggressive case.

## Story `jobProposals` vs Matching-derived operations

Unchanged by this correction, and still measured rather than asserted. Of **34** authored proposals, **0 of 20** materialize for `future-volksgeist` and **1 of 14** for `jayz-drake` — corroborated by production provenance (307/310 and 185/186 `matching_semantic_split`). In the **27** units where a Story advisory job applied, it differed from the keyword guess in **0** cases, because every proposal proposes `pose_a_question` and the keyword layer independently detects the `?`. Story's advice is **structurally redundant as authored**, not overridden.

## Failure class → earliest divergent stage

| Failure class | Stage | Count | Oracle |
| --- | --- | --- | --- |
| Operation set the perfect reference does not assign | `_presentation_operations` | **87** | gold reference |
| Job the perfect reference does not assign | `_derived_job` | 28 | gold reference |
| Operation fired on a term that never occurs as a word | `_presentation_operations` | 6 | the text itself |
| Co-perceptible claims emitted as separate tasks | `_semantic_units` | 7 | Story obligation (≥2 `mustBePerceptible`) |
| Quantitative claim unmatchable for want of a magnitude | **upstream** | 0 | — (Job 3 G-05, **story**) |
| ~~Continuity group fragmented across tasks~~ | **withdrawn** | 0 | none — wrongly treated continuity as same-task evidence |
| ~~Keyword fallback leaves no usable visual job~~ | **withdrawn** | 0 | none — gold makes the same call in 96–100% of the class |

## Replayable traces

**37 traces** against a minimum of 20 — 14 successes, 23 failures. Every failure carries a non-empty divergence with a **named oracle** and a non-null `firstDivergentStage`. The four disputed traces are included with their resolutions, plus the same `taskId` from the other package to make the composite-key defect visible. Keyed `story::taskId`. Full detail in the JSON.

## Unresolved evidence

| ID | Item | Owner | Hand to |
| --- | --- | --- | --- |
| **UE-26** | Mixed-payload handling unresolved — flag has zero read-sites, no split route, split module unwired; suppression's cost cannot be demonstrated at this baseline | matching | Jobs 6 & 8 |
| UE-23 | `OPERATION_PRIORITY` is a fixed global tuple with no stated derivation | matching | Job 5 |
| UE-24 | The ~120 literal terms have no recorded provenance; the gold now gives a partial oracle (88 of 309 disagree) | matching | Job 7 |
| UE-25 | `year-seventeen` has no committed adapter output, so a second gold oracle is unavailable | matching | Job 6 |
| UE-27 | The gold covers only `future-volksgeist`, so 186 `jayz-drake` units rest on Story and lexical oracles alone | data | Job 7 |

## Acceptance

| Check | Verdict |
| --- | --- |
| Distinguishes Story `jobProposals` from Matching-derived operations | **PASS** — measured; 0/20 and 1/14 materialize; 0-of-27 override with its structural reason |
| Tests primary-operation suppression without proposing an unrelated-family union | **PASS** — test completed **through the consumers**; earlier conclusion **withdrawn** (0 read-sites, no split route, unwired split module); recorded unresolved UE-26; no union proposed; all three named alternatives evaluated |
| ≥20 replayable traces, successes and failures, each naming the first divergent stage | **PASS** — 37 traces; **every** failure has a supported divergence and named stage |
| No code changes | **PASS** — harness outside the repo, read-only imports; all proposals proposal-only; diff touches only the two Job 4 artifacts and the shared correction file's Job 4 entry |

Stopping after the Job 4 correction. **Job 5 not started.**
