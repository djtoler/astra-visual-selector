# Master prompt — implement Astra P0–P2 with GPT-6.1 Sol

Copy the prompt below into the new conversation.

```text
You are implementing the first authorized repair slice of the general Matching
layer using GPT-6.1 Sol. Work in:

Repository: https://github.com/djtoler/astra-visual-selector
Branch: matching-layer
Handoff directory: docs/p0-p2-gpt-6-1-sol-handoff/

The editor explicitly authorizes implementation of Astra stages P0, P1 and P2
only. Continue sequentially through all three stages unless a real editor,
Story, Data or Matching blocker is reached. Stop after P2 and request editor
review. P3–P7, rendering, template/catalog changes, external provider spend,
custom visuals, a replacement architecture and new unsupported workflows are
not authorized.

FIRST ACTIONS — before editing:

1. Read the repository's AGENTS.md and media_workflows.md completely.
2. Read every file in docs/p0-p2-gpt-6-1-sol-handoff/ completely.
   `P0_FIXTURE_MIGRATION_AUTHORIZATION.md` contains the editor's scoped answer
   to the pending `28-28` replay blocker and is authoritative for that issue.
3. Verify the branch, working tree and every pinned hash in
   HANDOFF_MANIFEST.json. Do not silently continue from a different baseline.
   The default `../patterns-storypackage-review` checkout is dirty and is not at
   the pinned Story commit. Do not reset or modify it. Reuse an existing clean
   pinned checkout or create a separate non-destructive Git worktree at the
   pinned Story commit and set `STORYPACKAGE_AUTHORITY_ROOT` for checks that
   require the authority repository.
4. Read plans/ASTRA_MATCHING_REBUILD_PLAN.md and the Job 8 proposal, then read
   the Job 3, Job 6 and Job 7 reports and machine-readable companions listed in
   the manifest. Trace the actual existing code and tests named by the plan.
5. Inventory existing validators, contracts, projections, fixtures, test helpers
   and receipts before proposing any new file or abstraction. Existing systems
   and supported controls come first.
6. Save a stage-mapped implementation plan before changing production code.
   Map every P0–P2 acceptance check to an executable test, an existing component
   to reuse, and the intended receipt. State any exact capability gap. Do not
   replace an agreed stage with a shortcut.

GENERAL OBJECTIVE

Repair the provider-neutral general Matching layer so it can safely consume any
validated supported StoryPackage. Do not optimize for Future, Year Seventeen,
Jay-Z/Drake, a subject, beat ID or editor example. Those packages are calibration
or regression evidence only. Prior editor choices never admit, suppress or order
candidates for a new story unless a separately reconciled general rule and
versioned evidence explicitly support it.

MANDATORY ORDER

Implement P0, then P1, then P2. A downstream stage cannot pass on a missing,
stale or failed upstream receipt. For each stage:

- write or identify the failing regression/mutation tests first;
- demonstrate the frozen baseline failure and save its evidence;
- make the smallest change inside the existing architecture;
- run focused tests plus the relevant existing suite;
- verify immutable source/gold inputs and exact hashes;
- write a machine-readable stage receipt with inputs, outputs, versions,
  unresolved states, tests and rollback;
- commit the completed stage separately with no unrelated files;
- report what is next and name the blocker exactly as `you`, `data`, `story`,
  `matching` or `none`;
- continue automatically when the next authorized stage has no blocker.

P0 — FREEZE EVIDENCE AND EXECUTABLE FAILURES

Use the existing audit artifacts, context sidecars, fixtures and test harness.
Create a versioned calibration manifest and baseline/new outcome diff format.
Freeze exact evidence IDs, source hashes, effective catalog snapshot and author
scope. Do not regenerate or relabel the two gold references.

At minimum freeze executable baseline failures for:

- hashed-but-empty Data and Media handoffs being accepted as coverage;
- stale/mutated source or adapter receipts;
- template-ineligible/no-template route loss between consumers;
- task-contract field loss across requirements, gallery and focused review;
- subspan/scope/variant cases named by the Astra plan;
- the focused exploration tie: 58 of 59 audited focused tasks reached a
  frequency tie at the exploration cutoff, and the current secondary key can
  make admitted-list position decide among tied families.

The exploration-tie case is a P0 fixture for later P6 work. During P0–P2, prove
and preserve it; do not redesign ordering early. Accept only the verified core
finding. The interrupted Claude handoff and replay at commit
ae71e932cc475412ba701635eb671f759791b53c are supplementary evidence, not an
authority and not permission to import its unverified totals.

P0 passes only when the new fixtures demonstrably fail against the frozen
baseline for the intended reason, mutation controls fail closed, original
artifacts remain byte-identical, and the P0 receipt is reproducible.

For the historical `28-28` artifact specifically, follow
`docs/p0-p2-gpt-6-1-sol-handoff/P0_FIXTURE_MIGRATION_AUTHORIZATION.md`. The
editor authorizes a separately versioned deterministic fixture migration after
the original effective live inventory was found unrecoverable. Preserve the
legacy report byte-for-byte, bind the complete new fixture inputs, retain all
11 intended target failures and four integrity controls, and make no production
matching change during P0.

P1 — CONTENT- AND COVERAGE-VALIDATED BINDINGS

Strengthen the existing validators and consumer policy; do not replace the
supported StoryPackage or handoff schemas. A hash or structurally valid empty
object is not task coverage.

Required behavior:

- reject two hashed empty Data/Media objects as valid coverage;
- retain typed gaps for the audited 73 data-required and 104 media-required
  tasks instead of converting missing to zero or bound;
- reject field/source digest mismatch, stale adapter inputs and receipt/value
  mutation;
- accept a genuinely measured zero with valid source-bound evidence;
- bind coverage at the task and required-field level;
- preserve ownership: Matching does not invent Story meaning, Data facts or
  Media availability.

P1 passes only when its baseline failures are repaired, negative mutations still
fail, supported legacy inputs remain readable with explicit unresolved status,
and a P1 receipt binds all evidence and output hashes.

P2 — ONE SOURCE-BOUND TASK CONTRACT ACROSS CONSUMERS

Reuse current handoff/proposal fields and existing entrypoint gates. Define one
canonical source-bound task projection carrying at least route disposition,
primary and required meanings, obligations, continuity, values/cohorts,
media/data needs, quote attribution/required text and task-scoped admissions.
Migrate requirements, gallery and focused review together in a shadow/versioned
path before removing duplicate projection code.

Required behavior:

- all 12 audited template-ineligible route probes remain empty in gallery and
  focused review;
- quote attribution and required text survive while the question-versus-quote
  conflict is resolved from explicit obligations;
- mediaNeeds and cohort-media demand remain required;
- prior-story selections cannot enter a new task's input or ordering;
- no-template reason distinguishes intentional route, missing discovery and
  unresolved feasibility;
- every consumer binds the same projection version and source digest;
- omission, mutation, stale receipt or consumer reconstruction fails closed.

Do not implement P3 semantic splitting, P4 capability edits, P5 treatment
reconciliation or P6 ordering changes. If P2 cannot be completed without one of
those stages, preserve completed P0/P1 work, document the exact dependency and
stop with blocker `matching` or the correct upstream owner. Do not weaken P2.

NON-NEGOTIABLES

- No story-specific production branches, fixture IDs or subject names.
- No old editor choice as new-story admission or ordering input.
- No heuristic score, confidence or review label authorizes selection/rendering.
- No native-fit claim without task-bound evidence; unknown remains unknown.
- No custom renderer, template, visual or pipeline replacement.
- No direct AE/RLIS work and no rendering.
- No external model/API calls or paid actions without new explicit permission.
- Do not edit or regenerate source StoryPackages, gold references or editor
  evidence.
- Preserve unrelated user changes; do not reset or overwrite them.
- Follow the mandatory workflow-review checkpoint in AGENTS.md every turn.

VALIDATION AND DELIVERY

Run the narrow tests during iteration and the relevant complete existing suite
before each stage is declared complete. Use ACCEPTANCE_CHECKLIST.md as the
minimum, not the maximum. Record exact commands, results and known warnings.
Passing unrelated tests is not evidence that a required stage ran.

Push each completed stage to `matching-layer` with direct links to its commit,
receipt, tests and primary artifacts. After P2, produce a concise P0–P2 summary,
baseline-vs-new diff, remaining P3+ boundaries and rollback instructions. Stop
for editor review. Do not begin P3.
```
