# Job 3 — Story, Data and Media contract fitness

**Result: PASS** (corrected after editor review, round 1) · Next job: `04-matching-transformations` (Claude Desktop direct) · Blocker owner: `none`

> **The upstream contract is semantically rich and epistemically honest, and it transmits no quantities.**
>
> Matching is told what a number *means*, which words it came from, how it should be displayed, and what caveats attach to it — but never what the number **is**, in what unit, computed how, from which row.
>
> Five gaps are proven to cross-story standard. Five are held as hypotheses pending evidence a single handoff cannot provide.

## Corrections applied

`docs/astra-root-cause/JOB_03_CORRECTION_REQUEST.md` (commit `c04dc6f`) is **accepted in full. All three findings were correct.** Two further errors were found by applying its own test consistently.

| | Request | Action | Verdict |
| --- | --- | --- | --- |
| **C-1** | Typed-gap owners used `shared`, outside the allowed set, while the ownership check was declared passed | G-05, G-07, G-11 reassigned to one accountable `owner` from `{story, data, media, matching}` by artifact ownership. Cross-layer responsibility preserved in a new `supportingOwners` field on every gap, every affected matrix row and every ledger case. Nothing erased. | corrected |
| **C-2** | G-05 proposed `quantity` while claiming verbatim reuse of StoryPackage names, which use `value` | Canonical name settled as **`value`** — a true verbatim reuse — with interoperability justification and a verified compatibility note. `quantity` withdrawn. | corrected |
| **C-3** | G-07's `roundTo`/`roundMode` rested on many values from the *single* Year Seventeen handoff; structural recurrence inside one story ≠ cross-story recurrence | Delta removed from the accepted set, preserved as unresolved hypothesis **UE-17**. The absence of a second handoff is explicitly *not* treated as confirmation. | corrected |
| **C-4** | *Not raised — found by applying the same test to every gap* | Four more gaps failed it and were demoted: **G-04 → UE-18, G-08 → UE-19, G-10 → UE-20, G-12 → UE-21**. Two original recurrence claims were verified **wrong** and withdrawn (below). | corrected beyond request |
| **C-5** | *Not raised — a provenance error found during correction* | All four cited editor records were described as coming from "a package other than the one handoff". **Verified false:** all 49 `matching_output_feedback` records carry `packageId: null`. Every citation reworded; no accepted delta rests on them. | corrected beyond request |

Two of my original recurrence claims were simply wrong, and are withdrawn:

- **G-04** cited Job 2's principle P-3 as cross-package support. P-3 is derived from spans **S04, S11, S12, S15 — all `jayz-drake-settle-it`**. Single story.
- **G-12** claimed Job 2's P-7 was "derived from more than one package". P-7 derives from **span S18 alone — `future-volksgeist`**. Single story.

And on C-5: the four records (`ev_03fa59be374e88f2`, `ev_021919c932e157f2`, `ev_1fa1fe5aefd86338`, `ev_0e82f3649c6cf9b2`) all carry `packageId: null` and use a beat-id namespace (`facts:`, `facts-v2:`, `examples:`) that matches **no** audited package's claim-id scheme. They are **unattributed** and cannot support a cross-story argument in either direction — including mine. Logged as **UE-22**.

**The measured findings are unaffected.** The 27-row matrix, the 74-of-89 display measurement, the disjoint-history topology, the byte-exact receipt verification, the zero-as-unknown enforcement, the media/template verdict separation, and the resolutions of UE-01, UE-03 and UE-09 all stand as published.

## Execution receipt

| Field | Value |
| --- | --- |
| Operator | Claude Desktop (`claude_desktop`) |
| Required / observed execution mode | `desktop_conversation` / `desktop_conversation` — runtime origin `desktop_app`; no CLI subprocess used |
| Resolved model identifier | `claude-opus-5` |
| User-visible model name | Opus 5 |
| Effort (observed) | `high` |
| Metadata source | `get_session` (`session_context.model`, `external_metadata.last_served_model`, `configured_model`) |
| Session | `session_014CbgCFFrmJN4PKxJdBpZ7P` |
| Correction round | 1 |

Policy sets `recordResolvedModel: true` and names no required model, so none was assumed. Fable 5.1 was **not** used and must not be — Job 3 is a direct Desktop job. Job 1's caveat stands: the surface is Claude Desktop with origin `desktop_app`, but execution is cloud-backed, and the policy does not say whether that is excluded.

