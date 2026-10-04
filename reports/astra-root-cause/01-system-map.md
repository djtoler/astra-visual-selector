# Job 1 — System map and evidence integrity

**Audit result: PASS — completed with evidence-integrity findings.**

**Canonical evidence context: FAIL.** The normalized comments and statuses are preserved, but 33 current review records carry context from a different gallery revision. This is an audit finding, not a claim that the matching system is correct or ready for production.

**Next job:** `02-story-semantics.md` — not started. **Blocker owner for completing Job 1:** `none`. Findings requiring later correction belong primarily to `matching`; the manifest path typo belongs to `story`.

## Frozen authority and execution

- Matching: `1276d0ca1daece81b5b7b38c8b5f5280046e5077`, branch `matching-layer`.
- Story: `d5117a6de0fd0c640a336c6f456946ec8b40f319`, read from Git objects into a temporary inspection directory. The separate Story working checkout was not moved.
- Configured model: **gpt-6-astra / medium**. Verified in this task's session `turn_context`, line 58, timestamp `2026-10-04T19:32:04.945Z`. Exact receipt is in the JSON report. No High/Ultra escalation or separate served-model attestation.
- The user approved this baseline and the five pre-review clarifications on 2026-10-04. The saved Job 1 plan defines ordered stages, checks, owner vocabulary and revision alignment.
- No production code, grammar, original review, gallery, gold reference, StoryPackage or renderer was changed. Outputs are audit documents/data from existing files, not visual/template renders.

## What the evidence checks establish

| Check | Result |
|---|---|
| Canonical evidence JSON Schema and existing validator | PASS |
| Normalized observations | 439 distinct IDs, reproduced in memory from preserved sources |
| Source inventory | 24 distinct source artifacts plus 4 byte-identical aliases |
| Source and alias SHA-256 | 28/28 match |
| Source pointer interpretation | 526/527 resolve literally; one documented nonstandard root pointer |
| Current reviews | 12 Jay-Z/Drake + 48 Future, all accounted for once |
| Review-to-original-gallery hash binding | Both current review files match their reviewed galleries |
| Attached normalized context vs reviewed gallery | 27/60 exact; 33/60 differ |
| Gold references | Both SHA-256 digests match; 310 Future and 116 Year Seventeen tasks |
| Gold/current narration alignment | Exact script bytes, claim IDs, claim text and spans agree in both comparisons |
| Authoritative current StoryPackage checker | All three PASS; six typed unknown-speaker gaps remain in Future |
| Existing tests | 35/35 PASS across evidence, workflow, gate and harness suites |
| Frozen harness source receipts | 32/32 hashes match; production remains disallowed |

Authorship stays separate: **333 human**, **74 recovered verbatim human**, **32 derived from human**. The 527 source references are not 527 independent opinions: mirrors and repeated backup observations merge into 439 records. Machine review outputs under `matching-agent-evaluation-20261004` and this audit are system evidence, not human reviews. Source reconstruction verifies faithful export attribution; it does not independently authenticate the original human beyond saved provenance.

## Evidence-integrity findings

### J1-E01 — 33 review contexts come from the wrong gallery revision

All 33 are current Future reviews. The original review file is hash-bound to the **v12** gallery, while the normalized record's context comes from **v13**. Nineteen differ in candidate matching provenance; ten also differ in presentation operations; four also differ in binding provenance.

The source is directly traceable to `pipeline/build_astra_review_evidence.py::candidate_gallery_index` (line 46) and `parse_candidate_review` (line 133): the exporter sorts gallery files, indexes by `(taskId, candidateId)`, and lets a later file replace the context. It does not resolve the gallery using the review's `sourceGallerySha256`. This is a proven evidence-assembly defect; its effect on semantic/matching judgments is reserved for later jobs.

No editor words, statuses or original galleries were changed. All 60 current task/candidate pairs exist in their hash-bound reviewed galleries. The audit sidecar `01-reviewed-context-resolution.json` preserves the exact original task/candidate context for each review and cites its `evidenceId`. Later analysis can use that source-bound context without patching the exporter. The full affected ID list and comparison results are in `01-review-gallery-binding.json` and this report's JSON `/findings/0/evidenceIds`.

### J1-E02 — one nonstandard root pointer

