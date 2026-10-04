# Job 6 — Candidate pipeline audit

**PASS — audit complete.** Candidates disappear at several distinct boundaries: wrong primary contract, missing capability/scope handling, one-representative-per-family grouping, relevance ordering, and display caps. The strongest new defect is that focused review drops routing information and offers templates for tasks explicitly marked template-ineligible. No code was changed.

Matching production: `1276d0ca1daece81b5b7b38c8b5f5280046e5077`; Story: `d5117a6de0fd0c640a336c6f456946ec8b40f319`. Stop after Job 6.

## Evidence and reconstruction boundary

The audit covers all **60 current editor-review records, representing 59 distinct tasks**, bound to the exact Future v12 and Jay-Z v13 galleries by the Job 1 context sidecar. One Future task has two review records. Every review record includes its full historical displayed rows and editor response, plus a fresh replay with **442 catalog rows**, rejection reasons, family order, within-family order, display outcome and native-fit status: **26,520 candidate-lineage rows**.

[Complete lineages](06-candidate-lineages.json) · [Controlled probes](06-pipeline-probes.json) · [Machine-readable report](06-candidate-pipeline.json) · [Acceptance receipt](06-acceptance.json)

Historical intermediate states are **not recoverable exactly**: gallery manifests omit effective catalog snapshots and raw relevance scores. None of the historical ordered slates equals the fresh replay; five candidate sets match when order is ignored. We do not attribute every historical omission to a freshly observed gate. Complete fresh lineage and preserved historical displays are separate evidence, with the missing historical steps explicitly classified as a provenance gap.

The existing local macOS embedding workflow was used with the complete original proposal-query batches (310 Future; 186 Jay-Z), not a sampled subset. Source files match gallery digests after rebasing old workspace paths. Model scores influence order only. No paid model call or native render ran.

## Seven distinct boundaries

| Boundary | Actual behavior and audit conclusion |
|---|---|
| Eligibility/scope | Existing loader applies card eligibility, explicit overrides, removals and supersessions. All scopes load through `*`; operation scope filtering happens later. Raw source exclusions and effective families are recorded. |
| Capability admission | Only primary operation admits structured candidates; secondary operations are not unioned. Explicit task admissions and the 20+ spatial route are separate additions. Missing metadata and invalid primary contracts cannot be repaired by relevance. |
| Feasibility | Gallery does not evaluate it. Batch fit runs after exhaustive **family** retrieval, which already suppresses siblings. Conditional/unresolved remain distinct from native fit. |
| B-roll/no template | Early template-ineligible return works in the matcher, and source clips retain zero-template routes. Focused reconstruction omits that route; empty-output labels conflate intended no-template with missing discovery. |
| Family diversity | One representative per suffix-derived family. No within-slate duplicates observed; sibling variants are lost in final serialization. |
| Relevance | Existing IDF-weighted word embeddings order admitted records. Family order uses best member relevance; generic capacity/encoding ranking hooks exist, but current structured rows do not supply task-specific fit values. |
| Display/focused review | Gallery limits to 16 representatives with a six-slide-style cap. Focused view combines eight historical primaries with eight least-exposed reconstructed families. Neither is complete native feasibility. |

## Findings

### C06-01 — Focused review resurrects template-ineligible routes

**Classification:** `contract_gap`, `forced_template`.

The actual focused_candidate_diversity.build reconstructs tasks without routeDisposition. On all 12 route-ineligible tasks in the Jay-Z v13 gallery, it retrieves 22 template families and constructs exploration alternatives, despite the original gallery having no template candidates. A separate current T28 diagnostic returns zero when its route is preserved and 22 when omitted. forced_template here means forced template suggestions in review, not an executed selection or render.

Source: `pipeline/focused_candidate_diversity.py:build; pipeline/visualtask_matching.py:template_candidates`.

### C06-02 — Display caps discard admitted families before task-specific fit

**Classification:** `display_loss`, `ordering_loss`.

Across 60 review records, fresh replay contains 8,101 admitted record occurrences: 913 displayed, 5,788 suppressed within family, 232 family representatives deferred by the slideshow cap and 1,168 later representatives beyond the display limit. Counts include one twice-reviewed task. Removing only the slideshow cap changes 38 slates; removing relevance changes all 60 ordered displays. These are candidate losses, not proof that every omitted row is valid. The gallery evaluates no native feasibility or complete relationship reconciliation before limiting choices.

Source: `pipeline/visualtask_matching.py:template_candidates; match-trial/candidates.py:diversify`.

### C06-03 — Exhaustive family retrieval still discards variants before fit

