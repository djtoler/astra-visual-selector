# Handoff 031 capability remeasurement — completed

The corrected 145-ID video batch is complete. The earlier 105 valid responses were retained because handoff 031 exactly matches their IDs, clip paths, prompt hash and model. Forty gaps received one new provider call each; all 40 returned receiver-valid results. No previously valid clip was repurchased.

## Reconciliation

- Handoff records: 145
- Combined records: 145 unique IDs
- Original valid records retained: 105
- Recovery: 40 attempts, 40 valid, zero failures
- Read-only receiver ingest: 145 records, 145 unique IDs, zero invalid
- Google deletion receipts: complete for all 145 successful measurements
- Cleanup warnings: zero
- Estimated completed-response usage: $1.572838; actual billing remains unverified

`capability.json` supplied historical comparison data and helped identify remeasurement need; its prior capability objects were not sent to Gemini. Every saved request used the changed prompt, the exact current clip ID, its current human-facing description and the attached video.

## Changed readable vocabulary

- Prior records present: 139; six records were new/unmeasured.
- Prior records with exact `readable: ["none"]`: 130.
- Readable arrays changed: 135.
- New counts: label 126, statement 61, exact value 18, proportion 6, position in sequence 3, ordering 1, difference 1, none 3.
- All 145 `asserts` lines were scanned for the sample-content trap; none used a subject-specific demo claim.
- Mechanical label/statement cue reconciliation found 0 missing-tag cases.
- All 15 provisional or new records were separately reviewed. The `two-floors` user pack did not produce `carries: overlap`; its model record remains `difference` and is not rewritten to match intent.

## Preserved review flags

- Receiver capacity comparison reports 39 disagreements, 22 beyond tolerance. These are not auto-resolved.
- `04-history-documentary-20-slides--scene-014` reports `existing_description_mismatch`.
- `archive3-gallery-pro-carousel-2026-09-11-10-23-37-utc--review-v2-003b` returned `readable: none` with six text slots. Frame inspection shows tiny header/footer labels, so this is flagged for editorial review rather than silently edited or re-bought.
- Native editability remains unverified on all records, as required.

No capability sidecar, approved catalog, template selection or render was changed. The receiving side decides whether to merge with `--write`.
