# The system, stage by stage

What actually happens between narration and a finished shot, in order. Every stage says
what it takes in, what it puts out, whether a model is involved, what it BELIEVES, and
whether it exists.

Written 2026-09-21 because two false beliefs were found by accident in one day and both
cost a paid rerun. A belief can only be challenged if someone can see it. A stage nobody
has written down cannot be challenged at all — which is how "templates are pre-rendered"
survived inside a prompt while the user knew we render after choosing.

**Read this before changing anything, and before any paid run.** If the change touches a
stage, check what that stage believes. Facts live in `grammar/TEMPLATE-FACTS.md`; this
file says which stage depends on which.

Status: `BUILT` runs today · `PARTIAL` runs but is known incomplete · `ASSUMED` happens
somewhere outside this tree and is not described here · `MISSING` nothing does it.

---

## 1. Narration to timing — `BUILT`, outside this tree
Recorded VO through Whisper, word-level alignment.
**Out:** `year-seventeen-narration-whisper.json`, `-timing.json` — 30 passages, 804s.
**Believes:** nothing about templates.

## 2. Narration to beats — `PARTIAL` · MODEL · `prompts/PROMPT-beats.md`
A beat is one shot. Each carries quote, job (1 of 20), entity_count, entity_kind,
takeaway, must_be_true, must_be_perceptible, would_be_a_lie, unstated.
**Out:** `pipeline/beats-all.json` — 40 beats.
**Believes:** that a beat's requirements can be stated in prose; that `entity_count`
describes the beat's scale.
**Known incomplete:**
- 1,008 of 1,794 spoken words are inside a beat. 435s of 804s has a shot. The rest of
  each passage is unbeaten. Fine for discovering the grammar, not for finishing a video.
- `entity_count` does not describe everything a visual must hold. Beat 26 is one entity
  across six categories and there is no field for the second dimension (FACTS 2.8).
- `would_be_a_lie` is mostly caption constraints, not selection criteria (LOG, user).

### 2b. Beats to VisualTasks — `PARTIAL`, review-only · deterministic · `pipeline/visual_tasks.py`
Builds a source-hashed representation that can split a beat into exact narration tasks,
attach source-bound implied entities, and expand versioned cohorts. The current pilot emits
41 tasks from 40 beats and records one reviewed split for beat 28. It does not read the
global `_subject` declaration and does not guess an unresolved subject as Drake.
**Out:** `grammar/visual-tasks.json`.
**Believes:** a task is the matching unit; an entity may be resolved for continuity while
remaining visually withheld; a semantic item count is not automatically a person count.
**Known incomplete:** only the first source-bound overrides and two cohorts are encoded.
The slate, media, and pairing stages do not consume this artifact yet; activation requires a
separate reviewed migration with before/after output.

### 2c. VisualTask / measured AE requirements comparison — `PARTIAL`, review-only · deterministic
`pipeline/visualtask_ae_spec_comparison.py` imports the frozen AE measurements into a
portable exact-data index, links only explicitly reviewed scene families to measured
projects, and attaches them to the unchanged current slate. A separate mapping sidecar
resolves 20 of the 24 in-scope preview scenes to exact
native compositions from native master-timeline intervals or unique composition-name and
structure evidence; four ambiguous mappings remain explicit. It emits 41 task rows without
ranking, selecting, pairing, or rendering. `pipeline/visualtask_requirements.py` separately
preserves source-supported task constraints and exact saved audio spans for 39 tasks; the
two split beat-28 tasks remain unresolved.
**Out:** `grammar/visual-task-technical-requirements.json`,
`grammar/ae-template-technical-index.json` and
`reports/visualtask-ae-spec-comparison.json`.
**Believes:** a display identity is a semantic requirement, not automatically one media
slot. A project-family link cannot prove which native composition backs an individual
preview scene. Native duration coverage is an observation, not timing-fit approval.
**Known incomplete:** four scene-to-composition mappings, two split-task audio spans,
treatment-specific slot counts and media kinds, single/group eligibility, typed data fields,
required on-screen text and limits, duration-adjustment policy, and media availability are
not yet encoded. The 20 exact mappings expose their native dimensions, duration,
simultaneous/total media inputs and recursive text-field identities. Even so,
`fillable_now` is deliberately not computable, and this comparison is not connected to the
live slate.

## 3. Template pool — `BUILT` · deterministic · `match-trial/candidates.py load()`
`approved-list.json` enriched from `description-inventory.json` and `catalog.json`.
**Out:** 421 records — description, useWhen, avoid, axes, clip path, capability, kind.
**Believes:** `approved-list.json` is authoritative; `selectorEligible:false` and
`reference_only` mean exclude; three templates are scope-restricted (`grammar/SCOPE.md`).