**Classification:** `variant_loss`, `feasibility_unknown`.

FAM_MAX=1 chooses one row per inferred family even in exhaustive_families mode. C.diversify retains _siblings internally, but template_candidates serializes no sibling list. The batch matcher calls exhaustive_families=True and then assesses only those representatives. An incompatible representative therefore cannot establish that its unexamined siblings are incompatible; family exhaustion is not established. The observed 5,788 suppressed variants are not all defects, but their disposition must remain untested.

Source: `match-trial/candidates.py:diversify; pipeline/visualtask_matching.py:template_candidates; pipeline/visualtask_batch_matching.py:_template_result`.

### C06-04 — Timeline and spatial losses occur before relevance can help

**Classification:** `admission_error`, `metadata_gap`.

Both timeline scenes are eligible catalog records but fail scope compatibility in general operation admission. Four calibrated spatial records lack capability; ordinary admission rejects them, while the separate 20+ identity route can append spatial candidates. Relevance cannot recover an unadmitted row: setting an absent-capability spatial record to diagnostic relevance 1e9 still does not admit it for the tested sub-20 task. Historical editor expectations identify the question to test, not a global permission to admit.

Source: `pipeline/visualtask_matching.py:_supports_operation,template_candidates`. Editor evidence: `ev_de698031ae7624db`, `ev_ae89ed37733a21e4`.

### C06-05 — Wrong primary requirements explain some weak pools

**Classification:** `contract_gap`.

The exact reviewed Future lyric task uses evidence_presentation, excluding all seven lyric-scoped records; the reviewed tracklist task uses item_sequence, permitting many identity sequences. The reviewed event/slideshow task uses data_explanation, producing 133 rows before display. These are upstream operation/contract issues identified in prior jobs and now located before ordering. For Jay-Z side-by-side expectations, the recorded task is data_explanation: base-single-billboard is displayed in this replay, while a qualitative two-person spatial record is not admitted. A hypothetical comparison probe must not be substituted for that actual task.

Source: `reviewed source proposals; pipeline/visualtask_matching.py:_presentation_candidates`. Editor evidence: `ev_6c440a7b5cb840d4`, `ev_063fd655708a1b49`, `ev_2ab63ad9958fa8b2`, `ev_ae89ed37733a21e4`.

### C06-06 — Gallery discovery and native fit are separate, with a late fit boundary

**Classification:** `feasibility_unknown`.

All gallery rows are retrieved_unvalidated and fitValidated=false. The batch _candidate_fit uses native comparisons/timing/treatments, but missing exact mapping with capability can yield conditional and defer child checks. Direct probes return unresolved for the capability-free red-stage record and conditional for intro scene-012 with no exact comparison. No native fit is established by these probes. This honest uncertainty is not a reason to declare the catalog exhausted or build a custom substitute.

Source: `pipeline/storypackage_candidate_gallery.py:build; pipeline/visualtask_batch_matching.py:_candidate_fit`.

### C06-07 — Focused signatures compress meaning beyond their evidence

**Classification:** `sampling_gap`.

The queue groups on primary operation, job, a coarse entity bucket, presence of values/cohort/constraints/text and whether any candidates exist. It omits evidence kind, exact relationship, secondary requirements, explicit route and actual candidate families. A controlled 3-versus-93 identity and footage-versus-document change leaves its signature unchanged. Fresh queue construction yields 45 representatives for 310 Future tasks and 33 for 186 Jay-Z tasks. This is coverage of those coarse signatures only; the full gallery is preserved, so it is not global deletion of unreviewed tasks.

Source: `pipeline/focused_review_queue.py:_signature,build`.

### C06-08 — Focused exploration uses a different ordering context

**Classification:** `ordering_loss`.

Focused diversity preserves the first eight historical shown rows, then selects up to eight least-exposed admitted families. It reconstructs without candidateRelevance and templateAdmissions as well as routeDisposition. Thus it does not simply extend the same gallery ranking or preserve task-scoped explicit requests. Frequency depends on the supplied queue order. Missing task-scoped admissions is a code-path risk; no reviewed trace in this sample supplied such an admission.

Source: `pipeline/focused_candidate_diversity.py:build`.

### C06-09 — Exact historical intermediate lineage is not recoverable from saved galleries

**Classification:** `provenance_gap`.

The two reviewed galleries hash their proposals, adapters and bindings, but do not pin the effective template pool or persist relevance floats, rejected rows or pre-display ordering. Fresh local embeddings use all original package queries because IDF depends on the query batch. None of the 60 historical ordered slates matches the fresh ordered replay exactly; five sets match irrespective of order. The cause of each difference cannot be isolated to model/environment, historical code or catalog drift from those receipts. This audit provides complete fresh lineage and exact historical displayed rows/editor responses, and explicitly leaves unknown historical intermediate states unknown.

