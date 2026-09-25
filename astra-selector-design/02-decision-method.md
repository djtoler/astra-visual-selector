# 2. The decision method in plain language

No code, no scoring notation. This is the sequence a careful editor would follow, written so it can be argued with before it is built.

## The one rule that shapes everything else

**Do not start by choosing a template.** Start by working out what the viewer has to understand, and what would have to be on screen for them to understand it. Only once that is written down do you go looking for media, and only once you have the media do you ask which container presents it.

The back-test says this is not a stylistic preference. Two passages with identical narration structure land on the same treatment barely more often than two random passages, 44.9% against a 34.2% chance rate. Add knowledge of what media exist and that rises to 67.7%. The narration tells you what you owe the viewer. The media tells you how you can pay.

## Step 1. Read the passage in its neighbourhood

Read the target passage, the one before it, the one after it, and the stated purpose of the section. Not the whole script. When real audio exists, use the measured word timings; when it does not, say so, because phrase-level alignment cannot be trusted on estimated timings and anything downstream that depends on it has to be flagged for review.

## Step 2. Work out what the passage is doing

Answer, in order:

- What is the single thing the viewer must leave with? If there are two, the passage needs splitting.
- What is it doing rhetorically? Proving, comparing, escalating, sequencing, explaining, introducing, asserting, framing, or making the viewer feel something.
- What does it assert as fact, and how strong is the proof obligation for each assertion? Four levels: the exact source is required, the exact event or entity is required, something representative will do, or decoration is acceptable.
- Who and what must be visible, and will the viewer recognise them without a label?
- What must never be shown or implied, because the narration does not support it?

On the proof obligation, the corpus is unambiguous. Evidence passages demand an exact source 60% of the time and never accept decoration. Decoration is only ever the strictest requirement on transitions and section resets. Outside those two, nothing decorative may carry a passage.

## Step 3. Cut it into visual units

Split on meaning, not on sentences. Sentence boundaries are evidence but not instructions. Two adjacent claims can share one visual when that stays clear. One sentence splits when its claims need different visual jobs.

Two checks tell you the cut is wrong:

- **Too long.** A scene earns about six to seven seconds per visual change. If you cannot name a change roughly every seven seconds, split it.
- **Too crowded.** If the unit needs more than one takeaway, split it.

The reference median is nine seconds, with a normal range of six to fourteen. Infographics are the exception at around sixteen seconds in every reference measured.

## Step 4. Write the timed visual contract

Before any media is retrieved. The contract states the narration verbatim, the timing and its source, the takeaway, the claims and their proof obligations, the entities and whether they need labels, the media *roles* required, the visual events tied to the exact phrases that motivate them, the minimum readable holds, the acceptable duration range, the continuity with neighbours, the prohibitions, and the conditions for success and failure.

Media roles, never filenames. "The filing, cropped to the clause naming the damages figure, legible for at least two and a half seconds" is a role. `countersuit_scan_02.jpg` is a binding, and bindings happen later.

On event timing, the corpus has a specific lesson. The first phrase-aligned event lands a median of 2.3 seconds after a scene starts, and never before. Scenes establish, then the event lands on the word. Defaulting every event to the top of the scene would be wrong about two thirds of the time.

## Step 5. Find the media

Run the independent searches in parallel and merge before ranking. Local Media Library first. For factual proof, the original article, document, chart or primary source. For event and artist footage, the existing collection, then YouTube, Instagram and Twitter. For portraits, approved Media Library cutouts.

When a role cannot be filled, name the exact missing asset. Do not substitute something weaker and do not quietly drop the role. Substitution is the single most common failure in the reference corpus, at nearly twice the rate of the next worst.

## Step 6. Decide the treatment class

Only now. And the honest position is that the passage usually admits several.

What the corpus supports strongly: evidence passages want the document. Escalation wants a counter. Contrast, example and causation want archival footage. Those hold across every reference measured.

What the corpus does *not* support, despite looking convincing when the four videos are pooled: setup and claim passages wanting interview footage. That is one creator's habit and it must not become a rule.

