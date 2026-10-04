# Job 3 — Upstream contract fitness

**Audit status: PASS. Contract fitness: partial, with proven gaps. Blocker owner: none.**

Matching receives enough upstream meaning for several cases it currently mishandles, but not enough verified Data and Media coverage to claim general task readiness. The most serious gap is validation: a correctly hashed file can be marked as a bound handoff without its contents satisfying any task. The existing richer handoff formats already express many missing requirements. This audit proposes no new schema fields and makes no production changes.

Frozen production: Matching `1276d0ca1daece81b5b7b38c8b5f5280046e5077`; Story `d5117a6de0fd0c640a336c6f456946ec8b40f319`. The later report-publication commit does not change these baselines. Configured model: gpt-6-astra / medium. No escalation.

## What the evidence establishes

1. **A bound file is not a validated handoff.** Public preflight accepts correctly hashed empty `{}` Data and Media handoffs. The requirements function then removes all 177 missing-handoff warnings for the 186 Jay-Z/Drake tasks (73 data-required, 104 media-required). It uses binding presence rather than per-task content. This was tested through preflight and requirements only; no model/provider run or render occurred.
2. **Source hashes do not verify derived facts.** The Story checker rejects stale script/registry/cohort hashes, but accepts a changed supported value and an arbitrary receipt string. The legacy assignment validator verifies top-level source files, yet accepts a mismatched per-field receipt digest and a synthetic replacement of an explicit unavailable value with zero. Its baseline representation of absence is correct.
3. **Valid Story input is sometimes missed.** The 93-person cohort, reissue/festival scene and a b-roll-only Year task have explicit mediaNeeds, yet the general requirements function declares media not required. The Jay-Z/Drake comparison contains both artists in typed values and the obligation, while its reviewed presentation contract counts one. Evidence: `ev_c0014381cd5b341b`, `ev_4bad981eb189dc6f`, `ev_805456ee8bf50f03`, `ev_ae89ed37733a21e4`.
4. **Upstream annotation is also incomplete.** Six Year Seventeen obligations carry no requirement fields beyond their provenance note. Future’s collective-influence passage lacks group requirements; the fan-allegation and track-list cases need clearer evidence/perceptibility requirements. Evidence: `ev_76144b97f6b04467`, `ev_945fc64c57b6bbfb`, `ev_8d097d68699e413f`, `ev_063fd655708a1b49`.
5. **Existing richer contracts are not the general current path.** The Year@7 matching handoff has 41 tasks, 106 text fields and 89 value roles, including rounding, caveats, exact narration anchors and simultaneous versus sequential focal counts. Its existing tests pass. It is not a current @9/@5/@4 cross-story handoff, and the general agent does not consume it.

These observations distinguish a contract’s expressive capacity, actual input population, and what a consumer validates. A schema pass is not factual approval, a candidate is not a validated treatment, and a media need is not proof of available media.

## Measured inputs

| Package | Claims | Claim values | Supported claims | Values lacking nonempty basis | Timing |
|---|---:|---:|---:|---:|---|
| year-seventeen@9 | 150 | 0 | 0 | 0 | absent |
| future-volksgeist@5 | 502 | 0 | 0 | 0 | absent |
| jayz-drake-settle-it@4 | 222 | 62 | 70 | 61 | absent |

An empty basis is a diagnostic, not proof all context is absent: units, labels, cohorts and obligations may supply it elsewhere. Year Seventeen’s separate legacy Data artifact contains 79 fields for 28 tasks, with source selectors, columns and transforms. It does not establish general coverage for all current Story tasks. Jay-Z/Drake’s 70 supported claims use string receipts; the Story validator does not replay their values.

| Public evaluation package | Tasks | Data-required | Media-required | Missing-handoff warnings |
|---|---:|---:|---:|---:|
| year-seventeen@9 | 115 | 51 | 76 | 127 |
| future-volksgeist@5 | 310 | 17 | 258 | 275 |
| jayz-drake-settle-it@4 | 186 | 73 | 104 | 177 |

