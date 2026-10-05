# Job 6 — Candidate admission, diversity, ordering and display

**Result: PASS** (corrected after editor review, round 1) · Next job: `07-human-evidence-and-reference-evaluation` · Blocker owner: `none`

> **Corrected.** The variant ranker works, the display cap is deliberate, and the real defect is a **severed sibling list**. **Ordering, not the cap**, is where the pie chart was lost.
>
> `_within_family` ranks variants on eight keys and builds `_siblings` so the editor can reach the rest of the family. `template_candidates()` drops it before publication, so it reaches no artifact — and the code comment already recorded **429 hidden siblings across 40 beats** and the editor saying *"right family, wrong scene"* **twice**.

## Corrections applied

`docs/astra-root-cause/CORRECTION_REQUESTS.md` (opened after `a898f8f`) is **accepted in full. All four items were correct**, and item 2 pointed at a module this job never opened.

| | Request | Action | Verdict |
| --- | --- | --- | --- |
| **C6-1** | Ordering loss declared zero merely because display cuts by fixed count, not a score | **Reclassified.** The 16-cut is applied *after* an explicit ordering strategy. Pie chart traced: it failed **both** ordering halves. `display_loss` → `ordering_loss`; the two are now non-overlapping. | classification changed |
| **C6-2** | Variant selection called arbitrary; `C.diversify()` ranks variants and computes `_siblings`, which `template_candidates()` omits | **Mechanism rewritten.** Eight-key ranking found in `match-trial/candidates.py` — a module I never opened. "Arbitrary representative" withdrawn. The real defect is narrower and now proven. | mechanism rewritten |
| **C6-3** | 59 tasks used, 21 lack admitted/hidden sets, but only 1 finding typed `lineage_incomplete` | **Counts separated**: 21 incomplete **tasks** vs 1 `lineage_incomplete` **finding**. Reconstruction attempted, unavailable; the 21 are excluded. | scope tightened |
| **C6-4** | B-roll routing concluded from a global flag, not from the 16 tasks' actual routes | **Withdrawn.** The route artifact covers **Year Seventeen only** — 0 of 59 reviewed tasks. My route counts were also double-counted. | conclusion withdrawn |
| **C6-5** | *Not raised — found while verifying item 2* | Prior editor choice **does order** candidates (`picked` is the first sort key, on by default). It doesn't admit — which is what the check asks — but my basis implied no influence anywhere. | beyond request |

## Item 1 — ordering and display are distinct

**The rule now applied:** `ordering_loss` when a family was admitted and the ordering strategy placed it outside *every* surviving slot. `display_loss` only when ordering placed it *inside* a surviving slot and the cap removed it anyway.

**Pie-chart trace** — `jayz-drake…p04-4-03`, editor: *"calls for a pie chart to show porportion. none are good for that."*

| | |
| --- | --- |
| Admitted families | 41 |
| Displayed | 16 (`eight_primary_plus_eight_least_exposed_admitted_families`) |
| Hidden | 25 — pie family is 3rd in that list |
| Pie family exposure | **24 slates** |
| Its rank by ascending exposure among the 41 admitted | **27th** |
| Admitted families at **zero** exposure | **12** |
| Displayed families' exposures | 3, 3, 3, 8, 10, 11, 20, 25, 44, 58, 58, 61, 70, 76, 92, **136** |

The displayed set spans exposure 3 to 136, confirming the two halves use different signals: eight diversify-ranked primary, eight low-exposure exploration. The pie family ranked in **neither** — not top-8 primary, and 27th of 41 by exposure against twelve families at zero.

**So it became unavailable at ordering, not at the cap.** Had either half ranked it, the same 16-cap would have kept it. Assigning this to `display_loss` placed the divergence one stage too late.

All four previously-typed `display_loss` findings are reclassified the same way. **`display_loss` as a first divergence: 0 evidenced.** The 2,210 hidden family appearances remain real — they are the magnitude of what the editor never sees — but the cap *enforces* an ordering decision rather than making it.

## Item 2 — the variant mechanism, as actually implemented

My published description was wrong. The ranking lives in **`match-trial/candidates.py`**, reached via `visualtask_matching.py:18` (`import candidates as C`, after `sys.path.insert(0, ROOT/"match-trial")`) and called at **line 304** as `C.diversify(...)`.

`_within_family` (line 682) returns an **eight-key sort tuple**:

```
(picked, enc, fit, clear, declared, rel, still, id)
```

