# General Matching Layer publication plan

Date: 2026-10-03

## Objective

Package the current general beat-to-template Matching implementation, its cross-story fixtures, durable decisions and validation evidence into one reviewable Git branch in `djtoler/astra-visual-selector` without overwriting unrelated user work or implying render authorization.

## Required stages and acceptance checks

1. **Inventory and scope freeze**
   - Record all modified and untracked files.
   - Include Matching contracts, harnesses, StoryPackage adapters, semantic splitting, candidate retrieval, data/media handoffs, timing/release planning, tests, plans and durable reports.
   - Exclude `treatment-requirements/pilot-001/replacement-selection.json`, which predates this package and was previously identified as user-owned review state.

2. **Dedicated branch**
   - Create `codex/general-matching-layer-v12` from the current Matching history.
   - Preserve existing remote branches and commits.

3. **Dependency-only legacy intake**
   - Do not merge or refresh Claude-authored Matching work merely because it exists on another branch.
   - Treat Claude-only Matching implementation as a stale baseline unless the current general matcher has a demonstrated runtime or contract dependency on a specific component.
   - Preserve required dependencies already present in current history, but do not import unrelated stale implementation.
   - Integrate the canonical shared registry through the current general-matcher contract without restoring a second roster authority.

4. **Static validation**
   - Every added or modified JSON file parses.
   - Python modules compile.
   - `git diff --check` passes.
   - No obvious credential material or oversized generated binary is staged.

5. **Behavioral validation**
   - Run the complete repository unit-test suite.
   - Run the mandatory Matching harness and contract audit.
   - Run cross-story tests covering the current StoryPackages and registry-v12 binding.
   - Any failure blocks publication until fixed or explicitly documented as an external dependency.

6. **Publication receipt**
   - Save the exact included/excluded paths, commands, outcomes and resulting commit.
   - Commit only after all required checks pass.
   - Push the dedicated branch and verify the remote head.

## Non-goals

- No template selection or editor-choice fabrication.
- No rendering or custom visual construction.
- No modification of Story, Data, Media or registry authority.
- No inclusion of unrelated user-owned review state.