All three public evaluation contracts omit Data and Media handoff bindings. These 579 warnings do not mean 579 false facts, absent assets or incompatible templates. Some demands themselves are misclassified. The older Year-v12 proposal artifact produces different counts (89 warnings) because it is a different artifact; the JSON probes label that separate input explicitly.

Both frozen and live Production Ready manifest metadata pass the existing verification checks and list 575 distinct asset IDs: 70 article entries, 134 videos, 75 full images, 20 social posts, 1 lyric document, 21 covers, and 261 paired cutout/glow entries each. Counts overlap across categories. This is inventory metadata, not certification that a required interview, era, solo portrait, lyric or document is available and eligible. Asset bytes/playback/rights were not re-audited.

## Field-by-field sufficiency matrix

Ownership names the producer of the meaning/data/media; a consumer’s failure is separately described. “Partial” is never converted to a fabricated zero, asset or relation. Full paths and case joins are in [the JSON report](03-upstream-contract-fitness.json).

| Field area / owner | Existing contract and observed inputs | Consumer finding / sufficiency |
|---|---|---|
| script / spans / package revision / story | Exact text, UTF-8 digest, codepoint spans, story revision and packageId. All three exact packages validated; revisions @9/@5/@4. | Adapter validates; splitter trusts accepted receipt and does not bind mutated body to receipt. **sufficient_input_incomplete_downstream_revalidation**. |
| entityRegistry / canonical IDs / data | Repo, commit, path, digest; package-local entities are caches. All three bind entity_roster eacb739 / roster v12. | Story checker checks digest, not declared commit; public preflight plus registry binding checks commit/repo/digest. **sufficient_on_public_path_layered_validation_required**. |
| mentioned / display / representedBy / story | Separate mentioned, required/eligible/none/withheld display states and representation forms. Curren$y clause excludes Drake; unnamed Drake withheld in opening. | Fields survive adapter; historical media requests ignored scoped subject semantics. **adequate_in_examined_corrected_inputs**. Evidence: `ev_0183c99a16600ab0`. |
| cohorts / members / subset authorization / data | Replayable snapshot/rule, completeness, expectedCount, shownIds and approved shownAuthorization. Year: complete93 and incomplete12/10 cohorts; Jay-Z: complete31; Future has no cohorts. | Checker replays complete membership and retains unresolved gaps unless an authorized subset applies; public requirements ignore cohortRefs when deciding media_needed. **representation_sufficient_consumption_gap**. Evidence: `ev_c0014381cd5b341b`. |
| relationship participants / roles / story | Narration, entityRefs, obligations.intent/mustBePerceptible; richer handoff value roles/showTogether. No generic relation graph required by current schema. Rico/Future relationship explicit; Jay-Z values identify both comparators; Future collective influence only names Future in refs. | Gallery reviewed entityCount uses displayed refs without reconciling value participants. **mixed_upstream_omission_and_downstream_loss**. Evidence: `ev_5b014d59e8746769`, `ev_ae89ed37733a21e4`, `ev_945fc64c57b6bbfb`. |
| numeric values / units / data | Story values allow number/string, optional unit/label/entity/basis; Data assignments carry value/unit and source receipts. Year and Future: 0 claim values; Jay-Z: 62 values, 70 supported claims. Legacy Year assignments:79 fields/28 tasks. | General path has no per-task assignment-content consumer; typed values influence classification but not verified calculations. **not_sufficient_as_verified_general_data_contract**. Evidence: `ev_197e8df3cdb679e1`, `ev_76144b97f6b04467`. |
| measurement basis / population / comparability / data | Optional basis string; legacy assignment population/basis; richer handoff concept/caveats. 61/62 Jay-Z values have empty or absent basis. Some population is in labels/cohortRefs rather than basis. | No cross-field comparability verification in Story checker; unit changes do not prevent task merge. **partial_do_not_infer_every_empty_basis_is_semantically_unknown**. Evidence: `ev_197e8df3cdb679e1`, `ev_ae89ed37733a21e4`. |
| source row locator / columns / transform / data | Legacy assignment receipt already has sourcePath/sourceSha256/selector/columns/transform. Story receipts are strings. Structured receipts present in79 legacy fields; Jay-Z claim receipts identify source files in prose, not replayable per-value row/transform contracts. | Assignment validator verifies top-level source files but does not cross-check each field digest or recompute values. **insufficient_value_level_verification**. |
| supported status / receipts / data | Factual supported requires receipts under Story schema; factual unverified remains allowed. Year87 and Future364 factual claims are not thereby fact-checked; Jay-Z70 supported. | Supported value mutation and nonsense receipt survive Story checker. Passing structure is not fact approval. **structural_only**. |
| display / rounding / narration alignment / story | Richer matching handoff values specify display exact/rounded/ordering/qualitative/absent and narration anchors. Year@7 handoff has89 values with display roles; Year@9 and other general packages do not carry equivalent handoff artifacts on agent path. | General path does not consume richer handoff; legacy data fields lack a general rounding-to-narration check. **existing_representation_not_generally_connected**. Evidence: `ev_76144b97f6b04467`, `ev_81a8bfc05956e7b1`. |
| caveats / prohibited implications / story | obligations.mustBeTrue/wouldBeALie and richer handoff data.caveats. Jay-Z warns against calling Umbrella his single and against treating crowd examples as data-sourced; Year handoff has Spotify-only/history caveats. | Preserved in adapter/tasks; requirement status does not validate these constraints against handed-off content. **meaning_available_enforcement_unproven**. |
| missing value versus zero / data | Explicit typed absence exists in legacy assignment and absence role in matching handoff. Historical Jay-Z year17 meter: value:null, availability:unavailable. No missing value was interpreted as zero in this audit. | Assignment validate accepted synthetic replacement with numeric zero; whole-source digests do not bind derived payload. **correct_baseline_representation_weak_validator**. |
| evidence / documents / artifacts / story | mediaNeeds(kind=document/artwork/footage,constraints), needsOnScreenText and perceptibility. Track-list inspection and fan allegations lack explicit evidence requirements in examined claims. | Reviewed contexts classify as item_sequence/data_explanation; Future current adds evidence_presentation. **upstream_annotation_gap_and_downstream_classification_gap**. Evidence: `ev_063fd655708a1b49`, `ev_8d097d68699e413f`. |
| quote / lyrics / source footage / story | Beat speaker role, speaker identity/sourceTimestamp, quote text obligation, clip exact-footage need. Future36 clips,3quotes;6 unidentified speakers explicitly flagged. Lyrics request ev_6c440... is not satisfied merely by a document category existing. | Clip routes separate, quote grouped; rhetorical-question heuristics can override quote treatment metadata. **role_inputs_useful_asset_readiness_unverified**. Evidence: `ev_6c440a7b5cb840d4`. |
| text content / truncation / wrapping / story | Richer handoff text.fields supports copy/contentRef, role, priority,truncation,abbreviation,wrap,maxChars,simultaneousWith. Year@7 handoff106 text fields across31 tasks; no equivalent attached to current general runs. | Not consumed by general candidate gallery as text feasibility input. **existing_contract_capability_not_current_general_coverage**. Evidence: `ev_063fd655708a1b49`, `ev_60553fc81c4e442a`. |
| mediaNeeds versus availability / media | Story expresses needs; Media manifest expresses delivered asset IDs/kinds and lifecycle verification. Frozen and live manifests each575 distinct asset IDs; category counts do not establish any task has its required assets. Three public tasks contain no mediaHandoff. | _requirements tests presence of a file binding, not supply eligibility; it misses three Year tasks with explicit mediaNeeds. **general_media_supply_unverified**. Evidence: `ev_4bad981eb189dc6f`, `ev_65fa5e81c76d4c01`, `ev_805456ee8bf50f03`. |
| solo/group / identity / framing / era / media | Manifest/person_view and metadata; resolver kinds/framing and task requirements; Story can request solo images and era spread. Year editor distinguishes correct subjects from ineligible group framing and insufficient era assets. | Legacy media resolver exists; general gallery retrieves templates independently of live media feasibility. **separate_media_eligibility_required**. Evidence: `ev_040c6162ac818a19`, `ev_65fa5e81c76d4c01`, `ev_84d8227c5595ac1a`. |
| source provenance / lifecycle eligibility / media | Delivered source/delivery path and sha256, verification flags; lifecycle controls upstream. Both inspected manifests pass metadata gate; false source_media_unchanged rejected. Live asset bytes, rights or semantic identity not re-audited. | Existing consumer uses delivered path and metadata; optional generic media handoff is not parsed for lifecycle proof. **manifest_provenance_exists_general_handoff_content_unverified**. |
| focal simultaneous versus sequential counts / story | Richer handoff media.focal separates simultaneous/storyItems/sequencePermitted/basis and typed unknown. Year@7 handoff includes one focal_unknown; Story recognizableIdentityCount alone does not define staging. | Rich checker guards conflation; general path uses identity counts/operations without this input. **existing_richer_model_not_generally_connected**. Evidence: `ev_5b014d59e8746769`, `ev_81a8bfc05956e7b1`. |
| continuity / adjacency / return / story | continuity scope includes adjacency, sequence, template/family, palette/grammar/framing; strength and provenance. Year5, Future2, Jay-Z4 continuity groups. Required opening-chart return encoded. | Preserved in task artifacts; no assertion that per-task candidate lists enforce sequence invariants. **input_adequate_enforcement_deferred**. Evidence: `ev_197902cdbab5c967`, `ev_457bec72518e17bd`. |
| withholding / recognizable identity demand / story | display:withheld; obligations.withheld, recognizableIdentityCount, wouldBeALie. Opening hidden identity and93-person requirements explicit. | Fields cannot be replaced by raw entity-count heuristics or generic media presence. **adequate_specific_inputs_consumption_gap**. Evidence: `ev_c0014381cd5b341b`, `ev_0183c99a16600ab0`. |
| timing / freshness of audio attachment / story | timing status,joinKey,audio snapshot,claim start/end attachments. All3 packages timing absent. | Exact source timestamps are not narration durations; neither task length nor candidate existence proves timed fit. **explicitly_unresolved_not_zero**. |
| Data / Media handoff identity and completeness / matching | Optional task bindings contain path+sha256 only; generic content schema not enforced here. None supplied on all3 public evaluation task contracts. | Two {} files pass preflight and suppress177 missing-handoff gaps in Jay-Z requirements. No provider or full pipeline was run for this probe. **proven_validation_gap**. |
| adapter / source receipt freshness / matching | Adapter has accepted/packageSha256/authorityCommit/checkerSha256; proposals source digest. Frozen sources verified; public preflight rejects moved registry commit and stale handoff digest. | Standalone splitter accepted deliberately stale packageSha256; gallery verifies packageId but not stored source digest. **strong_entry_preflight_weak_intermediate_revalidation**. |

