# 7. Evaluation plan

## What we are testing for

The brief's evaluation standard has ten clauses. Seven are measurable, three are judgement. Both need to be in the plan, and the judgement ones must not be quietly dropped because they are harder.

**Measurable**

| Test | Metric | Fixture |
|---|---|---|
| Reproduces approved choices | Slate coverage: the approved treatment appears in the four | The 30 annotated passages |
| Avoids rejected mismatches | Rejection recall: previously rejected treatments never rank first | `evaluation-feedback.json`, rejected scenes |
| Aligns visual events to phrases | Drift within tolerance on decisive events | Annotated passages with measured timing |
| Separates media from template | Contract contains zero filenames and zero template ids | Static check on every contract |
| Refuses invented entities | No candidate introduces an entity absent from the contract | Static check on every candidate |
| Prefers direct treatment when right | Agreement on passages the user approved as direct footage or a plain hold | Approved catalog |
| Surfaces gaps | Missing assets and capabilities reported, not substituted | Passages with known missing assets |

**Judgement, assessed by review rather than a number**

Whether the reasoning is understandable enough to correct. Whether corrections land at the right scope. Whether the system survives a new script and a newly bought template without rework.

## Why top-1 agreement is not the headline metric

The corpus is unambiguous on this. Two passages with an identical narration contract agree on treatment only 44.9% of the time against a 34.2% chance rate, and the *same creator* facing the same contract signature agrees with themselves only 43% to 69% of the time.

Holding the system to high top-1 agreement would reward a model that had learned one person's habits rather than the actual constraints, and would push it toward confident answers on genuinely open choices. **Slate coverage plus zero gate violations is the honest target.** Top-1 is worth tracking as a secondary signal and worth being suspicious of if it gets very high.

## Test suites

### Suite 1. Ground truth replay — the primary suite

Run all 30 annotated passages through the pipeline with only the information available at decision time.

| Check | Pass condition |
|---|---|
| Slate coverage | The user's approved treatment appears in the four candidates |
| Winner agreement | Secondary signal only, no threshold |
| Gate violations | Zero. Any recommendation violating a hard gate is a failure regardless of what it picked |
| Rejected-treatment recall | No previously rejected treatment ranks first |
| Escalation precision | Every escalation corresponds to a real ambiguity in the record |
| Contract purity | No filenames, no template ids in any contract |

Gate violations and contract purity are absolute. Everything else is tracked as a rate.

### Suite 2. Held-out reference replay — generalization

The four reference documentaries, one held out at a time, as in the back-test. This catches overfitting to the project's own subject. Current measured values, which are the floor any implementation must beat:

| Metric | Value |
|---|---|
| Treatment top-1 from narration alone | 32.6% against an 18.8% baseline |
| Treatment top-1 with media family known | 40.6% against 18.8% |
| Contract-level agreement ceiling | 44.9% narration, 67.7% with media |

The most important property of this suite is that it is **already built and already run**, so it is a regression test from day one rather than an aspiration. `data/backtest-results.json` holds the current numbers.

### Suite 3. Gate unit tests

Each gate gets adversarial fixtures, built from the corpus failure conditions since those describe real mistakes.

- **Specificity.** A stock legal document against an exact-source claim must fail. This is the dominant real-world failure at 19 per 100 recorded conditions.
- **Legibility.** Evidence text below the size or hold threshold must fail.
- **Alignment.** A container with no movable beat at the trigger phrase must fail.
- **Era.** Modern footage against a historical era constraint must fail.
- **Forcing.** A template proposed where a direct treatment scores higher on priorities 1 to 3 must fail.
- **Density.** More simultaneous elements than can be read in the available time must fail.

### Suite 4. Correction scoping

Replay the stored corrections. For each, check that the system recorded it at the narrowest defensible scope, did not promote it on one example, and when it did propose a promotion, produced an impact preview naming every decision that would change.

