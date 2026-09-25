#!/usr/bin/env python3
"""Deterministic media candidate lookup. The media half of candidates.py.

WHAT THIS IS. A slot in a chosen template needs an asset. This resolves a BRIEF —
entities, role, and shape — into ranked candidates from the user's Media Library.
No model call. Same contract as the template side: never rejects on missing data,
ranks instead of excluding, and a beat with no candidates is a FINDING rather than
an error.

THE LIBRARY IS READ-ONLY. It is the user's canonical store: content-addressed,
immutable, with its own provenance. This opens sqlite with mode=ro and never
writes, moves or copies a file. Corrections live in a sidecar in this tree.

MATCHING. User ruling 2026-09-22: "lets just use a search thats case insensitive
and goes by contains instead of exact match. we'll get some contamination but
thats a tradeoff for now." So matching normalises both sides — lowercase, strip
every non-alphanumeric — and asks whether the entity is a SUBSTRING of a tag,
person label or caption.

That single rule dissolves three problems at once:
  * spelling drift   "Jay-Z" / "jay z" / "jayz" all normalise to jayz
  * case             Drake(7) and drake(97) were two tags, now one entity
  * the group tag    "kendrick-drake" contains both "kendrick" and "drake", so a
                     group brief matches it without parsing the hyphen at all,
                     and "Jay-Z" never has to be protected from being split
It also produces contamination, which is the accepted cost: "jay" matches
"jayrock". That is what the W correction is for.

THE CASCADE. User: "if a still of Future, Rico Wade, and Ludacris is needed, we
search for it in the group format... if empty, get them individually and find or
select a template that can hold them." So `resolve()` returns a GROUP tier and an
INDIVIDUAL tier, and the caller learns how many slots it actually needs from
which tier came back.

    python3 pipeline/media_candidates.py Future "Rico Wade" Ludacris
    python3 pipeline/media_candidates.py --role subject --cutout drake
"""
import json, pathlib, re, sqlite3, sys

P = pathlib.Path(__file__).resolve().parent
LIB = pathlib.Path("/Users/dwaynetoler/Media Library")
DB = LIB / "METADATA" / "media-library.sqlite3"
# Corrections live HERE, never in the user's library. Their ingest stays
# authoritative; our judgments stay ours. Same split as local-templates.json
# against approved-list.json.
WRONG = P.parent / "grammar" / "media-corrections.json"
PICKS = P.parent / "grammar" / "media-picks.json"

# Framing tags the library already carries, mapped onto media_rules' vocabulary
# so framing_matches() can be handed a value it understands.
# Tightest to widest. `quarter` is head-and-chest and sits BETWEEN headshot and
# half; it was previously mapped to three_quarter, the opposite end of the scale,
# so 8 tight crops were offered to slots wanting a wide shot and vice versa.
FRAMING_SCALE = ("headshot", "quarter", "half", "three_quarter", "full")
# The library tags the same framing under several names — '3quarter' on 9 assets
# and 'Three Quarter' on 5 are one thing. One canonical value per framing.
FRAMING_TAGS = {
    "headshot": "headshot", "head shot": "headshot", "closeup": "headshot",
    "close up": "headshot",
    "quarter": "quarter", "quarter body": "quarter",
    "half": "half", "half body": "half", "upper body": "half",
    "upperbody": "half", "waist": "half",
    "3quarter": "three_quarter", "three quarter": "three_quarter",
    "3/4": "three_quarter", "three-quarter": "three_quarter",
    "3 quarter": "three_quarter",
    "full": "full", "full body": "full", "fullbody": "full",
}
FRAMING_RULES = P.parent / "grammar" / "framing-rules.json"
KIND_RULES = P.parent / "grammar" / "media-kind-rules.json"
# "This is the authoritative lifecycle-approved Media Library delivery." Its
# README says so and its manifest verifies every category's asset ids against
# its files. A manifest that states identity and kind, and checks its own
# claims, outranks anything this side derives. LOG 0099.
DELIVERY = pathlib.Path("/Users/dwaynetoler/Media Library/50_COMPLETED/"
                        "Production Ready/manifest.json")

# The delivery's folder names ARE the media kinds, one mapping, no inference.
CATEGORY_KIND = {
    "Album - Single Covers": "artwork",
    "Articles": "document",
    "Social Posts": "document",
    "Lyrics": "document",
    "Videos": "footage",
    "Cutouts": "person",
    "Glow Cutouts": "person",
    "Full Images": "person",
}

