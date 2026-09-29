# Branch classification and scene-mapping continuation

Date: 2026-09-28
Branch: `codex/treatment-requirements-review`
Activation: review-only; no matching selection or rendering authorization

## Objective

Complete the first realignment checkpoint, then improve exact clip-to-native-composition coverage using only existing semantic catalogs, frozen AE technical evidence and previously saved native evidence. Do not depend on the pending StoryPackage or shared-roster revisions.

## Stage 1: freeze the branch delta

Enumerate every path changed from `origin/main` through the current branch head. Classify each path as:

- production code;
- reusable schema/data;
- regression fixture;
- generated report/output;
- test;
- plan/documentation.

Record the branch base, head, changed-path count, exact path classifications and any known fixture-specific identifiers intentionally present in non-production artifacts.

Acceptance:

- every changed tracked path appears exactly once;
- the manifest rejects a changed path that is omitted or classified twice;
- the unrelated untracked `replacement-selection.json` is recorded as excluded user work and is not added;
- no fixture-specific identifier in production code remains unacknowledged.

## Stage 2: audit production code for fixture coupling

Scan changed production modules for current-documentary beat IDs, matching-issue IDs, review-document paths, pilot directory names and case-specific branching. Distinguish default file locations and generated-report labels from behavior-changing fixture logic.

Acceptance:

- every production-code hit receives a disposition;
- reusable code does not require current-documentary issue/review files at runtime;
- any remaining fixture-coupled behavior is listed as a blocker rather than silently called generic.

## Stage 3: reconcile unreviewed scene mappings

For each currently `unreviewed` scene in `grammar/ae-scene-composition-mappings.json`, compare:

1. semantic preview title, description and source timestamps;
2. exact hash-linked native project;
3. measured composition IDs, paths, durations and parent sequencing;
4. existing saved native screenshots/renders when already available.

Promote a scene to `verified` only when one native composition is uniquely supported by replayable evidence. Use `unresolved` with explicit candidates when evidence is ambiguous. Do not use project-level capacity as clip-level capacity.

Acceptance:

- all 46 starting `unreviewed` records receive an evidence-backed reviewed disposition;
- zero records are guessed from family names alone;
- mapping paths and IDs replay against the frozen technical index;
- rendering is not used unless existing evidence cannot answer a concrete remaining ambiguity and the established gate authorizes the narrow probe.

## Stage 4: rebuild and verify derived evidence

Rebuild the coverage ledger and VisualTask technical comparison from the reviewed mappings. Run the mapping, registry, coverage, comparison and matching-accuracy tests.

Acceptance:

- derived artifacts reproduce deterministically;
- verified, ambiguous, unreviewed and unlinked counts reconcile;
- the five-case matching accuracy batch remains green;
- no live picks, pairings, selections, media decisions or source templates change.

## Stop conditions

Ask the editor only when two or more native compositions remain visually plausible after all existing catalog, timeline and technical evidence has been exhausted, or when a new native probe would be required. Do not manufacture an answer to avoid the stop.

## Completion record

- Stage 1 complete: `reports/branch-classification-2026-09-28.json` classifies 79 branch/current-work paths exactly once and explicitly excludes the user-owned untracked replacement selection.
- Stage 2 complete: nine reusable production modules were separated from seven documentary/pilot-bound executable fixtures; every identified fixture-coupling hit has a recorded disposition.
- Stage 3 complete: the 46 starting `unreviewed` mappings became 29 newly verified mappings and 17 reviewed unresolved mappings. The subsequent exact window-capacity pass promoted eight reviewed subranges, so the registry now has 60 verified (52 whole-composition and eight clip-window), 13 unresolved and zero unreviewed mappings.
- Stage 4 complete: the technical comparison and clip-coverage ledger were rebuilt from the updated mappings. Exact test commands and results are reported at handoff; no rendering or source-template mutation was used.
