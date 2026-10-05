# Job 3 — Story, Data and Media contract fitness

**Result: PASS** · Next job: `04-matching-transformations` (Claude Desktop direct) · Blocker owner: `none`

> **The upstream contract is semantically rich and epistemically honest, and it transmits no quantities.**
>
> Matching is told what a number *means*, which words it came from, how it should be *displayed* and what caveats attach to it — but never what the number **is**, in what unit, computed how, from which row.

## Execution receipt

| Field | Value |
| --- | --- |
| Operator | Claude Desktop (`claude_desktop`) |
| Required / observed execution mode | `desktop_conversation` / `desktop_conversation` — runtime origin `desktop_app`; no CLI subprocess used |
| Resolved model identifier | `claude-opus-5` |
| User-visible model name | Opus 5 |
| Effort (observed) | `high` |
| Metadata source | `get_session` (`session_context.model`, `external_metadata.last_served_model`, `configured_model`), read in Job 1 of this session |
| Session | `session_014CbgCFFrmJN4PKxJdBpZ7P` |

Policy sets `recordResolvedModel: true` for Job 3 and names no required model, so none was assumed. Fable 5.1 was **not** used and must not be — Job 3 is a direct Desktop job. Job 1's caveat still stands: the surface is Claude Desktop with origin `desktop_app`, but execution is cloud-backed, and the policy does not say whether that is excluded.

**Independence.** History was deepened on `fable_analysis` and `main` only. No `matching-layer` ref was fetched or read. Reading `main` is *required* by this job: the only committed handoff pins a commit on `main`, and whether that pin resolves is a Job 3 question. `main` is not the excluded branch.

## Resolved from earlier jobs

**UE-01 (Job 1) — now closed.** After a bounded `--depth=400` fetch, the frozen baseline commit resolves and `git merge-base --is-ancestor 1276d0ca… HEAD` succeeds. **`fable_analysis` does descend from the declared Matching baseline.** Job 1 could not verify this from a depth-1 clone.

**UE-03 — resolved.** `build_matching_handoff.py` is not a general builder. Lines 15–16 hardcode its input and output to one package; its docstring scopes it to that file; lines 82 and 253 embed literal story content in the source. It **cannot** emit a handoff for another package without editing the code. That is why two of three audited packages have no Story-owned presentation-requirements artifact at all — and why the harness's `story_handoff` stage has nothing to verify for them. Gap `G-01`, owner **story**.

**UE-09 — explained.** The handoff declares `year-seventeen@7` and reads the unversioned package file, whose internal `packageId` is `@7`. The manifest's audited package is `@9`. Boundary disagreements between the handoff and `@9` are **revision skew, not an authoring contradiction** within one revision. Gap `G-02`.

**UE-10 — confirmed absent**, and located as the same class of problem as the handoff's other cross-repo references: a Matching-repo grammar path consumed by a Story-layer builder. Carried to Job 7.

## The sufficiency matrix

27 field rows, each scored on *can the handoff contract carry it* / *can the Story schema carry it* / *is it actually populated*. Full detail in `03-upstream-contract-fitness.json` → `sufficiencyMatrix.rows`.

| | Count |
| --- | --- |
| Sufficient | 11 |
| Partial | 8 |
| **Insufficient** | **6** |
| Sufficient for its narrow purpose | 1 |
| Sufficient as a report, insufficient as coverage | 1 |

Measured against the one committed handoff: **41 tasks, 32 with a data binding, 89 values, 106 text fields, 3 unresolved items**, plus the 68-field handoff schema and the three audited packages.

### What the contract does well — and it is a lot

- **Value semantics.** 89 values across 14 roles: `count` 17, `comparison` 14, `share` 10, `subject` 9, `total` 6, `time` 6, `rate` 5, `rank_change` 5, `rank` 4, `difference`/`membership`/`threshold`/`ratio` 3 each, `absence` 1. A genuinely strong vocabulary.
- **Recognizable identity.** `required` 51, `eligible` 18, `none` 2, `withheld` 1 — a four-value vocabulary distinguishing "must be recognizable", "may be", "must not matter" and "deliberately withheld". Precise, and used.
- **Caveats.** Required on every data binding, non-empty on 20 of 32, and specific: one names that a figure covers a single platform *because the narration said so*; another that a derived daily figure reuses one catalog's rate rather than a second statistic.
- **Claim-text receipts.** `linkage.claimTextSha256` per task, recomputed by the validator, so a re-worded sentence invalidates the task depending on it. This is exactly the mechanism Job 2's P-9 relies on, correctly implemented.
- **Cohort versioning.** Explicit, so Matching can detect cohort drift instead of silently re-expanding.