prior user pick → encoding fit → declared capacity fit → binding verdict `clear` over `conditional` → declares a subject capacity → negated relevance → clip over still → **id**.

**Only the last key is arbitrary, and the docstring names it as such** — *"the arbitrary part is named as such rather than pretending to rank."* "Arbitrary representative" is withdrawn.

`FAM_MAX=1` showing one representative per family is an **intentional review-budget policy** with a stated reason in the code. **A one-variant-per-family slate is not by itself a failure.**

### The code already diagnosed this

`match-trial/candidates.py:795-799`:

> *"FAM_MAX=1 was set after a slate came back 7 scenes from one pack — the cap is right, but it **hides 429 bound siblings across 40 beats** and **the user has twice said 'right family, wrong scene' with no way to reach the sibling**."*

The codebase names the exact defect this job rediscovered, quantifies it, and records that the editor raised it twice. Line 800 sets `r["_siblings"]` to the rest of the ranked family — the designed escape hatch.

### The proven defect: `sibling_propagation_loss`

`template_candidates()` returns a row containing only `candidateId`, `name`, `condition`, `bindingProvenance` and `candidateMatchingProvenance`. **`_siblings` is not in the returned dict.** Verified: grepping `_siblings` across every file in `reports/` returns nothing — it reaches no gallery, no diversity artifact, no review queue, and therefore no review surface.

**The escape hatch built for exactly this complaint is severed one function before it would be published.**

### The case that meets the request's bar

`future-volksgeist…p03-2-01` — editor: *"shouldve shown the version with 2-3 cards, not 6 … 2 slots would be prefered"*

- **Displayed:** `intro-slideshow-full-720p--scene-012` — `slots_at_once: 6`, `structure: grid`
- **Family size:** 38 variants
- **Materially better variants that exist:** `--scene-015` and `--scene-016` (`slots_at_once: 3`, `sequence`); `--scene-002` and `--scene-008` (`slots_at_once: 1`, `slots_total: 2`)

The request's bar is *"proven only where a materially better variant existed and the system could not rank or expose it."* Both hold: the editor asked for 2–3 slots, the family contains exactly that, and the system could not **expose** it because `_siblings` is dropped at the return.

**Honest limit (UE-37):** `_encfit`, `_capfit` and `_rel` are annotated during a live retrieval run and recorded in no committed artifact, so the ranked order of the 38 variants cannot be replayed from the pinned inputs. What *is* established without them: the displayed variant, the existence of better variants, and the severing of `_siblings`.

## Item 3 — lineage coverage, counted separately

| | |
| --- | --- |
| Reviewed tasks used | 59 |
| **Complete** committed lineage | **38** |
| **Incomplete tasks** | **21** (all `future-volksgeist`) |
| `lineage_incomplete` **findings** | **1** |

**21 incomplete tasks is not the same number as 1 incomplete finding**, and neither is used as if it were the other.

**Reconstruction attempted and unavailable.** All 21 have a post-cut gallery slate, but **0 of 21** carry `admittedFamilyCount` or `hiddenAdmittedFamilies`, and the pre-cut admitted set requires re-running admission with `exhaustive_families=True`, which no committed artifact records for these tasks. No lineage was reconstructed, so none is labelled reconstructed and no input digests are claimed.

The 21 are **excluded** from every conclusion requiring admission, hidden-family or first-divergence evidence; stages 2 and 5 are scoped to the 38. Verified that this changes no classification — **zero** findings on those 21 rested on admitted, hidden or ordering evidence.

## Item 4 — b-roll routing: no route evidence exists

This exposed the most serious error in the published job.

`reports/ordered-visual-route-plan.json` holds **41 scenes whose taskIds are all 41 ids of `grammar/visual-tasks.json`** — the Year Seventeen corpus. It covers **0 of the 59** reviewed tasks.

| | |
| --- | --- |
| Reviewed tasks covered by any route artifact | **0 / 59** |
| B-roll-request tasks with an observed route | **0 / 16** |
| Template candidates still displayed on those 16 | **yes, all 16** |
| Actual plan route distribution | `template_review` **32**, `broll` **9** |

**My published counts were also wrong.** I reported "template_review 64 and broll 18" — collected by globbing `reports/*route*.json` and `*ordered*.json`, double-counting the plan against decision-derived rows. The plan holds 32 and 9.

**`forced_template` "not supported" is withdrawn for the reviewed set.** It can only be scoped to Year Seventeen, the sole corpus with observed routes — and the reviewed tasks are not in it. A fallback flag is not a route outcome. Recorded as **UE-36**.