**Independence.** History was deepened on `fable_analysis` and `main` only. No `matching-layer` ref was fetched or read. Reading `main` is *required* here: the only committed handoff pins a commit on `main`, and whether that pin resolves is a Job 3 question. `main` is not the excluded branch.

## Resolved from earlier jobs

**UE-01 (Job 1) — closed.** After a bounded `--depth=400` fetch, the baseline commit resolves and `git merge-base --is-ancestor 1276d0ca… HEAD` succeeds. **`fable_analysis` does descend from the declared Matching baseline.**

**UE-03 — resolved.** `build_matching_handoff.py` is not a general builder. Lines 15–16 hardcode input and output to one package; its docstring scopes it to that file; lines 82 and 253 embed literal story content. It **cannot** emit a handoff for another package without editing code. Hence two of three audited packages have no Story-owned presentation-requirements artifact, and `story_handoff` has nothing to verify for them. → `G-01`.

**UE-09 — explained.** The handoff declares `year-seventeen@7` and reads the unversioned package file, whose internal `packageId` is `@7`; the audited package is `@9`. Boundary disagreements are **revision skew, not an authoring contradiction**. → `G-02`.

**UE-10 — confirmed absent**, same class as the handoff's other cross-repo references. Carried to Job 7.

## The sufficiency matrix

27 field rows, each scored on *can the handoff carry it* / *can the Story schema carry it* / *is it populated*. Full detail in the JSON under `sufficiencyMatrix.rows`.

| | Count |
| --- | --- |
| Sufficient | 11 |
| Partial | 8 |
| **Insufficient** | **6** |
| Sufficient for its narrow purpose | 1 |
| Sufficient as a report, insufficient as coverage | 1 |

Measured against the one committed handoff: **41 tasks, 32 with a data binding, 89 values, 106 text fields, 3 unresolved items**, plus the 68-field handoff schema and the three audited packages. Every row's `owner` is drawn from `{story, data, media, matching}`; rows with cross-layer obligations carry `supportingOwners`.

### What the contract does well — and it is a lot

- **Value semantics.** 89 values across 14 roles: `count` 17, `comparison` 14, `share` 10, `subject` 9, `total` 6, `time` 6, `rate` 5, `rank_change` 5, `rank` 4, `difference`/`membership`/`threshold`/`ratio` 3 each, `absence` 1.
- **Recognizable identity.** `required` 51, `eligible` 18, `none` 2, `withheld` 1 — distinguishing "must be recognizable", "may be", "must not matter" and "deliberately withheld". Precise, and used.
- **Caveats.** Required on every data binding, non-empty on 20 of 32, and specific — one names that a figure covers a single platform *because the narration said so*.
- **Claim-text receipts.** `linkage.claimTextSha256` per task, recomputed by the validator, so a re-worded sentence invalidates the task depending on it. Exactly the mechanism Job 2's P-9 relies on.
- **Cohort versioning.** Explicit, so Matching can detect cohort drift rather than silently re-expanding.

### The central gap: no quantity anywhere

The Story schema **already carries** what is missing. `storypackage-0.2.schema.json` lines 702–722 define a value object that *requires* `value` (number|string) and permits `unit`, `label`, `entity`, `basis`.

The handoff's value object sets `additionalProperties: false` and permits only:

```
{ valueId, role, anchor, entity, population, display, absence }
```

**No magnitude, no unit, no basis.** In the handoff schema the tokens `"value"` and `"unit"` survive only as members of the *text-field role enum* (lines 463–464) — names of display slots, never data. All 89 observed values use exactly the key set above.

| `display` | Count |
| --- | --- |
| `exact` | 43 |
| `rounded` | 31 |
| `ordering` | 8 |
| `qualitative` | 6 |
| `absent` | 1 |

**74 of 89 values instruct Matching to render a figure exactly or rounded, while the contract carries no figure to render.**

It compounds on the text side. 106 text fields: role `value` **74**, `name` 28, `label` 3, `caveat` 1. Only 28 carry locked `copy`; **78 carry only a `contentRef`** — a narration pointer. Matching must size, truncate and lay out a number it was never given.

The one real handoff makes it concrete — a `role: rate` value with `display: rounded`:

```json
{ "valueId": "v-rate", "role": "rate",
  "anchor": { "claimId": "c1-provoke-1.1",
              "span": { "start": 161, "len": 28 },
              "text": "seven hundred times a second" },
  "display": "rounded" }
```

Rounded to what, from what figure? The only number present is spelled out in prose inside the anchor text.

