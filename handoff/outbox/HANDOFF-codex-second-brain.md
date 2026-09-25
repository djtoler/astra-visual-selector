# Handoff: be the second pair of eyes on candidate selection

Written by Claude, 2026-09-21, at the user's instruction. You are being asked to act as
a second brain on a problem I have been circling for a day and have made the same
mistakes in repeatedly. Everything below is read-only. Nothing here asks you to run an
API call or a render.

What I most need is not agreement. It is someone outside the loop who can see the
things I cannot, because several of my errors are only visible from outside.

---

## 1. The objective

**Land the right media candidate on the right beat.** Narration goes in; for each beat,
a small set of template candidates comes out, at least one of which communicates what
the beat is saying and none of which communicates something it does not.

Target scale is ~20 videos/day across niches, so the common case has to run without a
human. The current niche is "Year Seventeen", a documentary about Drake's 17th career
year, 30 passages, 804 seconds.

## 2. Where we are

The grammar works end to end and produced one human review pass.

```
BEATS SERVED      33/40   82%    at least one option the user would use
ACCEPTANCE RATE   61/199  30%    of options shown, on beats they judged
```

82% is the objective. 30% is wasted review time. They pull against each other — a wider
slate raises the first and lowers the second — so both are tracked.

That baseline was measured on slates that have since changed a great deal. Nothing has
been re-measured, because only a human pass can produce those numbers.

## 3. How it works, in one paragraph

A model reads narration and emits **beats**, each classified into one of **20
communication jobs** (`grammar/JOBS.md`). Separately and offline, a model judges every
one of **421 template records** against all 20 jobs, producing **bindings** with full
provenance. At shot time the beat's job is looked up, the bound records are filtered and
ranked deterministically, and up to 12 are shown to the user in a gallery. The user
picks up to 6. Their picks become permanent bindings that outrank the pipeline.

The full stage-by-stage account, including which stages do not exist, is `SYSTEM.md`.
**Read that first.**

## 4. The files, and why each matters

### Start here, in this order
| path | what it is |
|---|---|
| `SYSTEM.md` | 11 stages, narration to finished shot. Each says what it believes and whether it exists. The four stages whose belief is currently WRONG are tabulated near the bottom. |
| `grammar/TEMPLATE-FACTS.md` | 18 factual claims about what a template can do, each with a status and a source. Created because two false beliefs were found by accident in one day, each costing a paid rerun. |
| `CLAUDE.md` | the standing rules. Includes the working agreement added today after the user asked what they could do differently. |
| `no-drifting/LOG.txt` | 37 entries. Every defect, fix and withdrawn claim, with what was measured. `python3 no-drifting/check.py --index` lists them; `check.py <file>` shows what has already gone wrong with a file. |

### The prompts — where the judgment lives
| path | what it does |
|---|---|
| `prompts/PROMPT-bind.md` | **the one under question.** Judges a template against all 20 jobs. sha `50337c792883`. |
| `prompts/PROMPT-beats.md` | narration to beats |
| `prompts/PROMPT-describe-clip.md` | watches a clip, emits a capability record. sha `64e9839e56a8` |
| `prompts/PROMPT-judge-*.md` | DEAD. Pre-grammar approach, never called. Ignore, and note that one of them contains a false claim. |

### The deterministic layer
| path | what it does |
|---|---|
| `match-trial/candidates.py` | pool loading, capacity, family, match-cut detection, `diversify()`. The core. |
| `pipeline/shotlist.py` | beats + bindings + timing to slates. Five ordered steps; each can remove what the next never sees. |
| `pipeline/bind.py` | the binding run. `--only <ids.json>` re-judges a subset. |
| `pipeline/salvage_bindings.py` | **merges two binding runs per job by rule.** Question 1 below is about this. |
| `pipeline/ingest_picks.py` | review UI to `grammar/picks.json`, immutably |
| `pipeline/ingest_capability.py` | validates and merges capability records, all-or-nothing |
| `pipeline/metrics.py` | append-only metric series |
| `pipeline/preflight.py`, `validate_bindings.py` | gates; bind refuses to run if preflight fails |

### The data
| path | what it holds |
|---|---|
| `grammar/bindings.json` | 595 bindings, provenance on every one, three prompt shas deep |
| `grammar/picks.json` | the user's 61 selections, 138 derived rejections, 24 verbatim notes, 7 beats where nothing was acceptable |
| `grammar/passes/pass-*.json` | immutable copy of each review pass |
| `grammar/capability.json` | 208 of 421 records measured from their clips |
| `grammar/metrics.json` | the metric series |
| `pipeline/beats-all.json` | 40 beats, 30 passages |
| `tests/test_pipeline.py` | 99 tests. Each names the real defect it exists because of. |

### Snapshots for comparison
```
/tmp/bindings.pre-full.json    662 bindings, before today's full rebind
/tmp/bindings.fullrun.json     841 bindings, the unmerged new run
```

## 5. What we did today

1. Measured the review pass: 82% served, 30% accepted, 7 beats with nothing.
2. Found that **match-cut vessels are the best-performing category in the library** —
   8 shown, 6 selected, 75% against 30% overall — and were bound almost only to
   `enumerate`. Derived match-cut capability from the measured capability record rather
   than from family names.
3. Discovered `PROMPT-bind.md` judged templates by what they do **to data**, so
   `assert_without_data` (a beat with no data) could never be served. Fixed. $0.20.
