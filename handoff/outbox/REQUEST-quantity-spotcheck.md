# REQUEST — quantity spot-check before the 216-clip run

**Status: NOT AUTHORIZED. Do not send anything until the user says so in their
own words, naming Google Gemini as the destination and these four clips as the
payload.** The previous rerun correctly stopped for exactly this reason.

## Why

Twenty capability records exist so far, across two prompt versions. Every one of
them is a photo slideshow whose only capability is `identity`. The part of the
vocabulary the whole system depends on — telling what a clip ENCODES from what it
PRINTS — has never been exercised, because none of those clips encodes a quantity.

These four do. They are ~2% of the 216-clip batch and they test the ~2% of the
vocabulary that the slideshows could not reach. If the boundary reads badly here,
the records the demanding beats actually need would come back mis-filed and the
whole batch would repeat.

## Prompt

`~/timeline/prompts/PROMPT-describe-clip.md`, unchanged, sha256 `21af96b931c6ddcd5c764e83d770cc5eb5b79dc9789a42e3a15d05ca5b64c64a`.
Same prompt as the 10-clip rerun. Nothing about it is being tested here except
whether its `carries` / `readable` rule survives contact with real charts.

## Output

Write to a NEW file, `capability-quantity-spotcheck.jsonl`, one JSON object per
line, in the run directory. **Do not append to
`~/timeline/handoff/outbox/clip-capability-descriptions.jsonl`.** That file now
holds two runs interleaved, which already caused one wrong comparison on this
side: a diff keyed by id silently kept only the later run and reported ten
records unchanged when six had changed.

## The four clips, and what each one is for

Expected answers are written down BEFORE the run so the check can fail. They are
not instructions to the model and must not be shown to it.

### 1. `archive3-infographic-bar-charts--review-001`

- **clip** `/Volumes/onn. Drive/AE Templates/Archive 3/Infographic Bar Charts/preview_540p_crf22_higher_quality.mp4`
- **existing description** Four vertical capsule bar chart presentation, percentage indicators, lower description blocks, centered title.
- **declared capacity** none
- **testing** bar length encodes size AND the percentages are printed
- **expected** carries must include magnitude. readable must include exact_value. If percentages read as parts of a whole, carries should also include share_of_whole.
- **fails if** carries omits magnitude, or the printed percentages are recorded only as carries with readable left as none.

### 2. `counters-envato--scene-001`

- **clip** `/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/scene-library/clips/counters-envato/counters-envato--scene-001.mp4`
- **existing description** A bold central total accelerates to its target while an outlined COUNTERS ANIMATION label cuts across the digits. Best for a single headline quantity or record total that should dominate the frame.
- **declared capacity** {'focalAssetCount': 0}
- **testing** THE INVERSE TRAP: a single number animating up to its target
- **expected** readable must be exact_value. carries must NOT include magnitude — nothing about the digits' size encodes the value; they are just printed large. carries is plausibly ['none'] or ['identity'].
- **fails if** carries includes magnitude, which would mean animation was mistaken for encoding. This is the single most likely failure and the reason this clip is in the set.

### 3. `archive3-comparison-pack-ae--review-001`

- **clip** `/Volumes/onn. Drive/AE Templates/Archive 3/Comparison Pack - AE/comp-preview_540p_crf22_higher_quality.mp4`
- **existing description** Two-column comparison overlay, four animated stacked rows, centered numbered badges, top title.
- **declared capacity** none
- **testing** two columns, four stacked rows, numbered badges — a difference between two sides
- **expected** structure should be pair or grouped_clusters. If the two sides differ visibly in size, carries includes difference; if the gap is only legible from the badges, readable includes difference. Exactly one of the two, never both.
- **fails if** difference appears in BOTH carries and readable, which is the double-counting the new rule exists to prevent.

### 4. `archive3-infographic-bar-charts--review-002`

- **clip** `/Volumes/onn. Drive/AE Templates/Archive 3/Infographic Bar Charts/preview_540p_crf22_higher_quality.mp4`
- **existing description** Three-group dual vertical bar comparison, wireframe rounded containers, left Y-axis scale, bottom legend.
- **declared capacity** none
- **testing** dual vertical bars WITH A LEFT Y-AXIS SCALE
- **expected** structure should be axis_plot. carries should include magnitude, and rank if the bars are ordered. An axis makes values estimable by position, so readable gets exact_value only if numbers are actually printed on the bars.
- **fails if** structure comes back list rather than axis_plot, or an axis alone is treated as printed values.

## Pass criteria

1. All four validate against `pipeline/ingest_capability.py`.
2. No record puts the same fact in both `carries` and `readable` — the colliding
   pairs are difference/difference, rank/ordering, share_of_whole/proportion,
   membership/grouping.
3. `counters-envato--scene-001` does NOT carry `magnitude`. If it does, the rule
   has not landed and the 216 must not run.
4. At least one record carries `magnitude`. If none does, the model cannot see
   encoding at all and the vocabulary is unusable regardless of wording.
5. No `asserts` line names a subject, an industry, a brand or a person.

A failure on 3 or 4 blocks the 216-clip run. A failure on 2 means the prompt
needs another pass. A failure on 1 or 5 is a per-record fix.

## Cost

~6,200 tokens per clip on the ten-clip runs, so roughly 25k tokens for four.
Against ~1.34M for the full 216.
