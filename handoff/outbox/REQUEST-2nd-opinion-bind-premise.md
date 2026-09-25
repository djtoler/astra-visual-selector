# 2nd opinion — the binding premise, before we spend again

**Not a request to run anything.** No API calls, no renders. We want your read before
the next rebind, because we have now done three in one day and been wrong twice about
what a premise change would do.

## The objective

Bind each template in the library to the communication jobs it can serve, once, so a
beat's job looks up its candidates. 421 records, 20 jobs. `prompts/PROMPT-bind.md`.

## What changed today, and why

The user ruled on a set of factual claims that were either unwritten or wrong. They are
now in `~/timeline/grammar/TEMPLATE-FACTS.md`, 18 claims, 17 verified. The load-bearing
one is **3.6: rendering happens AFTER selection.**

> "we have to render after we choose a template"
> "slots should not be looked at as static. a 8 slot template can be modified to be 10 or 6"
> "we assume all templates can change colors and fonts"

So the question a binder must ask is not *does this communicate the job* but *can this
be MADE to communicate the job*. The prompt was rewritten to say so, with a guard:

> **But modification changes the DRESSING, never the MECHANIC.** Re-cutting a bar chart
> to six bars leaves a bar chart; it does not become a scatter. Scale, colour, type,
> data and slot count are adjustable. The encoding is not.

## What happened when we ran it

Full rebind, 421 records, 22 calls, $4.46, 0 truncated. Prompt sha `50337c792883`.

| | before | after |
|---|---|---|
| total bindings | 662 | 841 |
| assert_without_data | 43 | **254 — 60% of the corpus** |
| narrate_an_event | 133 | **211 — 50%** |
| inversion | 11 | **1** |
| parallel_instances | 50 | 21 |
| enumerate | 249 | 151 |
| define_terms | 22 | 38 |
| pose_a_question | 7 | 25 |
| change_across_set | 15 | 23 |

The guard held on VOLUME — 1.3x, not 10x — and failed on DISTRIBUTION. Two jobs
absorbed 465 of 841 bindings. The individual judgments read as defensible; it is the
aggregate that is wrong. A job matching 60% of the library has stopped selecting.

`inversion` collapsing to 1 is a straight regression: beat 27 is "the reversal itself
must be legible" and it now has one candidate.

## What we did about it, and what we want checked

Rather than keep or revert wholesale, we merged the two runs PER JOB on a stated rule —
`~/timeline/pipeline/salvage_bindings.py`:

- **revert** a job the new run floods (over 40% of corpus when the old was not)
- **revert** a job the new run collapsed (under half its former size, from a base of 4+)
- **keep** the new run otherwise

Result: kept new on 15 jobs, reverted 5, 595 bindings, no flooded job, all 61 of the
user's review selections still reachable, validator clean, mean options per beat
6.5 -> 8.2.

## The four questions

1. **Is the per-job merge legitimate, or is it laundering?** Each binding keeps its own
   provenance and no binding was invented or hand-chosen — but we are choosing which run
   to trust per job, and the criterion was written after seeing the results. Does that
   make it fitted to this one outcome?

2. **Is the DRESSING / MECHANIC guard the right cut?** It is the only thing standing
   between "can be made to do it" and "anything serves anything". It held the total and
   not the distribution. Is there a better formulation, or is the problem elsewhere?

3. **Is `assert_without_data` a coherent job at all?** Defined as "a norm, a hypothesis,
   or a limitation" — a beat with no data. Under the new premise almost any template can
   illustrate an assertion, which may mean the job is a catch-all rather than a job. The
   user's review scored it 0 of 12 before any of this.

4. **Should a flood be prevented at bind time rather than detected after?** We flag a
   job over 40% of the corpus as non-discriminating. Nothing stops the binder producing
   one. Would a cap in the prompt help, or would it just push the model to pick 40%
   arbitrarily?

## Files

```
~/timeline/prompts/PROMPT-bind.md          the prompt, sha 50337c792883
~/timeline/grammar/TEMPLATE-FACTS.md       18 claims, what is verified and by whom
~/timeline/SYSTEM.md                       11 stages, what each believes
~/timeline/grammar/bindings.json           the merged result, 595
~/timeline/pipeline/salvage_bindings.py    the merge rule
~/timeline/grammar/picks.json              the user's 61 selections, 24 notes
~/timeline/no-drifting/LOG.txt             every defect and decision, 36 entries
/tmp/bindings.pre-full.json                the pre-rebind state
/tmp/bindings.fullrun.json                 the unmerged new run
```

Read-only. Nothing here needs running. We will do the next rebind ourselves once we
have your read on 1–4.