`ev_47909742eab48515` points to `src_fb14e61f76ead873` with JSON pointer `/`. Under literal JSON Pointer semantics, this names an empty-key member, which the source lacks. `parse_carousel` uses it to mean the whole document. The hash-matched carousel review source is available and was read as the document root with this exception disclosed. The canonical package was not repaired.

### J1-E03 — one historical context remains unresolved

`ev_160840d04b878840` preserves a Future @2 comment about candidate `catalog-gap-clean` on `future-volksgeist.proposal.matching-derived-p01-1-05`. It lacks gallery context. Its reference to the preceding beat cannot safely be resolved from the comment alone. This affects one historical observation, not the 60 current reviews.

### J1-S01 — a manifest path typo, resolved without changing the pin

The manifest lists `architecture/storypackage/HANDOFF_data_matching_media.md`. At the Story commit it actually lives at `architecture/HANDOFF_data_matching_media.md`. The alternate was read and hashed. That document describes architectural recommendations and must not be mistaken for implemented current behavior.

## Executable system map

The table summarizes the path. The JSON lists every stage's owner, input contract, implementation symbols/commit, output, validation, bypass risk and downstream consumer. `01-code-symbol-index.json` records actual Python definitions and call sites from 13 central modules.

| Stage | Owner | Actual implementation | Output / consumer |
|---|---|---|---|
| story_creation | story | `architecture/storypackage/tools/build_tagged_script.py::module-level segmentation and package construction`; `architecture/storypackage/tools/build_year_seventeen.py::segment` | future@5, jayz-drake@4, year-seventeen@9 StoryPackage 0.2 files |
| story_validation | story | `architecture/storypackage/tools/check.py::check` | errors and typed gaps; adapter checker receipt |
| story_matching_handoff | story | `architecture/storypackage/tools/build_matching_handoff.py::task`; `architecture/storypackage/tools/check_handoff.py::check_handoff` | year-seventeen.matching-handoff-0.2.json -> reports/storypackage-02-year-seventeen-matching-handoff.json |
| entrypoint_contract_gate | matching | `pipeline/matching_contract_gate.py::enforce_contracts` | hash-bound contractEnforcementReceipt |
| matching_adaptation | matching | `pipeline/storypackage_adapter.py::build` | adapter with source schema/package, preserved story/script/entities/cohorts/beats/claims/jobs/obligations/continuity/timing and checker gaps |
| semantic_splitting | matching | `pipeline/storypackage_splitter.py::build` | taskProposals, speakerRoutes, gaps, routeDisposition, counts |
| requirement_derivation | matching | `pipeline/visualtask_matching.py::presentation_contract`; `pipeline/matching_agent.py::_requirements` | presentationContract and optional 30-data-media-requirements.json |
| catalog_eligibility | matching | `match-trial/candidates.py::load` | template_pool indexed by record ID |
| structured_admission | matching | `pipeline/visualtask_matching.py::template_candidates` | retrieved_unvalidated candidate records and admission evidence |
| ordering | matching | `pipeline/storypackage_candidate_gallery.py::_local_relevance`; `pipeline/retrieval/local_embeddings.swift::IDF-weighted mean NLEmbedding and token vectors` | ordering relevance + family representative slate |
| display | matching | `pipeline/storypackage_candidate_gallery.py::build`; `pipeline/focused_review_queue.py::_signature` | gallery, signature representatives, 8-primary + up-to-8 exploration focused slate |
| human_review | you | `ae-template-automation/scene-library/label-server.py::Labels.save_future_match_review`; `ae-template-automation/scene-library/approved/future-volksgeist-matches.js::saveReview` | candidate-review.json and previous-byte backup |
| review_reconciliation | matching | `pipeline/focused_review_reconciliation.py::build` | focused-review-reconciliation.json |
| evidence_export | matching | `pipeline/build_astra_review_evidence.py::source_candidates` | reports/astra-matching-review-evidence-20261004.json |
| legacy_requirement_derivation | matching | `pipeline/visualtask_requirements.py::build_requirements` | grammar/visual-task-technical-requirements.json |
| legacy_batch_feasibility | matching | `pipeline/visualtask_batch_matching.py::build`; `pipeline/media_candidates.py::load` | full-visualtask-batch-matching-current.json with separate template/media verdicts |
| harness_and_release_boundary | matching | `pipeline/matching_harness.py::build`; `pipeline/matching_agent.py::run_task` | matching-harness-audit.json; agent review route and machine-review receipts |

### The two paths must not be conflated

