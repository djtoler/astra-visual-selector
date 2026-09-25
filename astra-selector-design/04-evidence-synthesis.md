# 4. Winning-example evidence synthesis

Everything here comes from re-analysing the 628 annotated units in the four completed reference analyses. The paid Google analysis was not rerun. All figures are reproducible from `data/derived-priors.json` and `data/backtest-results.json`.

**Calibration note.** These four references are evidence-and-archival dominant: 129 evidence units against 16 comparison units. This documentary is the reverse — 13 of your 30 passages are comparisons and 17 allow an infographic. The structural and timing findings below transfer. The treatment-*frequency* findings largely do not, and reference 2, the data-led one, is the closer editorial analogue despite being labelled adjacent-subject.

Throughout, findings are tiered by how far they travel:

- **Cross-topic** means the effect holds in every reference where it could be measured.
- **Likely** means it holds in most, with too few cases in the rest to tell.
- **Single-creator** means one creator does it and the others do not. These must never become global rules.

---

## 4.1 The central finding: narration underdetermines treatment

I built a selector from the narration-side features alone, trained it on three references and tested it on the held-out fourth, rotating through all four.

| Predicting | Top-1 | Baseline | Top-4 | Baseline |
|---|---|---|---|---|
| Treatment from narration only | 32.6% | 18.8% | 76.8% | 83.6% |
| Treatment from media family plus contract | 40.6% | 18.8% | 79.1% | 83.6% |

Baseline means always proposing the most common treatments from the training references.

Two things follow, and the second one is uncomfortable.

**Narration features genuinely help at the top pick.** 32.6% against 18.8% is a real signal, and adding the media family lifts it to 40.6%. The features are not noise.

**At four candidates, every learned model scored below the baseline.** Always offering the four most common treatments beat every ranking I could build. This is not a tuning problem. It says a four-candidate slate must not be produced by taking the top four scores, because the tail of the ranking is worse than ignorance. A slate has to be constructed for meaningful difference under gate constraints, which is what the brief already asks for and what the candidate schema enforces.

### Why the ceiling is where it is

I measured how often two units that share an identical feature signature also share a treatment.

| Units share | Treatment agreement |
|---|---|
| Nothing (random pair) | 34.2% |
| The same full narration contract | 44.9% |
| The same media family alone | 56.2% |
| The same media family and contract | 67.7% |

Two passages with an identical narration contract agree on treatment barely more often than two random passages. Knowing only the media family does better than knowing the entire narration contract.

Even the same creator, on the same contract signature, agrees with themselves only 43% to 69% of the time.

This is the empirical case for the architecture the brief specifies. The narration determines the *obligations*: what must be proved, who must be visible, what may never be implied, when each event must land. What resolves the treatment is which media actually exist. A system that tries to go from sentence to template without the media inventory in the loop is guessing, and the numbers say it will guess wrong about two times in three.

It also sets the honest success metric. **Top-1 agreement with a human choice is the wrong target.** The defensible targets are slate coverage and zero gate violations.

### The one stage that does not work yet

Breaking the pipeline into stages and testing each:

| Stage | Top-1 | Baseline |
|---|---|---|
| Narration to required editorial role | 65.1% | 60.8% |
| Narration to required source specificity | 58.3% | 54.8% |
| **Narration to required media family** | **22.0%** | **27.5%** |

The media-family stage performs below baseline. Narration structure does not tell you what kind of media to go and find. Subject knowledge does. This is a genuine limit, not a gap to be closed by better features, and it is why the sourcing policy and the Media Library index matter more to output quality than the scoring formula does.

Caveat: my media-family mapper is a coarse regex over 425 free-text values and left 173 units in `other`. The direction of the finding is safe; the exact number is not.

---

## 4.1b Independently corroborated by a corpus 50 times larger

After this synthesis was written I was pointed at `johnny-harris-analysis`, which this design had never read: **197 videos, 2,707 visual beats**, analysed for pacing, transitions and narration-to-visual relationship.

| Beat duration | This design, 628 units | Johnny Harris, 2,707 beats |
|---|---|---|
| p25 | 6.0s | 5.5s |
| median | 9.0s | 8.0s |
| p75 | 14.0s | 11.0s |

The cadence prior holds against a different creator and a fifty-times-larger sample. The upper tail runs tighter there because that corpus covers intros only, which are faster than body content.

Two further things transfer. Cuts run at a median of 22 per minute, which against 5 to 7 editorial units per minute implies **about three shots inside one editorial unit** — a relationship the four-reference data could not show. And the narration-to-visual relationship splits with **literal illustration at 21.8% and evidence or proof at 21.2%**, together 43% of all beats. Showing the thing and proving the thing are the two dominant modes, which is the same conclusion the four references reached from the failure side.

That corpus has the same free-text drift: `host_to_camera`, `host to camera` and `host_on_camera` are three spellings of one value, and `cut`, `hard cut`, `hard_cut` and `Hard Cut` are four spellings of another. The normalization problem is not specific to the four reference analyses.

Full figures in `data/johnny-harris-corroboration.json`.

## 4.2 Timing: what the references actually do

