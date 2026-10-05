# Job 1 — System map and evidence integrity

**Result: PASS** · Next job: `02-story-semantics` (Fable 5.1 via CLI at medium) · Blocker owner: `none`

## Execution receipt

| Field | Value |
| --- | --- |
| Operator | Claude Desktop (`claude_desktop`) |
| Required execution mode | `desktop_conversation` |
| Observed execution mode | `desktop_conversation` — runtime reports session origin `desktop_app`; no CLI subprocess was used for any part of Job 1 |
| Resolved model identifier | `claude-opus-5` |
| User-visible model name | Opus 5 |
| `last_served_model` | `claude-opus-5` |
| `configured_model` | `claude-opus-5` |
| Effort level (observed) | `high` |
| Metadata source | `claude-code-remote` `get_session`: `session_context.model`, `external_metadata.last_served_model`, `configured_model`, `session_context.effort_level` |
| Session | `session_014CbgCFFrmJN4PKxJdBpZ7P` |
| Environment | `anthropic_cloud`, Claude Code CLI 2.1.289 |
| Audit branch head | `d48a5e27abba68348853840c99b46ac72a9364e6` |

Recorded caveats — stated rather than resolved, because `EXECUTION_POLICY.json` does not settle them:

1. The conversation surface is Claude Desktop and the runtime confirms origin `desktop_app`, but execution is backed by an Anthropic cloud container rather than a process on the editor's machine. The policy does not say whether `desktop_conversation` excludes a cloud-backed Desktop session.
2. The policy sets `recordResolvedModel: true` for Job 1 but names no required model, so no model requirement was applied or assumed.
3. The policy specifies no reasoning effort for Job 1. The session's own `high` is recorded as observed runtime metadata, not as a policy selection.

No runtime metadata was invented.

## Independence receipt

The excluded `matching-layer` branch was never fetched or read. `git for-each-ref` lists only `refs/heads/fable_analysis`, `refs/heads/main`, `refs/remotes/origin/HEAD`, `refs/remotes/origin/main`; `git rev-parse --verify origin/matching-layer` fails. No Astra Job 1–8 report and no post-baseline Matching commit was consumed.

One naming collision is worth stating plainly, because the obvious reading of the evidence paths is **inverted**:

> Inside `reports/astra-matching-review-evidence-20261004.json`, the `matching-layer/` path prefix is a **filesystem directory name** of the live repository checkout, not a reference to the excluded `matching-layer` branch. `pipeline/build_astra_review_evidence.py:17-20` sets `ROOT` to the repo root, `POLISH = ROOT.parent`, and renders source labels relative to `POLISH` — so the live repo's own directory name becomes the prefix.

Resolving a `matching-layer/`-prefixed evidence path therefore means reading a file **in this checkout**. All such paths were resolved that way, and nothing authorized or required reading the excluded branch.

## Commit verification

| Layer | Declared | Verified |
| --- | --- | --- |
| Story authority | `djtoler/patterns` `claude/friendly-maxwell-i5brux` @ `d5117a6de0fd0c640a336c6f456946ec8b40f319` | ✅ `git ls-remote` returns exactly that SHA as the branch tip; commit fetched read-only and resolves |
| Matching baseline | `1276d0ca1daece81b5b7b38c8b5f5280046e5077` | ❌ **not verified** — object absent from the depth-1 clone, so descent of `fable_analysis` from the frozen baseline is unconfirmed (UE-01) |

No write operation touched the Story repository.

## Manifest path verification

| Set | Checked | Present | Missing |
| --- | --- | --- | --- |
| Matching layer (contracts, transformation path, grammar, historical evidence) | 44 | 44 | 0 |
| Story layer (contracts, packages, transcripts) @ `d5117a6d` | 27 | 26 | 1 |
| Canonical human evidence trio | 3 | 3 | 0 |
| Gold-standard references | 2 | 2 | 0 |

The single miss is a **manifest defect, not a missing artifact** (AF-06): `REFERENCE_MANIFEST.md` lists `architecture/storypackage/HANDOFF_data_matching_media.md`, which does not exist at the pinned commit. The file is one directory higher, at **`architecture/HANDOFF_data_matching_media.md`**. Use that path for every manifest reference to the Story/Data/Media handoff.

## Perfect reference versions

Both editor-designated files verify completely and are classified as **positive target evidence**, not ordinary generated output.

