# Job 6 — Candidate admission, diversity, ordering and display

**Result: PASS** · Next job: `07-human-evidence-and-reference-evaluation` (Fable 5.1 via CLI at medium) · Blocker owner: `none`

> **Good candidates do not disappear at retrieval, admission or ordering. They disappear at display, twice over.**
>
> A fixed 16-family cap hides **2,210** admitted family appearances across 59 focused tasks — and within every family that *does* survive, only **one arbitrary variant** is shown, although **32 of 36** multi-variant families differ in exactly the slot count and readability the editor names as deciding.

## Execution receipt

| Field | Value |
| --- | --- |
| Operator | Claude Desktop (`claude_desktop`) |
| Required / observed mode | `desktop_conversation` / `desktop_conversation` — origin `desktop_app`, no CLI subprocess |
| Resolved model | `claude-opus-5` (Opus 5) · effort `high` |
| Session | `session_014CbgCFFrmJN4PKxJdBpZ7P` |

Fable was not used — Job 6 is a direct Desktop job. **Independence:** no new fetch; no `matching-layer` ref read.

## Evidence basis — the attributed oracle

Job 6 rests on the **attributed** editor review artifacts (`reviewer: dwaynetoler`), hash-verified in Job 1: 48 decisions over 47 Future tasks and 12 over 12 Jay-Z tasks. They are keyed `taskId::candidateId`, so a complaint joins to the exact candidate and task.

It deliberately does **not** use the 49 `matching_output_feedback` records as an oracle — the Job 3 correction established they carry `packageId: null` (UE-22).

**Status and comment are separate authorities.** Future: 3 rejected, 11 acceptable, **34 unreviewed**. Jay-Z: 2 acceptable, **10 unreviewed**. Many `unreviewed` rows carry substantive comments — including *"All acceptable selections"* — so `unreviewed` is a workflow state, **not** a rejection. Sentiment is read from comment text only.

**Lineage completeness:** 59 reviewed tasks traced; **38** have a full focused-diversity record. The other 21 Future tasks have gallery + review but no admitted/hidden family sets, so their findings are typed `lineage_incomplete` rather than guessed.

## The seven stages, evaluated separately

| # | Stage | Measured loss | Failure types |
| --- | --- | --- | --- |
| 1 | Eligibility and scope filtering | none measurable | — |
| 2 | Structured capability admission | median 38/97 (FV) and 61/97 (JD) catalog families not admitted — but **zero** editor-requested classes among them | `admission_error` **0 evidenced** |
| 3 | Feasibility and native fit | `conditional` 40 / `incompatible` 1 / **zero `native_fit`** | `feasibility_unknown` — systemic **by design** |
| 4 | B-roll and no-template routing | none; route exists and is used 18 times | `valid_no_template_outcome` (16, **not failures**) |
| 5 | Family/variant deduplication and diversity | **every family appears exactly once in all 484 slates** | **`variant_collapse`** (systemic), `family_duplication` (4) |
| 6 | Relevance ordering | none — display cuts by fixed count, not by score | `ordering_loss` **0 evidenced** |
| 7 | Display limits and focused sampling | **2,210 hidden admitted family appearances**; retention 25% / 31% | `display_loss` (3 evidenced; systemic in magnitude) |

Admission is **generous**: 4,896 candidate cards across 310 Future tasks, and **310 of 310 tasks have at least one candidate** — zero empty. Median admitted families: 61 (FV), 41 (JD).

Display is **uniform**: `displayLimit` = **16** and `slideshowLimit` = **6** on every focused task in both packages, with one strategy everywhere — `eight_primary_plus_eight_least_exposed_admitted_families`.

The diversity pass genuinely helps at the family level: unique families across focused slates rise **58 → 94** (FV) and **59 → 94** (JD).

**UE-16 resolved.** Job 3 asked whether 40-of-41 `conditional` means honest uncertainty or a matcher that cannot conclude. **Honest uncertainty, structurally** — the verdict is forced by a stated evidentiary rule, and Job 5 showed native editability is unknown for all 442 capability records, so a `native_fit` claim would be unsupported.

## Primary finding — `variant_collapse`

A failure type not in the spec's list, defined here because the evidence demands it.

**The proof:**

- Across **all 484 slates** in both packages, every family appears **exactly once**; max variants-per-family is **1 on every task**
- **36 of 97** catalog families have more than one variant, and **32 of those 36** differ in `slots_at_once`, `readable` or `structure`
- So variant is precisely where slot count and readability live — and variant choice never reaches the editor

**The editor names it, three ways:**

> *"intro-slideshow-full-720p--scene-012 is a good selection as well but **shouldve shown the version with 2-3 cards, not 6** … 2 slots would be prefered"*

> *"**base-single-billboard has double and triple hero ver[sions]**"*

> *"**06-the-history--scene-001 wouldve been perfect**"* — written twice, on `p03-6-04` and `p03-6-05`

That last one is the cleanest proof in the corpus, and tracing it corrected my own first reading. The family `06-the-history` **was displayed** on both tasks — so this is *not* a display loss of the family. What was displayed was `--scene-005` and `--scene-006`. The editor asked for `--scene-001`, whose `readable` set is `['label','exact_value']`; **neither displayed variant carries `label`**. The family has **11 variants** spanning `slots_at_once` 1–2 and structures `single`, `pair`, `sequence`.

The editor was right, and the pipeline was not wrong about the family — it was wrong about the variant, and it has no mechanism to be right.