Direct treatments compete here as equals. Cutting to archival footage, holding on an uncut interview, resting on one strong image: each is a candidate, not the absence of one. Sometimes the right answer is to stop moving. One reference holds twenty-five seconds of uncut testimony because, in the analyst's words, it conveys the reality better than graphics would, and cutting away early is the failure.

## Step 7. Check the containers

For each plausible container, ask four things:

1. **Capacity.** Can it hold this many focal entities *and* label them? Interview footage carries one entity 77% of the time. Carousels only justify themselves from two upward and dominate at four. Infographics are the only container that goes past four. And a container with no text slot cannot name anyone, which rules out several owned carousel packs for any passage needing a name or a date.
2. **Proof.** Can it carry the obligation? Presenting evidence inside a heavy stylistic frame can break an exact-source requirement. Spatial 3D scenes carry a proof role only 16% of the time in the corpus; they explain relationships rather than prove claims.
3. **Timing.** Does it have an internal beat that can be moved onto each decisive phrase? If a decisive event cannot land on its words, the container is out, however good it looks.
4. **Adjustment.** Can it be made to fit using only the four approved adjustments: speed, text removal, text modification, and colour where the template actually exposes it? On the drive, colour is exposed in only 53% of project files overall and in just two of twelve documentary packs, including neither of the two named style references. Anything deeper than the four is not available without separate approval.

## Step 8. Reject honestly

Throw a candidate out when it cannot communicate the claim, when it implies people, data or relationships the narration does not support, when it depends on bad crops, duplicated subjects, unreadable evidence or weak assets, when a stronger direct treatment exists and the only reason a template is in play is that templates are in play, or when its important events cannot reach their phrases.

When a template nearly fits, test the adjustment first. Reject only if adjusting costs meaning, style, legibility, motion quality or asset quality. Speeding a scene up is allowed when the motion stays readable and the events land better. It is not a way to rescue a container that was structurally wrong.

A clash with the dark cinematic system is a flag, not an automatic rejection. Outside the archival exception, keep a mismatched treatment only when nothing stronger exists.

## Step 9. Present four, recommend one

Four meaningfully different valid treatments where four exist. Different means a different visual strategy, not the same strategy in a different template pack.

An important caution from the back-test: the four should not simply be the top four scores. Every ranking I tested was *worse* than always proposing the four most common treatments once you got past the second candidate. The slate is there to show the user a real choice between real strategies, so it should be built for coverage and contrast under the gates, not by taking the top of a list.

Advance automatically only when confidence is high, every gate passes, the assets are in hand or reliably obtainable, the timing aligns, and the leader is meaningfully clear of the rest. Send it to the user when the top candidates are close, when confidence is low, when assets are missing, when evidence is thin or disputed, when a style exception is needed, when a template would need real structural change, or when phrase timing is unresolved.

There is no invented confidence number. Until enough of the user's own accept and reject decisions exist to calibrate against, confidence stays labelled uncalibrated and automatic advancement stays off.

## Step 10. Hand off, do not render

A high-confidence winner produces a draft handoff: the treatment and scene identifier, the exact narration and timing, the assets, the phrase-aligned events, the approved adjustments, and every flag. Preparing it authorises nothing. Rendering needs a separate instruction.

## The reverse direction

The same record read backwards. Given a scene, template, asset or pattern: which narration jobs can it serve, what claim structure does it need, how many entities can it hold, what media does it require, how long does it run, how does its timing behave, is it style-compatible, and how does it fail. That is what lets an agent search for a useful visual, and what tells you whether a newly bought Envato template actually expands coverage or duplicates it.

## When corrections come back

Every correction is stored with the passage and the decision that caused it, and is scoped as narrowly as the evidence allows. One correction supports a fact about that passage or that asset and nothing wider. A broader rule is proposed only when several examples point the same way, and before it activates the system shows which existing decisions it would change and which previously correct ones it would break. Family, project and global rules need explicit approval. Every active rule is versioned and every change keeps its rollback.