| File | Declared SHA-256 | Verdict | Package | Proposals |
| --- | --- | --- | --- | --- |
| `…/gold-standard/storypackage-02-year-seventeen-full-task-proposals.json` | `b03d2357…5dc3e1` | ✅ MATCH | `year-seventeen@7` ✅ | 116 ✅ |
| `…/gold-standard/storypackage-02-future-volksgeist-task-proposals.json` | `f48f7ed3…18ebde` | ✅ MATCH | `future-volksgeist@2` ✅ | 310 ✅ |

Three facts about them materially shape later jobs:

- **They are not structurally homogeneous (AF-07).** The Future reference carries top-level `granularityPolicy` and `speakerRoutes`, and per-proposal `presentationOperations`, `semanticDerivation`, `semanticDerived`, `sourceBeats`, `speakerDerived`, `taskText` and `advisoryJobProposalIds`. The Year Seventeen reference carries none of these. They were emitted by different generator schema generations, so any derived principle must name which reference it came from, and a field's absence from the Year Seventeen file must not be read as an editorial choice.
- **One has a live twin, the other does not (AF-09).** `reports/storypackage-02-year-seventeen-full-task-proposals.json` is byte-identical to the Year Seventeen gold copy. No live artifact reproduces the Future gold reference — current Future output is `future-volksgeist@5`, the reference is `@2`. The Future reference is irreplaceable preserved evidence, consistent with the prohibition on regenerating it.
- **The current Future output is a strict structural superset of the gold (AF-08).** Both hold exactly 310 task proposals. Proposal fields in gold but absent from current: **none**. Fields in current but not gold: `primaryPresentationOperation`, `routeDisposition` (plus top-level `contractEnforcementReceipt`).

That last point scopes the rest of the audit: on the Future path the gap to "perfect" is **not** a lost field or a lost proposal. It is content — beats, visual jobs, requirements, matchability. Equal counts across `@2` and `@5` do **not** establish one-to-one correspondence, and none is asserted here (UE-05).

## Evidence package integrity

`reports/astra-matching-review-evidence-20261004.json` — `astra-matching-review-evidence@1`, generated 2026-10-04T17:55Z.

**Schema conformance: conformant.** All 439 records carry every required field. Zero `evidenceId` pattern violations, zero `authorship` enum violations, zero `scope` enum violations, zero records with empty `sourceRefs`. `selectionAuthorized` and `renderingAuthorized` are `false` at package and record level.

**Merge arithmetic fully reconciles.** Source `recordCount` sums to 527 against 439 unique records — a delta of 88. 86 records cite exactly 2 sources and 1 cites 3, contributing 86 + 2 = 88 extra references. The delta is entirely cross-source merging of a single logical decision; no record is lost.

**Hash verification: zero mismatches.** Canonical paths are rendered relative to the parent workspace, so each was re-resolved against this checkout by stripping the `astra-visual-selector/`, `matching-layer/` and `ae-template-automation/` prefixes.

| Outcome | Sources | Notes |
| --- | --- | --- |
| Verified MATCH | 6 | every source reachable here verifies exactly |
| MISMATCH | **0** | — |
| Not present in checkout | 18 | 6 in sibling repo `ae-template-automation` (outside repository scope); 12 in the abandoned mirror `../astra-visual-selector`, absent from this container |

The 18 unreachable sources account for 392 of the 527 raw source records. Records resting solely on them are flagged provenance-unverifiable rather than accepted or rejected (UE-02).

### The abandoned mirror is not double-counted — verified, not assumed

`pipeline/build_astra_review_evidence.py` defines `ABANDONED = POLISH / "astra-visual-selector"` (line 19) and globs the same patterns under both `ROOT` and `ABANDONED` (lines 82-92). Dedup runs in two layers:

1. **Content-identical** files across root and mirror collapse into one source carrying `aliases` — this is the package's `sourceAliases: 4`. Line 353 sorts aliases with `(0 if ROOT in p.parents else 1, label)`, so a live-root file always wins the `canonicalPath` slot.
2. **Content-different** mirror variants stay separate sources, but their records are keyed into `records_by_key`, so one logical decision becomes **one `evidenceId` with multiple `sourceRefs`**, not multiple records.

The mandated accounting, checked per record:

| Package | Required | Found | Live source (hash) | Mirror variant | Shared IDs | **Mirror-only** | Double-counted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `jayz-drake-settle-it@4` | 12 | **12** | `…v13-candidate-review.json` ✅ MATCH | `.backup.json` (11) ✅ MATCH | 11 | **0** | **0** |
| `future-volksgeist@5` | 48 | **48** | `…v12-candidate-review.json` ✅ MATCH | `.backup.json` (47), absent | 47 | **0** | **0** |