**Scene length.** Across all 628 units: p25 6.0s, median 9.0s, p75 14.0s, p90 20.0s.

**Minimum readable hold.** Measured from 502 observed gaps between consecutive internal changes.

| Percentile | Gap |
|---|---|
| p5 | 1.1s |
| p10 | 1.5s |
| p25 | 2.0s |
| median | 3.0s |

Only 0.6% of real gaps fall below one second. This gives a defensible floor instead of an invented threshold: **1.0s absolute, 1.5s working, 2.0s comfortable**, and more for dense evidence text.

**Scenes establish before they land their event.** The first phrase-aligned event arrives a median of 2.3 seconds after the unit starts. Only 30% of units fire within one second of the cut, and none fire early. The picture arrives, the viewer orients, then the event lands on the word. A contract that defaults every event to zero offset would be wrong for two thirds of scenes.

**A scene earns roughly 6 to 7 seconds per internal change.** This ratio is flat across every duration bucket up to 30 seconds, which makes it a usable budget rather than a coincidence.

| Duration | Share with an internal change | Median changes |
|---|---|---|
| 0-6s | 51% | 1 |
| 6-10s | 83% | 1 |
| 10-15s | 88% | 2 |
| 15-20s | 90% | 3 |
| 20-30s | 95% | 3 |

The rule that falls out: if a scene cannot supply a visual change roughly every 6.8 seconds, it is too long and should be split. This is the checkable version of "a long scene remains active only when internal visual progression continues."

**Alignment quality.** Of 905 phrase-aligned events, 804 are rated strong, 99 acceptable, 2 weak. The references are genuinely phrase-locked, which is why phrase alignment is a fair standard to hold this system to.

---

## 4.3 Treatment durations, corrected for creator cadence

Raw medians mislead because the four creators cut at different speeds. Dividing each treatment's median by its own reference's baseline isolates the treatment effect.

| Treatment | Ratio to that creator's baseline | Holds across references |
|---|---|---|
| `counter_or_numeric` | 1.50x | Yes |
| `single_image_hold` | 0.81x | Yes |
| `infographic` | 16-17s absolute in all four | Yes, as an absolute |
| Everything else | 0.94x to 1.18x | No consistent effect |

Only three treatments have a duration signature worth encoding. Counters run half again as long as the surrounding cadence, single image holds run shorter, and infographics are a fixed-length scene regardless of who is cutting. The other nine simply take as long as the passage takes.

---

## 4.4 Container capacity by entity count

This is the cleanest structural signal in the corpus, and it drives the reverse mapping directly.

| Treatment | Median entities | p90 | One entity | Three or more |
|---|---|---|---|---|
| `interview_footage` | 1 | 2 | 77% | 2% |
| `single_image_hold` | 1 | 2 | 70% | 6% |
| `evidence_or_document` | 1 | 2 | 64% | 9% |
| `archival_footage` | 1 | 3 | 54% | 13% |
| `spatial_or_cinematic_3d` | 1 | 2 | 52% | 8% |
| `portrait_or_cutout` | 2 | 4 | 36% | 21% |
| `montage_gallery_or_carousel` | 2 | 4 | 20% | 38% |
| `infographic` | 2 | 7 | 29% | 45% |

As the entity count rises the containers hand off in a clear order. Interview footage collapses from 31% of one-entity units to near zero by four. Carousels climb from 5% to 58%. Infographics climb from 2% to 38% and are the only container that reaches past four entities.

Two consequences:

**Spatial and cinematic 3D is not a many-entity container.** Its maximum in the corpus is four and 92% of its uses carry one or two entities. It is a relationship device rather than a crowd device.

> **Corrected after reading the project.** I originally continued this finding to say spatial treatment rarely proves anything, on the grounds that it carries a proof role only 16% of the time against 95% for `evidence_or_document`. **That conclusion does not transfer to this documentary and is overridden by the confirmed rule `spatial_relationship_first`**, which requires retrieving spatial candidates *before* ordinary comparison charts for gap, distance, overlap, outlier and falling-rank claims.
>
> The corpus and the project rule are both right about different films. Three of the four references are biographies, which rarely make distance claims, so spatial treatment there is decorative and the 16% reflects that. This documentary is built on distance, gap and rank-loss claims, where the spatial field *is* the proof. The corpus was measuring the wrong population.
>
> The entity ceiling still holds and is corroborated locally: the scatter catalog's own profiles cap at 3-12 entities for the rank-loss field and 3-8 for the small-field outlier. What does not hold is the proof-role conclusion. See [`00-reconciliation.md`](00-reconciliation.md) §1.

**Duration stops scaling past three entities.** Median unit length runs 8.5s, 10.2s, 13.0s for one, two and three entities, then falls back to 12.0s at four and 10.8s beyond. Internal changes plateau at two from two entities upward. Beyond three, extra entities are shown simultaneously rather than sequenced, so time stops buying anything and legibility becomes the binding constraint instead.

---

## 4.5 Evidence obligations

`sourceSpecificity` is one of the four clean fields, and it behaves exactly as a proof ladder should.

