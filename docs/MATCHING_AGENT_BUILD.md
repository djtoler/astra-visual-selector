# Matching Agent build handoff

**Status:** authorized build handoff for a new conversation  
**Repository:** `djtoler/astra-visual-selector`  
**Branch:** `matching-layer`  
**Matching authority at handoff:** commit `bed08f03eb2e517bf79e5864dfeadbf87a52e256`  
**Default model decision:** GPT is the default Matching-agent provider. The initial concrete profile is OpenAI `gpt-6-astra` through the Codex CLI. Provider, exact model, transport and effort remain configuration values, and alternate providers must implement the same contracts.

## 1. Objective

Build a provider-neutral Matching agent around the existing general Matching layer. The agent accepts any validated supported StoryPackage, runs the existing contract-enforced Matching pipeline, and returns schema-valid review artifacts and a hash-bound receipt.

The agent must not contain story-specific behavior, choose templates by remembering another story, invent Story/Data/Media facts, authorize a selection, authorize rendering, or replace deterministic Matching code with model judgment.

The default execution profile is GPT. A Claude or other provider profile is a replaceable runner over the same task contract, tools, validations and acceptance fixtures—not a fork of Matching rules.

## 2. Read before changing code

Read these files completely:

1. `AGENTS.md`
2. `README.md`
3. `grammar/general-matching-layer-contract.json`
4. `grammar/matching-entrypoint-contract.json`
5. `grammar/matching-harness-stage-contract.json`
6. `plans/general-matching-layer-tasks.json`
7. `reports/matching-harness-audit.json`
8. The coordinator's reconciled agent architecture on `djtoler/content-project-mgr`, branch `codex/agent-architecture-plan`, especially `AGENT_ARCHITECTURE_RECONCILIATION_CODEX_20261003.md`

Treat this branch as the active Matching implementation. Leave unrelated Claude-authored Matching code on its existing branches stale unless this branch records a concrete executable or contract dependency on it.

## 3. Existing system to wrap

Do not reimplement the matcher. The agent orchestrates these existing deterministic components:

- `pipeline/storypackage_adapter.py`
- `pipeline/storypackage_splitter.py`
- `pipeline/storypackage_candidate_gallery.py`
- `pipeline/storypackage_matching_handoff.py`
- `pipeline/storypackage_data_handoff.py`
- `pipeline/storypackage_data_assignment.py`
- `pipeline/visual_tasks.py`
- `pipeline/visualtask_matching.py`
- `pipeline/visualtask_batch_matching.py`
- `pipeline/ordered_visual_route_plan.py`
- `pipeline/matching_harness.py`
- `pipeline/matching_contract_gate.py`

Every invoked entry point must remain registered in `grammar/matching-entrypoint-contract.json` and must call the shared contract gate before consuming task content. Unknown entry points fail closed.

## 4. Ownership boundary

### Matching owns

- consuming validated StoryPackages and template-neutral VisualTasks;
- deriving generic presentation requirements when the Story contract permits it;
- structured template-capability admission;
- candidate ordering and explanation;
- template/media feasibility;
- b-roll fallback disposition;
- sequence, timing and transition planning;
- Matching artifacts and receipts.

### Matching does not own

- Story meaning, claims, narration boundaries, entities or continuity;
- Data truth, measurements, methods or caveats;
- Media identity, availability, rights or production readiness;
- final editorial selection;
- custom visual approval;
- rendering or publication.

Missing upstream information becomes a typed blocker owned by `story`, `data`, `media`, `matching` or `you`. Do not guess it.

## 5. Configuration contract

Create a versioned YAML agent profile. Environment variables may supply secrets, machine-specific locations, endpoints and explicitly declared overrides. No secret belongs in YAML, source control, logs or receipts.

Target shape:

```yaml
schema_version: matching-agent-profile@1
agent_id: matching
contract_version: general-matching-agent@1
active_profile: ${MATCHING_PROFILE:-openai_gpt}

profiles:
  openai_gpt:
    provider: openai
    model: ${MATCHING_OPENAI_MODEL:-gpt-6-astra}
    transport: ${MATCHING_OPENAI_TRANSPORT:-cli}
    reasoning_effort: ${MATCHING_OPENAI_EFFORT:-high}
    prompt_version: matching-agent-prompt@1
    tool_policy: matching-tools@1
    permission_policy: matching-review-only@1
    evaluation_profile: matching-cross-story@1

  anthropic_challenger:
    provider: anthropic
    model: ${MATCHING_ANTHROPIC_MODEL}
    transport: ${MATCHING_ANTHROPIC_TRANSPORT:-cli}
    reasoning_effort: ${MATCHING_ANTHROPIC_EFFORT:-high}
    prompt_version: matching-agent-prompt@1
    tool_policy: matching-tools@1
    permission_policy: matching-review-only@1
    evaluation_profile: matching-cross-story@1
```

Requirements:

- `openai_gpt` is the default profile.
- Initially use the installed Codex CLI; do not introduce an external API dependency merely to complete the first build.
- CLI/API/SDK transport differences stay behind a runner adapter.
- Unknown keys, unresolved required variables and unsupported profile combinations fail closed.
- Resolve configuration once per run and emit a redacted configuration receipt containing the resolved tuple and its digest.
- The configured tuple includes provider, model, served model when available, transport, reasoning effort, prompt version, tool policy, permission policy and evaluation version.

## 6. Provider-neutral runner

Use one logical interface:

```text
capabilities() -> capability_manifest
run(task_contract, workspace, agent_profile) -> run_handle
status(run_handle) -> run_state
steer(run_handle, message) -> acknowledgement
cancel(run_handle) -> cancellation_receipt
collect(run_handle) -> agent_receipt
```

