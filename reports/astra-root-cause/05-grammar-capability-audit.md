# Job 5 — Grammar and template-capability audit

**PASS: Job 5 audit complete.** The architecture has useful separations between Story intent, retrieval metadata and native evidence, but the vocabulary and its consumers do not yet expose all intended alternatives consistently. Several editor-expected families exist and are hidden or mischaracterized; catalog absence is not the general explanation. This is an audit result, not product acceptance.

Production baseline: `1276d0ca1daece81b5b7b38c8b5f5280046e5077`. Story baseline: `d5117a6de0fd0c640a336c6f456946ec8b40f319`. No runtime, grammar, catalog or schema was changed. No native project was modified or rendered.

## Catalog authority and coverage

The existing `C.load(content_class="*")` loaded **442 unique records across 102 inferred families**, using Matching’s local approved-list export plus the existing sidecars and optional enrichment. Source hashes and effective records are preserved in [05-catalog-evidence.json](05-catalog-evidence.json). The raw capability file also has 442 entries, but 11 are outside the effective pool and 11 effective records have no capability; matching counts must not be mistaken for complete coverage. The removed entries comprise three retired 3Dz scenes and eight disallowed text-carousel scenes. Local pending inventory is empty.

Optional description-inventory.json and approved/catalog.json enrichment files were missing in this environment; the loader recorded those absences and used the approved export and sidecars. Therefore missing optional enrichment is not proof that no richer source exists elsewhere.

Descriptions come from the approved export for 425 records and local registrations for 17; there were no title-fallback records in this load. This measures availability of prose, not its accuracy. Seven lyric records use scoped retrieval without measured capability. Four explicitly admitted spatial records have no capability and are invisible to ordinary operation admission.

**Provenance correction:** Job 4’s catalog receipt named the neighboring AE export, although the invoked loader used the local Matching export. They have different hashes. G05-11 identifies the correction; the full actual source is now pinned.

## Findings

### G05-01 — Timeline scope removes an existing family

Both search-bar timeline scenes are in the 442-record pool, with measured sequence/chronology metadata. Every operation returns None solely because scope=timelines is not handled. Clearing only scope in an in-memory diagnostic admits archival_progression; this is a causal probe, not a proposed scope removal. Explicit task admissions remain a separate bypass for reviewed requests; general exposure is broken.

Source: `match-trial/candidates.py:SCOPED; pipeline/visualtask_matching.py:_supports_operation`. Scoped editor evidence: `ev_65fa5e81c76d4c01`, `ev_de698031ae7624db`.

### G05-02 — Approved qualitative spatial layouts have no capability record

catalog-gap-clean, topographic-cloud, hologram-stage and kendrick-red-stage-clean load through eligibility overrides but capability=None. Generic operation predicates reject them. The 20+ identity spatial route or explicit task admissions can still expose them, so they are not universally absent. A two-person comparison cannot rely on the 20+ route. The corrected red-stage description explicitly permits numeric text without treating portrait position/size as magnitude.

Source: `grammar/eligibility-overrides.json; grammar/local-templates.json:profileCorrections; pipeline/visualtask_matching.py:template_candidates`. Scoped editor evidence: `ev_ae89ed37733a21e4`, `ev_c0014381cd5b341b`.

### G05-03 — Demo text and variant metadata can hide editor-expected treatments

The accepted dropoff review-002 is identity/sequence but readable includes exact_value, so relationship_intro rejects it. Its current record does not prove whether those numeric labels are removable. base-single-billboard has corrected axes of 3 heroes/10 entities, but its demo capability says nested, magnitude and 5 media slots; comparison rejects it even though readable includes difference. The editor expected double/triple hero versions. Native variant compatibility remains pending; this is a metadata/consumer mismatch, not permission to assert the variants fit.

Source: `grammar/local-templates.json:capacityOverrides; grammar/capability.json; pipeline/visualtask_matching.py:_supports_operation`. Scoped editor evidence: `ev_0125568cf745b6da`, `ev_ae89ed37733a21e4`.

### G05-04 — Relationships and data operations remain too broad for fit

150 records pass relationship_intro for both the two-person contract and a diagnostic 19-person simultaneous labeled relationship with explicit negative constraints. The operation predicate does not read those changed demands. data_explanation admits 133 records under a non-typed probe contract from any recognized data carry or exact-value readability. These are retrieval sets, not 150 or 133 valid choices. Relationship edges, denominator, rate, scale and measurement method still need reconciliation.