# By Person folders carry informal and misspelled names. Resolved against the
# roster, longest first, so `Nipsey` finds `Nipsey Hussle` and never the reverse.
IDENTITY_ALIASES = {
    "macklamore": "Macklemore",      # misspelled in the delivery
    "nipsey": "Nipsey Hussle",
    "pusha": "Pusha T",
    "busta": "Busta Rhymes",
    "freddie": "Freddie Gibbs",
    "snoop": "Snoop Dogg",
}
NOT_AN_IDENTITY = {"_unidentified", "_no_faces", "_catalog"}

MEDIA_KINDS = ("person", "footage", "document", "artwork", "graphic")
# Tag phrases that say what a thing IS. Ordered by strength: a face beats any of
# these, because an article ABOUT someone is still an article while a portrait
# filed under a project named "...article" is still a portrait.
KIND_TAGS = (("document", ("article or post", "ocr extracted", "screenshot")),
             ("artwork", ("artwork", "album cover", "cover art")),
             ("person", ("person photo", "group photo", "group")))


def validate_delivery_manifest(d):
    """Return a verified delivery manifest or fail closed."""
    v = d.get("verification") or {}
    categories = set((d.get("categories") or {}).keys())
    checks = v.get("category_checks") or {}
    failures = []
    if set(checks) != categories:
        failures.append("category verification set differs from delivery categories")
    for cat in sorted(categories):
        c = checks.get(cat) or {}
        if not c.get("passed") or not c.get("asset_ids_match"):
            failures.append(f"{cat} failed its delivery verification")
    for key in ("cutout_glow_sets_match", "person_view_covers_cutouts",
                "protected_catalog_counts_unchanged", "source_media_unchanged"):
        if v.get(key) is not True:
            failures.append(key)
    if v.get("sqlite_integrity") != "ok":
        failures.append("sqlite_integrity")
    if failures:
        raise ValueError("unverified Production Ready delivery: " + "; ".join(failures))
    return d


def resolve_identity(folder):
    """A By Person folder name -> a roster name, or None.

    The delivery's folders are what a human typed: `Nipsey`, `Pusha`,
    `macklamore`. An alias map handles those; everything else matches the roster
    by normalised prefix, longest candidate first, so a short folder cannot grab
    a long name it does not mean.
    """
    if not folder or folder in NOT_AN_IDENTITY: return None
    key = folder.strip().lower()
    if key in IDENTITY_ALIASES: return IDENTITY_ALIASES[key]
    try:
        import entities as E
        names, _ = E.roster()
    except Exception:
        return folder.strip() or None
    n = norm(folder)
    exact = [x for x in names if norm(x) == n]
    if exact: return exact[0]
    pref = sorted([x for x in names if norm(x).startswith(n)], key=len)
    return pref[0] if pref else (folder.strip() or None)


_DEL = None
def delivery():
    """{asset_id: {kind, identities, category, tags}} from the delivery, or {}."""
    global _DEL
    if _DEL is not None: return _DEL
    _DEL = {}
    if not DELIVERY.exists(): return _DEL
    d = validate_delivery_manifest(json.load(open(DELIVERY)))
    for cat, items in (d.get("categories") or {}).items():
        for it in items:
            aid = it.get("asset_id")
            if not aid: continue
            e = _DEL.setdefault(aid, {"identities": [], "categories": [], "tags": []})
            e["categories"].append(cat)
            # Cutouts and Glow Cutouts are paired sets over the same asset, so a
            # category list is right and a single value would silently drop one.
            e["kind"] = CATEGORY_KIND.get(cat, e.get("kind"))
            if it.get("delivery_path"):
                # Cutout and glow are two approved views of the same asset. The
                # ordinary cutout is the placement default; glow remains an
                # explicitly addressable delivery category, never an accidental
                # replacement caused by JSON object order.
                if "path" not in e or cat == "Cutouts":
                    e["path"] = it["delivery_path"]
    for pv in (d.get("person_view") or []):
        aid = pv.get("asset_id")
        if not aid: continue
        e = _DEL.setdefault(aid, {"identities": [], "categories": [], "tags": []})
        for f in (pv.get("folders") or []):
            who = resolve_identity(f)
            if who and who not in e["identities"]: e["identities"].append(who)
    for aid, tags in (d.get("tags") or {}).items():
        e = _DEL.setdefault(aid, {"identities": [], "categories": [], "tags": []})
        e["tags"] = tags
    return _DEL


