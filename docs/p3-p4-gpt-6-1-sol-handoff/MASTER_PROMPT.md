# Master prompt — implement Astra P3 and P4 with GPT-6.1 Sol

```text
Continue the general Matching-layer repair on:

Repository: https://github.com/djtoler/astra-visual-selector
Branch: matching-layer
Verified P0-P2 head: 5bff1156fe26855a5c9988ff023ee304f961e0f2

EDITOR AUTHORIZATION

On 2026-10-05, after independent validation of P0-P2, the editor explicitly
approved continuing with P3 and P4. This authorization supersedes only the
earlier stop-after-P2 boundary. P5-P7, rendering, template creation, catalog
redesign, external provider/API spend, and unsupported schema extensions remain
unauthorized.

PRECONDITIONS

1. Pull the latest matching-layer branch and verify HEAD includes 5bff115.
2. Read AGENTS.md and media_workflows.md completely.
3. Read plans/ASTRA_MATCHING_REBUILD_PLAN.md, especially P3 and P4.
4. Verify P0, P1 and P2 receipts with tests/verify_astra_stage.py and preserve
   all frozen evidence, expected failures and source/gold hashes.
5. Save a P3/P4 implementation plan mapping every acceptance requirement to an
   existing component, a failing test, a repair, and a receipt. Inventory all
   existing semantic-split, capability, correction, catalog, intake and native
   evidence systems before proposing anything new.

AUTHORIZED WORK

P3 — repair semantic moment materialization and proposal review.

- Materialize exact rate/value subspans without omitted or invented words.
- Do not interpret repeated mentions of one subject as comparison or plurality.
- Do not merge different measures or roles merely because they share a subject;
  preserve coherent rank/cohort tasks where the evidence supports one task.
- Ensure lexical counterprobes such as headliner, left floor and fans cannot
  override source-supported meaning.
- Provider proposals remain review-only: they cannot change facts, select
  templates, erase unknowns or activate without schema and coverage checks.
- Preserve exact claims, spans, relationships, units, participants, rationale,
  required meanings and unresolved alternatives.

P4 — repair existing capability and scope representation.

- Keep timeline capability timeline-only while making it retrievable for valid
  chronological intent.
- Keep missing spatial or lyric evidence unresolved; never invent capability to
  improve recall.
- Optional numeric text does not imply mandatory data encoding.
- Qualitative variants require supported-control evidence.
- Keep reduction-versus-all-at-once contradictions unresolved until reviewed.
- Stale mappings must invalidate fit evidence.
- Preserve observed demo, declared supported range, verified controls and scoped
  restrictions as distinct evidence classes.

P3 and P4 are independent after P2/P0 respectively and may be worked in
parallel, but they must remain separate reviewable commits and receipts. Do not
begin P5. P5 depends on both and requires a new editor checkpoint.

EXISTING-SYSTEM AND SCHEMA BOUNDARY

Repair and connect existing components first. If current supported schemas and
controls cannot express a required meaning or capability distinction, do not
silently extend them. Document the exact exhausted options, counterexample,
smallest proposed versioned delta, migration impact and tests, then stop for
editor approval on that delta. Unknown remains unknown.

IMPLEMENTATION ORDER AND EVIDENCE

For each stage:

- write the regression and mutation tests first;
- demonstrate the intended frozen failure;
- make the smallest general, source-neutral repair;
- prohibit story IDs, subject names or prior selections from production logic;
- run focused tests and the full relevant suite with the pinned Story authority
  and shared entity roster paths;
- preserve the four later-stage expected failures unless the current authorized
  stage owns the specific failure;
- produce a machine-readable receipt binding its upstream receipt, exact input
  and output hashes, code revision, commands/results, unresolved states and
  rollback;
- commit and push P3 and P4 separately;
- state what is next and name the blocker as you, story, data, media, matching or
  none.

NON-NEGOTIABLES

- General Matching layer only; no package-specific runtime rules.
- No prior editor choice may admit, suppress or order candidates for a new story.
- No confidence or heuristic score authorizes selection or rendering.
- No template, catalog or native-fit claim without source-bound evidence.
- No rendering, AE/RLIS work, custom visuals or new renderer.
- No external model/provider/API execution or spend without new permission.
- Do not edit source StoryPackages, gold references or historical reviews.
- Do not weaken P0-P2 contracts or make tests pass by relabeling unresolved state.

STOP CONDITION

After both P3 and P4 independently pass, push their receipts and a combined
baseline-versus-new summary, then stop for editor review. Do not start P5.
```
