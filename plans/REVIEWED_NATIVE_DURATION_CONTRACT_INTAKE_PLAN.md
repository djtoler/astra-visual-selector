# Reviewed native-duration contract intake plan

Date: 2026-09-30
Status: authorized implementation scope

## Objective

Complete the post-render timing diagnostic for reviewed After Effects clips that are
not present in the older approved catalog. Derive timing-only contracts from the
existing review catalog, verified scene-to-composition mappings, exact clip windows
where present, and the source-bound technical index. Do not promote clips into the
approved catalog, render media, mutate After Effects, or infer missing evidence.

## Required stages and acceptance checks

### 1. Identify only the current contract gaps

- Read candidate IDs from the existing VisualTask comparison and subtract scenes
  already covered by the approved catalog.
- Acceptance: repeated candidate placements share one derived contract record and
  no unrelated review-catalog scene is promoted.

### 2. Bind reviewed and native evidence

- Require `available_for_use`, a usable reviewed scene boundary, a settled boolean
  transition requirement, and no pending transition review.
- Require a verified native mapping and an exact measured composition. For a
  `verified_window` mapping, require its exact saved window and use that duration;
  otherwise use the mapped composition duration.
- Acceptance: project, composition ID/path and source project hash agree across the
  mapping/technical evidence; any absent or contradictory fact remains unresolved.

### 3. Build timing-only contracts

- Set post-render retiming from the already authorized timing policy, preserve the
  reviewed transition requirement, and retain evidence provenance on every record.
- Acceptance: the derived native duration equals the comparison's independently
  saved native-duration observation; no selection or rendering authorization is
  introduced.

### 4. Rebuild and verify the diagnostic

- Extend the timing report with source hashes, contract-intake counts and per-scene
  evidence outcomes.
- Acceptance: all currently evidence-complete gaps calculate deterministically;
  synthetic missing, stale, approximate or conflicting evidence remains unresolved;
  focused tests pass and a second report build is byte-identical.
