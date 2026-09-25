# Combining clips — what is already authorized

## Order of preference

1. **One template, one scene.** Always preferred.
2. **One template, scenes combined.** Still one design language, one tone.
3. **Two templates combined.** **Fallback only**, on the user's instruction of 2026-09-18.

Cross-template merging is last because it is the only case that crosses two design languages.
Every template carries its own tone, and joining two means joining two looks in one beat. It
is also the only case needing a composed-treatment check, so it costs the most to verify.

Reach for it when no single template and no same-template combination serves the job. Segment
18, a member sequence into a counter, is a legitimate use: nothing single serves it. When used,
flag it, because it is the beat most likely to read as assembled.

Three distinct cases. Rules exist for all three, scattered across `scene-tag-rules.json`, the
carousel render log and the Claude/Codex agreement. None is implemented in `candidates.py`.

## 1. Same template, scenes combined for slot count

**Authorized.** Nine families carry `relationship:merge` and `relationship:sequence` in
`scene-tag-rules.json`, authorized 2026-09-17: documentary slideshow, modern photo slideshow,
both memories photo slideshow families, intro slideshow, photo-slideshow, carousel,
carousel-slideshow, text-list carousel.

User confirmation, 2026-09-18: "templates that have scenes clipped can be combined to make a
number issue work." Documentary Slideshow reaching six slots is the worked example.

**Caveat from the source:** these tags "identify group/sequence editorial use, not verified
native merging controls." Editorial permission, not proof the timeline stitches cleanly.

## 2. Native slots beyond what the clip shows

**Authorized, with one hard constraint.** A template's native capacity can exceed what its
preview clip displays. Carousel 01 exposes six native placeholders regardless of how many
appear in any given sample.

From the carousel render work: record the chosen unique count explicitly, and **fill unused
native slots with declared loop repeats rather than inventing additional entities.** The
five-artist pass used one declared Kendrick repeat for the sixth slot.

This is the rule that stops a slot count becoming a lie. Never invent a member to fill a hole.

Corollary, already a standing rule: never read a clip's visible count as the template's
capacity. That is the mechanic-versus-sample error in another form.

## 3. Two clips from different templates — FALLBACK

**Authorized as a fallback only, and it needs its own check.** Segment 18 is the worked case: a sequence of
existing member presentations followed by an existing counter.

Components matching individually does not establish the combination. A composed treatment
needs its own verification covering:
- the full required payload across both parts
- shared units across the seam
- ordered phrase cues
- the transition and timing handoff

From the earlier diagnosis: 417 compound options were generated for segment 18 as an exact
cross product of 139 sequence scenes against 3 counter scenes, each carrying a synthesized
reason string. Nothing checked whether any particular pairing actually composes. Generating
combinations is not the same as verifying one.

## Not implemented

`candidates.py` treats every scene as an independent record with its own capacity. It does not
sum across a template's scenes, does not read native capacity beyond the clip, and does not
form or check compound treatments. All three are known gaps, not decisions.