**And the figures were never derived from the package.** `year-seventeen@7` contains **zero** occurrences of `"values"` — the handoff's 89 values were hand-authored as literals in the builder script.

Notably, **no editor record complains about missing data**: searching all 49 feedback records for "unknown / not stated / no data / missing" returns **zero** hits. The gap surfaces as editorial *hedging*, not as a reported defect — which is why it has gone unnoticed.

## Registry pins: the handoff points into a disjoint history

The handoff pins two cross-repo receipts into `djtoler/astra-visual-selector` @ `da8b175`:

| Receipt | At `da8b175` (pinned) | At the audited baseline |
| --- | --- | --- |
| `grammar/entity-roster.json` | **exists**, 25,546 B, sha `7b6a38a7…b9905` — **byte-exact** vs receipt | **does not exist** (only `entity-roster-source.json`, sha `bea07385…`) |
| `grammar/visual-tasks.json` | sha `0dcc1de3…bc4f` — **byte-exact** vs receipt | sha `a58c8e40…` — different file |

**The receipts are correct at the commit they name.** The problem is the commit:

```
git merge-base da8b175 1276d0ca   →  (empty)
--is-ancestor, both directions    →  false
commits on main not in baseline   →  10
commits in baseline not on main   →  19
```

**`da8b175` and the audited Matching baseline share no common ancestor.** The handoff is a valid, hash-exact contract against a Matching lineage the audited layer does not share. → `G-11`, accountable owner **story** (the handoff and its validator are Story-owned artifacts), supporting owner **matching** (owner of the pinned lineage).

Compounding it, the packages have **moved registry regimes** while the handoff has not: the handoff pins `astra-entity-roster/snapshot` inside the *Matching* repo; packages `@4`/`@5` pin `djtoler/entity_roster/entity-context@1.1.0` in a *separate* repository.

**Validator behaviour.** `check_handoff.py` on the real handoff exits 1 with `no local clone for djtoler/astra-visual-selector`. Mounting the audited Matching checkout then raises an unhandled `FileNotFoundError` from `check.fsha` on the absent roster path. Failing closed on an unmounted repo is **correct and credited**; crashing on a mounted repo missing a pinned path is a robustness defect. Either way: **the only committed handoff cannot be validated end to end at the audited commit pair.**

### Correcting two intermediate readings of my own

Mid-job I believed the receipts were stale *and* that the validator passed anyway. **Both halves were wrong.** The receipts are byte-exact at their pinned commit, and the apparently clean validator run was a **no-op**: `check_handoff.py`'s `main()` iterates over `argv` paths, so invoking it with no arguments validates nothing and returns 0 — and the exit code I first read came from `tail`, not Python.

## Acceptance guards, verified rather than asserted

### Missing data is not treated as zero — **satisfied, and actively enforced**

- `check_handoff.py` lines 37–40 scan every scalar and reject any numeric zero outside a span start: **`"zero value at {path}: unknowns must be typed, not zero"`**. Forbidden *by validation*, not convention.
- `$defs/positiveCount` is `oneOf[integer minimum 1, $defs/unknown]` — zero is **unrepresentable** for a count; unknown is a typed object carrying its reason.
- The handoff uses it: `focal.simultaneous` and `focal.storyItems` carry `{"unknown": "the narration does not say how many pre-streaming rappers"}`, with a matching `focal_unknown` unresolved item.
- `data.values[]` enforces a bi-conditional: `role: absence` requires a reason **and** forces `display: absent`, and vice versa.
- The validator also rejects empty strings and any forbidden selection/capacity key, keeping template choice out of the Story contract entirely.

The system is **rigorous about not inventing facts and silent about not transmitting them** — which is precisely why its safeguards never caught G-05.

### Missing media is not treated as candidate incompatibility — **satisfied**

Disjoint vocabularies in `visualtask_batch_matching.py`: fit uses `{native_fit, adapted_fit, conditional, incompatible, unresolved, no_candidate}`; media uses `availabilityVerdict ∈ {available, unavailable, conditional, unresolved, not_required}`. The media vocabulary has **no** `incompatible` member.

Over the 41-task run: `templateVerdicts` — `conditional` 40, `incompatible` 1. `mediaVerdicts` — `not_required` 30, `available` 7, `unavailable` 3, `conditional` 1. **Three tasks have unavailable media; only one is template-incompatible.**

*Side observation:* 40 of 41 template verdicts are `conditional`. Handed to Job 6 as UE-16.

## Typed gaps — 5 proven, 5 held, 1 by design without a delta

