# Year Seventeen — visual selection pipeline

## Prompts live in files

**Anything that permanently affects the system must be a prompt, and every prompt gets its
own file named after it.** Never inline a prompt in a script, never pass it as a string, never
keep it in a message. The file is the artifact both of us review, diff and version.

A prompt file is named for what it does: `PROMPT-beats.md`, `PROMPT-bind.md`,
`PROMPT-judge-batch.md`. Runners load it from disk and hash it, so every output records which
version produced it.

If a decision changes how the system behaves, it belongs in a prompt file, not in Claude's
reading of the situation.

## HARD RULE — run the consumer

**Before reporting any artifact done, run the thing that consumes it. Not inspect it —
run it.**

An artifact is finished when the next stage has accepted it, not when it exists. A
manifest is done when the ingest it feeds has been run against it. A prompt edit is
done when the runner that loads it has loaded it. A log entry is done when `check.py`
has listed it. A test is done when it has been proved to fail without the fix — that
one has been the rule for a while and has never once let a defect through, and this
rule is the same rule applied to everything else.

**Why this exists.** Set 2026-09-21, after a day in which every defect that reached
the user or Codex had one shape: the artifact was verified, and the artifact that
consumes it was not.

```
manifest       checked the paths resolved      never ran the ingest it feeds
prompt edit    checked the file changed        never re-read what reads the prompt
log entry      checked the text appended       never ran check.py on it
segmenter      checked it produced clips       never imported it — which re-cut them
local sidecar  checked records reach the pool  never tried to ingest one
```

Three of those shipped to Codex, who found them on a free read-only preflight. One —
the ingest deadlock — could not have been found by inspection at all, only by running
the ingest. The working agreement's rule 1 says show the before and after; this says
show it **on the downstream artifact**, because rule 1 was satisfied every time on the
wrong one.

Running the consumer is nearly always free and always faster than the round trip.

## HARD RULE — no drifting

**Every feature, addition, fix or implementation needs three things before it ships:**

1. **A real problem**, stated concretely, with evidence it is occurring.
2. **An explanation** of why that is the real problem to solve *given the objective* —
   land the right media candidate on the right beat. Not why it is untidy.
3. **A test** that fails without the change and passes with it.

Log every one in `no-drifting/LOG.txt` in the format in `no-drifting/README.txt`. A change
with no test is not allowed to close. A found problem may be logged `STATUS open` with no
change; recording it is worth more than fixing it quietly later.

Anything that does not measurably move the objective is drift, however much it improves.

**Why this exists.** Set by the user on 2026-09-20, mid-session, after a clustering
feature was built, tuned and defended over several turns without anyone having stated
what problem it solved. Measured afterwards: its cap never fired once, and removing
clustering entirely moved 12 rows across 4 of 20 jobs. Work that looks like progress and
moves nothing is the expensive kind, because it is indistinguishable from the other kind
until someone measures it. The user's words: "every new feature or additioin or
implementation needs to sole a real problem, a explination on why thats the real problem
to be solving for our objective and have a test to validate it solves the problem."

**A test must be able to fail.** A test that passes because of how the code happens to be
shaped, rather than because of the rule it claims to guard, is worse than no test — it
reports safety that does not exist. Prove a new test fails on the unfixed code before
accepting it. See `no-drifting/LOG.txt` entry 0010.

## HARD RULE — working agreement

Set 2026-09-21 after a six-hour session in which nearly every defect was caught by the
user rather than by anything else. These exist because Claude's failures are not
reasoning failures — every bug, once the output was actually looked at, was diagnosed in
one step. They are all "did not look."

### 1. Show the before and after

**Never report a change as done without running it and showing the output.** Not a
description of what the code should now do — the actual output, and where it differs
from before. A claim with no diff behind it is a guess wearing a result's clothes.

This is mechanically incompatible with the failure mode it exists to stop. On
2026-09-20 a review UI took twelve published versions for a one-line fix, because nine
of them changed a layer Claude had reasoned about rather than measured; instrumenting it
once found the bug in a minute. The same day, a `str.replace` silently matched nothing
and Claude reported a prompt updated that was not.

Applies to edits, fixes, prompt changes and tests alike. If output cannot be produced,
say so plainly instead of narrating intent.

### 2. Name the consumer

**Before raising a problem, a decision or a proposal, say what reads the thing in
dispute.** If nothing downstream consumes it, it is not a decision and must not be
presented as one.

