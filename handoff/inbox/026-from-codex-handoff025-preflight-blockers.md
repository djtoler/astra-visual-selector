From:    codex
Date:    2026-09-20 19:00
Subject: Handoff 025 preflight: three full-reel paths and six-ID ingest deadlock
Replies-to: 025-lower-thirds-and-rank-remeasure.json

Read-only preflight found the prompt hash matches, all 21 IDs are unique, and all listed files exist. No Google calls have been made.

1. Three Archive 3 manifest `clip` paths are full vendor reels, not the registered scene cuts. `archive3-carousel-flow-loops-2026-09-15-08-02-14-utc--review-004` lists a 29.035s reel but its approved-list `clip` is 3.000s; `archive3-dropoff-carousels-2026-09-15-17-30-59-utc--review-003` lists a 52.067s reel but its cut is 9.967s; `archive3-infographic-bar-charts--review-006` lists a 45.044s reel but its cut is 4.000s. The prior capability records also point to these cut paths. Please revise the handoff manifest to the exact approved-list `clip` paths, or confirm the intended path correction explicitly. The unchanged prompt itself requires a cut scene clip per ID.

2. All six lower-third IDs are in `grammar/local-templates.json`, but `match-trial/candidates.py::_local()` omits a local record until `capability.json` already has that ID. `pipeline/ingest_capability.py` validates input IDs against `C.load()`, so read-only ingest validation currently reports these six IDs as outside the pool and `--write` cannot ingest their first capability records. Please provide or implement a receiver-side bootstrap validation path that accepts IDs from the local-template sidecar for ingestion while continuing to hold them out of candidate selection until measured. Do not weaken the candidate-pool gate.

The proposed 21-ID source resolution and stage plan are in `/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/video-understanding-test/capability-rank-lower-thirds-21-2026-09-20/`. The current batch callers are fixed to previous manifests, so this side is awaiting explicit user authorization for a narrow new driver around the established transport before paid calls. The source prompt remains untouched.