Source: `pipeline/visualtask_matching.py:presentation_contract,_supports_operation`. Scoped editor evidence: `ev_5b014d59e8746769`, `ev_197e8df3cdb679e1`.

### G05-05 — Document capability depends on descriptive wording

The evidence predicate has no dedicated document/screen capability field. screen-mockup-rfx--review-001 is admitted with evidence_descriptor:article; clearing only its title/description/useWhen/asserts removes admission while structure/counts/readable fields remain unchanged. This proves dependence on prose, not an invalid template. Conversely, mentioning a screen does not certify document legibility.

Source: `pipeline/visualtask_matching.py:_operation_text,_supports_operation`. Scoped editor evidence: `ev_063fd655708a1b49`.

### G05-06 — Reduction is documented but staging contradicts it

two-floors and truth-cohort-attrition retain staging=all_at_once while asserts describe isolating selected points or dropping members. Sidecar correction notes explicitly identify the missing elimination vocabulary and avoid substituting another wrong term. This is a known unresolved representation gap, not a new inferred native behavior.

Source: `grammar/local-templates.json:capabilityCorrections; grammar/capability.json`. Scoped editor evidence: `ev_5b0549ebba618177`.

### G05-07 — Legacy vocabulary and bindings drift apart

JOBS.md lists 21 jobs including attributed_quote; bindings has 20 keys, no attributed_quote and an additional inversion. JOBS.md says nobody builds explain_the_encoding, while 5 bindings exist. Neither those bindings nor their model verdicts prove native instructional capability. SCOPE.md lists one timeline scene, but two replacement local scenes load. Seven legacy references across jobs still name the three deliberately retired 3Dz scenes; the effective loader correctly removes them.

Source: `grammar/JOBS.md; grammar/SCOPE.md; grammar/bindings.json; grammar/local-templates.json:remove`.

### G05-08 — Native evidence exists but does not close fit

The technical index covers 57 projects, 5,806 compositions and 4,089 text fields. Among 382 effective AE records, 105 have verified mappings, 222 verified_window, 14 unreviewed and 41 no mapping. All 431 loaded records with capability include native_editability in unclear; seven lyrics and four calibrated spatials lack capability altogether. Mapping status locates compositions; it does not certify a task-specific render. Legacy technical/media requirements explicitly remain review_only_not_connected. No new native test ran.

Source: `grammar/ae-template-technical-index.json; grammar/ae-scene-composition-mappings.json; grammar/visual-task-technical-requirements.json`.

### G05-09 — Family cap prevents simple variant flooding but can hide treatment variants

442 records group into 102 inferred families. Largest families have 56, 38 and 19 scenes. A 150-row relationship probe spans 21 families; default diagnostic display shows 16 rows from 16 families, exhaustive diversity returns 21. Thus no duplicate-family crowding occurred in this probe. C.diversify attaches siblings, but template_candidates serializes no sibling field. One family representative can hide a materially different native treatment. The existing focused_candidate_diversity report separates hidden admitted families from unadmitted families, but remains review_only_not_connected and does not certify fit. Family identity is suffix-derived; no template ID split across multiple inferred families was observed. Full ranking/reconciliation sequence is Job 6.

Source: `match-trial/candidates.py:_family,diversify; pipeline/visualtask_matching.py:template_candidates`.

### G05-10 — Adjustment evidence is distributed and not a universal authorization

growable describes observed capability; capacityOverrides and capabilityCorrections record specific user rulings; bindings styleAdaptation can remain unassessed; technical mappings identify native sources. These must not be collapsed into arbitrary recutting. Intro scene-012 documents six media slots; the editor preferred a 2–3-card treatment while allowing supporting media. That preference does not prove an editable 2–3-card version exists.

Source: `grammar/local-templates.json; grammar/bindings.json; grammar/ae-scene-composition-mappings.json`. Scoped editor evidence: `ev_5b014d59e8746769`.

### G05-11 — Job 4 catalog-source receipt needs correction