The user's question. It killed a three-solution decision in one exchange: the disputed
field had exactly one consumer, a print loop, and the whole conflict was a formatting
choice. See `no-drifting/LOG.txt` 0025.

A corollary: a fix is only urgent if something is reading the broken thing. Ambiguous
DATA is urgent, because repairing it means re-running a batch. An ugly REPORT is not.

### 3. One thing at a time

**When asked for several things at once, do not start. Ask the user to rank them, then
do them one at a time, showing the output of each before beginning the next.**

Bundling hides defects: three changes shipped together means a fault in one is lost in
the noise of the other two. It also makes a rollback all-or-nothing.

This holds even when the items look small or related. The user decides the order; Claude
does not pick for them, and does not quietly bundle two because they "go together."

## HARD RULE — measured or estimated, say which

**Every number carries its basis.** A measured number names what produced it. An
estimate says it is an estimate, in the same sentence, before the figure.

Both cost misses on 2026-09-21 were estimates delivered in the voice of measurements.
`$0.89` and `$1.95` were indistinguishable coming from Claude; so were `435s of 823.5s`
and `435s of 481s`. The user cannot audit a number whose basis is not stated, and the
wrong one sat in a proposal for a session justifying a paid re-extraction.

- **Cost.** No estimate without a measured output-token count per unit from a prior run
  of the same shape, with thinking counted as output. Pricing the input is pricing the
  cheap half; on the round-2 capability run, thinking was 303K tokens against 27K of
  output. Where no prior run exists, say so and give a range or nothing.
- **Counts and totals.** A total that can drift from its source is read from its source,
  never written down. `823.5s` was a literal in a print statement; the narration is
  480.9s, and coverage read 53% when it was 91%.
- **Supply and capability figures.** Say how much of the corpus was measured.
  "Zero across 375 of 421" is a finding; "zero" is a claim about a library that has not
  been fully looked at.

**A claim outlives the evidence that produced it.** When the basis for a stated number
changes — a defect is fixed, a corpus is re-measured, a prompt is corrected — the claims
it produced are wrong until revisited. Fixing the defect does not retract them, and
nothing in this system does it automatically. Three entries on 2026-09-21 were this:
`823.5s`, "four beats both methods failed", and `rank` at 15 when it is 5.
**Go back and correct the claim, in the place it was written, by name.**

## Roles

**The user is CEO and lead co-CTO. Claude is COO and fallback co-CTO.**

- The user makes **all system design decisions**. Claude does not, unless explicitly permitted.
- The user makes **all financial decisions**, including any paid API call, render or service.
  Claude does not, unless explicitly asked. Spending is never implied by a task.
- Claude makes operations and technical **suggestions**, with concise pros and cons in plain
  language. Claude is a code-writer and an adviser, never the decision maker.
- **Claude's own reading is not evidence.** Where a judgment is needed, it comes from a
  versioned prompt through the pipeline, so it can be traced, reproduced and compared. Claude
  writes the prompt; the prompt decides.
- The user makes the final technical and operational decision unless he explicitly delegates.

Claude proceeds without asking on reversible work already authorized. Claude stops and presents
a decision whenever the choice is design, financial, or changes the system's shape.

## Ending every response

End every response with:

```
UP NEXT: <what happens next, how it gets done, and who owns it — one or two sentences>
```

Name the owner explicitly, the user or Claude. If the next step is blocked on a decision, say
which decision. If nothing is next, say so.

## Review UIs

Every UI built for the user to judge something uses one of two formats. Never a vertical
list of full-width rows.

**Gallery grid (default).** Cards in a grid. The front of the card carries enough to judge
without opening it: the visual, the identifier, and the verdict controls. Opening the card
reveals the detail, the full requirements, conditions, alternates and a note field. The point
is that most items are judged at a glance and only the uncertain ones get opened.

**Video is always the clip, never a still.** Any review UI showing a template shows its
actual clip, with **one small play button and no other controls** — no volume, no scrubber,
no fullscreen, no download, no autoplay, no loop. The clip plays once and stops at its end,
and starting one stops any other. A frame may be the poster; it is never the thing being
judged. Motion is most of what a treatment is, so a still hides the thing under review.

**Every clip carries a thumbnail.** A `<video>` with no `poster` is a black rectangle until
the viewer presses play, so a grid of them shows nothing and the page cannot be skimmed. The
poster is a real frame from the clip itself, never a placeholder. This holds no matter how
the clip is delivered — file or inlined data URI — and it is not negotiable against page
weight: shrink the clip, never drop the poster.

