# The system, step by step

Confirmed 2026-09-22 by reading each script's own path constants, not from memory.
Every path is relative to `~/timeline` unless marked `[codex]` (read-only, Codex's tree).

`SYSTEM.md` says what each stage *believes*. This says what each stage *does*.

**Paid steps are marked 💲 — four of them. Everything else is arithmetic.**

> **Discrepancy worth ruling on.** `CLAUDE.md` says *"a model is warranted at exactly
> two points"* — beat extraction, and template-to-job judgment. There are now **four**.
> Steps 3 and 4 were added later: they measure the two sides of the encoding handshake,
> which neither of the original two points covers. Either the principle should say four,
> or steps 3 and 4 need justifying against it. Not decided.

---

## 1 · Extract beats 💲

- **In** — narration, 30 passages `[codex] .../narration-visual-annotations/year-seventeen-30-passages.md`; `prompts/PROMPT-beats.md`
- **Does** — splits narration into beats; classifies each into one of 20 jobs; records `quote`, `entity_count`, `must_be_true`, `must_be_perceptible`, `would_be_a_lie`
- **Out** → `pipeline/beats-all.json`
- **Runs** — `pipeline/extract.py <first> <last>` → `pipeline/run.py` (claude-sonnet-5)

## 2 · Load the template pool

- **In** — `astra-selector-design/approved_media/approved-list.json` (generated export, never hand-edited); sidecars `grammar/local-templates.json`, `grammar/eligibility-overrides.json`, `grammar/capability.json`
- **Does** — builds every selectable record; applies scope, removals, supersedes, clip/capacity/capability/profile overrides. **Never rejects on missing data.**
- **Out** → in-memory list (445 records at `content_class="*"`, 436 bare)
- **Runs** — `match-trial/candidates.py` `load()` — imported, not executed

## 3 · Measure what a clip encodes 💲 *(Codex runs this — no Gemini key on this machine)*

- **In** — `prompts/PROMPT-describe-clip.md`; the manifest below
- **Does** — watches each clip and records `carries` / `readable` / `implies` / `structure` / `staging` / slot counts
- **Out** → `handoff/outbox/NNN-*.json` → Codex → `handoff/inbox/NNN-*.jsonl`
- **Runs** — `pipeline/build_capability_manifest.py` builds it; Codex executes; `pipeline/ingest_capability.py --write` merges

### 3b · Ingest the measurements

- **In** — the returned `.jsonl`
- **Does** — validates every record against the closed vocabulary; **all-or-nothing**, nothing writes unless all pass; reports capacity disagreements, never auto-resolves
- **Out** → `grammar/capability.json` (434 of 445 measured)
- **Runs** — `pipeline/ingest_capability.py`

## 4 · Classify what each beat must make visible 💲

- **In** — `pipeline/beats-all.json`; `prompts/PROMPT-perceptible.md`
- **Does** — turns each `must_be_perceptible` sentence into the same closed vocabulary as step 3, with cited evidence. This is the **beat side of the handshake**
- **Out** → `grammar/perceptible.json` (cache `grammar/.perceptible-cache.json`, written only on a partial run)
- **Runs** — `pipeline/classify_perceptible.py --write`

## 5 · Preflight the pool

- **In** — the loaded pool; `pipeline/rules.json`
- **Does** — field coverage, thin descriptions, missing enrichment. **Blocks step 6 if it fails**
- **Out** → stdout only
- **Runs** — `pipeline/preflight.py` (auto-called by `pipeline/bind.py`)

## 6 · Bind templates to jobs 💲

- **In** — the pool; `prompts/PROMPT-bind.md`
- **Does** — for each record, asks which of the 20 jobs it can communicate, with `verdict` / `mechanism` / `evidence`. Batched 20, 6 workers. `--only <ids.json>` re-judges a named set and keeps the rest
- **Out** → `grammar/bindings.json` (624 rows / 20 jobs) · raw at `pipeline/bind-raw.json` · per-batch `pipeline/bind-parts/`
- **Runs** — `pipeline/bind.py [--only f.json]`

### 6b · Validate provenance

- **In** — `grammar/bindings.json`
- **Does** — refuses any binding lacking `promptSha`, `model`, `runId`, `verdict`, `mechanism`, `evidence`. Exception: `source: "user"`
- **Out** → exit code + stdout (currently 624 bindings, 0 invalid)
- **Runs** — `pipeline/validate_bindings.py`

## 7 · Build the slate

- **In** — `pipeline/beats-all.json`, `grammar/bindings.json`, `grammar/perceptible.json`, `grammar/picks.json`, `grammar/beat-flags.json`, `grammar/primaries.json`, word timings `[codex]`
- **Does**, in this order — admit match-cut vessels → admit scoped → admit user-named → drop prior rejections (keeping user-named) → route spatial (**ranks, never excludes**) → capacity rank → encoding rank (the handshake) → diversify to `FAM_MAX=1` per family, `SLATE_LIMIT=10`
- **Out** → `pipeline/shotlist.capacity.json` (with `--capacity`) or `pipeline/shotlist.json` (without — **nothing downstream reads this one**)
- **Runs** — `pipeline/shotlist.py --capacity`

## 8 · Build the review UI

- **In** — a shotlist; clips from `grammar/local-clips` and `[codex]` preview dirs
- **Does** — transcodes each clip to 8s/640px, extracts a real poster frame, inlines posters as base64
- **Out** → `pipeline/ui2/{data.json,media/}` — published as an Artifact
- **Runs** — `pipeline/build_review.py [--out=DIR] [--slate=F]`
  *Variant:* `pipeline/build_pass3.py` → `pipeline/ui4-unseen/`, only cards never shown

## 9 · Human review

- **In** — the published Artifact
- **Does** — the user selects, rejects by omission, writes per-beat notes
- **Out** → artifact database, one doc per beat
- **Runs** — the user. **This is the only judgment that outranks the pipeline.**

## 10 · Ingest the picks

- **In** — pick docs; the UI's **own** `data.json` as the slate of record (never the live shotlist — it drifts)
- **Does** — records selections; derives rejections from what was shown; merges across all passes (selections and rejections accumulate, flags never expire, beats outside the pass are untouched)
  - `--new-pass` record a new sitting · `--subset` the pass showed part of each slate · `--passed-is-judged` the user confirmed a pass-over is a rejection
- **Out** → `grammar/picks.json` (current state) + `grammar/passes/pass-<date>.json` (**immutable**)
- **Runs** — `pipeline/ingest_picks.py <pick-dir> --write`

### 10b · Apply a later ruling

- **In** — `grammar/pass-rulings.json`, the immutable pass files
- **Does** — applies what the user said a past pass *meant*, with their words. Never rejects something they selected
- **Out** → `grammar/picks.json`
- **Runs** — `pipeline/apply_pass_rulings.py --write`

## 11 · Register a template the user cut

- **In** — vendor reels in `templates/`; the user's chosen spans
- **Does** — `pipeline/segment_reel.py` finds every point a design holds still and cuts candidates; `pipeline/cut_scenes.py` cuts the chosen spans as named library scenes
- **Out** → `pipeline/lt-pick/` (candidates) · `grammar/local-clips/` + `grammar/local-templates.json` (registered)
- **Runs** — `pipeline/segment_reel.py`, then `pipeline/cut_scenes.py --write`

---

---

# The media track — steps M1 to M6

Added 2026-09-26. Steps 1–11 above are the TEMPLATE half: which treatment serves a
beat. This half is the other one: which ASSET goes in it. The two ran as separate
tracks for days and nothing joined them until M6, which is why 19 fully-decided
beats had nowhere to go.

**The library is read-only from this side.** sqlite opens `mode=ro`, no file is
moved or copied, and every judgment lives in a sidecar under `grammar/`.

## M1 · Snapshot the library

- **In** — `~/Media Library/METADATA/media-library.sqlite3` + `assets.jsonl` + the Production Ready manifest
- **Does** — exports exactly the five queries the selector reads, plus captions, the delivery, the ingestion project names and the derived-source tag suppressions
- **Out** → `grammar/library-snapshot.json` — roughly an eighth the size of the
  binary sqlite it replaces, and diffable. Both grow as the library does, so the
  ratio is the durable figure, not either number
- **Runs** — `python3 pipeline/export_library.py --write`
- **Why** — the media is 11 GB and the metadata is 25 MB. A session with no library mounted reads the snapshot and resolves identical candidates (LOG 0105)

## M2 · Load the selectable pool

- **In** — the snapshot or the live catalog; `grammar/approved-overrides.json`, `media-corrections.json`, `media-tags.json`
- **Does** — admits exactly the Production Ready delivery plus assets the user waved past the gate. Applies user tags, user tag removals, W corrections. Derives kind, framing, group, display path
- **Out** → in memory. 565 selectable as of 2026-09-26; re-measure rather than
  quote it — the pool moves every time an asset clears the gate
- **Runs** — `media_candidates.load()`
- **Not** — the raw catalog. Most of what is in it is not selectable, and the boundary is the user's lifecycle gate, not this code

## M3 · Resolve candidates for a beat

- **In** — the beat's entities, its chosen templates' framing and kind wants, its quote
- **Does** — entity match both directions (tokens, roster-unique only), ranks on kind fit, framing fit, aboutness against the beat's own words, then evidence strength. **Ranks, never excludes**
- **Out** → a group tier and an individual tier per entity, plus `gaps`
- **Runs** — `media_candidates.resolve(...)`

## M4 · Build the media review

- **In** — `grammar/media-briefs.json`, `beat-flags.json`, `beat-entities.json`
- **Does** — one slate per beat per entity, spread across media type and framing, prior picks pinned; recovers template posters from the source when the cache misses
- **Out** → `pipeline/ui5-media/{data.json,media/,template-media/}` — published as an Artifact
- **Runs** — `python3 pipeline/build_media_review.py`

## M5 · Ingest the media picks

- **In** — the artifact database (`media_picks`, `media_notes`, `media_corrections`)
- **Does** — merges; derives rejections from what was shown on a beat the user judged; records `noneAcceptable`; **refuses to write if the result holds fewer briefs or selections than disk**; stops on an orphan tier whose picks are recorded nowhere else
- **Out** → `grammar/media-picks.json` + `grammar/media-corrections.json`
- **Runs** — `python3 pipeline/ingest_media_review.py <harvest.json> --write`

## M6 · Pair media to template — **the join**

- **In** — `grammar/picks.json` (templates) + `grammar/media-picks.json` (assets) + the capability record
- **Does** — proposes one asset per slot, one slot per ENTITY in the beat's order, honouring framing and kind. Surplus slots report `recutTo`, never a shortfall
- **Out** → `grammar/pairings.json`; `user` outranks `proposed`
- **Runs** — `python3 pipeline/pair.py --write`, reviewed in `pipeline/ui10-pair`
- **Open** — the user's pairings are the evidence for rules that do not exist yet. The proposal is arithmetic; the taste is theirs

---

## 12 · Modify and render — **DOES NOT EXIST**

- **Would take** — a chosen template + the beat's data and media
- **Would do** — re-cut slots, recolour, retype, bind data, drop footage into media wells, render
- **Out** → nothing. **No script in `pipeline/` fills a slot or renders anything** (confirmed by inspection 2026-09-22)
- **Runs** — nothing. All 107 selections are templates with empty slots.

## 13 · Source the footage — **out of scope, by ruling**

- User, 2026-09-21: *"dont worry about finding it, worry about correctly flagging that a beat should use it."*
- Detection is built (`rawBroll`, `needsTextTemplate` in `grammar/beat-flags.json`); retrieval is somebody else's.
- 3 beats currently carry the flag and no template: `23-23`, `29-29c`, `30-30b`.

## 14 · Edit and assemble — outside this tree

---

## Checks, not steps

| | |
|---|---|
| `tests/test_pipeline.py` | 255 tests over the deterministic layer. Run before any publish. |
| `no-drifting/check.py <name>` | every prior defect touching a file or idea. Run **before editing anything**. |
| `pipeline/metrics.py` | coverage across bindings, capability, picks |
| `pipeline/second_opinion.py` | send a decision to Codex via `handoff/` |

## State, 2026-09-22 — every figure below re-measured, not recalled

- 40 beats · **37 served** · 3 unserved, all raw b-roll
- 107 selections, all reachable · 520 rejections · 3 review passes
- pool 445 · 434 measured · 624 bindings, 0 without provenance
- **The blocker is step 12.**
