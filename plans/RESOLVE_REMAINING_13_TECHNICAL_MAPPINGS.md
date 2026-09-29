# Resolve the remaining 13 technical mappings

Date: 2026-09-28
Branch: `codex/treatment-requirements-review`
Activation: inspection and review only; no selection or rendering authorization

## Objective

Resolve as many of the 13 remaining clip-level technical mappings as the existing native projects can prove without rendering. Keep genuinely visual ambiguities unresolved until existing evidence is exhausted and a narrow native preview is justified.

## Stage 1: correct and inspect Intro Slideshow

Replace the incorrect `intro-slideshow-full-720p` link to Slideshow HD with a source-bound inspection of the actual Intro Slideshow `Project-1.aep`. Use a disposable copy and preserve the source project unchanged.

Acceptance:

- the original and disposable copy hashes are recorded before inspection;
- the native report identifies the actual 154.48-second main composition used by the saved preview;
- the technical registry receives a distinct Intro Slideshow project ID and source hash;
- the seven reviewed clips receive exact window capacity only if their saved preview timestamps align directly to the measured native composition;
- no render occurs.

## Stage 2: capture keyframe evidence

Extend the existing native inspector to record keyframe times and values for layer opacity and time remapping. Preserve existing report fields and keep expressions explicitly flagged.

Acceptance:

- unkeyframed properties do not produce fabricated keys;
- keyed opacity and time remap properties preserve ordered native time/value pairs;
- inspector unit/static checks cover the new report fields;
- the source project remains unchanged.

## Stage 3: resolve Moving Contact Sheets and Carousel

Reinspect the existing source-bound projects using the enhanced inspector. Use time-remap keys to translate the two Moving Contact Sheets preview windows into child-composition windows. Use master-preview opacity keys to identify the active native Carousel composition at each reviewed excerpt.

Acceptance:

- Moving Contact Sheets mappings include replayable master-to-child time transforms;
- Carousel mappings identify exactly one candidate only when opacity/timeline evidence proves it;
- unresolved status remains if expressions, masks, effects or missing key values prevent a unique answer;
- no visual guess is promoted to exact capacity.

## Stage 4: rebuild and verify

Rebuild the technical index, scene-window capacities, clip-coverage ledger, VisualTask comparison and five-case matching batch. Run focused technical tests and the full repository suite.

Acceptance:

- all derived reports reproduce deterministically;
- the remaining unresolved count is reconciled by evidence group;
- live picks, pairings, media selections and source templates remain unchanged;
- any remaining Gallery Pro Carousel or Carousel Slideshow ambiguity is reported as a narrow visual-review requirement rather than guessed.

## Execution result

Completed without rendering or modifying a source AEP:

- Added a distinct, source-hash-bound `intro-slideshow` technical project and corrected the prior family link that incorrectly pointed at Slideshow HD.
- Resolved all seven Intro Slideshow excerpts as exact native timeline windows in composition `02:34`.
- Added opacity/time-remap key evidence to both technical inspectors and covered the new fields with tests.
- Corrected numbered `Image 01`-style edit compositions as media inputs only under the measured `01. Edit/Image/` hierarchy.
- Resolved both Moving Contact Sheets excerpts as exact local windows after translating their native time-remap keys.
- Reused prior native-render evidence to resolve `carousel--review-001` to `Carousel 01/Carousel 01` and `carousel-slideshow--review-001` to `2.Final/Render 01`.
- Rebuilt the window-capacity registry, clip coverage ledger, VisualTask comparison and five-case matching accuracy batch.

Result: 11 of the 13 formerly unresolved mappings are now verified (nine exact clip windows and two verified parent compositions). Two remain deliberately unresolved because existing evidence does not identify one unique native composition:

- `carousel--review-011`: Carousel 09, 10, 11 or 12. These candidates do not share identical media capacity, so choosing by geometry alone would change the technical answer.
- `archive3-gallery-pro-carousel-2026-09-11-10-23-37-utc--review-001`: Gallery Pro Orbit or Showcase. Both currently measure 20 media inputs, 20 simultaneously enabled inputs, zero text fields and 30 seconds, but exact composition identity still matters for later native filling/rendering.

The next justified step is a narrow native visual comparison of only those candidate compositions. It is not required to trust the 11 completed mappings.
