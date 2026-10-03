# Entity roster reconciliation

The Matching roster and Data entity-context registry are intentionally different contracts. `entity-roster.json` remains the compact Matching gazetteer. The Data registry remains authoritative for stable entity IDs, types, reviewed alias state, evidence and story bindings.

`entity-roster-reconciliation.json` is the deterministic bridge evidence. It was produced by `tools/reconcile_entity_rosters.py` from the exact pinned branches and commits recorded inside the report.

Current result:

- 309 Data entities and 308 Matching names were inspected.
- 164 identities align: 163 by normalized canonical name and Big Pun through the explicit `Big Pun -> Big Punisher` Matching alias.
- 145 Data entities require Matching-scope review; organizations remain Data context unless a VisualTask requires them.
- 144 Matching names require Data entity-resolution review.
- 11 aligned identities use different canonical display spelling.
- No normalized-key collision, invalid Matching alias or Data alias collision was found.

The bridge does not automatically modify either roster. Promotions require the owning layer to publish a reviewed update and a new version/receipt.
