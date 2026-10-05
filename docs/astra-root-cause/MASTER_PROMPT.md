# Master prompt — Fable independent matching root-cause audit

You are the independent systems auditor for a general StoryPackage-to-template
Matching layer. Your job is to establish why the system sometimes returns
repeated, irrelevant or incomplete template candidates and misses obvious valid
alternatives. Evaluate both the upstream Story layer and the current Matching
implementation step by step. Do not assume the defect belongs to one layer.

## Repositories

- Story authority: `djtoler/patterns`, branch
  `claude/friendly-maxwell-i5brux`, audited commit
  `d5117a6de0fd0c640a336c6f456946ec8b40f319`.
- Matching production authority for this audit: `djtoler/astra-visual-selector`
  at frozen commit `1276d0ca1daece81b5b7b38c8b5f5280046e5077`, exposed
  by the `fable_analysis` branch.
- Audit workspace: `djtoler/astra-visual-selector`, branch `fable_analysis`,
  created from Matching commit
  `1276d0ca1daece81b5b7b38c8b5f5280046e5077` before Astra Job 1.
- The exact reference paths and commit-pinned URLs are in
  `docs/astra-root-cause/REFERENCE_MANIFEST.md` on the audit branch.

## Independent comparison boundary

This is a clean independent pass. Do not inspect, fetch, merge, quote, summarize
or use the Astra Job 1–8 reports or repair plan from the `matching-layer`
branch. Do not use later Matching commits as evidence. Work only from this
branch, its byte-preserved evidence, the manifest's pinned Story commit and the
manifest's explicitly named source repositories. If an excluded Astra result is
accidentally exposed, identify it, do not use it, and record the contamination
risk in the current job receipt.

Historical file and directory names containing `astra` identify the repository,
evidence package or inherited workflow layout. They do not identify the model
running this audit and must not be renamed or reinterpreted as Fable-authored
evidence.

## Canonical human evidence

Read and validate:

- `reports/astra-matching-review-evidence-20261004.json`
- `grammar/astra-review-evidence.schema.json`
- `docs/ASTRA_MATCHING_ROOT_CAUSE_HANDOFF_20261004.md`

Treat editor comments as scoped evidence, not automatically global rules.
Distinguish verbatim human observations, recovered human data, derived prior
choices, and machine evaluation. Cite `evidenceId` for every conclusion that
depends on a review.

## Perfect reference versions

The editor has designated these exact files as **perfect reference versions**
for the beat/script-to-template task-proposal quality the general system must
learn to produce:

- `docs/astra-root-cause/references/gold-standard/storypackage-02-year-seventeen-full-task-proposals.json`
- `docs/astra-root-cause/references/gold-standard/storypackage-02-future-volksgeist-task-proposals.json`

Verify their SHA-256 digests against `REFERENCE_MANIFEST.md`. Evaluate how
their beat boundaries, coherent visual moments, visual jobs, requirements and
template-matchable task descriptions differ from current outputs. Treat their
quality as the target, while extracting story-neutral principles rather than
hardcoding either documentary's subjects, package IDs or beat IDs.

## Mandatory model strategy

Read and obey `EXECUTION_POLICY.json` before starting:

1. Run every job with the user-visible `Fable` model at `medium` reasoning
   effort.
2. Before Job 1, verify the active session reports Fable and Medium. Public
   OpenAI documentation and this checkout do not establish Fable's internal
   model ID, so do not invent one. Record the exact resolved model identifier
   exposed by the running session, the user-visible model name and effort.
3. If the active model is not Fable or the effort is not Medium, stop before
   analysis and report the exact mismatch.
4. Do not raise or lower reasoning effort during this audit. Preserve difficult
   unresolved questions for the job report; a different effort requires a new
   explicit editor instruction.

## Execution contract

The audit is divided into separate jobs under `docs/astra-root-cause/jobs/`.
Perform exactly one job at a time, in numerical order. Begin with
`01-system-map-and-evidence.md` only. Do not silently continue to Job 2.

For every job:

1. Read its listed sources directly.
2. Trace actual code and artifacts; do not infer implementation from a summary.
3. Separate observed fact, measured result, hypothesis and recommendation.
4. Cite file paths, symbols/JSON pointers, commit hashes and editor evidence IDs.
5. Save the required Markdown and JSON outputs under
   `reports/astra-root-cause/` using the job's filenames.
6. Run the stated acceptance checks.
7. End with `PASS`, `FAIL`, or `BLOCKED`, plus the exact next job and blocker
   owner: `you`, `data`, `story`, `matching`, or `none`.
8. Commit and push only the completed job's audit outputs and required plan or
   receipt updates to `fable_analysis`, then provide direct GitHub file links.
   If publication fails, preserve the local commit and report the exact blocker.
9. Stop after that job. Do not begin the next numbered job until the editor
   explicitly replies to continue.

## Non-negotiable boundaries

- Audit the general system, never optimize for Future, Jay-Z/Drake, Year
  Seventeen, a subject name, or a reviewed beat ID.
- Preserve source narration, StoryPackage revisions, candidate galleries and
  review evidence before proposing changes.
- Do not patch Story, Data, Media, Matching, grammar, ranking or review code
  during Jobs 1–7.
- Do not turn historical popularity, similarity score, prior-story selection or
  sample subject matter into candidate admission authority.
- A valid result may be no template. B-roll, sourced evidence, still imagery,
  cutouts/text and deliberate continuation remain legitimate routes.
- Do not select a template or authorize rendering.
- Do not implement a repair, edit production code or modify evidence during
  Jobs 1–8. Job 8 produces a proposal and stops for editor review.
- If the original “org” transcript-to-beat/visual-job reference is not fully
  present in the manifest, identify the exact missing artifact and continue all
  analysis that does not require it. Never reconstruct it from memory.

Start now with Job 1 only.
