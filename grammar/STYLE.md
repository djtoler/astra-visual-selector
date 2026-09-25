# Style layer

Separate from the grammar, and it must stay separate. The grammar answers *which treatment
serves this job*. Style answers *does it look like our channel*. If look constrains treatment
selection, correct treatments get rejected for aesthetic reasons.

Not designed yet, deliberately. A house style cannot be designed against templates nobody has
seen assembled. Run one video through the grammar, watch it, then design against evidence.

## The known conflict

After Effects templates carry a `tone` field and the tones are mutually hostile:

| family | tone |
|---|---|
| Documentary Slideshow | warm, papery, contemplative; a light table |
| Documentary Promo | aggressive, editorial-zine; street-poster energy |
| Intro Slideshow | warm, nostalgic; a shoebox of photographs |
| Counters | clean, bold, modern, technical |
| History and Documentary | archival, investigative; a dim room of stored records |

Every one of those can be the correct answer for its job. Drawing across them inside one video
reads as stock assembly, which is the thing that separates this from the reference channels.
Five of fourteen families have no tone recorded at all.

## Parameterizable axes — what is actually exposed today

Verified, not assumed.

| axis | where | state |
|---|---|---|
| glow | infographic `style.glow_presets` | four presets: original, off, wardrobe, reference. All 55 profiles. |
| motion | infographic `motion.presets` | slide left/right, drop up/down, plus still. Whole-scene only. |
| background | `background_manager.py` | replaceable, prepared to 3840x2160, deterministic upgrade path with optional AI upscale |
| typeface | After Effects | swappable, proven in the carousel work (Bebas to Hanson Bold, registered by PostScript name) |
| media | everywhere | swappable. Established. |
| **palette** | nowhere | **not exposed.** No color tokens in any profile or catalog record. |
| **grade** | nowhere | **not exposed.** Would have to happen at composite. |

Palette is the gap that matters most, because color is what makes families read as a set.

## The binding field

Every job-to-treatment binding carries `styleAdaptation`, empty until the house style exists.

```json
"styleAdaptation": {
  "status": "unassessed",
  "exposes": [],
  "needs": {},
  "notes": ""
}
```

- `status` — `unassessed`, `parameterized` (all needed changes are presets or swaps),
  `manual` (needs per-use hand work), `blocked` (cannot be made to match).
- `exposes` — which axes this template actually offers, from the table above.
- `needs` — axis to target value, filled once a house style exists.
- `notes` — anything a person must know before using it.

`status: manual` is the number that decides throughput. A binding that needs hand work every
time cannot run at twenty a day; one whose changes are all presets and swaps costs once.

## Colour: breadth is the answer

User instruction, 2026-09-18. When a treatment is not a colour match by default:

1. Check whether its colour can be changed meaningfully.
2. If it can, adapt it.
3. If it cannot, take the best remaining option, preferring one whose colour *can* be changed.

So colour-changeability is a tiebreak among otherwise valid treatments, never a filter. This
is what the breadth from the binding stage is for: a job with several bound treatments can
absorb a colour mismatch by moving to a sibling. A job bound to one treatment cannot, which is
a third reason thin bindings are a risk.

Palette is not exposed anywhere today, so step 1 currently has no data to answer from. Until
it does, record the question rather than guessing the answer.

## Rule

Style never eliminates a candidate during selection. A mismatch sets `styleAdaptation.status`
and is resolved after the treatment is chosen, or the treatment is rebound deliberately with
the reason recorded.
