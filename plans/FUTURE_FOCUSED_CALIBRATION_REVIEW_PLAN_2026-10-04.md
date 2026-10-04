# Future focused calibration review plan

Status: editor approved 2026-10-04; no review tasks are discarded by this
plan.

## Decision

Do not linearly review all 289 remaining Future tasks. Future is a calibration
package, not an untouched acceptance package, and exhaustive review would tune
the matcher too closely to one story. Use the 21 completed tasks as calibration
evidence, review a focused coverage set, update the general matching rules, and
then validate on a new untouched StoryPackage.

## Evidence

- 310 total Future tasks; 21 tasks currently have persisted review evidence.
- The 21 reviewed task slates already expose 49 of the 59 template families in
  the current gallery.
- The 289 remaining tasks contain extensive repetition: 105 use the
  `concept_statement` operation, 53 use `event_narration`, and 41 use
  `archival_progression`.
- Only 10 template families have not appeared in a completed task slate.
- A greedy coverage pass needs 26 remaining tasks to expose every currently
  uncovered presentation-operation combination and every unseen template
  family. Reviewing individual scene variants after their family behavior is
  established is not required unless a scene has materially different
  capabilities.

## Required stages and acceptance checks

1. **Reconcile the 21 saved reviews before requesting more editor labor.**
   Convert reusable findings into general task contracts, family capabilities,
   exclusions, B-roll/overlay routing and semantic-split corrections. Preserve
   story-specific preferences as calibration evidence only.
   - Check: every saved review is classified as reusable, story-specific, or
     requiring clarification; none is silently ignored.
2. **Generate a focused 26-task Future queue.** Select tasks that jointly cover
   all uncovered presentation-operation combinations and all ten unseen
   template families. Keep the full 289-task queue available as history.
   - Check: the coverage receipt lists zero uncovered current operation
     combinations and zero unseen current template families.
3. **Audit candidate-family diversity before asking for those reviews.** For
   each focused task, compare the complete structurally admitted family set to
   the capped review slate. Report families that are valid but hidden separately
   from catalog families that do not pass the task contract. The review surface
   must show one representative per family before repeating scene variants.
   - Check: every focused task records admitted families, displayed families,
     hidden admitted families, the display limit, and the slideshow limit.
   - Check: no family is force-admitted and no unknown native capability is
     represented as validated fit.
4. **Review in short batches and regenerate.** After each batch, reconcile
   general findings and rerun candidate retrieval so the editor does not keep
   reviewing stale candidate behavior.
   - Check: later batches bind to the new gallery hash and display the matching
     rules produced by earlier batches.
5. **Use exceptions, not exhaustive repetition.** Add a task only when it has a
   materially new contract, family capability, candidate shortage, ranking
   failure or conflict with an earlier rule.
   - Check: every added task names its new coverage reason.
6. **Validate generalization on an untouched StoryPackage.** After focused
   Future calibration, use a new user-supplied package for a small stratified
   audit; do not treat Future, Apollo or Year Seventeen as the untouched gate.
   - Check: no package-specific runtime rules are added, all narrated spans get
     typed route dispositions, and candidate admission is explained entirely by
     portable contracts.

## Expected editor workload

- Already complete: 21 Future tasks.
- Additional focused Future review: 26 tasks, subject to shrinking after each
  reconciliation/regeneration batch.
- Final untouched-package audit: approximately 10–15 stratified tasks, expanding
  only for a concrete new failure class.

This reduces the immediate Future queue from 289 tasks to at most 26 targeted
tasks. It does not claim exhaustive editorial approval for every Future beat;
it provides enough diverse evidence to improve and test the general matcher.

## Implemented diversity correction

The exhaustive structured-admission audit found hidden valid alternatives on
all 26 focused tasks: 1,186 admitted-family appearances were outside the former
displayed slates. The focused review slate now preserves the first eight primary
candidates and fills the other eight positions with the least-exposed admitted
families across the queue. Every slate contains 16 distinct families. This
increases focused-queue exposure from 58 to 94 distinct families without
changing admission, asserting fit, selecting a template or authorizing a render.
