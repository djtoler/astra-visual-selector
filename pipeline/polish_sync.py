#!/usr/bin/env python3
"""Fetch the few Polish files this pipeline reads, from GitHub, not the filesystem.

WHY THIS EXISTS. ~/Documents/ChatGPT/Polish became unreadable on 2026-09-26 —
VS Code runs App-Translocated from ~/Downloads, so no TCC grant attaches to it
(LOG 0126). The first workaround was a local copy, guarded against staleness by
comparing mtimes (LOG 0127). Both are beaten by the fact that Codex's tree is
`github.com/djtoler/Polish`, pushed to the same day. GitHub reaches past the
file-access wall entirely, and it is CONTENT-ADDRESSED: a git blob sha says a
file is the same file, which an mtime only approximates.

WHAT IT TAKES. 5 files, 4.5 MB, out of a 338 MB / 6,742-file repo. Not the
clips: .thumbcache already holds 828 derived previews and covers every template
we have shown. Each file is here because something reads it, named below.

    python3 pipeline/polish_sync.py           report what is stale, fetch nothing
    python3 pipeline/polish_sync.py --fetch   write them into polish-mirror/
"""
import base64, hashlib, json, pathlib, subprocess, sys, time

REPO = "djtoler/Polish"
REF = "main"
P = pathlib.Path(__file__).resolve().parent
MIRROR = P.parent / "polish-mirror"
MANIFEST = MIRROR / ".mirror.json"

# Every path here names its consumer. A file with no consumer does not belong.
FILES = {
    "ae-template-automation/scene-library/approved/approved-list.json":
        "candidates.load() — the authoritative template pool, 445 records",
    "ae-template-automation/scene-library/approved/catalog.json":
        "candidates.load() enrichment — family, which FAM_MAX caps slates by",
    "ae-template-automation/scene-library/description-inventory.json":
        "candidates.load() enrichment — mechanism and name",
    "ae-template-automation/narration-visual-annotations/year-seventeen-30-passages.md":
        "paths.narration() — the beat passages",
    "media_workflows.md":
        "standing project rules, cited by CLAUDE.md",
}


def gh(path, jq=None):
    cmd = ["gh", "api", path] + (["--jq", jq] if jq else [])
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode:
        raise SystemExit(f"   gh api {path} failed:\n   {out.stderr.strip()[:400]}")
    return out.stdout


def remote_tree():
    """path -> (blob sha, size) for the paths we care about."""
    raw = gh(f"repos/{REPO}/git/trees/{REF}?recursive=1",
             '.tree[] | select(.type=="blob") | "\\(.path)\\t\\(.sha)\\t\\(.size)"')
    tree = {}
    for line in raw.splitlines():
        p, sha, size = line.split("\t")
        if p in FILES:
            tree[p] = (sha, int(size))
    missing = set(FILES) - set(tree)
    if missing:
        raise SystemExit(f"   not in {REPO}@{REF}: {sorted(missing)}")
    return tree


def blob_sha(data: bytes) -> str:
    """Git's own object id, so a fetched file can be proved to be the blob asked
    for. A length check would pass on a truncated-then-padded download."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def load_manifest():
    if not MANIFEST.exists():
        return {}
    try:
        return json.loads(MANIFEST.read_text()).get("files", {})
    except (json.JSONDecodeError, OSError):
        return {}


def status():
    """(verdict, rows). Compares the mirror's recorded blob sha against GitHub."""
    tree, have = remote_tree(), load_manifest()
    rows = []
    for p in FILES:
        sha, size = tree[p]
        local = MIRROR / p
        rec = have.get(p)
        if not local.exists() or not rec:
            rows.append({"path": p, "state": "missing", "sha": sha, "size": size})
        elif rec.get("sha") != sha:
            rows.append({"path": p, "state": "stale", "sha": sha, "size": size,
                         "was": rec.get("sha", "")[:8]})
        elif blob_sha(local.read_bytes()) != sha:
            rows.append({"path": p, "state": "corrupt", "sha": sha, "size": size})
        else:
            rows.append({"path": p, "state": "fresh", "sha": sha, "size": size})
    bad = [r for r in rows if r["state"] != "fresh"]
    return ("fresh" if not bad else "stale"), rows


def fetch():
    tree = remote_tree()
    head = json.loads(gh(f"repos/{REPO}/commits/{REF}"))
    wrote, kept = [], []
    have = load_manifest()
    files = {}
    for p in FILES:
        sha, size = tree[p]
        local = MIRROR / p
        if local.exists() and have.get(p, {}).get("sha") == sha \
                and blob_sha(local.read_bytes()) == sha:
            kept.append(p)
        else:
            data = base64.b64decode(json.loads(
                gh(f"repos/{REPO}/git/blobs/{sha}"))["content"])
            got = blob_sha(data)
            if got != sha:
                raise SystemExit(f"   {p}: blob sha mismatch, got {got[:8]} "
                                 f"want {sha[:8]} — refusing to write")
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(data)
            wrote.append((p, len(data)))
        files[p] = {"sha": sha, "size": size, "reason": FILES[p]}
    MIRROR.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(
        {"repo": REPO, "ref": REF, "commit": head["sha"],
         "committedAt": head["commit"]["committer"]["date"],
         "fetchedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
         "files": files}, indent=1) + "\n")
    for p, n in wrote:
        print(f"   fetched  {n/1e6:6.2f} MB  {p}")
    for p in kept:
        print(f"   current              {p}")
    print(f"\n   {REPO}@{head['sha'][:8]}  committed {head['commit']['committer']['date']}")
    return 0


def main():
    if "--fetch" in sys.argv:
        return fetch()
    verdict, rows = status()
    have = load_manifest()
    for r in rows:
        print(f"   {r['state']:8} {r['size']/1e6:6.2f} MB  {r['path']}")
    print(f"\n   {verdict.upper()} against {REPO}@{REF}")
    if verdict != "fresh":
        print("   run: python3 pipeline/polish_sync.py --fetch")
    return 0 if verdict == "fresh" else 1


if __name__ == "__main__":
    sys.exit(main())
