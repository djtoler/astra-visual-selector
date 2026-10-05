# Job 5 — Grammar, tags and template-capability coverage

**Result: PASS** · Next job: `06-candidate-pipeline` (Claude Desktop direct) · Blocker owner: `none`

> **The grammar can express more than the contract carries, and the catalog is built for identity while the job vocabulary is built for data.**
>
> Admission correctly refuses to treat metadata as proof, and all 442 templates honestly record that their native editability is unknown. But only **49 of 442** carry any quantitative role against a job set that is two-thirds data jobs; the job and operation vocabularies **share no names**; and verified native evidence for **344** templates is never reflected back into the record admission reads.

*Output filenames follow the job spec (`05-grammar-capability-audit.*`), which differs from the job file's own slug.*

## Execution receipt

| Field | Value |
| --- | --- |
| Operator | Claude Desktop (`claude_desktop`) |
| Required / observed mode | `desktop_conversation` / `desktop_conversation` — origin `desktop_app`, no CLI subprocess |
| Resolved model | `claude-opus-5` (Opus 5) · effort `high` |
| Session | `session_014CbgCFFrmJN4PKxJdBpZ7P` |

Policy sets `recordResolvedModel: true` and names no required model, so none was assumed. Fable was not used. **Independence:** no new fetch; no `matching-layer` ref read.

## Artifacts audited

| Artifact | Role | Measured |
| --- | --- | --- |
| `grammar/JOBS.md` | the declared closed job set | **21 jobs**, 15 of them data jobs |
| `grammar/bindings.json` | job → treatment bindings | **624 records**, 20 job keys, 370 distinct templates |
| `grammar/capability.json` | **the record admission actually reads** | **442 template records** |
| `grammar/ae-template-technical-index.json` | source-bound AE index | 57 projects, **5,806 compositions**, `renderingPerformed: false` |
| `grammar/ae-scene-composition-mappings.json` | clip-scene → native composition bridge | 398: **140 verified, 244 verified_window, 14 unreviewed** |
| `grammar/library-snapshot.json` | **media** catalog, not templates | 1,685 assets, 15,271 tags, 49 suppressed claims |
| `grammar/class-tags.json` | tags excluded from identity evidence | tag list + a measured collision note |
| `grammar/eligibility-overrides.json` | dated, attributed gate overrides | an `admit` block citing a user decision |

## The two vocabularies share no names

| | Count | Shared names |
| --- | --- | --- |
| `JOBS.md` jobs | 21 | **0** |
| Presentation operations | 13 | **0** |

`bindings.json` is keyed by **job**. Admission is keyed by **primary presentation operation**.

**This is deliberate, not accidental.** `visualtask_matching.py:273-277` states that in the structured path legacy bindings are *secondary evidence only*, and `_supports_operation` reads `record["capability"]`, not the binding's prose — its docstring says **"Generic family words never admit a record."**

The consequence is still real: two parallel descriptions of the catalog coexist. A reader of `JOBS.md` would reasonably believe job bindings drive selection. They do not.

**And the closed set is not closed:**

- 21 jobs declared, **19** have bindings
- `attributed_quote` and `paired_values_by_group` are declared with passages and **have no bindings at all** — `attributed_quote` being the job the cross-story acceptance package was said to add
- `inversion` carries **12 binding records** and appears as a job value in the Year Seventeen gold reference, yet `JOBS.md` does not list it

## Supply versus demand — the inversion

Demand is Job 4's measured job distribution over 492 replayed units. Supply is binding records, and how many have a capability record carrying *any* quantitative role.

| Job | Demand | Bound | Families | **Quantitative-capable** |
| --- | --- | --- | --- | --- |
| `assert_without_data` | **220** | 47 | 27 | **1** |
| `narrate_an_event` | **164** | 141 | 24 | **1** |
| `derived_quantity` | 35 | 15 | 9 | 6 |
| `enumerate` | 31 | **145** | 35 | 2 |
| `pose_a_question` | 30 | 26 | 11 | 0 |
| `parallel_instances` | 10 | 52 | 26 | 11 |
| `locate_in_distribution` | **0** | 22 | 22 | 13 |
| `change_across_set` | **0** | 24 | 15 | 11 |
| `entity_vs_benchmark` | **0** | 18 | 15 | 10 |
| `members_then_total` | **0** | 6 | 3 | **0** |

