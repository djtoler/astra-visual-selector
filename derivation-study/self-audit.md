# Self-audit: does my own build have the defects I found in Codex's?

Ran the same critique from handoff 017/019 against `astra-selector-design/prototype`.
Answer: yes, all of them, plus one more.

| defect found in facts-v2 | present in my build? | where |
|---|---|---|
| contract hand-authored per segment | **yes** | `seeds/slice.json`, 30 entries keyed by passage number |
| ranking by an authored priority table | **yes** | `PRESENTATION_FIT` in `select.py`, scalar weights 0.1–1.0 |
| acknowledged uncertainty penalized | **yes, three times** | `comm` unknown 0.5, `fact` unknown 0.6, `capacity` unknown 0.4 |
| scalar overlap scoring | **yes** | `overlap = len(want & have)`, then `intent_fit` steps 0.40 / 0.92 / 1.0 |
| sparse metadata rewarded | **yes** | no tags scores 0.55; recorded-and-mismatched scores 0.40 |

Notes on each.

**Authored contracts.** `seeds/slice.json` supplies `takeaway`, `entityRelationship`,
`focalEntityCount`, claims, entities and prohibitions for each of 30 passages. A 31st
passage has no entry. This is the same shape as `facts-v2/contracts.py` SPECS, authored
wider. The file's own `_note` says the judgement inputs are written rather than derived, so
it was labelled honestly, but the generalization critique applies unchanged.

Worth noting `takeaway` is exactly the viewer-objective field I proposed to Codex as the
one thing missing from v2. I had identified it and then hand-authored it thirty times
instead of deriving it.

**Uncertainty.** `score()` carries a comment stating that an unknown must not be scored
worse than a pass, because every After Effects scene reports unknown on event alignment and
would otherwise be structurally unable to win. That guarantee is implemented for `align`
only. The next three lines score unknown at 0.5, 0.6 and 0.4 against a pass at 1.0. The
comment states a principle the code then breaks.

**Sparse metadata.** A candidate with no recorded intents scores 0.55. One whose intents
were recorded and do not match scores 0.40. So failing to describe a template ranks it
above describing it accurately and finding it unsuitable.

## What is genuinely different

Ordering is lexicographic across named priorities rather than a single weighted sum, so a
lower priority cannot buy back a higher one. And `align` really does treat unknown as pass.
Those two hold up.

## Implication

Neither build currently satisfies the method Codex and I agreed in handoff 018–020. Any
comparison of the two should say so rather than score one against the other on criteria
both fail.
