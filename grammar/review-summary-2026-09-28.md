# What the Review Found

**Twelve problems, drawn from 31 beat reviews and the data they stood on.** Each one carries what was measured, your own words where you named it, and what solving it opens up or holds back. Ordered by how much work it is currently blocking.

No solutions here, by request.

| beats | reviewed | with notes | pairings made | templates kept | templates rejected | assets on offer |
|-------|----------|------------|---------------|----------------|---------------------|-----------------|
| 40 | 31 | 28 | 18 | 67 | 446 | 229 |

All figures measured from `grammar/beat-review-export-2026-09-27.json`, the pool, and the bindings. Nothing here is estimated.

---

## Blocking the most work — these stop beats from being pairable at all

### 1. Drake is added to every beat, whether the beat is about him or not

**36 of 40 beats**

- **36 of 40** beats carry Drake in their entity list while the beat's own sentences never name him. On those beats **367 of 708** candidates are Drake.
- On **13 beats** every single candidate is Drake — 01-01, 02-02b, 03-03, 05-05a, 05-05b, 06-06, 07-07, 08-08, 11-11a and more.
- It comes from one field: `_subject: Drake` in `beat-entities.json`, merged into all 40.

> "drake has no place in the beat. this beat is about currensys songs/albums. currency album covers and songs artwork should be whats available to select from" — 02-02b

> "templates are correct. drake being here is not" — 07-07

**Solving it unblocks:** Slate space. Ten Drake portraits stop crowding out the entities a beat is actually about, on 36 beats at once. It is also the cheapest of the twelve — one field, no model run.

**But it cannot be a blind removal:** Drake is the unnamed subject of much of the script. On 01-01 — "one rapper's catalog" — he is correct and unnamed. Strip the subject everywhere and those beats come back empty. The question is when the subject is implied versus when it is simply absent, and that is a judgement the pipeline currently never makes.

---

### 2. A beat that names a group resolves to nobody

**11 of 40 beats**

- **11 beats** refer to people by count or label rather than by name: "ninety-three rappers", "the 2010 class", "seven rappers", "the next five artists", "eighty-one of the ninety-three", "eleven rappers under the rule".
- **6 of those 11** resolve to exactly one entity, Drake, with 10 candidates, all Drake: 03-03, 13-13a, 13-13b, 14-14, 19-19, 22-22.
- 18-18 says "stack all seven end to end" and resolves **3 of 7** — Drake, J. Cole, Nicki Minaj. The other four of the 2010 class are absent.
- The gazetteer works correctly on names: only **2 of 40** beats name a roster artist with no media, both for Curren$y. The failure is specific to groups, which carry no names to match.

> "where are they in the media selection and why aren't they here" — 19-19

> "only drake images available. system should ask for images of the 93 rappers. drake is only 1 of 93 artists that need to be in this scene" — 03-03

**Solving it unblocks:** Eleven beats become pairable instead of impossible, and it is the precondition for sourcing: you cannot request images of a cohort nobody has enumerated. Six of the eleven currently offer nothing usable at all.

**It also gates problem 3:** A spatial scene holds one marker per person. Offering it on a beat whose cohort is unresolved gives you a template with nothing to put in it.

---

### 3. Spatial scenes are gated by job binding, not by how many things the beat names

**6+ beats · 3 of 4 spatial templates withheld**

- Four spatial/scatter templates are bound to any job. Three of them — `07_labeled_outlier_scatter`, `23_portrait_scatter`, `31_greatest_team_scatter` — are bound **only** to `intersection_of_sets` and `locate_in_distribution`.
- So beat 03-03, which is `explain_the_encoding` and names ninety-three rappers, was offered **2 templates total, 1 of them spatial**.
- 16-16, 18-18, 19-19, 20-20, 21-21a and 27-27 were offered **zero** spatial options despite all referring to cohorts.

> "all spatial templates should be shown as options. period. make 20+ entities and any type of comparative / contrasting intentions be the condition to always show all spatial scenes as options" — 03-03

**Solving it unblocks:** The only template family that can hold ninety-three things becomes reachable on the beats that need it. This is the cheapest fix to the cohort beats' template side — the templates already exist and are already bound, just to the wrong jobs.

