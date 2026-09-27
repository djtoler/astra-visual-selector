#!/usr/bin/env python3
"""Media Library catalog -> grammar/library-snapshot.json. Everything, no pixels.

WHY. The deterministic layer never opens a pixel: it reads ids, tags, faces,
derivative paths, identity and kind. Measured 2026-09-25 — the media is 11 GB and
what the code actually needs is 25 MB, a ratio of 440 to 1. So a cloud session is
not blocked on media, it is blocked on metadata sitting behind absolute local
paths.

This exports EXACTLY the five queries media_candidates.load() runs, plus the
Production Ready delivery, into one diffable JSON. Committing the 20 MB sqlite
directly would bloat history — it is binary and rewrites on every ingest.

    python3 pipeline/export_library.py            report the size, write nothing
    python3 pipeline/export_library.py --write    write the snapshot
"""
import json, os, pathlib, sqlite3, sys, datetime, hashlib

P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P))
import paths as PATHS

OUT = P.parent / "grammar" / "library-snapshot.json"
WRITE = "--write" in sys.argv


def build():
    db_path = PATHS.library_db()
    if not db_path or not os.path.exists(db_path):
        raise FileNotFoundError(f"library catalog not found: {db_path}")
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    assets = {}
    for aid, mt, ext, w, h, dur, path in db.execute(
            "select asset_id, media_type, extension, width, height, duration, "
            "canonical_path from assets"):
        assets[aid] = {"media_type": mt, "ext": ext, "width": w, "height": h,
                       "duration": dur, "path": path,
                       "tags": [], "people": [], "faces": 0, "derivatives": []}
    for aid, tag, src in db.execute("select asset_id, tag, source from tags"):
        if aid in assets: assets[aid]["tags"].append({"tag": tag, "source": src})
    for aid, name in db.execute(
            "select asset_id, identity_name from faces "
            "where identity_name is not null and identity_name <> ''"):
        if aid in assets and name not in assets[aid]["people"]:
            assets[aid]["people"].append(name)
    for aid, n in db.execute("select asset_id, count(*) from faces group by 1"):
        if aid in assets: assets[aid]["faces"] = n
    for aid, dt, dp in db.execute(
            "select asset_id, derivative_type, path from derivatives"):
        if aid in assets: assets[aid]["derivatives"].append({"type": dt, "path": dp})

    # captions ride in assets.jsonl, not the catalog
    jl = PATHS.library_jsonl()
    caps = 0
    if jl and os.path.exists(jl):
        for line in open(jl):
            try: r = json.loads(line)
            except json.JSONDecodeError: continue
            aid, et = r.get("asset_id"), r.get("embedding_text") or ""
            if aid in assets and "Captions:" in et:
                c = et.split("Captions:", 1)[1].strip()
                if c:
                    assets[aid].setdefault("captions", []).append(c)
                    caps += 1

    # The Production Ready delivery is the authoritative identity/kind boundary.
    # Folded in rather than referenced, so the snapshot is self-sufficient.
    delivery = None
    dm = PATHS.delivery_manifest()
    if dm and os.path.exists(dm):
        d = json.load(open(dm))
        # `verification` rides VERBATIM. media_candidates.validate_delivery_manifest
        # fails closed on it — per-category checks plus four bools plus
        # sqlite_integrity — and flattening it to one summary bool would make the
        # snapshot path pass a gate the live path has to earn. The gate must be
        # the SAME gate whichever source answers.
        delivery = {"version": d.get("version"), "generated_at": d.get("generated_at"),
                    "verification": d.get("verification") or {},
                    "categories": {k: [{"asset_id": i["asset_id"],
                                        "delivery_path": i.get("delivery_path")}
                                       for i in v]
                                   for k, v in (d.get("categories") or {}).items()},
                    "person_view": [{"asset_id": pv["asset_id"],
                                     "folders": pv.get("folders") or [],
                                     "identities": pv.get("identities") or []}
                                    for pv in (d.get("person_view") or [])],
                    "tags": d.get("tags") or {}}
    # The project set and the suppressed claims are part of the evidence contract,
    # so the snapshot must carry them or a cloud session silently loses both rules.
    projects = sorted({r[0] for r in db.execute(
        "select distinct project from ingestions where project is not null "
        "and project <> ''") if r[0]})
    import media_candidates as _MC
    claims = [[a, t] for a, t, src in db.execute(
        "select asset_id, tag, source from tag_suppressions")
        if src in _MC.DERIVED_SOURCES]
    return {"projects": projects, "suppressedClaims": claims,
            "_note": "Snapshot of the Media Library catalog — EXACTLY the fields "
                     "media_candidates.load() reads, and nothing else. No pixels. "
                     "Regenerate with pipeline/export_library.py --write.",
            "_source": str(db_path),
            "_generatedAt": datetime.datetime.now().isoformat(timespec="seconds"),
            "_counts": {"assets": len(assets),
                        "tags": sum(len(a["tags"]) for a in assets.values()),
                        "derivatives": sum(len(a["derivatives"]) for a in assets.values()),
                        "captions": caps,
                        "delivered": len(delivery["person_view"]) if delivery else 0,
                        "projects": len(projects), "suppressedClaims": len(claims)},
            "delivery": delivery,
            "assets": assets}


def main():
    snap = build()
    blob = json.dumps(snap, indent=1, ensure_ascii=False)
    mb = len(blob.encode()) / 1e6
    c = snap["_counts"]
    print(f"assets {c['assets']}  tags {c['tags']}  derivatives {c['derivatives']}  "
          f"captions {c['captions']}  delivered {c['delivered']}")
    print(f"snapshot: {mb:.1f} MB   (the sqlite it replaces is "
          f"{os.path.getsize(PATHS.library_db())/1e6:.0f} MB and is binary)")
    if snap["delivery"]:
        import media_candidates as MC
        MC.validate_delivery_manifest(snap["delivery"])   # the SAME gate, run here
        print(f"delivery folded in, {len(snap['delivery']['categories'])} categories, "
              f"verification gate PASSES on the snapshot copy")
    if not WRITE:
        print("\nDRY RUN — nothing written. Re-run with --write.")
        return 0
    OUT.write_text(blob)
    print(f"\nwrote {OUT.relative_to(P.parent)}  "
          f"sha {hashlib.sha256(blob.encode()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
