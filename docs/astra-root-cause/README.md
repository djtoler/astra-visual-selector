# Astra matching root-cause workflow

This directory contains one kickoff prompt and eight focused jobs for auditing
and redesigning the general StoryPackage-to-template matching system.

Use `MASTER_PROMPT.md` to start the Astra conversation. Astra must execute one
job at a time, save that job's evidence-backed result, and stop at its acceptance
gate. Later jobs consume earlier outputs; they are not invitations to perform a
single broad speculative review.

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
