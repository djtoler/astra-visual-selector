# 3. Decision model

Stages, gates, features, priority handling, confidence and escalation. This is the buildable form of the method in the previous document.

## Stage map

```
  narration passage + neighbours + section purpose + audio timing
        |
  [A] SEGMENT ........... cut into visual units on meaning
        |
  [B] CONTRACT .......... obligations, media roles, phrase-aligned events
        |                  (no media, no templates, no filenames)
        |
  [C] RETRIEVE .......... parallel search, merge, dedupe, rank
        |                  -> bound assets, or named missing assets
        |
  [D] GENERATE .......... candidate treatments, direct and template alike
        |
  [E] GATE .............. hard rejections, evaluated per candidate
        |
  [F] RANK .............. lexicographic priority, ties broken within a level
        |
  [G] DECIDE ............ auto-advance, escalate, or report a capability gap
        |
  [H] HANDOFF ........... draft only; rendering needs a separate instruction
```

Stages A and B are narration-only. Stage C is the first point at which the world outside the script enters. Stages D onward cannot run correctly without C, which is the whole reason for the ordering.

## Features, and which ones are trustworthy

Only four fields in the reference corpus are clean controlled vocabularies. Those are the features the model may key on directly.

**Trustworthy today**

| Feature | Source | Values |
|---|---|---|
| `rhetoricalFunction` | annotated, controlled | 18 |
| `evidenceObligation` | annotated, controlled | 4 |
| `editorialRole` | annotated, controlled | 9 |
| `treatmentClass` | annotated, controlled | 13 |
| duration and event timings | measured | continuous |

**Requires normalization before use**

`claimType` (442 free-text values), `mediaType` (425), `presentationFamily` (198), `entityRelationship` (580), `layout` (580). The schemas replace each with a small enum. Until a normalizer exists and is checked, these must not be scoring inputs.

**Blocked until the crosswalk exists**

The job axis itself. Three vocabularies are in use — `input.job` in your 30 cases, `scene.function` in the approved catalog, and `rhetoricalFunction` in the reference analyses — plus two `intents` vocabularies in the generation systems. Only `quantify` and `compare` mean the same thing in more than one. Matching a passage's job to a container's function is inference today and becomes a lookup once one crosswalk table exists.

**Derived**

`narrationJob` from `rhetoricalFunction`. `mediaFamily` from normalized `mediaType`. `focalEntityBucket` from the entity count. `durationBucket` from the timing.

## The gates

Gates are boolean and they run before ranking. A candidate failing any hard gate cannot win, and normally should not be presented as valid at all.

| Gate | Fails when | Evidence |
|---|---|---|
| `communicates_claim` | The viewer could not extract the takeaway from this picture. | Brief |
| `evidence_specificity_honoured` | A representative or decorative asset is carrying a claim whose obligation is exact. | Dominant corpus failure mode, 19 per 100 conditions |
| `no_unsupported_implication` | The picture asserts a person, number, relationship or causation the narration does not. | Brief |
| `evidence_legible` | Required text or detail is too small, or held below the readable floor. | Second corpus failure mode, 8 per 100 |
| `decisive_events_alignable` | A decisive event cannot reach its trigger phrase within tolerance. | Third corpus failure mode, 6 per 100 |
| `asset_quality_sufficient` | Bad crops, duplicated subjects, heavy upscaling, unusable source. | Brief |
| `not_forcing_a_template` | A direct treatment is clearly stronger and the template exists only because templates were being considered. | Brief |
| `density_acceptable` | Too many simultaneous elements to read in the available time. | Fourth corpus failure mode, 5 per 100 |
| `era_consistent` | Asset era contradicts a recorded era constraint. | Corpus failure mode, low frequency, silent when missed |

`era_consistent` is my addition. It is infrequent in the corpus but cheap to check once an era constraint sits on the media role, and it fails silently, which is the worst property a defect can have.

**Flags, not rejections.** Style conflict with no comparably strong styled option. A needed adjustment inside the four approved categories. A missing asset or template family that would have to be sourced. A change of visual family that a transition can bridge.

## Priority handling

The eight priorities are applied **lexicographically, not as a weighted sum**. **Order updated by user ruling, 2026-09-16:** among candidates that clear every hard gate, the better-timed one wins.

1. Spoken-word and visual-event alignment
2. Exact communication of the claim
3. Factual accuracy
4. Structural compatibility of media and container
5. Style consistency
6. Asset quality
7. Visual polish
8. Render speed and cost

A weighted sum would let a beautiful, cheap, perfectly styled candidate outscore a well-timed one. Lexicographic comparison makes that impossible: candidates are compared on priority 1, and only those that tie move to priority 2. Scores exist to break ties *within* a level. Render cost decides only between candidates that are otherwise equal.

**What moving accuracy to third does not mean.** The hard gates are unchanged. A candidate still cannot introduce an unsupported person, number or relationship, and still cannot present unreadable evidence. Answer 23 preserves both explicitly. What was deprioritised is asset-identity exactness — a simple screenshot that communicates the point is acceptable, and chasing the perfect asset is not this phase's focus.