## 4. Capability measurement — `PARTIAL` · MODEL, video · `prompts/PROMPT-describe-clip.md`
Each clip watched; what it ENCODES in its form vs what it PRINTS as text.
**Out:** `grammar/capability.json` — 208 records.
**Believes:** FACTS 1.1–1.4 (media swappable, timing elastic, text fits, nothing baked).
**Known incomplete:**
- 208 of 421. The 49 infographics and 5 spatial scenes have NO capability record, so
  every corpus-wide capability count excludes them. This is how `change_over_time` was
  measured at 2 and reported as a gap.
- 14 AE clips failed on Google 503s: `text-list-carousel` ×9, `story-on-photo-slideshow` ×5.
- Still collects `native_editability` as unclear on every record. FACTS 1.6 settles it;
  the prompt has not been updated.

## 5. Job binding — `BUILT` · MODEL, offline · `pipeline/bind.py` + `PROMPT-bind.md`
Every record judged against all 20 jobs, once, reusable across scripts.
**Out:** `grammar/bindings.json` — 624 bindings, provenance on each. 579 until 2026-09-22, when 19 records the user added were judged and merged. A `--only` run now keeps the existing grammar as its base: the first one rebuilt the whole file from every cached judgment and silently undid salvage_bindings.py. See LOG 0071.
**Believes:** all 17 verified claims, including FACTS 3.6 — rendering happens AFTER
selection, so the question is whether a template can be MADE to carry the job — with the
guard that modification changes the dressing, never the mechanic. Prompt sha `50337c79`.
**Known incomplete:**
- The full rebind under that premise FLOODED two jobs (assert_without_data to 60% of the
  corpus, narrate_an_event to 50%) and collapsed inversion from 11 to 1. The current
  grammar is a per-job MERGE of two runs (`pipeline/salvage_bindings.py`), which Codex
  correctly calls "a named, reversible rollback; not validated as a better grammar".
  **Treat it as provisional.** 333 rows from the current prompt, 241 from two older ones,
  21 user-sourced.
- **A binding's `condition` is free text that nothing evaluates.** 41 of 43
  `assert_without_data` bindings are conditional. See the mechanism gap below.

## 6. Slate build — `BUILT` · deterministic · `pipeline/shotlist.py` + `candidates.py`
Five steps, in order. Each can remove options the next never sees.
1. **job lookup** — the beat's job to its bound records, 1 to 249
2. **match-cut admission** — a beat the user flagged raw b-roll admits match-cut vessels
   across jobs (`is_match_cut`, derived from capability)
3. **spatial route** — over 20 slots goes to spatial scenes only, flagged
4. **capacity rank** — `--capacity` only; annotates `_capfit` and RANKS. Drops nothing,
   because a slot count is not static (FACTS 2.7). A match-cut vessel is exempt entirely.
5. **diversify** — one scene per family, at most 3 slideshow-ish, families holding a user
   pick first, cap 12
**Out:** `pipeline/shotlist.json` / `shotlist.capacity.json`.
**Believes:** FACTS 2.1–2.7.
**THE MECHANISM GAP, found by Codex 2026-09-21 and verified:** this stage cannot enforce
the objective that no option communicates something false. It copies `must_be_true`,
`must_be_perceptible`, `would_be_a_lie` and a binding's `condition` into the shot record
**after** the slate is chosen (shotlist.py:148, 158). **No step evaluates any of them
against the beat.** This is why 43 versus 254 bindings made no difference, and why both
the job grammar and an independent RAG pilot fail the same four beats. It is a mechanism
gap, not a threshold.

## 7. Human review — `BUILT` · `pipeline/ui2`, `ui3-capacity`
Up to 6 per beat, raw-b-roll flag, free-text note.
**Out:** artifact db, then `grammar/picks.json` via `pipeline/ingest_picks.py`.
**Believes:** no selection means nothing was good enough; on a judged beat, unselected
means rejected.
**Missing:** a "needs text template" flag, and a way to say WHAT modification a
near-miss needs — now that everything is modified anyway, "needs modification" is less
useful than naming the modification.

## 8. Grammar — `BUILT` for discovery
User picks become permanent user-named bindings that survive any rerun.
**Out:** `grammar/picks.json`. `grammar/primaries.json` is empty **by agreement** —
choosing one primary per job is deferred until the grammar is settled, not a gap.