def kind_of(rec, delivered=None):
    """What this asset IS, deterministically, or None when nothing says.

    A DETECTED face counts even when unnamed — 131 assets have a face nobody has
    labelled, and they are photographs of people whatever we call them.
    """
    # A DELIVERED kind wins outright. An Article with a face in it is a
    # document; inference called it a person.
    if delivered: return delivered
    if rec.get("media_type") == "video":
        return "footage"
    if rec.get("people") or (rec.get("faces") or 0) > 0:
        return "person"
    tags = {str(t.get("tag", "")).lower() for t in (rec.get("tags") or [])}
    for kind, phrases in KIND_TAGS:
        for p in phrases:
            if any(p in t for t in tags):
                return kind
    return None


_KR = None
def kind_wanted(template_id, kind=None):
    """What KIND of media this template's slots take, or () for no preference."""
    global _KR
    import os
    if _KR is None:
        _KR = json.load(open(KIND_RULES)) if os.path.exists(KIND_RULES) else {}
    byid = _KR.get("byId") or {}
    if template_id in byid: return tuple(byid[template_id]["wants"])
    rule = (_KR.get("byKind") or {}).get(kind or "")
    return tuple(rule["wants"]) if rule else ()


def framing_of(tag):
    """One canonical framing from whatever the library called it. None if the
    tag says something else — 'Group' and 'Person Photo' are subject COUNT."""
    return FRAMING_TAGS.get(str(tag or "").strip().lower())


_FR = None
def framing_wanted(template_id, kind=None):
    """What framing this template's media slots want, or () for no preference.

    Declared in grammar/framing-rules.json with the user's words, because
    NOTHING in the capability measurement says how close a slot crops. Inferring
    it would put full-body shots on marker nodes forever.
    """
    global _FR
    import os
    if _FR is None:
        _FR = json.load(open(FRAMING_RULES)) if os.path.exists(FRAMING_RULES) else {}
    byid = _FR.get("byId") or {}
    if template_id in byid: return tuple(byid[template_id]["wants"])
    if kind is None:
        # NO SILENT FALLBACK. The first version wrapped this in a bare except and
        # `match-trial` was not on sys.path when the builder ran, so kind came
        # back None for every template and the whole feature did nothing while
        # reporting success. A caller that knows the kind must pass it.
        import os
        mt = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "match-trial")
        if mt not in sys.path: sys.path.insert(0, mt)
        import candidates as C
        kind = next((r.get("kind") for r in C.load(content_class="*")
                     if r["id"] == template_id), None)
        if kind is None:
            raise KeyError(f"framing_wanted: {template_id!r} is not in the pool; "
                           f"pass kind= explicitly if it is a local record")
    rule = (_FR.get("byKind") or {}).get(kind or "")
    return tuple(rule["wants"]) if rule else ()
GROUP_TAGS = {"group", "group photo"}
# `ingest` tags are PROJECT and collection labels — "Drake Year 17 - Instagram"
# sits on 118 assets including photos of other people entirely. They are matched
# but ranked last and labelled, never dropped: 10 of the 20 assets tagged
# "Drake and Jay-Z together collection" carry no other tag naming both, so
# excluding the source would delete real signal to remove noise. LOG 0087.
PROJECT_SOURCES = {"ingest"}


def norm(s):
    """lowercase, alphanumerics only. The whole matching rule lives here."""
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def _db():
    if not DB.exists():
        raise FileNotFoundError(f"media library catalog not found: {DB}")
    return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)


def corrections():
    """(asset_id, normalised entity) pairs the user has marked WRONG.

    User 2026-09-22: "w means wrong person or entity, do the self correction."
    A W is entity-scoped, not beat-scoped: if contains-matching `jay` surfaced a
    Jay Rock photo under a Jay-Z brief, it is wrong for EVERY Jay-Z brief. Beat-
    scoped would make the user re-reject the same contamination on every beat,
    which is the loose match staying expensive forever instead of getting cheaper.
    """
    if not WRONG.exists():
        return set()
    d = json.load(open(WRONG))
    return {(w["assetId"], norm(w["entity"])) for w in (d.get("wrong") or [])}


def picked():
    """{brief::tier -> [assetId]} from the ingested review. ONE reader.

    The file grew a per-tier shape when the review started recording rejections
    and noneAcceptable alongside selections; two places were reading the old flat
    `picks` map and one of them failed silently. Shape belongs in one function.
    """
    import os
    if not os.path.exists(PICKS): return {}
    d = json.load(open(PICKS))
    if "picks" in d:                       # pre-2026-09-22 flat form
        return dict(d["picks"])
    out = {}
    for brief, b in (d.get("briefs") or {}).items():
        for tier, t in (b.get("tiers") or {}).items():
            if t.get("selected"): out[f"{brief}::{tier}"] = list(t["selected"])
    return out


