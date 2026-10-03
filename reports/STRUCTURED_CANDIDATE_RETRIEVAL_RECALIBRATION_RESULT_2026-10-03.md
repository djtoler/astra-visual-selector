# Structured Candidate Retrieval Recalibration Result — 2026-10-03

## Conclusion

The original matching architecture was directionally correct but not complete enough to prevent the failure seen in the Future StoryPackage gallery.

It correctly assigned StoryPackage extraction and template-neutral beat requirements upstream, kept template selection in Matching, called for machine-readable template capabilities, separated template/media/pairing verdicts, and prohibited retrieval from becoming selection. The StoryPackage 0.2 reference contract was not the main defect.

Two distinct problems remained:

1. **Plan/specification gap:** the plan did not define an executable admission mapping from each VisualTask's entities, cohorts, typed values, obligations, presentation operations and forbidden implications to the template catalog's structured capability fields. It also did not explicitly prohibit generic descriptive words or an old broad matching job from admitting a candidate.
2. **Implementation deviation:** the Future gallery consumer dropped several fields the upstream package supplied, reduced the beat to crude operation labels, and unconditionally unioned legacy job-binding candidates. It could therefore reuse nearly the same pool even when two beats required different visual communication.

The plan was therefore not fundamentally wrong, but it was insufficiently enforceable at the candidate-retrieval boundary. The implementation also failed to honor the stronger parts that already existed.

## Original stages that were present

- Story-owned extraction of exact spans, claims, entities, values, obligations, continuity and presentation requirements.
- A template-neutral VisualTask handoff rather than Story choosing template IDs.
- Matching against reusable template specifications and measured capabilities.
- Separate template, media and combined-pair feasibility.
- Human review before selection or rendering.
- Provenance and receipts for the matching path.

## Missing or unenforced stages

- A deterministic **VisualTask-to-capability contract derivation** stage.
- A deterministic **structured candidate-admission** stage.
- A rule that prior editor choices and legacy job bindings may enrich or order compatible candidates but cannot admit incompatible candidates into a new story.
- A stage receipt proving structured admission ran before the gallery was published.
- Regression checks for materially different beats receiving identical ordered slates.
- Sufficient semantic-splitter tests to prevent incidental digits, plurals, or sentence openings such as “When” from becoming data, sequence, or question requirements.

## Implemented correction

The gallery now runs these stages in order:

1. semantic task split;
2. task-specific presentation-contract derivation;
3. structured catalog-capability admission;
4. local semantic relevance ordering within the admitted set;
5. family diversification;
6. review-only publication with selection and rendering still disabled.

Legacy job bindings cannot admit a candidate in this path. Two existing editor notes were preserved as explicit task-scoped, unvalidated admissions rather than silently converted into general rules.

## Verification

- 310 task slates generated from the Future StoryPackage.
- 502 narrator claims covered, with zero uncovered narrator claims.
- 4,896 review-only candidate cards.
- 310 distinct ordered slates; the largest repeated ordered slate is one task.
- 36 source-clip routes retained.
- 58 matching and StoryPackage tests passed.
- 13 review-storage tests passed.
- Selection authorization remains false.
- Rendering authorization remains false.
- No template was edited and no visual was rendered.

## Remaining limitation

Structured admission establishes plausible capability fit, not editor approval or native-template proof. The refreshed gallery is the next calibration surface. Rejections should update reusable capability evidence or operation mapping, not create story-specific template rules unless the reason is truly story-specific.