`JOBS.md` asserts *"roughly two in three beats want a data treatment"* and makes 15 of 21 jobs data jobs. Both the catalog and the measured demand point the other way:

- Only **49 of 442** capability records (11%) carry any quantitative role, against **392 of 442** carrying `identity`
- Only **216 of 624** binding records (34%) serve data jobs
- The two highest-demand jobs — `assert_without_data` 220 and `narrate_an_event` 164 — carry **2 quantitative-capable bound templates between them**
- **13 of 20** bound jobs have *zero* measured demand while holding 175 binding records

Supply and demand are mismatched **in both directions at once**. The data jobs the grammar was designed around are barely exercised by the current operation layer, while the generic jobs it does produce are bound almost entirely to identity-carrying treatments. This is the catalog-level form of the editor's complaint that offered options are wrong for counting and comparison beats.

**Attribution caution:** this is a mismatch between three layers, not one layer's fault. Demand is set by the operation inference (Job 4, *matching*). Job coverage is set by the bindings (*matching*). Whether a beat should have been a data job at all depends on Story values, which Job 3 G-05 shows are not transmitted. No layer is blamed alone.

## Crowding out — narrow, not systemic

Family = template id with a trailing `--scene-NNN` / `--review-NNN` suffix removed.

**Only 2 of 20 bound jobs have a single family at ≥50%** — so the broad worry is mostly not borne out. 18 of 20 draw on several families, and `locate_in_distribution` has 22 variants across 22 families, the healthiest binding in the set.

Where crowding occurs it is severe, and it coincides with the jobs that have fewest records at all:

| Job | Records | Families | Top family share | Why it matters |
| --- | --- | --- | --- | --- |
| `explain_the_encoding` | 5 | 2 | **80%** `intro-slideshow-full-720p` | the dominating family's records read `carries: identity` with `readable: none` — a treatment that reads no value cannot teach a viewer to read a chart |
| `members_then_total` | 6 | 3 | **66%** `intro-slideshow-full-720p` | the job is *show the members, then their sum*; **0 of 6** bound records are quantitative-capable, so no bound treatment can show the total |

So the problem is **thin supply compounded by one family filling the gap**, not a broad crowding effect.

## Acceptance criteria, verified

### A tag is not treated as native-fit proof — **satisfied by design**

`visualtask_batch_matching.py:420-422` says it outright:

> *"Exact layer counts do not prove that a visual slot accepts a requested media kind, that copy is readable at its required limits, or that typed data has a native encoding. Those treatment-specific claims need reviewed evidence."*

Any required media, text or typed data appends a `conditional` gap and returns `conditional` **before** `native_fit` is reachable. `native_fit` further requires frame-exact timing and available media. `_supports_operation` returns `None` for any record with no structured capability.

**Empirically binding:** Job 3's production run measured `conditional` 40, `incompatible` 1, **zero `native_fit`**. The gate is not merely stated.

This audit therefore credits the behaviour as a designed strength and **proposes no `native_fit` tag** — with the reason recorded under `notProposed`: native fit is a per-task comparison, not a template property.

### Unknown capability remains unknown — **honoured in the data, reported with its limit**

`capability.json` carries an explicit `unclear` list on **442 of 442** records:

- `native_editability` unknown on **all 442**
- `still_only` on 46 — and those same 46 carry `staging: "unknown"`
- `growable: null` on **90**
- five further one-off unknowns named individually, including `existing_description_mismatch`, `clip_boundaries`, `slots_total`

Nothing is rounded up to a claim — not in the data, and not in this audit: HC-2 states that for **98** records the unknown is irreducible, HC-4 **explicitly declines** to quantify hidden capability, and UE-30/UE-31 record what cannot be established.

**But no code reads these markers.** Zero occurrences of `unclear`, `native_editability`, `styleAdaptation` or `unassessed` across `pipeline/`. Unknowns do not become permission today **only because** the conditional gate intercepts first. The protection is *incidental, not designed* — if that gate were relaxed, 442 records of unknown editability would become eligible for `native_fit` with nothing to stop them. Recorded as **UE-28**.