### The central gap: no quantity anywhere

The Story schema **already carries** what is missing. `storypackage-0.2.schema.json` lines 702–722 define a value object that *requires* `value` (number|string) and permits `unit`, `label`, `entity`, `basis`.

The handoff's value object sets `additionalProperties: false` and permits only:

```
{ valueId, role, anchor, entity, population, display, absence }
```

There is **no magnitude field, no unit, no basis**. In the handoff schema the tokens `"value"` and `"unit"` appear only as members of the *text-field role enum* (lines 463–464) — names of display slots, never data. All 89 observed values use exactly the key set above and never a number.

The consequence is sharp:

| `display` | Count |
| --- | --- |
| `exact` | 43 |
| `rounded` | 31 |
| `ordering` | 8 |
| `qualitative` | 6 |
| `absent` | 1 |

**74 of 89 values instruct Matching to render a figure exactly or rounded, while the contract carries no figure to render.** And `rounded` is used 31 times with no precision: `precision` and `decimals` have *zero* occurrences in either schema.

It compounds on the text side. 106 text fields: role `value` **74**, `name` 28, `label` 3, `caveat` 1. Only 28 of 106 carry locked `copy`; **78 carry only a `contentRef`** — a narration pointer. So for most display slots, Matching must size, truncate and lay out a number it was never given, with the narration prose as its only source.

The one real handoff makes this concrete. A `role: rate` value with `display: rounded` arrives as:

```json
{ "valueId": "v-rate", "role": "rate",
  "anchor": { "claimId": "c1-provoke-1.1",
              "span": { "start": 161, "len": 28 },
              "text": "seven hundred times a second" },
  "display": "rounded" }
```

Rounded to what? From what figure? The only number present is spelled out in prose inside the anchor text.

**And the figures were never derived from the package.** `year-seventeen@7` contains **zero** occurrences of `"values"` — so the handoff's 89 values were hand-authored as literals in the builder script, not computed from Story data.

The editor confirms the cost, from a *different* package than the one handoff — `ev_03fa59be374e88f2`:

> "1, 4, and 6 are all great options. **if the number of songs is actually 8 or close, option 4 would be perfect.** otherwise 1 or 6."

The correct template is conditional on a magnitude the contract does not transmit. Notably, **no editor record complains about missing data**: searching all 49 feedback records for "unknown / not stated / no data / missing" returns **zero** hits. The gap surfaces as editorial *hedging*, not as a reported defect — which is why it has gone unnoticed.

## Registry pins: the handoff points into a disjoint history

This was the job's most consequential finding, and it inverted my working hypothesis twice.

The handoff pins two cross-repo receipts into `djtoler/astra-visual-selector` @ `da8b175`:

| Receipt | At `da8b175` (pinned) | At the audited baseline |
| --- | --- | --- |
| `grammar/entity-roster.json` | **exists**, 25,546 B, sha `7b6a38a7…b9905` — **byte-exact** vs receipt | **does not exist** (only `entity-roster-source.json`, sha `bea07385…`) |
| `grammar/visual-tasks.json` | sha `0dcc1de3…bc4f` — **byte-exact** vs receipt | sha `a58c8e40…` — different file |

**The handoff's receipts are correct at the commit they name.** The problem is the commit:

```
git merge-base da8b175 1276d0ca   →  (empty)
--is-ancestor, both directions    →  false
commits on main not in baseline   →  10
commits in baseline not on main   →  19
```

**`da8b175` and the audited Matching baseline share no common ancestor.** The Story→Matching handoff is a valid, hash-exact contract against a Matching lineage that the audited Matching layer does not share. Gap `G-11`, owner **shared** — the handoff is Story-authored but pins a Matching commit, so neither layer alone owns the drift.

Compounding it, the packages have **moved registry regimes** while the handoff has not: the handoff pins contract `astra-entity-roster/snapshot` inside the *Matching* repo, while packages `@4`/`@5` pin `djtoler/entity_roster/entity-context@1.1.0` in a *separate* repository.

