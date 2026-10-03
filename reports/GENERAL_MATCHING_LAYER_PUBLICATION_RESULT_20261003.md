# General Matching Layer publication result

Date: 2026-10-03
Branch: `codex/general-matching-layer-v12`

## Scope

This branch packages the current provider-independent Matching implementation: mandatory contracts and entrypoint enforcement, StoryPackage adaptation and semantic splitting, structured template-capability retrieval, cross-story evidence, shared entity-registry consumption, Data/Media handoffs, ordered route/timing/release receipts, review artifacts, and their tests.

Claude-authored Matching implementation that is not an executable or contract dependency of this package was not refreshed or merged. It remains a stale baseline. Existing history was preserved; this publication imports no new Claude-only Matching implementation.

The user-owned `treatment-requirements/pilot-001/replacement-selection.json` is explicitly excluded.

## Acceptance results

- Active Matching package: 202 tests passed.
- Mandatory Matching harness: 20 tests passed.
- Exact StoryPackage authority handoff: passed against clean commit `d5117a6de0fd0c640a336c6f456946ec8b40f319`.
- Ordered route receipt: 41 scenes, 32 template-review routes, 9 b-roll routes, 0 deferred routes, 41 required transitions, 0 sequence conflicts.
- Prior editor-choice reconciliation: 32/32 routes resolved; no rendering authorization granted.
- Cross-story contract: four distinct packages, including a user-supplied held-out package, execute through the story-neutral runtime.
- Current harness state: automated stages are valid; `GML-14` remains an explicit editor-review boundary and reports `you` as the blocker.

## Full repository audit

The complete legacy repository suite ran 730 tests: 668 passed, 10 failed, 39 errored, and 13 skipped. Publication does not treat that suite as green. The failures are isolated from the active 202-test Matching package and fall into these preserved legacy/environment groups:

- source-bound AE catalog/window fixtures whose recorded hashes no longer match the current external template catalog;
- retired `3dz-charts` source expectations after the missing Blue project was removed from the active template pool;
- old fixed mapping-count and cached-source expectations;
- an environment-dependent R2 configuration assertion;
- one pre-canonical-roster partial-name tag expectation;
- the default dirty Story checkout, superseded in active validation by the exact clean pinned checkout.

Per the user’s direction, unused stale Matching-era behavior was not rewritten merely to turn these legacy checks green. The active package fails closed at its own contract boundaries and passes its complete targeted validation set.

## Authorization boundary

This publication packages matching and review evidence only. It does not select a new template, authorize a render, authorize custom visual construction, or authorize publication of media.