## Typed gaps and smallest proposed changes

No new fields are proposed. Each delta uses existing fields/contracts or strengthens their binding and validation. Cross-story evidence supports the recurring needs; isolated instructions remain scoped to their originating scene. These are recommendations for the later integrated audit, not implementation authorization.

### G01 — required_meaning_only_in_provenance (story)

Six Year obligations carry only id/claims/provenance; Future collective influence and fan-evidence cases omit required perceptibility/evidence annotations.

**Minimal proposed delta:** Populate existing obligations.intent/mustBePerceptible/mediaNeeds/wouldBeALie and implied entityRefs where source-supported; never invent closed membership from a collective phrase.

**Evidence:** `ev_76144b97f6b04467`, `ev_945fc64c57b6bbfb`, `ev_8d097d68699e413f`.

### G02 — typed_data_not_bound_to_general_tasks (data)

No dataHandoff on any public evaluation contract; Year/Future have no claim values; Jay-Z values lack replayable structured receipts. Historical Year79 fields do not cover arbitrary current tasks.

**Minimal proposed delta:** Supply current task-bound assignments using existing typedFields/receipt selector+columns+transform/sourceSha256, keyed to exact claim/task/package identities. Keep unsupported quantities unresolved.

**Evidence:** `ev_76144b97f6b04467`, `ev_197e8df3cdb679e1`.

