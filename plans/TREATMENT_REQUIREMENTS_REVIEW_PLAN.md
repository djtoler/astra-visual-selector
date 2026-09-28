# Treatment-requirements drafting and human review plan

Date: 2026-09-28
Branch: `codex/treatment-requirements-review`

## Objective

Add a candidate-specific layer between the existing VisualTasks and final fillability. The existing 41 VisualTasks remain the source of truth for what each narration task must communicate. This layer only proposes how one specific existing template would carry one task through its native slots, text fields, data fields, and duration.

No draft becomes matching evidence until the user reviews it. No LLM, Codex, or validator can approve a treatment.

## Roles

- **Existing VisualTask:** defines the editorial requirement; it is not rewritten here.
- **Drafting model:** proposes a slot-by-slot treatment using a versioned prompt and only supplied evidence.
- **Deterministic validator:** checks IDs, exact native capacity, source quotations, required fields, and unresolved claims. It never judges editorial quality.
- **User:** approves, edits, rejects, or leaves unresolved every treatment.
- **Fillability consumer:** reads only approved treatment requirements.

## Required stages and acceptance checks

### 1. Freeze one pilot pairing

Start with one exact-mapped VisualTask/template pair. Bind the VisualTask, baseline candidate, reviewed preview record, exact composition mapping, native technical specification, and prompt by hash.

Acceptance: the pilot references one existing candidate already offered to that task and one verified exact native composition. No new candidate or template is invented.

### 2. Create a versioned drafting prompt and closed schema

The prompt must map content to exact native media slots and text fields, state media kinds and person/group constraints, allocate data values, propose native timing use, and list every unresolved item. It must distinguish observation, proposal, and verified technical fact.

Acceptance: the model cannot emit approval, `fillable_now`, selection, rendering authorization, a nonexistent slot, or a custom structural extension.

### 3. Prepare before any model call

Create the exact pilot request and validate it locally. Report its input scope and estimated paid-call cost from a measured prior run of the same shape; if no comparable measured run exists, say so rather than inventing a cost.

Acceptance: preparation is free and deterministic. A paid external call requires separate explicit user authorization.

### 4. Validate the draft

Reject stale prompt/input hashes, unknown slots or fields, missing evidence, unsupported media kinds, unauthorized timing adjustments, and any claim of approval. Preserve omissions as unresolved.

Acceptance: validation proves structural consistency only; it cannot promote the draft.

### 5. User review

Show the template clip, task narration and constraints, exact technical capacity, proposed slot/text/data/timing assignments, and unresolved items together. The user may approve, edit, reject, or leave unresolved, with a saved decision and note.

Acceptance: no default approval; edits retain the original draft and provenance. The first pilot must be accepted before expanding the batch.

### 6. Compare only approved treatments

An approved treatment may be compared with exact composition capacity and available media. Results may be `fillable_now`, `conditional`, `incompatible`, or `unresolved`, with exact missing requirements.

Acceptance: absence of a current approved treatment blocks a final verdict. This branch remains disconnected from live slate, pairing, rendering, and selection paths.

## Initial scope

Build the schema, prompt, deterministic pilot-request builder, validator, and one prepared pilot without making a paid model call. The first pilot pairing will be selected deterministically from exact-mapped candidate placements that already have an exact task audio span; the saved request will identify it before any drafting run.

## Execution review

Started on 2026-09-28:

| Stage | Evidence | Result |
|---|---|---|
| 1. Freeze one pilot pairing | Deterministic preparation selected the first exact-mapped candidate with exact task timing: `02-02a.main` / `screen-mockup-rfx--review-002`, native composition 262. The request binds comparison, catalog, slate, prompt and schema by hash. | Passed |
| 2. Prompt and schema | `PROMPT-treatment-requirements.md`, the closed draft schema and custom validator prohibit approval, fillability verdicts, invented slots, custom structural extensions, selection and rendering. | Passed for preparation |
| 3. Prepare before call | `treatment-requirements/pilot-001/request.json` was built and consumed by the validator. It exposes one verified media input, zero native text fields, 8.008 seconds native duration and 3.1 seconds task duration. No paid call was made. No prior measured run of this exact request shape exists, so no cost estimate is claimed yet. | Passed; call pending authorization |
| 4. Validate draft | `treatment-requirements/pilot-001/draft.json` proposes the one verified visual slot for the 2009 XXL Freshman cover, assigns the exact identity/date requirements, adds no native text, and preserves six unresolved questions. The deterministic validator reports one media, zero text and two data assignments without approval or verdict. | Passed for the unreviewed draft |
| 5. User review | `review-001.json` preserves the editor's exact direction: establish the complete cover, then zoom into Curren$y in post; the native template does not need a zoom control. The decision approves treatment requirements only and authorizes neither selection nor rendering. | Passed |
| 6. Compare approved treatments | `capacity-comparison.json` finds the one-slot template structurally capable of holding the full cover and assigns the zoom outside the template. Verdict remains `conditional` because the exact cover asset is only 546×246 for a 4K composition and the 8.008-to-3.1-second timing policy remains unresolved. | Passed; two explicit conditions remain |

No VisualTask was rewritten. No AE application, render, paid call, source-template edit, live ranking, pairing or selection change occurred.
