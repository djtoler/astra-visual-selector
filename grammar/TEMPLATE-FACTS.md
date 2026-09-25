# What the system believes about templates

Every **factual claim** the system makes about what a template is or can do. Not process
rules — those live in the prompts and in CLAUDE.md. A factual claim can be *false*, and
only the user or an inspection can settle one.

Created 2026-09-21, after two false beliefs were found by accident in one day: that a
template's semantics are only what it does to *data* (so nothing could serve
`assert_without_data`), and that templates are *pre-rendered* (so change over time was
treated as unavailable to 54 data-driven templates).

## Why this file exists

A claim written inline in a prompt has no owner, no date and no way to be challenged.
It reads as established. Five prompts restate overlapping claims in different words and
at least two contradict each other. This register is the single place a claim lives;
prompts should reference it rather than assert.

## Status values

| | |
|---|---|
| `VERIFIED` | the user stated it directly, or an inspection confirmed it. Trustworthy. |
| `ASSERTED` | written into the system by Claude or Codex without confirmation. **Treat as unproven.** |
| `DISPUTED` | two parts of the system disagree, or the user has contradicted it. **Blocks any run that depends on it.** |
| `UNKNOWN` | the question has been asked and not answered. |

## The register

### 1. Media, text and timing
| # | Claim | Status | Source |
|---|---|---|---|
| 1.1 | All media in a template is swappable | `VERIFIED` | user, standing rule |
| 1.2 | Timing is elastic; a clip can be any length | `VERIFIED` | user, standing rule |
| 1.3 | Text fit is handled downstream; text never disqualifies | `VERIFIED` | user, standing rule |
| 1.4 | Nothing is baked | `VERIFIED` | user, standing rule |
| 1.5 | Templates are **pre-rendered** | `FALSE` | **Overridden by the user 2026-09-21: "we have to render after we choose a template."** A template is a STARTING POINT, not a finished thing. Selection picks what to render, not what to play. |
| 1.6 | Native editability is confirmed for every template | `VERIFIED` | **User 2026-09-21: "they'll be edited and rendered to fit the beat."** Editability is not in question and must not be flagged as unclear. |

### 2. Capacity and structure
| # | Claim | Status | Source |
|---|---|---|---|
| 2.1 | Slot counts never disqualify; tolerance is ±33% | `VERIFIED` | user, standing rule |
| 2.7 | **A slot count is not static.** An 8-slot template can be modified to 6 or 10 | `VERIFIED` | user 2026-09-21: "this is what i mean by slots should not be looked at as static". Declared capacity is a hint about scale, never a gate. |
| 2.8 | A beat's `entity_count` does not describe everything the visual must hold. Beat 26 is one entity across six categories | `VERIFIED` | user 2026-09-21: "26 is right, 1 entity, 6 catagories". The beat record has no field for the second dimension. |
| 2.2 | Scenes clipped from one template can combine to reach a count | `VERIFIED` | user; 9 families authorized, grammar/MERGE.md |
| 2.3 | Native capacity can exceed what a clip shows | `VERIFIED` | user, standing rule |
| 2.4 | All **9** spatial (`cinematic_3d`) scenes have unlimited capacity | `VERIFIED` | user, 2026-09-21. Was 5; four more were calibrated in the same day (LOG 0059). Their cards state capacity as prose — "35 entities as shipped, ~12-40 workable" — and the user ruled: **"fix that to unlimited"**. `shape()` already returns `unlimited` for the kind, so behaviour was correct; the prose was not, and it is display-only. |
| 2.9 | **A spatial scene's measured `carries` understates it.** The camera is controllable and the point count is unbounded, so what it can be MADE to show exceeds what one rendered clip happens to show | `VERIFIED` | user 2026-09-21, on `truth-rank-fall`: "whatever the beat calls for that the spatial scene can do. it can be camera controlled and has infinite data points so its very flexible". Consequence: for `kind: cinematic_3d`, a missing term in `carries` is weak evidence of absence — the pass watched one camera path over one dataset. This does NOT license inventing terms; it licenses asking. |
| 2.10 | **The hero billboard holds 3 heroes and 10 entities, with unbounded text in L5.** | `VERIFIED` | user 2026-09-21: "hero can take up to 3 heros and up tp 10 entities or unlimited text in the text/data l5 section". The card declares L4 1-3 and L5 "five-entity CSV row"; the user raises L5 to 10 and declares its text unbounded. Recorded in local-templates.json capacityOverrides because layerContract capacity is prose. |
| 2.5 | A portrait slot does not require a picturable subject | `VERIFIED` | user, standing rule |
| 2.6 | A template can be **re-cut to a different slot count**, not only filled to its declared capacity | `VERIFIED` | user 2026-09-21: "yes absolutely they can be re-cut". Declared capacity is a starting point, not a ceiling. |
| 2.11 | **A card's shipped prose can be factually wrong, and a wrong card is unfixable in the export.** `kendrick-red-stage-clean` asserted in ten fields that no quantity may appear in its frame. It may. | `VERIFIED` | user 2026-09-22: **"remove the kendrick avoid list. its wrong. numbers are ok."** The shipped demo prints no numbers; that is the sample, not the mechanic (3.2, and CLAUDE.md's "judge the mechanic, never the sample"). What survives is narrower and is about the mechanic: left/right position and portrait size are authored constants and do not encode magnitude, so the layout compares two subjects without placing them on a scale. Correction lives in local-templates.json `profileCorrections`; the export is generated and never hand-edited. **Consequence: the same ten-field prohibition may be wrong on other cards. Nothing has audited the rest of the corpus for it.** |