### G03 — value_receipt_not_verified (matching)

Story checker accepts modified supported values and arbitrary receipt strings; assignment validator accepts field sourceSha256 inconsistent with top-level verified source.

**Minimal proposed delta:** Validate existing receipt references against bound sources and replay declared transformations or require Data verification receipt; distinguish structural acceptance from verified fact acceptance.

**Evidence:** pinned code/artifacts and named validation probes.

### G04 — empty_handoff_suppresses_missing_gaps (matching)

Public preflight accepts two correctly hashed {} files; _requirements marks all73 data-required and104 media-required tasks bound.

**Minimal proposed delta:** Require existing assignment/media receipt content validation plus exact package/task coverage before marking bound; retain per-task typed gaps for absent or invalid coverage.

**Evidence:** pinned code/artifacts and named validation probes.

### G05 — explicit_media_need_not_detected (matching)

Three Year proposals p-03-03,p-07-07,p-30-30b carry mediaNeeds yet public requirements say media not_required.

**Minimal proposed delta:** Derive demand from existing obligations.mediaNeeds, cohortRefs representedBy and speaker routes, not only entityRefs/operation labels.

**Evidence:** `ev_c0014381cd5b341b`, `ev_4bad981eb189dc6f`, `ev_805456ee8bf50f03`.