Both totals rest on sources that hash-verify in this checkout. Every mirror-variant record resolves to an `evidenceId` the live source already carries, entering as an additional `sourceRef`. The mirror adds no record and inflates no count.

Separately, 3 records belong to the superseded `future-volksgeist@2` revision, all `status: unreviewed`, correctly excluded from the 48. One of them — `ev_e3cdfcea23c5057c` — is the package's only 3-`sourceRef` record: the same decision appears in the mirror's `.backup.json`, `.json` and `.pre-structured-retrieval` variants and merged into **one** record. It is the cleanest single demonstration that mirror variants are not duplicated.

### Machine evaluations are not labeled as editor feedback

Zero of 439 records carry machine authorship: `human` 333, `human_verbatim_recovered` 74, `derived_from_human` 32. `excludedClasses` explicitly bars `model_review_and_evaluation_outputs` with the reason that machine judgments remain diagnostic inputs.

One case deserved real scrutiny rather than a tick. The 49 `matching_output_feedback` records carry `authorship: human`, have no `reviewer` field, and come from `ae-template-automation/scene-library/approved/**evaluation-feedback.json**` via a parser named `evaluation_feedback`. Both the filename and the parser name contain "evaluation", and this is the only evidence stating which offered options the editor judged wrong and which **unoffered** options would have been better — so a mislabel here would corrupt the most diagnostically valuable block in the package.

**The human label is corroborated.** The comment bodies are first-person editorial prose with consistent human orthography and typing errors — *"wouldve"*, *"seperate"*, *"magnatitude"*, *"communicationg"*, *"3is"*, *"wotldve"* — and express preference over options the system never proposed (`ev_021919c932e157f2`: *"scrolling-screen wouldve been a good option for this as well, a great option actually"*). Machine evaluation output does not carry that signature.

**Residual risk:** the source file is in a sibling repository absent from this checkout, so its declared digest could not be verified. Verdict: *corroborated but provenance-unverifiable*.

Also preserved: all 32 `route_decision` records are `derived_from_human`, not verbatim. Any later job citing route evidence must keep that distinction rather than presenting a derived prior choice as direct editor instruction.

**Supports root-cause analysis: yes** — schema-conformant across all 439 records, merge arithmetic reconciled, zero hash mismatches, 12/48 accounted for per record with zero double-counting, no machine evaluation mislabeled; subject to the 18 provenance-unverifiable sources.

## System map

Nine mandated stage groups. Every one resolves to real code or is explicitly human.

| # | Stage | Owner | Kind | Implementation · symbol | Output | Gated |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Story creation | story | code + human authoring | `tools/build_tagged_script.py` | `*.storypackage-0.2.json` ×3 | n/a |
| 2 | Story validation | story | code | `tools/check.py`, `build_matching_handoff.py`, `check_handoff.py` | `year-seventeen.matching-handoff-0.2.json` | n/a |
| 3 | Matching adaptation | matching | code | `storypackage_adapter.py` · `build()` | `…-adapter.json` | ✅ |
| 4 | Semantic splitting | matching | code | `storypackage_splitter.py` · `build()` | `…-task-proposals.json` | ⚠️ partial |
| 5 | Requirement derivation | matching | code, manual, **outside gate** | `visualtask_requirements.py` · `build_requirements()` | `grammar/visual-task-technical-requirements.json` | ❌ |
| 6 | Admission | matching | code | `visualtask_matching.py` · `template_candidates()`; `visualtask_batch_matching.py`; `focused_candidate_diversity.py` | `…-candidate-admissions.json`, `…-focused-candidate-diversity.json` | ✅ |
| 7 | Ordering | matching | code | `ordered_visual_route_plan.py`, `carry_prior_route_choices.py` | `reports/ordered-visual-route-decisions.json` | ✅ |
| 8 | Display | matching | code | `storypackage_candidate_gallery.py`, `focused_review_queue.py` | `…-candidate-gallery.json`, `…-focused-review-queue.json` | ✅ |
| 9 | Human review | **editor** | human + code reconciliation | HUMAN; `focused_review_reconciliation.py`, `prior_review_reconciliation.py`, `build_astra_review_evidence.py` | `…-candidate-review.json`, evidence package | ❌ |

Full input contracts, symbols, validation, bypass risks and downstream consumers per stage are in `01-system-map.json` under `stages[]`, with a crosswalk to the 8 declared harness stages under `harnessStageContractCrosswalk`.

### Architectural findings