Only expose an operation when the capability manifest supports it. The first implementation is a `CodexCliRunner`. Do not let runner-specific output become a Matching artifact without parsing and validating it against the shared schema.

The agent may reason about an ambiguous task or explain candidates, but deterministic code remains authoritative for:

- StoryPackage validation;
- entity-roster pinning and resolution;
- entry-point registration;
- candidate capability admission;
- contract and schema validation;
- cross-story regression checks;
- selection/render authorization flags.

## 7. Task contract

Each invocation must include:

- `taskId`, `objectiveId`, `owner` and `requestedBy`;
- exact StoryPackage path, repository commit and file digest;
- exact entity-roster commit, registry version and file digest;
- approved template-catalog identity and digest;
- optional typed Data and Media handoff artifacts with digests;
- expected output schema and destination;
- dependency receipt IDs;
- profile, prompt, policy and contract versions;
- tool allow-list and mutation scope;
- acceptance checks;
- timeout/retry class;
- whether user input is allowed or required.

Reject stale, incomplete, mutable-only or branch-name-only inputs. A branch may be recorded for provenance, but the execution binding is an exact commit and digest.

## 8. Output and receipt

Return structured artifacts rather than a conversational claim of completion. At minimum, the receipt records:

- resolved provider/model/transport and model actually served when the runner reports it;
- start/end time, wall time, usage and cost when supported;
- exact input commits, paths and hashes;
- output paths and hashes;
- commands/checks run and outcomes;
- MCP servers, skills, tools and permissions actually loaded when available;
- contract, prompt, policy and evaluation versions;
- status: `passed`, `failed`, `blocked` or `needs_review`;
- current blocker: `you`, `data`, `story`, `matching`, `media`, `coordinator` or `none`;
- exact missing input/action when blocked;
- warnings, typed gaps and invalidated downstream receipts;
- `selectionAuthorized: false` and `renderingAuthorized: false` for Matching review runs.

Unsupported telemetry must be recorded as unsupported/unavailable, never inferred.

## 9. One public end-to-end command

Add one contract-enforced command that accepts a task contract plus the selected profile and runs the supported StoryPackage-to-review pipeline. It should produce:

1. authority and digest preflight;
2. validated StoryPackage adapter output;
3. semantic split/VisualTask proposals;
4. typed Data/Media requirements and gaps;
5. structured candidate admissions;
6. ordered visual-route proposal with b-roll fallback;
7. candidate-review artifact;
8. harness audit;
9. agent receipt.

The public command must call existing modules rather than duplicate their logic. It must preserve partial artifacts on failure for diagnosis while marking the final receipt failed or blocked. It must not render.

## 10. Portability work required before acceptance

Remove machine-specific runtime assumptions from executable code. In particular, audit and replace hard-coded `/Users/...` paths in runtime modules with validated configuration or task-contract inputs. Historical reports may retain absolute paths as provenance; runtime defaults may not depend on them.

Test from a clean checkout with only declared inputs. The implementation is not portable merely because it works in the current workspace.

## 11. Build order

1. Inventory existing coordinator schemas and runners before creating anything new.
2. Freeze or adopt schemas for profile, capability manifest, task contract, run state and receipt.
3. Add YAML resolution, environment allow-listing and redacted configuration receipts.
4. Implement `CodexCliRunner` and its capability manifest.
5. Add the one public Matching-agent command over existing pipeline modules.
6. Remove executable hard-coded machine paths.
7. Add deterministic validation and failure-path tests.
8. Run the existing isolated suite and Matching harness.
9. Run the same agent path on the saved cross-story fixtures.
10. Run one new user-supplied untouched StoryPackage after the last reusable Matching change.
11. Save the evaluation and activation receipt for the GPT default profile.
12. Update the task list and documentation only after every acceptance check passes.

Do not start with plugins, an API server, a UI rewrite or a second provider. Those come after the CLI vertical slice passes.

## 12. Acceptance checks

The build is complete only when all of these pass:

- the default `openai_gpt` profile resolves without source edits;
- an alternate provider profile can be selected without changing domain code;
- every run is bound to exact input commits and hashes;
- every called Matching entry point enforces the shared gate;
- the end-to-end command works from a clean checkout with configured paths;
- malformed contracts, stale receipts and missing authorities fail closed;
- selection and rendering remain false;
- no package, subject, beat or candidate fixture identifier exists in reusable runtime decisions;
- prior-story choices cannot admit, suppress or order candidates for a new package;
- all narration claims are routed to a VisualTask, exact source clip/quote route, b-roll fallback or typed gap;
- candidate admission is supported by structured template capabilities;
- at least two regression packages and one untouched user-supplied package use the identical agent path;
- the full isolated test suite and Matching harness pass;
- the GPT profile has an exact evaluation/activation receipt;
- the final receipt names the current blocker correctly.

## 13. Existing validation commands

Preserve and run:

```text
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m pipeline.matching_harness build
python3 -m pipeline.matching_harness validate
```

Add tests for the agent runner and public command without weakening these checks.

## 14. First-conversation instruction

Start by auditing the repository and coordinator contracts against this document. Save an implementation plan mapping every required stage to code and acceptance checks before editing. Reuse existing contracts, runners and pipeline components where suitable. If a required coordinator schema or runner already exists, adopt it rather than creating a parallel format.

Continue until the build is complete or a concrete user/external decision is required. Every status response must identify exactly one current blocker. Do not claim completion from a successful model response; completion requires validated artifacts, receipts, the clean-checkout run and cross-story evidence.

