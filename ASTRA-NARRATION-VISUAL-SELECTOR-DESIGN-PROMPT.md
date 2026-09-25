# Astra prompt: deterministic narration-to-visual planning system

You are working inside this existing project:

`/Users/dwaynetoler/Documents/ChatGPT/Polish`

Your job is to design a practical, increasingly deterministic system that maps documentary narration to the right visual treatment, media, and template. It must also support the reverse lookup: given a template, scene, asset, or visual pattern, identify the kinds of narration it can validly serve.

The system is intended to help an agent build documentary videos. It must make precise decisions about what the viewer should see, when it should change, which media are required, whether a template is appropriate, and how the visual events align with the spoken words.

## Current phase and stopping point

Begin with inspection, analysis, and design. Do not implement the production system, modify After Effects projects, render scenes, download Envato templates, or make production edits during this phase.

First:

1. Inspect the existing project materials listed below.
2. Explain the proposed decision method in clear language.
3. Demonstrate it on representative passages from the existing ground-truth cases.
4. Present the design, findings, uncertainties, and proposed evaluation method to the user.
5. Stop and wait for explicit user approval before implementing a prototype.

The user wants to see and approve the method before anything is built.

## Primary source of confirmed requirements

Read this file first and treat it as the source of truth for confirmed decisions:

`/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/narration-visual-annotations/astra-selector-formula-inputs.json`

Do not convert passage-specific corrections into global rules unless the evidence supports the generalization. Clearly separate:

- global selection rules;
- project-level style rules;
- template-family rules;
- individual template limitations;
- passage-specific facts or exceptions.

For every user correction:

- store the correction with the example and decision that caused it;
- classify its scope as passage, asset, scene, template, template family, project, or global;
- never promote one correction directly into a global rule;
- propose a broader rule only when multiple examples support it;
- show which existing ground-truth decisions and recommendations would change before activating the broader rule;
- require user approval for template-family, project-level, and global promotion;
- version every active rule and preserve rollback information.

## Existing ground truth and system materials

Inspect at least the following:

### User annotations and selector results

- `ae-template-automation/narration-visual-annotations/year-seventeen-30-selector-cases.json`
- `ae-template-automation/narration-visual-annotations/year-seventeen-30-selector-results.json`
- `ae-template-automation/narration-visual-annotations/year-seventeen-30-selector-results.md`
- `ae-template-automation/narration-visual-annotations/feedback-calibration.json`
- `ae-template-automation/narration-visual-annotations/approved-template-family-map.json`
- `ae-template-automation/narration-visual-annotations/year-seventeen-asset-requirements.json`
- `ae-template-automation/narration-visual-annotations/year-seventeen-production-plan.json`
- `ae-template-automation/narration-visual-annotations/year-seventeen-narration-timing.json`

### Approved scene catalog and user feedback

- `ae-template-automation/scene-library/approved/catalog.json`
- `ae-template-automation/scene-library/approved/evaluation-feedback.json`
- `ae-template-automation/scene-library/approved/evaluation.json`
- `ae-template-automation/scene-library/approved-catalog-policy.json`
- `ae-template-automation/scene-library/ae-media-compatibility.json`
- `ae-template-automation/scene-library/descriptions.json`
- `ae-template-automation/scene-library/clips/*/Scenes.md`
- `ae-template-automation/profiles/`

### Infographic system

- `infographic-template-system/RENDERING-RULES.md`
- `infographic-template-system/rendering-policy.json`
- `infographic-template-system/profiles/catalog.json`
- `infographic-template-system/profiles/`

### Spatial and cinematic 3D system

- `cinematic-scatter/RENDERING-RULES.md`
- `cinematic-scatter/CAMERA-FLIGHT-LOGIC.md`
- `cinematic-scatter/rendering-policy.json`
- `cinematic-scatter/profiles/catalog.json`
- `cinematic-scatter/profiles/`
- `cinematic-scatter/data/year-seventeen-spatial-data.json`

### Existing Google video-understanding work

- `ae-template-automation/video-understanding-test/`

Reuse the lessons, structured-output approach, usage accounting, and cost reporting from those tests. Earlier generic video descriptions were not useful enough; this task requires narration-to-visual alignment analysis.

## Central design requirement

Do not begin by choosing a template.

For each narration passage, first determine the visual communication job. The method should:

1. Read the target passage together with the immediately preceding passage, immediately following passage, and current section purpose. Full-script inspection is not required for every decision. When available, use actual audio timing.
2. Identify its factual claims, entities, relationships, rhetorical purpose, evidence needs, emotional function, and changes in meaning.
3. Divide it into visual units based on meaning and required visual events. Sentence boundaries are useful evidence but are not mandatory scene boundaries.
4. Allow adjacent claims to share a visual when that remains clear. Split a sentence when its claims require different visual jobs.
5. Create a timed visual contract before searching for media or selecting a template.
6. Decide the best treatment class.
7. Define and retrieve the required media.
8. Only then evaluate templates, direct footage, infographics, spatial scenes, archival/document treatments, carousels, custom scenes, or other presentation methods.

The timed visual contract should specify at least:

- exact narration text and surrounding context;
- audio start, end, and duration when known;
- the single viewer takeaway;
- claims and facts that must be communicated;
- required visible subjects, evidence, documents, comparisons, quantities, relationships, or changes;
- required media roles rather than premature filenames;
- phrase-triggered reveals, removals, highlights, camera moves, and transitions;
- minimum readable hold times;
- acceptable duration range;
- continuity with the preceding and following scenes;
- what must never be implied or shown;
- success and failure conditions.

## Candidate treatment classes

The design must compare templates against direct and custom treatments. It must never force every passage into an After Effects template.

Candidate classes should include, where appropriate:

- direct b-roll or interview footage;
- archival footage;
- evidence, source, screenshot, document, quote, magazine, or article presentation;
- single portrait or cutout treatment;
- multi-image montage, gallery, carousel, or sequence;
- After Effects scene or grouped scene sequence;
- infographic;
- accelerating counter or numeric treatment;
- spatial or cinematic 3D relationship scene;
- custom motion graphic;
- a restrained hold on one strong image when additional motion would weaken the point.

The formula must evaluate the required media separately from the container used to present it. A strong template with the wrong media is not a valid recommendation. Strong media should not be forced into a structurally incompatible template.

When required media are missing, use this sourcing policy:

- check the local Media Library first;
- for factual proof, search original articles, documents, charts, and primary sources;
- for event or artist footage, search the existing footage collection, YouTube, Instagram, and Twitter;
- for portraits, use approved Media Library cutouts;
- present suitable candidates for user review when a decision is needed;
- when nothing suitable is found, flag the exact missing asset instead of substituting something weak or misleading.

Run independent source checks and searches in parallel as much as possible. Merge and deduplicate the results before ranking or presenting them. Keep dependent operations sequential.

## Priority order

Apply this order. A lower priority cannot compensate for failure at a higher priority:

1. Factual accuracy
2. Exact communication of the narration claim
3. Spoken-word and visual-event timing alignment
4. Structural compatibility between the media and presentation/template
5. Style consistency
6. Asset quality
7. Overall visual polish
8. Render speed and cost

Render speed and cost are tie-breakers among otherwise valid choices.

## Rejection and escalation gates

Hard-reject a candidate when:

- it cannot clearly communicate the narration claim;
- it introduces unsupported people, data, relationships, or implications;
- it depends on poor crops, duplicated subjects, unreadable evidence, or weak assets;
- a stronger direct treatment exists and the system is merely forcing the passage into a template;
- its important visual events cannot align with the relevant spoken phrases.

When a template's slots, framing, transitions, or duration do not naturally fit, first test whether it can be adjusted cleanly. Reject it only if the adjustment would sacrifice meaning, style, legibility, motion quality, or asset quality.

A template scene may be accelerated or slowed when that preserves readable motion and lets important events land on the relevant spoken phrases. Timing adjustment is a capability, not permission to rescue a structurally wrong template.

The currently approved template adjustments are:

- speed adjustment;
- text removal;
- text modification;
- color adjustment when the template exposes or safely supports it.

Do not assume that deeper structural or stylistic modifications are available unless they are separately verified and approved.

A conflict with the dark cinematic system is a flag rather than an automatic rejection. Outside the approved archival exception, retain a style-mismatched treatment only as a last resort when no stronger option exists.

## Candidate and confidence behavior

For each passage, return four valid, meaningfully different treatments when four valid treatments exist. Rank them and identify a recommended winner.

Automatically advance the winner only when:

- confidence is high;
- it clears every rejection gate;
- required assets and evidence are available or reliably obtainable;
- timing can be aligned;
- the leading candidate is meaningfully stronger than the alternatives.

Require user review when:

- the top candidates are close;
- confidence is low;
- required assets are missing;
- evidence is insufficient or disputed;
- a style exception is required;
- a template requires material structural modification;
- phrase-level timing remains unresolved.

