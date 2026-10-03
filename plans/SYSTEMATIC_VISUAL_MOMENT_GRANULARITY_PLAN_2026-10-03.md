# Systematic Visual-Moment Granularity Plan — 2026-10-03

## Objective

Make multi-moment narration splitting a reusable matching-layer stage for every accepted StoryPackage. A source beat must never become one template decision merely because it is one beat, and a claim must never become one VisualTask merely because it is one claim.

## Required stages and acceptance checks

1. **Keep StoryPackage ownership semantic and template-neutral**
   - Story owns exact script, beat/claim spans, atomic propositions, entities, obligations, continuity and provenance.
   - Story does not choose task count, templates, media, fit or rendering.
   - Acceptance: StoryPackage guidance explicitly says claim boundaries are split evidence, not VisualTask boundaries; compound independently assertable propositions should be separate claims where possible.

2. **Derive visual moments in matching**
   - Matching groups adjacent claims when one developing treatment can communicate one visual payload and separates them when the subject, measure, evidence mode, comparison, sequence, reveal or rhetorical function changes.
   - A strong scope expansion inside a claim may create multiple tasks. Punctuation, sentence count, duration and template capacity alone never create a split.
   - Acceptance: the implementation contains no story IDs or story-specific entity names; the Future opening resolves to five tasks from general rules.

3. **Preserve exact complete source coverage**
   - Every derived narrator task carries an exact source span and exact source text.
   - Sibling task spans are ordered, contiguous, complete and non-overlapping across their source beat.
   - Acceptance: concatenating task text reconstructs the source beat exactly; any gap, overlap or altered quote fails.

4. **Retrieve independently per task**
   - Candidate retrieval receives only that task's quote, operation, entities and requirements.
   - Acceptance: a multi-task beat creates distinct review cards and candidate slates; no slate is copied from the parent beat.

5. **Run cross-story regressions**
   - Run Future, Apollo and Year Seventeen through the same code path.
   - Acceptance: complete claim routing remains zero-gap, Apollo's explicit one-to-many and many-to-one proposals survive, and no story-specific rule is introduced.

6. **Remain review-only**
   - Granularity and candidate results are proposals for editor review.
   - Acceptance: selection and rendering authorization remain false; no render is started.

## Execution result

- StoryPackage producer guidance now requires independently assertable claims where exact subdivision is possible while explicitly preserving claim/VisualTask separation. No schema field assigns shots or templates.
- The matching splitter contains no Future identifiers. It groups same-payload adjacent claims and splits a compound scope expansion without using punctuation alone as the rule.
- The Future opening produces five tasks and their exact task text concatenates to the original narration byte-for-byte at the Unicode text level.
- Future, Apollo and Year Seventeen use the same implementation. Future routes all 502 claims with zero uncovered claims; Apollo retains its explicit one-claim/many-task and many-claim/one-task proposals.
- The active Future gallery contains 311 review tasks and 4,969 retrieval-only candidate cards. All remain unvalidated and review-only; selection and rendering authorization are false.
- Fifty matching/StoryPackage tests and thirteen review-storage tests pass. The upstream StoryPackage mutation checker also passes all 17 negative mutations. The separate Year Seventeen matching-handoff mutation suite remains stale against its pre-existing changed VisualTask receipt and was not represented as passing.
