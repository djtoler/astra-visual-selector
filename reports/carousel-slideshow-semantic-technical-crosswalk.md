# Carousel Slideshow: semantic and native-capability crosswalk

Date: 2026-09-28
Template family: `carousel-slideshow`
Source project: `Carousel Slideshow.aep`
Purpose: concrete example of the information required to match a VisualTask, an existing template scene and actual media. This is inspection and analysis only; it does not select or render a treatment.

## Reviewed preview scenes

### `carousel-slideshow--review-001` — Fast portrait carousel sequence

- Clip: `/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/selector-prototype/intake/carousel-slideshow/clips/carousel-slideshow--review-001.mp4`
- Reviewed duration: 7.0 seconds.
- Description: 3D portrait-card carousel rotating right to left on a dark background with no text.
- Observed presentation: six focal images; cylindrical orbit; center focal card with depth-of-field supporting cards.
- Intended use: multi-item showcase without captions.
- Avoid when: individual text labels or long pauses per item are required.
- Media constraint: vertical/portrait cards.
- Native uncertainty: which of the eight enabled slots becomes focal inside this seven-second excerpt and whether rotation speed is exposed safely.
- Native mapping: composition verified as `2.Final/Render 01`; native window approximately `0.000–7.000` seconds.

### `carousel-slideshow--review-002` — Landscape image landing and caption

- Clip: `/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/selector-prototype/intake/carousel-slideshow/clips/carousel-slideshow--review-002.mp4`
- Reviewed duration: 4.866667 seconds.
- Description: 3D landscape-card carousel over a starfield with a lower-right script caption.
- Observed presentation: five focal images; rounded landscape cards; continuous orbit and gentle floating drift.
- Intended use: overview of landscape photography, travel locations or artwork with brief text.
- Avoid when: complex multi-line text is required.
- Media constraint: landscape assets, preferably 16:9 or 4:3.
- Native uncertainty: exact per-card text association inside the excerpt.
- Native mapping: composition verified as `2.Final/Render 02`; native opening window approximately `0.000–4.867` seconds.

### `carousel-slideshow--review-003` — Slow multi-card portrait sequence

- Clip: `/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/selector-prototype/intake/carousel-slideshow/clips/carousel-slideshow--review-003.mp4`
- Reviewed duration: 9.933333 seconds.
- Description: wide 3D portrait carousel with stepping rotation, dark background and no text.
- Observed presentation: seven focal images; broad cylindrical orbit; pronounced blur on flanking cards.
- Intended use: fast visual summary or cast/gallery montage.
- Avoid when: each image needs detailed analysis or an on-screen label.
- Media constraint: vertical assets; off-center edges are heavily blurred.
- Native uncertainty: exact slot exposure and whether stepping cadence is configurable.
- Native mapping: composition verified as `2.Final/Render 03`; native window approximately `0.000–9.933` seconds.

### `carousel-slideshow--review-004` — Fast multi-card comparison sequence

- Clip: `/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/selector-prototype/intake/carousel-slideshow/clips/carousel-slideshow--review-004.mp4`
- Reviewed duration: 10.2 seconds.
- Description: close 3D portrait carousel with smooth continuous rotation, a dark background and no text.
- Observed presentation: seven focal images; center card is prominent; dynamic rack focus.
- Intended use: a sequence of people, vertical products or highlights.
- Avoid when: long reading time or a static presentation is needed.
- Media constraint: high-contrast upright assets.
- Native uncertainty: exact slot exposure and safe trim/loop behavior.
- Native mapping: composition verified as `2.Final/Render 03`; native window approximately `9.933–20.133` seconds, immediately following scene 003.

### `carousel-slideshow--review-005` — Landscape image landing and caption, alternate

- Clip: `/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/selector-prototype/intake/carousel-slideshow/clips/carousel-slideshow--review-005.mp4`
- Reviewed duration: 6.5 seconds.
- Description: landscape 3D carousel over a starfield with lower-right script caption and an upward camera exit.
- Observed presentation: four focal images; revolving horizontal cards; transition toward a logo section.
- Intended use: concluding showcase of wide images.
- Avoid when: portrait assets or dense text are required.
- Media constraint: horizontal assets; portrait media may crop or pillarbox.
- Native uncertainty: exact slot exposure and whether the final camera exit can be trimmed without changing the intended transition.
- Native mapping: composition verified as `2.Final/Render 02`; native pre-logo window approximately `24.020–30.520` seconds.

## Verified native composition capacity

