# Local rules

Self-contained. Nothing in this directory is ever written back to `~/Documents/ChatGPT/Polish`, and no rule here is global scope.

| File | What it is |
|---|---|
| `base-rules.snapshot.json` | Read-only copy of the project's 10 derived global rules, with the source path and a sha256 of the file it was taken from. |
| `local-overlay.json` | Locally approved corrections, applied on top of the base at read time. Capped at project scope. |

## How resolution works

`prototype/astra/rules.py` loads the base snapshot, then applies every overlay correction whose `status` is `active`. Each resolved rule reports its version and which trigger matched, so any decision can be traced to either the base rule or a local correction.

## How to revert

Set a correction's `status` to anything other than `active`, or delete `local-overlay.json`. The base snapshot alone restores unmodified behaviour. Verified working: with `COR-0001` reverted, passage 24's cohort attrition layout drops from rank 1 to rank 4 and the rule reports version `1.0.0-project`.

## Active corrections

**`COR-0001-spatial-attrition`** extends `spatial_relationship_first` to cover attrition and survival claims, not just gap, distance, overlap, outlier and falling-rank. Approved by the user on 2026-09-16.

Impact preview before activation: applied to all 30 annotated passages, it changes exactly one, passage 24, and agrees with that passage's recorded desired outcome. No regressions.

A first draft of the trigger matched the bare word "gone", which caught the album title *So Far Gone* in passages 06 and 24. Narrowed to "gone quiet", "went quiet" and explicit attrition language before activation.

## If the base rules change upstream

The snapshot records a sha256 of the source file. When it stops matching, the project's rules have moved and the snapshot should be retaken and the overlay re-checked against it.