**Depends on problem 2:** Worth little on its own. A 93-slot field with ten Drake photos in it is not progress.

---

## Library reachable but unused — the thing you asked for already exists

### 4. Seventy-five pool records are bound to no job — including the template you asked for twice

**75 of 445 records · 17% of the library**

- **75 of 445** pool records are bound to zero jobs, so they can never appear on any slate.
- **51 of those 75** match carousel, rail or slideshow language.
- All **11** `vertical-cinematic-slideshow` records are unbound. That is a vertical carousel of single portrait reveals — the exact treatment you asked for on 27-27.

> "none of the templates are good. a vertical carousel would be perfect. b-roll would be perfect too… The media selections are perfect. all artists show up and are available" — 27-27

> "or any other carousel of multiple cards would be good for this beat, because it's needing multiples rappers from the past" — 30-30a

**Solving it unblocks:** 27-27 and 30-30a directly, and a sixth of the library becomes available to every beat. On 27-27 the media is already right by your own verdict — the template is the only thing missing.

**Blocks nothing, but changes problem 6:** Re-binding the exhausted beats before these 75 are in the pool means binding against a library that is missing a sixth of itself, and doing it twice.

---

## Shape of the unit — the beat is the wrong size for the decision

### 5. A beat carries more than one communication job, and the system allows one

**8 beats, split by you in your own notes**

- On **8 beats** you wrote out which sentence needs which template, by hand: 13-13a, 13-13b, 14-14, 21-21b, 23-23, 24-24, 25-25a, 28-28.
- Each of those beats got **one** job and therefore one bound template set.
- This is why several pairings you made are recorded and then described in the note as wrong — the pairing is the best single answer to a two-part question.

> "'The test uses two floors…' should be separate and matched to a text template that I have to source. 'Plots multiple items across a three-dimensional coordinate space…' is the right choice for 'Watch this one and count how many artists clear both floors'" — 28-28

> "needs separate media and template to depict the 240 million per verse" — 21-21b

**Solving it unblocks:** One pairing per claim instead of one per beat. It removes the forced choice that is producing "the current pairing is not a good match, it's an error" verdicts on beats where both halves were individually answerable.

**It is a paid re-classification, and it gates problem 6:** Beat extraction and job classification would both change shape. Re-binding before this is settled means binding one job per beat and then needing two.

---

### 6. Template supply is exhausted on sixteen beats

**16 of 40 beats · 3 down to two options**

- 446 rejections across the review. After them, **16 beats** have six or fewer bound templates left.
- **Three are down to two**: 02-02b, 04-04, 28-28. 08-08, 11-11b and 26-26 have three.
- 18-18 had **2 offered and 2 rejected** — nothing survived the slate.

> "no good templates to choose from, Nicki, Cole plus 7 other artists need to be shown collectively to represent the 97 billion" — 18-18

**Solving it unblocks:** The sixteen thinnest beats get real choices again rather than a shortlist you have already rejected.

**Should be last, not first:** Re-binding is a paid run, and it depends on problems 4 and 5. Run it now and it binds against a library missing 75 records, with one job per beat where you have asked for several — then it has to be run again.

---

## Eligibility and fit — what is offered cannot always be used

### 7. A template can be offered that no available media can fill

**named on 2 beats, structural across all**

- Nothing records what a template *needs* from its media beyond framing and kind — not era spread, not count, not subject type.
- On 07-07 the beat needs deluxe reissues, a festival slot and a 7:40 set time. All **10 of 10** candidates are Drake portraits.

> "that timeline within the context of the beat, is asking for either 8 albums or 8 portraits from different years/eras. needs to be sourced and overall template to media requirements needs tightening" — 24-24

> "no media thats available can satisfy what this beat needs to communicate" — 07-07

**Solving it unblocks:** The slate stops offering treatments that cannot be filled, and every unfillable one turns into an explicit, specific sourcing request instead of a beat you stall on.

**Blocks nothing:** Independent of the rest, and it makes the sourcing list concrete rather than "more Drake".

---

### 8. Media eligibility has no per-template rules, so group photos reach spatial slots

**1 beat named · affects every spatial scene**

