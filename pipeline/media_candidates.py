#!/usr/bin/env python3
"""Deterministic media candidate lookup. The media half of candidates.py.

WHAT THIS IS. A slot in a chosen template needs an asset. This resolves a BRIEF —
entities, role, and shape — into ranked candidates from the user's Media Library.
No model call. Same contract as the template side: explicit evidence gates first,
rank within the eligible pool, and a beat with no candidates is a FINDING rather
than an error.

THE LIBRARY IS READ-ONLY. It is the user's canonical store: content-addressed,
immutable, with its own provenance. This opens sqlite with mode=ro and never
writes, moves or copies a file. Corrections live in a sidecar in this tree.

MATCHING. User ruling 2026-09-22: "lets just use a search thats case insensitive
and goes by contains instead of exact match. we'll get some contamination but
thats a tradeoff for now." So matching normalises both sides — lowercase, strip
every non-alphanumeric — and asks whether the entity is a SUBSTRING of a tag,
person label or caption. Identity evidence is staged: Production Ready identities,
named faces and content tags form the primary pool; captions and project labels are
used only when that entity has no primary match.

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
sys.path.insert(0, str(P))
import paths as PATHS
LIB = PATHS.library_root()
DB = LIB / "METADATA" / "media-library.sqlite3"
# Corrections live HERE, never in the user's library. Their ingest stays
# authoritative; our judgments stay ours. Same split as local-templates.json
# against approved-list.json.
WRONG = P.parent / "grammar" / "media-corrections.json"
PICKS = P.parent / "grammar" / "media-picks.json"
# Tags the USER added by name. Additive counterpart to media-corrections.json:
# the library's ingest stays authoritative, our judgments stay ours, and nothing
# is written into the Media Library from this side.
USER_TAGS = P.parent / "grammar" / "media-tags.json"
# Assets the user approved despite their lifecycle gate receipt. ADMITS only.
APPROVED = P.parent / "grammar" / "approved-overrides.json"

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
# HEADSHOT AND QUARTER ARE ONE CLASS, for now. User ruling 2026-09-26: "we shiiuld
# treat headshot and quarter as the same for now." They are adjacent on the scale —
# quarter is head-and-chest, headshot is head-and-shoulders — and the library's
# tagging does not separate them reliably enough for the distinction to carry
# weight. Declared as an equivalence rather than collapsed in FRAMING_TAGS, so the
# underlying tags stay intact and the ruling can be lifted by deleting one line.
FRAMING_EQUIV = ({"headshot", "quarter"},)


def framing_class(f):
    """The framing, or the class it belongs to. Two framings in one class are
    interchangeable wherever a template states what it wants."""
    if not f: return f
    for g in FRAMING_EQUIV:
        if f in g: return "|".join(sorted(g))
    return f


def framing_matches(f, wants):
    """Does this asset's framing satisfy what the template asks for?"""
    if not wants: return True
    if not f: return None                      # unknown — the caller ranks it middle
    w = {framing_class(x) for x in wants}
    return framing_class(f) in w


