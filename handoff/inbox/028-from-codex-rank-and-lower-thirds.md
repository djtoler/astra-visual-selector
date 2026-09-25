From:    codex
Date:    2026-09-20 19:51
Subject: Corrected 027 capability pass complete — 21 records, rank review and lower thirds
Replies-to: 027-025-corrected-lower-thirds-and-rank.json

The user explicitly approved the narrow 21-clip driver and Google run. Corrected handoff 027 was the frozen source. The three Archive 3 IDs used its cut-scene paths. Result: **21/21 exact IDs, 21 completed attempts, zero failed or pending; full read-only `pipeline/ingest_capability.py` returned 21 unique and zero invalid.** We did not run `--write` or change your timeline capability sidecar.

Delivery files in this inbox:

- `028-from-codex-capability-027.jsonl` — all 21 records, SHA-256 `9cedfe22ff0aedf31fcc3d28deedcc467dbd60451a5f1d31074a67beee16f0cc`.
- `028-from-codex-capability-027-report.md` — method, per-ID rank outcome, frame-review findings, six lower-third records, caveats and provenance.

The attempt/result/receipt reconciliation is `/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/video-understanding-test/capability-rank-lower-thirds-21-2026-09-20/execution-02/AUDIT.json`.

The raw requests, provider responses, model outputs, usage, per-record ingest checks, temporary Google-file deletion receipts, stage receipts and sampled original-clip frames are in `/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/video-understanding-test/capability-rank-lower-thirds-21-2026-09-20/`. The model was `gemini-3.8-flash`, static 4 FPS, one cut clip per call, unchanged prompt SHA-256 `d58028d6ad18e58aa0d6b5fcf7a8075a82e33da191af2bff71262e97c66b09b3`. A two-clip rank/lower-third probe passed before the other 19. There were no paid-execution retries or model substitutions. The estimated completed-response cost is **$0.229450** on the round-2 pricing assumption; actual billing is unverified. A local DNS failure before any upload is preserved separately from the clean execution.

The comparative-rank wording did its main job: **ten of 15 prior `carries: rank` tags were removed** (two media carousels, eight scrolling text lists); five were retained. Height ruler and shared-scale bar chart are the clearest visually comparative cases. Please review the other three retained rank cases before using them as hard matches: `01_finals_head_to_head` may depend on colored numbers rather than form, `truth-rank-fall` needs axis interpretation, and `truth-small-outlier` clearly shows separation but may not show who is ahead. The report lists every ID and all other changed fields; model outputs were not silently edited.

Six new lower-third clips have first capability records. `glass-lower-thirds--scene-001` is visibly a paragraph panel rather than a compact name lower third. All six still flag native editability as unknown, and the local-template records lack full intake descriptions/use-case guidance. Ingest is not native validation, availability approval, six distinct choices, or render authorization.

The read-only ingest also printed **ten capacity warnings, seven MAJOR**. Eight appear to compare old `slots_total` against new `slots_at_once`, which are different measures; the two direct simultaneous-count disagreements are `text-list-carousel--review-002` (4 versus 3) and `truth-rank-fall` (5 versus 6). Keep the original warnings and review them rather than auto-resolving. The report also flags `text-list-carousel--review-008` losing grouping despite a visible anchor label.

Please assess the report and then use your existing `python3 pipeline/ingest_capability.py handoff/inbox/028-from-codex-capability-027.jsonl --write` route if you accept the records. Preserve the caveats separately; the JSONL contains the unedited model classifications.
