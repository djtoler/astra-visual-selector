# P6 — ordering and focused review of the shared P5 ledger

Authority: docs/p6-gpt-6-1-sol-handoff/MASTER_PROMPT.md and AUTHORIZATION.json.
Base f1852cc includes accepted P5/CR-01 3e0b605. GPT-6.1 Sol medium only.
P6 only; stop before P7. No model execution, rendering or catalog edits.

Inventory: storypackage_candidate_gallery.build/_local_relevance; P5 batch
build/validate and canonical sources; candidates._family/diversify/capacity_band;
focused_candidate_diversity.build exploration; focused_review_queue._signature/
build; focused_review_reconciliation.build; existing sourceGallerySha256-bound
candidate-review decisions. MANIFEST.md and README.md explicitly exclude old UI
experiments. Preserve the active gallery JSON interface; do not import archived
UI/Claude code or build a replacement UI. Local relevance remains supported for
legacy discovery; P6 consumes persisted scores only and never runs a model.

Existing outputs use open dictionaries with candidates, sources, counts and
contractEnforcementReceipt containers. The candidate-review artifact already
binds sourceGallerySha256 and task/candidate decision identities. Use those
representations for a versioned display consumer policy and exact replay. No
source schema extension is required. Legacy discovery remains explicitly
unvalidated, separate from reconciled review publication.

| Stage | Existing component and change | Test-first controls |
|---|---|---|
| P5 prerequisite | Validate exact ledger and source/catalog freshness before use | Ledger/route/catalog/source tampering |
| Ordering | Gallery consumes ledger rows; persisted scores, eligible before unknown, descending score then candidate ID | Process/root determinism, extreme scores, cutoff tie |
| Bounded view | Eligible options up to explicit limit; no family quotas; full templateResult retained verbatim | One/many/zero, overflow, incompatible representative siblings |
| Exploration | Existing family grouping with complete member references and per-member state | Unknown/provenance retention; no family representative suppression |
| Sampling | Existing queue signatures; references to original ledger task hashes, full coverage and explicit unreviewed state | Focused/full identity and coverage mutation |
| Persistence | Existing reconciliation checks exact gallery/queue/display hashes and decision identities | Limit/order/score/family/display/reviewer/feedback mutations |
| Delivery | New reports/astra-p6 evidence, upstream P5 receipt binding and independent replay | Full suite, P0-P6 verifiers, clean-worktree replay |

Before production edits: verify P0-P5, strict P5 replay, 44 focused tests and
278-test full suite (one frozen P6 expected failure). Save new failing regressions
and frozen cutoff-tie target. Production logic stays story-neutral. P5 candidate
membership/fit/duties remain unchanged. Persisted score inputs bind all scores and
limits/reviewer sequence; sorting never grants selection/render authority.
Empty template queues remain valid; missing source route detail is not invented.
No inferred editor review, quality promotion, minimum count or custom exhaustion.

Workflow review: these changes implement existing selection-after-intake,
shared-ledger and human-review memory rules; no new workflow rule is required.
Rollback: revert P6 consumers and invalidate display-bound feedback publication;
retain P5 ledger, complete overflow and historical review evidence.

## Final behavior and acceptance evidence

The registered gallery build supports ledger + persisted ordering inputs. P5
publication replay is mandatory. Eligible native/adapted options precede unresolved
records; score and stable candidate ID break ties within each state. Family quota
is recorded as ignored. Complete templateResult rows remain byte-equivalent to P5,
with separate unknown records, explicit eligible overflow, rejection reasons and
member-level hashes/flags/provenance. Complete task ordering is persisted and bound.
Focused queue signatures reference original task hashes and exactly cover the
complete queue; the sample copies original gallery rows and never retrieves again.
Saved comments retain their status, including unreviewed, and multiple candidate
comments round-trip against the exact gallery/queue and ledger identity. Neither
sampling nor reconciliation infers a package/task human-review state.

The frozen P6 cutoff failure and 10 initial tests fail before production edits
(14 assertions, zero errors, including subtests). The cross-process/root regression
also fails against f1852cc and passes after repair. Two intermediate repair logs
preserve the initial four missing-duty-field/obsolete-score fixture errors and the
corrected run; none are acceptance evidence. Final focused suite: 74 tests pass.
Final complete suite: 290 tests pass with no expected failures; no P7 frozen test
exists in this repository and no P7 quality evaluation or promotion was performed.
All 15 original integrity/stage regressions now pass, including the P6 tie.

Strict P5 replay retains 1,540 variants and zero native/adapted claims. The P6
current (41 tasks, 1,466 variants) and synthetic (2 tasks, 74 variants) artifacts
preserve every record; all remain unresolved, with zero eligible displays. The
focused signature queue retains all 43 tasks because their declared duties differ.
This is truthful coverage, not a claimed review reduction. Positive synthetic
controls separately demonstrate two verified siblings, one verified option, an
incompatible representative, native-unknown sibling, limit overflow and zero route.
Real quality/native/editorial assessment remains pending. JSON gzip artifacts are
only deterministic transport for existing dictionaries. No UI experiment is
imported, no visual fidelity or editor interaction is claimed, and no new schema,
model execution, template, renderer or source/catalog mutation is introduced.

Delivery also requires exact artifact replay from a clean independent worktree,
all P0-P6 verifier bindings, unchanged upstream receipts and gold hashes. Stop for
editor review after push; P7 remains unstarted.