Every `owner` is one accountable layer from `{story, data, media, matching}`, chosen by **artifact ownership**; `supportingOwners` records who must supply or consume the contract without diluting accountability.

### Accepted deltas (cross-story evidence established)

| Gap | Title | Owner | Supporting | Recurrence basis |
| --- | --- | --- | --- | --- |
| **G-05** | Handoff cannot carry value magnitude, unit or basis | story | data, matching | Job 2 P-4 spans **two** stories (S09 jayz-drake; S16, S17 future-volksgeist); independently measured — `values` appears in jayz-drake only (50 in `@3`/`@4`), **zero** in the other two packages; and the schema defect is story-neutral by construction |
| **G-11** | Cross-repo pins resolve only against a disjoint Matching history | story | matching | Measured git topology, not story observation; affects 2 of 3 required snapshot receipts; **adds no semantic field** |
| **G-01** | Handoff builder hardcoded to one package | story | — | Measured across all **three** packages: two lack a handoff entirely |
| **G-02** | Freshness measured against the pinned file, not the current revision | story | matching | Property of shared Story-owned validator code governing every package, plus the measured `@7`↔`@9` skew |
| **G-09** | Evidence kinds don't separate document / quote / lyric / artifact | story | media, matching | Job 2 F-08 spans **two** stories (S16, S19, S20 future-volksgeist; S10 jayz-drake) |

### Held as unresolved hypotheses (excluded from accepted deltas)