### Broad tags

**Templates:** admission uses no free tags at all, so a broad tag cannot admit an invalid template on the template side.

**Media:** there is a documented, measured collision, and the grammar says so itself —

> *"Matching a tag TOKEN against an entity token makes `cole` reach J. Cole — and also makes `post`, from the content-class tag 'Article Or Post', reach **Post Malone on 48 assets**. The generosity is wanted; the collision is not."*

The mitigation is **wired, not aspirational**: `media_candidates.py:381-394` loads `class-tags.json` and defines `is_class_tag()`; line 869 excludes project and class tags from identity evidence. Residual: 49 `suppressedClaims` as `[assetId, tag]` pairs, including entity-looking tags like `Jay` and `ludacris` — suppressions already applied, so they evidence the collision class rather than an open defect. Media-side tag quality is Job 6's scope.

## Two evidence layers that are never reconciled

| | `capability.json` | `ae-template-technical-index.json` |
| --- | --- | --- |
| Records | 442 templates | 57 projects, 5,806 compositions |
| Derivation | **model-asserted** (`gemini-3.8-flash`) from 396 clips + 46 stills | **source-bound**, with `sourceProjectSha256` per project |
| Native editability | `unclear` on all 442 | the composition data that could answer it |

The bridge — `ae-scene-composition-mappings.json` — holds 398 mappings, **384 of them verified** (`verified` 140, `verified_window` 244), covering **344 of 442** capability records.

So native evidence exists and is largely verified. Yet every capability record still declares native editability unclear, and **no code reads either the unclear marker or the mapping status** when forming the presentation contract. The 98 records with no mapping are genuinely unknown. Recorded as **UE-29**.

## Concept map — Story meaning → presentation contract → template capability

15 rows in the JSON. The load-bearing ones:

| Concept | Story | Contract | Capability | Status |
| --- | --- | --- | --- | --- |
| identity of a subject | `entityRefs[].display` | `entityCount` | `carries: identity` (392/442) | expressible end to end |
| sequence and order | claim order, continuity | `OPERATION_PRIORITY` | `staging` (5 values) | expressible — the best-formed axis |
| a magnitude | `values[].value/unit/basis` | `hasTypedValues` + `quantitativeClaim` **booleans** | `carries: magnitude` (38/442) | **lossy** — Job 3 G-05: the handoff can't carry the figure |
| on-screen text limits | `truncation`, `maxChars`, `wrap` | `needsOnScreenText` | `text_slots` **count only** | **lossy** |
| sum vs named individuals | `one_vs_aggregate` / `one_vs_many_individually` | one label, `comparison` | `carries: aggregate` on **1** of 442 | **missing** |
| evidence kind | `obligation.mediaNeeds` | `evidenceKind` computed | **no field** | **missing at capability** |
| teaches its own encoding | job `explain_the_encoding` | no field | **no field** | **missing** |
| editorial vs factual register | `claim.lane` | **not carried** | no field | **missing in contract** |
| treatment consistency | `continuity.scope/strength` | **not carried** | n/a | **missing in contract** |
| native editability | n/a | n/a | `unclear` on 442/442 | **universally unknown** |

## Unsupported claims and contradictions

**UC-1 — `explain_the_encoding`.** `JOBS.md` asserts it is *"the one nobody builds for"* and that *"no template in the current catalog is described as doing it"* — yet **5 templates are bound to it**. Four are `intro-slideshow-full-720p--scene-010`–`013`, whose capability records carry `identity`/`identity+membership` with `readable: none` or `label+statement`. Four bindings claim a capability the capability records contradict, and the document itself says the capability does not exist. Only `truth-population-field` (`carries: magnitude, difference`, `readable: exact_value`, `structure: axis_plot`) is plausible — and its binding verdict is `null`.

**UC-2 — "natively verified" is overstated.** `JOBS.md` describes binding each job to *"a small set of natively verified treatments"* with *"native verification happening once per treatment."* The records say otherwise: **603 of 624** generated by `claude-sonnet-5` via `pipeline`, only 21 by `user`; verdicts `conditional` **314**, `clear` 289, absent 21; `styleAdaptation.status: unassessed` on **all 624**. The records are honest about themselves — the prose framing them is not.