Do not invent an arbitrary confidence threshold. Propose a calibration method using the user's approved and rejected cases. Expose the reasons for selection, rejection, and escalation in plain language.

After a high-confidence winner is selected, prepare a draft production handoff containing:

- the selected treatment and template or scene identifier;
- exact narration text and timing;
- required assets;
- phrase-aligned visual events;
- approved template adjustments;
- missing-asset, evidence, confidence, and rendering flags.

Preparing the handoff does not authorize rendering. Rendering requires a separate user instruction.

## Bidirectional mapping

Design both directions:

### Narration to visuals

Given a passage and context, return its visual contract, required media roles, valid treatment classes, compatible scenes/templates, ranked candidates, timing plan, confidence, and review flags.

### Visuals to narration

Given a scene, template, asset, or visual pattern, return the narration functions it can serve, required claim structure, supported entity count, required media, duration range, timing behavior, style compatibility, and known failure modes.

The reverse mapping should help an agent search for a useful visual and should also help identify where a newly acquired Envato template expands catalog coverage.

## Deterministic style profile

Propose a machine-readable style profile that turns “dark cinematic” into checkable constraints. Cover:

- palette and contrast;
- typography;
- backgrounds;
- image treatment;
- crop and framing quality;
- spacing and information density;
- motion language;
- transitions;
- camera behavior;
- archival and evidentiary exceptions.

One unified dark cinematic system should govern the documentary. Scene families may vary, but their palette, typography, contrast, motion, framing, and tone must remain compatible.

Archival and evidentiary source material may preserve its native appearance. Its surrounding frame, background, typography, transitions, and presentation must remain compatible with the dark cinematic system.

Work with the real capabilities and adjustable controls of the supplied templates. Do not assume every template can be fully recolored or rebuilt. Distinguish:

- a compatible template as supplied;
- a compatible template after safe adjustments;
- a usable last-resort style exception;
- an incompatible template.

The following are initial style references whose individual scenes still require user approval:

- `/Volumes/onn. Drive/AE Templates/03 Documentary & Archival/history-and-documentary-2024-09-12-11-11-54-utc`
- `/Volumes/onn. Drive/AE Templates/Archive 2/Carousels & Slideshows`

Do not modify these templates during this design phase.

## Winning-example video study

Use the following reference videos to learn structure, composition, pacing, motion, evidence presentation, media sequencing, and narration-to-visual timing. Translate the useful structural lessons into this project's dark cinematic system; do not copy the creators' surface styling or content.

1. Exact subject matter; highest weight for media and treatment decisions:
   `https://www.youtube.com/watch?v=NZ105XlGPus`
2. Adjacent subject matter; high weight for transferable storytelling patterns:
   `https://www.youtube.com/watch?v=SAr_zIz5GSU`
3. Different subject matter; use to isolate cross-topic patterns:
   `https://www.youtube.com/watch?v=tiVSpUvQyHc`
4. Different subject matter; use to isolate cross-topic patterns:
   `https://www.youtube.com/watch?v=Cl_JpCSvTpk`

The Google video-understanding study is complete and approved. Do not rerun it unless the user explicitly requests a new analysis. Use these machine-readable artifacts:

- `ae-template-automation/video-understanding-test/creator-reference-pilot/creator-reference-1-full.json`
- `ae-template-automation/video-understanding-test/creator-reference-pilot/creator-reference-2-full.json`
- `ae-template-automation/video-understanding-test/creator-reference-pilot/creator-reference-3-full.json`
- `ae-template-automation/video-understanding-test/creator-reference-pilot/creator-reference-4-full.json`
- `ae-template-automation/video-understanding-test/creator-reference-pilot/creator-reference-comparison.json`

The readable cross-reference explanation is `ae-template-automation/video-understanding-test/creator-reference-pilot/CREATOR-REFERENCE-COMPARISON.md`. The four analyses contain 625 editorial visual units. They record:

- narration text and timestamps;
- claim or rhetorical function;
- visual communication job;
- shot/scene boundaries;
- media type and source role;
- entity count and relationship;
- layout or template family;
- movement, reveal, transition, and emphasis timing;
- the exact spoken phrase that motivates each important visual event;
- duration, pacing, reuse, and information density;
- why the treatment works;
- what is topic-specific;
- what generalizes to other subjects;
- reverse-mapping tags describing which narration structures could use the pattern.

