# Job 2 — Story beat, claim and visual-moment semantics

## Required execution mode

Claude Desktop invokes the Claude CLI for this job and explicitly selects
Claude Fable 5.1 (`claude-fable-5-1`) at `medium` effort. Record Desktop as the
operator, the CLI invocation as the execution mode, and the resolved model and
effort in the receipt. Stop without analysis if that configuration is not
active.

## One job

Evaluate how the Story layer defines and produces beats, claims, obligations,
job proposals and continuity, and whether those units are fit for downstream
visual matching.

## Questions

- What is a beat in the source transcript, authored script, StoryPackage schema
  and actual builder? Are those definitions consistent?
- What is a claim, and when should one claim contain several visual moments or
  several claims share one moment?
- Do tagged-script boundaries, sentence/line heuristics, lane assignment and
  narrator/clip/quote handling preserve semantic intent?
- Are `jobProposals` useful advice, misleading legacy labels, or incomplete?
- Do obligations express identity, relationships, evidence, text, data,
  continuity, withholding and perceptibility precisely enough?
- Compare Year Seventeen, Future and Jay-Z/Drake with their source/reference
  transcripts and manually evaluated jobs. Identify under-splitting,
  over-splitting, lost relationships and oversized beats.

## Required outputs

- `reports/astra-root-cause/02-story-semantics.md`
- `reports/astra-root-cause/02-story-semantics.json`

For at least 15 representative spans across all three stories, provide exact
source/script spans, current beat and claim boundaries, intended visual moments,
observed defect or success, and evidence citations. Keep proposed semantics
template-neutral.

## Acceptance

- Beat, claim and VisualTask are never conflated.
- Every finding distinguishes Story-authoring failure from a valid Story input
  later mishandled by Matching.
- No runtime or schema change is made.

Stop after Job 2.