def load():
    """Every lifecycle-approved delivered asset a brief can match against.

    Production Ready is the consumer boundary, not enrichment over the historical
    catalog. Rows outside its verified manifest may remain useful provenance, but
    they are not selectable production media.
    """
    dl = delivery()
    if not dl:
        raise FileNotFoundError(f"authoritative media delivery is missing: {DELIVERY}")
    db = _db()
    rows = {}
    for aid, mt, ext, w, h, dur, path in db.execute(
            "select asset_id, media_type, extension, width, height, duration, "
            "canonical_path from assets"):
        if aid not in dl:
            continue
        rows[aid] = {"id": aid, "media_type": mt, "ext": ext, "width": w,
                     "height": h, "duration": dur, "path": path,
                     "tags": [], "people": [], "captions": [], "derivatives": [],
                     "faces": 0}
    for aid, tag, src in db.execute("select asset_id, tag, source from tags"):
        if aid in rows: rows[aid]["tags"].append({"tag": tag, "source": src})
    for aid, name in db.execute(
            "select asset_id, identity_name from faces "
            "where identity_name is not null and identity_name <> ''"):
        if aid in rows and name not in rows[aid]["people"]:
            rows[aid]["people"].append(name)
    # A DETECTED face, named or not. 131 assets have one nobody has labelled;
    # they are photographs of people either way.
    for aid, n in db.execute("select asset_id, count(*) from faces group by 1"):
        if aid in rows: rows[aid]["faces"] = n
    for aid, dt, dp in db.execute(
            "select asset_id, derivative_type, path from derivatives"):
        if aid in rows: rows[aid]["derivatives"].append({"type": dt, "path": dp})
    # captions ride in assets.jsonl, not the sqlite catalog
    jl = LIB / "METADATA" / "assets.jsonl"
    if jl.exists():
        for line in open(jl):
            try: r = json.loads(line)
            except json.JSONDecodeError: continue
            aid, et = r.get("asset_id"), r.get("embedding_text") or ""
            if aid in rows and "Captions:" in et:
                cap = et.split("Captions:", 1)[1].strip()
                if cap: rows[aid]["captions"].append(cap)
    for aid, e in dl.items():
        r = rows.get(aid)
        if not r:
            raise RuntimeError(f"delivered asset is absent from the catalog: {aid}")
        r["delivered_identities"] = list(e.get("identities") or [])
        r["delivered_kind"] = e.get("kind")
        r["delivered_categories"] = list(e.get("categories") or [])
        for t in (e.get("tags") or []):
            if t not in r["tags"]: r["tags"].append(t)
        if e.get("path"): r["delivered_path"] = e["path"]
    for r in rows.values():
        r["_hay"] = norm(" ".join(
            [t["tag"] for t in r["tags"]] + r["people"] + r["captions"]
            + (r.get("delivered_identities") or [])))
        r["framing"] = next((framing_of(t["tag"]) for t in r["tags"]
                             if framing_of(t["tag"])), None)
        r["is_group"] = any(t["tag"].lower() in GROUP_TAGS for t in r["tags"])
        r["has_cutout"] = "Cutouts" in (r.get("delivered_categories") or [])
        r["kind"] = kind_of(r, r.get("delivered_kind"))
        r["display"] = display_path(r)
    return rows


# What to SHOW, best first. The raw import is the identity and the provenance;
# it is not what gets placed. `kept-original` is the exception and it is the
# user's own decision — they ticked "Keep original, do not run this image through
# the processing pipeline" in the sourcing gallery, and substituting a derivative
# would override a choice they already made.
DISPLAY_ORDER = ("cutout", "glow-cutout", "preview")