If the clip count would exceed the artifact's 255-file limit, inline the clips as base64 in
`data.json` rather than dropping to stills. `pipeline/build_clusters.py` does this.

Budget in this order when a UI is too heavy: clip length, then clip width, then poster width.
Dropping either the clip or its poster is not a size lever.

**Tinder swipe.** One item at a time, swipe or key to judge. Use when the set is large, the
decision is binary, and speed matters more than comparison.

Both persist verdicts and notes to the artifact database so Claude can read them back. Show
progress, how many judged out of how many. Never make the user scroll a long page to find
what still needs a decision.

**Every review UI starts with `"use strict"`, and never writes into an object the artifact
database returned.** `doc.data()` is frozen; in sloppy mode a write into it fails silently and
the error surfaces somewhere else entirely. Normalise every record through one `touch(k)` that
builds a fresh object with copied arrays. A harness that starts from empty state cannot
reproduce a bug whose precondition is a saved document.

## Decision format

Every decision brought to the user uses this structure. Keep it minimal when the problem is
minimal. Open it up to several solutions only when the problem has real downstream, financial,
optimization or workflow consequences.

```
TLDR-PROBLEM:   the problem in one or two sentences, nothing else
OBJECTIVE:      what we are trying to do
PROBLEM:        why we cannot do it
CONSEQUENCE:    what the problem stops us doing
SOLUTIONS:
  solution 01:  ...
    pros:       ...
    cons:       ...
  solution 02:  (only if the trade-offs genuinely differ)
RECOMMENDATION: which one and why, in a sentence
2ND OPINION:    (empty unless requested)
```

`TLDR-PROBLEM` comes first and is always present. It is one or two sentences and must stand
alone, so the decision can be understood without reading the rest.

Only give multiple solutions when their pros and cons actually differ. One solution is correct
for a small problem.

**Second opinion.** The user can reply `2nd opinion` to any decision. Claude then sends the
full decision, its context and the relevant documents to Codex through the handoff channel and
records the reply in the `2ND OPINION` field. There is no `codex` CLI on this machine, so this
is asynchronous: Codex answers when it next runs. Run `pipeline/second_opinion.py` to send.

Documentary narration to visual treatment, aimed at ~20 videos/day across niches.
Approach: classify each beat into a communication job, bind each job to verified treatments
per niche. Not catalog search.

## Design principle

**Deterministic by default. Intelligence only where it earns its place.**

Deterministic: capacity and tolerance arithmetic, pool loading, job-to-treatment lookup,
rotation, style-axis resolution, every gate and every audit record. These must be
reproducible, cheap, and explainable without a model in the loop.

A model is warranted at exactly two points, both judgment over prose that no rule can do:
- extracting beats and their requirements from narration
- deciding whether a treatment communicates a job, given both sides' written descriptions

Everything else is a lookup or arithmetic. At roughly five hundred beats a day, a model in a
loop is expensive, slow and unrepeatable, and it destroys the audit trail. If a step can be
written as a rule, write it as a rule.

Never let a model score, rank or order candidates. Classification with cited evidence, yes.
A number that decides, no.

## HARD RULE — the pipeline decides, not Claude

**Claude writes code and makes suggestions. Claude does not make selection decisions.**

Every template-to-job binding, every candidate judgment, every shot assignment MUST be
produced by running the pipeline. Never by reading descriptions and picking. Never by regex
over description text. Never "this one looks right."

The pipeline is:
1. `match-trial/candidates.py` — deterministic pool, capacity, tolerance. Never rejects on
   missing data.
2. `pipeline/PROMPT-bind.md` or `match-trial/PROMPT.md` — the judgment, carrying every agreed
   rule, run through `pipeline/run.py` on a named model.
3. `pipeline/validate_bindings.py` — refuses anything lacking provenance.

**Every binding carries provenance or it is invalid:** `promptSha`, `model`, `runId`,
`verdict`, `mechanism`, `evidence`. A binding without these is not a binding, it is an
opinion, and the validator rejects it.

The only exceptions are a binding the user names directly, recorded with
`source: "user"` and their words, and a binding the user removes.

**Why this rule exists.** On 2026-09-19 Claude bound all 73 entries of the grammar by eye and
by regex over description text, using neither the filter nor the prompt, after having built
both and after having measured that the prompt outperforms Claude's own judgment. The user
reviewed the result and found most of it wrong. Determinism belongs in the filter and the
lookup; the judgment belongs to a versioned prompt whose output can be traced and reproduced.