**Validator behaviour.** `check_handoff.py` on the real handoff exits 1 with `no local clone for djtoler/astra-visual-selector`. Mounting the audited Matching checkout then raises an unhandled `FileNotFoundError` from `check.fsha` on the absent roster path. Failing closed on an unmounted repo is **correct and credited**; crashing with a traceback on a mounted repo missing a pinned path is a robustness defect — a moved artifact should surface as a typed error. Either way: **the only committed handoff cannot be validated end to end at the audited commit pair by any available means.**

### Correcting two intermediate readings of my own

Recorded so the audit trail is honest. Mid-job I believed the receipts were stale *and* that the validator passed anyway. **Both halves were wrong.** The receipts are byte-exact at their pinned commit. And the apparently clean validator run was a **no-op**: `check_handoff.py`'s `main()` iterates over `argv` paths, so invoking it with no arguments validates nothing and returns 0 — and the exit code I first read came from `tail` in a pipeline, not from Python.

## Acceptance criteria, verified rather than asserted

### Missing data is not treated as zero — **satisfied, and actively enforced**

This is the strongest part of the contract and deserves explicit credit:

- `check_handoff.py` lines 37–40 run a fail-closed scan over every scalar and reject any numeric zero outside a span start: **`"zero value at {path}: unknowns must be typed, not zero"`**. The Story layer forbids zero-as-unknown *by validation*, not by convention.
- `$defs/positiveCount` is `oneOf[integer minimum 1, $defs/unknown]` — zero is **unrepresentable** for a count by construction, and unknown is a typed object carrying its reason.
- The handoff uses it: `focal.simultaneous` and `focal.storyItems` both carry `{"unknown": "the narration does not say how many pre-streaming rappers"}`, with a matching `unresolved` item of kind `focal_unknown`.
- `data.values[]` enforces a bi-conditional — `role: absence` requires a reason **and** forces `display: absent`, and vice versa.
- The validator also rejects every empty string and every forbidden selection/capacity key, keeping template choice out of the Story contract entirely.

Worth stating plainly: the system is **rigorous about not inventing facts and silent about not transmitting them**. G-05 is the opposite failure mode from a zero-for-unknown, which is why the existing safeguards never caught it.

### Missing media is not treated as candidate incompatibility — **satisfied**

Two disjoint verdict vocabularies in `visualtask_batch_matching.py`: template fit uses `{native_fit, adapted_fit, conditional, incompatible, unresolved, no_candidate}`; media uses `availabilityVerdict ∈ {available, unavailable, conditional, unresolved, not_required}`. The media vocabulary has **no** `incompatible` member.

Empirically, over the 41-task run:

- `templateVerdicts` — `conditional` 40, `incompatible` 1
- `mediaVerdicts` — `not_required` 30, `available` 7, `unavailable` 3, `conditional` 1

**Three tasks have unavailable media; only one task is template-incompatible.** Media unavailability demonstrably does not propagate into template incompatibility.

*Side observation, not diagnosed here:* 40 of 41 template verdicts are `conditional`. The matcher almost never reaches a definitive verdict. Handed to Job 6 as UE-16.

## Typed gaps and proposed deltas

11 gaps, each with an owner and a **minimal** proposed contract delta. No schema was edited; every delta is labelled proposal-only and names its target.

| Gap | Title | Owner | Severity |
| --- | --- | --- | --- |
| **G-05** | Handoff cannot carry value magnitude, unit or basis | shared | **primary** |
| **G-07** | Display intent actionable only for values carrying no figure | shared | **primary** |
| **G-11** | Cross-repo pins resolve only against a disjoint Matching history | shared | **primary** |
| G-04 | Comparison participants and direction must be reconstructed | story | — |
| G-08 | No value traceable to its source data row | data | — |
| G-01 | Handoff builder hardcoded to one package | story | — |
| G-02 | Freshness measured against the pinned file, not the current revision | story | — |
| G-09 | Evidence kinds don't separate document / quote / lyric / artifact | story | — |
| G-10 | Adjacency has no first-class expression; continuity sparse (8/41) | story | — |
| G-12 | Narration production will replace has no disposition | story | — |
| G-03 | Legacy beat-to-script join absent | story | *no delta proposed* |

The headline delta (G-05) is three optional properties — `quantity`, `unit`, `basis` — reusing the Story schema's own field names verbatim so the builder can copy them across, with one condition: require `quantity` when `display` is `exact` or `rounded`, forbid it when `role` is `absence`. It cannot reintroduce zero-for-unknown, because the absence and unknown mechanisms already own that case.

### Recurrence discipline