**AF-01 — The matching layer is a file-mediated artifact pipeline, not an in-process call graph.** Across all 31 modules in `pipeline/`, the only production import edges among the declared transformation path are each module importing `matching_contract_gate`, plus `visualtask_batch_matching`, `storypackage_candidate_gallery` and `focused_candidate_diversity` importing `visualtask_matching`, and `visualtask_matching` importing `media_candidates`. No module composes the end-to-end run. Each stage is an independently invoked CLI that writes a JSON artifact; the next stage re-reads it from disk. **Stage ordering is an operational convention, not a code-enforced sequence.**

**AF-02 — `matching_harness.build` is a verifier, not an orchestrator.** `pipeline/matching_harness.py:325` reads each stage artifact from disk, recomputes `sha256` against every recorded source, and emits `stageResults` with the first blocked stage (lines 535-558). It calls no other stage's `build()`. A stage never run, or run from stale inputs, surfaces as a gap row rather than being executed.

**AF-03 — The contract gate is cooperative, and eight runnable modules bypass it.** `grammar/matching-entrypoint-contract.json` sets `unknownEntrypointsAllowed: false` and declares 19 entrypoints; **all 19 resolve to a real module and callable** (verified by AST). `matching_contract_gate.enforce_contracts` raises on an unregistered entrypoint (line 206) — but only if the module calls it. 20 modules do; these 8 expose a runnable `main()`/`__main__` and never do:

`build_astra_review_evidence.py` · `entities.py` · `media_candidates.py` · `paths.py` · `post_render_timing.py` · `prior_review_reconciliation.py` · `visualtask_requirements.py` · `visualtask_split_proposals.py`

The closed-world claim is therefore unenforceable. Three are load-bearing: requirement derivation, baseline reconciliation, and — pointedly — **the canonical evidence package this audit relies on is produced outside the entrypoint contract it is used to audit.**

**AF-04 — Requirement derivation is an orphaned, manually triggered producer.** `visualtask_requirements.py` imports no pipeline module and is imported by none. Its only in-repo references are one test and `REFERENCE_MANIFEST.md:81`. It is not a declared entrypoint. Its product, `grammar/visual-task-technical-requirements.json` (158,786 bytes), is read by `matching_harness.py`, `storypackage_data_handoff.py` and `ordered_visual_route_plan.py`. **Derived requirements enter the system as static checked-in grammar data, with nothing in the gated path regenerating them or asserting freshness against the current StoryPackage** — so requirements can silently diverge from the story they were derived from.

**AF-05 — Stage gating contains a non-general hardcoded total.** `matching_harness.py:537` gates `baseline_reconciliation` on `priorSelectionCoverage.total == 107`, a literal integer. A stage in a layer whose mandate is story-neutral passes only when prior-selection coverage equals one corpus-dependent count; any other corpus blocks it regardless of actual completeness. *Observation only — Jobs 1–7 forbid patching production code, and nothing was changed.*

Two further risks worth carrying forward: the harness marks `template_media_feasibility` status `passed` unconditionally while attaching gap rows (lines 541-547), so admission defects surface as non-blocking annotations; and the harness's `human_review` validation requires each decision to name a candidate **within that task's offered `templateChoices`** (lines 526-534) — which structurally cannot capture the reported defect of a valid alternative never being offered, precisely what `ev_021919c932e157f2` records the editor saying.

## Missing references — named precisely, nothing reconstructed

**1. The "org" transcript-to-beat/visual-job reference: NOT PRESENT as a distinct artifact.**

- *Expected name and role:* an explicit transcript-span-to-beat/visual-job mapping for the two source documentaries, expected alongside `analysis_002.json` / `analysis_006.json` — a crosswalk letting the audit **verify** rather than infer how source structure became beats, claims and visual obligations.
- *Search performed:* all 27 Story-layer manifest paths probed individually at `d5117a6d`; `git ls-tree -r` over the full commit filtered for handoff/handover/mapping names; all 6 declared transcript and analysis paths confirmed present; all 44 matching-layer paths probed.
- *What is present:* both full transcripts (16,126 / 50,808 bytes), both analyses (47,504 / 60,289 bytes), `pattern_library.json` (37,852), `playbook.md` (7,847), `youtube_doc_analysis/HANDOFF.md`, and the finished StoryPackages — source structure at one end, authored beats at the other.
- *Exact decisions not verifiable without it:* whether a given beat boundary derives from a specific transcript span or was authored independently; which source pattern authorized a given visual obligation; and whether the perfect references' beat boundaries trace to source structure or to editorial judgment applied afterward — which decides whether their quality is a **reproducible derivation** or a **human act**.
- *Why present artifacts are insufficient:* `pattern_library.json` and `playbook.md` generalize *across* documentaries; the analyses describe each source's own structure. Neither carries a per-span linkage to any beat ID, so the derivation is observable only at its endpoints, never as a traceable step.
- *Smallest sufficient supply:* one export, for one documentary, mapping transcript span (or timecode range) → beat ID → visual job. A single file for `future-volksgeist@2` would anchor the derivation.
- *Analysis continues without it.* Only the provenance questions above are blocked; later jobs can still evaluate beat quality against the perfect references — they just cannot attribute that quality to a derivation step.