### G06 — task_specific_media_supply_unverified (media)

No general-run media handoff covers requested artwork/era spread/footage. Historical review proves shortages in some scopes; current575-asset manifest alone cannot resolve them.

**Minimal proposed delta:** Return task-scoped eligible asset IDs with existing lifecycle/source digest and kind/identity/framing evidence, or an explicit unmet sourcing brief. Do not report template incompatibility for absent media.

**Evidence:** `ev_65fa5e81c76d4c01`, `ev_4bad981eb189dc6f`, `ev_032190ddc33477c4`.

### G07 — participant_information_not_reconciled (matching)

Jay-Z/Drake values and formula obligation name both artists but reviewed entityCount=1; valid Rico/Future relation shows semantic inputs can carry both.

**Minimal proposed delta:** Reconcile existing values.entity, entityRefs, cohortRefs and obligation participants before constructing display demand; preserve hidden/none states.

**Evidence:** `ev_ae89ed37733a21e4`, `ev_5b014d59e8746769`.

### G08 — richer_handoff_not_connected_generally (matching)

Year@7 matching handoff41 tasks/106 text fields/89 value roles passes existing tests; general current agent path does not consume it.

**Minimal proposed delta:** Consume a current source-bound matching handoff through the established checker; require upstream refresh per package rather than repinning or copying legacy authored tables blindly.

**Evidence:** `ev_063fd655708a1b49`, `ev_81a8bfc05956e7b1`, `ev_65fa5e81c76d4c01`.

### G09 — intermediate_receipt_not_revalidated (matching)

Standalone splitter accepts stale adapter packageSha256 despite accepted:true; public entry checks do not make independent downstream calls safe.

**Minimal proposed delta:** Bind existing receipts to exact consumed artifact bytes and reject mismatch at consumption boundaries, retaining checker authority/source hashes.

**Evidence:** pinned code/artifacts and named validation probes.

### G10 — typed_absence_can_be_coerced (matching)

Legacy baseline uses unavailable/null correctly; validator accepts mutated value=0 as resolved.

**Minimal proposed delta:** Enforce existing availability/absence representation and value type at validation. Legitimate observed zeros remain numeric; unknown values stay explicit missing states.

**Evidence:** pinned code/artifacts and named validation probes.

### G11 — unidentified_clip_speaker (story)

Pinned Future checker emits six speaker_unidentified gaps.

**Minimal proposed delta:** Resolve speaker through existing beat.speaker.entity only with source evidence, or keep speaker_unidentified and exact-footage constraints; do not substitute narrator or a guessed person.