| Function | Exact source | Exact event or entity | Representative | Decorative |
|---|---|---|---|---|
| evidence | 60% | 37% | 3% | 0% |
| example | 45% | 50% | 5% | 0% |
| comparison | 44% | 50% | 6% | 0% |
| summary | 36% | 48% | 16% | 0% |
| claim | 29% | 62% | 10% | 0% |
| contrast | 20% | 59% | 22% | 0% |
| transition | 21% | 62% | 7% | **10%** |
| setup | 31% | 49% | 18% | **3%** |
| emotional_beat | 7% | 64% | 29% | 0% |

**Decorative media appears as the strictest obligation on transition and setup beats only.** Every other rhetorical function is at zero. That is a clean enforceable rule: outside a transition or a section reset, nothing decorative may carry a unit.

---

## 4.6 Which function-to-treatment associations actually travel

Testing each association per reference rather than pooling.

**Cross-topic. Holds in every reference where it could be measured.**

| Association | Lift | Units |
|---|---|---|
| evidence to `evidence_or_document` | 3.03x | 51 |
| escalation to `counter_or_numeric` | 2.80x | 6 |
| contrast to `archival_footage` | 1.93x | 26 |
| example to `archival_footage` | 1.84x | 22 |
| example to `direct_broll` | 1.82x | 14 |
| causation to `archival_footage` | 1.59x | 13 |

The evidence association also runs in reverse: evidence passages actively avoid `direct_broll` at 0.56x and `portrait_or_cutout` at 0.48x. Proof passages push decorative containers away.

**Likely, but thinner.** comparison to carousel and to portrait pairs, chronology to single image hold, summary and transition to interview footage, evidence to infographic, reversal to portrait.

**Single-creator. Do not promote.** contrast to portrait, claim to carousel, chronology to carousel, summary to custom motion graphic, causation to custom motion graphic, and notably **setup to interview footage** and **claim to interview footage**. Those last two look strong when pooled and are one creator's habit. A naive lift table would have encoded them as global rules.

---

## 4.7 What the references say goes wrong

681 recorded failure conditions, all distinct. Ranked by frequency of theme:

| Theme | Per 100 conditions |
|---|---|
| Generic, stock or unrelated media standing in for something specific | 19 |
| Text or evidence illegible, or held too briefly to read | 8 |
| Visual event out of sync with the spoken phrase | 6 |
| Clutter, too many simultaneous elements | 5 |
| Holding too long with no internal change | ~4 |
| Anachronism, modern footage for a historical claim | ~1 |

The dominant failure is substitution: using something that looks right instead of the thing that is right. It is more than twice as common as the next theme. This is direct empirical support for the brief's priority order, and it is the reason the specificity gate sits above the timing gate.

Anachronism is low-frequency but I would still promote it to a hard gate. It is cheap to check when an era constraint is recorded on the media role, and it is silently wrong when missed, which is the worst combination.

---

## 4.8 A traceable replacement for the eight patterns

Because the eight headline patterns have no link to any unit, I derived a replacement from the four clean fields: narration job, evidence obligation, primary editorial role, entity bucket. Sixteen clusters have at least eight units and appear in at least two references, covering 358 of 628 units. Every cluster carries its unit ids, so any claim about it can be checked. The full set is in `data/derived-contract-clusters.json`.

The largest, as a sample:

| Job | Specificity | Role | Entities | n | Refs | Median | Top treatments |
|---|---|---|---|---|---|---|---|
| PROVE | exact | proof | 1 | 68 | 4 | 8.9s | evidence_or_document, custom_motion_graphic, archival |
| FRAME | exact | subject | 1 | 57 | 4 | 7.0s | interview, direct_broll, custom_motion_graphic |
| PROVE | exact | proof | 2 | 44 | 4 | 11.8s | archival, evidence_or_document, direct_broll |
| ASSERT | exact | subject | 1 | 42 | 4 | 8.0s | interview, direct_broll, archival |
| COMPARE | exact | subject | 1 | 23 | 4 | 7.0s | archival, interview, portrait |

Fifteen of the sixteen clusters carry an exact obligation. The single loose cluster is also the shortest at 4.8 seconds median. Precision is the norm in this corpus and vagueness is a brief functional beat, not a resting state.

I am not proposing these clusters replace the eight patterns as a vocabulary. The eight read better. The point is that a pattern set should carry its evidence, and this shows that is achievable cheaply.

---

## 4.9 What is subject-specific

**Specific to the exact-subject music documentary.** Music video and concert footage as a dominant media family. Album artwork as a proof artifact. The particular density of archival footage at 101 of 274 units. Performance footage as an emotional reset.

**Adjacent-domain, from the data-led reference.** Progressive chart scenes that advance internal callouts rather than cutting. Benchmark sampling, where known mid-tier examples are shown before the outlier. A much slower overall cadence, which as established is the creator and not the format.

**Cross-topic, safe to carry over.** The evidence-to-document association. The proof ladder and the decorative-media restriction to transitions. The roughly 6 to 7 seconds per internal change budget. The 1.5 second readable floor. The establish-then-land event offset. Container capacity by entity count. Counters running long and single image holds running short. The generic-substitution failure mode as the dominant risk.