def display_path(rec):
    """The processed file, where one exists. LOG 0093.

    The review showed assets.canonical_path — raw 10_ORIGINALS imports — while
    347 cutouts, 201 previews and 146 glow-cutouts sat unused. 90 of the 165
    cards on screen had a cutout that was never shown, and the user said so:
    "you're pulling from somwehere that has the pre-processed images. these are
    even before they're been cropped."
    """
    # The lifecycle gate has already selected and hash-verified the exact bytes.
    # Registered derivatives are historical possibilities; they cannot outrank
    # the file the authoritative delivery approved.
    if rec.get("delivered_path"):
        return rec["delivered_path"]

    # A SUBSTITUTION IS ONLY VALID WITHIN THE SAME MEDIUM. A video's `preview`
    # derivative is a STILL; returning it made the builder transcode one PNG into
    # a 0.04-second mp4, and 57 of 73 clips shipped unplayable. 245 of 325 videos
    # were affected. LOG 0100.
    VID = (".mp4", ".mov", ".m4v", ".webm")
    is_video = rec.get("media_type") == "video"
    by = {}
    for d in rec.get("derivatives") or []:
        if not (isinstance(d, dict) and d.get("path")): continue
        if is_video and not str(d["path"]).lower().endswith(VID): continue
        if not is_video and str(d["path"]).lower().endswith(VID): continue
        by.setdefault(d["type"], d["path"])
    if "kept-original" in by:
        return rec["path"]
    for t in DISPLAY_ORDER:
        if t in by: return by[t]
    return rec["path"]


def matches(rec, entity, wrong=frozenset()):
    """Does this asset show this entity? Contains, normalised, minus corrections."""
    e = norm(entity)
    if not e: return False
    if (rec["id"], e) in wrong: return False
    return e in rec["_hay"]


def _why(rec, entity):
    """Which field carried the match — so a W press is informed, not blind.

    A `project:` prefix means the asset merely sits in a collection whose NAME
    contains the entity. That is the weakest evidence in the system and the user
    needs to see it as such before deciding whether to press W.
    """
    e = norm(entity)
    for t in rec["tags"]:
        if t.get("source") in PROJECT_SOURCES: continue
        if e in norm(t["tag"]): return f"tag:{t['tag']}"
    for p in rec["people"]:
        if e in norm(p): return f"face:{p}"
    for c in rec["captions"]:
        if e in norm(c):
            i = norm(c).find(e)
            return f"caption:…{c[max(0, i - 24):i + len(entity) + 24]}…"
    for t in rec["tags"]:
        if t.get("source") in PROJECT_SOURCES and e in norm(t["tag"]):
            return f"project:{t['tag']}"
    return "?"


def spread(recs, n, used=frozenset(), pin=frozenset()):
    """Fill n slots by ROTATING across facets, not by sorting on them.

    Sorting by a property makes the top of the list homogeneous in that property.
    Measured on the first real pass: `has_cutout` ranked second and no clip has a
    cutout, so video came back at 11% of what was shown against 25% of the
    library; framing came back full_body 71 to headshot 6; and every entity
    appearing on more than one brief got an IDENTICAL top-8.

    Same defect FAM_MAX fixed on the template side, one layer down. This takes
    the ranked list and deals round-robin across (media_type, framing) buckets,
    so the visible set mirrors what the library actually holds. `used` carries
    the assets already shown for this entity on an EARLIER brief and sends them
    to the back, which is what stops the fourth Drake brief being the first one
    again.

    `pin` is the assets the user has already PICKED here. They lead and they can
    never be rotated out: a selection is a decision and a reshuffle is not allowed
    to take it away. Adding this function without pinning dropped 4 of the user's
    14 picks — LOG 0031 on the media side.

    Ranks, never excludes: everything handed in comes back, only reordered.
    Deterministic — the same input gives the same order every time.
    """
    if pin:
        first = [r for r in recs if r["id"] in pin]
        rest = [r for r in recs if r["id"] not in pin]
        tail = spread(rest, None if n is None else max(0, n - len(first)), used=used)
        out = first + tail
        return out if n is None else out[:max(n, len(first))]
    buckets = {}
    for r in recs:
        key = (r.get("media_type"), r.get("framing"))
        buckets.setdefault(key, []).append(r)
    # Bucket order follows the incoming rank of each bucket's best member, so
    # strong evidence still leads; only the SPREAD across buckets is new.
    order = sorted(buckets, key=lambda k: recs.index(buckets[k][0]))
    out, seen = [], set()
    for tier in (0, 1):                       # unused first, then already-used
        while True:
            took = False
            for k in order:
                for r in buckets[k]:
                    if r["id"] in seen: continue
                    if tier == 0 and r["id"] in used: continue
                    out.append(r); seen.add(r["id"]); took = True
                    break
            if not took: break
    return out[:n] if n is not None else out