Source: `pipeline/storypackage_candidate_gallery.py:build,_local_relevance; pipeline/retrieval/local_embeddings.swift`.

### C06-10 — Family flooding and historical-pick leakage were not observed in these slates

**Classification:** `no_failure_observed`.

All 60 fresh slates have at most one candidate per inferred family. The gallery explicitly sets ignorePriorSelections=True, so C.diversify does not use global picks. Structured admission does not union legacy bindings, and historical comments in this audit never modify task admission. Repetition of broad families across different tasks remains possible when their contracts match; it is not duplicate-family flooding inside one slate.

Source: `pipeline/storypackage_candidate_gallery.py:build; pipeline/visualtask_matching.py:template_candidates; match-trial/candidates.py:diversify`.

### C06-11 — No-template is valid, but routing and explanatory labels need consistency

**Classification:** `route_policy_gap`.

templateEligible=false returns [] before explicit admissions or spatial additions. Source-clip routes explicitly request original footage with zero templates; the splitter declares b-roll fallback available. Gallery output calls every empty set no_bound_template_candidates, including intentional template-ineligible routes. The batch adds an existing_template_candidate missing gap on every empty retrieval. That wording conflates intentional no-template with failed discovery. No selection or rendering occurs, and availability of suitable b-roll is not proven by the fallback flag.

Source: `pipeline/storypackage_candidate_gallery.py:build; pipeline/visualtask_batch_matching.py:_template_result; pipeline/storypackage_splitter.py:task_from_claims`.

## Expected families, traced without assuming fit

| Editor expectation | What the fresh replay shows |
|---|---|
| Portrait/documentary intro — ev_5b014d59e8746769 | Exact intro scene-012 is present and displayed. Its preferred 2–3-card adjustment remains unverified; this is not catalog absence. |
| Comparison — ev_ae89ed37733a21e4 | Actual primary is data_explanation. Base-single-billboard is displayed; red-stage lacks capability and is not admitted. Hypothetical comparison results from Job 5 are not substituted for this real task. |
| Timeline — ev_de698031ae7624db | Both search-bar timeline scenes fail scope before ordering. Carousel records span nonadmission, sibling suppression, display cap and displayed outcomes. |
| Screen/document — ev_063fd655708a1b49 | Actual primary is item_sequence. screen-mockup review-001 and scrolling-screen review-005 display, alongside other sequence families. Their presence does not establish tracklist readability. |
| Event slideshow — ev_2ab63ad9958fa8b2 | Actual primary is data_explanation. Two history-slideshow rows display, but 215 slideshow-named records are not admitted. This is a wrong-demand question before a diversity question. |
| Interview/evidence — ev_032190ddc33477c4 | Evidence primary admits seven families; screen-mockup and documentary families appear. Combining speaker and source footage still requires a treatment check. |
| Lyrics — ev_6c440a7b5cb840d4 | Reviewed primary is evidence_presentation; all seven lyrics records fail scope. Current regenerated inference is separate from this historical reviewed input. |
| Item carousel — ev_2794546a910cc39b | Four carousel records display; other records are unadmitted, suppressed siblings or slide-cap omissions. A claim that the family is missing would be false. |

Every row above links to the full per-record outcomes in the JSON. Name/description family searches are discovery aids, not evidence that every returned scene is an eligible treatment. No old editor choice was used to admit or rank a new-story record.

## Validation and implications

33 existing tests passed across visual-task matching, batch fit, focused queue and review reconciliation. Existing resource warnings occurred without failures. Audit checks additionally replay saved inputs/scores, verify source hashes, account for every eligible record, reject missing/reordered audit stages and verify unchanged production code, grammar and catalog.

The separate cap probes preserve the same task and scores: one removes only the slideshow cap, one removes only the overall display limit; exhaustive mode is recorded separately because it changes both. The actual focused consumer was also tested on all 12 route-ineligible Jay-Z tasks with only source paths rebased. These results do not certify a new renderer or approve any selection.

Proposed next design questions are to preserve one task contract across consumers, reconcile required meaning and candidate-specific treatment before truncation, expose materially different sibling variants, and persist enough intermediate evidence to explain future losses. These remain proposals for the later integrated audit, not changes made here. No-template can be the correct outcome; missing media, unknown native fit and deliberate routing must remain distinct.

**Next job: `07-human-evidence-and-reference-evaluation.md`. Blocker owner: `none`. Job 7 has not started.**
