#!/usr/bin/env python3
"""The three local roots, in ONE place, overridable by environment variable.

WHY. Measured 2026-09-25: 17 absolute paths hardcoded across 8 files, all of
them under one of three roots. A cloud session has none of those roots, so every
one of them is an ImportError or a silent empty result, and the deterministic
layer — which needs no pixels at all — cannot run off this machine.

    ASTRA_MEDIA_LIBRARY   default ~/Media Library     (assets, tags, faces)
    ASTRA_POLISH          default ~/Documents/ChatGPT/Polish   (Codex's tree, READ ONLY)
    ASTRA_SNAPSHOT        default grammar/library-snapshot.json

THE FALLBACK IS THE POINT. `library_db()` returns the sqlite when the library is
mounted and None when it is not. A caller that can read the snapshot instead
checks `snapshot()` first; `using_snapshot()` says which source answered, so a
result can never quietly come from the wrong one — the failure mode this file
exists to prevent is not a missing file, it is a present-but-stale one.

    python3 pipeline/paths.py        report what resolves, and from where
"""
import json, os, pathlib, sys

P = pathlib.Path(__file__).resolve().parent
HOME = pathlib.Path.home()


def _env(name, default):
    v = os.environ.get(name)
    return pathlib.Path(os.path.expanduser(v)) if v else default


def library_root():
    return _env("ASTRA_MEDIA_LIBRARY", HOME / "Media Library")


def polish_source():
    """Where Codex's tree really lives, whatever we happen to be reading."""
    return _env("ASTRA_POLISH_SOURCE", HOME / "Documents" / "ChatGPT" / "Polish")


def mirror_root():
    return _env("ASTRA_POLISH_MIRROR", P.parent / "polish-mirror")


def _active_polish():
    """The configured root, BEFORE the freshness guard runs. Separate from
    polish_root() so the guard and the report can both ask what is in use
    without recursing through the guard itself."""
    return _env("ASTRA_POLISH", HOME / "Documents" / "ChatGPT" / "Polish")


def is_mirrored():
    """True when we are reading a copy rather than Codex's own tree."""
    return _active_polish().resolve() != polish_source().resolve()


# --- the mirror guard -------------------------------------------------------
# WHY. The Polish tree became unreadable on 2026-09-26 — VS Code runs
# App-Translocated from ~/Downloads, so no TCC grant can attach to it (LOG 0126).
# The workaround is a local copy. A copy is exactly the failure this file's
# docstring names: "the failure mode this file exists to prevent is not a missing
# file, it is a present-but-stale one." When Codex regenerates approved-list.json
# the mirror keeps answering with the old pool, silently, and every slate built
# from it is wrong in a way nothing reports.
#
# THE AFFORDANCE THAT MAKES THIS CHECKABLE. macOS denies read() on a TCC-protected
# file but still allows stat(). Measured 2026-09-26: open() on catalog.json raised
# PermissionError while stat() returned 1.29 MB. So the mirror's freshness is
# verifiable even when the source's CONTENT is not — mtime and size are enough to
# know the copy is behind, and that is the whole question.

MIRROR_SKEW = 2.0  # seconds; cp does not preserve mtime to the nanosecond


def mirror_status(mirror=None, source=None):
    """Every file in the mirror against its source. Never raises.

    Returns (verdict, rows). verdict is one of:
      "absent"     no mirror on disk
      "fresh"      every file matches its source in mtime and size
      "stale"      at least one source is newer, or differs in size
      "unverified" the source cannot even be stat'd, so nothing can be claimed
    """
    source = pathlib.Path(source or polish_source())
    # Default to the mirror ACTUALLY IN USE. Defaulting to mirror_root() reported
    # "absent" while a mirror was live on ASTRA_POLISH — a guard that inspects the
    # wrong directory is worse than none, because its silence reads as a pass.
    mirror = pathlib.Path(mirror) if mirror else (
        _active_polish() if _active_polish().resolve() != source.resolve()
        else mirror_root())
    if not mirror.is_dir():
        return "absent", []
    rows, stale, unknown = [], 0, 0
    for m in sorted(mirror.rglob("*")):
        if not m.is_file() or m.name.startswith("."):
            continue
        rel = m.relative_to(mirror)
        src = source / rel
        try:
            ss = src.stat()
        except OSError as e:
            rows.append({"rel": str(rel), "state": "unknown", "why": type(e).__name__})
            unknown += 1
            continue
        ms = m.stat()
        if ss.st_mtime > ms.st_mtime + MIRROR_SKEW or ss.st_size != ms.st_size:
            rows.append({"rel": str(rel), "state": "stale",
                         "why": (f"source {ss.st_size}B "
                                 f"{'newer' if ss.st_mtime > ms.st_mtime else 'differs'}, "
                                 f"mirror {ms.st_size}B"),
                         "behind": round(ss.st_mtime - ms.st_mtime)})
            stale += 1
        else:
            rows.append({"rel": str(rel), "state": "fresh", "why": ""})
    if stale: return "stale", rows
    if unknown and unknown == len(rows): return "unverified", rows
    if unknown: return "stale", rows          # partial knowledge is not freshness
    return "fresh", rows


