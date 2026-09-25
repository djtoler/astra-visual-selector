# Proposal: replace `entity_count` with a list of media slots

Not a change. A proposal, because it implies re-extracting all 40 beats, which costs
money and is the user's call.

Source: creator references 5 and 6, 122 visual units, 163 media roles. Their
`visualJob`, `presentationFamily` and `entityRelationship` are free text and useless to
us. **Two of their fields are closed vocabularies and we have neither.**

## What they record that we do not

```
editorialRole        what a slot is FOR
   proof 58 · subject 46 · context 30 · atmosphere 14
   comparison 6 · identity 4 · scale 3 · transition_support 2

sourceSpecificity    how specific the media must be
   exact_event_or_entity_required 63
   exact_source_required          50
   representative_media_allowed   45
   decorative_media_allowed        5
```

And critically: **`mediaRoles` is a LIST.** 163 roles across 122 units. A single shot
routinely needs more than one kind of media — a subject and the proof it happened.

## What we record

```
entity_count   one integer
entity_kind    one free-text string
```

One number and one phrase for the whole beat.

## The three things this would fix, with our own beats

**1. Beat 26, which `entity_count` gets wrong.**

```
entity_count 1 · entity_kind "rapper"
"Number one as a lead single. Eleven times. Number one as an album. Nine..."
```

The user confirmed: one entity, six categories. Both numbers are true and no field holds
the second. As slots: one `subject`, six `comparison`. Beat 26 came back
CAPACITY IMPOSSIBLE under the old hard filter for exactly this reason.

**25 of 40 beats already have a compound `entity_kind`** — "rappers (dots on a
plays-per-day chart)", "catalog song categories (Drake's own vs. guest)". The extractor
is already trying to express a structure the field cannot hold, and packing it into
prose nobody parses.

**2. The raw-b-roll flag, currently four booleans set by hand.**

`sourceSpecificity` is that flag as a four-value spectrum, derived rather than
remembered. A beat with any `exact_event_or_entity_required` slot needs sourced footage
of a specific thing; one where every slot is `representative_media_allowed` does not.
Stage 10's job is detection, not retrieval — this is what detection would be made of.

Honest caveat: a naive keyword pass over our beats marks 37 of 40 as naming a real
entity, and the user flagged only 4. **So the mapping is not mechanical and the
extractor would have to make the judgement per slot.** I cannot derive it from what we
already have.

**3. The capacity check would have something real to compare.**

`shape()` compares one template number against one beat number. With slots it compares
a template's capacity against the count of slots of a given ROLE — six comparison slots,
not six of anything. That is the difference between "can it hold six things" and "can it
hold six things being compared".

## What it does NOT fix

**Not the mechanism gap.** Nothing would still evaluate a binding's condition against
the beat. Codex's finding stands untouched: requirements are attached after the slate is
chosen. Slots make the check *possible*; they do not perform it.

~~**Not the four beats both methods failed.** `23`, `29c`, `30a`, `30b` fail because
the library has no treatment for a hypothesis, a scope limitation, an absence or a
scoped definition.~~

**HALF WITHDRAWN 2026-09-21 — see LOG 0046.** 29c and 30a did not fail for lack of
supply. 17 match-cut vessels were bound to their job the whole time and the slate
showed zero of them; the slideshow cap spent the slate on photo packs first. Once the
slate was fixed the user selected 7 of 7 on 29c and 5 of 5 on 30a, **every one a
match-cut vessel.** The `noneAcceptable` verdicts were answers to a question that was
not fairly asked. 23 and 30b remain untested — neither was in the A/B ten.

**Not the multi-shot problem.** 12 of 55 reference patterns span 2 to 5 shots. Slots
describe one shot better. They say nothing about a figure that unfolds across five.

## Cost

Re-extraction of all 40 beats — one paid run, and `PROMPT-beats.md` changes. ~~It is the same run that would close the 47% of narration with no beat~~ —
**WITHDRAWN 2026-09-21. That 47% came from a hardcoded 823.5s in the run summary;
the narration is 480.9s and coverage is 91%. Only passages 29 (10.0s) and 09
(7.4s) hold more than 5s of uncovered narration. Re-extraction buys almost no
coverage, so the cost must be justified by the slot fields alone.** It is still
the same run that would add `reveal` if that is wanted. **Do it once, with everything decided.**

Downstream: `shape()`, `capacity_rank()` and `needs_spatial()` all read `entity_count`
and would need to read a slot list. `grammar/beat-flags.json` loses `rawBroll` as a
manual field if specificity is extracted instead.

## The question for the user

Adopt `editorialRole` and `sourceSpecificity` as-is, with their exact vocabularies, or
define our own? Theirs are observed from 122 real units on the channel we are mimicking,
which is far better evidence than anything we would invent. Against that, they were
produced by three models with drift elsewhere in the same files, so the two closed
fields may be closed by accident rather than by design.

My read: adopt them unchanged. If they turn out wrong we will find out the way we found
out about everything else, and a vocabulary borrowed from the target is a better starting
point than one derived from our own reasoning — which is how we got `carries` and
`readable` overlapping.
