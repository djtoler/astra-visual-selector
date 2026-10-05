# Job 7 — Human evidence and reference-match evaluation

## Editor-selected execution mode

Before this job starts, the editor must explicitly choose either direct Claude
Desktop conversation or Claude Desktop invoking Claude Fable 5.1
(`claude-fable-5-1`) through the CLI at `medium` effort. There is no default;
do not infer the choice from an earlier job or model availability. Record the
explicit selection, operator, execution mode, resolved model and any applicable
effort in the receipt. Stop without analysis if no Job 7 selection exists or
the active execution does not match it.

## One job

Use the editor reviews, manually evaluated matches and original reference
transcripts/mappings to measure what works, what fails and which principles
generalize.

## Method

- Cluster evidence by failure mechanism, not by story or subject.
- Contrast accepted, rejected and comment-only records.
- Reconstruct what the editor saw from the source gallery and task context.
- Compare the org/reference transcript-to-beat/visual-job mapping with current
  Story and Matching outputs where the exact artifact exists.
- Separate reusable principles from story/task-specific preferences.
- Identify contradictory or superseded editor evidence explicitly.

If an exact org artifact is missing, emit the smallest precise request for the
user. Do not pause analysis of the 439 normalized records.

## Required outputs

- `reports/astra-root-cause/07-human-evidence-analysis.md`
- `reports/astra-root-cause/07-human-evidence-analysis.json`

Include an error taxonomy with counts, evidence IDs, pipeline stage, responsible
owner, generalizable principle and counterexample. Produce a balanced success
set as well as a failure set.

## Acceptance

- Verbatim human evidence, recovered evidence and derived choices stay distinct.
- “Same as last beat” and other contextual comments are resolved only from the
  preserved review order, never guessed in isolation.
- No review comment directly becomes a runtime rule.

Stop after Job 7.
