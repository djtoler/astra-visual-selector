# P5 correction requests

## CR-01 — Make deterministic evidence replay checkout-independent

**Status:** required before P5 acceptance and before any P6 implementation.

P5 is otherwise directionally accepted. Its stage verifier, all P0-P5 stage
verifiers, the 42 focused tests and the complete 276-test suite pass in an
independent worktree. Do not redesign P5 or begin P6.

### Independently reproduced failure

At commit `83c4c6efa28aa19b84246f873424d3550880853b`, from a clean worktree at
`/private/tmp/matching-p5-audit`:

```text
$ python3 tests/astra_p5_evidence.py
ValueError: P5 ledger does not replay from pinned inputs: current
```

The committed and regenerated candidate content is stable. The byte mismatch is
caused by repository-internal source bindings serialized as absolute paths from
the original checkout. Replaying in another checkout serializes the new root;
that also changes `contractEnforcementReceipt.candidateReconciliation.bodySha256`.

Observed uncompressed current-ledger SHA-256 values:

- committed: `d5858f5f5ffb2417693f4fec2db0fab7010251ea4105023049db47642a395151`
- independent replay: `b5bcab86731a19ba6015e220767eaf04b85814530e9d9d81087d205f2083949d`

Normalizing the two checkout-root prefixes leaves only the dependent receipt
body hash different. This is therefore a portability defect in source identity
and hashing, not a candidate-semantics discrepancy.

### Required correction

1. Represent repository-internal evidence sources with a checkout-independent
   canonical identity. Prefer repo-relative paths resolved against the runtime
   repository root. An equivalent design may separate a non-hashed local
   locator from a hashed logical/repo-relative source identity.
2. Do not merely make `tests/astra_p5_evidence.py` ignore absolute paths while
   the contract receipt continues to hash checkout-specific values.
3. Preserve source freshness and mutation detection. Genuinely external inputs
   may retain an absolute locator when necessary, but their stable logical
   identity and content hash must remain explicit.
4. Regenerate the current and synthetic ledgers, outcome diff, P5 receipt and
   every hash/log affected by the canonical representation.
5. Add a regression test that builds or replays P5 evidence under two distinct
   checkout roots and proves identical canonical ledger bytes and receipt hashes
   (or an equivalently strict deterministic representation).

### Acceptance checks

- `python3 tests/astra_p5_evidence.py` passes from an independent clean
  worktree whose absolute root differs from the producing checkout.
- All P0-P5 stage verifiers pass.
- Focused P5, batch-matching and P4 tests pass.
- The complete test suite passes with only the already-frozen expected P6
  failure; the count may increase for the new portability regression.
- Source mutation and freshness tests still fail closed.
- Candidate membership, fit semantics, the zero native/adapted-fit claim,
  catalog/source gold artifacts and production behavior remain unchanged.
- P6 ordering, sampling and display work does not begin.

Commit and push the correction separately, then report the commit plus the exact
independent-worktree replay and test receipts for re-audit.
