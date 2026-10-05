# GPT-6.1 Sol handoff — Astra P0–P2 implementation

This packet starts a new Codex conversation on the approved first implementation
slice of the Astra matching repair plan. It is deliberately bounded to P0, P1
and P2. It does not authorize P3–P7, template selection, rendering, catalog
invention, external provider spend or a new replacement architecture.

## Start here

1. Open `MASTER_PROMPT.md` and paste its fenced prompt into the new conversation.
2. Run that conversation with the user-selected `gpt-6.1-sol` model.
3. Point the conversation at repository `djtoler/astra-visual-selector`, branch
   `matching-layer`, and this directory.
4. The implementation conversation must verify the branch and hashes in
   `HANDOFF_MANIFEST.json` before editing.
5. P0, P1 and P2 run sequentially. Each stage must first prove the frozen
   baseline failure, then implement the narrow repair, then publish a stage
   receipt. Stop after P2 for editor review.

## Current state

- Authoritative implementation branch: `matching-layer`
- Packet parent commit: `5083ba40702181c8c8fa7b53b80d4c009a2aa728`
- Frozen production baseline used by the audit:
  `1276d0ca1daece81b5b7b38c8b5f5280046e5077`
- P0–P2 implementation: authorized by the editor on 2026-10-05
- P3–P7 implementation: not authorized
- Rendering or native-template work: not authorized
- Current blocker at handoff: `none`

Known preflight condition: the default local Story authority checkout at
`../patterns-storypackage-review` is currently on commit
`66992e7bf61483838cfb3609c56076059ee8d4e8` and contains unrelated user changes,
while the audit pins Story commit `d5117a6de0fd0c640a336c6f456946ec8b40f319`.
Do not reset, checkout over or modify that dirty tree. Reuse an existing clean
pinned checkout if available or create a separate non-destructive Git worktree
for the pinned Story commit and point `STORYPACKAGE_AUTHORITY_ROOT` to it.

## Packet files

- `MASTER_PROMPT.md` — ready-to-paste conversation prompt
- `HANDOFF_MANIFEST.json` — pinned branch, evidence and scope authority
- `ACCEPTANCE_CHECKLIST.md` — stage gates and stop conditions

## Supplementary Claude evidence

Claude's interrupted Job 6 work is not a replacement plan and is not an audit
authority. It contributed one verified regression case: 58 of 59 focused-review
tasks land inside an exploration-frequency tie at the cutoff, allowing admitted
list position to decide which tied families appear. Freeze that case in P0 as a
pending P6 regression fixture; do not implement P6 ordering changes during
P0–P2. Do not adopt the handoff's unreproducible historical exposure figures or
its exact aggregate totals without a committed generator and independent check.
