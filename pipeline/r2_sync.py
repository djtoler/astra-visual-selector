#!/usr/bin/env python3
"""Media Library files -> Cloudflare R2, by tier, id-addressed. Dry run by default.

WHY R2 AND NOT THE REPO. Measured 2026-09-25: the display tier is 1.46 GB across
557 files. Git cannot hold that; the metadata snapshot (2.7 MB) can and does. So
the split is metadata in git, pixels in object storage, and the two are joined by
a key derived from the asset id — never by a local absolute path, which is the
thing that made the layer local-only in the first place (LOG 0105).

THE KEY IS DERIVED, NEVER STORED. `media/<asset_id>/<role><ext>`. An id-addressed
key means the snapshot needs no new field, a re-export cannot invalidate a URL,
and the same asset re-processed lands on the same key. A key built from the
source filename would break on every rename in the library.

    python3 pipeline/r2_sync.py                       plan the display tier, upload nothing
    python3 pipeline/r2_sync.py --tier derivatives    plan a wider tier
    python3 pipeline/r2_sync.py --push                UPLOAD. Costs money. Ask first.

SPEND IS THE USER'S DECISION. This never runs without --push, never creates a
bucket, and never writes a credential. It reads ~/.aws/credentials profile
`astra-r2` and the endpoint from ASTRA_R2_ENDPOINT, both of which the user sets.
"""
import collections, json, os, pathlib, subprocess, sys

P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P))
import paths as PATHS
import media_candidates as M

import r2_client as RC
_E = RC.env()
BUCKET = os.environ.get("ASTRA_R2_BUCKET") or _E.get("CLOUDFLARE_R2_BUCKET") or "niche01-bucket"
PUBLIC = _E.get("CLOUDFLARE_PUB_DEV_URL", "").rstrip("/")
TIERS = ("display", "derivatives", "originals")


def key_for(asset_id, role, path, disambiguator=""):
    suf = pathlib.Path(path).suffix.lower()
    return f"media/{asset_id}/{role}{disambiguator}{suf}"


def _sha8(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:8]


def plan(tier="display", pool=None):
    """-> [{asset_id, role, local, key, bytes}], deduped on key.

    Ordered display-first so a partial upload is still a usable library: the
    review UIs show the display file and nothing else.
    """
    pool = M.load() if pool is None else pool
    refs, seen_path = [], set()

    def add(aid, role, path):
        if not path or not os.path.exists(path) or path in seen_path:
            return
        seen_path.add(path)
        refs.append({"asset_id": aid, "role": role, "local": path,
                     "bytes": os.path.getsize(path)})

    for aid, r in sorted(pool.items()):
        add(aid, "display", r.get("display"))
    if tier in ("derivatives", "originals"):
        for aid, r in sorted(pool.items()):
            for d in r.get("derivatives") or []:
                add(aid, d.get("type") or "derivative", d.get("path"))
    if tier == "originals":
        for aid, r in sorted(pool.items()):
            add(aid, "original", r.get("path"))

    # COLLISIONS. Measured 2026-09-25 on the originals tier: 2275 file references
    # produce 2023 naive keys, and 244 keys hold more than one distinct file. Two
    # causes, and they must NOT be treated alike:
    #   identical bytes in two places — output/previews and output/review hold the
    #     same 3,243,432-byte file, and two lifecycle runs kept the same original.
    #     One key is correct; deduping is the point.
    #   DIFFERENT files under one derivative_type — output/cutouts and
    #     output/quality-cutouts are both type `cutout` at 440,621 and 1,074,025
    #     bytes. One key means the later upload silently wins, possibly the worse
    #     file. A content suffix separates them and nothing is lost.
    # The first version dropped both with `if k in seen: return` and said nothing.
    by = collections.defaultdict(list)
    for r in refs:
        by[key_for(r["asset_id"], r["role"], r["local"])].append(r)
    out, collisions = [], []
    for k, group in sorted(by.items()):
        if len(group) == 1:
            group[0]["key"] = k
            out.append(group[0])
            continue
        digests = {}
        for r in group:
            digests.setdefault(_sha8(r["local"]), []).append(r)
        if len(digests) == 1:                      # same bytes: one key, no loss
            r = group[0]
            r["key"] = k
            r["duplicates"] = len(group) - 1
            out.append(r)
            continue
        collisions.append((k, {d: len(v) for d, v in digests.items()}))
        for d, v in sorted(digests.items()):       # distinct files: distinct keys
            r = v[0]
            r["key"] = key_for(r["asset_id"], r["role"], r["local"], f"-{d}")
            r["disambiguated"] = d
            out.append(r)
    return out, collisions



