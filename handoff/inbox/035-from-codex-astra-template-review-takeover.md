# HANDOFF 035 — Claude resumes Astra template/media review work

Date: 2026-09-25
From: Codex
To: Claude

## Scope boundary

Resume the Astra template-selection/review task only. Codex is separately handling the new `latest_09-25-26` media-treatment automation. Do not mix that folder-processing task into this one.

## Read first

1. `/Users/dwaynetoler/timeline/STEPS.md`
2. `/Users/dwaynetoler/timeline/CLAUDE.md`
3. `/Users/dwaynetoler/timeline/no-drifting/LOG.txt`, especially entries 0101–0104
4. `/Users/dwaynetoler/timeline/grammar/astra-media-review-recovered-decisions-2026-09-25.json`
5. `/Users/dwaynetoler/timeline/grammar/media-corrections.json`
6. `/Users/dwaynetoler/timeline/pipeline/media_candidates.py`
7. `/Users/dwaynetoler/timeline/pipeline/build_media_review.py`

## Preserved user work — do not redo or reinterpret

- The failed localhost review was recovered before the page was changed.
- 173 live W corrections were reconstructed and replay-verified across every tier.
- 29 user notes were preserved verbatim.
- Those corrections were merged with 28 earlier corrections for 201 unique durable entity-scoped corrections.
- The pre-merge file remains at `grammar/media-corrections.pre-live-recovery-2026-09-25.json`.
- Keep the 74 still-valid prior media picks. Two prior picks are explicitly displaced by the authoritative Production Ready boundary and require replacement; do not silently restore them.

## Template state

- `grammar/picks.json` template IDs match the template IDs recorded in `grammar/media-briefs.json`; the bad-looking review was not evidence that the refined template choices had been replaced.
- The problem to resume is the review presentation and eligibility context: several selected templates lacked usable preview presentation, so the page made correct selections look wrong or absent.
- Six selected IDs were observed without presentation previews in the current cache. Treat missing preview evidence as missing evidence, not as permission to substitute another template.
- Lettered beat sides are distinct decisions. For example, `02-02a` and `02-02b` must stay visibly paired while retaining separate narration, intent and media selections.
- Existing cached source-template clips/posters must be shown beside each beat. Never use a still as the thing being judged when a template clip exists.

## Media matching state relevant to this review

- `/Users/dwaynetoler/Media Library/50_COMPLETED/Production Ready/manifest.json` is the exact selectable lifecycle boundary.
- Identity evidence now has a hard fallback boundary: Production Ready identity, named face and non-project content tags are primary. Captions, titles and ingest/project labels are allowed only when no primary identity candidate exists for that entity.
- The non-published verification build changed 470 to 337 card slots and 227 to 172 distinct assets, removing all caption/project/unknown-evidence cards from entities that already had primary identity evidence.
- Full Timeline suite passed 351 tests with two skips after this change.

## Next work

1. Convert the 29 preserved user notes into explicit beat/template eligibility rules only where the note deterministically supports such a rule. Keep the verbatim note and attribution beside every derived rule.
2. Prove each rule changes the intended candidate/eligibility outcome with a failing-before/passing-after test and record it in `no-drifting/LOG.txt`.
3. Rebuild the existing review consumer with the original refined template picks and real cached template previews. Do not reselect templates, fabricate previews, or create a replacement design.
4. Ensure review decisions persist before inviting another user review. A local-only page must not present itself as durable.
5. Run the actual downstream consumer and inspect the resulting review page before reporting it ready.

## Non-negotiable gates

- Preserve the established six-choice/template-selection rules and native-template gates.
- No custom render, template substitution or invented approval.
- Missing or unverified preview/capability remains visibly flagged.
- Do not make the user repeat recovered decisions.

## Acceptance evidence to report

- Exact count of preserved picks, corrections and notes consumed by the rebuilt review.
- Before/after candidate or eligibility change for each newly encoded note-derived rule.
- Template preview coverage: selected IDs, posters, playable clips and genuinely missing previews.
- Full test result and the output of the downstream review consumer.

