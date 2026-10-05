# Job 3 correction request

Status: **required before Job 4**  
Target artifacts:

- `reports/astra-root-cause/03-upstream-contract-fitness.md`
- `reports/astra-root-cause/03-upstream-contract-fitness.json`

Correct Job 3 only. Do not start Job 4 and do not modify production code,
schemas, grammar, evidence, gold references or earlier job outputs.

## Why the current PASS is not accepted

The published analysis contains valuable measured findings, but three parts do
not satisfy Job 3's existing output and acceptance contract.

### 1. Typed-gap owners use a value outside the allowed set

Job 3 requires typed gaps assigned to `story`, `data`, `media`, or `matching`.
The JSON assigns G-05, G-07 and G-11 to `shared`, then declares the ownership
acceptance check passed.

For each affected gap:

- choose one accountable `owner` from the allowed set;
- preserve cross-layer responsibility in a separate `dependencies`,
  `supportingOwners`, or equivalent field;
- update the Markdown table, JSON gap, attribution explanation and acceptance
  basis consistently;
- do not erase the evidence that another layer must supply or consume part of
  the contract.

The accountable owner should follow artifact ownership. For example, a missing
field in the Story-owned handoff schema can be owned by `story` while identifying
`data` as the supplier of the factual value and `matching` as its consumer.

### 2. G-05 contradicts its own naming claim

G-05 proposes a handoff property named `quantity` but says the delta reuses the
StoryPackage field names verbatim. The StoryPackage value object uses `value`,
not `quantity`.

Choose and justify one interoperable canonical name. If the proposal retains
`quantity`, stop claiming it is a verbatim reuse and define the required
projection from Story `value`. If it uses `value`, describe the direct copy and
any compatibility implications. Keep the proposal provider- and story-neutral.

### 3. G-07 does not yet meet the recurring-evidence requirement

The proposed `roundTo` and `roundMode` fields are measured across multiple
values, but all observed handoff values come from the one committed Year
Seventeen handoff. Structural recurrence inside one story is not the same as
recurring cross-story evidence.

Either:

1. cite independent recurring evidence from another package or editor-reviewed
   case that proves these exact fields are required; or
2. remove them from the accepted minimal contract deltas and preserve them as
   an unresolved hypothesis for later validation.

Do not invent evidence or treat the absence of another handoff as confirmation.

## Required validation

Before republishing:

1. Parse the corrected JSON successfully.
2. Assert every `typedGaps[].owner` is one of `story`, `data`, `media`, or
   `matching`.
3. Assert the G-05 proposed name and its naming rationale agree.
4. Assert every accepted proposed field cites recurring evidence beyond one
   story; otherwise label it unresolved and exclude it from accepted deltas.
5. Make the Markdown and JSON agree on gap owners, evidence status, proposed
   deltas and the acceptance verdict.
6. Confirm the diff modifies only the two Job 3 report artifacts and any
   necessary Job 3 receipt/status metadata.

Commit and push the corrected Job 3 artifacts to `fable_analysis`. In the final
response, provide direct GitHub links to the corrected Markdown, JSON and commit,
state the next job and blocker owner, and stop. Do not begin Job 4.