Job 4 diagnostics invoked C.load without catalog overrides, which selects astra-selector-design/approved_media/approved-list.json (SHA 96a699ae623ad00e19680e58256734bb6519fa1cc087d310d39f03cf8d4a843e). Its catalogInputs instead named the neighboring AE export (SHA c278d5ec7715b3bfbc8a9589edb3358a74048bb508019a23bc24ed885d6d69d8). Those bytes differ. This report records the actually loaded source; prior operation counts remain observations of the local export. Earlier reports are preserved with this explicit correction.

Source: `reports/astra-root-cause/04-diagnostic-probes.json; match-trial/candidates.py:approved_path`.

## Normalized concept map

These are proposed reusable requirements, not approved schema changes. Every proposal names observable behavior; unmeasured behavior stays unresolved.

| Concept | Story meaning → current contract | Template capability | Gap / observable requirement |
|---|---|---|---|
| relationship | Story typed relationships and participant roles → relationship_intro; entityCount only, no typed edge consumed | identity + pair/list/grid/sequence/grouped_clusters; capacity >=2 | Partial: kinship, collaboration and causal edges collapse to co-presence. Proposed observable requirement: endpoints and edge meaning perceptible together or in an explicit reveal. |
| reading demand | Quoted words, source attribution, required labels and phrase timing → needsOnScreenText, mustBePerceptible, wouldBeALie | readable categories and text_slots | Partial: counts are not exact strings, line capacity, dwell or attribution. Those demand fields do not constrain _supports_operation. Require measurable field assignment and timed reading review. |
| evidence kind | Document/screen versus source footage, speaker/source → evidenceKind inferred from narration words | Evidence admission matches descriptor words plus readable/text slots | Missing dedicated evidence-role capability: document region, legible source, attribution, footage/speaker coexistence. Existing descriptions are discovery evidence only. |
| ordered sequence | Ordered works, milestones, temporal direction → item_sequence / archival_progression | structure, staging, chronology; slots_total | Partial: order labels and distinct identities do not prove chronology, duration, exact sequence or reusable native length. Preserve explicit order and verify supported timing controls. |
| identity cardinality | Distinct people, works, anonymous cohort members and repeated appearances → entityCount and hasCohort | media_slots, slots_at_once, slots_total, corrected axes | Partial: entity count is not media-slot demand. Separate simultaneous identity demand, total items and hero/support roles; validate treatment mapping. |
| cohort structure | Membership, subset, benchmark, intersection, population → hasCohort boolean | membership/overlap/aggregate/absence carries | Partial: nested groups, denominators and survivor sets are not represented by the boolean. Observable encoding must preserve set membership and the reference population. |
| quantitative relation | Share, rate, aggregate, difference, rank, magnitude and derivation → hasTypedValues, quantitativeClaim; data_explanation / comparison | carries and readable; broad union of data carries | Missing relation-specific reconciliation: a rank or exact-value display is not automatically a proportion, derivation or explanation of scale. Require verified data-to-mark mappings. |
| elimination | Population reduces to survivors; absence differs from zero → No distinct reduction requirement in presentation contract | absence/overlap corrections, but all_at_once staging remains | Missing staging vocabulary. Proposed reduces_to_subset means visible membership removal with survivors retained; require beginning/end membership and transition evidence. |
| layout roles and variants | Primary subjects versus supporting works; two-person qualitative comparison → comparison/relationship_intro | Demo capability + independent capacity overrides | Contradiction: hero axes say 3 heroes/10 entities, demo fields still say 4 simultaneous/6 total/5 media; predicate reads demo fields. Supported variant capability needs explicit provenance and native mapping. |
| scope | Explicit editorial content-class restriction → Only lyric scope special-cased by _supports_operation | lyrics and timelines scopes | Timeline class has no accepted operation path. Preserve restriction and implement matching content-class compatibility in a later authorized job; never erase the restriction. |
| permitted adjustments | Approved timing/text/color or scoped post work → No adjustment plan argument in operation predicate | growable, sidecar corrections, native mappings, binding styleAdaptation | Partial/distributed: demo observation, declared supported range and approved adjustment are different evidence. Require candidate-specific existing-control plan and verify it; do not infer recutting permission from comments. |
| style and sample content | Universal communication job independent of sample subject → Operations are story-neutral in intent | asserts/description, implies, readable; profileCorrections | Prose/sample numeric text can suppress qualitative use. Proposed distinction: optional label content versus unavoidable visual quantitative encoding, validated against existing controls. |

