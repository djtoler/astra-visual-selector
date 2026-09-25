# 5. Demonstrations

The method applied to six of your thirty annotated passages, covering the five situations the brief asks for plus one that is too instructive to leave out. Each case runs the same sequence — job and takeaway, claims and obligations, entities, media roles, events — then candidates, gates and the decision.

Every case is checked twice: against the desired outcome recorded in `year-seventeen-30-selector-cases.json`, and against what you actually said in `feedback-calibration.json`.

Case durations are estimates. `year-seventeen-narration-timing.json` holds measured audio and should replace them before any of this is built.

---

## Case A. A direct evidentiary claim

**Passage 15.** *"In 2010, XXL offered him a spot on the Freshman cover. He turned it down."*

**Job** evidence. **Takeaway** He was offered the cover and refused it.

**Decomposition.** Two shots, and the reason is the rule `shot_decomposition`: the artifact and the action claim need different visual treatments. The cover is a document. The refusal is an event that needs separate proof. Your own annotation says two shots.

**Claims.**

| Claim | Class | Obligation |
|---|---|---|
| XXL offered him a 2010 Freshman spot | documented fact | exact source — the actual 2010 cover |
| He turned it down | documented fact | exact source — a screenshot, quote or footage of the refusal |

The second claim is the hard one. An offer is evidenced by the artifact; a refusal is evidenced only by testimony or reporting. Nothing about the cover proves it was declined, so a single-shot treatment showing only the cover would state the first claim and leave the second unsupported.

**Media roles.** Shot 1: one `proof` role, family `document_or_screen`, the 2010 XXL Freshman cover, exact source, text legible. Shot 2: one `proof` role, family `document_or_screen` or `archival_motion`, a screenshot or clip showing the refusal.

**Events.** Shot 1: cover reveals on *"XXL offered him a spot"*. Shot 2: the decisive line becomes legible on *"He turned it down"*. Both decisive.

**Prohibitions.** Do not show the 2009 cover — a different cohort, and passage 2 uses 2009 for a different purpose. Do not let an artist portrait stand in for either claim.

**Candidates.** Shot 1 draws on `magazine_or_document_presentation`, which is an approved family with four candidates. Shot 2 has no clean fit: `screenshot_or_evidence_presentation` inherits its candidates from the portrait and magazine families and adds a legibility requirement, but there is no document-native container.

**Your recorded fallback** is *"artist portrait, flagged for review"* — which is the right call and also an explicit acknowledgement that the second claim would go unproven.

**Check against your feedback.** On 15.01 you wrote *"really good selections."* On 15.02, *"good selections. will also be adding a group of document templates which will be a good choice for this type if its a screenshot."* You identified the same missing capability from the other direction. The `Documents & Screens` group in the drive's Archive 2 — YouTube UI, screen mockup, monitor and scrolling screen packs — is undocumented in the drive README and is a candidate for exactly this.

---

## Case B. A passage suited to a media sequence

**Passage 07.** *"Year seventeen of a rap career is anniversary-tour territory. Deluxe reissues with three unreleased demos on the back. A festival slot at seven-forty, before the headliner."*

**Job** sequence. **Takeaway** Year seventeen normally means a nostalgia career, not a dominant one.

This passage makes no claim about a specific person. It establishes an expectation the documentary will then overturn. Rhetorically it is a setup, and its evidence obligation is the loosest in the whole set — representative media is acceptable, because the claim is about a general pattern rather than a named fact.

**But there is a limit.** Your annotation asks for *"several rappers in year 17 or later, plus performances or projects."* Those rappers become named entities the moment they are recognisable, and each one then carries its own claim: that this artist is in year seventeen or later. So the passage is loose about *which* artists and strict about whether each chosen one actually qualifies. That distinction belongs in the contract as a per-role constraint, not a per-passage one.

**Entities.** Several, `group_collective`. Your annotation says multiple shots.

