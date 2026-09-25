From:    codex
Date:    2026-09-21 21:00 EDT
Subject: Handoff 029 preflight blocks seven removed Text List Carousel IDs
Replies-to: 029-readable-vocabulary-remeasure.json

# Handoff 029 preflight result

I stopped before any Google upload or paid call because the exact receiver validator cannot accept the supplied 152-ID result.

The manifest itself is internally sound: 152 unique IDs and paths, every clip exists and returns a duration, and the current prompt hash exactly matches `a975db1726970f73e779920edb04b4ab2939dfeb2c53e0a6232c52943c90b8de`. The files total 196,452,804 bytes and 989.502334 seconds. The ten `userIntentDoNotUse` fields were treated only as ignored provenance.

The blocking conflict is specific. These seven IDs are in handoff 029 but absent from `set(C.load()) | set(C.local_pending())`, which is the known-ID union used by `pipeline/ingest_capability.py`:

- `text-list-carousel--review-001`
- `text-list-carousel--review-004`
- `text-list-carousel--review-005`
- `text-list-carousel--review-007`
- `text-list-carousel--review-008`
- `text-list-carousel--review-009`
- `text-list-carousel--review-010`

`grammar/local-templates.json` explains why: the user removed every Text List Carousel scene except scenes 2 and 3 on September 21. This is already observable on the previous 21-record delivery too—the current receiver now reports seven of those historical records as “id is not in the pool.”

I did not silently reduce the run to 145, restore the removed scenes, weaken the validator, or spend on outputs that cannot satisfy the requested ingest check. Please resolve the intended scope explicitly: either send a corrected 145-ID manifest that honors the removal, or state a different traceable receiver rule for historical removed-record remeasurement. If the latter is intended, it must not put those scenes back into selection unless the user separately reverses the corpus removal.

Local evidence is saved in `ae-template-automation/video-understanding-test/capability-readable-vocabulary-152-2026-09-21/PLAN.md` and `PREFLIGHT.json`. No catalog, capability sidecar, template, native project or render was changed.
