# Prompts

Every prompt the system runs. Each is a file because it decides something permanent, and both
of us need to read, diff and version it. Runners load these from disk and hash them, so every
output records which version produced it.

Nothing here is inline in a script. If you change a file here, you change the system.

## The four

### `PROMPT-beats.md` — script to beats
**Runs:** once per video, batched five passages per call, six to eight calls.
**In:** passages of narration with their neighbours as context.
**Out:** per beat — one job from the closed set of 20, entity count and kind, takeaway,
must-be-true, must-be-perceptible, would-be-a-lie, unstated.
**Decides:** where shots begin and end, and what each one has to communicate.
**Key rule:** a beat is one shot. Split only when the subject changes, the measure changes,
the job changes, or an identity statement precedes a claim about it. A shot can develop over
time, so a counter ticking to its total is one beat, not two.
**Validated:** produced 40 beats where your own shot plan had 36, matching passage for
passage across the first five except one editorial disagreement.

### `PROMPT-bind.md` — template to jobs
**Runs:** once per template, ever. Reused on every video and every niche.
**In:** a template's description, use-when, avoid-when, encoding, caveats, capacity.
**Out:** which of the 20 jobs it can serve, each with a mechanism and a quoted line of
evidence from the record.
**Decides:** the candidate set for every future beat.
**Key rule:** judge the mechanic, never the sample. No quoted evidence, no binding.
**Status:** never run. This replaces the 73 hand-picked bindings that were discarded.

### `PROMPT-judge-single.md` — one candidate against one beat
**Runs:** on demand, one candidate at a time.
**In:** a beat's requirements and one template's record.
**Out:** complete fit, weaker fallback, contradicted, or unresolved, with cited evidence.
**Decides:** whether a specific template serves a specific beat.
**Key rule:** first match wins, and a limitation you infer is not a contradiction.

### `PROMPT-judge-batch.md` — the same, twenty at a time
**Runs:** when a whole beat's candidate pool needs judging.
**Same contract as above**, batched for cost.
**Validated:** on the "Seventeen." beat it picked the counter you marked right after Claude
had demoted it, and discriminated correctly across nine counter scenes that share identical
template-level contract text. Passed 7% of 412 candidates, against a tag system that admitted
78%.

## Rules every prompt carries

These are repeated in each file rather than referenced, so a prompt is complete on its own.

- **Judge the mechanic, never the sample.** A demo filled with years is not time-only.
- **A prohibition names a false implication, never a visual family.** "Do not rank them"
  forbids implying they compete; it does not forbid bars or axes.
- **Default to magnitude over tables.** Showing size beats printing values unless the beat is
  genuinely a lookup.
- **Slot counts do not disqualify.** ±33% is workable, scenes combine, native capacity can
  exceed what a clip shows.
- **A portrait slot does not require a picturable subject.** Labels carry the category.
- **Selection is not staging.** Reveal and animation are downstream editing decisions.
- **Absence of evidence is unresolved, never contradicted.**

Each of those exists because a specific mistake was made and corrected.

## What is deterministic instead

Not everything is a prompt, and most of the pipeline is not. Pool loading, capacity maths,
tolerance, scope filtering, job lookup, rotation and timing are all arithmetic in
`match-trial/candidates.py` and `pipeline/shotlist.py`. A model is used at exactly two points:
writing beats, and judging fit. Everything else is a lookup.
