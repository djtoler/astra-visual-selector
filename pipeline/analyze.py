#!/usr/bin/env python3
"""Analyse the rerun: what the new records contributed, and slates by mechanism."""
import json, sys, pathlib
from collections import Counter, defaultdict
P=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/"match-trial"))
import candidates as C

TRIAL={  # what the hand trial showed, and the user's verdict on each
 "B1":{"history-slideshow-envato--scene-001":"shown","counters-envato--scene-003":"shown/RIGHT",
       "modern-photo-slideshow-envato--scene-001":"shown"},
 "B2":{"36_four_portrait_cards":"shown/RIGHT","20_prime_portrait_cards":"shown/RIGHT",
       "intro-slideshow-full-720p--scene-019":"shown/RIGHT"},
 "B3":{"58_big_three_stat_rows":"shown","28_stat_profile_cards":"shown",
       "05_measured_height_ruler":"shown/WRONG"},
 "B4":{"33_contract_portrait_grid":"shown (now removed)","16_ranked_table_and_bars":"shown",
       "06_historical_winners_table":"shown"},
}
PASS={"complete_fit","weaker_fallback"}

def main():
    res=json.load(open(P/"rerun-results.json"))
    recs={r["id"]:r for r in C.load()}
    for beat in ("B1","B2","B3","B4"):
        vs=res.get(beat) or []
        if not vs: print(f"\n=== {beat}: no verdicts ===");continue
        d=Counter(v.get("verdict") for v in vs)
        fit=[v for v in vs if v.get("verdict")=="complete_fit"]
        fb=[v for v in vs if v.get("verdict")=="weaker_fallback"]
        print(f"\n=== {beat} — {len(vs)} judged ===")
        print(f"  {dict(d)}")
        newfit=[v for v in fit if recs.get(v['id'],{}).get('isNew')]
        print(f"  complete fits: {len(fit)}   of those from the 182 new records: {len(newfit)}")

        # slate by distinct mechanism, no ranking
        seen=set(); slate=[]
        for v in fit+fb:
            m=(v.get("mechanism") or "").lower()
            if m in seen: continue
            seen.add(m); slate.append(v)
            if len(slate)==6: break
        print(f"  slate (distinct mechanism, {len(fit)} fits tied):")
        for v in slate:
            tag=" NEW" if recs.get(v['id'],{}).get('isNew') else ""
            print(f"    {v.get('verdict'):16} {v['id'][:40]:40} {v.get('mechanism','')}{tag}")

        print("  trial comparison:")
        for tid,note in TRIAL[beat].items():
            hit=[v for v in vs if v["id"]==tid]
            if hit: now=hit[0].get("verdict")
            elif tid in recs: now="not yet judged"
            else: now="NOT IN CORPUS"
            print(f"    {tid[:40]:40} trial={note:20} now={now}")

    allv=[v for b in res.values() for v in b]
    print(f"\n=== overall ===")
    print(f"  judged {len(allv)}   {dict(Counter(v.get('verdict') for v in allv))}")
    nf=[v for v in allv if v.get('verdict') in PASS and recs.get(v['id'],{}).get('isNew')]
    print(f"  passing candidates from the new records: {len(nf)}")
    print(f"  top new mechanisms: {Counter(v.get('mechanism') for v in nf).most_common(6)}")

if __name__ == "__main__":
    main()
