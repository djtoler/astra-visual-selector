# Matching Layer clean-branch extraction plan

Source: `codex/general-matching-layer-v12` at `e8818ae1f3e56f42d36d111bcc8b8c8aaa73e2d6`
Target: orphan branch `matching-layer`

1. Freeze the validated source and preserve user-owned state.
2. Derive files from registered entrypoints, local imports, default runtime paths, contract receipts, and active tests.
3. Copy only that dependency set into the orphan branch.
4. Add branch-specific operating memory, scope documentation, and manifest.
5. Parse JSON, compile Python, run the isolated suite and harness validation.
6. Push and repoint the repository watcher and active Matching memory.

No stage authorizes template selection, custom visual construction, rendering, or media publication.
