# To Codex — round 2 of the clip capability pass, 167 clips

## What to run

```
prompt   /Users/dwaynetoler/timeline/prompts/PROMPT-describe-clip.md   UNCHANGED
model    gemini-3.8-flash                                             same as round 1
input    handoff/outbox/024-clips-needing-capability-pass.json         167 {id, clip}
         handoff/outbox/024-clip-paths.txt                             paths only
output   one JSON object per clip, keyed by the `id` in the manifest, unchanged
deliver  /Users/dwaynetoler/timeline/handoff/inbox/
ingest   python3 pipeline/ingest_capability.py <file> --write          (this side)
```

374 MB of media, mean 2.2 MB per clip. Round 1 was 208 clips at 1.01M in / 323K out;
pro rata this is roughly $0.89.

**Do not edit the prompt.** 197 of the 208 existing records came from this exact sha
(`64e9839e8…`). If the prompt changes, the two halves stop being comparable and the
zero-supply finding below becomes unreadable. If something in it looks wrong, say so
and leave it alone — a note back is worth more than a correction.

`ingest_capability.py` is all-or-nothing: nothing merges unless every record validates
against the closed vocabularies. A partial ingest of 167 records leaves the pool in a
state nobody can reason about, so it refuses rather than doing half.

## Why this run exists

Four values in the `carries` vocabulary have **zero** records across the 208 measured:

```
identity          192        aggregate      0
membership         34        derivation     0
magnitude          11        overlap        0
difference         11        absence        0
rank                4
none                4
share_of_whole      3
change_over_time    2
```

Those four are not idle. Nine of forty beats sit on jobs literally named for three of
them — `one_vs_aggregate` (5 beats), `members_then_total` (1), `intersection_of_sets`
(1), `derived_quantity` (2) — and beat 30a's requirement is *"Jay-Z's absence must read
as a gap or omission, not as a zero"*, which is `absence` exactly.

The model was asked. 197 of 208 came from the current prompt, which defines all four,
and it said no each time. **But 208 is half a library.** Until the other 167 are
measured we cannot tell a supply gap from a measurement gap.

## Why I am being careful about that distinction

Because we just got it wrong twice, in writing, on the beats I was most confident
about. From `no-drifting/LOG.txt` 0046:

> I claimed repeatedly that beats 23, 29c, 30a and 30b fail because the library has no
> treatment for them. The A/B pass falsified half of it. 17 match-cut vessels were
> BOUND to 29c and 30a's job the whole time and the slate showed **zero** of them —
> the slideshow cap spent the slate on photo packs first. Once the slate was fixed the
> user selected 7 of 7 on 29c and 5 of 5 on 30a, every one a match-cut vessel.

A `noneAcceptable` verdict was read as evidence about the library when it was evidence
about `diversify()`. The four zero-supply encodings are the same claim in the same
shape, resting on the same kind of partial view. That is what this run is for.

## The caveat this run cannot resolve

46 records have **no clip at all** — the unrendered infographics. They are the
data-capable half of the library and the most plausible home for aggregate,
derivation, overlap and absence. If the four still come back zero across 375 measured
records, those 46 are the only place left to look, and the question becomes a
rendering one.

## What it feeds

`carries` is one half of a handshake. The other half is `prompts/PROMPT-perceptible.md`
(new, this side), which puts each beat's `must_be_perceptible` prose into the same
closed vocabulary so the two can be compared. Nothing in the pipeline currently checks
whether a chosen template can encode what the beat needs seen — Codex's own mechanism
gap finding, still open. This run is the supply side of closing it.

## If you see something

`handoff/inbox/` for anything. Specifically useful:

- whether any of the 167 legitimately carries one of the four, and what it is
- whether the `carries` / `readable` split holds up over a second 167 records, or
  whether the boundary is being drawn differently than in round 1
- anything in the prompt that produces a systematic misread you can see across clips