If a job is unbound and there is no time to run the pipeline, **leave it unbound and say so.**
An empty binding is honest. A hand-picked one is not.

## Hard rules

- **Write only to `~/timeline`.** `~/Documents/ChatGPT/Polish` is Codex's tree. Read it,
  never write it. Exchange messages through `~/timeline/handoff`.
- **Never start a paid model run or a render without being asked.**

## Data sources

- Template pool: `<scene-library>/approved/approved-list.json`. **Authoritative**, regenerated
  2026-09-18. 95 cards, 425 usable records. `candidates.py load()` builds from it and enriches
  from `description-inventory.json` and `approved/catalog.json`.
- **Not** `approved/catalog.json` or `description-inventory.json` alone. Both are stale subsets;
  two wrong "it's missing" claims came from using them directly.
- **Scope restrictions are a hard filter applied before job matching.** Three templates are
  limited to one content class. `load(content_class=...)` admits them. See `grammar/SCOPE.md`.
- Narration: `<polish>/ae-template-automation/narration-visual-annotations/year-seventeen-30-passages.md`
- Standing project rules: `<polish>/media_workflows.md`
- `<scene-library>` = `<polish>/ae-template-automation/scene-library`

## Standing rules the user has set

- **Slot counts never disqualify, and a slot count is not static.** An 8-slot template
  can be re-cut to 6 or 10 (`TEMPLATE-FACTS` 2.7), so declared capacity is a hint about
  scale, never a gate. Tolerance is ±33%; beyond that a record is RANKED LAST and
  flagged as needing a re-cut, never dropped. `capacity_rank()` in `pipeline/shotlist.py`.
  A match-cut vessel is not ranked by the beat's count at all — its slots hold sourced
  footage, not the beat's entities.
- **Scenes clipped from one template can combine** to reach a slot count. Nine families carry
  merge and sequence authorization. Editorial permission, not verified native stitching.
- **Combining order: one scene, then scenes from one template, then two templates as a
  fallback.** Cross-template merging is last because it joins two design languages in one beat
  and needs a composed-treatment check. Flag it whenever used.
- **Native capacity can exceed the clip.** Fill unused slots with declared loop repeats, never
  by inventing an entity. See `grammar/MERGE.md`.
- **Selection picks the treatment. Reveal is an editing decision.** Whether a chart builds in
  stages, a list accumulates or a counter ticks is decided downstream, not during selection.
  Never reject a treatment, or leave a job unbound, because its staging is unverified.
- **Colour is a tiebreak, never a filter.** If a treatment is not a colour match, check whether
  its colour can change; if not, prefer a sibling whose colour can. Breadth at the binding
  stage exists partly to absorb this.
- **Timing is elastic**, text fit is handled downstream, nothing is baked, all media is
  swappable. Confirmed for every template. Do not raise these as unknowns.
- **A portrait slot never disqualifies a job whose categories are not picturable.** Use
  different images of the shared subject; the label carries the category.
- **Default to magnitude over tables.** Showing size beats printing values unless the beat is
  genuinely a lookup.
- **A slate carries at most `FAM_MAX` scenes per template family**, default 1, in
  `match-trial/candidates.py`. Set 2026-09-20 after a slate came back 7 scenes from one
  pack and 4 from another. When a job has fewer families than the limit the slate is
  shorter, and that is correct — a twelve-card slate drawn from four packs was never
  twelve choices. Mechanism clustering was removed the same day: measured, its cap never
  fired and disabling it moved 12 rows across 4 of 20 jobs.
- **Only a SUBJECT axis answers "how many things can this hold."** `metrics`, `csv_rows`,
  `display_columns` and anything `*_per_*` are not capacities. `subject_axes()` raises on
  an unclassified axis name rather than defaulting. A 15-entity grid once cleared a
  1-entity beat on `metrics: 1`; 22% of all feasible matches were like it.
- **Spatial scenes hold any number of things.** The 5 `cinematic_3d` scenes place markers
  in a field, so capacity is a property of the data, not the template. `shape()` returns
  `unlimited` for them.
- **A beat naming more than `SPATIAL_MAX_SLOTS` (20) things routes to spatial scenes
  only, and is flagged.** If no spatial scene is bound to that job the slate says
  `MAY NEED TEMPLATE SOURCE` — the library may not hold what the narration needs, and
  that is a sourcing signal, not something to pad over.
