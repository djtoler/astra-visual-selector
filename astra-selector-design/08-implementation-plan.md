# 8. Implementation plan

Not to be executed. Presented for approval, in small reviewable stages. Each stage has a deliverable that can be inspected on its own and a reason it comes where it does.

**Stage 0 is a prerequisite for most of what follows**, because seven of the twelve design deliverables depend on files that were unreadable.

---

### Stage 0. Reconcile — done

Completed during this design phase once Documents access opened. The confirmed requirements, the 30 cases, the feedback calibration, the approved catalog and policy, and both generation systems were read, and this package was revised against them.

*Deliverable:* [`00-reconciliation.md`](00-reconciliation.md). One of my findings was overridden by your `spatial_relationship_first` rule, four of your global rules were added to the model, the capability schema was reframed as an extension of your existing `selectionContract`, and the coverage report was rewritten against the approved catalog rather than raw drive inventory.

### Stage 1. The vocabulary crosswalk

**The highest-value single task in this plan.** One table mapping the 30 cases' `job` values, the approved scenes' `function` values, the reference analyses' `rhetoricalFunction`, and the `intents` vocabularies of the infographic and scatter profiles onto one another. Only `quantify` and `compare` currently mean the same thing in more than one of them.

In the same stage, normalize the five free-text reference fields into the schema enums, and rebuild the pattern layer with unit ids attached so every pattern claim is testable.

*Deliverable:* the crosswalk, plus a mapping report naming everything that could not be mapped.

*Why first:* until a passage's job can be matched to a scene's function by lookup rather than inference, nothing downstream is deterministic. This is what the word "deterministic" in the brief actually costs.

### Stage 2. Fill the capability gaps

Not new records. Four fields added to your existing `selectionContract`, plus the annotation that is already missing.

**Extract automatically** with the `.aep` parser prototyped for this design: text-slot capability, colour-control exposure, media-slot names and counts. The parser already reproduces the manual finding behind your `history-envato` exclusion, so it can pre-screen the whole library.

**Annotate by review:** motion activity (for the `readability` rule), evidence obligation ceiling, portrait legibility at capacity, and `focalEntityCount` on the 171 scenes that lack it.

**Derive from the existing per-scene renders:** internal event beats and their movability. This is the one that unblocks phrase alignment and is the largest piece of work in the stage.

**Write by hand:** four `direct_media_treatment` records — archival cut, interview hold, single image hold, montage — so that not using a template can compete in a slate. An afternoon, and `not_forcing_a_template` has nothing to hand decisions to without them.

*Deliverable:* extended contracts for all 185 approved scenes, marked `auto_extracted_unverified` where extracted.

*Manual tasks inside this stage:* inspect `Archive 2 / Documents & Screens` against gap 2, inspect `Comparisons 01.aep` for the empty `two_dimensional_plot` family, and update the stale collection paths in `future_review_request`.

### Stage 3. Contract builder

Narration in, contract out. No media, no templates. Runs on the 30 annotated passages and the reference corpus. Uses `year-seventeen-narration-timing.json` for measured audio rather than estimated durations.

*Deliverable:* contracts for all 30 passages, reviewable as documents, plus the static purity check that no contract names a file or a template.

*Gate before proceeding:* the user reads a sample of contracts and confirms the obligations are right. If the contracts are wrong, nothing downstream can be right, and this is the cheapest place to find out.

### Stage 4. Gates

Implement the nine hard gates as independent checks with the adversarial fixtures from the evaluation plan. Gates before scoring, deliberately: a system that rejects correctly and ranks crudely is useful, and one that ranks beautifully and rejects nothing is dangerous.

*Deliverable:* gate suite with fixtures, each gate independently testable.

### Stage 5. Retrieval and binding

Parallel search across the Media Library, primary sources, the footage collection and the social sources, merged and deduplicated before ranking. Binds assets to roles, or names the missing asset.

*Deliverable:* binding reports for the 30 passages, including an explicit missing-asset list.

*Why it comes before scoring:* the back-test shows media availability resolves treatment choice more than narration structure does. Scoring without bindings would be measuring the wrong thing.

### Stage 6. Candidate generation and ranking

Generate candidates including direct treatments, apply gates, rank lexicographically, and construct the slate for strategic difference rather than by taking the top four. Run Suites 1 and 2.

*Deliverable:* candidate slates for the 30 passages with the full evaluation report.

### Stage 7. Correction and promotion machinery

Correction capture at the narrowest scope, promotion proposals requiring multiple examples, impact previews before activation, versioning and rollback. Run Suite 4, including the adversarial case that a single passage-specific correction must not become a global rule.

*Deliverable:* a correction log and a working promotion workflow with rollback demonstrated.

### Stage 8. Reverse mapping and coverage

Build the three reverse indexes. Produce a real coverage-gap report against the approved catalog. Add the "what does this new template add" query.

*Deliverable:* reverse lookup plus a coverage report that supersedes the partial one in this package.

### Stage 9. Calibration

Once enough accept and reject decisions exist, fit the calibration curve and propose an auto-advance threshold for approval. **Auto-advance stays off until this stage completes and the user approves the threshold.**

*Deliverable:* a calibration curve, a proposed threshold, and the decision record.

### Stage 10. Production handoff

Emit handoff records. Rendering remains behind a separate explicit instruction.

---

## Ordering rationale

Gates before scoring, because correct rejection is worth more than elegant ranking. Retrieval before scoring, because the evidence says media availability is the resolving input. Contracts reviewed by the user before anything downstream, because a wrong contract cannot produce a right candidate. Calibration last, because it needs decisions that only exist once the rest is running.

## What Stage 0 already changed

The plan is shorter than the pre-access draft in two places and longer in one.

**Shorter:** the style profile no longer needs writing from scratch. `infographic-template-system/RENDERING-RULES.md` and `cinematic-scatter/RENDERING-RULES.md` already contain most of it, including a phrase-alignment rule stated better than mine — *"Focal enlargement begins on the phrase that establishes focus, eases in, and never anticipates the narration."* The work is unifying two documents into one checkable profile, not inventing content. Coverage analysis is also shorter, because the approved catalog turned out to cover more than raw drive inventory suggested.

**Longer:** Stage 1 became a vocabulary crosswalk, which I did not know was needed. It is now the critical path.
