# Matching Agent implementation plan

**Date:** 2026-10-04  
**Authority:** `docs/MATCHING_AGENT_BUILD.md`  
**Branch:** `matching-layer`  
**Current blocker:** `external_provider_payload_authorization`

## No-deviation assessment

This build wraps the existing deterministic Matching layer. It does not replace candidate admission, StoryPackage validation, entity-roster validation, the Matching contract gate, or the Matching harness with model judgment. It does not select a template or authorize rendering. The coordinator architecture is adopted as the lifecycle and receipt authority; the coordinator branch contains architecture documents but no reusable executable schema or runner implementation at audit time, so this repository must freeze the Matching-owned instances of those contracts.

The versioned profile is stored as JSON-compatible YAML. JSON is a strict YAML subset and can be parsed with the Python standard library, avoiding an undeclared PyYAML dependency while preserving a `.yaml` configuration surface.

## Stages, implementation mapping, and acceptance checks

| Order | Required stage | Implementation mapping | Acceptance check |
|---:|---|---|---|
| 1 | Inventory coordinator schemas and runners | Record coordinator audit in this plan; reuse the reconciled lifecycle and telemetry fields | No duplicate coordinator runtime exists; adopted fields are traceable to `AGENT_ARCHITECTURE_RECONCILIATION_CODEX_20261003.md` |
| 2 | Freeze agent contracts | Add JSON Schemas for profile, capability manifest, task contract, run state, model review, and receipt | Schema fixtures accept valid examples and reject missing, unknown, mutable-only, or authorization-bearing inputs |
| 3 | Resolve YAML profile | Add strict profile resolver and `config/matching-agent-profiles.yaml` | Default `openai_gpt` resolves without source edits; alternate profile selection changes no domain code; unknown keys/variables/combinations fail closed; redacted tuple digest is stable |
| 4 | Implement provider-neutral runner | Add runner protocol and `CodexCliRunner` using the installed Codex CLI, read-only sandbox, structured output schema, and capability discovery | Fake-CLI tests cover run/status/collect/cancel and unsupported steering; runner output is parsed and schema-validated before admission |
| 5 | Add public end-to-end command | Add one registered contract-enforced command that performs immutable preflight, invokes existing adapter/splitter/gallery/handoff/harness components, writes partial artifacts atomically, and emits a final receipt | The same command produces adapter, proposals, typed gaps, candidate admissions, ordered review route, candidate review, harness audit, and final receipt; selection/render flags remain false |
| 6 | Remove machine-specific executable defaults | Replace runtime `/Users/...` assumptions in invoked code with task-contract/config inputs; historical reports remain provenance | Runtime Python source scan has no `/Users/`; clean-checkout execution uses declared authorities only |
| 7 | Add failure-path tests | Test malformed contracts, moved commits, digest mismatch, stale dependency receipts, unsupported runner combinations, invalid model output, and partial-artifact preservation | Every invalid case fails closed with a typed blocker and no selection/render authorization |
| 8 | Preserve existing validation | Run the full isolated suite plus Matching harness build/validate | Existing checks pass, except any independently reproduced baseline external-authority mismatch must be resolved or recorded with exact evidence |
| 9 | Cross-story evaluation | Run two saved regression packages and the preselected untouched user-supplied held-out package through the identical public command | Exact commits/hashes, complete claim routing, capability-backed admissions, and package-neutral runtime scan pass |
| 10 | Clean-checkout proof | Clone or worktree the final commit, supply only declared inputs, and rerun the public command and tests | No ambient path dependency; output receipt binds the clean checkout and declared authorities |
| 11 | Activate GPT default | Save evaluation and activation receipts for the exact provider/model/transport/effort/prompt/tool/permission/evaluation tuple | Receipt reports configured and served model when available, unsupported telemetry explicitly, current blocker, exact checks, and false authorization flags |
| 12 | Close objective | Update the agent task list and documentation only after all prior checks pass | Every task has a current receipt; no pending automated acceptance stage is mislabeled complete |

## Baseline evidence

- Matching checkout was clean at `cccb07a9a08ca50229d73c9e4e8eaf672400feb9` on branch `matching-layer`.
- Installed runner: `codex-cli 0.153.4`.
- PyYAML is not installed; JSON-compatible YAML avoids adding a dependency.
- The pre-edit isolated suite ran 185 tests with one baseline error: the configured StoryPackage authority checkout was not at the pinned commit in `test_storypackage_matching_handoff`. This is an external checkout-state mismatch, not an agent-build test failure, and must be retested with the pinned authority before final acceptance.
- The coordinator branch `codex/agent-architecture-plan` contains architecture documents only; it has no executable runner or frozen agent schemas to import.

## Output boundary

All generated Matching-agent outputs are review artifacts. Every schema and receipt must carry `selectionAuthorized: false` and `renderingAuthorized: false`. Rendering is out of scope and prohibited by the branch policy.

## Acceptance evidence

- The isolated suite passes all 198 tests when the pinned StoryPackage authority and shared entity roster are declared.
- Matching harness build and validation pass with `currentBlocker: none`, `productionAllowed: false`, and the expected first downstream boundary `render_release_handoff`.
- Two regression packages and the untouched `jayz-drake-settle-it@4` held-out package passed the identical public command with GPT configured as `gpt-6-astra`; all claims were routed and all selection/render authorization flags remained false.
- A detached clean checkout at `96363a637421ba24d8f9375f6932bb9958729c90` passes the full 198-test suite and Matching harness without modifying the checkout.
- The final duplicate provider call from that clean checkout did not run. The execution boundary rejected transmission of the compact review manifest because it still contains pinned repository identifiers, commits, digests, and evaluation metadata. Explicit user authorization for that payload is the only remaining acceptance decision; no workaround was attempted.
