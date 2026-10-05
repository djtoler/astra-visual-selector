# P0–P2 implementation acceptance checklist

This is the minimum stage gate. The implementation agent may add stricter tests
but may not remove, weaken, reorder or silently defer these checks.

## Preflight

- [ ] Branch is `matching-layer`; working tree and remote state are reported.
- [ ] Packet parent commit and every manifest hash are verified.
- [ ] Dirty `patterns-storypackage-review` user work is untouched; tests use a
      separate clean checkout pinned to the manifest's Story commit.
- [ ] `AGENTS.md`, `media_workflows.md`, the Astra plan and required audit
      evidence were read before edits.
- [ ] Existing components/options are inventoried before introducing code.
- [ ] A saved plan maps every P0–P2 requirement to executable checks.
- [ ] No unrelated, story-specific, render or template work is in scope.

## P0 — frozen evidence and failing fixtures

- [ ] Calibration manifest binds exact evidence IDs, authorship, source hashes,
      catalog revision and frozen baseline commit.
- [ ] Baseline/new outcome diff has a versioned schema or validated existing
      equivalent.
- [ ] Empty Data/Media coverage, stale receipt, route loss, contract-field loss,
      subspan/scope and variant cases fail for the expected baseline reason.
- [ ] Focused-exploration tie fixture proves the current admitted-position
      dependency without implementing P6.
- [ ] Mutation tests reject altered hashes, context and omitted evidence.
- [ ] Gold and source artifacts remain byte-identical.
- [ ] P0 receipt contains exact commands, results, hashes and rollback.

## P1 — evidence binding and freshness

- [ ] Hashed empty objects cannot satisfy Data or Media coverage.
- [ ] Audited 73 Data and 104 Media needs remain typed gaps where unbound.
- [ ] Field/source mismatch, stale adapter and mutated values fail closed.
- [ ] Unresolved values are never coerced to zero; a measured zero can pass.
- [ ] Coverage is task- and required-field-specific, not file-presence-based.
- [ ] Existing supported schemas remain readable with honest unresolved status.
- [ ] P1 receipt binds P0 receipt, exact inputs/outputs, tests and rollback.

## P2 — shared task projection

- [ ] One versioned source-bound task projection is used by requirements,
      gallery and focused-review consumers.
- [ ] Projection retains route, required meaning, obligations, continuity,
      values/cohorts, Data/Media needs, quote requirements and scoped admissions.
- [ ] All 12 template-ineligible route fixtures stay empty in both gallery and
      focused review.
- [ ] Question-versus-quote behavior follows explicit obligations without losing
      attribution or required text.
- [ ] Prior-story selections cannot affect a new story's input or ordering.
- [ ] Intentional no-template, missing discovery and unresolved feasibility are
      distinct outcomes.
- [ ] Missing/stale projection receipts and local consumer reconstruction fail.
- [ ] P2 receipt binds P1, exact inputs/outputs, tests and rollback.

## Final boundary

- [ ] Relevant full existing test suite passes; unrelated pass status is not
      substituted for missing stage evidence.
- [ ] Baseline/new behavior diff is published with direct links.
- [ ] No P3–P7, rendering, catalog, template or provider work was performed.
- [ ] P0, P1 and P2 are separate reviewable commits or equivalently isolated
      commits with explicit receipts.
- [ ] Agent stops after P2 and names the current blocker.
