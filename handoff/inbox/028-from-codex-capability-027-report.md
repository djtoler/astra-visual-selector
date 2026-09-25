# Handoff 027 capability remeasurement — 21 cut clips

## Outcome

**21/21 exact IDs completed and passed the receiver's read-only ingest validator.** There are no failed or pending IDs in the paid execution. The run produced 15 remeasurements of records previously tagged `carries: rank` and six first capability records for lower-third scene clips. No catalog, timeline sidecar, native project, or render was changed by this run; the receiver decides whether to ingest the JSONL.

The model was `gemini-3.8-flash`, one cut clip per call at static 4 FPS. The corrected handoff 027 and unchanged `PROMPT-describe-clip.md` were used with exact ID and existing-description context. Prompt SHA-256: `d58028d6ad18e58aa0d6b5fcf7a8075a82e33da191af2bff71262e97c66b09b3`. Handoff SHA-256: `fe16316042ea9a1e4759a1798e6140a553123a8e4210f8fd18b62bbe406b718c`. The three Archive 3 IDs used the corrected cut scenes, not full demo reels.

All requests, provider responses, model outputs, usage, per-record validation and Google file deletion receipts are under `execution-02/raw/`. Every deletion receipt says complete; no cleanup warning exists. The first local probe stopped at DNS before an upload and is preserved in the parent directory's attempt ledger. It is not one of the 21 paid-execution attempts. The subsequent two-clip rank/lower-third probe passed before the remaining 19 were sent. There were no paid-execution retries, model substitutions, or normalized empty capability arrays.

Provider usage across 21 completed responses: **105,948 input**, **3,612 output**, **36,385 thought** tokens. At the same estimated rate used for round 2, completed-response cost is **$0.229450**, below the saved $1 stop. Actual account billing is unverified. The delivery JSONL SHA-256 is `9cedfe22ff0aedf31fcc3d28deedcc467dbd60451a5f1d31074a67beee16f0cc`.

## Rank result and visual assessment

The revised prompt defines `rank` as a visible comparative order, rather than the order in which items arrive. All 15 previously tagged records were remeasured with that wording. **Ten lost `rank`; five retained it; none gained it** (all 15 started with the tag). The two carousel cuts and eight scrolling text-list cuts account for all ten removals. Their sampled frames show cards or text rotating through a focus position, without a visual claim that an earlier item is ahead. This supports the intended correction.

| ID | New `carries: rank` | Frame-review finding |
|---|---:|---|
| `01_finals_head_to_head` | Retained | Paired subjects and colored numerical metrics. Comparative advantage may depend on reading the values or color applied to the values; form-only rank remains **uncertain**. New `implies` also dropped `ranking` while keeping `competition`. |
| `05_measured_height_ruler` | Retained | Shared baseline and visibly different heights support comparative order. |
| `archive3-carousel-flow-loops-2026-09-15-08-02-14-utc--review-004` | Removed | Media cards cycle along a depth rail; step markers indicate sequence. |
| `archive3-dropoff-carousels-2026-09-15-17-30-59-utc--review-003` | Removed | Fanned cards peel away to reveal the next card. |
| `archive3-infographic-bar-charts--review-006` | Retained | Bar lengths on a shared scale visibly order quantities. |
| `text-list-carousel--review-001` | Removed | Center emphasis moves from phrase to phrase. |
| `text-list-carousel--review-002` | Removed | Angled text statements advance through the center. |
| `text-list-carousel--review-004` | Removed | Text steps through a center position. |
| `text-list-carousel--review-006` | Removed | Numbered items advance in turn; the new record retains `readable: ordering, position_in_sequence`, not visual comparative rank. |
| `text-list-carousel--review-007` | Removed | Boxed items scroll into view. |
| `text-list-carousel--review-008` | Removed | Text cycles beside a fixed anchor label. The new record also removed `membership` and `readable: grouping`; the visible anchor makes that separate change worth human review. |
| `text-list-carousel--review-009` | Removed | Badges pass through an angled sequence. |
| `text-list-carousel--review-010` | Removed | Boxed text advances along a staggered path. |
| `truth-rank-fall` | Retained | Plotted points have relative vertical positions and move, suggesting comparative order; verify intended axes and whether this is rank rather than magnitude/difference before hard matching. |
| `truth-small-outlier` | Retained | A spatial outlier is separated from a cluster. The frames strongly show difference, but whether one point is **ahead** is unclear; flag `rank` for editorial review. |

