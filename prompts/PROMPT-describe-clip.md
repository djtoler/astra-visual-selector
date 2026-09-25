# PROMPT-describe-clip

Produce a **new, ID-keyed capability description** for each After Effects scene clip, so it
can later be matched to a narration beat. Run against a video-understanding model, one
clip per call. Take the eligible scene IDs from
`/Users/dwaynetoler/timeline/no-drifting/clips-to-describe.txt` (367 listed IDs), then
resolve each ID and its **cut scene clip** in the `after_effects` items of
`/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/scene-library/approved/approved-list.json`.
The paths printed next to IDs in the input list often point to the full source preview;
they are not the clip to analyze. Pass the exact listed scene ID to the model; never
infer an ID from a filename or template name.

## This adds. It does not replace.

The existing description stays exactly as it is. It says what the clip **looks like** —
"Floating portrait photo card, part 3 of 14, slow push-in, blurred photo stack
background" — and that is genuinely useful for a human picking between two similar
scenes in a review gallery.

What it cannot do is tell a matcher what the clip can **assert**. That is what this pass
adds as a separate record in an append-only log, keyed by the existing clip ID. Nothing
in the approved export, original description, scene catalog, or video is overwritten.
The records can be matched and combined later by ID, after review:

    description        what it looks like     unchanged, human-facing
    capability record  what it can assert     new, machine-facing, separate log

Do not restate appearance in the capability record. Do not correct or rewrite the
existing description. If the existing description is wrong, say so in `unclear` and
leave it alone — a human decides.

The output vocabulary below is the same vocabulary narration beats state their
requirements in. That is the point: matching becomes a set comparison, not a judgment.

---

## THE ONE RULE THAT MATTERS MOST

**Describe the mechanic. Never the sample content.**

The clip is a template filled with placeholder data for the demo. Every photo, name,
number, label and colour in it is replaceable. Your description must be true of the
template no matter what it is later filled with.

- A clip showing three basketball players is **not** "a basketball comparison." It is
  "holds three subjects side by side."
- A clip counting up to 1,200,000 is **not** "a view-count animation." It is "holds one
  quantity, animates it to its final value."
- A clip captioned "PARIS 1924" is **not** "a historical travel scene." It is "holds one
  subject with a short label."

**Never put a subject noun in your output.** No sport, no music, no place, no industry,
no person. If your description would stop being true when the demo content is swapped,
it is wrong.

The video proves what is visible, not what the native template lets an editor change.
Do not assume text or media is replaceable, colours are adjustable, the layout can grow,
or timing is elastic. Describe the visible mechanic; put unverified native controls in
`unclear` so a separate native inspection can resolve them. Never turn an observation
from the demo into a claim of proven editing capability.

---

## DEFINITIONS

**Slot** — a place a distinct subject can go. Two photos of the same person in one scene
is one slot if the scene is about one subject, two if they are compared.

**slots_at_once** — how many distinct subjects are on screen simultaneously at the
fullest moment. A four-up grid is 4. A single card is 1. A title card with no subject
is 0.

**slots_total** — how many distinct subjects pass through across the whole clip. A list
that scrolls through 14 entries showing 5 at a time is `at_once 5, total 14`. If nothing
scrolls or cycles, total equals at_once.

**If the clip loops**, count one cycle only.

**growable** — true only when a repeated structure visibly accommodates additional
items, false when a visibly fixed layout has no repeat mechanism, null when the preview
cannot establish this. This is an observed structural assessment, not a verified native
capacity or promise that extra items can actually be added.

---

## OUTPUT

Return one JSON object. Every field is required. Use only the listed values.

```json
{
  "id": "<the id you were given, unchanged>",
  "slots_at_once": 0,
  "slots_total": 0,
  "growable": null,
  "structure": "single",
  "staging": "all_at_once",
  "carries": [],
  "readable": [],
  "implies": [],
  "asserts": "",
  "text_slots": 0,
  "media_slots": 0,
  "unclear": []
}
```

**structure** — how the subjects are arranged. Exactly one:
`single` `pair` `list` `grid` `grouped_clusters` `axis_plot` `nested` `sequence`

**staging** — how they arrive. Exactly one:
`all_at_once` `builds_up` `reveals_in_turn` `accumulates_to_total` `unknown`

### `carries` and `readable` are not the same question

This is the distinction the whole record turns on, so decide it deliberately:

> **`carries`** — the relation is in the VISUAL FORM. Length, height, position, area,
> colour. You would still see it **with every label and number removed.**
>
> **`readable`** — the viewer gets it by READING. Printed values, printed ranks,
> written labels. Remove the text and it is gone.

A treatment may do both, one, or neither. Four faces in a grid with a number under each
is `readable: exact_value` and `carries: identity` — the numbers are printed, but the
faces are all the same size, so nothing about the numbers is in the form. Four bars of
different heights with no labels is the reverse: `carries: magnitude` and
`readable: none`.

Several terms appear in both lists, or read as near-synonyms across them. Use this rule
to place them — the question is always *form or text*:

| the visual encodes it | the viewer reads it |
|---|---|
| `carries: difference` a visible gap | `readable: difference` a printed delta |
| `carries: rank` who is ahead is visible | `readable: ordering` printed 1, 2, 3 |
| `carries: share_of_whole` a visible part of a visible whole | `readable: proportion` a printed % |
| `carries: membership` a visible grouping | `readable: grouping` a group heading |

**`rank` is COMPARATIVE rank, never sequence position.** Ten of the fifteen records
this prompt tagged `rank` were scrolling text lists — items passing through a frame in
turn. That is the order they ARRIVE in, not a claim that the first beats the last, and
the model was following this section when it said so. The wording was wrong.

Ask: if two items swapped places, would the visual be asserting something DIFFERENT
about them? On a bar chart, yes — the taller one is ahead. On a scrolling list, no —
it is the same list in a different order.

Sequence position is already recorded, twice, and does not belong here: `structure:
sequence` says the items form a sequence and `staging: reveals_in_turn` says they
arrive one at a time. A scrolling list gets those two and **no** `rank`.

If the order is only apparent because each row is numbered, that is
`readable: ordering`. If a layout genuinely encodes who is ahead AND prints the
positions, say both — in their own fields.

**carries** — what relations between subjects this clip can make visible IN ITS FORM.
Zero or more. Include one only if a viewer could still see the relation with the labels
stripped off.

**A RELATION COUNTS WHETHER IT IS SHOWN IN ONE FRAME OR ACROSS THE CLIP.** This is the
most important instruction in the section and it was missing until 2026-09-21.

Every definition below used to read as a claim about a single frame — two shapes
crossing, several bars pooling — while everything temporal lived in `staging`. A
relation the clip *performs* fell between the two fields and was recorded by neither.
Measured consequence: across 396 records and three versions of this prompt,
`overlap`, `aggregate` and `absence` were assigned **zero times each**, while nine
records were staged `accumulates_to_total` and a scene built expressly to show an
intersection came back as `difference`. A term never once used is more likely
inoperable than universally absent.

So: if the clip ENDS somewhere, judge what it ends on. If groups reduce, if parts
gather, if an item leaves, that is the relation — and you should usually record the
matching `staging` too. Both fields, not one or the other.

- `magnitude` size differences are visible as size
- `share_of_whole` a part reads as a proportion of a total
- `rank` who is ahead is visible in the layout — comparative, not arrival order
- `change_over_time` movement between states is visible
- `difference` a gap between two things is visible as a gap
- `parity` two or more things read as THE SAME — deliberately equal, not merely
  unranked. Matched heights, a shared line, a visible balance. Sameness asserted, not
  sameness left unstated.
- `aggregate` several things pool into one. In one frame as parts inside a total, OR
  across the clip as items gathering, stacking or summing into a single figure.
- `derivation` one value is visibly computed from another — a connector, an arrow, a
  formula, a value handed from one node to the next.
- `membership` belonging to a group is visible
- `overlap` the intersection of two sets is visible. In one frame as two sets crossing
  with their shared members in the crossing, OR across the clip as two sets reducing
  until only the members common to both remain.
- `absence` something reads as MISSING, distinct from a zero. Present as a gap, an
  empty slot or a break in a run — or shown by an item leaving and not being replaced.
  A zero is a value; an absence is the lack of one.
- `identity` who or what a subject is, is visible
- `none` presentation only, carries no relation

**readable** — what a viewer gets by READING text on screen. Zero or more:
`label` `statement` `exact_value` `ordering` `proportion` `difference` `grouping`
`position_in_sequence` `none`

- `label` a short name or title identifying what is on screen — a person's name, a
  category, a heading. The text says WHO or WHAT.
- `statement` a phrase or sentence read as a claim, a question, a rule or a
  definition. The text IS the message, not a caption on something else.
- the six below are all DATA read from text: `exact_value` a printed figure,
  `ordering` printed 1 2 3, `proportion` a printed %, `difference` a printed delta,
  `grouping` a group heading, `position_in_sequence` an index.

**`label` and `statement` were added 2026-09-21 and the omission was serious.** Every
earlier value was a data relation, so a template whose whole purpose is putting a
sentence on screen had nothing to claim and correctly returned `none`. 137 of the 223
records with text slots — 61% — read `none`, including every scene of a text carousel
that does nothing but scroll statements. The register could not say that a template
displays prose, which is exactly the capability the corpus is shortest of.

Keep the two apart. A lower third naming a person is `label`. A card asking the viewer
a question is `statement`. A beat that must state a rule needs the second and is not
served by the first, and that distinction is the whole reason there are two terms.

**implies** — what this clip unavoidably suggests even when that is not intended. This
is how a beat rules a treatment out, so be strict. Zero or more:
`ranking` `competition` `chronology` `causation` `completeness` `equality`
`independence` `none`

`independence` was added 2026-09-21: a layout can suggest two figures are unrelated
facts standing side by side. A beat whose whole point is that the second number came
FROM the first is ruled out by it, and there was no way to say so.

  A left-to-right row of bars sorted by height implies `ranking` whether or not the data
  is a ranking. A podium implies `competition`. A left-to-right timeline implies
  `chronology`. A pie implies `completeness`.