**Evidence:** pinned code/artifacts and named validation probes.

### G12 — timing_unattached (story)

All three pinned packages declare timing.status=absent.

**Minimal proposed delta:** Attach existing source-bound timing contract when timing becomes available; retain duration/readability fit as unresolved until then.

**Evidence:** pinned code/artifacts and named validation probes.

Timing absence and unresolved speaker identity are explicit readiness gaps, not proof that the contract is malformed. Media’s responsibility is eligible supply and its evidence; Matching is responsible for requesting, consuming and validating that evidence. Missing supply must remain distinct from template capability.

## Editor cases: upstream omission versus downstream failure

All current candidate reviews use the Job 1 gallery-bound context sidecar. Historical Year Seventeen supply statements are retained as historical observations; they are not assertions about today’s live library. Each JSON case includes the exact claims, obligations, continuity and review source pointers.

- **U01 / `ev_0183c99a16600ab0` / `year-seventeen@9`:** Corrected Story names Curren$y artwork and excludes Drake; historical wrong media is not a template-fit failure. Classification: `adequate_story_historical_matching_media_error`.
- **U02 / `ev_c0014381cd5b341b` / `year-seventeen@9`:** Cohort and93-person obligation adequate, but public media-needed classifier misses this demand. Classification: `adequate_story_matching_failure`.
- **U03 / `ev_040c6162ac818a19` / `year-seventeen@9`:** Solo-image constraint is explicit; group photos require Media eligibility rejection independent of template capability. Classification: `media_eligibility_not_template_incompatibility`.
- **U04 / `ev_4bad981eb189dc6f` / `year-seventeen@9`:** Story has reissue artwork/festival-footage requirements; historical user says templates correct but supply unsuitable; public demand misses it. Classification: `media_shortage_and_matching_demand_failure`.
- **U05 / `ev_65fa5e81c76d4c01` / `year-seventeen@9`:** Eight artworks/portraits across eras is a sourceable brief; historical lack of eligible media does not reject the timeline capability. Classification: `media_supply_gap`.
- **U06 / `ev_84d8227c5595ac1a` / `year-seventeen@9`:** Editor explicitly says media are available and correct but pairing/template choice is wrong. Classification: `adequate_media_historical_matching_failure`.
- **U07 / `ev_457bec72518e17bd` / `year-seventeen@9`:** Required opening-chart return is encoded in continuity, not a request for new data. Classification: `adequate_story_continuity_input`.
- **U08 / `ev_76144b97f6b04467` / `year-seventeen@9`:** Rate subspan exists; contextual comparison identities and structured obligation are incomplete; text expansion is Matching defect. Classification: `mixed_story_omission_matching_failure`.
- **U09 / `ev_ae89ed37733a21e4` / `jayz-drake-settle-it@4`:** Both artist values and comparison obligation exist despite only Jay-Z in entityRefs. Classification: `adequate_cross_field_input_matching_failure`.
- **U10 / `ev_197e8df3cdb679e1` / `jayz-drake-settle-it@4`:** Share and streams/track are typed separately; they should not merge merely because subject is identical. Classification: `adequate_data_semantics_matching_failure`.
- **U11 / `ev_8d097d68699e413f` / `jayz-drake-settle-it@4`:** Attributed fan allegation needs evidence; no explicit evidence obligation, plus wrong quantitative classification. Classification: `story_omission_and_matching_failure`.
- **U12 / `ev_063fd655708a1b49` / `future-volksgeist@5`:** Track-list evidence needs readable document/text; historical operation omitted it; current operation improved but requirement remains unverified. Classification: `story_annotation_gap_partial_matching_improvement`.
- **U13 / `ev_5b014d59e8746769` / `future-volksgeist@5`:** Both family participants and relation available; reviewer’s simultaneous/sequential capacity concern exceeds a raw entity count. Classification: `adequate_story_relation_staging_reconciliation_needed`.
- **U14 / `ev_032190ddc33477c4` / `future-volksgeist@5`:** Witness and interview identities are supplied; exact evidence/media availability is not certified by that supply. Classification: `adequate_story_identity_media_readiness_unresolved`.
- **U15 / `ev_6c440a7b5cb840d4` / `future-volksgeist@5`:** Lyrics-specific requirement concerns readable/source-faithful content, not generic identity imagery. Classification: `evidence_requirement_reconciliation`.