**General StoryPackage review:** Story validation → adapter → semantic splitter → presentation contract → catalog admission → ordering/family limits → gallery/focused queue → editor review → reconciliation.

`storypackage_candidate_gallery.build` calls `visualtask_matching.template_candidates`. It does **not** call `visualtask_requirements.build_requirements` or `visualtask_batch_matching._candidate_fit`. Its own `fitValidated` is false. General-agent `_requirements` records Data/Media handoff gaps; it does not replace the richer native-fit assessment.

**Legacy feasibility/sequence:** reviewed VisualTasks + technical requirements + Story matching companion + technical comparison/timing/treatment/Data/Media evidence → `visualtask_batch_matching.build` → separate fit/availability verdicts → sequence/review/release receipts → `matching_harness.build`.

The harness reads saved artifacts; it is not an orchestrator that automatically runs all earlier stages. `matching_agent.run_task` calls it using default fixture paths after building the new gallery. The frozen harness mixes cross-story generality receipts with Year Seventeen feasibility/sequence/release evidence. Its 32 source hashes match, but that does not prove the new gallery passed all those stages. This is a boundary observation, not a redesign recommendation.

### Additional code-path risks for later jobs

- The shared gate enforces contract declarations and registered entry points. Review-only gate success does not itself demonstrate per-task semantic quality, completed native checks or production readiness.
- Structured admission has explicit task-request and spatial-route additions, while older tasks without presentation operations use a legacy binding branch. Jobs 4–6 must evaluate these separately.
- Embedding vectors are computed before per-task admission and applied as ordering values to admitted candidates. A receipt's list of logical stages is not alone evidence of physical call order.
- `candidates.diversify` selects a family representative and applies a slideshow cap. The focused review queue selects one task per signature; its diversity view assembles primary/exploration rows. These are distinct reductions.
- The external UI uses `focusedCandidates` in focused mode, whereas the save handler checks membership in ordinary `candidates`. This is an inspected risk, not a reproduced failed save in this audit.
- The UI considers a task completed once any decision record exists, including `unreviewed`. Queue completion is therefore not evidence that all candidates were accepted/rejected.
- The external server and UI are hash-recorded observed files, outside the pinned Matching tree. No browser/native rendering was performed, and no source-gallery read endpoint was invoked because it can initialize review state.

## Gold references and the original mapping question

Both gold files retain their editor-designated positive-target role. Future @2 (310 tasks) aligns exactly in script bytes and claim text/spans to Future @5; Year Seventeen @7 (116 tasks) aligns to @9. Their source-adapter hashes also match. This establishes a safe narration alignment for later quality comparison; it does not claim entity annotations, requirements or proposal quality are identical. Identity/provenance differences still require inspection in later jobs.

The manifest sources, their source declarations, Story's documentary-analysis manifest, analyses 002/006, historical Year Seventeen beat-script map, matching-accuracy files and gold source adapters were examined. Narrative structural analyses exist for the source videos, and the supplied gold task mappings exist. A **separate original-video transcript-span-to-visual-job/shot mapping** was not identified. The narrative analyses contain story beats and retention functions, not a recorded visual treatment for every source span.

No filename is invented. Only if “org” means an additional reference beyond the supplied gold files, the smallest useful input is its existing path or an export containing timestamp/exact transcript span, visual-job label and review provenance. This does not block Job 1 or unrelated later analysis. The historical previous-beat comment remains separately flagged rather than guessed.

## Acceptance and limits

Every required map stage resolves to inspected code or explicit human/editorial work. All 12/48 current reviews are preserved, deduplicated and linked back to their original gallery; both gold sources are verified and classified as positive evidence. Source path/pointer/context exceptions are explicit. Model configuration is verified. Production and original evidence remain frozen.

The audit can therefore PASS while the canonical evidence-context check FAILS. A required audit stage being absent would instead prevent completion; the report-validation receipt tests deletion of each of the six ordered stage receipts. The canonical exporter issue remains a finding for later repair, not permission to change code during Jobs 1–7.

No semantic quality verdict, Story-vs-Matching blame assignment, candidate selection, template rendering or redesign was performed. Existing tests do not substitute for those later jobs. No higher-effort rerun was needed.

See `01-acceptance.json` for final field/order/omission and production-hash checks. The workflow checkpoint is recorded in the JSON report.

**PASS. Next: Job 2 — `02-story-semantics.md`. Blocker owner: `none` for Job 1. Stop here.**
