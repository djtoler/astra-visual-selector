# 6. Catalog coverage and gaps

Measured against the approved catalog, the infographic and cinematic-scatter systems, and the owned template drive.

**The headline: the gaps are not template families. They are four missing capability fields and one crosswalk table.** Nothing here recommends a purchase.

> **Corrected 2026-09-16, second pass.** I surveyed only four areas of the project on the first read and stopped. Twelve of the twenty top-level directories were never opened, and most of what this report calls missing was already there. See the correction below before reading the gaps.
>
> **`ae-template-automation/profiles/`** holds 12 per-template motion profiles covering 10 of the 14 approved templates. They carry `pacing.usable_reading_time_s` measured per template, a **graded** eight-role documentary vocabulary with `not_supported` exclusions, `style.pace` and `style.density`, `narration.suitability` with observed on-screen word counts, standalone-versus-transition-dependent scene ids, full slot capacity, and `selection.reject_if` with `choose_instead`. Every claim carries a confidence and a sha256 staleness fingerprint.
>
> **`magnates-motion-system/`** holds `MOTION-SPEC.md` and `motion-presets.json`: measured entrance and exit seconds per preset, drift phases, six normalized staging zones, an explicit easing model, and a 4-to-8-frame stagger rule for multiple entrances. That is event-beat data for the person-motion engine.
>
> **`scene-manifest-system/`** defines the render job contract a production handoff has to conform to.
>
> The prototype now reads the motion profiles. A template's measured usable reading time governs the legibility gate, above both raw scene duration and my corpus-derived 1.5s floor, because scene durations include shared transition handles and the usable core is shorter.
>
> **What stays true:** `aep.colour_control` is recorded as `unknown` on 10 of 12 profiles, so the `.aep` parse in this package is still additive rather than duplicative. And per-event beats *inside* an After Effects template scene still do not exist anywhere; what exists is per-scene pacing and usable reading time, which is more than I credited but is not the same thing.
>
> **Original note, 2026-09-16 first pass.** Answer `23_prototype_capability_clarifications` closes or downgrades three of the gaps below. `independentTiming` is confirmed, so gap 1 is an annotation task rather than a capability gap. Gap 2 has a fallback — a simple screenshot is accepted when it communicates the point — and the named source collections include `Documents & Screens / Screen_Mockup` and `Scrolling_Screen_Animations`. Gap 4 has a fallback too, simple words on a background, and `Archive 2 / Lists & Titles / text-carousel` exposes 8 text slots and a colour control, which serves it properly. The sections below are left as written with these notes inline, so the reasoning stays visible.

## Coverage by treatment class

| Treatment class | Approved coverage | Assessment |
|---|---|---|
| `infographic` | 57 profiles | Strong. Capacity, data mapping, encoding audit and `avoid_when` all recorded. |
| `spatial_or_cinematic_3d` | 9 layouts | Strong and well documented, with implementation evidence cited to source lines. |
| `counter_or_numeric` | `counters-envato`, 9 scenes | Adequate for one verified magnitude. Explicitly no image or video slot. |
| `montage_gallery_or_carousel` | `four_or_five_slot_sequence` plus slideshow families | Adequate. |
| `portrait_or_cutout` | `single_portrait_with_side_text`, `two_person_portrait`, `three_person_portrait` | Adequate at one to three entities. |
| `evidence_or_document` | `magazine_or_document_presentation`; `screenshot_or_evidence_presentation` inherits from it | **Thin.** See gap 2. |
| `after_effects_scene` | 14 templates, 185 scenes | Broad, unevenly annotated. |
| Direct footage and interview | 1 b-roll retrieval profile | **Thin as records.** See gap 3. |
| Plain readable text | none | **Missing.** See gap 4. |

Two families in `approved-template-family-map.json` are empty and awaiting your selection: `two_dimensional_plot` and `three_dimensional_plot`. The scatter catalog has 9 profiled layouts that could populate the 3D family.

---

## Gap 1. Event beats — REFRAMED, see the note

> **This gap was framed backwards.** `deliverables/astra-template-tests-2026-09-16` rebuilt passages 15, 17 and 20 from real template elements and passed 22 frame-verified reveal and hold checks. Its finding: a template's native schedule routinely *violates* the required holds, so the working method replaces that schedule with a cue schedule derived from the contract, including independent per-element visibility control.
>
> So beats are not read out of a template and fitted around. They are authored from the contract and imposed on the template. The gap is a schedule-authoring workflow, not a metadata-extraction task, and a version of it already exists and has been rendered.
>
> This also means the four approved adjustments are not the ceiling. Schedule replacement is a fifth class, recorded as `COR-0012` and pending approval.

### Original framing, kept for the record

**Priority: high, and downgraded from highest.** The *capability* is confirmed by answer 23 — image, value or highlight can be scheduled to the relevant phrase. What is missing is the *data*: per-scene event times and movability are unrecorded, and the mappings still have to be authored and checked. That is an annotation task, not something to build or buy.

Timing control today is whole-scene retime: `allowSpeedUp`, `allowSlowDown`, `outputDuration = nativeDuration / playbackRate`, available on every approved scene. That fits a scene to a duration. It cannot land a highlight on a word.

**What is missing.** Per-scene internal event times, event types, and whether each beat can be moved independently of the rest of the scene. Without them a candidate can only be checked for total duration, and the alignment gate degrades to a human judgement every time.