**2. The stage contract's own cited authority: REFERENCED BUT ABSENT.** `grammar/matching-harness-stage-contract.json` names `../content-project-mgr/final_documentary_system_plan.md` (`masterPlan`) and `../content-project-mgr/HANDOFF_data_matching_media.md` (`layerHandoff`) as its authority. Neither exists; `content-project-mgr` is a sibling workspace repository outside this audit's scope. A same-named file exists in the Story repo at `architecture/HANDOFF_data_matching_media.md` (AF-06), but cannot be assumed identical. Consequently, whether the 8 stages, owners and `requires`/`produces` sets faithfully reflect the master plan they claim as authority is **unverifiable**. Smallest sufficient supply: those two files, or confirmation that the Story-repo file is the authoritative layer handoff.

## Unresolved evidence carried forward

| ID | Item | Resolution path |
| --- | --- | --- |
| UE-01 | Descent of `fable_analysis` from baseline `1276d0ca` unverified (object absent from shallow clone) | bounded `--depth=1000` fetch, then `merge-base --is-ancestor` |
| UE-02 | 18 of 24 evidence sources unreachable (392 of 527 raw records); declared hashes unverifiable — notably the 49 `matching_output_feedback` records | editor supplies `ae-template-automation/scene-library/approved/` files, or confirms out of scope |
| UE-03 | Only `year-seventeen` has a committed matching-handoff artifact, yet `future-volksgeist` and `jayz-drake-settle-it` both have current Matching output | Job 3 |
| UE-04 | Perfect references are structurally heterogeneous (AF-07); one has a live twin, one does not (AF-09) | Jobs 4 & 7 must attribute each principle to a specific reference |
| UE-05 | Future gold is `@2`, current is `@5`, both exactly 310 proposals; one-to-one correspondence not established | Job 4 |
| UE-06 | Policy does not state whether `desktop_conversation` admits a cloud-backed Desktop session | editor clarification if material |
| UE-07 | `candidateReviewsWithoutGalleryContext: 1` — one editor review whose gallery context could not be reconstructed | Job 7 |

## Acceptance

| Check | Verdict |
| --- | --- |
| Every stage resolves to actual code or is explicitly human/manual | **PASS** — 9 mandated groups and 8 harness stages mapped to files and symbols; 19/19 declared entrypoints resolve; stages 1 and 9 marked human-involved |
| All 12 Jay-Z/Drake and 48 Future reviews accounted for, abandoned mirror not treated as duplicate | **PASS** — both totals on hash-verified live sources; 0 mirror-only records, 0 double-counted; dedup proven from source |
| Machine evaluations not labeled as editor feedback | **PASS** — 0/439 machine authorship; the one risk case scrutinized and corroborated, residual risk recorded |
| Any missing org reference precisely named | **PASS** — two absent references named with role, search, unverifiable decisions, insufficiency and smallest sufficient supply; nothing reconstructed from memory |
| Both perfect references match manifest hashes, classified as positive target evidence | **PASS** — both SHA-256 match; packages and counts (116, 310) confirmed; `evidenceClass: positive_target_evidence` |
| Execution receipt reports Claude Desktop plus exact model identifier | **PASS** — `claude_desktop` / `desktop_conversation` / `claude-opus-5` (Opus 5), source named, 3 caveats recorded |
| No production file modified | **PASS** — only the two Job 1 outputs created; Story repository read-only |

Semantic quality was not judged and no redesign was proposed, per Job 1 scope.

## Next job

`02-story-semantics` — **requires Fable 5.1 via Desktop-managed CLI at explicit medium effort**, not a direct Desktop job.

Feasibility is confirmed in advance: Claude CLI 2.1.289 supports `--model` and `--effort`, and a pre-flight `claude -p --model claude-fable-5-1 --effort medium` returned `claude-fable-5-1 (Claude Fable 5.1), effort level: medium.` — confirming Medium is selected explicitly rather than defaulting to High as Fable does in Claude Code.

**Stopping after Job 1**, per the execution contract.
