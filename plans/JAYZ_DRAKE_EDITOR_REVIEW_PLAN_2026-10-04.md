# Jay-Z/Drake @4 editor-review plan

Status: ready for editor review. This is the first editor-facing review of the already
accepted `jayz-drake-settle-it@4` StoryPackage. Automated held-out processing
does not count as editor review.

## Required stages and acceptance checks

1. **Bind the exact accepted package.** Verify the package ID, package digest,
   Story authority commit and shared entity-registry receipt already recorded
   by the adapter.
   - Check: the package digest is
     `21f02e6aa12b133583d7ccfb9683b5879c529a53f41bb692bac0a6d9fe4119d3`
     and the package ID is `jayz-drake-settle-it@4`.
2. **Regenerate review-only matching artifacts in the clean repo.** Run the
   registered splitter and candidate-gallery entry points against current
   general contracts and matching data.
   - Check: every artifact has a current contract-enforcement receipt, source
     paths resolve inside `matching-layer`, and selection/rendering remain
     false.
3. **Create a package-neutral focused review queue.** Select deterministic
   representative tasks by reusable semantic/capability signatures while
   preserving the complete gallery for optional inspection.
   - Check: every represented signature is traceable, no fixture or story ID
     appears in the selection logic, and the queue never validates fit.
4. **Serve the existing review UI from package configuration.** Reuse the
   current gallery, comments, speech-to-text, completed-item filtering and
   source-preview system; do not build a replacement renderer or UI.
   - Check: the page reports `jayz-drake-settle-it@4`, saves to a gallery-hash-
     bound review file, and no Future review state is reused.
5. **Smoke-test and hand off.** Validate the API payload, one reversible review
   save/clear cycle, focused/full queue counts and browser load.
   - Check: the review remains human evidence only and the editor can begin
   without another matching-layer action.

## Readiness result

- Exact package: `jayz-drake-settle-it@4`; accepted package digest matches the
  Story handoff receipt.
- Current review-only output: 186 tasks, 174 with candidates, 12 honest
  no-template tasks, 2,784 candidate cards.
- Focused calibration: 33 deterministic representatives covering all 186 tasks
  through distinct semantic/capability signatures; the full queue is retained.
- Review decisions begin empty and are bound to the exact current gallery hash.
- The configured review API and browser UI loaded successfully; storage and
  revision-conflict tests pass.

## Boundary

This work does not select a final template, authorize rendering, alter an
existing template, or convert a regression result into human approval.
