# Fable independent matching root-cause workflow

This directory contains one kickoff prompt and eight focused jobs for auditing
and redesigning the general StoryPackage-to-template matching system.

Use `MASTER_PROMPT.md` to start the Fable conversation. Fable must execute one
job at a time, save that job's evidence-backed result, and stop at its acceptance
gate. Later jobs consume earlier outputs; they are not invitations to perform a
single broad speculative review.

The inherited `astra-root-cause` directory name preserves stable evidence and
job paths. This branch is an independent Fable audit rooted at Matching commit
`1276d0ca1daece81b5b7b38c8b5f5280046e5077`; later Astra Job 1–8 outputs on
the `matching-layer` branch are excluded comparison material until both audits
are complete.

## Order

1. System map and evidence integrity
2. Story beat, claim and visual-moment semantics
3. Story/Data/Media upstream contract fitness
4. Matching transformations and visual-job derivation
5. Grammar, tags and template-capability coverage
6. Candidate admission, diversity, ordering and display
7. Human-review and reference-match error analysis
8. Integrated root cause, redesign and validation plan

No job authorizes template selection, rendering, or implementation. Preserve
the current failing artifacts until Job 8 is reviewed.

## Mandatory execution policy

`EXECUTION_POLICY.json` is part of the workflow contract. Every job runs with
the user-visible Fable model at `medium` reasoning effort. Each job records the
exact resolved model identifier exposed by its running session, the display name
and the effort. Because no public or local registry in this checkout establishes
Fable's internal model ID, the audit must not invent one. A model or effort
mismatch blocks work; effort changes require a separate explicit editor
instruction.

The two files under `references/gold-standard/` are editor-designated perfect
reference versions. They define the target quality for beat boundaries,
coherent visual moments, visual-job derivation and task proposals. Use them to
derive general principles, not story-specific production rules.