**Candidates.** Three of the four come from `four_or_five_slot_sequence`, an approved family. The fourth is direct footage, which is not optional here: the rule `video_competes_with_stills` requires it, and the passage names performances and festival slots, which are motion events. A still of a stage is a weaker version of the thing being described.

**Check against your feedback.** On 07.01 you wrote *"This a good choice. Also couldve selected something like Ten portrait-topped magnitude columns, Seven people-and-resources packages, Hero-led seven-entry leaderboard, Candidate scores with visible criteria."* Every one of those is an infographic profile, and three of the four carry portraits. The correction is that the slate was too narrow — it stayed inside the AE sequence families when infographic profiles could serve the same job with labels attached. That is the `include_infographic` rule doing real work.

---

## Case C. A quantitative comparison suited to an infographic

**Passage 14.** *"Take his ten biggest. Then take the single biggest song from each of the next five artists and add those five together. His ten win, twenty-one billion to fifteen."*

**Job** compare. **Takeaway** Ten of his songs outweigh the best song of each of the next five artists combined.

**Claims.** One quantitative comparison, exact source required: 21 billion against 15 billion, with both sides constructed from named, verifiable song lists.

**Entities.** Six — the subject plus five named artists. Relationship `group_comparative`, one against many.

Six entities is the structural crux. From the reference corpus, containers that hold six focal entities at once are essentially carousels and infographics, and only infographics reach past four with labels intact. From your catalog, `01_finals_head_to_head` is explicitly two subjects and `avoid_when` says more than two. So the head-to-head family is out despite the passage sounding like a head-to-head.

**Events.** His ten build on *"Take his ten biggest"*. The five singles assemble on *"the single biggest song from each of the next five"*. The result resolves on *"twenty-one billion to fifteen"*. The third is decisive and must not precede its phrase — the conclusion cannot be visible while the comparison is still being built.

**Check against your feedback.** On 14.01: *"only Six portrait value cards was decent because it has nice size portraits given that were only talking about a handful of artists. Full-body portraits inside magnitude bars & Eight portrait columns with paired counts would be a..."*

The operative reason is portrait size at six entities. You accepted the six-card layout because the portraits stay large enough to identify people, and questioned layouts whose capacity exceeds the entity count. That is a legibility constraint that scales inversely with capacity, and it is not currently recorded anywhere: a profile states how many subjects it *can* hold, not the count at which its portraits stop being identifiable. It is worth adding as a field.

---

## Case D. A relational, change-over-time passage that justifies a spatial treatment

**Passage 12.** *"Ab-Soul falls twenty-eight places. Latto falls thirteen. Jay Rock, twelve. Macklemore keeps seventy-three percent of his streams and drops three spots. Drake loses four point four billion streams, keeps ninety-seven percent of his total, and finishes exactly where he started."*

**Job** rank. **Takeaway** Everyone else falls. He does not move.

This is the case that corrects my own analysis. From the reference corpus I concluded spatial treatment is a weak proof device. Your confirmed rule `spatial_relationship_first` says the opposite for exactly this claim shape — gap, distance, overlap, outlier, falling rank — and this passage is four of those five at once.

The corpus was measuring biographies, which rarely make distance claims. Here the distance *is* the claim. The project rule wins, and the reconciliation document records why.

**Claims.** Five named rank deltas plus two retention percentages, all exact-source. Seven verified numbers in one passage.

**Entities.** Five, `group_comparative` with one distinguished.

**Events.** Each named artist falls on their own name. The subject holds position on *"finishes exactly where he started"*, which is decisive and is the only event that must read as an *absence* of movement. That is unusual and worth stating in the contract: the visual event is that nothing happens, and it only reads if the others are visibly falling at the same time.

**The container.** `Before-and-after rank-loss field` in the scatter catalog: 3 to 12 entities, one rank delta each from a shared zero start, intents `rank`, `change`, `resilience`. It matches the claim structure exactly.