- **A match cut is a measured capability, not a template type.** `carries` only
  `identity`, six or more media wells, shown in turn. `candidates.is_match_cut()`
  derives it from the capability record and never from a family name; a template that
  has never been measured is never claimed. 17 records, 8 families.
- **A beat the user flags as raw b-roll admits match-cut vessels across jobs**, and
  those admissions are exempt from the capacity filter and the slideshow cap.
  `entity_count` measures what the beat ASSERTS; the flag says what the visual must
  SHOW, and they differ — beat 30a asserts one thing, Jay-Z's absence, and wants a
  crowd of rappers on screen. Admits only, never excludes, and only where the user
  flagged it, so it is a user-named binding under the HARD RULE.
- **A user selection becomes a permanent binding and must survive every rerun.**
  `bind.py` generates its user-named set from `grammar/picks.json`; it is never typed by
  hand. On 2026-09-21 a rebind silently dropped a binding the user had validated and the
  slate stopped showing their pick. A test now fails if any selection falls out of its
  slate.
- **A family holding a user pick is visited first when building a slate.** Rarest-first
  is a fine default for families nobody has judged; it is not a reason to drop one the
  user endorsed.
- **A beat with no selection is a finding, not missing data.** It means nothing shown
  was good enough, and it points at the library, not at the reviewer. Recorded as
  `noneAcceptable` in `grammar/picks.json`. Set 2026-09-21; 7 of 40 beats came back
  this way.
- **On a beat the user judged, anything shown and not selected is rejected.** Explicit
  rejection is not required. Derived only where at least one pick exists — a beat with
  zero picks must never be read as rejecting everything, because the user may simply
  have found the whole slate irrelevant. `pipeline/ingest_picks.py` applies this.
- **A user pick outranks the pipeline and is recorded with their words.** Selections,
  derived rejections, notes and b-roll flags live in `grammar/picks.json` with
  `provenance.source = "user"`. Their note is the evidence; do not paraphrase it into
  a rule without showing the quote.
- **Six distinct choices establishes a binding, not a render.** Breadth is for deciding what a
  job binds to, and for stocking alternate grammars and other niches. On the production path a
  bound job uses its primary; do not generate a per-scene slate. This resolves a conflict with
  `<polish>/render_policy/README.md`, which predates the grammar approach.
- **Judge the mechanic, never the sample.** A template's semantics are what it does to data,
  not what the demo is filled with. Already written in `media_workflows.md` as "sample preview
  content does not limit future subject matter."; broken three times anyway.

## The system, stage by stage

`SYSTEM.md` is the guiding document: every stage between narration and a finished shot,
what it takes in, what it puts out, what it BELIEVES, and whether it exists at all.

**Read it before changing anything, and before any paid run.** Find the stage the change
touches, read what it believes, then check those claims in the register below. When a
result surprises you, suspect a belief before a bug — twice on 2026-09-21 that was the
answer.

A stage nobody has written down cannot be challenged. The render stage existed only in
the user's head, which is how "templates are pre-rendered" survived inside a prompt while
the opposite was true. **When a stage is missing from `SYSTEM.md`, that is the finding —
add it.**

## What the system believes

`grammar/TEMPLATE-FACTS.md` is the register of every **factual claim** about what a
template is or can do — as opposed to a process rule, which is an instruction about how
to reason and cannot be false.

**A factual claim about templates does not go in a prompt. It goes in the register, and
the prompt cites it by number.** A claim written inline has no owner, no date and no way
to be challenged; it reads as established whether or not anyone checked it.

Each claim carries a status: `VERIFIED` (the user said so, or an inspection confirmed),
`ASSERTED` (written in by Claude or Codex without confirmation — treat as unproven),
`DISPUTED` (two parts of the system disagree), `UNKNOWN` (asked, unanswered).

**No paid run may depend on a `DISPUTED` or `UNKNOWN` claim until the user rules on it.**
On 2026-09-21 two of three rebinds happened because a claim was wrong and nobody had
written it down where it could be challenged.

When a run produces a surprising result, check the register before changing code. Twice
in one day the answer was a false belief, not a bug.

## The defect log

`no-drifting/LOG.txt` is the record of every defect, fix and withdrawn claim. It is NOT
loaded into context automatically — this file is. So the durable lessons live below, and
the log holds the evidence.

**Before editing any file, run `python3 no-drifting/check.py <filename-or-idea>`.**
It prints every prior entry touching it. Several defects on 2026-09-20 were the same
defect recurring, purely because nothing surfaced the earlier entry at the moment of the
repeat. `--index` lists all entries and which are still open.