A deliberate adversarial case: feed a correction that is genuinely passage-specific and confirm no global rule appears. The corpus shows exactly how this goes wrong — `setup` to `interview_footage` and `claim` to `interview_footage` look like strong global rules when the four references are pooled and are one creator's habit. A scoping mechanism that would have promoted those is broken.

### Suite 4b. Vocabulary crosswalk

Once the crosswalk exists, check it both ways: every `input.job` value in the 30 cases resolves to at least one scene `function` and at least one profile `intent`, and every catalog value is reachable from some job. Unreachable catalog entries and unservable jobs are both defects, and the current state has plenty of each.

### Suite 5. Reverse mapping

For each capability record, generate the narration structures it claims to serve, and confirm that passages of that structure in the corpus actually used a comparable container. Records claiming capability they never demonstrate are flagged as untested rather than trusted.

### Suite 6. Confidence calibration

Not runnable yet. It needs accumulated accept and reject decisions. The method: bucket recommendations by score, measure observed acceptance per bucket, fit score to acceptance, and set the auto-advance threshold at the band meeting the user's chosen acceptance rate. Report reliability as calibration error, not accuracy.

Until this suite has data, **auto-advance stays disabled** and every decision reports `uncalibrated_prior`. That is a policy, not a tuning parameter.

## Fixtures

All fixtures are now readable and every suite can be built.

| Suite | Fixture | Status |
|---|---|---|
| 1 Ground truth replay | `year-seventeen-30-selector-cases.json`, `-results.json`, `year-seventeen-30-passages.md` | Available. 30 cases with desired outcome, shot count and fallback. |
| 1 Baseline to beat | `year-seventeen-30-selector-results.md` | Available. A deterministic baseline has already been run across all 30 with scores and review flags, so this is a regression comparison, not a cold start. |
| 2 Held-out reference | `data/backtest-results.json` | Built and run. |
| 3 Gate fixtures | `feedback-calibration.json` raw comments, `approved-catalog-policy.json` exclusions | Available. Real rejections with reasons, including a template removed for style and two excluded for having no dark-theme control. |
| 4 Correction scoping | 33 feedback records, 10 derived global rules | Available. `30.01` is missing from an expected 34. |
| 5 Reverse mapping | `scriptMatching` on 72 of 185 scenes, `intents` on all infographic and scatter profiles | Partially available. The AE side is 39% populated. |
| 6 Calibration | none yet | Needs accumulated accept/reject decisions. |

**Two suite-1 details worth setting now.** Your cases record a `shots` field, so shot decomposition is independently scorable against ground truth rather than being folded into treatment choice. And `fallback` is `review` on 20 of 30 cases, which means escalation is the expected outcome for two thirds of the set — a system that escalates rarely is failing, not succeeding.

**A gate fixture worth building.** The specificity gate needs a case where correct-looking assets are not the named entities. The scatter system already has the machinery to check this — `headshot-requirements.json` and `spatial-media-preflight.json` — so the fixture is a render whose image bindings were not completed, asserted as identity evidence. The expected result is a specificity failure at preflight, not at selection.

### Suite 2. Held-out reference replay — generalization

The four reference documentaries, one held out at a time, as in the back-test. This catches overfitting to the project's own subject. Current measured values, which are the floor any implementation must beat:

| Metric | Value |
|---|---|
| Treatment top-1 from narration alone | 32.6% against an 18.8% baseline |
| Treatment top-1 with media family known | 40.6% against 18.8% |
| Contract-level agreement ceiling | 44.9% narration, 67.7% with media |

The most important property of this suite is that it is **already built and already run**, so it is a regression test from day one rather than an aspiration. `data/backtest-results.json` holds the current numbers.

### Suite 3. Gate unit tests

Each gate gets adversarial fixtures, built from the corpus failure conditions since those describe real mistakes.

