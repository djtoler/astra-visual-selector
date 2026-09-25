#!/usr/bin/env python3
"""Measure a review pass, or the current slates, and append to grammar/metrics.json.

Two kinds of entry, because they answer different questions:

  REVIEW  a human judged these slates. Gives the real numbers — beats served,
          acceptance — and can only be produced by someone doing a pass.
  SLATE   what the system currently offers. No acceptance rate, because nobody has
          judged it. Tracks slate-side change BETWEEN reviews so a regression is
          visible before the next pass rather than after it.

Every entry records the system state it was measured against — prompt shas, binding
count, capability coverage — because a metric with no attribution cannot explain its
own movement.

Reads only files in this tree, so it works when the scene library is unreachable.

    python3 pipeline/metrics.py                       show the series
    python3 pipeline/metrics.py slate  <label>        record what the slates offer now
    python3 pipeline/metrics.py review <label>        record a judged pass
    python3 pipeline/metrics.py ... --write
"""
import collections, datetime, hashlib, json, pathlib, sys
P    = pathlib.Path(__file__).resolve().parent
G    = P.parent / "grammar"
OUT  = G / "metrics.json"

def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12] if p.exists() else None

def state():
    """What the system was when this was measured. Without it a number cannot be read."""
    b = json.load(open(G / "bindings.json"))
    cap = json.load(open(G / "capability.json")) if (G / "capability.json").exists() else {}
    prov = collections.Counter(r["provenance"].get("promptSha")
                               for rows in b.values() for r in rows
                               if r["provenance"].get("source") != "user")
    return {
        "bindPromptSha": _sha(P.parent / "prompts" / "PROMPT-bind.md"),
        "clipPromptSha": _sha(P.parent / "prompts" / "PROMPT-describe-clip.md"),
        "bindings": sum(len(v) for v in b.values()),
        "bindingsByPromptSha": dict(prov),
        "userNamedBindings": sum(1 for rows in b.values() for r in rows
                                 if r["provenance"].get("source") == "user"),
        "capabilityRecords": len(cap),
    }

def slate_metrics(shotfile):
    raw = json.load(open(P / shotfile))
    shots = raw["shots"] if isinstance(raw, dict) else raw
    n = len(shots)
    opts = [len(s["options"]) for s in shots]
    return {
        "beats": n,
        "optionSlots": sum(opts),
        "meanOptionsPerBeat": round(sum(opts) / n, 2),
        "beatsWithNoOptions": sum(1 for o in opts if o == 0),
        "beatsFlaggedCapacityImpossible":
            sum(1 for s in shots if s.get("floodNote") and "CAPACITY IMPOSSIBLE" in s["floodNote"]),
        "beatsRoutedSpatial": sum(1 for s in shots if s.get("spatialRoute")),
        "shotlist": shotfile,
    }

def review_metrics():
    b = json.load(open(G / "picks.json"))["beats"]
    sel = sum(len(x["selected"]) for x in b.values())
    rej = sum(len(x["rejected"]) for x in b.values())
    served = [k for k, x in b.items() if x["selected"]]
    byjob = collections.defaultdict(lambda: [0, 0, 0, 0])
    for x in b.values():
        j = byjob[x["job"]]
        j[0] += len(x["selected"]); j[1] += len(x["shown"])
        j[2] += 1; j[3] += 1 if x["selected"] else 0
    return {
        # the objective: did we land a usable candidate on the beat
        "beatsServed": len(served),
        "beatsServedPct": round(len(served) * 100 / len(b), 1),
        "beatsNoneAcceptable": sum(1 for x in b.values() if x["noneAcceptable"]),
        # the counter-metric: how much of the reviewer's time was wasted.
        # a wider slate raises beatsServed and lowers this. Watch both or neither.
        "accepted": sel, "rejected": rej,
        "acceptancePct": round(sel * 100 / max(sel + rej, 1), 1),
        "picksPerServedBeat": round(sel / max(len(served), 1), 2),
        "flaggedRawBroll": sum(1 for x in b.values() if x["rawBroll"]),
        "flaggedNeedsText": sum(1 for x in b.values() if x.get("needsTextTemplate")),
        "byJob": {j: {"served": f"{v[3]}/{v[2]}", "accepted": f"{v[0]}/{v[1]}",
                      "acceptancePct": round(v[0] * 100 / max(v[1], 1), 1)}
                  for j, v in sorted(byjob.items())},
    }

def show(series):
    if not series: print("no entries yet"); return
    print(f"{'date':11s} {'kind':6s} {'label':26s} {'served':>7s} {'accept':>7s} {'slots':>6s}  bindings")
    for e in series:
        m = e["metrics"]
        sv = f"{m.get('beatsServedPct','—')}%" if "beatsServedPct" in m else "—"
        ac = f"{m.get('acceptancePct','—')}%" if "acceptancePct" in m else "—"
        print(f"{e['date'][:10]:11s} {e['kind']:6s} {e['label'][:25]:26s} {sv:>7s} {ac:>7s} "
              f"{m.get('optionSlots','—'):>6}  {e['state']['bindings']}")
    if len(series) > 1:
        a, b = series[-2]["metrics"], series[-1]["metrics"]
        print("\nagainst the previous entry:")
        for k in ("beatsServedPct", "acceptancePct", "optionSlots", "meanOptionsPerBeat"):
            if k in a and k in b and a[k] != b[k]:
                d = round(b[k] - a[k], 2)
                print(f"   {k:22s} {a[k]} -> {b[k]}   {'+' if d > 0 else ''}{d}")

def main(argv):
    series = json.load(open(OUT)) if OUT.exists() else []
    if len(argv) < 2:
        show(series); return 0
    kind = argv[1]
    if kind not in ("slate", "review"): print(__doc__); return 2
    label = argv[2] if len(argv) > 2 and not argv[2].startswith("--") else "unlabelled"
    # A REVIEW entry measures the slate that was JUDGED, not the one that exists now.
    # Mixing them makes a metric that cannot be read: 259 slots offered today against
    # an acceptance rate earned on 226.
    if kind == "review":
        m = slate_metrics("ui3-capacity/data.json")
        m.update(review_metrics())
    else:
        m = slate_metrics("shotlist.capacity.json" if (P / "shotlist.capacity.json").exists()
                          else "shotlist.json")
    entry = {"date": datetime.datetime.now().isoformat(timespec="seconds"),
             "kind": kind, "label": label, "state": state(), "metrics": m}
    print(json.dumps(entry["metrics"], indent=1)[:900])
    if "--write" not in argv:
        print("\nnot written. Re-run with --write to append.")
        return 0
    series.append(entry)
    OUT.write_text(json.dumps(series, indent=1))
    print(f"\nappended; {len(series)} entr{'y' if len(series)==1 else 'ies'} in {OUT.name}")
    show(series)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
