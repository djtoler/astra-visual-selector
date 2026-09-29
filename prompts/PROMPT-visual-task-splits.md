# VisualTask split proposal

Review existing documentary beats and decide whether each beat can be communicated by one developing visual treatment or requires multiple sequential visual treatments.

This stage does not rewrite narration or factual requirements. It proposes task boundaries for editor review.

## Split only when necessary

Keep one task when one treatment can develop over time to carry the full thought. Do not split because of punctuation, sentence count, duration, number of people, template capacity, or a desired transition.

Propose a split when the beat contains two or more visual jobs that cannot truthfully and readably share one treatment—for example:

- evidence or setup followed by a distinct conclusion;
- group context followed by one specific person;
- footage-dependent action followed by a data or document treatment;
- a rule/explanation followed by a separate comparison or reveal.

Existing editor notes outrank model judgment. If the editor assigns different parts of a beat to different treatments, preserve that as split evidence.

Reconcile the result against `issues_matching_layer.json`, especially every beat listed under PI-05, and the bound matching-layer plan sections. A beat named by PI-05 is evidence requiring an explicit disposition, not automatic permission to invent a split. If a reviewed clause is absent from the current source beat, return a `source_mismatch` with the missing reviewed text instead of rewriting narration, silently keeping it single, or fabricating an exact span.

## Output rules

- Every task quote must be one exact, unique substring of the source beat.
- Proposed task quotes must cover the complete beat in order without overlap or lost non-whitespace text.
- Each task gets one matching job from the existing closed job vocabulary.
- Allocate perceptibility constraints to the task that must show them; do not copy every beat constraint to every sibling.
- Preserve source facts and prohibitions. Do not add claims, entities, cohorts, templates, media assets, timing seconds, approvals, selections, or render authorization.
- `keep_single` is a real decision and must include a short reason.
- Every PI-05 beat must be explicitly reconciled exactly once as `propose_split`, `existing_approved_split`, `keep_single`, or `source_mismatch`.
- All multi-task proposals remain `model_draft_unreviewed` until the editor approves, edits, or rejects them.

Return JSON only.