The dual native inspection passes agree exactly for the project. The project contains 66 compositions and three final renders relevant to the reviewed family.

### `2.Final/Render 01`

- 1920×1080, 25 fps, 30 seconds.
- Eight independent visual-media inputs.
- Eight maximum simultaneously enabled recursive visual inputs.
- No verified editable text fields.

### `2.Final/Render 02`

- 1920×1080, 25 fps, 38 seconds.
- Six independent visual-media inputs.
- Six maximum simultaneously enabled recursive visual inputs.
- Six editable text fields, with at most two simultaneously enabled.
- Each measured field is named `Your text`, uses LindseySignature at 36 px, and belongs to one of the six Carousel 02 text compositions.
- This is the verified native composition for reviewed scene 002.

### `2.Final/Render 03`

- 1920×1080, 25 fps, 30 seconds.
- Twelve independent visual-media inputs.
- Twelve maximum simultaneously enabled recursive visual inputs.
- No verified editable text fields.

## Pilot verification result

All three original final compositions were rendered through the gated native-template test path with the AEP's existing gray placeholders; the original AEP was not overwritten. All three H.264 files passed full decoding:

- Render 01: 480×270, 25 fps, 750 frames/30 seconds; render time 203.173 seconds.
- Render 02: 480×270, 25 fps, 950 frames/38 seconds; render time 2,638.666 seconds. The render confirms the six timed captions and the logo transition beginning around the measured 30.52-second layer entry.
- Render 03: 480×270, 25 fps, 750 frames/30 seconds; render time 516.155 seconds.

The native renders verify the three distinct motion/layout structures and therefore the composition identities. They cannot provide pixel-identical alignment to the Envato preview because the distributed AEP contains gray `Delete Me` placeholders instead of Envato's sample photos. The five window offsets therefore remain explicitly approximate.

The reusable mapping method is now math-first: use native layer anchors, frame rates and preview duration before rendering. Scene 005 demonstrates the calculation: the technical report places the logo entry at 30.52 seconds, and `30.52 − 6.50 = 24.02`, producing the approximate `24.02–30.52` pre-logo window. Future visual ambiguity should use a still/contact sheet or short targeted probe instead of a full composition render.

## What the two layers establish—and what they do not

The reviewed clip layer establishes the scene's visible communication behavior: portrait versus landscape, focal presentation, background/support cards, motion, text presence, observed focal count, use cases, avoidance cases and transitions.

The native technical layer establishes the available implementation structure: exact compositions, editable inputs, total slots, simultaneously enabled slots, text fields, duration, resolution and frame rate.

Neither layer alone proves a match. In particular:

- observed focal-image count is not the same as total native slot count;
- a template having enough slots does not prove that the required people become recognizable;
- a preview showing four to seven focal images does not identify which of six, eight or twelve source slots drive those moments;
- total duration does not establish safe trim, loop, speed or transition behavior;
- text-field count does not establish which caption appears with which card or its readable character limits;
- media orientation does not establish acceptable crop for the actual selected assets;
- surplus slots need an explicit treatment and cannot be resolved by arithmetic alone.

## Required complementary capability model

For each reviewed scene, add an exact native scene profile that joins the semantic description to its composition and time behavior:

1. **Exact mapping:** reviewed scene ID → native composition ID/path and, when applicable, native time range or variation.
2. **Slot roles:** identify every slot as focal, supporting/background, transition-only, logo or inactive for the reviewed scene.
3. **Temporal exposure:** record when each slot enters, becomes focal, remains recognizable and exits.
4. **Replacement behavior:** orientation/crop behavior, whether slots can be disabled or reordered, and what happens when fewer assets than native slots are supplied.
5. **Text behavior:** bind each text field to its card or global scene role, with simultaneous visibility and measured readability limits.
6. **Timing controls:** distinguish safe trim, loop, speed, freeze and transition points from unverified adjustments.
7. **Treatment evidence:** save actual slot assignments, surplus-slot handling, render receipts and editor verdicts without turning one accepted treatment into an unsupported global rule.

The matcher should then compare one VisualTask against one scene profile and the actual available media. It should produce:

- a proposed slot-by-slot treatment;
- a template-structure verdict;
- a media-availability verdict;
- a combined pairing verdict of `fillable_now`, `conditional`, `incompatible` or `unresolved`;
- exact missing evidence or asset briefs;
- a native replacement-content test request only when an unresolved visual question cannot be answered from existing reviewed evidence.

This preserves both sides of the system: scene descriptions explain what a template can communicate, while native profiles explain exactly how that communication can be filled and adjusted.