9 of 11 gaps are **structural** schema or validator properties, which cannot be story-specific. The two evidence-anchored ones (G-04, G-09) cite editor evidence or Job 2 findings drawn from a package *other* than the single package that has a handoff.

One candidate field was **rejected** for resting on a single observation: a per-task simultaneous-focal ceiling, prompted by one task carrying `focal.simultaneous = 93`. That may be correct for a 93-member cohort, and proposing a ceiling from one data point would risk converting a legitimate large cohort into an artificial incompatibility. Handed to Job 6 instead.

## Attribution ledger — who owed what

Deliberately small and evidence-anchored, so that no layer is blamed for data it does not own.

| Case | Evidence | Absent because | Owner | Matching at fault |
| --- | --- | --- | --- | --- |
| A-01 | `ev_03fa59be374e88f2` | upstream meaning/data missing | story + data | **no** |
| A-02 | `ev_021919c932e157f2` | mixed | story + matching | **partially** |
| A-03 | `ev_1fa1fe5aefd86338` | Matching failed, upstream adequate | matching | **yes** |
| A-04 | `ev_0e82f3649c6cf9b2` | Matching failed, upstream adequate | matching | **yes** |
| A-05 | G-01 (2 of 3 packages) | upstream artifact never produced | story | **no** |

A-02 is the instructive one. The editor writes:

> "All options are bad. 24, 38, 45 wouldve been much better because its **group vs group and entity vs entity with multiple. both thresholds are the seperate groups.**"

The editor diagnoses the failure in precisely the vocabulary the contract lacks — the relation is group-vs-group, and the two thresholds *are* the two sides. The handoff can say `role: threshold` with a `population` string, but cannot say the thresholds are the sides (G-04). So part of the meaning was genuinely absent — **and** the role/entity/population triples present were enough to tell that both sides were groups rather than individuals, and Matching did not use them. Story owed a clearer relation; Matching owed a correct reading of what it did receive. The case is split rather than assigned.

This ledger is **not a population estimate**: only 10 of 49 feedback records name a better or unoffered option, and that whole block's provenance is unverifiable here (Job 1 UE-02). Jobs 6 and 7 should quantify the split properly.

## Coverage, stated honestly by the contract itself

The handoff's `unresolved[]` mechanism works. It records plainly that **66 claims have no VisualTask** and that the 41 tasks cover only the 40 reviewed beats, plus a `focal_unknown` where the narration does not state a count, plus an untasked second clause. That is a correct disclosure — and it means the entire Matching run is scoped to the reviewed subset, which bears directly on Jobs 6 and 7.

## Unresolved evidence carried forward

| ID | Item | Owner | Hand to |
| --- | --- | --- | --- |
| **UE-13** | Whether `main` or the frozen baseline is the intended Matching authority for the handoff's pins. The histories are disjoint; only the editor can settle it. | you | editor → Jobs 4, 8 |
| UE-14 | Whether Matching consumes `showTogether`, `continuityGroupIds` and `focal` at all, or attaches them after grouping as Job 2 found for obligations and lanes | matching | Job 4 |
| UE-15 | The 49 feedback records anchor this job's ledger but their source digest is unverifiable here | data | Job 7 |
| UE-16 | 40 of 41 template verdicts are `conditional` — honest uncertainty, or a matcher that cannot conclude? | matching | Job 6 |
| UE-02 | *(carried, unchanged)* 18 of 24 evidence sources unreachable | data | Job 7 |

## Acceptance

| Check | Verdict |
| --- | --- |
| No layer is blamed for data it does not own | **PASS** — every gap carries an owner and rationale; G-05 and G-11 assigned `shared`; A-05 declines to fault Matching for requirements never sent; A-02 is split into story and matching shares |
| Missing data not treated as zero; missing media not treated as incompatibility | **PASS** — both verified in code *and* empirically: validator rejects zero-as-unknown, `positiveCount` makes zero unrepresentable, and 3 unavailable-media tasks yielded only 1 incompatible template |
| Every proposed field justified by recurring evidence, not one story | **PASS** — 9 of 11 gaps structural; 2 cite evidence from a package other than the one handoff; one candidate field explicitly rejected for single-observation support; G-03 deliberately proposes no delta |
| JSON contains a field-by-field sufficiency matrix with typed gaps | **PASS** — 27 field rows; 11 typed gaps owned across story/data/shared with minimal deltas |
| No schema edited | **PASS** — all deltas proposal-only; only the two Job 3 reports created; Story worktree clean at `d5117a6d` |

Stopping after Job 3.