**Check against your feedback.** On 12.01: *"3D scatter plot would be good to show Drake high at the top and barely moving and the other artists falling dramatically. Selections are decent but not perfect."* The desired outcome in the cases file says the same. The method reaches it through the project rule, not through the corpus prior, which would have ranked it third.

---

## Case E. A passage where no existing template should be used

**Passage 17.** *"One rule, applied to everybody. A record you lead, or share the lead on equally, counts in full. A feature or a remix verse counts at half."*

**Job** evidence, presentation text. **Takeaway** One counting rule, stated plainly, applied to everyone.

**Why the catalog fails.** This passage has no entity, no quantity to compare and no artifact. It has three clauses the viewer must *read* and remember, because the rest of the documentary depends on them. The requirement is a calm, readable hold.

Every approved AE scene in the relevant families is built to present media with motion. There is no media. Your global rule `readability` states it: *"Rules, lists, and evidence text require a calm readable hold; reject scenes whose motion or layout prevents reading."*

**Check against your feedback.** On 17.01: *"1st 2 are ok, 3rd is a horrible choice because the scene isnt made for reading, more for viewing. 1st to a just ok because the animation on them is a little too active for expecting the viewer to read rules. Will add templates for..."*

Two distinct failures, and the second is the more interesting one. The third candidate was categorically wrong. The first two were the right *kind* of container and still too active. So "readable" is not a binary property of a scene — it is a threshold on motion activity, and the passage sets the threshold. Nothing in the catalog records a motion-activity value, so this rejection cannot currently be computed. It has to be a field.

**Timing.** Three clauses, each needing a genuine read. At a 1.5-second working floor and realistically 2.5 to 3 seconds per clause for text this dense, the shot wants 9 to 12 seconds and the internal change budget is satisfied by the clauses themselves appearing in turn.

**Your recorded fallback** is *"plain text card"*, and the desired outcome is *"Simple readable rules text."* The method agrees, and the useful output is not a template recommendation but a named missing capability: a low-motion text-rule card that belongs in the dark cinematic system. Under `15_existing_source_or_build_priority` that is flagged to you rather than decided.

---

## Case F. The passage that must refuse to answer

**Passage 30.** *"And the rappers this should really be measured against — the ones whose seventeenth year happened before streaming counted anything — can't go on this chart at all. There's no daily meter for Jay-Z's year seventeen."*

Included because it is the clearest test in the set of the gate that matters most.

The narration names exactly one historical artist. Your annotation asks for a five-slot scene using named historical artists, and your recorded fallback is unusually explicit: *"hold for script clarification; the narration names only Jay-Z but the intended visual needs five historical artists."*

A system optimising for a filled slate would pick four plausible peers and produce a beautiful, defensible-looking scene that asserts something the narration never said. That is `no_unsupported_implication`, and it is the failure the whole priority order exists to prevent.

The correct output is not a recommendation. It is a blocked decision naming the exact conflict between the script and the intended visual, handed back for a script decision. You reached that conclusion manually. The method reaches it from the gate.

**One note:** this is the single passage whose feedback record is missing. `feedback-calibration.json` expects 34 entries and holds 33, and `30.01` is the absent one. Given what this case demonstrates, it is worth recovering.

---

## What the six show together

The deciding factor was different every time: the evidence obligation on the second claim in A, the breadth of the slate in B, portrait legibility at six entities in C, a project rule that overrides a corpus prior in D, a motion threshold that nothing currently records in E, and a refusal in F.

No single feature decided more than one case. That is consistent with the back-test — no narration feature dominates — and it is the practical argument for gates plus lexicographic priority rather than a scoring formula. Different passages are decided at different gates.

Three of the six also surfaced a field the catalog does not yet carry: motion activity, portrait legibility at capacity, and the evidence obligation a container can honour. That is the more useful output of this exercise than the treatment picks, which mostly agreed with yours already.
