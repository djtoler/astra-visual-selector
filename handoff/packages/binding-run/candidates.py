"""Candidate builder. Pool = approved-list.json (authoritative), multi-axis capacity, 33% tolerance."""
import json, re, math
S="/Users/dwaynetoler/Documents/ChatGPT/Polish/ae-template-automation/scene-library"
TOL=1/3.0   # 6 -> 4..8

def bounds(n):
    d=max(1, round(n*TOL))
    return n-d, n+d

def axes(rec):
    """Every capacity axis a record declares, not the first key found."""
    out={}
    cap=rec.get("capacity") or {}
    for k,v in (cap.get("semantic_counts") or {}).items():
        if isinstance(v,(int,float)): out[k]=int(v)
        elif isinstance(v,list) and v and all(isinstance(x,(int,float)) for x in v):
            out[k+"[n]"]=len(v); out[k+"[sum]"]=int(sum(v))
    cr=cap.get("csv_rows") or {}
    if isinstance(cr.get("exact"),int): out["csv_rows"]=cr["exact"]
    fa=(rec.get("selectionContract") or {}).get("focalAssetCount")
    if isinstance(fa,int): out["focalAssetCount"]=fa
    return out

APPROVED = S + "/approved/approved-list.json"
# Templates whose use is restricted to one content class. Hard filter, applied before
# job matching. See grammar/SCOPE.md.
SCOPED = {
 "archive3-grunge-lyric-video-template": "lyrics",
 "archive3-horizontal-music-players-with-lyric-vol-2": "lyrics",
 "archive3-search-bar-business-timeline-2026-09-12-21-38-59-utc": "timelines",
}

def approved_ids():
    """Every scene and template id in the authoritative approved list."""
    ids=set()
    for c in json.load(open(APPROVED))["items"]:
        if c.get("templateId"): ids.add(c["templateId"])
        for sc in (c.get("scenes") or []): ids.add(sc["id"])
    return ids

def scope_of(rec_id, template_id=None):
    """Return the content class this record is restricted to, or None."""
    for t, cls in SCOPED.items():
        if rec_id == t or rec_id.startswith(t) or template_id == t:
            return cls
    return None

def load(content_class=None):
    """Pool from approved-list.json (authoritative), enriched with description-inventory
    and the catalog's structured fields. content_class admits scoped templates."""
    inv={e["id"]:e for e in json.load(open(S+"/description-inventory.json"))["entries"]}
    cat=json.load(open(S+"/approved/catalog.json"))
    detail={}
    for t in cat["afterEffects"]:
        for sc in (t.get("scenes") or []):
            detail[sc["id"]]=dict(sc, _template=t.get("templateId"), _kind="after_effects")
    for r in cat["infographics"]:
        detail[r["template_id"]]=dict(r,_template=r.get("number"),_kind="infographic")
    for r in cat["cinematic3d"]:
        detail[r.get("layout_id")]=dict(r,_template=r.get("number"),_kind="cinematic_3d")

    recs=[]
    for card in json.load(open(APPROVED))["items"]:
        tid=card.get("templateId")
        kind=card.get("type")
        if kind == "asset_retrieval":
            continue
        scenes = card.get("scenes") or [{"id": tid, "title": card.get("title")}]
        for sc in scenes:
            rid=sc.get("id") or tid
            if scope_of(rid, tid) not in (None, content_class):
                continue
            e=inv.get(rid, {})
            d=detail.get(rid, {})
            def pick(*cands):
                """Return (value, which source supplied it)."""
                for src, v in cands:
                    if v not in (None, "", [], {}): return v, src
                return None, None
            desc, desc_src = pick(("approved-list", sc.get("description")),
                                  ("inventory",     e.get("description")),
                                  ("catalog",       d.get("description")),
                                  ("title-fallback", sc.get("title")))
            avoid, avoid_src = pick(("approved-list", sc.get("avoidWhen")),
                                    ("catalog-contract", (d.get("selectionContract") or {}).get("avoidWhen")),
                                    ("catalog", d.get("avoid_when")))
            recs.append(dict(
                id=rid, template=tid, kind=kind,
                scope=scope_of(rid, tid),
                isNew=bool(card.get("isNew")),
                description=desc,
                title=sc.get("title"),
                sources={"description": desc_src, "avoid": avoid_src},
                useWhen=sc.get("useWhen"),
                axes=axes(d),
                clip=(e.get("clip") or (e.get("evidence") or {}).get("clip") or sc.get("sourcePath")),
                narration=(d.get("selectionContract") or {}).get("appropriateNarration") or d.get("intents") or [],
                avoid=avoid or [],
                caveats=d.get("caveats") or [],
                encoding=d.get("visual_encoding") or d.get("function")))
    return recs

def shape(recs, n):
    lo,hi=bounds(n); out=[]
    for r in recs:
        hits=[(k,v) for k,v in r["axes"].items() if lo<=v<=hi]
        if hits:
            exact=any(v==n for _,v in hits)
            out.append((r,"exact" if exact else "within", hits))
        elif not r["axes"]:
            out.append((r,"unknown",[]))          # missing capacity never disqualifies
        else:
            out.append((r,"outside", sorted(r["axes"].items(), key=lambda kv:abs(kv[1]-n))[:2]))
    return out