## Duration is elastic

A related ruling from the same turn: *"we arent trying to cram or stretch to fit a duration budget."* If the evidence needs five more seconds to finish, it takes them, and the narration pauses so source audio can carry the proof.

Three consequences for the model:

- The duration range is a descriptive expectation, never a constraint a candidate must fit inside.
- `evidenceMustComplete` defaults true. Truncating a proof to hit a length is a failure, not a trade.
- The 6.8-second internal change budget becomes a split hint rather than a cap, and does not apply while a unit runs long for evidence or carries continuous testimony.

## The project's ten global rules

These are already derived from your corrections in `feedback-calibration.json` and they govern. Six match what this design proposed independently; four were additions.

| Rule | Where it acts |
|---|---|
| `four_distinct_options` | Slate construction. Four candidates from four different template IDs. |
| `include_infographic` | Slate construction. At least one infographic candidate whenever infographics are allowed. |
| `spatial_relationship_first` | Retrieval order. Gap, distance, overlap, outlier and falling-rank claims retrieve spatial candidates before comparison charts. |
| `video_competes_with_stills` | Candidate generation. Footage showing the named people or event enters the slate rather than stills only. |
| `separate_asset_retrieval` | Scoring. Template quality is scored independently of whether the assets are the right people. |
| `focal_hierarchy` | Contract. The focal subject comes from the main claim, not the first named entity. |
| `multi_asset_evidence` | Contract. A passage naming an artifact, a catalog and projects requests every supporting visual, not one portrait. |
| `shot_decomposition` | Segmentation. Split when data, portrait, documentary evidence or qualitative comparison need different treatments. |
| `readability` | Gate. Rules, lists and evidence text need a calm readable hold. |
| `continuity` | Candidate generation. A setup visual may hold into the following reveal and populate with data rather than cutting. |

`four_distinct_options` is stricter and more checkable than the "meaningfully different visual strategy" wording this design started with, and replaces it. `separate_asset_retrieval` is the same separation the back-test argues for, and your feedback is the better evidence: on case 09.01 you wrote *"good selections for templates. bad artists selections except latto."*

## Building the slate

The back-test result that most shapes this stage: **every ranking model I tested scored below the always-propose-the-four-most-common baseline at four candidates**, even though the same models beat baseline by a wide margin at one candidate. Ranking degrades fast past the top.

So the slate is constructed, not sliced off a list:

1. Take the highest-scoring gate-passing candidate. That is the recommendation.
2. Fill the remaining three under `four_distinct_options`: four different template IDs, maximising strategic difference from what is already in the slate while still passing the gates.
3. Apply `include_infographic`: if infographics are allowed for the shot, one slate position is an infographic.
4. Apply `video_competes_with_stills`: if footage directly shows the named people or event, it takes a position.
5. Where a strong direct treatment exists, it occupies a position. Not using a template is always a candidate, and this is where `not_forcing_a_template` gets somewhere to hand the decision.
6. Where fewer than four valid, distinct treatments exist, return fewer and say why. Padding a slate hides the real choice.

Rejected candidates are kept in the output with the gate that removed them, so the user can see what the system refused and correct it.

## Confidence

No invented threshold. Confidence has two parts and both must be satisfied.

**Absolute confidence** is calibrated against the user's own decisions. Group past recommendations into score bands, measure how often the user accepted each band, and fit the mapping from score to acceptance rate. The threshold for auto-advance is then not a guess but the band where observed acceptance reaches whatever rate the user is comfortable with. Until that sample exists, confidence is reported as `uncalibrated_prior` and auto-advance stays off.

**Margin** is how far the winner sits above the runner-up. A narrow margin forces review regardless of absolute confidence, because it means the system is choosing between genuine alternatives and the user's taste is the tiebreaker. The corpus says this will be common: two passages with identical contracts pick the same treatment only 44.9% of the time, so real ties are the normal case, not an edge case.

Auto-advance requires all of: calibrated high confidence, a clear margin, every gate passing with no `unknown` results, assets bound or reliably obtainable, and timing aligned.

Escalate on any of: close candidates, low confidence, missing assets, insufficient or disputed evidence, a required style exception, a required structural modification, unresolved phrase timing, or no clean catalog fit.

## The success metric

Top-1 agreement with a human choice is the wrong target, and the corpus proves it: the same creator, facing the same contract signature, agrees with themselves only 43% to 69% of the time. Holding a machine to a standard the humans do not meet would push the system toward a false confidence.

The defensible targets are:

- **Slate coverage.** The choice a knowledgeable editor would make appears somewhere in the four.
- **Zero gate violations.** No recommendation ever violates a hard gate.
- **Escalation precision.** When the system asks for review, there was a real decision to make.
- **Phrase alignment.** Decisive events land within tolerance of their trigger phrases.

## Reverse direction

The same capability records read backwards, driven by three indexes: narration job to containers, media family and entity count to containers, and required phrase-event shape to containers with a matching movable internal beat. This answers both "what could serve this passage" and "what does this newly bought template add that we did not already have".