FRAMING_RULES = P.parent / "grammar" / "framing-rules.json"
KIND_RULES = P.parent / "grammar" / "media-kind-rules.json"
# "This is the authoritative lifecycle-approved Media Library delivery." Its
# README says so and its manifest verifies every category's asset ids against
# its files. A manifest that states identity and kind, and checks its own
# claims, outranks anything this side derives. LOG 0099.
DELIVERY = LIB / "50_COMPLETED" / "Production Ready" / "manifest.json"

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
    # VERIFY WHAT CAN BE VERIFIED; TRUST ONLY WHAT CANNOT.
    # The manifest regenerated 2026-09-26T05:24 dropped `cutout_glow_sets_match`
    # altogether — the flag was absent, not false — and this fell over on an
    # absence while the underlying condition was plainly true in the same file:
    # 261 Cutouts, 261 Glow Cutouts, zero on either side alone. Failing closed on a
    # missing self-report is right in principle and was wrong here, because the
    # claim is checkable from the manifest's own categories. So check it. A
    # computed answer also beats a trusted one when the two disagree.
    cats = d.get("categories") or {}
    cut = {i.get("asset_id") for i in cats.get("Cutouts", [])}
    glow = {i.get("asset_id") for i in cats.get("Glow Cutouts", [])}
    if cats.get("Cutouts") is not None and cats.get("Glow Cutouts") is not None:
        if cut != glow:
            failures.append(
                f"cutout_glow_sets_match: {len(cut - glow)} cutout-only, "
                f"{len(glow - cut)} glow-only (computed, not read)")
        elif v.get("cutout_glow_sets_match") is False:
            failures.append("cutout_glow_sets_match: the manifest says false but "
                            "the sets match — the manifest disagrees with itself")
    elif v.get("cutout_glow_sets_match") is not True:
        failures.append("cutout_glow_sets_match")
    for key in ("person_view_covers_cutouts",
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
    if DELIVERY.exists():
        raw = json.load(open(DELIVERY))
    else:
        # No library mounted. grammar/library-snapshot.json carries the delivery
        # verbatim, verification block included, so the gate below is the same
        # gate. A snapshot with no delivery is NOT a delivery of nothing — it is
        # an absent source, and load() raises on it rather than returning {}.
        snap = PATHS.snapshot() or {}
        raw = snap.get("delivery")
        if not raw: return _DEL
    d = validate_delivery_manifest(raw)
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
    # USER APPROVALS, after the verified delivery and never replacing it. An
    # approved asset carries no delivered identity, kind or category — the delivery
    # is what confers those, and this is explicitly NOT a delivery. kind_of() infers
    # from tags and faces as it does for anything else. LOG 0119.
    if APPROVED.exists():
        for a_ in (json.load(open(APPROVED)).get("approved") or []):
            aid = a_.get("assetId")
            if aid and aid not in _DEL:
                _DEL[aid] = {"identities": [], "categories": [], "tags": [],
                             "userApproved": True}
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
# sits on 118 assets including photos of other people entirely. It remains useful
# discovery evidence, but only as fallback when no delivered identity, named face
# or explicit content tag matches that entity. LOG 0104.
PROJECT_SOURCES = {"ingest"}
# A PROJECT NAME IS NOT EVIDENCE. User ruling 2026-09-25: "Drake Year 17 -
# Instagram. shouldnt be a tag. that add garbage to the canidates. i seen this
# frst hand. projects shouldnt be tags at all."
#
# Measured: 2,254 of 14,957 tag rows are an ingestion project name, and
# `Drake Year 17 - Instagram` alone put 96 assets into every Drake query through
# the normalised contains rule — a folder name, matching an artist.
#
# DERIVED, NOT DECLARED. The library already separates the two concepts: the
# ingestions table has a `project` column and media_search keeps `projects` and
# `tags` in different columns. So the set comes from ingestions.project, and a
# project created tomorrow is excluded the day it appears. A hand-written deny
# list would have gone stale on the next import — 19 of the 30 current projects
# are dated batch names.
_PROJ = None


def projects():
    """{normalised project name} — tags matching one of these carry no evidence."""
    global _PROJ
    if _PROJ is not None: return _PROJ
    if DB.exists():
        db = _db()
        _PROJ = {norm(r[0]) for r in db.execute(
            "select distinct project from ingestions "
            "where project is not null and project <> ''") if norm(r[0])}
    else:
        snap = PATHS.snapshot() or {}
        _PROJ = {norm(x) for x in (snap.get("projects") or []) if norm(x)}
    return _PROJ


def is_project_tag(tag):
    return norm(tag) in projects()


CLASS_TAGS = P.parent / "grammar" / "class-tags.json"
_CLS = None


def class_tags():
    """Lifecycle and content-class vocabulary: never about WHO is in an asset."""
    global _CLS
    if _CLS is None:
        _CLS = ({norm(t) for t in json.load(open(CLASS_TAGS))["tags"]}
                if CLASS_TAGS.exists() else set())
    return _CLS


def is_class_tag(tag):
    return norm(tag) in class_tags()


# GENEROUS MATCHING, BOTH DIRECTIONS. User 2026-09-26: "we need more generous tag
# matching, shouldnt be case sensitive and should be contains, not exact match".
# It was already case-insensitive and already contains — but only one way round,
# entity inside tag. So `jcole` never matched the tag `cole` and the 2010 XXL
# Freshman cover reached NO beat in the script (LOG 0114).
#
# The reverse direction is matched on TOKEN BOUNDARIES, not raw substrings, and
# only on tokens that name exactly one roster artist.
#   raw substring would match `rick` inside `kendricklamar` — a Rick Ross tag
#     landing on Kendrick Lamar.
#   every token, at a length floor, brings `jay` -> Jay Rock on 72 assets,
#     `lil` -> Lil Baby on 10, `big` -> Big Sean on 9. Those are exactly the 21
#     tokens entities.py already refuses to resolve because they belong to several
#     roster names, and guessing puts the wrong person on screen.
# Measured over the 25 entities in this script: +32 candidates, every one correct —
# kendrick x29, sean, cole, nicki. No length constant; the roster decides.
_UNIQ = None


def unique_roster_tokens():
    global _UNIQ
    if _UNIQ is None:
        try:
            sys.path.insert(0, str(P))
            import entities as _E
            names, _ = _E.roster()
            idx = _E._index(names)
            _UNIQ = {t for t, v in idx.items() if len(v) == 1}
        except Exception:
            _UNIQ = set()
    return _UNIQ


def _name_tokens(s):
    return {norm(w) for w in re.split(r"[\s\-\.]+", str(s or "")) if norm(w)}


def tag_names_entity(tag, entity_tokens):
    """Does this tag name the entity by one of its distinctive words?"""
    return bool({t for t in _name_tokens(tag) if t in unique_roster_tokens()}
                & entity_tokens)


# A SUPPRESSED ENTITY CLAIM STAYS SUPPRESSED, whatever route it takes back.
# The library records 39 tag_suppressions. Dropping the suppressed TAG is not
# enough: asset 54e95e16b8 has 'Jay-Z' and 'Kanye West' suppressed from
# caption-entity, and the raw caption still says both — it is a Kendrick Lamar
# birthday post that name-drops them as fellow entrepreneurs. So the tag went and
# the identical claim came straight back through caption evidence.
#
# Same class as the project ruling: an incidental mention is not evidence. Where
# the library has ruled a DERIVED extraction wrong for an asset, weak evidence for
# that entity on that asset is void.
#
# Scope: DERIVED sources only. It never touches delivered_identities or faces —
# asset 13cc794125 has 'Wiz Khalifa' suppressed from face-recognition while both
# the delivery and the faces table confirm him, and the Production Ready delivery
# is authoritative. Overriding it on a tag suppression would be the tail wagging
# the dog, and that call is the user's, not this file's.
DERIVED_SOURCES = {"caption-entity", "caption-action", "caption-location",
                   "filename-entity", "filename-auto", "filename-action",
                   "filename-location", "ocr-entity", "finder"}
_SUPPRESSED = None


def suppressed_claims():
    """{(asset_id, normalised entity)} the library has ruled wrong."""
    global _SUPPRESSED
    if _SUPPRESSED is not None: return _SUPPRESSED
    if DB.exists():
        _SUPPRESSED = {(a, norm(t)) for a, t, src in _db().execute(
            "select asset_id, tag, source from tag_suppressions")
            if src in DERIVED_SOURCES and norm(t)}
    else:
        snap = PATHS.snapshot() or {}
        _SUPPRESSED = {(a, norm(t)) for a, t in (snap.get("suppressedClaims") or [])
                       if norm(t)}
    return _SUPPRESSED


# WHAT THE BEAT IS ABOUT, not just who it names. An entity match says WHO; on
# beat 15-15 — "In 2010, XXL offered him a spot on the Freshman cover" — 127 assets
# say Drake and exactly one is the XXL cover, and it ranked 124th.
#
# The signal is LITERAL: how many words the beat's quote and the asset's tags share.
# No model, no embedding, reproducible from the two strings. Measured on that beat,
# the cover scores 3, the next best scores 1, and 111 of 127 score zero.
#
# Short and common words carry no information and would make everything score, so
# they are dropped. A trailing `s` is stripped so `freshmen`/`freshman` and
# `covers`/`cover` meet. Project names are excluded for the same reason they carry
# no evidence (LOG 0109) — a batch folder shares words with a beat by accident.
QUOTE_STOP = set(
    "the a an and or of in on at to for with his her its it he she they them that "
    "this these those was were is are be been had has have him by from as but not "
    "what when how all one two out up down over into than then so no who which "
    "while after before same each more most only just about got get had".split())


# DECLARED, because the stemmer cannot do it. `freshman` and `freshmen` are the
# same word and differ by a vowel, so stripping a trailing `s` never makes them
# meet — and that pair is the entire difference between the XXL Freshman cover and
# a standard XXL issue. English irregular plurals are a closed set; declaring the
# ones that matter is honest, where a fake stemmer would quietly mangle names.
QUOTE_SYNONYMS = {"freshmen": "freshman", "women": "woman", "men": "man",
                  "children": "child", "people": "person"}


def _qtok(text):
    out = set()
    for w in re.findall(r"[a-z0-9$]+", str(text or "").lower()):
        if len(w) > 2 and w not in QUOTE_STOP:
            w = w[:-1] if w.endswith("s") and len(w) > 4 else w
            out.add(QUOTE_SYNONYMS.get(w, w))
    return out


def quote_overlap(quote, rec, entities=()):
    """Distinct words the asset's tags share with the beat, BEYOND the entity.

    `entities` are removed from the comparison. The entity is already matched and
    already ranked by evidence strength, so counting its name again is a second
    vote for the same fact — and it inverts that ranking, letting an asset tagged
    "Wiz Khalifa" outrank one the delivery confirms IS Wiz Khalifa. Measured: it
    decided the top card on 3 of 7 changed slates purely on the name.
    """
    q = _qtok(quote)
    for e in entities or ():
        q -= _qtok(e)
    if not q:
        return 0
    t = set()
    for tag in rec.get("tags") or []:
        name = tag.get("tag")
        if is_project_tag(name):
            continue
        # FRAMING TAGS ARE NOT ABOUTNESS. Measured on the first run: 11-11a
        # ("Three percent") scored on the tag `Three Quarter`, 08-08 ("Half of it
        # is other people's songs") on `half`, 20-20 on `full`. Framing is already
        # its own axis in fit(), so counting it here is a second vote for the same
        # fact AND it collides with ordinary numbers and quantities, which is most
        # of what this script's beats are made of.
        if framing_of(name):
            continue
        t |= _qtok(name)
    return len(q & t)


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


_UTAGS = None


_UREM = None


def removed_tags():
    """{asset_id: {normalised tag}} the user says do not belong on that asset.

    The library has tag_suppressions for exactly this and it is read-only from
    here, so the same judgment lives in the sidecar. It exists because OCR reads
    everything printed on a page: all three XXL covers came back tagged both 2009
    AND 2010, and the standard 2010 issue came back tagged `freshmen` because its
    cover lines mention the class. Every one of those is true text and false
    metadata, and together they made the three covers indistinguishable.
    """
    global _UREM
    if _UREM is not None: return _UREM
    _UREM = {}
    if USER_TAGS.exists():
        for t in (json.load(open(USER_TAGS)).get("remove") or []):
            aid, tag = t.get("assetId"), t.get("tag")
            if not (aid and tag):
                raise ValueError(f"media-tags.json remove entry needs assetId and tag: {t}")
            if not t.get("words"):
                raise ValueError(
                    f"removal of {tag!r} on {aid} carries no words — a named "
                    "binding records the user's own words (CLAUDE.md, HARD RULE)")
            _UREM.setdefault(aid, set()).add(norm(tag))
    return _UREM


def user_tags():
    """{asset_id: [{tag, source, words}]} the user declared. Never inferred.

    A user tag is a NAMED BINDING under the HARD RULE, so each entry carries
    source "user" and their words. It is the fix for an asset the user picked
    whose only machine evidence was weak — a tag makes it findable on every future
    beat, where an exception would have fixed one card.
    """
    global _UTAGS
    if _UTAGS is not None: return _UTAGS
    _UTAGS = {}
    if USER_TAGS.exists():
        for t in (json.load(open(USER_TAGS)).get("tags") or []):
            aid, tag = t.get("assetId"), t.get("tag")
            if not (aid and tag):
                raise ValueError(f"media-tags.json entry needs assetId and tag: {t}")
            if not t.get("words"):
                raise ValueError(
                    f"user tag {tag!r} on {aid} carries no words — a named binding "
                    "records the user's own words (CLAUDE.md, HARD RULE)")
            _UTAGS.setdefault(aid, []).append(
                {"tag": tag, "source": "user", "words": t["words"]})
    return _UTAGS


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


# Which reader produced the rows currently loaded. NOT the same claim as
# paths.source(), which only says what exists on disk. A test asserting the
# latter passed while a hardcoded-path build read the live catalog behind it.
SOURCE = None


def _blank(aid, mt, ext, w, h, dur, path):
    return {"id": aid, "media_type": mt, "ext": ext, "width": w, "height": h,
            "duration": dur, "path": path, "tags": [], "people": [],
            "captions": [], "derivatives": [], "faces": 0}


def _rows_live(dl):
    """From the mounted sqlite catalog + assets.jsonl."""
    global SOURCE
    SOURCE = "live"
    db = _db()
    rows = {}
    for aid, mt, ext, w, h, dur, path in db.execute(
            "select asset_id, media_type, extension, width, height, duration, "
            "canonical_path from assets"):
        if aid in dl: rows[aid] = _blank(aid, mt, ext, w, h, dur, path)
    # NO SUPPRESSION FILTER HERE, DELIBERATELY. tag_suppressions is the library's
    # HISTORICAL record: measured 2026-09-25, 0 of its 39 rows still exist in
    # `tags`, because the library already removed them. A filter here removed
    # nothing and its test could not fail, so it was deleted rather than kept as
    # reassurance. The suppressions still matter for CAPTION evidence, where the
    # raw text survives the tag's deletion — see suppressed_claims().
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
    return rows


def _rows_snapshot(dl):
    """From grammar/library-snapshot.json, for a session with no library mounted.

    Not a reduced view. It carries exactly the fields _rows_live produces, and
    tests/test_pipeline.py asserts resolve() returns the identical ranked ids
    from both — a snapshot that quietly answered with less would be the worst
    outcome here, because a short candidate list reads as a thin library.
    """
    global SOURCE
    SOURCE = "snapshot"
    snap = PATHS.snapshot()
    if not snap:
        raise FileNotFoundError(
            f"no media library at {DB} and no snapshot at {PATHS.snapshot_path()} "
            "— run pipeline/export_library.py --write on a machine that has one")
    rows = {}
    for aid, a in (snap.get("assets") or {}).items():
        if aid not in dl: continue
        r = _blank(aid, a.get("media_type"), a.get("ext"), a.get("width"),
                   a.get("height"), a.get("duration"), a.get("path"))
        r["tags"] = [dict(t) for t in (a.get("tags") or [])]
        r["people"] = list(a.get("people") or [])
        r["captions"] = list(a.get("captions") or [])
        r["derivatives"] = [dict(d) for d in (a.get("derivatives") or [])]
        r["faces"] = a.get("faces") or 0
        rows[aid] = r
    return rows


def load():
    """Every lifecycle-approved delivered asset a brief can match against.

    Production Ready is the consumer boundary, not enrichment over the historical
    catalog. Rows outside its verified manifest may remain useful provenance, but
    they are not selectable production media.
    """
    if not DB.exists() and not PATHS.snapshot():
        raise FileNotFoundError(
            f"no media source: catalog absent at {DB} and no snapshot at "
            f"{PATHS.snapshot_path()} — run pipeline/export_library.py --write "
            "on a machine that has the library mounted")
    dl = delivery()
    if not dl:
        raise FileNotFoundError(f"authoritative media delivery is missing: {DELIVERY}")
    rows = _rows_live(dl) if DB.exists() else _rows_snapshot(dl)
    unknown = []
    for aid, tags in user_tags().items():
        if aid not in rows:
            unknown.append(aid)
            continue
        for t in tags:
            if not any(norm(x["tag"]) == norm(t["tag"]) and x["source"] == "user"
                       for x in rows[aid]["tags"]):
                rows[aid]["tags"].append({"tag": t["tag"], "source": "user"})
    if unknown:
        # A user tag on an asset outside the pool is a FINDING, not a no-op: it
        # means they tagged something the delivery boundary excludes.
        raise ValueError(
            f"grammar/media-tags.json tags {len(unknown)} asset(s) absent from the "
            f"selectable pool: {unknown[:5]} — either the asset needs delivering or "
            "the tag needs removing")
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
    # REMOVALS RUN LAST, after the delivery merge. Placed before it, they did
    # nothing: the delivery manifest carries its own `tags` map and re-appends
    # every tag it holds, so `2009` and `freshmen` came straight back and all
    # three XXL covers still scored identically. The loop ran, the keys matched,
    # and the effect was undone one block later.
    for aid, drop in removed_tags().items():
        if aid in rows:
            rows[aid]["tags"] = [t for t in rows[aid]["tags"]
                                 if norm(t["tag"]) not in drop]
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


PRIMARY_EVIDENCE = {"identity", "face", "tag"}


def _evidence(rec, entity):
    """Return the strongest field that names an entity, or ``None``.

    Production Ready identities, named faces and explicit content tags are
    identity evidence. Captions/descriptions and ingest/project names are
    discovery hints only; resolve() admits them only as a fallback when the
    stronger pool is empty for that entity.  All comparisons retain the existing
    normalised contains rule so compound tags such as ``kendrick-drake`` work.
    """
    e = norm(entity)
    if not e:
        return None
    for name in rec.get("delivered_identities") or []:
        if e in norm(name):
            return "identity", name
    for person in rec.get("people") or []:
        if e in norm(person):
            return "face", person
    # A PROJECT NAME IS SKIPPED IN BOTH LOOPS — it is not evidence at any strength,
    # which is the user's ruling. The source-based demotion below is left exactly as
    # it was: an earlier version of this also PROMOTED every non-project ingest tag
    # to primary, on the reasoning that `Headshot` and `Group Photo` are real
    # content. That made unregistered collection-style tags STRONGER than before —
    # Codex's fixture "Jay-Z fan collection" is not in ingestions.project, so it
    # became primary identity evidence for Jay-Z. Narrow the rule to the ruling.
    et = _name_tokens(entity)
    for tag in rec.get("tags") or []:
        name = tag.get("tag")
        if is_project_tag(name) or is_class_tag(name):
            continue
        if tag.get("source") in PROJECT_SOURCES:
            continue
        if e in norm(name):
            return "tag", name
        if tag_names_entity(name, et):
            return "tag", name
    if (rec.get("id"), e) in suppressed_claims():
        return None                     # the library ruled this extraction wrong
    for caption in rec.get("captions") or []:
        if e in norm(caption):
            return "caption", caption
    for tag in rec.get("tags") or []:
        if is_project_tag(tag.get("tag")):
            continue
        if tag.get("source") in PROJECT_SOURCES and e in norm(tag.get("tag")):
            return "project", tag.get("tag")
    return None


def matches(rec, entity, wrong=frozenset()):
    """Does any evidence name this entity, minus durable user corrections?"""
    e = norm(entity)
    if not e: return False
    if (rec["id"], e) in wrong: return False
    return _evidence(rec, entity) is not None


def _why(rec, entity):
    """Which field carried the match — so a W press is informed, not blind.

    A `project:` prefix means the asset merely sits in a collection whose NAME
    contains the entity. That is the weakest evidence in the system and the user
    needs to see it as such before deciding whether to press W.
    """
    evidence = _evidence(rec, entity)
    if evidence:
        kind, value = evidence
        if kind == "caption":
            e = norm(entity)
            i = norm(value).find(e)
            return f"caption:…{value[max(0, i - 24):i + len(entity) + 24]}…"
        return f"{kind}:{value}"
    return "?"


# HOW RECENTLY, AND HOW OFTEN — not whether. User 2026-09-26: "that needs to be a
# timed thing. dont stop media from being avaiable, just less desirable for the next
# 180 seconds after being shown x amount of times."
# `used` was a set: shown once, demoted on every later beat for the rest of the
# video, whether that was four seconds ago or eleven minutes. The narration runs
# 804 seconds and every beat carries a real start time, so elapsed time was known
# and simply not used.
COOL_WINDOW = 180.0          # seconds for one showing to fade to nothing
COOL_FREE = 1                # showings inside the window before any penalty bites


def cooldown(shown_at, now, window=COOL_WINDOW, free=COOL_FREE):
    """How undesirable this asset is right now. 0 is cool, higher is hotter.

    Each showing inside the window contributes what is left of its fade — 1.0 the
    instant it appears, 0.0 `window` seconds later. Showings older than the window
    contribute nothing, so an asset used at 0:20 is fully available again by 3:20.
    The first `free` showings are forgiven, which makes this a penalty for
    REPETITION rather than for having been used at all.

    Never excludes: the caller ranks on this, and a hot asset still appears when
    nothing cooler exists.
    """
    if not shown_at: return 0.0
    live = sorted((max(0.0, 1.0 - (now - t) / window)
                   for t in shown_at if t is not None and t <= now), reverse=True)
    return round(sum(live[free:]), 4) if len(live) > free else 0.0


def spread(recs, n, used=frozenset(), pin=frozenset(), history=None, now=None):
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
        tail = spread(rest, None if n is None else max(0, n - len(first)),
                      used=used, history=history, now=now)
        out = first + tail
        return out if n is None else out[:max(n, len(first))]
    buckets = {}
    for r in recs:
        key = (r.get("media_type"), r.get("framing"))
        buckets.setdefault(key, []).append(r)
    # Bucket order follows the incoming rank of each bucket's best member, so
    # strong evidence still leads; only the SPREAD across buckets is new.
    order = sorted(buckets, key=lambda k: recs.index(buckets[k][0]))
    # TIERS BY HOW HOT, NOT BY WHETHER SEEN. `used` was binary — an asset shown once
    # sat in tier 1 for the rest of the video. Tiers now come from cooldown(), so an
    # asset used eleven minutes ago is tier 0 again while one used four seconds ago
    # is not. `used` still works unchanged when no timing is passed, because six
    # callers rely on it.
    hist = history or {}
    def heat(r):
        if now is None:
            return 1 if r["id"] in used else 0
        c = cooldown(hist.get(r["id"]), now)
        return 0 if c <= 0 else (1 if c < 1.0 else 2)
    out, seen = [], set()
    for tier in (0, 1, 2):                    # cool first, warm, then hot
        while True:
            took = False
            for k in order:
                for r in buckets[k]:
                    if r["id"] in seen: continue
                    if heat(r) > tier: continue
                    out.append(r); seen.add(r["id"]); took = True
                    break
            if not took: break
    return out[:n] if n is not None else out


def resolve(entities, pool=None, media_type=None, cutout=None, framing=None,
            wrong=None, wants=(), kinds=(), quote=""):
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
        if framing and r["framing"] and not framing_matches(r["framing"], (framing,)):
            return False
        return True

    eligible = [r for r in pool.values() if ok(r)]
    all_matches = {
        e: [r for r in eligible if matches(r, e, wrong)]
        for e in ents
    }
    primary = {
        e: [r for r in all_matches[e]
            if (_evidence(r, e) or (None,))[0] in PRIMARY_EVIDENCE]
        for e in ents
    }
    # Captions/descriptions and project names are a true fallback stage. They
    # cannot enter a slate, and therefore cannot be promoted by spread(), while
    # any tag/face/delivered identity candidate is available for that entity.
    individual = {e: (primary[e] or all_matches[e]) for e in ents}

    primary_group = [
        r for r in eligible
        if len(ents) > 1 and all(
            matches(r, e, wrong)
            and (_evidence(r, e) or (None,))[0] in PRIMARY_EVIDENCE
            for e in ents
        )
    ]
    fallback_group = [
        r for r in eligible
        if len(ents) > 1 and all(matches(r, e, wrong) for e in ents)
    ]
    # If every entity has a strong individual option, a weak caption/project
    # group is unnecessary. If an entity has no strong option, the weak group is
    # retained as the documented fallback rather than hiding a sourcing gap.
    group = primary_group or (
        fallback_group if any(not primary[e] for e in ents) else []
    )
    # Rank: a named face beats a tag beats a caption; a cutout beats a raw still;
    # stills before video unless video was asked for. Never excludes — orders.
    STRENGTH = {"identity": 0, "face": 0, "tag": 1,
                "caption": 2, "project": 4}
    def fit(r):
        """0 right framing, 1 unknown, 2 wrong. RANKS, never excludes.

        An UNTAGGED asset scores 1, not 2: 436 of 506 carry no framing tag, and
        ranking them below a known-wrong one would hide most of the library
        behind a tag nobody has applied yet. The user's own words on 28-28 —
        "quarter, headshot or no no size specified images".
        """
        if not wants: return 0
        m = framing_matches(r.get("framing"), wants)
        return 1 if m is None else (0 if m else 2)
    def kfit(r):
        """Same shape as fit(): 0 right kind, 1 unknown, 2 wrong. 660 of 1,381
        assets carry no kind signal, so unknown sits in the middle."""
        if not kinds: return 0
        k = r.get("kind") or kind_of(r)
        if not k: return 1
        return 0 if k in kinds else 2
    # ABOUTNESS SITS AFTER kind and framing, BEFORE evidence strength. Once an
    # asset can physically serve the slot, being about the right THING outranks
    # being a stronger match on WHO: a confirmed photo of Drake is not a better
    # answer than the actual XXL cover on a beat about the XXL cover. Placing it
    # after STRENGTH leaves the cover behind every delivered-identity portrait,
    # which is the 124-of-127 the user reported.
    def qscore(r, es):
        return -quote_overlap(quote, r, es)  # negative: more shared words ranks first
    def rank(r, e):
        return (kfit(r), fit(r), qscore(r, (e,)),
                STRENGTH.get(_why(r, e).split(":", 1)[0], 3),
                0 if r["has_cutout"] else 1,
                0 if r["framing"] else 1,
                r["id"])
    # A GROUP is only as good as its WEAKEST leg. Ranking on the first entity
    # hid that the second matched nothing but a project label.
    def grank(r):
        return (kfit(r), fit(r), qscore(r, ents),
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