## Legacy jobs versus presentation operations

The original jobs preserve useful relational distinctions: `one_vs_aggregate`, `entity_vs_benchmark`, `proportion_of_cohort`, `intersection_of_sets`, `derived_quantity` and `explain_the_encoding` are not interchangeable. Current `data_explanation` retrieves by a much broader union. `enumerate` maps roughly to item_sequence; `narrate_an_event` to event_narration; `pose_a_question` to rhetorical_question; assert/define work often reaches concept_statement. These are analytical correspondences, not lossless conversion rules. Attributed quotation adds speaker/source/readability duties that no single current operation fully establishes. Relationship, lyrics and transformation operations add useful cross-story expressiveness beyond the original niche vocabulary.

Structured tasks use operation predicates; legacy bindings only enrich provenance for already-admitted records. Tasks without presentation operations retain the legacy replay route. Thus repairing only JOBS.md or bindings cannot repair current admission. The claim of a closed niche job set is historical rationale, not proof of general cross-story coverage.

`class-tags.json` serves a different purpose: media lifecycle/content tags are excluded from identity matching to prevent collisions such as “Article Or Post” with a person’s name. It is not the template-capability taxonomy. `library-snapshot.json` is historical media inventory, not native-template evidence; this audit does not infer current media availability or rights from it.

## Editor-expected alternatives: present versus verified

| Expected treatment | Inventory result | What remains unresolved |
|---|---|---|
| Lyrics (ev_6c440a7b5cb840d4) | 7 records in 2 scoped families; all admitted by lyric scope | Capability/native editing/readability absent from those records |
| Search-bar timeline (ev_65fa5e81c76d4c01; ev_de698031ae7624db) | 2 local timeline scenes, 8 and 6 total slots | Scope prevents general admission; exact task timing and native fit not certified |
| Long carousel (ev_81a8bfc05956e7b1) | 9 carousel-named records declare 12–22 total slots, across several families | Nineteen years is not automatically nineteen slots; verify item/time demand, order and native variant |
| Tracklist/document (ev_063fd655708a1b49) | 55 name/description search hits; these are discovery hits, not 55 validated screens | Exact document legibility, cropping/source attribution and fit |
| Two-person spatial/hero (ev_ae89ed37733a21e4) | Requested spatial and base-single-billboard records are present | Missing spatial capabilities and demo/variant mismatch; no new certification of double/triple configuration |
| Intro grid (ev_5b014d59e8746769) | Exact scene-012 exists, six slots, grid/builds_up | Preferred 2–3-card treatment requires existing-control verification |
| Collaboration carousel (ev_0125568cf745b6da) | Exact accepted dropoff review-002 exists | Sample exact_value readability blocks relationship predicate; artist/work roles need reconciliation |

Full evidence IDs, reviewed gallery hashes and per-record operation results are in the companion evidence file. Current Future reviews use the corrected v12 context sidecar, not substituted v13 task context. Historical Year Seventeen comments remain historical. Search hits and predicate admission are neither editor approval nor native feasibility.

## Validation and limits

25 existing tests passed: `tests.test_visualtask_matching` and `tests.test_visualtask_technical_requirements`. Existing resource warnings occurred without failures. Controlled in-memory probes tested timeline scope, ignored relationship demands, descriptive evidence dependence, expected-layout admission and family diversity. They did not mutate production inputs.

Replay with the pinned Matching baseline and the source hashes in the evidence inventory: invoke `pipeline.visualtask_matching.C.load(content_class="*")`, `presentation_contract`, `_supports_operation` and `C.diversify` using the recorded contracts/records and family-probe settings. Optional enrichment can change effective records across machines; use the captured effective pool for an exact predicate replay and compare source hashes before claiming a fresh-loader reproduction. Technical index inspection does not replace native testing.

The acceptance receipt checks ordered stage evidence, rejects omission/reordering, verifies source integrity and confirms unchanged runtime/grammar/catalog. No complete candidate pipeline or sequence audit is claimed; that is Job 6. Vocabulary improvements and reconciliation requirements above are proposals only.

**Exact next job: `06-candidate-pipeline.md`. Blocker owner: `none`. Stop after Job 5; Job 6 has not started.**
