#!/usr/bin/env python3
"""Does relevance ranking beat alphabetical? Measured against both ledgers.

Stage 2 of the pipeline does not exist. Its slot is occupied by `id` — alphabetical
sort — as the last tiebreak in _within_family and the family order. This asks whether
a local relevance score in that slot surfaces more of what a human approved.

Two ledgers, both frozen:
  the user's 61 selections from review pass 1
  Codex's 66 approvals from the independent RAG pilot

Writes grammar/relevance-sweep.json. Changes no setting.

    python3 pipeline/retrieval/sweep_relevance.py [--write]
"""
import json, math, pathlib, re, subprocess, sys, datetime
P = pathlib.Path(__file__).resolve().parent
ROOT = P.parent.parent
sys.path.insert(0, str(ROOT / "match-trial")); sys.path.insert(0, str(ROOT / "pipeline"))
import candidates as C, shotlist as S
DB = ["docker", "exec", "-i", "contradiction-pgvector", "psql", "-U", "contradiction",
      "-d", "beat_template_retrieval", "-tA", "-F", "\t"]

def vectors(table, key):
    out = subprocess.run(DB + ["-c", f"select {key}, embedding from {table};"],
                         capture_output=True, text=True).stdout.strip().split("\n")
    d = {}
    for line in out:
        if not line.strip(): continue
        k, v = line.split("\t", 1)
        d[k] = [float(x) for x in v.strip("[]").split(",")]
    return d

def cos(a, b):
    n = math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(y*y for y in b))
    return sum(x*y for x, y in zip(a, b)) / n if n else 0.0

def main(argv):
    which = "openai" if "--openai" in argv else "local"
    suf = "_openai" if which == "openai" else ""
    tv = vectors("template_vectors" + suf, "template_id")
    bv = vectors("beat_vectors" + suf, "beat_id")
    print(f"embedder: {which}")
    print(f"loaded {len(tv)} template and {len(bv)} beat vectors from pgvector")
    pool = {r["id"]: r for r in C.load()}
    bindings = json.load(open(ROOT / "grammar" / "bindings.json"))
    beats_by_p = json.load(open(ROOT / "pipeline" / "beats-all.json"))
    picks_raw = json.load(open(ROOT / "grammar" / "picks.json"))["beats"]
    user = {k.split("-", 1)[1]: v for k, v in picks_raw.items()}
    md = (ROOT / "handoff" / "inbox" / "022-from-codex-second-brain-and-beat-review.md").read_text()
    rag = {b: re.findall(r"\`([^\`]+)\`", ids) for b, _, _, _, _, ids in
           re.findall(r"^\| \`(\w+)\` \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (.+)$", md, re.M)}

    def build(limit, relevance):
        out = {}
        for pid, bs in beats_by_p.items():
            for b in bs:
                b = dict(b); b["_passage"] = pid
                rows = bindings.get(b["job"]) or []
                rows, _ = S.admit_match_cuts(b, rows, pool, picks_raw)
                rows, _ = S.capacity_rank(b, rows, pool)
                rows, _ = S.route_spatial(b, rows, pool)
                if relevance and b["id"] in bv:
                    q = bv[b["id"]]
                    for r in rows: r["_rel"] = cos(q, tv[r["id"]]) if r["id"] in tv else -1.0
                else:
                    for r in rows: r.pop("_rel", None)
                sl, _, _ = C.diversify(rows, limit=limit, corpus_size=len(pool), pool_index=pool)
                out[b["id"]] = [r["id"] for r in sl]
        return out

    rows = []
    for limit in (6, 8, 12):
        for rel in (False, True):
            m = build(limit, rel)
            slots = sum(len(v) for v in m.values())
            u = sum(1 for b, v in user.items() for i in v["selected"] if i in set(m.get(b, [])))
            r = sum(1 for b, ids in rag.items() for i in ids if i in set(m.get(b, [])))
            rows.append({"limit": limit, "relevance": rel, "optionSlots": slots,
                         "userPicksReachable": u, "userTotal": 61,
                         "ragApprovalsReachable": r, "ragTotal": 66})
    print(f"\n{'limit':>6} {'ranking':>12} {'slots':>6} {'your 61':>9} {'RAG 66':>8}")
    for x in rows:
        print(f"{x['limit']:>6} {'relevance' if x['relevance'] else 'alphabetical':>12} "
              f"{x['optionSlots']:>6} {x['userPicksReachable']:>6}/61 {x['ragApprovalsReachable']:>5}/66")
    print()
    for limit in (6, 8, 12):
        a = next(x for x in rows if x["limit"] == limit and not x["relevance"])
        b = next(x for x in rows if x["limit"] == limit and x["relevance"])
        print(f"   at limit {limit:>2}: your picks {a['userPicksReachable']}->{b['userPicksReachable']}  "
              f"RAG approvals {a['ragApprovalsReachable']}->{b['ragApprovalsReachable']}")
    if "--write" in argv:
        (ROOT / "grammar" / "relevance-sweep.json").write_text(json.dumps(
            {"measuredAt": datetime.datetime.now().isoformat(timespec="seconds"),
             "embedder": which,
             "store": "pgvector beat_template_retrieval", "sweep": rows}, indent=1))
        print("\nwrote grammar/relevance-sweep.json")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
