# Job 8 — Integrated root cause, redesign and validation plan

## One job

Synthesize Jobs 1–7 into an evidence-backed repair or redesign plan for the
general matching system. Do not implement it in this job.

## Required analysis

- Rank root causes by impact, recurrence and confidence.
- State which current components should be retained, repaired, replaced or
  removed and why.
- Define clean ownership and contracts across Story, Data, Media and Matching.
- Define beat, claim, semantic visual moment, visual job, presentation contract,
  template capability, candidate, route and review evidence unambiguously.
- Propose the smallest architecture that preserves deterministic contracts while
  allowing model-assisted semantic reasoning behind provider-neutral interfaces.
- Define how grammar/tags and capability records are authored, reviewed and
  versioned.
- Define evaluation: calibration stories, untouched held-out packages, positive
  and negative candidate recall, family diversity, no-template correctness,
  review effort, and regression gates.

## Required outputs

- `reports/astra-root-cause/08-root-cause-and-redesign.md`
- `reports/astra-root-cause/08-root-cause-and-redesign.json`
- `plans/ASTRA_MATCHING_REBUILD_PLAN.md`

The plan must be staged, reversible and test-first. Every proposed change needs
an owner, inputs, outputs, migration, acceptance test, rollback, dependent jobs
and evidence citations. Clearly label decisions requiring the editor.

## Acceptance

- Every redesign element resolves a proven root cause.
- No story/package/subject/beat-specific runtime branch is proposed.
- Existing valid contracts and template evidence are reused where possible.
- Implementation cannot begin until the editor reviews this plan.

Stop and request review of Job 8.