Use the completed comparison artifact as the empirical starting point for scene-boundary, visual-change-frequency, shot-duration, and pacing guidance. The exact-subject and cross-topic documentary references cluster around 6–15-second editorial units, with medians near 9 seconds. The data-led adjacent reference uses 14.5–28-second progressive scenes, with an 18-second median, because charts and callouts continue changing internally. These are planning priors rather than hard limits. Exact communication, phrase alignment, readability, and the needs of the passage remain controlling.

The central finding is that media selection and template selection are separate decisions. First derive the passage's communication and proof obligations, required entities and relationships, media roles, and phrase-aligned visual events. Only then retrieve and score templates whose slots, framing, duration, and internal events can satisfy those requirements.

A generic video summary, list of shots, or style critique is not acceptable.

The analysis workflow used short overlapping windows, absolute source-video timestamps, boundary validation, and deterministic merging. All prompts, raw responses, usage records, costs, and normalization notes are retained under `ae-template-automation/video-understanding-test/creator-reference-pilot/`. Temporary Google uploads were deleted after processing.

## Catalog coverage and Envato sourcing

Compare the documented reusable visual patterns against the approved catalog and existing direct-media, infographic, counter, spatial, and custom-generation workflows.

Produce a coverage-gap report with:

- patterns already supported;
- patterns supported after safe template adjustment;
- missing template families;
- missing scene-generation workflows;
- functional requirements for each missing family;
- example narration structures each gap would serve;
- recommended Envato search language;
- source-versus-build recommendation;
- priority based on how often and how critically the pattern is needed.

The user currently has Envato access. Reusing an owned template is useful, but do not prefer it when it materially weakens accuracy, phrase alignment, media fit, or visual quality.

When the approved library has no clean fit, do not autonomously decide to source a new template or build a custom scene. Flag the gap for the user and explain:

- why the existing options fail;
- which visual or structural capability is missing;
- why that capability matters for the narration passage;
- what a sourced template or custom scene would need to support.

The user decides whether to source or build.

## Design deliverables before implementation

Present the following for review:

1. **Current-state audit** — what already exists, what is reliable, what is incomplete, and what conflicts.
2. **Plain-language decision method** — the full narration-to-visual sequence without code jargon.
3. **Decision model** — stages, gates, features, priority handling, confidence, and escalation.
4. **Timed visual-contract schema** — field definitions and a filled example.
5. **Template/scene capability schema** — field definitions supporting both mapping directions.
6. **Style-profile schema** — global rules, family rules, adjustable traits, locked traits, and exceptions.
7. **Candidate output schema** — four ranked treatments, winner, reasoning, timing, required assets, confidence, and flags.
8. **Winning-example evidence synthesis** — use the four completed analyses and comparison artifact to show which findings are subject-specific, adjacent-domain, and cross-topic; do not rerun the paid analysis.
9. **Demonstrations** — apply the proposed method manually to several representative ground-truth passages, including at least:
   - a direct evidentiary claim;
   - a passage suited to a carousel or media sequence;
   - a quantitative comparison suited to an infographic;
   - a relational or change-over-time passage that might justify a spatial treatment;
   - a passage where no existing template should be used.
10. **Evaluation plan** — tests using the 30 annotated passages, saved feedback, approved and rejected treatments, and corrected infographic/spatial examples.
11. **Open issues and coverage gaps** — what still requires user judgment, better assets, additional labels, or new template families.
12. **Implementation plan** — what would be built after approval, in small reviewable stages. Do not execute this plan yet.

For each design choice, identify the project evidence that supports it. When evidence is weak or contradictory, say so and present the decision for user review.

## Evaluation standard

The proposed method should be judged by whether it:

- reproduces the user's approved choices for the right reasons;
- avoids previously rejected mismatches;
- aligns important visual events with the exact narration phrases;
- distinguishes media selection from template selection;
- refuses to invent unsupported entities or relationships;
- recognizes when direct footage, evidence, or a simple image is better than a template;
- identifies missing assets and template families instead of hiding the gap;
- remains understandable enough for the user to correct;
- converts corrections into appropriately scoped rules;
- supports new scripts and newly sourced templates without rewriting the entire system.

At this stage, impose no fixed reuse limit on images, footage, scenes, or templates. Choose the treatment that works best and leave room to add repetition controls after real production feedback. Cross-scene visual continuity is useful but is not a hard requirement; a strong transition may validly bridge different visual families.

Finish the design phase by showing the user the proposed method and representative demonstrations. Ask for approval before implementing anything.