These are model records plus frame review, not verified native capacity or final selector decisions. The two clearest form-only comparative controls are the height ruler and bar chart. The other three retained `rank` records need the specific caution above. The raw output has not been edited to impose this judgment.

The remeasurement also changed fields beyond `rank`: all 15 `asserts` lines changed, nine structures changed (primarily `list` to `sequence`), two `slots_at_once`, three `slots_total`, two `growable`, three `readable`, one `implies`, three `text_slots`, and two `media_slots`. Eleven `carries` arrays changed in total. Review these before replacing whole prior records. The new `text-list-carousel--review-008` grouping loss and `01_finals_head_to_head` rank/implies disagreement should stay visible.

The full receiver ingest report flags **ten capacity disagreements, seven labeled MAJOR**. Eight of the ten appear to be a comparison-method issue: the checker uses the larger declared `slots_total` to compare against the model's `slots_at_once`, although those count different things. Six of the seven major flags have an exact match between old and new `slots_at_once`; the same is true for two of the three minor flags. The two direct simultaneous-count disagreements are `text-list-carousel--review-002` (declared 4, model 3; flagged MAJOR) and `truth-rank-fall` (declared 5, model 6; flagged minor). These are review findings, not automatic corrections or a reason to hide the receiver's original warnings.

## Six new lower-third scene records

| ID | Returned mechanic | Frame-review note |
|---|---|---|
| `grunge-lower-thirds--scene-001` | One subject image with two identifying text lines; `carries: identity`. | Matches a name/title introduction. |
| `glass-lower-thirds--scene-001` | Multi-line text block in a frosted panel over full-frame media; `carries: none`. | This is a paragraph panel, not a compact name lower third. Keep its original source label but review its selection guidance. |
| `paper-lower-thirds--scene-001` | Single subject with identifying lower-third text; `carries: identity`. | Name/title on a torn-paper band. |
| `paper-lower-thirds--scene-002` | Single subject with banner and callout; `carries: identity`. | Paper treatment with callout. |
| `paper-lower-thirds--scene-003` | Single subject with animated title; `carries: identity`. | Another paper name treatment. |
| `paper-lower-thirds--scene-004` | Single subject with label; `carries: identity`. | Another paper name treatment. |

All six correctly retain `unclear: native_editability`. The video cannot prove editable text/media fields, timing controls, or compatibility. The four paper scenes are separate cuts but their similar job does not establish four distinct valid choices for a narration scene. The local-template records still have no full scene descriptions or use-case guidance; capability `asserts` is a fallback in the receiver loader. Ingesting them should not by itself mark template intake complete, grant availability, validate six choices, or authorize rendering.

## Validation and files

- `execution-02/capability-027.jsonl`: 21 exact-ID records. The receiver's `pipeline/ingest_capability.py` returned **21 unique, zero invalid**, plus the ten capacity warnings described above, in read-only mode. `--write` was not run here.
- `execution-02/AUDIT.json`: reconciles the 21 attempts/results, ordered stage receipts, request settings, raw files, deletion outcomes, usage and full-file ingest result.
- `execution-02/STATUS.json`: no failed or pending IDs, plus estimate and source hashes.
- `rank-contact-sheet.png`, `rank-controls-timeline.png`, and `lower-third-contact-sheet.png`: sampled **original cut-clip frames** used for the visual assessment. They are not renders or native-template tests.
- `selection-027.json` and `PLAN.md`: frozen source hashes and agreed ordered stages. The source correction and receiver bootstrap fix came from handoff 027.

The required stage order is evidenced in `execution-02/stage-receipts.jsonl`: frozen scope, established transport, two valid probes, remaining 19, this review, then final read-only ingest and atomic handoff. The same capability prompt still references the original 367 AE ID list; corrected handoff 027 supplied the explicit 21-ID scope, including non-AE and local clips, while its mechanic rules and schema were unchanged. No native fit or render decision follows from this capability pass.
