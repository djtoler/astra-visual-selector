# Matching-system realignment audit

Date: 2026-09-28
Branch: `codex/treatment-requirements-review`
Status: audit baseline; no merge or live activation authorized

## Product boundary

The current documentary, narration, beat IDs, issue register, editor notes, candidate choices and native renders are evaluation fixtures. The product is reusable beat/VisualTask-to-template-and-media matching that accepts a fresh story package and template/media libraries without source-code changes. Runtime code must not require this documentary's issue IDs, beat IDs or review prose. Contract work supports this matcher; it is not a separate replacement project.

## Work completed since 2026-09-27

### 1. AE template technical specifications

Completed:

- A standalone inspection package measures compositions, durations, editable text fields, total independent media inputs and maximum simultaneously enabled inputs.
- The dual-pass reconciliation, frozen summaries and inventory tooling cover all 32 current source projects.
- Two composition-level accuracy pilots were completed separately from capacity extraction.
- Original AE projects remain read-only; inspection does not require rendering.

Disposition: **retain as reusable system code and library data**.

Required scaling work:

- Replace any remaining machine-specific defaults with an explicit run configuration.
- Publish a stable technical-spec schema/version for downstream consumers.
- Test a second library root as a portability case. Do not redo the 32 measured projects unless their source hashes change.

### 2. Shared entity-context roster

Completed:

- Versioned schema and semantic validator for entities, aliases, relationships, cohorts, facts, source-attributed characterizations, retrieval leads, interpretive branches and editor context.
- Manual editor context has explicit priority while remaining separate from factual evidence.
- Subjective lenses remain labeled and separate; interpretive branches carry direct and cautious language.
- Vector-only evidence cannot silently establish facts, observed relationships or source-attributed characterizations.
- Twenty-seven focused tests and a data-layer implementation handoff exist on `codex/entity-context-roster` in `content-project-mgr`.

Disposition: **retain as reusable contract**.

Required scaling work:

- Integrate the contract into actual Data/Story package production and Matching consumption.
- Test more than the synthetic example, including two stories sharing one entity and story-scoped editor context.
- Define registry storage/version ownership; do not create a second matching-only roster.

### 3. VisualTask contract, entity resolution and cohorts

Completed:

- A source-bound VisualTask artifact separates visual jobs, exact narration spans, identities, cohorts, truth constraints, perceptibility constraints, prohibitions, continuity and timing state.
- Validators reject duplicate IDs, unknown entities/cohorts, lost or overlapping split text and stale cohort evidence.
- One approved beat split demonstrates multiple tasks under one source beat.

Disposition: **retain the contract and deterministic validation; refactor the producer**.

Required scaling work:

- Accept a versioned StoryPackage instead of assuming `beats-all.json`, this narration timing file and this roster layout.
- Generate entity/cohort references upstream rather than relying on documentary-specific override files.
- Add schema validation and a story namespace so IDs do not collide across projects.
- Replace the hand-authored split override path with the general semantic splitter described below.

### 4. VisualTask-to-AE technical comparison

Completed:

- A portable technical index imports measured AE evidence.
- Exact preview-scene-to-native-composition mappings can attach verified slots, text fields and duration to candidate comparisons.
- Unknown mappings and missing requirements remain unresolved rather than being promoted to fillable.

Disposition: **retain the evidence engine and measured mappings**.

Required scaling work:

- Replace assumptions about the current slate/catalog file shapes with versioned interfaces.
- Run comparisons from arbitrary VisualTask and candidate collections, not the current documentary's full artifact.
- Separate reusable candidate-fit logic from generated reports and fixture mappings.
- Add multi-project tests using a second synthetic StoryPackage.

### 5. VisualTask technical requirements

Completed:

- Technical requirements preserve semantic constraints, identity demand and exact timing evidence.
- Unknown media-slot, text-field and typed-data requirements fail unresolved rather than being invented.
- Editor-approved split timing can be bound to measured narration evidence.

Disposition: **retain the schema and fail-closed behavior; refactor inputs**.

Required scaling work:

- Consume generic StoryPackage timing and VisualTasks instead of the current baseline slate.
- Define how the semantic splitter allocates truth, perceptibility, media-kind and data requirements between sibling tasks.
- Support explicit timing evidence providers rather than one narration artifact format.

### 6. Treatment-requirements pilot

Completed:

- A closed schema, prompt, source binding and deterministic validator distinguish verified native capacity from proposed treatment assignments.
- The user approved one exact treatment and a replacement native template test.
- The Story on Photo native test rendered successfully at 3.12 seconds and was accepted as “perfect, 100% perfect.”
- The incompatible AE-26 screen-mockup candidate was held out rather than rebuilt.

Disposition: **retain the schema, prompt principles and validator; keep the render as fixture evidence**.

Required scaling work:

- Replace the `pilot-001` builder that chooses the first available pairing with an API accepting an explicit StoryPackage, VisualTask and candidate.
- Support batch drafting without hard-coded directories or candidate discovery behavior.
- Formalize reusable ingestion of native-test evidence, font substitutions and editor review.
- The approved render proves one pairing, not general treatment accuracy.