## 9. Modify and render — `ASSUMED`, and this is the stage that was invisible
The chosen template is re-cut, recoloured, retyped and rendered to fit the beat.
FACTS 3.6: **rendering happens after selection.** Slot counts change (2.7), colour and
type change (3.4, 3.5), data is bound, footage is dropped into media wells.
**Nothing in this tree describes it, and stages 5 and 6 were written as if it does not
exist.** That is the single largest known gap in this document.

## 10. B-roll and text flagging — `PARTIAL`
**This system's job is DETECTION, not retrieval.** Finding the footage is somebody
else's problem; correctly flagging that a beat wants footage, or wants a text
treatment, is this system's problem. User ruling 2026-09-21: "dont worry about finding
it, worry about correctly flagging that a beat should use it."
**Built:** a raw-b-roll flag the user sets by hand; 4 beats in review pass 1. A flagged
beat admits match-cut vessels across jobs (stage 6 step 2).
**Missing:** the same for text. `define_terms` scored 1/12 and `pose_a_question` 5/12,
and two notes asked for text treatments directly. Three text templates exist and are
unprocessed.
**Open question:** both flags are manual. Nothing derives them, so a new script starts
with none set.

## 11. Edit and assemble — `ASSUMED`, outside this tree

---

## Where a stage's belief is currently wrong

| stage | believes | should believe | cost |
|---|---|---|---|
| 6 slate | a candidate cannot say something false | nothing checks it — conditions and beat requirements are attached after selection | both methods fail the same 4 beats |
| 5 binding | the merged grammar is an improvement | it is a rollback, unvalidated | 241 of 595 rows on two older premises |
| 4 capability | editability is unverified | settled (1.6) | one dead flag on every record |
| 2 beats | entity_count describes the scale | a beat has more than one dimension (2.8) | beat 26 mis-sized |
| 6 slate | a slot is a slot | a slot has an editorial ROLE and a source SPECIFICITY (reference refs 5/6) | b-roll flagged by hand instead of derived |
| 2 beats | a beat is one shot | 12 of 55 reference patterns span 2-5 shots | no way to express a multi-shot figure |
| 10 flagging | a human sets every flag | flags should be derivable, or at least suggested | a new script begins with nothing flagged |

## Evidence from outside this system

Added 2026-09-21. Until then nothing here had ever been checked against anything but our
own reasoning.

- **`grammar/reference-classification.json`** — 30 beats from a reference-channel
  beat-to-visual mapping, classified through `prompts/PROMPT-classify-reference.md`.
  **26 of 30 fit an existing job; all 4 misses were non-editorial** (sponsor read,
  channel ident, mid-roll, placeholder). The taxonomy holds on a script we did not write.
  `assert_without_data` was the MOST-used job, 6 of 26 — it is real, our library just
  cannot serve it.
  Staging carried the beat in **16 of 30**, against our rule that reveal is an editing
  decision. broll/data split 13/17.
- **Creator references 5 and 6**, 122 visual units, in Polish. Their `visualJob` is FREE
  TEXT (122 distinct over 122 units) so it is not a taxonomy to compare against. Two
  fields ARE closed and we have neither:
  `editorialRole` — proof 58, subject 46, context 30, atmosphere 14, comparison, identity,
  scale, transition_support. What a slot is FOR.
  `sourceSpecificity` — exact_event_or_entity_required 63, exact_source_required 50,
  representative_media_allowed 45, decorative_media_allowed 5. How specific the media
  must be. This is the b-roll question answered as a spectrum rather than a boolean.
  48 of 55 of their `segmentPatterns` are `cross_topic` — the portability claim our job
  grammar makes — but 12 of 55 span 2 to 5 shots, which we cannot express.
- **An independent RAG pilot** over the same 421 records and 40 beats (Codex, run by the
  user) scored 32/40 beats served and 66/207 approved — statistically identical to this
  system's 33/40 and 61/199. It placed the right answer FIRST on 14 of 40, which this
  system has no equivalent of. Four beats fail under both methods: 23, 29c, 30a, 30b.

## How to use this file

- **Before changing code**, find the stage. Read what it believes. Check those claims in
  `grammar/TEMPLATE-FACTS.md`.
- **Before a paid run**, check that no stage it depends on is `PARTIAL` for a reason that
  affects the run, and that no claim it rests on is `DISPUTED` or `UNKNOWN`.
- **When a result surprises you**, suspect a belief before a bug. Twice on 2026-09-21 the
  answer was a false belief.
- **When a stage is missing from this file**, that is the finding. Add it.
