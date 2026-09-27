#!/usr/bin/env python3
"""What the library is missing, named precisely enough to go and get it.

WHY. User on beat 12-12a, 2026-09-26: "missing headshot or quarter for ab soul.
system should say what it needs. spatial only take headshots and quarters. system
should say need absoul headshot." The gap list said `Ab-Soul` and stopped there —
which entity, never which FRAMING, and never why. "We need a picture of Ab-Soul"
is not actionable; "we need an Ab-Soul headshot or quarter, because beat 12-12a
renders on a spatial scene and a node cannot hold a full-body shot" is.

THREE SHAPES OF NEED, and they are different jobs:
  ABSENT      the entity has no asset at all. Sourcing.
  WRONG SIZE  assets exist and none matches what the beat's template can hold.
              Sourcing, at a stated framing.
  UNTAGGED    assets exist, framing unknown, so nothing can be ranked. TAGGING,
              not sourcing — and cheaper, because the file is already here.

    python3 pipeline/needs.py              the report
    python3 pipeline/needs.py --write      also grammar/needs.json
    python3 pipeline/needs.py --csv        one line per need
"""
import collections, json, pathlib, sys

P = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P))
sys.path.insert(0, str(P.parent / "match-trial"))
import candidates as C
import media_candidates as M

OUT = P.parent / "grammar" / "needs.json"
BRIEFS = P.parent / "grammar" / "media-briefs.json"
BE = P.parent / "grammar" / "beat-entities.json"
FLAGS = P.parent / "grammar" / "beat-flags.json"


def main(argv):
    pool = M.load()
    wrong = M.corrections()
    briefs = json.load(open(BRIEFS))["briefs"]
    be = json.load(open(BE)) if BE.exists() else {}
    extra, subj = be.get("beats") or {}, (be.get("_subject") or {}).get("entity")
    flags = (json.load(open(FLAGS)).get("beats") or {}) if FLAGS.exists() else {}
    tpool = {r["id"]: r for r in C.load(content_class="*")}

    needs = []
    for b in briefs:
        name = b["brief"]
        ents = set(b["entities"]) | set((extra.get(name) or {}).get("entities") or [])
        if subj: ents.add(subj)
        tids = [t["id"] for t in (b.get("selectedTemplates") or [])]
        wants = sorted({f for t in (b.get("selectedTemplates") or [])
                        for f in M.framing_wanted(t["id"], t.get("kind"))})
        decl = (flags.get(name) or {}).get("wantsMediaKind") or []
        kinds = list(decl) or sorted({k for t in (b.get("selectedTemplates") or [])
                                      for k in M.kind_wanted(t["id"], t.get("kind"))})
        # which chosen template forces the framing — the reason, not just the rule
        because = [t for t in tids
                   if set(M.framing_wanted(t, (tpool.get(t) or {}).get("kind"))) & set(wants)]
        for e in sorted(ents):
            got = M.resolve([e], pool=pool, wrong=wrong)["individual"].get(e, [])
            if not got:
                needs.append({"beat": name, "entity": e, "need": "ABSENT",
                              "wantFraming": wants, "wantKind": kinds,
                              "have": 0, "because": because,
                              "say": f"{e}: no asset at all. Source any image of them"
                                     + (f"; this beat needs {' or '.join(wants)}"
                                        if wants else "")})
                continue
            if not wants:
                continue
            fits = [c for c in got if M.framing_matches(c.get("framing"), wants) is True]
            unknown = [c for c in got if c.get("framing") is None]
            if fits:
                continue
            if unknown:
                needs.append({"beat": name, "entity": e, "need": "UNTAGGED",
                              "wantFraming": wants, "wantKind": kinds,
                              "have": len(got), "unknown": len(unknown),
                              "because": because,
                              "say": f"{e}: {len(unknown)} asset(s) exist with no "
                                     f"framing tag. TAG them — this beat needs "
                                     f"{' or '.join(wants)} and nothing can be "
                                     f"ranked until one says so"})
            else:
                have = sorted({c.get("framing") for c in got if c.get("framing")})
                needs.append({"beat": name, "entity": e, "need": "WRONG SIZE",
                              "wantFraming": wants, "wantKind": kinds,
                              "have": len(got), "haveFraming": have,
                              "because": because,
                              "say": f"{e}: {len(got)} asset(s), all {'/'.join(have)}. "
                                     f"Source a {' or '.join(wants)} — this beat "
                                     f"renders on {because[0] if because else 'its template'}"})
    if "--csv" in argv:
        for n in needs:
            print(f"{n['beat']},{n['entity']},{n['need']},"
                  f"{'|'.join(n['wantFraming'])},{n['have']}")
        return 0
    by = collections.Counter(n["need"] for n in needs)
    print(f"   {len(needs)} needs across {len({n['beat'] for n in needs})} beats: "
          + ", ".join(f"{k} {v}" for k, v in by.most_common()))
    # GROUPED BY ENTITY, NOT BY BEAT. The first version printed per beat and
    # deduped the entity, which hid that Ab-Soul blocks TWO beats and showed him
    # under only one — losing the single most useful thing here, which is how much
    # each missing asset costs. One tagging job can unblock several beats.
    ent = {}
    for n in needs:
        e = ent.setdefault((n["need"], n["entity"]),
                           {"beats": [], "want": set(), "have": n["have"],
                            "n": n.get("unknown", 0), "haveFraming": n.get("haveFraming")})
        e["beats"].append(n["beat"])
        e["want"] |= set(n["wantFraming"])
    for need, title in (("ABSENT", "nothing exists — source it"),
                        ("WRONG SIZE", "assets exist, none fits what the beat renders on"),
                        ("UNTAGGED", "the file is already here — this is TAGGING, "
                                     "not sourcing, and it is the cheap fix")):
        rows = sorted(((k[1], v) for k, v in ent.items() if k[0] == need),
                      key=lambda x: (-len(x[1]["beats"]), x[0]))
        if not rows: continue
        print(f"\n   {need} — {title}")
        for who, v in rows:
            beats = ", ".join(sorted(set(v["beats"])))
            w = " or ".join(sorted(v["want"])) or "any framing"
            extra = (f"{v['n']} untagged of {v['have']}" if need == "UNTAGGED"
                     else f"{v['have']} asset(s), all {'/'.join(v['haveFraming'] or [])}"
                     if need == "WRONG SIZE" else "none at all")
            print(f"     {who:16} blocks {len(set(v['beats']))} beat(s): {beats}")
            print(f"     {'':16} needs {w}  ({extra})")
    if "--write" in argv:
        OUT.write_text(json.dumps(
            {"_note": "What the library is missing, per beat per entity, with the "
                      "framing the beat's own template forces and the reason. "
                      "ABSENT and WRONG SIZE are sourcing; UNTAGGED is tagging and "
                      "is cheaper, because the file is already on disk.",
             "_generatedBy": "pipeline/needs.py",
             "_counts": dict(by), "needs": needs}, indent=1, ensure_ascii=False))
        print(f"\n   wrote {OUT.relative_to(P.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