The strongest counterexample to blaming upstream media is `ev_84d8227c5595ac1a`: the editor says the media are available and correct, but the template pairing is wrong. Conversely, `ev_4bad981eb189dc6f` says the templates are correct and the available media do not communicate the scene. Those must remain different verdicts.

## Freshness and validation probes

Sixteen existing tests passed: 14 covering agent contracts and Data handoff/assignment, plus 2 authoritative matching-handoff tests using the pinned Story checkout. Thirty focused probe observations are recorded in [03-validation-probes.json](03-validation-probes.json). Synthetic changes were restricted to temporary files or in-memory copies.

| Probe | Observed result | Interpretation |
|---|---|---|
| `baseline_story_year-seventeen` | accepted | Structurally valid; approved subsets can coexist with incomplete underlying cohorts. |
| `baseline_story_future-volksgeist` | accepted | Structurally valid with six explicit unidentified speaker gaps. |
| `baseline_story_jayz-drake-settle-it` | accepted | Structurally valid, not independently fact-verified. |
| `stale_script_digest` | rejected | Expected rejection. |
| `stale_registry_digest` | rejected | Expected rejection. |
| `stale_cohort_digest` | rejected | Expected rejection. |
| `registry_commit_changed_hash_unchanged` | accepted | Standalone checker checks bytes but not declared git commit; public path adds registry authority checks. |
| `supported_value_changed_receipt_unchanged` | accepted | Supported status/string receipt does not verify the number. |
| `supported_receipt_nonsense` | accepted | No receipt locator/parser validation here. |
| `splitter_stale_adapter_receipt` | accepted | accepted:true is trusted without rebinding content. |
| `public_preflight_baseline` | accepted | Pinned current public inputs resolve. |
| `public_preflight_wrong_registry_commit` | rejected | Expected fail-closed authority check. |
| `public_empty_data_media_handoffs` | accepted | Content/coverage not checked; 177 gaps disappear. |
| `public_stale_media_handoff_digest` | rejected | Expected file digest check. |
| `stored_data_assignment_freshness` | accepted | Stored79-field artifact source files still match. |
| `fresh_legacy_data_assignment` | accepted | Existing legacy recipe reproduces resolved status, not general coverage. |
| `stale_data_source_digest` | rejected | Expected stale source rejection. |
| `field_receipt_digest_unlinked_to_source` | accepted | Per-field receipt is not cross-checked. |
| `typed_absence_replaced_with_zero` | accepted | Validator accepts invalid loss of typed absence; baseline was correct. |

Passing negative tests proves only the tested boundary. Accepting an intentionally bad input proves a validation hole; it does not establish actual corruption of production inputs. No missing measurement in this report is treated as zero.

## Sources and scope

Key pinned implementations:

- [pipeline/storypackage_adapter.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/storypackage_adapter.py)
- [pipeline/storypackage_splitter.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/storypackage_splitter.py)
- [pipeline/storypackage_candidate_gallery.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/storypackage_candidate_gallery.py)
- [pipeline/storypackage_matching_handoff.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/storypackage_matching_handoff.py)
- [pipeline/storypackage_data_handoff.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/storypackage_data_handoff.py)
- [pipeline/storypackage_data_assignment.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/storypackage_data_assignment.py)
- [pipeline/matching_agent.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/matching_agent.py)
- [pipeline/matching_agent_contracts.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/matching_agent_contracts.py)
- [pipeline/media_candidates.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/media_candidates.py)
- [pipeline/visualtask_matching.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/visualtask_matching.py)
- [pipeline/visualtask_requirements.py](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/pipeline/visualtask_requirements.py)
- [plans/storypackage-02-integration-tasks.json](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/plans/storypackage-02-integration-tasks.json)
- [grammar/matching-agent-task.schema.json](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/grammar/matching-agent-task.schema.json)
- [grammar/library-snapshot.json](https://github.com/djtoler/astra-visual-selector/blob/1276d0ca1daece81b5b7b38c8b5f5280046e5077/grammar/library-snapshot.json)
- [architecture/storypackage/SPEC-0.2.md](https://github.com/djtoler/patterns/blob/d5117a6de0fd0c640a336c6f456946ec8b40f319/architecture/storypackage/SPEC-0.2.md)
- [architecture/storypackage/storypackage-0.2.schema.json](https://github.com/djtoler/patterns/blob/d5117a6de0fd0c640a336c6f456946ec8b40f319/architecture/storypackage/storypackage-0.2.schema.json)
- [architecture/storypackage/matching-handoff-0.2.schema.json](https://github.com/djtoler/patterns/blob/d5117a6de0fd0c640a336c6f456946ec8b40f319/architecture/storypackage/matching-handoff-0.2.schema.json)
- [architecture/storypackage/tools/check.py](https://github.com/djtoler/patterns/blob/d5117a6de0fd0c640a336c6f456946ec8b40f319/architecture/storypackage/tools/check.py)
- [architecture/storypackage/tools/check_handoff.py](https://github.com/djtoler/patterns/blob/d5117a6de0fd0c640a336c6f456946ec8b40f319/architecture/storypackage/tools/check_handoff.py)
- [architecture/storypackage/tools/build_matching_handoff.py](https://github.com/djtoler/patterns/blob/d5117a6de0fd0c640a336c6f456946ec8b40f319/architecture/storypackage/tools/build_matching_handoff.py)
- [architecture/storypackage/year-seventeen@9.storypackage-0.2.json](https://github.com/djtoler/patterns/blob/d5117a6de0fd0c640a336c6f456946ec8b40f319/architecture/storypackage/year-seventeen@9.storypackage-0.2.json)
- [architecture/storypackage/future-volksgeist@5.storypackage-0.2.json](https://github.com/djtoler/patterns/blob/d5117a6de0fd0c640a336c6f456946ec8b40f319/architecture/storypackage/future-volksgeist@5.storypackage-0.2.json)
- [architecture/storypackage/jayz-drake-settle-it@4.storypackage-0.2.json](https://github.com/djtoler/patterns/blob/d5117a6de0fd0c640a336c6f456946ec8b40f319/architecture/storypackage/jayz-drake-settle-it@4.storypackage-0.2.json)

Important symbols: `check.check`, `storypackage_adapter.build`, `matching_agent_contracts.preflight`, `matching_agent._validate_registry_binding`, `matching_agent._requirements`, `storypackage_splitter.build`, `storypackage_data_assignment.validate`, `storypackage_matching_handoff.build`, `media_candidates.validate_delivery_manifest`, `media_candidates.delivery` and `media_candidates.resolve`. All listed runtime and schema bytes were compared with their frozen git objects.

The old cross-layer handoff document’s “claim is roughly a shot” wording is historical and superseded by StoryPackage0.2’s explicit claim/VisualTask distinction. The manifest’s misplaced HANDOFF path was resolved to `architecture/HANDOFF_data_matching_media.md`; no missing source was invented.

Hypothesis, not final redesign: connecting and validating the existing richer handoff may address more failures than adding schema fields. Automatic `brollFallbackAvailable:true` is observed, but no downstream misuse or actual footage readiness is asserted. Jobs4–8 must complete before an integrated redesign conclusion.

Acceptance: all required field areas covered; each typed gap owned by Story, Data, Media or Matching; minimal deltas supplied; no unsupported new fields; exact evidence IDs/source context; missing data and media kept separate from zero and incompatibility; ordered-stage omission and reorder checks; frozen production unchanged. See [03-acceptance.json](03-acceptance.json).

**PASS — Job 3 complete. Exact next job: `04-matching-transformations.md`. Blocker owner: `none`. Job 4 has not started.**
