# Provider-independent semantic split proposal plan

Date: 2026-09-30
Status: authorized implementation; review-only and not connected to matching

## Objective

Replace the documentary-specific split-draft producer with a reusable proposal
boundary for unseen stories. The stage accepts a versioned StoryPackage, closed
task vocabulary, roster references and story-scoped editor context; it prepares a
provider-neutral request and validates an externally supplied structured response.
It does not call a model, approve a proposal, create active VisualTasks, select a
template or authorize rendering.

## Required stages and acceptance checks

### 1. Validate versioned inputs

- Require version 1, review-only StoryPackage, vocabulary, roster and editor-context
  artifacts with closed object shapes.
- Validate distinct beat IDs/ordinals, known entity/cohort/context references and
  story namespace ownership.
- Acceptance: malformed, cross-story, unknown or activation-bearing input fails
  before a proposal request is prepared.

### 2. Prepare a provider-neutral request

- Bind all four input files by path, SHA-256 and bytes.
- Expose only the closed beat evidence, vocabulary, roster references and applicable
  editor context needed to propose visual tasks.
- Acceptance: no provider/model field, current-documentary issue identifier or
  matching-catalog decision is required; identical inputs produce identical bytes.

### 3. Validate an externally supplied proposal

- Require one proposal for every beat, one or more tasks per proposal, one visual
  job and takeaway per task, exact character spans and exact source quotes.
- Require spans to be ordered, contiguous, complete and non-overlapping, including
  whitespace and punctuation. Require vocabulary and roster/context references to
  resolve and source truth/prohibition/data requirements to remain allocated.
- Acceptance: gaps, overlaps, reordered spans, unknown references, extra fields or
  stale request/source hashes fail closed.

### 4. Preserve human approval and inactivity

- Every response remains `external_proposal_unreviewed` with human approval pending.
- Acceptance: no response may claim approval, selection, rendering or activation;
  validation returns only review counts and never emits active VisualTasks.

### 5. Test unseen synthetic stories

- Cover both a keep-single proposal and a multi-task proposal in a non-documentary
  story fixture.
- Acceptance: valid unseen proposals pass; missing beats, non-exact spans, lost
  constraints, unknown jobs/entities/context, added schema fields and invented human
  approval each fail deterministically.
