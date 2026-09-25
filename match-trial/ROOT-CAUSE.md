# Root cause: beat match trial, 18 Sep 2026

Feedback: B1 counter marked right (I ranked it second). B2 all three right, plus "a graph
would work as well" and a redundancy complaint. B3 first two right, height ruler wrong
(agreed), plus "why are we not visually communicating the rate as clear as possible". B4 no
card verdicts, and a list of templates I never showed.

## 1. I searched half the library

| | records |
|---|---|
| described library | 468 |
| what I loaded | 249 |
| never considered | 219 |

I built candidates from `approved/catalog.json`. That file holds 185 of the 283 main scene
records, 55 infographics and 9 cinematic 3D, and **none** of the 119 newer intake scenes.

All 34 carousels live in the intake collection. Documentary Slideshow has 8 scenes in the
library and 5 in `catalog.json`. So neither was rejected. Neither was loaded.

This is a repeat. Yesterday I claimed scrolling-screen was absent from the catalog, Codex
corrected me from the trace, and I wrote a memory saying to check the snapshot including
`intakeScenes` and never to inspect `approved/catalog.json` alone. I then used
`approved/catalog.json` alone.

It also invalidates the clip finding I reported. All 283 main-library records and all 119
intake records have a playable clip on disk. Infographics genuinely have no motion render;
everything else does.

## 2. Capacity is multi-dimensional and I collapsed it to one number

My filter read the first key present from a fixed priority list, then compared that single
number to the beat's entity count.

- `55_best_vs_value` is `{subjects: 2, metrics: 6}`. For a beat with six independent labelled
  counts, **metrics is the matching axis**. My code read `subjects`, got 2, and dropped it.
- `54_trade_package_panels` is `{packages: 7, ...}`. `packages` was not in my key list at all,
  so its capacity read as unknown.

Reading one axis of a multi-axis record is not a capacity check. It is a coin flip over which
key happens to sort first.

## 3. No slot tolerance, and anything under capacity was discarded

The filter kept `cap == n` or `cap > n`. Below-capacity records were dropped outright, and
exact matches were ranked above near matches. For B4 at six slots, your ±2 rule admits
`51_debut_leaderboard` (7 entries), `53_lineup_rotation_columns` (8 entities) and
`54_trade_package_panels` (7 packages). I showed none of them.

**Two things to settle.** The two tolerances you gave disagree: ±2 slots admits 4 through 8 at
n=6, while ±25% admits 4.5 through 7.5, so the 8-entity layout is in under one and out under
the other. I read you as meaning the union, but say so.

And this rule was previously refused in writing. `media_workflows.md` records "The eight-slot
alternative is conditional on the actual item count and verified treatment, not a global
slot-tolerance rule." I proposed a tolerance, Codex rejected it as unapproved invention, and I
withdrew it. Your instruction reverses that, which is your call, but it should be recorded as
a reversal rather than quietly applied.

## 4. Scene combination is not modelled anywhere

Every After Effects scene was treated as an independent record carrying its own focal count.
Nothing sums capacity across clipped scenes of one template, and no field expresses it.

Documentary Slideshow: 8 scenes, five of them "standalone entity presentation with one focal
image", which is where your six comes from. My pipeline can only ever see a one-slot scene.

## 5. My prohibitions banned encoding families instead of false implications

This is the one that explains B1, B2 and B3 together, and it is a fault in how I wrote the
intent records, not in the catalog.

- **B1.** I wrote "would be a lie: decoration, anything that invites comparison," then used it
  to demote the counter to second. You marked it right. The count-up was never a lie. I
  promoted a stylistic preference into a prohibition and it eliminated the correct answer.
- **B2.** I wrote "would be a lie: one shared axis," and excluded every chart in the catalog.
  You say a graph works. The lie is implying the four artists compete, not the axis itself.
- **B3.** I wrote "must not share a scale" and concluded text. Your correction is the sharpest
  one: if the per-verse rate is the load-bearing figure, text is the weakest way to carry it.
  Two separate labelled magnitude encodings communicate a large gap, or a near tie, far better
  than numbers on screen. "Do not put two units on one axis" does not imply "do not encode
  magnitude."

A prohibition must name the false implication, never the visual family. Written the other way
it removes correct candidates and looks principled while doing it. That is the same defect as
a hand-authored contract: an authored constant nobody can check.

## 6. The slate was redundant

All three B2 candidates were portrait-card layouts. I argued to Codex for stratifying a slate
by visual mechanism rather than ranking, then did not apply it to my own.

## What changes

1. Build candidates from the 468-record description inventory, never `approved/catalog.json`.
2. Match every capacity axis a record declares, not the first key in a list.
3. Apply the tolerance as a union of ±2 slots and ±25%, admit under-capacity, flag beyond.
4. Add combined-scene capacity for templates whose scenes are clipped from one project.
5. Rewrite every "would be a lie" to name the false implication. Magnitude encodings are back
   in scope for B2 and B3.
6. Fill a slate by distinct mechanism before a second instance of any mechanism.
