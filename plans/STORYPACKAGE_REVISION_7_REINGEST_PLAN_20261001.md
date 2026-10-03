# StoryPackage Revision 7 reingest

## Objective

Reingest `year-seventeen@7` through the existing StoryPackage path and consume the new
matching handoff as the story-owned source of task linkage, media presentation, on-screen
text, and data-presentation requirements. This is review-only work; it does not select a
template, approve a treatment, or authorize rendering.

## Required stages and acceptance checks

1. **Validate the upstream authority and artifacts.** Run the upstream StoryPackage and
   matching-handoff checkers plus both negative suites at commit `66992e7`. Acceptance:
   the package and handoff pass against the exact pinned Astra snapshot, and every negative
   mutation is rejected.
2. **Repin and re-run the existing StoryPackage adapter/splitter.** Acceptance: the adapter
   consumes `year-seventeen@7`, the splitter covers the current reviewed task scope, and
   their source/checker receipts are fresh.
3. **Add the matching-handoff adapter.** Acceptance: the upstream handoff checker runs
   before normalization; all 41 task records and all three typed unresolved items survive;
   selection, treatment approval, and rendering stay false.
4. **Feed the handoff into the existing full-task matcher.** Overlay the story-owned media,
   text, and data-presentation requirements in memory, preserving the technical and data
   layers' own fields. Acceptance: every current task has one handoff record; focal unknowns
   remain unknown; story fields reach candidate/media checks; no source grammar is rewritten.
5. **Run downstream consumers.** Rebuild and replay-validate the full batch report, then
   rebuild and validate the matching harness. Acceptance: source receipts are fresh, stage
   ordering is unchanged, and production/selection/rendering remain denied.
6. **Record system state.** Update the integration task ledger, `SYSTEM.md`, no-drifting log,
   and mandatory workflow checkpoint with measured results.

## Known upstream unresolved items

- `13-13b` second clause has no VisualTask.
- `30-30a.main` has an unknown number of pre-streaming focal artists.
- 66 claims outside the 40 reviewed beats have no VisualTask.

These remain visible gaps. Reingest must not invent tasks, counts, or approval to clear them.