**asserts** — the new capability description: one sentence, present tense, mechanic
only, no subject nouns. What is visibly true of anything shown in this clip. Under 25
words. This is **not** the existing human-facing `description` field.

**text_slots / media_slots** — how many distinct, visible candidate text positions and
image/video wells the clip shows. Count appearances, not verified editable AE fields;
actual native editability and capacity remain unknown until inspected.

**unclear** — anything you could not determine. Name the field. An empty list means you
are confident about every field from the video. Include `native_editability` whenever
replacement controls have not been verified separately. Guessing is worse than saying
so here.

---

## WORKED EXAMPLES

A four-up portrait grid with a number under each face:
```json
{"id":"example-a","slots_at_once":4,"slots_total":4,"growable":false,
 "structure":"grid","staging":"all_at_once",
 "carries":["identity","membership"],"readable":["exact_value"],"implies":["none"],
 "asserts":"Presents four subjects together, each with its own printed number, at equal visual weight.",
 "text_slots":8,"media_slots":4,"unclear":["native_editability"]}
```
Note two things. `readable` has `exact_value` because the numbers are printed, but
`carries` does **not** have `magnitude` — the faces are all the same size, so nothing
about the numbers is visible as size. And the four-up layout is `carries: membership`,
a visible grouping, **not** `readable: grouping` — no heading names the group, the
arrangement does. Form goes left, text goes right. That distinction is the whole job.

A bar chart whose bars grow from a shared baseline:
```json
{"id":"example-b","slots_at_once":6,"slots_total":6,"growable":true,
 "structure":"list","staging":"builds_up",
 "carries":["magnitude","rank","difference"],
 "readable":["exact_value"],"implies":["ranking"],
 "asserts":"Holds several labelled quantities on one shared scale, each bar's length showing its size.",
 "text_slots":12,"media_slots":0,"unclear":["native_editability"]}
```
Note: `readable` is **only** `exact_value`. The ordering and the gaps between bars are
real and important — they are already recorded, as `carries: rank` and
`carries: difference`, because you see them in the bar lengths. They would go in
`readable` only if the chart printed a rank number or printed the delta.

**Both fields at once is correct when both are genuinely there.** A bar whose fill shows
a share AND a printed "47%" beside it is `carries: share_of_whole` and
`readable: proportion` — two real capabilities, because a beat that needs the share to
*look* like a sliver and a beat that needs the number *legible* are different beats, and
this clip serves both. Three visible clusters with printed labels is likewise
`carries: membership` and `readable: grouping`.

The error to avoid is not recording twice. It is recording in the WRONG field: putting
something you can only see in the form into `readable`, or something only printed as text
into `carries`. Ask of each entry, separately: with every label stripped off, is it still
there? With the visual flattened to plain text, is it still there? Whichever answers yes,
gets it. Sometimes both answer yes.

A single photo card with a slow push-in and a caption:
```json
{"id":"example-c","slots_at_once":1,"slots_total":1,"growable":false,
 "structure":"single","staging":"all_at_once",
 "carries":["identity"],"readable":["none"],"implies":["none"],
 "asserts":"Holds one subject with a short caption and no comparison to anything else.",
 "text_slots":2,"media_slots":1,"unclear":["native_editability"]}
```

### Wrong, for contrast
```json
{"asserts":"A sleek modern slideshow perfect for showcasing your team or portfolio."}
```
Marketing copy, names a subject, says nothing a matcher can use.
```json
{"asserts":"Compares three NBA players' scoring averages."}
```
Describes the demo content. The template does not know what an NBA player is.

---

## INPUT

```
id:                   <exact scene id from the approved export; copy unchanged>
existing description: <kept, unchanged, whatever you answer. Shown for context only.
                       It describes appearance; do not copy it, do not correct it,
                       do not let it override what you can see in the clip.>
clip:                 <the video>
```

Watch the whole clip before answering. Return exactly one JSON object with the same
`id` you were given and all required fields above. Do not output an edited copy of
the existing description, another clip's ID, a merged catalog record, or prose.

---

## HOW THE RESULT IS LOGGED (caller, not the model)

The caller iterates only the IDs in `clips-to-describe.txt` and looks each one up in
the approved export's `after_effects` scene records. Pass one exact ID, its current
description, and its cut scene clip to the model per call. The older `/clips/...` URLs
resolve under
`/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/scene-library`;
the reviewed-intake clip paths are already absolute. Before calling the model, check
that the supplied IDs are unique and the clip files exist.

Validate the returned JSON, especially that its `id` matches the input ID. Append one
line per successful attempt to
`/Users/dwaynetoler/timeline/handoff/outbox/clip-capability-descriptions.jsonl`.
Each line is the returned capability record plus caller-stamped `clip_path`,
`prompt_sha256`, `model`, and `generated_at` fields. Keep failed attempts and retries
traceable; a retry appends a new line rather than silently replacing the old one.
The model cannot save a file merely because this prompt tells it to; the caller must
do the validation and append. Do not merge records into the approved catalog in this
pass. Any mismatch with an existing `axes` or capacity field is a review flag for
the later matching step, not an automatic correction.