### 7. Five-case matching accuracy batch

Completed:

- A replayable read-only batch covers a long carousel, split beat, text-heavy document, actual-footage requirement and missing-media conditional.
- Source hashing and no-selection/no-rendering boundaries work.
- The corrected batch measured three passes and two genuine gaps.
- The 20+ spatial inclusion rule and test-specific eleven-person carousel treatment were separated.
- The eleven-person native test actually placed eleven unique people into a fourteen-photo template, filled the three surplus native slots with specified repeated images, rendered the replacement content, and received the editor's “good” response. That is visual treatment evidence about surplus-slot handling, not merely proof that fourteen is greater than eleven.

Disposition: **retain all five cases as regression fixtures; refactor the evaluator**.

Required scaling work:

- The evaluator currently contains one custom code branch per known case. Replace that with declarative assertions over general pipeline output.
- Keep expected outcomes and beat/candidate IDs in fixture files only.
- Add held-out cases not used to design the matcher.
- Fix the two measured product gaps through general typed requirements and verdict logic, not beat-specific conditions.
- Revise the eleven-person result so it preserves the exact surplus-slot treatment, actual media assignments, render receipt and editor verdict; do not reduce it to a capacity-qualified candidate assertion.

### 8. Independent VisualTask matching pilot

Completed:

- Beat 28 proves that sibling VisualTasks can query template bindings and Production Ready media independently.
- Each template and media result carries task-level provenance.
- A text-only setup task does not inherit people media from its sibling.

Disposition: **retain the isolation rule and provenance checks; refactor the runner and matching logic**.

Required scaling work:

- Process every VisualTask in an arbitrary StoryPackage rather than requiring one `sourceBeatId` argument.
- Consume task-specific typed requirements, template technical capacity, editor exclusions and media-kind needs.
- Produce separate template-fit and media-availability verdicts, including `conditional` with typed gaps.
- Replace reliance on old job bindings as the primary matcher with the full VisualTask contract and verified template capabilities.

### 9. Semantic split proposal work

Completed:

- Useful general principles were established: split by distinct visual jobs, preserve exact source spans, cover all narration without overlap or loss, assign one job per task and require review before activation.
- The current documentary produced one approved split, five new proposals and one source/review mismatch.

Disposition: **retain the principles, exact-span validator and current decisions as fixtures; redesign the production stage**.

Required scaling work:

- Remove hard-coded PI-05 IDs and matching-document hashes from runtime code.
- Move `issues_matching_layer.json`, the beat-review export and the current split draft into the regression/evaluation layer.
- Add an LLM-backed, provider-independent semantic splitter that accepts only the versioned StoryPackage, VisualTask vocabulary, roster references and applicable editor context.
- Emit structured one-task or multi-task proposals for every unseen beat.
- Apply deterministic validation after the model response.
- Test against the current reviewed cases and a genuinely unseen holdout set before connecting it to live matching.

## What does not need to be redone

- The 32-project AE technical inspection.
- The two AE capacity accuracy pilots.
- The shared roster schema, epistemic lanes and editor-priority rules.
- Exact-span, stale-source, capacity and provenance validators.
- The accepted Story on Photo native render.
- The existing reviewed beats, issue register and five-case batch as regression evidence.

## What must be redone or materially refactored

1. Semantic split generation for unseen beats.
2. StoryPackage-to-VisualTask production without documentary-specific overrides.
3. Batch VisualTask matching from full task requirements rather than old beat/job bindings.
4. Declarative accuracy evaluation instead of five hard-coded evaluator branches.
5. Treatment request generation for arbitrary task/candidate pairs instead of `pilot-001` discovery.
6. End-to-end integration tests using at least one unseen story package.

## Realignment execution order and acceptance checks

1. **Freeze and classify the current branch.**
   - Acceptance: every changed file is labeled production code, reusable schema/data, regression fixture or generated output; no fixture ID remains unacknowledged in production code.
2. **Freeze the existing VisualTask contract and add only the minimum versioned StoryPackage input envelope the matcher needs.**
   - Acceptance: the current VisualTasks and one unrelated sample story enter the same matcher without changing Python source; no broad Story/Data redesign is introduced in this matching task.
3. **Build the provider-independent semantic splitter.**
   - Acceptance: it emits exact complete spans and one or more tasks for unseen beats; invalid or incomplete model output fails closed.
4. **Refactor VisualTask production and matching into batch APIs.**
   - Acceptance: one command processes every task in either sample story and emits independent template and media results.
5. **Convert current reviews into declarative regressions.**
   - Acceptance: current cases run without case-specific branches in production or evaluator code.
6. **Run held-out accuracy evaluation.**
   - Acceptance: results separately report split accuracy, requirement preservation, template retrieval, media retrieval and conditional-gap accuracy; failures remain visible and do not activate selection.

No matching, selection or render output should be called scalable until all six stages pass in order.