4. The user then ruled on five unsettled factual claims. The load-bearing one:
   **rendering happens AFTER selection.** A template is a starting point; slots, colour
   and type all change. So the question is *can this be MADE to carry the job*.
5. Rewrote `PROMPT-bind.md` with that premise plus a guard, and rebound all 421. $4.46.
6. **The result was mixed and is where we are stuck.**

## 6. Where we are stuck

The full rebind fixed the starved jobs and flooded two others.

| job | before | after | |
|---|---|---|---|
| assert_without_data | 43 | **254** | 60% of the corpus |
| narrate_an_event | 133 | **211** | 50% |
| inversion | 11 | **1** | beat 27 left with one candidate |
| parallel_instances | 50 | 21 | |
| define_terms | 22 | 38 | the fix working |
| pose_a_question | 7 | 25 | the fix working |

The guard held on **volume** — 662 to 841, 1.3x not 10x — and failed on
**distribution**. Two jobs took 465 of 841 bindings. Each individual judgment reads as
defensible; the aggregate is wrong. A job matching 60% of the library has stopped
selecting.

Rather than keep or revert wholesale we merged per job on a rule
(`pipeline/salvage_bindings.py`): revert a job the new run floods, revert a job it
collapsed by more than half, keep the new run otherwise. Result: 595 bindings, no
flooded job, all 61 user picks still reachable, mean options per beat 6.5 to 8.2.

**That merge is the thing I am least sure about, and question 1 is about it.**

## 7. My repetitive mistakes — read this before trusting anything above

These recur. I have logged each and still repeated several. If you see one in the work
above that I have not caught, that is the most valuable thing you can tell me.

**I assert instead of verifying.** I write code, reason about what it should do, and
report it done. A review UI took **twelve published versions for a one-line fix**
because nine of them changed a layer I had reasoned about rather than measured. I told
the user a prompt was updated when a `str.replace` had silently matched nothing. Today I
reported a round of binding numbers taken from a stale file. Every single time I
actually ran something, I found something.

**I let a signal fail silently.** Four instances in one day: a `str.replace` with no
assert; a rule exception that matched no family and quietly disabled itself; a
hand-maintained test list that skipped a third of a directory **and was hiding an
unauthorised-spend vector**; a substring that matched inside a longer name and corrupted
a constant. I logged the lesson twice and hit it again in my own tooling.

**I over-correct a right diagnosis into a wrong rule.** Twice, maybe three times. I
diagnosed one case of mis-filing and banned a legitimate pattern outright — *"never
record the same fact in both fields"* — which would have silently discarded half the
capability of every chart that both encodes and prints. I diagnosed one substring
over-match and banned substring matching, which broke the user's own rule. **The
dressing/mechanic guard in the current prompt may be the same error again**, and I
cannot tell from inside.

**I produce artifacts shaped like rigor.** A five-whys that climbed from a sharp finding
at step 2 to a truism at step 7. A three-solution decision, with a recommendation and a
request for a second opinion, for a problem that turned out to be a print loop. A
recommendation to spend money confirming something already measured. The user cut
through each with a single question. Format reads as rigor and is not.

**I write tests that cannot fail.** `FAM_MAX` was declared, never read, and guarded by a
test that passed by observing the loop instead of the constant. When I later built a
harness to prove some tests bite, the harness reported zero failures for every mutation
— it was broken, and only "all five mutations pass" being implausible caught it.

**I measure on a partial set and report it as the whole.** I told the user
`change_over_time` existed on 2 records and recommended sourcing charts for it. That
count came from a capability pass covering 208 of 421 records — it excluded every
template the capability actually applies to.

**I break one thing while checking another.** Today: sliced `admit_match_cuts` out of
`shotlist.py` while editing the function next to it; diffed a file against itself
because two runs had been appended to one output and my dict comprehension kept only the
last.

**I did not know what the system believed.** Two false premises sat inside prompts for
days — "a template's semantics are what it does to data" and "templates are
pre-rendered" — each written as a confident assertion with no owner and no date. Both
were found by accident, each after a paid run. `TEMPLATE-FACTS.md` exists because of
this, and I would not assume it is complete.

## 8. What I want from you

Four questions, sharpest first.

**1. Is the per-job merge legitimate, or is it laundering?**
`pipeline/salvage_bindings.py`. No binding is invented, edited or hand-chosen, and each
keeps its own provenance. But I am choosing which run to trust per job, and **I wrote
the criterion after seeing the results.** That is the shape of a rule fitted to one
outcome. No test I write can detect that. Should this be thrown away and the premise
fixed instead?

**2. Is DRESSING vs MECHANIC the right cut?**
It is the only thing between "can be made to do it" and "anything serves anything". It
held the total and not the distribution. Better formulation, or is the problem not in
the guard at all?

**3. Is `assert_without_data` a coherent job?**
Defined as "a norm, a hypothesis, or a limitation" — a beat with no data. Under the new
premise almost any template can illustrate an assertion. It scored **0 of 12** in the
user's review before any of this. It may be a catch-all wearing a job's name.

**4. Should a flood be prevented at bind time, or only detected after?**
We flag a job over 40% of the corpus as non-discriminating. Nothing stops the binder
producing one. Would a cap in the prompt help, or would it just make the model pick 40%
arbitrarily?

And one standing request: **if you spot one of the section 7 patterns in anything above,
say so plainly.** That is worth more to me than an answer to any of the four.
