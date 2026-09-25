#!/usr/bin/env python3
"""Refuse any binding that was not produced by the pipeline.

A binding is valid only if it carries provenance (promptSha, model, runId, verdict,
mechanism, evidence) or is explicitly sourced to the user. Exits non-zero on failure.
Run before publishing anything built on the grammar.
"""
import json, sys, pathlib
G = pathlib.Path("/Users/dwaynetoler/timeline/grammar/bindings.json")
REQUIRED = ("promptSha", "model", "runId", "verdict", "mechanism", "evidence")

def main():
    b = json.load(open(G))
    bad, ok, byuser = [], 0, 0
    for job, rows in b.items():
        for r in rows:
            src = (r.get("provenance") or {})
            if src.get("source") == "user":
                byuser += 1; continue
            missing = [f for f in REQUIRED if not src.get(f)]
            if missing: bad.append((job, r["id"], missing))
            else: ok += 1
    total = ok + byuser + len(bad)
    print(f"bindings: {total}   pipeline-produced: {ok}   user-named: {byuser}   INVALID: {len(bad)}")
    if bad:
        print("\nThese carry no provenance. They were not produced by the pipeline:")
        for job, rid, miss in bad[:40]:
            print(f"  {job:26} {rid[:40]:40} missing {','.join(miss)}")
        if len(bad) > 40: print(f"  ... and {len(bad)-40} more")
        print("\nFIX: run pipeline/bind.py. Do not hand-pick. See the HARD RULE in CLAUDE.md.")
        return 1
    print("all bindings traceable.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