- A spatial node is one marker per person. A photograph containing three people cannot be one marker, but nothing excludes it.
- Eligibility today is framing and kind. Neither describes how many people are in the frame.

> "perfect except drake shows up in single images with others. group photos are ineligible for spatial scenes" — 04-04

**Solving it unblocks:** Spatial beats can trust their candidate lists. 04-04 was otherwise the cleanest result in the review — your word was "perfect except".

**Blocks nothing:** Narrow and self-contained.

---

## Continuity and process

### 9. Nothing carries a treatment across consecutive beats

**4 beats asked for it**

- Selection treats all 40 beats independently. There is no run, no inheritance, and no way to mark a template mandatory for a stretch.
- Asked for on 05-05a, 10-10, 12-12b and 29-29c.

> "needs the same downward template from the previous beat. the one thats paired could work but for visual consistency, they should be the same" — 12-12b

> "beat is asking for a specific chart from the beginning so that template should be the same one marked as mandatory here with explicit decision to go against it" — 29-29c

**Solving it unblocks:** Visual consistency inside a cycle, which you raised four times unprompted. It also reduces the work: a run of three beats becomes one decision rather than three, which matters at twenty videos a day.

**Blocks nothing:** Though it argues against rotation pressure, which currently pushes the other way.

---

### 10. A media verdict cannot be recorded without a template to attach it to

**cost a correct verdict on 27-27**

- Pairing requires a template and at least one asset. On a beat whose template gap is the actual problem, the media judgement has nowhere to go.
- 27-27 records **zero** selected media, and the note says the media was perfect.

> "The media selections are perfect. all artists show up and are available… no selected media because I can't pair it to a template" — 27-27

**Solving it unblocks:** Media work proceeds independently of template gaps. "The media is right here" becomes a durable record the pipeline can read instead of a sentence in a note only a person can interpret.

**Blocks nothing:** But note the data already understates itself: some beats read as unreviewed when they were reviewed and found unpairable.

---

### 11. There is no numeric baseline, because the rating was never the tool you used

**0 of 31 rated · 28 of 31 written**

- **0 of 31** records carry a 1–5 rating. **28** carry prose notes.
- The rating existed to answer your own framing — "current state, we need to use this as how much we need to improve and where". That measurement does not exist.
- The notes are richer than a rating would have been. They name the template wanted, the sentence it belongs to, and the missing media. A score would have carried none of that.

**Solving it unblocks:** A before-and-after for every change in this list. Right now improvement can be argued but not shown, which is the one thing the project's own rules refuse to accept.

**Do not solve it by asking for scores:** You reviewed 31 beats in prose and skipped the buttons on all 31. That is evidence about the instrument, not about compliance.

---

### 12. Six beats have no eligible b-roll, and one should be b-roll only

**6 beats flagged**

- Marked no eligible b-roll: 01-01, 02-02a, 05-05b, 24-24, 25-25a, 30-30b. Each had **5** clips on offer and rejected all five.
- 15-15 recorded "no available broll" in prose before the button existed.
- 27-27 is the opposite case — b-roll was wanted and available, and could not be used for want of a template.

> "this should be b-roll" — 30-30b

> "drake b-roll performance footage needed" — 01-01

**Solving it unblocks:** Beats where no still can do the job. 30-30b and 01-01 are both cases where the note says footage, not a photograph.

**Yours to call:** You said you would raise supply shortages, so this is recorded rather than diagnosed. Listed because the verdicts are in the data now and will otherwise sit unread.

---

## Where the numbers come from

31 review records read from the artifact database, joined against `grammar/bindings.json` (624 bindings), the 445-record pool from `approved-list.json`, the 40-beat shotlist, and the 229 assets named in the export. Entity detection used the 297-name gazetteer in `grammar/entity-roster.json` with word-boundary matching.

**One measurement withdrawn.** A first pass reported "0 of 40 beats name an artist with no media candidate". It built its name list from the assets that already had media, so it could only ever return zero. Redone against the real gazetteer: 2 of 40, both Curren$y.

**What is not here.** No solutions and no code, by request. Dependency order is stated inside each problem where one exists — the short version is that 4 and 5 come before 6, and 2 comes before 3.
