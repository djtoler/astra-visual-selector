# Matching Layer

This branch is the active, single-purpose implementation of the general StoryPackage-to-template Matching layer.

It accepts validated supported StoryPackages, extracts template-neutral visual tasks, admits candidates through structured template capabilities, keeps Data and Media requirements typed and separate, preserves b-roll as a valid route, and fails closed at contract and render-release boundaries.

## Active authority

- Repository: `djtoler/astra-visual-selector`
- Branch: `matching-layer`
- Frozen source publication: `codex/general-matching-layer-v12` at `e8818ae1f3e56f42d36d111bcc8b8c8aaa73e2d6`
- Claude-authored Matching branches are stale baselines unless this branch records a concrete executable or contract dependency on a specific component.

## What belongs here

- Matching contracts and enforcement
- StoryPackage adapters and semantic splitting
- VisualTask extraction and structured candidate retrieval
- shared entity-registry consumption
- typed Data and Media handoffs
- timing, sequence, human-review and render-release receipts
- cross-story fixtures and tests needed to prove the same runtime works across stories
- durable Matching decisions and operating memory

Template intake systems, render implementations, old review UIs, bulk treatment drafts, archived experiments, and unrelated source-bound calibration batches do not belong here.

## External authorities

The branch consumes, but does not duplicate or replace:

- StoryPackage specification and checker from `djtoler/patterns`
- the canonical registry from `djtoler/entity_roster`
- Data assignments from the Polish data layer
- production-ready media metadata from the Media layer
- the approved template catalog from `ae-template-automation`
- coordinator contracts from `djtoler/content-project-mgr`

External locations are configurable where the runtime exposes an environment variable. Their identity and digest must remain visible in generated receipts.

## Validation

Run the isolated suite:

```text
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m pipeline.matching_harness build
python3 -m pipeline.matching_harness validate
```

The exact StoryPackage authority test also accepts `STORYPACKAGE_AUTHORITY_ROOT` pointing to a clean checkout of the pinned authority commit.

## Matching agent

The authorized provider-neutral Matching-agent handoff is [docs/MATCHING_AGENT_BUILD.md](docs/MATCHING_AGENT_BUILD.md). GPT is the default profile; provider-specific runners must preserve the same Matching contracts, deterministic gates and cross-story acceptance path.

The implementation uses the JSON-compatible YAML profile at
`config/matching-agent-profiles.yaml` and one public command:

```text
python3 -m pipeline.matching_agent run --task /absolute/path/to/matching-agent-task.json
```

The task must bind the StoryPackage, shared entity registry, approved template
catalog, dependency receipts and output scope to exact commits and SHA-256
digests. The command writes partial diagnostic artifacts as stages complete and
finishes with `matching-agent-receipt.json`. Its Codex runner is read-only; only
the orchestrator writes inside the task's declared output scope. A Matching-agent
receipt never authorizes template selection or rendering.

## Authorization boundary

Matching output is review evidence. It never silently authorizes a template selection, custom visual, render, or media publication.
