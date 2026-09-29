# Beat 28 split-task accuracy test

Status: authorized accuracy test on `codex/treatment-requirements-review`; review-only and disconnected from live selection or rendering.

## Required stages and acceptance checks

1. Bind the editor-approved phrase boundary to measured narration evidence.
   - The setup task ends and the overlap task begins at the measured start of “Five clear the left floor.”
   - The two task spans must be contiguous, remain inside the saved source-beat speech span, and retain their exact source quotes.
2. Rebuild the VisualTask technical requirements.
   - Both split tasks must carry exact reviewed audio spans.
   - No media-slot, text-field, typed-data, selection, or rendering approval may be inferred from the timing decision.
3. Rebuild the AE technical comparison.
   - The two task records must remain separate and preserve their distinct roles, identity demands, and timing spans.
4. Evaluate actual task-level matching isolation.
   - Report each task’s candidate IDs independently.
   - Passing requires evidence that candidates were matched from each VisualTask’s own role and requirements, rather than copied from the shared source-beat slate.
   - Shared candidates are allowed only when independently justified for both tasks; an identical inherited source-beat pool is not proof of task-level matching.
5. Run deterministic tests and validate every rebuilt artifact.
   - A stale timing-review source must fail validation.
   - Omitting either reviewed split span must leave that task unresolved or fail closed; it must never invent a boundary.

## Explicit non-goals

- No template selection or render authorization.
- No rendering.
- No custom visual or template implementation.
- No live-slate mutation.
