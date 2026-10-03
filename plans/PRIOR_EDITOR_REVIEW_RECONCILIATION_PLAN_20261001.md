# Prior editor-review reconciliation plan

Status: authorized correction; universal matching harness, review-only

## Objective

Make prior editorial review a mandatory input to documentary matching so the system cannot re-ask settled selections, revive dismissed shown options, or inherit source-beat choices into independently split VisualTasks. The current documentary is regression evidence, not the product boundary.

## Required stages and acceptance checks

1. **Bind source evidence** — Load the reviewed beat/template decisions and current VisualTask comparison through hash-bound inputs. Acceptance: all 40 reviewed beats are present; selection and rendering remain false.
2. **Classify every current candidate** — Emit `prior_selected`, `prior_dismissed`, `prior_none_acceptable`, `not_previously_shown`, or `split_task_requires_independent_review`. Acceptance: selected and dismissed sets reproduce the source exactly; unshown candidates are never called rejected.
3. **Audit prior selections technically** — Attach current mapping/evidence/timing status without converting partial technical evidence into approval. Acceptance: technical conflicts and unresolved evidence remain explicit; no score or probability is used.
4. **Create the human-attention queue** — Include only prior selections with a concrete technical conflict, split-task candidates requiring independent task-level review, and genuine unreviewed shortages. Acceptance: already selected candidates with no contradiction are not shown as fresh choices; dismissed options never enter the approval queue.
5. **Regression and held-out boundary** — Test preserved counts, non-selected semantics, split-task non-inheritance, stale hashes, determinism, and a synthetic unseen fixture. Acceptance: the documentary fixture and synthetic fixture pass with no selection/render authorization.

## Non-goals

- Re-selecting this documentary's templates.
- Treating non-selection as a library-wide rejection.
- Automatically approving final six-choice packets or rendering.
- Hardcoding beat IDs or candidate IDs into runtime logic.
