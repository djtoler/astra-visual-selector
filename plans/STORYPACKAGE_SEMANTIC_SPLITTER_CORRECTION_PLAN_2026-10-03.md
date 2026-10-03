# StoryPackage Semantic Splitter Correction Plan — 2026-10-03

## Objective

Correct the fresh-story matching path so optional StoryPackage `jobProposals[]` are advisory inputs rather than a coverage gate. The matching layer must derive review-only VisualTask proposals from the complete accepted StoryPackage and must not leave obvious template-capable narration blank merely because the story writer supplied no job proposal.

The story layer continues to own story meaning, exact spans, entities, claims, obligations, continuity and provenance. It does not select templates or decide template fit.

## Required stages and acceptance checks

1. **Preserve complete story input**
   - Consume every accepted narrator beat and claim, plus obligations, continuity, entity/cohort roles and optional job proposals.
   - Acceptance: no accepted narrator claim disappears before semantic splitting.

2. **Derive semantic VisualTask proposals in the matching layer**
   - Group adjacent claims when one developing treatment can communicate them; split when the subject, measure or communication job changes.
   - Treat source `jobProposals[]` as evidence that may inform a task, never as the only route into task production.
   - Derive a template-neutral presentation operation alongside the legacy communication job, including subject introduction/profile, relationship establishment, archival progression, evidence presentation, milestone reveal, sequence/list, comparison and data explanation. Do not force these operations into `pose_a_question` or the generic `assert_without_data` bucket.
   - Acceptance: one-to-many and many-to-one task relationships remain supported; task spans are exact and non-overlapping within their routed narration.
   - Acceptance: every operation is general and reusable across subjects; no operation names a template family or story-specific entity.

3. **Give every narrated span an explicit route disposition**
   - Allowed dispositions are template-eligible VisualTask, source-footage primary, B-roll, deliberate no-template/continuation, or a typed unresolved semantic gap.
   - Acceptance: no claim is represented only by `job_proposal_missing`; a typed unresolved result states the actual ambiguity that prevented routing.

4. **Preserve downstream ownership**
   - Data and media requirements attach after semantic task formation. Template retrieval and fit remain matching-layer responsibilities.
   - Acceptance: no derived task selects a template, media asset, treatment, or render authorization.

5. **Run general-purpose regression fixtures**
   - Run Future, Year Seventeen and Apollo through the same splitter code path without story-specific IDs or rules.
   - Acceptance: Future produces complete route coverage; Apollo preserves its one-claim/many-task and many-claim/one-task cases; Year Seventeen preserves reviewed task semantics.

6. **Replace the invalid Future gallery**
   - Supersede the current job-binding retrieval slate only after the corrected semantic tasks pass coverage checks.
   - Acceptance: the review UI presents candidates derived from complete task contracts and clearly distinguishes unresolved tasks, B-roll and no-template routes.

## Execution result — 2026-10-03

- Stages 1–5 passed for the review-only implementation.
- The same splitter path passes the Apollo, Year Seventeen and Future fixtures.
- Superseded count: the first complete-coverage pass produced 58 beat-sized task proposals. The systematic granularity pass now produces 311 task proposals: 308 matching-derived narrator tasks and three speaker-derived quote tasks, plus 36 source-footage-primary routes.
- All 502 claims have a route; `uncoveredClaims` is zero. The 43 remaining typed gaps concern the six already-known unidentified clip speakers, 36 missing clip end timings and one missing quote attribution source—not missing semantic jobs.
- The current gallery contains 4,969 retrieval-only candidate cards across 311 tasks. Every task has at least one candidate; candidate fit remains unvalidated.
- Superseded granularity result: the first corrected pass still collapsed `p01-1` into one five-claim task. Editor review established that this passage requires five independently selectable visual moments: linked identity setup, streaming stature, influence through rap, expanded pop-industry reach and the misunderstood-artist turn. The splitter now derives tasks within beats at claim/meaning changes and strong contrast pivots while retaining only closely linked setup/restatement pairs.
- The prior job-proposal-only task and gallery artifacts are retained with the suffix `diagnostic-job-proposals-only.json`.
- Stage 6 is complete as a review surface, not as candidate approval: the existing gallery now displays the corrected tasks and durable feedback controls. No selection or rendering authorization was created.
