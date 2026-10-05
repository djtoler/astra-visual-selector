# Claude Desktop and Fable CLI independent matching workflow

This directory contains one kickoff prompt and eight focused jobs for auditing
and redesigning the general StoryPackage-to-template matching system.

Use `MASTER_PROMPT.md` in Claude Desktop, which remains the operator throughout
the workflow. It performs some jobs directly and invokes Fable through the CLI
for the assigned jobs. Each execution mode must run exactly one assigned job,
save and publish that job's
evidence-backed result, provide direct GitHub output links, and stop at its
acceptance gate. Later jobs consume earlier published outputs; they are not
invitations to perform a single broad speculative review.

The inherited `astra-root-cause` directory name preserves stable evidence and
job paths. This branch is an independent mixed-executor audit rooted at Matching commit
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

`EXECUTION_POLICY.json` is part of the workflow contract. Claude Desktop
directly performs Jobs 1 and 3–6. For Jobs 2, 7 and 8, Claude Desktop invokes
Claude Fable 5.1 (`claude-fable-5-1`) through the Claude CLI at explicit
`medium` effort. Each job records its operator, execution mode and exposed model
metadata. An execution-mode/model/effort mismatch blocks work; reassignment
requires a separate explicit editor instruction.

The two files under `references/gold-standard/` are editor-designated perfect
reference versions. They define the target quality for beat boundaries,
coherent visual moments, visual-job derivation and task proposals. Use them to
derive general principles, not story-specific production rules.
