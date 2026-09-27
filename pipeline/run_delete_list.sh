#!/bin/bash
# Execute grammar/delete-list-2026-09-26.json. DRY RUN unless --apply is passed.
#
# Claude does not run this. The Media Library is read-only from Claude's side by
# standing rule, and deletion is irreversible — so the list is produced here and
# the user executes it.
#
#   bash pipeline/run_delete_list.sh            show what would go
#   bash pipeline/run_delete_list.sh --trash    move to ~/.Trash (recoverable)
#   bash pipeline/run_delete_list.sh --apply    rm -f, permanent
set -euo pipefail
LIST="$(dirname "$0")/../grammar/delete-list-2026-09-26.json"
MODE="${1:-dry}"
python3 - "$LIST" "$MODE" <<'PY'
import json, os, shutil, sys, time
list_path, mode = sys.argv[1], sys.argv[2]
d = json.load(open(list_path))
files = [(a["assetId"], f["path"], f["bytes"]) for a in d["assets"] for f in a["files"]]
gone = [(a, p, b) for a, p, b in files if not os.path.exists(p)]
live = [(a, p, b) for a, p, b in files if os.path.exists(p)]
print(f"  list: {len(d['assets'])} assets, {len(files)} registered files")
print(f"  on disk now: {len(live)}  ({sum(b for _,_,b in live)/1e9:.2f} GB)")
print(f"  already gone: {len(gone)}")
if mode == "dry":
    for a, p, b in live[:10]:
        print(f"    {b/1e6:8.2f} MB  {p}")
    if len(live) > 10: print(f"    ... {len(live)-10} more")
    print("\n  DRY RUN — nothing touched.")
    print("  --trash moves to ~/.Trash (recoverable). --apply removes permanently.")
    sys.exit(0)
if mode == "--trash":
    dest = os.path.expanduser(f"~/.Trash/astra-delete-{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(dest, exist_ok=True)
    n = 0
    for a, p, b in live:
        t = os.path.join(dest, a[:12] + "__" + os.path.basename(p))
        try:
            shutil.move(p, t); n += 1
        except OSError as e:
            print(f"    could not move {p}: {e}")
    print(f"  moved {n} file(s) to {dest}")
elif mode == "--apply":
    n = 0
    for a, p, b in live:
        try:
            os.remove(p); n += 1
        except OSError as e:
            print(f"    could not remove {p}: {e}")
    print(f"  permanently removed {n} file(s)")
else:
    print(f"  unknown mode {mode!r}"); sys.exit(2)
print("  NOTE: the sqlite catalog still lists these assets. Their rows are stale "
      "until the library's own tooling reconciles them — that is the library's "
      "job, not this script's.")
PY
