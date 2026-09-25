# Handoff 033 gap-scope capability report

**Completed:** 112/112 supplied measurable assets returned one receiver-valid record on
their first call: 66 videos and 46 still images. There were no failed calls, retries,
pending IDs, cleanup warnings, or missing provider-file deletion receipts. The complete
JSONL passes `/Users/dwaynetoler/timeline/pipeline/ingest_capability.py` without
`--write`. The receiver capability sidecar was not changed.

The run used `gemini-3.8-flash` and prompt SHA-256
`96326905a89cde447856b174515cd27cded58f146f010cc4b679ca0c2ea24480`.
Every still returned `staging: unknown` and `unclear: still_only`. The four supplied
`cannotRun` IDs remain unmeasured because no rendered source exists:
`catalog-gap-clean`, `hologram-stage`, `kendrick-red-stage-clean`, and
`topographic-cloud`.

## Relationship results

| Vocabulary value | Count | Records / review |
|---|---:|---|
| `aggregate` | 1 | `48_playoff_path_summary`; visual review confirms four round scores equated to a 3.44 average. |
| `derivation` | 2 | `truth-ratio-days`, `48_playoff_path_summary`; both visibly present inputs and a computed output. |
| `overlap` | 0 | `two-floors` was inspected because of its user-intent label, but no model result was rewritten. Convergence across a divider is not automatically a meaningful shared-region intersection. |
| `absence` | 0 | `truth-cohort-attrition` visibly reduces a population to two highlighted survivors and remains a manual coding flag under the repaired definition; the returned record is preserved unchanged. |
| `parity` | 8 | Newly returned across one video and seven stills. |
| `independence` | 3 | Newly returned on three videos. |

The changed prompt therefore found narrow evidence for aggregate and derivation, but
did not produce a validated `overlap` or `absence` record. This does not prove those
capabilities are absent from the library. It means the returned records do not yet
close those two vocabulary gaps. The two manual review flags are not silent edits or
selection approval.

Thirty video IDs overlap the prior 145-record delivery. Seven of those thirty changed
at least one `carries`, `readable`, or `implies` array under the new prompt. None of the
old responses replaced a fresh measurement.

The receiver reports 45 slot-count disagreements, 22 beyond its tolerance. These are
preserved as review flags and were not auto-resolved. Native editability remains
unverified; capability measurements do not establish native fit, six valid choices,
or render authorization.

## Usage

- Videos: estimated `$0.815203`
- Stills: estimated `$0.570854`
- Total: estimated `$1.386057`

These figures use the provider-reported token counts and the established rate formula.
Actual Google billing was not independently verified. The total remained below the
authorized `$1.50` safety ceiling.

## Provenance

- Handoff SHA-256: `3ac548f56d034d04a83960ef15f5bef65d5fdad836e0bd68596066369e2b8821`
- Frozen selection SHA-256: `6ccbbc636310dfa90afec282e0efe8a62ae94613ac2ab7ffc4bb6822b85cf062`
- Result JSONL SHA-256: `8a56ce065cda18785987a89f9522b346230f2060735e286f02b23b513384ee72`

No template, approved catalog, selection, render, or receiver sidecar was changed.