_checked = {}


def _assert_mirror_fresh(root):
    """Called from polish_root() so no consumer can route around it.

    A stale mirror stops the run. It does NOT warn and continue: a warning on
    stdout is indistinguishable from the 40 other lines a builder prints, and the
    artifact it produces carries no record of having been built on old data.
    """
    key = str(root)
    if key in _checked:
        return root
    _checked[key] = True
    verdict, rows = mirror_status(mirror=root)
    if verdict == "stale":
        bad = [r for r in rows if r["state"] != "fresh"]
        lines = "\n".join(
            f"      {r['state']:9} {r['rel']}  ({r['why']})" for r in bad[:12])
        raise SystemExit(
            f"\n   STALE POLISH MIRROR — {len(bad)} of {len(rows)} files are behind "
            f"{polish_source()}\n{lines}\n"
            f"\n   Re-copy them, or unset ASTRA_POLISH to read the real tree.\n"
            f"   Refusing to run: a slate built from a stale pool is wrong and says so "
            f"nowhere.\n")
    return root


def polish_root():
    """The Polish tree, or a local mirror of it when ASTRA_POLISH points at one.

    A mirror is verified on first use. The real tree is never checked — it is
    the source, it cannot be stale against itself.
    """
    root = _active_polish()
    if is_mirrored():
        _assert_mirror_fresh(root)
    return root


def scene_library():
    return polish_root() / "ae-template-automation" / "scene-library"


def narration():
    return (polish_root() / "ae-template-automation"
            / "narration-visual-annotations" / "year-seventeen-30-passages.md")


def library_db():
    """The sqlite catalog, or None when the library is not mounted."""
    p = library_root() / "METADATA" / "media-library.sqlite3"
    return p if p.exists() else None


def library_jsonl():
    p = library_root() / "METADATA" / "assets.jsonl"
    return p if p.exists() else None


def delivery_manifest():
    p = library_root() / "50_COMPLETED" / "Production Ready" / "manifest.json"
    return p if p.exists() else None


def snapshot_path():
    return _env("ASTRA_SNAPSHOT", P.parent / "grammar" / "library-snapshot.json")


def snapshot():
    """The exported catalog, or None. Never a partial dict: a truncated write
    would be worse than an absent file, because it reads as a small library."""
    p = snapshot_path()
    if not p.exists():
        return None
    try:
        with open(p) as fh:
            d = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None
    return d if isinstance(d, dict) and d.get("assets") else None


def using_snapshot():
    """True when the live library is unavailable and a snapshot is present.

    Callers print this. A number derived from a snapshot dated three weeks ago
    is not the same claim as one read from the live catalog, and CLAUDE.md's
    measured-or-estimated rule makes stating which one mandatory.
    """
    return library_db() is None and snapshot() is not None


def source():
    if library_db(): return "live"
    if snapshot(): return "snapshot"
    return "none"


def main():
    rows = [("library root", library_root()), ("  catalog", library_db()),
            ("  assets.jsonl", library_jsonl()),
            ("  delivery manifest", delivery_manifest()),
            ("polish root (read-only)", polish_root()),
            ("  scene library", scene_library()),
            ("  narration", narration()),
            ("snapshot", snapshot_path())]
    for label, p in rows:
        if p is None:
            print(f"   {label:26} MISSING")
            continue
        ok = "ok " if pathlib.Path(p).exists() else "GONE"
        sz = (f"{pathlib.Path(p).stat().st_size/1e6:7.1f} MB"
              if pathlib.Path(p).is_file()
              else ("        dir" if pathlib.Path(p).is_dir() else "          -"))
        print(f"   {label:26} {ok} {sz}  {p}")
    verdict, mrows = mirror_status()
    if verdict != "absent":
        n_ok = sum(1 for r in mrows if r["state"] == "fresh")
        print(f"\n   polish mirror              {verdict.upper()}  "
              f"{n_ok}/{len(mrows)} files match {polish_source()}")
        for r in [x for x in mrows if x["state"] != "fresh"][:8]:
            print(f"      {r['state']:9} {r['rel']}  {r['why']}")

    s = snapshot()
    print(f"\n   source: {source()}"
          + (f"   snapshot has {s['_counts']['assets']} assets, generated "
             f"{s.get('_generatedAt')}" if s else "   no snapshot"))
    if source() == "none":
        print("   NOTHING RESOLVES — set ASTRA_MEDIA_LIBRARY or export a snapshot.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