## Seven separate lineage stages

| # | Stage | Observed loss | Failure type |
| --- | --- | --- | --- |
| 1 | Retrieval and eligibility | none measurable | — |
| 2 | Structured capability admission | 0 editor-requested classes unadmitted *(scoped to the 38)* | `admission_error` 0 |
| 3 | Feasibility and native fit | conditional 40 / incompatible 1 / zero native_fit *(Year Seventeen only)* | `feasibility_unknown` systemic |
| 4 | B-roll and no-template routing | **undetermined — no route evidence** | `forced_template` **undetermined** |
| 5 | **Family ordering** | pie family outside both halves | **`ordering_loss`** |
| 6 | **Variant ordering within a family** | `_siblings` severed at the return | **`variant_collapse` / `sibling_propagation_loss`** |
| 7 | Display cap and sampling | 2,210 hidden appearances; enforces ordering | `display_loss` **0 as first divergence** |

**Failure counts:** `displayed_but_rejected` 38 · `valid_no_template_outcome` 16 *(not failures)* · `family_duplication` 4 · **`ordering_loss` 4** · `lineage_incomplete` 1 · `display_loss` **0** · `admission_error` / `not_in_catalog` / `contract_gap` / `metadata_gap` 0.

## What is *not* the problem

| Claim | Verdict |
| --- | --- |
| The displayed variant is chosen arbitrarily | **withdrawn** — eight-key ranking; only the id tiebreak is arbitrary |
| One variant per family is itself a failure | **withdrawn** — deliberate review-budget policy |
| Ordering causes no loss | **withdrawn** — the pie chart is `ordering_loss` |
| `forced_template` is unsupported | **withdrawn for the reviewed set** — no observed routes |
| Admission filters out good candidates | still not supported, **now scoped** to the 38 complete tasks |
| The slate is dominated by repeated families | partially supported — 4 of 59 |

## Acceptance

**Retrieval, admission, ordering and display never collapsed — PASS.** Now seven stages, with family ordering (5) and variant ordering (6) split from the display cap (7), and `ordering_loss`/`display_loss` defined as non-overlapping. Five artifact boundary statements still quoted.

**Historical editor choice does not admit — PASS, with the ordering influence now stated.** Verified at three sites for admission. But `_within_family`'s first and strongest key is `picked = honor_global_picks and r[id] not in _picked_ids()`, and `visualtask_matching.py:311` passes `honor_global_picks=not task.get("ignorePriorSelections", False)` — **on by default**. Prior choice doesn't *admit*; it *orders*. My published basis implied no influence anywhere. The task-level `ignorePriorSelections` override exists and surfaces as `ignoredPriorStorySelections` in candidate provenance.

**"No template" remains valid — PASS as audit discipline, route outcome explicitly unverified.** 16 requests typed `valid_no_template_outcome` and excluded from failure counts; nothing treats a missing template as a defect. The separate claim that routing *handled* them is withdrawn (UE-36).

**No code changes — PASS.** Read-only throughout, including the newly opened `match-trial/candidates.py`. Diff touches only the two Job 6 artifacts and the canonical correction file.

## Unresolved evidence

| ID | Item | Owner | Hand to |
| --- | --- | --- | --- |
| **UE-36** | No reviewed task has an observed route; the route artifact covers Year Seventeen only | matching | Job 8 |
| **UE-37** | `_encfit`/`_capfit`/`_rel` are recorded in no artifact, so within-family order cannot be replayed from pinned inputs | matching | Job 8 |
| **UE-38** | `match-trial/candidates.py` is load-bearing for diversification and variant ranking yet appears **nowhere** in `REFERENCE_MANIFEST.md`'s declared transformation path — which is why this job first missed it. The manifest understates the audited surface | **you** | editor; Job 8 scope |
| UE-32 | `displayLimit` 16 / `slideshowLimit` 6 uniform, no stated derivation | matching | Job 8 |
| UE-33 | Focused-review sampling rationale not reconstructable | matching | Job 8 |
| UE-34 | 21 reviewed tasks have no committed lineage and could not be reconstructed | matching | Job 8 |
| UE-35 | Whether the review surface shows the variant id — now matters more, since `_siblings` never reaches it either way | **you** | Job 8 |
| UE-26 | *(carried)* Mixed-payload handling has no consumer; no split route produced | matching | Job 8 |

Stopping after the Job 6 correction. **Job 7 not started.**