- **Specificity.** A stock legal document against an exact-source claim must fail. This is the dominant real-world failure at 19 per 100 recorded conditions.
- **Legibility.** Evidence text below the size or hold threshold must fail.
- **Alignment.** A container with no movable beat at the trigger phrase must fail.
- **Era.** Modern footage against a historical era constraint must fail.
- **Forcing.** A template proposed where a direct treatment scores higher on priorities 1 to 3 must fail.
- **Density.** More simultaneous elements than can be read in the available time must fail.

### Suite 4. Correction scoping

Replay the stored corrections. For each, check that the system recorded it at the narrowest defensible scope, did not promote it on one example, and when it did propose a promotion, produced an impact preview naming every decision that would change.

A deliberate adversarial case: feed a correction that is genuinely passage-specific and confirm no global rule appears. The corpus shows exactly how this goes wrong — `setup` to `interview_footage` and `claim` to `interview_footage` look like strong global rules when the four references are pooled and are one creator's habit. A scoping mechanism that would have promoted those is broken.

### Suite 4b. Vocabulary crosswalk

Once the crosswalk exists, check it both ways: every `input.job` value in the 30 cases resolves to at least one scene `function` and at least one profile `intent`, and every catalog value is reachable from some job. Unreachable catalog entries and unservable jobs are both defects, and the current state has plenty of each.

### Suite 5. Reverse mapping

For each capability record, generate the narration structures it claims to serve, and confirm that passages of that structure in the corpus actually used a comparable container. Records claiming capability they never demonstrate are flagged as untested rather than trusted.

### Suite 6. Confidence calibration

Not runnable yet. It needs accumulated accept and reject decisions. The method: bucket recommendations by score, measure observed acceptance per bucket, fit score to acceptance, and set the auto-advance threshold at the band meeting the user's chosen acceptance rate. Report reliability as calibration error, not accuracy.

Until this suite has data, **auto-advance stays disabled** and every decision reports `uncalibrated_prior`. That is a policy, not a tuning parameter.

## Fixtures

All fixtures are now readable and every suite can be built.

| Suite | Fixture | Status |
|---|---|---|
| 1 Ground truth replay | `year-seventeen-30-selector-cases.json`, `-results.json`, `year-seventeen-30-passages.md` | Available. 30 cases with desired outcome, shot count and fallback. |
| 1 Baseline to beat | `year-seventeen-30-selector-results.md` | Available. A deterministic baseline has already been run across all 30 with scores and review flags, so this is a regression comparison, not a cold start. |
| 2 Held-out reference | `data/backtest-results.json` | Built and run. |
| 3 Gate fixtures | `feedback-calibration.json` raw comments, `approved-catalog-policy.json` exclusions | Available. Real rejections with reasons, including a template removed for style and two excluded for having no dark-theme control. |
| 4 Correction scoping | 33 feedback records, 10 derived global rules | Available. `30.01` is missing from an expected 34. |
| 5 Reverse mapping | `scriptMatching` on 72 of 185 scenes, `intents` on all infographic and scatter profiles | Partially available. The AE side is 39% populated. |
| 6 Calibration | none yet | Needs accumulated accept/reject decisions. |

**Two suite-1 details worth setting now.** Your cases record a `shots` field, so shot decomposition is independently scorable against ground truth rather than being folded into treatment choice. And `fallback` is `review` on 20 of 30 cases, which means escalation is the expected outcome for two thirds of the set — a system that escalates rarely is failing, not succeeding.

**A gate fixture that already exists in your data.** The scatter profile for the receding rank ladder records that its field cutouts are placeholders assigned by a seeded random shuffle, confirmed by you with *"no need to match artists atp"*, and states plainly that *"Image slots are not identities."* Any candidate using that layout where the narration names the people must fail the specificity gate. That is a ready-made adversarial test with a known correct answer.

## Reporting

Each run produces per-suite pass rates, a list of every gate violation with the passage and candidate, every escalation with its trigger, a diff against the previous ruleset version, and the calibration curve once it exists. A ruleset change that improves slate coverage while increasing gate violations is a regression, not an improvement, and the report should say so rather than leaving it to be noticed.