def preflight():
    """Say plainly what is and is not configured. Never fixes it.

    Uses pipeline/r2_client.py, not the aws CLI: awscli 2.18.12 on this machine
    cannot load _cffi_backend and exits 255 before the network. See LOG 0109.
    """
    need = ("CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_ACCESS_KEY",
            "CLOUDFLARE_SECRET_ACCESS_KEY")
    for k in need:
        print(f"   {k:30} {'set' if _E.get(k) else 'MISSING'}")
    print(f"   {'bucket':30} {BUCKET}")
    print(f"   {'public base url':30} {PUBLIC or 'not set (objects will need signed reads)'}")
    if any(not _E.get(k) for k in need):
        return False, None
    r2, _ = RC.from_env()
    code, _ = r2.head_bucket(BUCKET)
    print(f"   {'bucket reachable':30} {'yes' if code == 200 else f'NO (HTTP {code})'}")
    if code != 200:
        return False, r2
    c, keys, _, _ = r2.list_objects(BUCKET, prefix="media/", limit=1000)
    print(f"   {'objects already present':30} {len(keys)}")
    return True, r2


def main(argv):
    tier = "display"
    for t in TIERS:
        if f"--tier={t}" in argv or (("--tier" in argv) and t in argv):
            tier = t
    push = "--push" in argv
    confirmed = "--confirm" in argv

    print("=== R2 configuration ===")
    ready, r2 = preflight()
    print(f"\n=== plan: tier {tier} ===")
    items, collisions = plan(tier)
    by = collections.Counter(i["role"] for i in items)
    tot = sum(i["bytes"] for i in items)
    for role, n in by.most_common():
        b = sum(i["bytes"] for i in items if i["role"] == role)
        print(f"   {role:16} {n:5} files  {b/1e9:6.2f} GB")
    print(f"   {'TOTAL':16} {len(items):5} files  {tot/1e9:6.2f} GB")
    dupes = sum(i.get("duplicates", 0) for i in items)
    print(f"   source: {M.SOURCE}   first key: {items[0]['key'] if items else '—'}")
    print(f"   byte-identical duplicates collapsed: {dupes}")
    if collisions:
        print(f"   DISTINCT FILES SHARING A derivative_type: {len(collisions)} keys "
              f"— each split by an 8-char content hash, nothing dropped")
        for k, d in collisions[:3]:
            print(f"     {k} -> {len(d)} versions")

    if not push:
        print("\n   DRY RUN — nothing uploaded. --push --confirm uploads, "
              "and that is spend.")
        return 0
    if not ready:
        print("\n   REFUSING to push: the configuration above is incomplete.")
        return 1
    if not confirmed:
        # Two words, not one. A stray --push in a test harness nearly sent 1.46 GB
        # on 2026-09-25; the credentials come from .env, so withholding an env var
        # did not stop it. Spend is the user's decision (CLAUDE.md, Roles).
        print(f"\n   REFUSING to push: --push needs --confirm as well. "
              f"This would send {len(items)} file(s), {tot/1e9:.2f} GB, "
              f"to {BUCKET}.")
        return 1
    # Per-object PUT, skipping keys already present at the same size. R2 charges
    # Class A per write, so re-uploading an unchanged object is pure waste.
    _, existing, token, _ = r2.list_objects(BUCKET, prefix="media/", limit=1000)
    while token:
        _, more, token, _ = r2.list_objects(BUCKET, prefix="media/", token=token, limit=1000)
        existing += more
    have = dict(existing)
    todo = [i for i in items if have.get(i["key"]) != i["bytes"]]
    skip = len(items) - len(todo)
    print(f"\n   {skip} already uploaded at the same size, {len(todo)} to send "
          f"({sum(i['bytes'] for i in todo)/1e9:.2f} GB)")
    sent = failed = 0
    for n, i in enumerate(todo, 1):
        ct = RC.CT.get(pathlib.Path(i["local"]).suffix.lower())
        code, body, _ = r2.put_file(BUCKET, i["key"], i["local"], content_type=ct)
        if code in (200, 204):
            sent += 1
        else:
            failed += 1
            print(f"   FAILED {i['key']} HTTP {code} "
                  f"{body[:120].decode('utf8','replace')}")
            if failed >= 5:
                print("   stopping after 5 failures")
                break
        if n % 50 == 0 or n == len(todo):
            print(f"   {n}/{len(todo)}  sent {sent}  failed {failed}")
    (P.parent / "grammar" / "r2-manifest.json").write_text(json.dumps(
        {"_bucket": BUCKET, "_publicBase": PUBLIC, "_tier": tier,
         "_count": len(items), "_bytes": tot, "_sent": sent, "_skipped": skip,
         "_failed": failed,
         "keys": {i["asset_id"]: i["key"] for i in items if i["role"] == "display"}},
        indent=1))
    print(f"   wrote grammar/r2-manifest.json")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
