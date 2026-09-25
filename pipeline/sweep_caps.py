#!/usr/bin/env python3
"""Sweep FAM_MAX and SLIDE_MAX against the two review ledgers we have.

Both caps were set on 2026-09-21 from one real complaint — beat 02.02a came back 7
scenes from one pack and 4 from another. They are now measurably discarding options the
user approved: of 39 RAG approvals absent from the frozen pass-1 slate, 21 are cut by
these two rules.

Measures, for every setting, against BOTH ledgers:
  RECOVERED   approvals from Codex's RAG review that the slate now contains
  KEPT        the user's own 61 selections still reachable
  COST        total option slots the reviewer must read

No model calls. Writes grammar/cap-sweep.json so the numbers are a record, not a
message. CHANGES NO SETTING — it restores FAM_MAX and SLIDE_MAX before exiting.

    python3 pipeline/sweep_caps.py [--write]
"""
import json, pathlib, re, sys
P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P)); sys.path.insert(0, str(P.parent / "match-trial"))
import candidates as C, shotlist as S
G = P.parent / "grammar"
OUT = G / "cap-sweep.json"

def rag_approvals():
    md = (P.parent / "handoff" / "inbox" /
          "022-from-codex-second-brain-and-beat-review.md").read_text()
    return {b: re.findall(r"\`([^\`]+)\`", ids) for b, _, _, _, _, ids
            in re.findall(r"^\| \`(\w+)\` \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (.+)$", md, re.M)}

def build(pool_index, bindings, beats, picks, limit=12):
    """One slate per beat at the current cap settings. Mirrors shotlist.main()."""
    out = {}
    for pid, bs in beats.items():
        for b in bs:
            b = dict(b); b["_passage"] = pid
            bound = bindings.get(b["job"]) or []
            bound, _ = S.admit_match_cuts(b, bound, pool_index, picks)
            bound, _ = S.capacity_rank(b, bound, pool_index)
            routed, _ = S.route_spatial(b, bound, pool_index)
            slate, _, _ = C.diversify(routed, limit=limit, corpus_size=len(pool_index),
                                      pool_index=pool_index)
            out[b["id"]] = [r["id"] for r in slate]
    return out

def main(argv):
    pool_index = {r["id"]: r for r in C.load()}
    bindings = json.load(open(G / "bindings.json"))
    beats = json.load(open(P / "beats-all.json"))
    picks_raw = json.load(open(G / "picks.json"))["beats"]
    picks = {k: v for k, v in picks_raw.items()}
    user = {k.split("-", 1)[1]: v for k, v in picks_raw.items()}
    rag = rag_approvals()

    rag_total = sum(len(v) for v in rag.values())
    user_total = sum(len(v["selected"]) for v in user.values())
    real_f, real_s = C.FAM_MAX, C.SLIDE_MAX
    rows = []
    try:
        for f in (1, 2, 3):
            for sl in (3, 5, 8, 99):
                for lim in (12, 16, 20):
                    C.FAM_MAX, C.SLIDE_MAX = f, sl
                    sl_map = build(pool_index, bindings, beats, picks, limit=lim)
                    slots = sum(len(v) for v in sl_map.values())
                    rec = sum(1 for b, ids in rag.items() for i in ids
                              if i in set(sl_map.get(b, [])))
                    kept = sum(1 for b, v in user.items() for i in v["selected"]
                               if i in set(sl_map.get(b, [])))
                    served = sum(1 for v in sl_map.values() if v)
                    rows.append({"FAM_MAX": f, "SLIDE_MAX": sl, "limit": lim,
                             "optionSlots": slots,
                             "meanPerBeat": round(slots / len(sl_map), 2),
                             "ragApprovalsReachable": rec, "ragTotal": rag_total,
                             "userPicksReachable": kept, "userTotal": user_total,
                             "beatsWithOptions": served})
    finally:
        C.FAM_MAX, C.SLIDE_MAX = real_f, real_s

    print(f"{'FAM':>4} {'SLIDE':>6} {'LIMIT':>6} {'slots':>6} {'per beat':>9} "
          f"{'RAG approvals':>14} {'your picks':>11}")
    for r in rows:
        star = "  <- live" if (r["FAM_MAX"], r["SLIDE_MAX"], r["limit"]) == (real_f, real_s, 12) else ""
        print(f"{r['FAM_MAX']:>4} {r['SLIDE_MAX']:>6} {r['limit']:>6} {r['optionSlots']:>6} "
              f"{r['meanPerBeat']:>9} {r['ragApprovalsReachable']:>5}/{r['ragTotal']:<8} "
              f"{r['userPicksReachable']:>4}/{r['userTotal']:<6}{star}")
    base = next(r for r in rows if (r["FAM_MAX"], r["SLIDE_MAX"], r["limit"]) == (real_f, real_s, 12))
    print(f"\nagainst the live setting (FAM_MAX={real_f}, SLIDE_MAX={real_s}, limit=12):")
    for r in rows:
        if r is base: continue
        dr = r["ragApprovalsReachable"] - base["ragApprovalsReachable"]
        ds = r["optionSlots"] - base["optionSlots"]
        if dr > 0:
            print(f"   FAM {r['FAM_MAX']} SLIDE {r['SLIDE_MAX']} LIM {r['limit']}: +{dr} approvals "
                  f"for +{ds} slots  ({ds/dr:.1f} extra cards read per approval recovered)")
    if "--write" in argv:
        OUT.write_text(json.dumps({"measuredAt": __import__("datetime").datetime.now()
                                   .isoformat(timespec="seconds"),
                                   "live": {"FAM_MAX": real_f, "SLIDE_MAX": real_s},
                                   "ledgers": {"ragApprovals": rag_total,
                                               "userSelections": user_total},
                                   "sweep": rows}, indent=1))
        print(f"\nwrote {OUT}")
    else:
        print("\nnot written. Re-run with --write.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