### 3. What a template can be made to do
| # | Claim | Status | Source |
|---|---|---|---|
| 3.1 | **Any infographic or spatial template can be modified to show change over time** | `VERIFIED` | user, 2026-09-21. Not yet in any prompt. Contradicts 1.5. |
| 3.2 | A template's semantics are what it does to its *contents*, not only to *data* | `VERIFIED` | corrected 2026-09-21; a slot can hold sourced footage |
| 3.3 | Staging — build, accumulate, tick — is an editing decision, never a reason to reject | `VERIFIED` | user, standing rule |
| 3.4 | **Every** template can change colours and fonts — at minimum background colour and fonts | `VERIFIED` | user 2026-09-21: "we assume all templates can change colors and fonts". Supersedes the older CLAUDE.md wording implying some cannot. |
| 3.5 | Typography can be changed per beat | `VERIFIED` | user 2026-09-21: "yes it can if we need it to" |
| 3.6 | **Rendering happens AFTER selection.** The question at selection is whether a template can be MADE to communicate the beat, not whether it already does | `VERIFIED` | user 2026-09-21, from the 1.5 override. The single most load-bearing claim in this file. |

### 4. Consequences, after the rulings of 2026-09-21
All five open claims are now settled, and together they change the question selection is
asking. Nothing in the system reflects this yet.

- **3.6 is the big one.** Every prompt and filter judges a template as a finished artefact.
  With rendering after selection, the real question is *can this be MADE to carry the beat*.
  `PROMPT-bind.md` asks the wrong question of all 425 records.
- **2.6 weakens the capacity filter.** If a template can be re-cut to a different slot count,
  declared capacity is a starting point, not a ceiling, and `shape()` dropping a record as
  `outside` is too strong. It should down-rank, or flag, not exclude.
- **3.4 and 3.5 retire a standing rule.** CLAUDE.md's colour tiebreak — "check whether its
  colour can change; if not, prefer a sibling whose colour can" — describes a constraint
  that does not exist. All templates can change colour and type.
- **1.6 retires the `native_editability` flag.** Every capability record carries it; it is
  now answered and should not be collected again.
- **3.1 + 3.6 shrink the sourcing list.** Capabilities I recommended BUYING —
  change over time, aggregate, share of whole, derivation — are largely MODIFICATIONS of
  templates already held. `absence` may be the only genuine build.

## The rule

**A factual claim about templates does not go in a prompt. It goes here, and the prompt
cites it.** When a prompt needs a claim, it states the claim AND its number, so anyone
reading can check the status. A prompt asserting an unregistered fact is a defect.

**No paid run may depend on a `DISPUTED` or `UNKNOWN` claim** without the user ruling on
it first. Two of the three re-binds on 2026-09-21 happened because a claim was wrong and
nobody had written it down to be challenged.
