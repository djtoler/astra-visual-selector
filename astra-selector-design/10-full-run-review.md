# 10. Full run — all thirty passages

Contract, retrieval, per-shot candidate slates, gates and decision, across every annotated passage. Nothing rendered, nothing written to the project.

| | |
|---|---|
| Passages | 30 of 30 |
| Slate coverage | **26 / 30** |
| Desired outcome ranked first | **21 / 30** |
| Phrase-aligned events resolved to measured audio | **91 / 91** |
| Multi-shot passages, each shot selected independently | 6 |

Every trigger phrase in the script resolved to a measured timestamp, at match confidence 0.90 to 1.00. That includes names the transcript mangles: "Absoles" for Ab-Soul, "Lotto" for Latto, "jazzy's" for Jay-Z. It also required normalising spoken numbers, because the narration says "ninety-seven percent" and the transcript says "97 %", and this film is built on figures.

## Decisions

| Outcome | Passages |
|---|---|
| Blocked, missing assets | 23 |
| Blocked, script conflict | 3 |
| Require user review | 3 |
| Auto-advance | 1 |

Twenty-three of thirty block on assets. That is not the selector failing. It is the selector reporting the true state of the Media Library against what the script actually claims, which is the behaviour your `17_asset_sourcing_order` answer asks for: name the missing asset rather than substitute something weak.

Your own recorded fallback is `review` on 20 of 30 cases, so a system that rarely escalates would be the one getting it wrong.

## What the run says about the project, not the method

**Eighteen distinct assets are missing across the script.** Named people with no usable asset: Latto, Jay Rock, Macklemore, Biz Markie, Post Malone, Ty Dolla $ign, XXXTentacion. Named artifacts with nothing at all: the XXL Freshman covers, So Far Gone. Plus four group rosters that have never been defined as a set, and two claims whose proof has no source yet.

**Twenty-two of thirty passages need verified values that are not in the Media Library and never will be.** They come from the dataset, not from assets. Those roles are reported as `data_required` rather than missing, because the distinction matters: one is a sourcing job, the other is a data job.

## The four misses, honestly

**Passage 18** and **passage 25** are near misses. The layout you named is viable and ranks just outside the four-candidate slate: sixth of thirty-two for passage 18, fourteenth to sixteenth of eighty-six for passage 25. Reachable with a scoring adjustment; I did not make one, because tuning until a specific case lands is how a selector gets overfitted.

**Passage 11** is my authoring error. You said the slate should carry Hero with chronological ledger *and* the ones already selected, which reads as two shots: the hero distribution, then the comparison against Future. I wrote it as one shot with two entities, so the hero layout gets measured against a two-entity requirement it cannot hold and ranks last. The fix is decomposition, not scoring.

**Passage 28 is a conflict inside the ground truth.** The case records `allowedKinds: ["infographic"]`. Your feedback on the same passage says you could have used 3D templates and names Radial instrument stage and Two-portrait qualitative comparison, both of which are scatter layouts. The selector honours the recorded constraint and therefore cannot reach the layouts you named. One of the two records needs to change, and that is your call, not mine.

## Ten defects found by extending

Extending from five passages to ten dropped coverage to 6 of 10. Extending to thirty dropped it to 22 of 30. Both times the drop was mine.

Worth naming, because each was invisible at the smaller sample:

| | Defect |
|---|---|
| D1 | Every After Effects scene was hardcoded as carrying no data, so all nine counter scenes failed on a passage whose entire point is a number. Your catalog says plainly that they accept numeric data. |
| D2 | `allowedTemplateIds` was read by the selector but never written into the contract. Your template restriction was never applied; it only looked like it worked because the job filter isolated the same template by coincidence. |
| D3 | The portrait preference keyed on `editorialRole == "identity"`, so passage 7, which carries portraits under a `subject` role, got none of it. |
| D4 | Nine portrait-bearing layouts had unreadable designed capacity and escaped portrait fitting entirely, floating above layouts with a known exact fit. |
| D5 | I authored `readingLoad: high` for a one-line question. That is a beat to think in, not a dense read, and it caused the reading gate to reject every template. |
| D6 | The era gate scraped four-digit numbers out of asset summaries **including image dimensions**, so a 2059-pixel width read as the year 2059 and contradicted a 2015 constraint. All 46 candidates on passage 23 were rejected. |
| D7 | The script-conflict gate fired on any recorded conflict, including ones about factual accuracy rather than entity count. |
| D8 | The `evidence` job routed to one scene function covering 2 of 185 scenes, so an evidence passage restricted to After Effects had nowhere to go. |
| D9 | `approved-template-family-map.json` was never used at all. Nine curated families, including the magazine and document presentation family, were unreachable. |
| D10 | See below. It is the most interesting one. |

## D10: making timing priority 1 had a consequence I did not anticipate

You ruled that among candidates clearing every gate, the better-timed one wins. Timing became priority 1 in a lexicographic order, so any deduction there is decisive.

No approved scene record carries internal event beats. So every After Effects scene reported `unknown` on alignment, scored below every infographic and direct treatment, and became **structurally unable to ever win a slate**. Not unlikely. Impossible.

That is the timing-first ruling meeting a missing capability field, and it would have quietly removed 185 approved scenes from consideration.

The fix is that an `unknown` is no longer scored below a `pass`. The uncertainty is still carried, by the decision, which escalates on unknowns. But it no longer decides the ranking.

This is the strongest argument yet for recording event beats. Until they exist, the top-priority criterion cannot actually be evaluated for the largest part of your catalog, and the system is guessing where it should be measuring.

## Correction: most of D10's fix already existed

After the run I was pointed at the rest of the project and found that `ae-template-automation/profiles/` already carries what I had called missing. Twelve per-template profiles, covering 10 of the 14 approved templates, with measured `usable_reading_time_s` running from 3.0 to 12.0 seconds, a graded eight-role documentary vocabulary, style pace and density, and narration suitability with observed word counts. `magnates-motion-system` carries measured entrance and exit timings per motion preset.

The prototype now reads them. A template's own measured usable reading time governs the legibility gate, which is better than both the raw scene duration and my 1.5-second corpus floor, because scene durations include shared transition handles and the usable core is shorter. Coverage held at 26 of 30 after the change, so nothing broke.

Two things from the original claim survive. `aep.colour_control` is `unknown` on 10 of 12 profiles, so the `.aep` parse here still answers something the profiles do not. And per-event beats *inside* an After Effects scene still do not exist; per-scene pacing is not the same as knowing when a highlight can land.

## Pending your approval

Two corrections are marked `approvedBy: pending` because I decided them myself:

- **`COR-0007`** — when the ground truth restricts a shot to fewer templates than the slate size, distinctness falls back to different scenes inside the allowed template.
- **`COR-0009`** — each planned shot gets its own contract scope, slate and gate evaluation, and a passage-level `presentation` annotation binds the first shot only.
- **`COR-0011`** — the selector reads `ae-template-automation/profiles/`, measured usable reading time governs the legibility gate, and a documentary role marked `not_supported` is a hard exclusion.

Eleven corrections are active in total. Eight carry your approval or are flagged as self-corrections.

## State for the comparison

Nothing has been written to the project. The rule snapshot still matches your `feedback-calibration.json` by hash. I have not read the other prototype's implementation since discovering it, so the two builds remain independently derived.

Reproduce this run with `python3 run_slice.py` from `prototype/`. It writes thirty passage JSON files and `out/SLICE-REPORT.md`.
