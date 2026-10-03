# Shared entity roster migration

Matching no longer owns a separate artist gazetteer. Its only live roster
configuration is `entity-roster-source.json`, which pins the exact commit,
digest, registry ID and registry version of the canonical document in
`djtoler/entity_roster`.

`entity-roster-reconciliation.json` is retained as historical migration
evidence for the 2026-10-03 comparison. It is not a runtime registry and must
not be used to recognize, resolve or mint entities. The canonical repository's
`migration-receipt-20261003.json` records the completed v10 + Matching merge.

At runtime, set `SHARED_ENTITY_ROSTER_PATH` to a checkout of
`entity_roster/entity-roster.json`, or keep the repositories as siblings under
the Polish workspace. `pipeline.entities.roster()` verifies the source manifest
before exposing canonical names, aliases, stable IDs and entity types.

Unknown narration surfaces remain typed gaps. Matching recognition never mints
an entity ID; additions and alias-state changes must be reviewed and published
through the canonical registry repository.