**This confirms Job 5's MC-4 (`item_range`) and upgrades it from a proposal to an evidenced need.** Job 5 observed that a cohort of 14 and a cohort of 3 are indistinguishable because `growable` is a bare boolean, null on 90 records. Job 6 now has the editor naming slot count as the deciding factor on four separate tasks.

## Proven `display_loss` — a closed loop

Task `jayz-drake-settle-it.proposal.matching-derived-p04-4-03`:

> *"this first part of this beat **calls for a pie chart** to show porportion. **none are good for that.**"*

Traced: the catalog holds exactly one pie family, `3d-pie-chart-set`. On this task it is in **`hiddenAdmittedFamilies`** — admitted by the capability pass, then withheld by the 16-family display cap. Absent from `displayedFamilies` and from the gallery slate.

The editor asked for a pie chart; the catalog has one; admission admitted it; **the display cap hid it.** `display_loss`, proven end to end against an attributed request.

## What is *not* the problem

Stating this plainly matters as much as the findings, and three of my own going-in assumptions did not survive:

| Claim | Verdict | Basis |
| --- | --- | --- |
| Good candidates are filtered out by admission | **not supported** | Across the 38 fully-traced tasks, **not one** editor-requested family class fell in `notAdmittedCatalogFamilies`. All six classes the editor names exist in the 97-family catalog, so `not_in_catalog` is unsupported too |
| Ordering drops good candidates | **not supported** | Display cuts by a fixed count under a stated strategy, not by a score; ordering carries an explicit scope excluding admission and fit |
| The slate is dominated by repeated families | **partially supported, narrower than expected** | The editor flags recurrence on **4 of 59** tasks — most sharply *"the selected carousel that keeps coming up and is usually irelevant"*. But family dedup is total *within* a slate and variety rises 58→94. The repetition is **across** slates, which the least-exposed-family half of the strategy is meant to address |
| The system forces a template where none belongs | **not supported** | `brollFallbackAvailable` true on every task; broll route produced 18 times; `media_candidates.py:7` states a beat with no candidates is a **finding**, not a failure |

The largest single count in the classification is **38 `displayed_but_rejected`** — the requested family class *was* shown and the editor still judged the slate inadequate. I define that type explicitly so it is **not** miscounted as a pipeline loss. Much of it is the variant problem above; the rest is genuine editorial judgment about specific templates.

## Failure classification

| Type | Count |
| --- | --- |
| `displayed_but_rejected` | 38 |
| `valid_no_template_outcome` *(not a failure)* | 16 |
| `family_duplication` | 4 |
| `display_loss` | 3 |
| `lineage_incomplete` | 1 |
| `admission_error` · `ordering_loss` · `not_in_catalog` · `forced_template` · `contract_gap` · `metadata_gap` | **0 evidenced** |
| `variant_collapse` | systemic — 484/484 slates |
| `feasibility_unknown` | systemic by design — 40/41 conditional |

Full per-task lineage for all 59 reviewed tasks is in the JSON under `reviewedTaskLineage.rows`, each with operations, job, editor statuses and comment, gallery families, admitted/displayed/hidden/not-admitted family sets, and typed findings.

## Acceptance

**Retrieval, admission, ordering and display are never collapsed into one score — PASS.** Seven stages reported separately, never aggregated. The separation is also verified *in the artifacts*: five distinct boundary statements, including `retrieval_only_not_fit`, `ordering_only_not_admission_or_fit`, the gallery's `ordering_only_not_admission_fit_selection_or_rendering`, the diversity boundary (*"an admitted family is eligible for editor review only; this report does not establish native fit"*), and `_presentation_candidates`' `evidenceBoundary`.

**Historical editor choice does not admit a new-story candidate — PASS.** Verified at three sites: the matcher has no reference to prior or carried choices and admits only from the capability record; `carry_prior_route_choices` acts only on rows already at `template_review` and adds no candidate; the batch matcher treats prior-review reconciliation as `_review_only`. The audit's own discipline matches — editor decisions judge the slates they were made against, never admit elsewhere.

**"No template" remains a valid correct outcome — PASS.** 16 of 59 reviewed tasks carry an explicit b-roll/no-template request, typed `valid_no_template_outcome` and **excluded from failure counts by definition**. `forced_template` is recorded as not supported.

**No code changes — PASS.** Read-only throughout; only the two Job 6 reports created.

## Unresolved evidence

| ID | Item | Owner | Hand to |
| --- | --- | --- | --- |
| **UE-32** | `displayLimit` 16 and `slideshowLimit` 6 are uniform everywhere with **no stated derivation** — and 16 is the single highest-leverage number in the pipeline | matching | Job 7 |
| UE-33 | Focused review covers 26/310 and 33/186 tasks; the sampling rationale is not reconstructable from the artifact | matching | Job 7 |
| UE-34 | 21 of 47 reviewed Future tasks have no diversity record, so their admitted/hidden sets are unknown | matching | Job 8 |
| **UE-35** | The editor named `--scene-001` while a different scene was displayed. **Whether the review surface shows the variant id at all** cannot be established here — and it bears on how to read every "no good candidates" comment | **you** | Job 7 |
| UE-26 | *(carried)* Mixed-payload handling has no consumer. Job 6 adds: **no split route is produced in any artifact** — the vocabulary is `template_review` and `broll` only, yet three reviewed tasks ask to split the beat, including *"beat should be split into 2"* | matching | Job 8 |

Stopping after Job 6.