**What it would need.** For each approved scene: a list of `{eventId, nativeTimeSeconds, eventType, movable, boundToSlot}`. Derivable in part from the existing per-scene renders, which already exist as MP4s, and in part from the `.aep` structure.

**Source or build.** Build. No purchased template ships this.

## Gap 2. A document-native evidence container

**Priority: high.** Three of your thirty passages are evidence jobs and three name a document presentation. `screenshot_or_evidence_presentation` has no candidates of its own — it inherits from the portrait and magazine families and adds a note that the inserted material must stay readable long enough to substantiate the narration. That is a requirement without a container.

**Why the existing options fail.** The magazine family presents an artifact as an object in a scene. A screenshot needs to be presented as a *surface to be read*, held still, at legible size, often with a specific line highlighted. Those are different jobs.

**You already identified this.** On passage 15.02: *"good selections. will also be adding a group of document templates which will be a good choice for this type if its a screenshot."*

**Likely owned answer, unchecked.** The drive's `Archive 2 / Documents & Screens` group holds a YouTube UI mockup, a screen mockup, a computer-monitor pack and scrolling screen animations. None is documented in the drive README and none is in the approved catalog. **Inspect these before sourcing anything.**

## Gap 3. Direct treatments are not catalog entries

**Priority: high, and cheap.** `not_forcing_a_template` is a hard gate, and your rule `video_competes_with_stills` requires footage in the slate when it shows the named people or event. But the catalog holds one b-roll retrieval profile and no records at all for an archival cut, an uncut interview hold, or a single image on screen.

A treatment with no record cannot be scored, ranked or placed in a four-candidate slate. So the gate that says "do not force a template" currently has nothing to hand the decision to.

**What it would need.** Four `direct_media_treatment` capability records with the same contract shape as a scene: accepted media, entity capacity, duration behaviour, evidence obligation ceiling, and the narration jobs each can serve.

**Source or build.** Build, and it is an afternoon of writing rather than an engineering task.

## Gap 4. A low-motion readable text card

**Priority: medium.** Passage 17 needs three clauses read and remembered, and your feedback rejected one candidate outright as *"not made for reading, more for viewing"* and called two others *"a little too active for expecting the viewer to read rules."*

**Why existing options fail.** Every approved AE scene in the relevant families presents media with motion, and this passage has no media.

**What it would need.** A dark cinematic text card holding two to four clauses, each appearing on its own phrase, with motion restricted to opacity and a slow settle. No camera move, no card flight, no kinetic typography.

**Source or build.** Build. This is small, the style constraints are strict, and the drive's typography packs are kinetic by design, which is the opposite of the requirement.

---

## Gap 5. Three fields, not a family

These block correct rejection rather than correct selection, which makes them cheaper and more urgent than any container.

| Missing field | Why it matters | Evidence |
|---|---|---|
| **Motion activity** | The `readability` rule cannot be applied without it. Your passage-17 feedback distinguishes "wrong kind of scene" from "right kind, too active" — a threshold, not a boolean. | Feedback 17.01 |
| **Text-slot capability** | Whether a container can name an entity, date or source. Twelve drive projects have 8-plus media slots and zero text slots, including a named style reference. | `.aep` parse |
| **Evidence obligation ceiling** | The strictest proof obligation a container can honour. A scene that crops, stylises or overlays evidence cannot serve `exact_source_required`. | Dominant corpus failure mode at 19 per 100 conditions |

A fourth belongs with them, surfaced by case C in the demonstrations: **portrait legibility at capacity**. Profiles record how many subjects a layout *can* hold, not the count beyond which its portraits stop being identifiable. Your passage-14 feedback turns on exactly that distinction.

---

## Gap 6. The vocabulary crosswalk

Not a template gap, and the single highest-value task in the plan. Three job vocabularies are in use across the cases, the scene catalog and the reference analyses, plus two `intents` vocabularies in the generation systems. Only `quantify` and `compare` mean the same thing in more than one. Until one crosswalk exists, job-to-container matching is inference rather than computation.

---

## Unfilled annotation, not missing capability

Distinct from the gaps above, because the containers exist and their records are simply incomplete:

- `focalEntityCount` on 14 of 185 approved scenes
- `scriptMatching` on 72 of 185
- `function` on 112 of 185
- Both plot families in the approved template map empty
- One feedback record missing (`30.01`)

Populating `focalEntityCount` alone would do more for selection quality than any new template, because entity capacity is the cleanest structural filter in the reference data.

---

## Envato sourcing

**No purchase recommended.** Every gap above has either an owned candidate that has not been inspected, or is a build task too specific to buy.

If, after inspecting `Archive 2 / Documents & Screens`, the document container is still missing, the search language would be:

- "document screenshot reveal after effects dark"
- "article highlight annotation template"
- "evidence document zoom highlight"

And only then. The requirement is a readable surface with a controllable highlight, which is a narrow enough ask that most marketplace results will be the magazine-object treatment you already have.

---

## What changed from my pre-access draft

My earlier report measured raw drive inventory and named a two-entity comparison container as the top gap. Against the actual approved catalog that is wrong: `01_finals_head_to_head` is an approved two-subject comparison profile, and the scatter catalog adds `Exact two-point duration ratio` and `Two-portrait qualitative comparison on a photographic stage`. The comparison need is covered. `Comparisons 01.aep` on the drive is still worth ten minutes for the empty `two_dimensional_plot` family, but it is no longer the priority.
