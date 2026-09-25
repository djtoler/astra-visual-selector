# Comparison of the two tagging runs

Claude Code review of the 2026-09-17 independent tagging comparison, held separately
from the project. Reviewed:

- `Polish/ae-template-automation/selector-prototype/text-tagging/comparison-2026-09-17/assistant/RESULTS.md`
- `Polish/ae-template-automation/selector-prototype/text-tagging/comparison-2026-09-17/claude/RESULTS.md`

Compared for the purpose of automating media and narration sequence/timing matching,
and tagging to filter media and template candidates.

Read-only against the project. Nothing was written there.

**Provenance, corrected 2026-09-17.** `assistant/analysis.json` was authored by Codex.
`claude/analysis.json` was authored by an independent Claude CLI run. Neither is this
reviewer. Below, the two runs are named by artifact rather than by author, because
"Claude" is ambiguous once a third Claude is doing the comparing.

---

I compared the structured JSON rather than the prose, since that's what a filter would actually consume. **They agree on substance far more than the write-ups suggest, and disagree on the two fields you'd build the automation on.**

**The 47% headline is an artifact.** Raw scope agreement across all 240 answers is 47%. Collapse `whole`/`part` into "present" and it jumps to **86%**. The cause: `assistant/` answered `part` 205 times out of 240 and `whole` only 3 times. `claude/` used `whole` 95 times. That isn't a disagreement about the script, it's two readings of an underspecified field. As written, `scope` is not safe to filter on.

**Where they genuinely differ, it matters.**

| | `assistant/` | `claude/` |
|---|---|---|
| Beats | 54 | 66 |
| "Entities must share the screen" | 4 | 27 |
| Uncertainties logged | 23, on 21 segments | 34, on all 30 |
| Distinct tags used | 52 | 61 |

`claude/` splits finer on 15 segments, coarser on 3. Since a beat is a candidate shot, that's a systematically different cut of the film.

**The simultaneous-display field is the real problem.** They disagree on 15 of 30 segments about whether entities must appear together, and `claude/` calls it "required" nearly seven times as often. That field gates template capacity directly. On passage 12, the five-artist rank-loss passage, `assistant/` says optional and `claude/` says required. Optional lets a sequential layout through. Required forces a container holding five at once. Same script, two incompatible candidate sets.

**On quality of the tagging itself**, `claude/`'s output is more useful for your stated purpose. Its uncertainties are operational rather than decorative. On segment 1 it flags: whether 700-per-second and 59-million-per-day should be one continuous accumulation or two separate figures. That is precisely the question deciding one counter animation versus two, and `assistant/` doesn't raise it.

**What I'd do.** Neither is ground truth, and the 86% substantive agreement means the disagreement is concentrated and fixable. Define `whole` versus `part` with examples, and define what makes simultaneous display *required* rather than nice, then rerun both. Until those two definitions exist, tag-based filtering will behave differently depending on which author produced the tags, and you won't be able to tell why.

One caveat on my own read: both passed the same structural validation, so nothing here says either is editorially correct. I compared them to each other, not to your judgement.
