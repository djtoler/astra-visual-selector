# 9. Open issues

What needs your judgement, ordered by how much it affects the design. Updated after reading the project.

## 1. Priority order versus highest-priority gate

`04_priority_order` ranks factual accuracy first and spoken-word alignment third. `05_rejection_policy` names `highestPriorityGate` as *"Important visual events must align with the relevant spoken phrases."*

I have built the model on the reading that these are compatible: alignment is the gate that is never traded away, and factual accuracy governs ranking among candidates that pass every gate. Under the other reading — alignment outranks accuracy outright — case A in the demonstrations would resolve differently, because a perfectly aligned counter beats an unaligned document.

One sentence settles it.

## 2. Evidence and citation policy — answered locally, still deferred upstream

**Answered 2026-09-16: record the source, do not require it on screen.** Every proof role records its provenance in the contract and carries it into the handoff. Whether a credit appears in frame is an editorial choice per scene, and attribution capability never filters a container.

Held as `COR-0002-citation-policy` in `rules/local-overlay.json`, because `18_evidence_quality_and_citation_policy` is still `confirmed: false` in the project requirements and nothing here writes to the project. If you want it upstream, it needs to go into that file deliberately.

Implementing it caught a real defect. The binder was marking passage 15's refusal proof as "generated, authored from the script" — an external claim about the world being treated as something the documentary could simply assert. Proof roles with an exact-source obligation can now only be authored when the source is the documentary's own stated rule, as in passage 17. Otherwise they report `missing` and `NOT YET SOURCED`.

## 3. Three derived rules — all resolved 2026-09-16

**Anachronism is now a hard gate.** `COR-0003`. An asset whose era contradicts a recorded era constraint is rejected. It reports unknown while the role is unbound, because an era cannot be checked before an asset exists. No decision changed today; only passage 15 records an era constraint and its assets are unbound. The gate goes live as assets bind.

**The 6.8-second change budget is advisory and overridable.** `COR-0004`. It may suggest splitting a unit. It never rejects a candidate and never forces a split. Your wording: "if its necessary, override it. like the interview needs its time to say what it needs to say."

**Continuous media is a standing exception to it.** Also `COR-0004`. Any unit whose media family is talking head or performance is exempt outright, because the absence of change is the treatment. Verified firing on a synthetic case.

I had argued this exception was made redundant by the elastic duration ruling. You kept it, and on reflection that is right: elastic duration says a unit may run long, while this says a long unit with no internal change is not even a warning. Those are different statements.

## 4. Rapid reveals that are counted, not read

Nine covers in eleven seconds is 1.2 seconds each, below the 1.5-second floor, and correct when the takeaway is volume rather than any one title. But order-dependent reveals need each one distinguishable even when none needs reading.

Proposed starting position: a reveal may fall below the floor when the takeaway is aggregate and the assembled set holds above the floor afterwards. I cannot derive the order-dependent minimum from four videos.

This bears directly on passage 13 — *"thirty-five of the ninety-three... eighty-one of the ninety-three"* — where the count is the point and no individual is read.

## 5. Portrait legibility — resolved 2026-09-16

`COR-0005`. A layout designed for many faces renders each one small whatever you put in it, so designed capacity rather than supplied count sets portrait size. The system now prefers the smallest designed capacity that still holds the passage's entities, and penalises a layout that shows no portraits when the contract carries a portrait identity role.

No hand-entered numbers were needed. Designed capacity reads out of each profile's `semantic_counts`, with a pairwise layout resolving to pairs times two plus heroes.

Effect on passage 14: "Six portrait value cards" moved from outside the top eight to rank 1, at an exact fit for six entities. That is the layout you called decent, for the reason you gave.

Implementing it exposed a scoring defect of my own, recorded as `COR-0006`. I was scoring layouts by raw count of matching intents, so a layout carrying three routed intents beat one carrying a single routed intent regardless of fit. That rewarded overlap with my crosswalk wording rather than any property of the layout. Serving a job is now near-binary. The same fix routed the `overview` intent, which my first crosswalk audit had already flagged as unreachable from any job.

## 6. Which reference to weight

The comparison artifact weights reference 1, the Future biography, highest because it shares subject matter. By editorial shape your documentary is closer to reference 2, the data-led one: 13 of 30 passages are comparisons and 17 allow an infographic, against a corpus that is evidence-and-archival dominant.

I have used the structural and timing findings from all four and discounted the treatment-frequency findings from 1, 3 and 4. Worth confirming that is the right call, because it inverts the stated weighting.

## 7. Is the 18-value rhetorical vocabulary useful to you?

It is clean and it came from a model describing four videos, not from your practice. Your own cases use seven job values and your catalog uses eight function values. When the crosswalk is built, the question is which vocabulary is canonical. My recommendation is yours — `input.job`, seven values, because it is the one attached to real decisions — with the others mapping onto it.

## 8. Five things to look at rather than decide

- **`Archive 2 / Documents & Screens`** on the drive, against gap 2. You already said you would add document templates; these may be them.
- **`Comparisons 01.aep`**, for the empty `two_dimensional_plot` family.
- **Stale paths** in `future_review_request`: `01 Slideshows` and `02 Openers & Intros` no longer exist.
- **The missing `30.01` feedback record**, on the passage that best demonstrates refusing to invent entities.
- **The scatter catalog's `layout_id`** field, where the infographic catalog uses `template_id`. Minor, but it will bite a crosswalk.

## 9. No repetition controls, by instruction

`19_reuse_limits` says impose none yet. Nothing here counts asset, scene or template reuse. The contract has a `mustDifferFrom` field ready, unused.

## 10. Two limits of my own analysis

**The media-family stage does not work and may not be fixable by formula.** Predicting which media family a passage needs from narration structure alone scored 22.0% against a 27.5% baseline. Below baseline. The practical consequence is that retrieval quality, not scoring quality, is the lever on output. My media-family mapper is also a coarse regex over 425 free-text values that left 173 units unmapped, so the direction is safe and the exact figure is not.

**The four-candidate slate construction rule is my design choice, not a data finding.** Every ranking I tested was worse than always proposing the four most common treatments once past the second candidate. Slate construction by distinctness under gate constraints is a reasonable response, and it now aligns with your `four_distinct_options` rule, but it deserves a second opinion.