| Gap | Title | Held as | Why it failed the test |
| --- | --- | --- | --- |
| G-07 | Rounding precision (`roundTo`, `roundMode`) | **UE-17** | All 89 values come from the single Year Seventeen handoff *(the request's finding)* |
| G-04 | First-class relation participants and direction | **UE-18** | P-3's support is all one story; editor evidence unattributed |
| G-08 | Source-row locator (`dataRef`) | **UE-19** | Need follows from G-05, not from independent cross-story evidence |
| G-10 | First-class adjacency | **UE-20** | Both observations come from the single handoff |
| G-12 | Disposition for replaced/omitted narration | **UE-21** | P-7 derives from span S18 alone |

Each hypothesis retains its full proposal text under `heldHypothesis` in the JSON — nothing is lost — plus a `whatWouldSettleIt` statement. **G-03** (absent beat-to-script join) proposes no delta by design.

### G-05's canonical name, settled

The property is **`value`** — the name the StoryPackage value object already uses at `storypackage-0.2.schema.json:705`. The verbatim-reuse claim is now *true*; `quantity` is withdrawn.

- **Justification:** the builder can copy `value`, `unit` and `basis` across without a rename or projection, so both schemas share one vocabulary and no mapping table needs maintaining. A new name would require a documented projection for no benefit.
- **Compatibility, verified:** in the handoff schema the token `"value"` occurs **exactly once**, at line 463, as a member of the `tasks[].text.fields[].role` enum. An enum member string and a property name under `tasks[].data.values[]` occupy different namespaces, so adding a `value` property introduces no ambiguity and invalidates no existing document.
- **Constraint:** require `value` when `display` is `exact` or `rounded`; forbid it when `role` is `absence`, preserving the absence bi-conditional. It cannot reintroduce zero-for-unknown, because the absence and unknown mechanisms already own that case.

One candidate field remains **rejected outright**: a per-task simultaneous-focal ceiling, prompted by one task carrying `focal.simultaneous = 93`. That may be correct for a 93-member cohort, and a ceiling from one data point risks converting a legitimate large cohort into an artificial incompatibility. Handed to Job 6.

## Attribution ledger — who owed what

Each case names one accountable owner from the allowed set, with supporting owners recorded separately.

| Case | Evidence | Absent because | Accountable | Supporting | Matching at fault |
| --- | --- | --- | --- | --- | --- |
| A-01 | `ev_03fa59be374e88f2` *(unattributed)* | upstream meaning/data missing | story | data | **no** |
| A-02 | `ev_021919c932e157f2` *(unattributed)* | mixed | story | matching | **partially** |
| A-03 | `ev_1fa1fe5aefd86338` *(unattributed)* | Matching failed, upstream adequate | matching | — | **yes** |
| A-04 | `ev_0e82f3649c6cf9b2` *(unattributed)* | Matching failed, upstream adequate | matching | — | **yes** |
| A-05 | G-01 (2 of 3 packages) | upstream artifact never produced | story | — | **no** |

A-02 remains the instructive case. The editor writes:

> "All options are bad. 24, 38, 45 wouldve been much better because its **group vs group and entity vs entity with multiple. both thresholds are the seperate groups.**"

The editor diagnoses the failure in precisely the vocabulary the contract lacks — the relation is group-vs-group, and the two thresholds *are* the two sides. Part of the meaning was genuinely absent **and** the role/entity/population triples present were enough to tell both sides were groups, which Matching did not use. Accountability sits with `story` for the contract; `matching` is recorded as a supporting owner for the misreading. The case is split, not assigned.

**All four cited records are unattributed** (`packageId: null`, UE-22). The ledger is therefore illustrative, not a population estimate — only 10 of 49 records name a better or unoffered option. Jobs 6 and 7 should quantify the split against attributable evidence.

## Coverage, stated honestly by the contract itself

The `unresolved[]` mechanism works. It records plainly that **66 claims have no VisualTask** and that the 41 tasks cover only the 40 reviewed beats, plus a `focal_unknown` and an untasked clause. A correct disclosure — and it means the whole Matching run is scoped to the reviewed subset.

## Unresolved evidence carried forward

| ID | Item | Owner | Hand to |
| --- | --- | --- | --- |
| **UE-17** | *Hypothesis (G-07)* — does the handoff need explicit rounding precision? Validating needs a second handoff, which depends on G-01 | story | Job 8 |
| **UE-18** | *Hypothesis (G-04)* — does it need a first-class relations object? | story | Job 4 |
| **UE-19** | *Hypothesis (G-08)* — do values need a source-row locator? | data | Job 8 |
| **UE-20** | *Hypothesis (G-10)* — does it need first-class adjacency? | story | Job 4 |
| **UE-21** | *Hypothesis (G-12)* — does replaced/omitted narration need a disposition? | story | Job 7 |
| **UE-22** | All 49 `matching_output_feedback` records carry `packageId: null` and a beat-id namespace matching no audited package, limiting every cross-story argument resting on them | data | Job 7 |
| **UE-13** | Whether `main` or the frozen baseline is the intended Matching authority. Histories are disjoint; only the editor can settle it | you | editor → Jobs 4, 8 |
| UE-14 | Does Matching consume `showTogether`, `continuityGroupIds`, `focal` at all? | matching | Job 4 |
| UE-15 | The 49 feedback records' source digest is unverifiable here | data | Job 7 |
| UE-16 | 40 of 41 template verdicts `conditional` — honest uncertainty, or a matcher that cannot conclude? | matching | Job 6 |
| UE-02 | *(carried)* 18 of 24 evidence sources unreachable | data | Job 7 |

## Acceptance

| Check | Verdict | Basis |
| --- | --- | --- |
| No layer blamed for data it does not own; every typed gap assigned to `story`/`data`/`media`/`matching` | **PASS** | Owners now `story` 10, `data` 1 — all in-vocabulary. `shared` removed everywhere, including the matrix and ledger. Cross-layer responsibility preserved via `supportingOwners` + `ownerRationale`, not erased. G-05 → `story` (field is in the Story-owned schema) with `data` as figure supplier and `matching` as consumer; G-08 → `data`. A-05 still declines to fault Matching for requirements never sent; A-02 still records a matching share |
| Missing data not treated as zero; missing media not treated as incompatibility | **PASS** | Unchanged and independently verified in code *and* empirically |
| Every proposed field justified by recurring evidence, not one story | **PASS** | Enforced **by demotion**, not assertion: 5 accepted with cross-story or story-neutral basis; **5 failed and were removed** to UE-17–UE-21; 2 original claims verified wrong and withdrawn; the unattributed corpus supports no accepted delta; 1 field still rejected outright. Absence of a second handoff is nowhere treated as confirmation |
| JSON contains a field-by-field sufficiency matrix and a minimal delta for each **proven** gap | **PASS** | 27 rows; 11 gaps each with `deltaStatus`; only the 5 proven carry a delta, the 5 unproven carry `null` with text preserved under `heldHypothesis` |
| G-05's proposed name and naming rationale agree | **PASS** | Canonical name `value` = StoryPackage's own field name, so verbatim reuse is true; compatibility verified (one occurrence, enum member, different namespace); `quantity` withdrawn; provider- and story-neutral |
| No schema edited | **PASS** | All deltas proposal-only; diff touches only the two Job 3 artifacts; Story worktree clean at `d5117a6d`; no earlier job output modified |

Stopping after the Job 3 correction. **Job 4 not started.**