**UC-3 — incomplete binding metadata.** `enc` empty on **389/624**, `condition` empty on **310/624**, `cap` empty on 26. Because bindings are secondary evidence this admits no invalid template, but the job-keyed layer cannot be read as an explanation of *why* a treatment fits a job.

**UC-4 — the closed set is not closed.** `inversion` is bound and used, and absent from `JOBS.md`.

**UC-5 — declared but unreachable.** `attributed_quote` and `paired_values_by_group` have no bindings.

## Capability families hidden by poor metadata

| ID | Finding | Consequence |
| --- | --- | --- |
| HC-1 | **72 of 442** capability records are bound to no job | the operation path can still admit them, but they are invisible to anyone working from the job vocabulary |
| HC-2 | **98 of 442** have no native composition mapping | for these the unknown is **irreducible** at this baseline, not merely unreconciled |
| HC-3 | **46 of 442** derived from a still only — all with `staging: unknown` | cannot be matched on the one best-formed capability axis |
| HC-4 | 5,806 AE compositions against 442 capability records | **no claim made** about how much capability is hidden — whether the remainder are distinct treatments or scene variants is not determinable from these artifacts (UE-30) |

## Proposed vocabulary

Story-neutral, each tied to something a reviewer could confirm by watching the template render. **Nothing is applied.**

| Field | Layer | Observable test | Closes |
| --- | --- | --- | --- |
| `evidence_surface` | capability | does the template render a surface on which a document, post, caption, lyric or quotation is legible? | MC-1 |
| `carries: aggregate` | capability | does it show a summed quantity distinct from its members? — **no new vocabulary**; the value exists and is used once, so the gap may be coverage rather than expressiveness | MC-2 |
| `teaches_encoding` | capability | does it render an axis label, legend, unit key or worked example before/alongside the data? | MC-3 |
| `item_range` | capability | the smallest and largest item count rendered without redesign — supersedes `growable`, null on 90 | MC-4 |
| `register` | capability | does the surface read as a claim, a question, or a measurement? — **flagged as a hypothesis**, the least observable of the five | MC-5 |

**Deliberately not proposed:** a `native_fit` tag on capability records (it would invite exactly the inference the code is credited for refusing); and merging the job and operation vocabularies (premature — Job 4's UE-23 means the operation vocabulary's own provenance should be established first).

## Unresolved evidence

| ID | Item | Owner | Hand to |
| --- | --- | --- | --- |
| **UE-28** | Unknown markers are read by no code; unknowns stay unknown only because the conditional gate intercepts first | matching | Job 8 |
| **UE-29** | Verified native evidence for 344 of 442 templates is never reflected into the record admission reads | matching | Job 8 |
| UE-30 | 5,806 compositions vs 442 capability records — distinct treatments or scene variants is undeterminable here | matching | Job 6 |
| UE-31 | Binding provenance names a `promptSha` and `runId` but no prompt or transcript is present, so the basis of 289 `clear` verdicts cannot be inspected | matching | Job 7 |
| UE-23 | *(carried)* `OPERATION_PRIORITY` underived — and it orders the **operation** vocabulary, which shares no name with the **job** vocabulary the catalog is bound by, so it cannot be checked against `JOBS.md`'s own data split | matching | Job 8 |

## Acceptance

| Check | Verdict |
| --- | --- |
| A tag is not treated as native-fit proof | **PASS** — verified in code (`:420-430`, `_supports_operation`) and empirically (zero `native_fit` in production); credited as a strength, and no `native_fit` tag proposed, with the reason recorded |
| Unknown capability remains unknown | **PASS** — explicit `unclear` on 442/442 honoured; the audit declines to quantify hidden capability (HC-4) and states where the unknown is irreducible (HC-2); reports that no code enforces it (UE-28) rather than treating data honesty as enforcement |
| Proposed vocabulary story-neutral and maps to observable behavior | **PASS** — 5 additions each with an observable test, none naming a subject/package/beat; one proposes no new vocabulary; the weakest flagged as hypothesis; two tempting ideas explicitly declined |
| No catalog or grammar record is changed | **PASS** — all artifacts opened read-only; only the two Job 5 reports created; Story worktree clean at `d5117a6d` |

Stopping after Job 5.