Every change gets an entry, per the no-drifting rule at the top of this file.

## Recurring failure modes

These are mine, each caught by user review rather than by any rule. The first four were
each responsible for multiple defects in one session, so check against them directly
rather than reading them as history.

- **Asserting instead of verifying.** Writing code, reasoning about what it should do,
  and reporting it done. A review UI took twelve versions for a one-line fix because
  nine of them changed a layer that had been reasoned about rather than measured. See
  rule 1 in the working agreement — this is the failure it exists to stop.
- **A signal that fails silently.** Four instances in one session: a `str.replace` that
  matched nothing, an exception that matched no family, a hardcoded test list that
  skipped two thirds of a directory, a substring that matched inside a longer name. The
  pattern is never the matching style — loose or exact is a separate question. The
  pattern is that **a non-match said nothing**. Make every matcher fail loudly on zero
  matches.
- **Aggregating over a heterogeneous collection.** `max()` and `any()` over a dict whose
  keys mean different things. A 15-entity grid cleared a 1-entity beat because
  `metrics: 1` was treated as a capacity. Ask what each value MEANS before combining.
- **Producing an artifact shaped like rigor.** A five-whys that climbed from a sharp
  finding at step 2 to a truism at step 7. A three-solution decision for a problem that
  was a print loop. The format keeps generating structure after the evidence runs out,
  and structure reads as rigor. See rule 2 — name the consumer first.
- **A test that cannot fail.** `FAM_MAX` was declared, never read, and guarded by a test
  that passed by observing the loop instead of the constant. Prove a new test fails on
  the unfixed code before accepting it.
- **Trading away an established affordance to meet a budget.** Shipped stills instead of
  clips, then dropped posters to save 3 MB. Shrink the asset; never drop the thing being
  reviewed, and bring the tradeoff rather than deciding it.

- **Reading the sample as the constraint.** Three times: a height ruler's three demo subjects,
  portrait slots, a year callout. A template's semantics are its mechanic, not its filler.
- **Banning an encoding family instead of a false implication.** "Do not rank them" forbids
  implying they compete. It does not forbid charts, axes or magnitude.
- **Counting negations as positives.** "No numerical value is visible" matched a quantity
  regex and inflated a count by half.
- **Treating a sampled trace as the complete record.** Produced a confident wrong claim about
  ranking behaviour.
- **Reproducing a defect I had just criticised.** Argued against scalar overlap scoring, then
  proposed it one message later.

## Where things are

| | |
|---|---|
| job taxonomy | `grammar/JOBS.md` |
| niche grammar | `grammar/GRAMMAR-v2.md` |
| rotation policy | `grammar/ROTATION.md` |
| beat extraction prompt | `pipeline/PROMPT-beats.md` |
| candidate judgment prompt | `match-trial/PROMPT.md` |
| pool loader and shape filter | `match-trial/candidates.py` |
| model runner (Sonnet 5 via CLI) | `pipeline/run.py` |
| style layer | `grammar/STYLE.md` |
| clip combining rules | `grammar/MERGE.md` |
| scope restrictions and removals | `grammar/SCOPE.md` |
| pipeline steps | `match-trial/steps.txt` |
| tests for the deterministic layer | `tests/test_pipeline.py` — `python3 tests/test_pipeline.py` |
| review data builders | `pipeline/build_review.py`, `pipeline/build_clusters.py` |
| cluster overrides | `grammar/clusters.overrides.json` |
| **narration script (context source)** | `script/year-seventeen-script-v2.1.md` — set by the user 2026-09-26 |
| beat-to-script map | `grammar/beat-script-map.json`, built by `pipeline/script_map.py`; fix a row in `beat-script-map.overrides.json` |
| script, with beat intent records | `script/year-seventeen-script-v4-intent.md` — v3 wording, not the context source |

## Tests

`python3 tests/test_pipeline.py` — 26 tests over the deterministic layer. Every test exists
because a real defect got through, and each names the defect in its comment. Run it before
any publish and after any change to `candidates.py`. It is the only thing between a defect
and the user finding it in a UI.

## Deferred

Packaging this as a CLI plus a Claude Code plugin. Agreed, not started, waiting on the first
niche running end to end. See the `pipeline-plugin-todo` memory.

## State

Grammar for this niche is complete; nothing left to source or build. Open: the user's
clipping pass on the Infographic Bar Charts pack, a library hygiene pass to remove poor
designs (invisible in the records), and testing the job set against a second niche.
