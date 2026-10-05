# P0 fixture-migration authorization — 2026-10-05

## Decision

The editor authorizes a **versioned P0 fixture migration** for the historical
`28-28` replay case, subject to every constraint below. This authorization is
limited to making the P0 regression evidence deterministic. It does not
authorize changing production matching behavior, rewriting historical evidence,
or starting P1 before P0 passes.

## Why migration is necessary

The original replayable media state cannot be recovered from the available
artifacts:

- Historical artifact:
  `reports/visualtask-match-pilot-28-28.json`
- Historical artifact SHA-256:
  `f7328a5860113597fc51366eae61b076a405bfa2eb01c05df108f137da1b2e77`
- Artifact-producing commit investigated:
  `5f8068493bc402552f62bcad9b4200a58a1e0d3e`
- Checked-in media snapshot:
  `grammar/library-snapshot.json`
- Checked-in snapshot SHA-256:
  `14716d55a4e178f2f5cff9d172011e3ac56541eace9f75ee5be4328be510b867`

The checked-in snapshot contains the historical candidate IDs, but the
historical artifact does not replay from that snapshot at the historical commit.
The four available Media Library database backups from 2026-09-23 cannot be
paired honestly with the later delivery manifest: replay fails closed because
delivered assets are absent from those older catalogs. They therefore are not a
valid reconstruction of the original effective inventory.

This establishes that the historical export depended on live state that was not
fully pinned. Treat that as a provenance limitation of the legacy artifact, not
as permission to alter or discard it.

## Mandatory migration constraints

1. Preserve `reports/visualtask-match-pilot-28-28.json` byte-for-byte at the
   historical hash above. Label it legacy/non-replayable in new metadata only;
   do not edit or relabel the file itself.
2. Create a separately named, versioned replay fixture and manifest. Do not
   overwrite the legacy path and do not silently convert the old report into a
   new baseline.
3. Bind the new fixture to the complete effective media inventory, all grammar
   and policy inputs that influence candidate output, the code revision, and
   SHA-256 hashes. A database path or catalog name alone is insufficient.
4. Preserve the intended P0 assertions and the 11 frozen target failures. The
   migration may make the fixture replayable; it may not repair, hide, weaken,
   or reclassify those failures.
5. Preserve the four integrity controls and add a mutation check proving that a
   changed inventory or bound input invalidates replay.
6. Production behavior and production artifacts remain unchanged during P0.
   No matching-rule, candidate-ordering, Story, Data, Media, template, render,
   P3+, or provider change is authorized.
7. P0 passes only when the focused checks and the relevant complete existing
   suite pass, immutable source/gold hashes remain unchanged, and the P0 receipt
   records the migration lineage, commands, results, hashes, warnings, and
   rollback.
8. Do not start P1 until the passing P0 receipt is committed and independently
   reproducible from the repository.

## Required receipt statement

The P0 receipt must state plainly that the original `28-28` live media state was
not recoverable, that the old report is preserved as historical evidence, and
that the new fixture is a versioned deterministic migration—not a claim that the
legacy export replayed from fully frozen inputs.

## Resume instruction

Resume P0 from the pending receipt. Apply the smallest fixture-only migration
that satisfies this authorization and the existing handoff checklist. Continue
automatically to P1 only after P0 passes. Report the blocker each turn as one of
`you`, `data`, `story`, `matching`, or `none`.
