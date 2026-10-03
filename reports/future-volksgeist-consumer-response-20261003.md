# Future Volksgeist StoryPackage consumer response

Date: 2026-10-03
Package: `future-volksgeist@2`
Pinned package commit: `b8dc0dbbe182bebacbabb366d66e89498d37db4b`
Package SHA-256: `3e0c681d00a24bb6ad35c2bc8d0dc27d8085f7b7f9c12bd754354ec1dc54f6a7`

## Corrected matching-layer result — 2026-10-03

The earlier consumer result below is retained as failure evidence. It incorrectly treated optional StoryPackage `jobProposals[]` as a coverage gate. The corrected matching-layer semantic splitter now consumes the complete accepted claim set and derives template-neutral presentation operations before candidate retrieval.

- 308 matching-derived narrator task proposals after same-payload claim grouping;
- three speaker-derived attributed-quote tasks;
- 36 source-footage-primary routes;
- all 502 claims routed, with zero uncovered claims;
- 311 template-eligible review tasks, all with retrieved candidates;
- 4,969 candidate cards in the practical review display;
- prior-story editor selections ignored for fresh-story retrieval order;
- candidate fit, selection and rendering remain unauthorized and unvalidated.

The 43 remaining typed gaps are unrelated to semantic task coverage: six unidentified clip speakers, 36 missing clip end timings and one missing structured quote-attribution source. The active review artifacts are `reports/storypackage-02-future-volksgeist-task-proposals.json` and `reports/storypackage-02-future-volksgeist-candidate-gallery.json`. The earlier job-only artifacts are preserved with the suffix `diagnostic-job-proposals-only.json`.

The initial correction over-grouped `p01-1` as one five-claim task. Editor review superseded that result: the opening now requires five independently selectable visual moments covering the linked identity setup, streaming stature, influence through rap, expanded pop-industry reach and the misunderstood-artist turn. This is enforced as a general matching rule: neither beat count nor claim count determines task count, same-payload adjacent claims may merge, strong scope expansions may split, and sibling task text must reconstruct the source beat exactly.

## Acceptance result

The authoritative checker accepts the package and reports the six supplied
`speaker_unidentified` gaps. The matching consumer preserves every
`beats[].speaker` object unchanged. It does not import any Year Seventeen
editor choice, review record, or task-scoped admission.

The generated review-only artifacts are:

- `reports/storypackage-02-future-volksgeist-adapter.json`
- `reports/storypackage-02-future-volksgeist-task-proposals.json`

## VisualTasks currently produced

The splitter currently produces 23 review-only task proposals:

- 20 source-provenanced `pose_a_question` proposals;
- 3 speaker-derived `attributed_quote` proposals, one for each quote beat.

It also produces 36 source-clip routes. These are deliberately not ordinary
template VisualTasks: the required source footage is the primary visual. A
lower third or name overlay may be matched later as an optional overlay, but a
template must not replace or illustrate the speaker's words.

This is not yet a complete match-ready VisualTask set. The package contains 328
narrator claims without a job proposal. The consumer abstains rather than
assigning those claims a job heuristically or borrowing a prior story's editor
choice.

## Speaker handling

| role | consumer route | template behavior |
|---|---|---|
| `narrator` or absent | semantic VisualTask proposal | eligible after a source-provenanced job/split exists |
| `clip` | `source_footage_primary` | not eligible for a replacement template; optional overlay only |
| `quote` | `attributed_quote_template` | creates an `attributed_quote` proposal; quote-card treatment is eligible |

`speaker.sourceTimestamp` is retained only as a source-video start locator. It
is never used as narration duration or clip-end timing.

## Rejections and required additions

1. **328 narrator claims lack a job proposal.** Full template matching is
   rejected until the Story-owned semantic split/job proposals cover them, or
   explicitly route them to no-template/B-roll.
2. **All 36 clip beats lack structured end timing.** Supply
   `sourceEndTimestamp` or `duration`. The start timestamp alone cannot define
   an edit.
3. **Quote beat `p02-13` lacks a structured attribution source.** The quoted
   entity is known, so a person attribution can be shown, but a source line
   cannot be authored from the current structured fields.
4. **Six clip speakers remain unidentified:** `p01-3`, `p02-10`, `p03-7`,
   `p04-4`, `p06-3`, `p07-7`. The exact source clips may still be used by
   locator; identity must not be guessed.
5. **No own-production timing exists.** Duration-fit matching remains
   unresolved until narration/clip timing is supplied.

No rejection invalidates the StoryPackage itself. These findings block only a
claim that the package already yields a complete, match-ready VisualTask set.

## Next acceptance step

Return a revised package or matching handoff containing the missing narrator
semantic jobs/splits and structured clip timing. The same generic adapter and
splitter can then produce the complete task set and begin template-family
candidate generation without using prior story-specific selections.