def resolve(entities, pool=None, media_type=None, cutout=None, framing=None,
            wrong=None, wants=(), kinds=()):
    """The cascade. Returns {'group': [...], 'individual': {entity: [...]}, ...}.

    GROUP first: one asset showing every named entity, so one slot serves them
    all. INDIVIDUAL second: one asset each, so the beat needs as many slots as
    there are entities. The caller uses which tier came back to decide what
    template can hold it — media availability constrains the treatment, not the
    other way round.
    """
    pool = load() if pool is None else pool
    wrong = corrections() if wrong is None else wrong
    ents = [e for e in entities if norm(e)]

    def ok(r):
        if media_type and r["media_type"] != media_type: return False
        if cutout is True and not r["has_cutout"]: return False
        if framing and r["framing"] and r["framing"] != framing: return False
        return True

    group = [r for r in pool.values()
             if ok(r) and len(ents) > 1 and all(matches(r, e, wrong) for e in ents)]
    individual = {e: [r for r in pool.values() if ok(r) and matches(r, e, wrong)]
                  for e in ents}
    # Rank: a named face beats a tag beats a caption; a cutout beats a raw still;
    # stills before video unless video was asked for. Never excludes — orders.
    STRENGTH = {"face": 0, "tag": 1, "caption": 2, "project": 4}
    def fit(r):
        """0 right framing, 1 unknown, 2 wrong. RANKS, never excludes.

        An UNTAGGED asset scores 1, not 2: 436 of 506 carry no framing tag, and
        ranking them below a known-wrong one would hide most of the library
        behind a tag nobody has applied yet. The user's own words on 28-28 —
        "quarter, headshot or no no size specified images".
        """
        if not wants: return 0
        if not r.get("framing"): return 1
        return 0 if r["framing"] in wants else 2
    def kfit(r):
        """Same shape as fit(): 0 right kind, 1 unknown, 2 wrong. 660 of 1,381
        assets carry no kind signal, so unknown sits in the middle."""
        if not kinds: return 0
        k = r.get("kind") or kind_of(r)
        if not k: return 1
        return 0 if k in kinds else 2
    def rank(r, e):
        return (kfit(r), fit(r),
                STRENGTH.get(_why(r, e).split(":", 1)[0], 3),
                0 if r["has_cutout"] else 1,
                0 if r["framing"] else 1,
                r["id"])
    # A GROUP is only as good as its WEAKEST leg. Ranking on the first entity
    # hid that the second matched nothing but a project label.
    def grank(r):
        return (kfit(r), fit(r),
                max(STRENGTH.get(_why(r, e).split(":", 1)[0], 3) for e in ents),
                0 if r["has_cutout"] else 1,
                0 if r["framing"] else 1,
                r["id"])
    group.sort(key=grank)
    for e in individual:
        individual[e].sort(key=lambda r: rank(r, e))
    return {"entities": ents, "group": group, "individual": individual,
            "slotsNeeded": 1 if group else len([e for e in ents if individual[e]]),
            # A gap is a FINDING, and it is the sourcing list. Same rule as a beat
            # with no acceptable template: it points at the library, not the user.
            "gaps": [e for e in ents if not individual[e] and not group]}


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a.split("=")[0]: (a.split("=")[1] if "=" in a else True)
             for a in argv[1:] if a.startswith("--")}
    if not args:
        print(__doc__)
        return 2
    pool = load()
    out = resolve(args, pool=pool,
                  media_type=flags.get("--type"),
                  cutout=True if flags.get("--cutout") else None,
                  framing=flags.get("--framing"))
    print(f"library: {len(pool)} assets    entities: {', '.join(out['entities'])}")
    print(f"slots needed: {out['slotsNeeded']}"
          + (f"    GAPS (nothing in the library): {', '.join(out['gaps'])}"
             if out["gaps"] else ""))
    if out["group"]:
        print(f"\nGROUP — one asset showing all {len(out['entities'])}: "
              f"{len(out['group'])} candidate(s)")
        for r in out["group"][:6]:
            print(f"   {r['id'][:12]}  {r['media_type']:5} {r['framing'] or '—':13} "
                  f"{'cutout' if r['has_cutout'] else '':7} {_why(r, out['entities'][0])[:60]}")
    else:
        print(f"\nGROUP — none. Falls to individual, so the beat needs "
              f"{out['slotsNeeded']} slot(s).")
    for e, rs in out["individual"].items():
        print(f"\n{e.upper()} — {len(rs)} candidate(s)")
        for r in rs[:6]:
            print(f"   {r['id'][:12]}  {r['media_type']:5} {r['framing'] or '—':13} "
                  f"{'cutout' if r['has_cutout'] else '':7} {_why(r, e)[:60]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
