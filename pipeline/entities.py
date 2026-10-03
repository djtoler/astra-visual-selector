#!/usr/bin/env python3
"""Deterministic entity extraction from a beat. A gazetteer, not a model.

WHY NOT A MODEL. The names in this domain are exactly what statistical NER gets
wrong: `Curren$y` splits at the `$`, `21 Savage` and `50 Cent` read as CARDINAL +
noun, `Ty Dolla $ign` is three tokens of punctuation soup. A model can also
normalise a name into something that is not it — `Curren$y` to `Curreny` — and
then every downstream lookup misses. A roster match cannot hallucinate.

WHY NOT AN NER PACKAGE. spaCy and friends are reproducible, not deterministic:
still a statistical model, still versioned, still a large dependency, and they
would need this same domain lexicon bolted on to handle the hard cases. If the
lexicon is doing the work, use the lexicon.

THE SHARED ROSTER IS THE DOMAIN. Data, Story and Matching consume the same
digest-pinned `djtoler/entity_roster` document. Matching keeps only a name-free
source manifest and derives its in-memory surface index after verification.

THREE MATCHES, IN ORDER, AND THE THIRD REFUSES TO GUESS:

  1 FULL NAME, longest first. "Jay Rock" beats any shorter overlap, which is the
    whole fix for the defect that sent a Jay Rock brief to 68 Jay-Z photos.
  2 UNIQUE TOKEN. The narration says "Kendrick"; the roster says "Kendrick
    Lamar". A token belonging to exactly one roster name resolves to it — 142 of
    them do. `Kendrick`, `Nipsey`, `Freddie`, `Gibbs`, `Thug`.
  3 AMBIGUOUS TOKEN. Seven tokens belong to several names: lil, young, the, kid,
    god, rock, ybn. These are REPORTED, never resolved. Guessing between Kid Cudi
    and Kid Ink would put the wrong person on screen, and a wrong entity is the
    one failure the review downstream cannot correct.

CAPITALISATION IS REQUIRED. Six roster names are also ordinary English words —
Future, Drake, Logic, Wale, Gunna, Blueface. Matching case-insensitively would
turn "in the future" into the artist Future. The source text must have the name
capitalised. Zero false positives in the current 40 beats; the guard is for the
next script, not this one.

    python3 pipeline/entities.py "Ab-Soul falls twenty-eight places. Jay Rock, twelve."
    python3 pipeline/entities.py --beats          every served beat
"""
import collections, hashlib, json, os, pathlib, re, sys

P = pathlib.Path(__file__).resolve().parent
ROOT = P.parent
ROSTER_SOURCE = ROOT / "grammar" / "entity-roster-source.json"
BEATS = P / "beats-all.json"
PICKS = P.parent / "grammar" / "picks.json"
MIN_TOKEN = 3
# Function words are never distinctive, whatever roster name happens to contain
# them. "the" belongs to Chance the Rapper AND Ski Mask the Slump God, so before
# this it was reported as an ambiguous entity on 5 of 24 beats. It is an article.
STOP = {"the", "and", "for", "with", "his", "her", "them", "they", "that", "this",
        "there", "here", "from", "into", "only", "than", "then", "was", "are",
        "who", "what", "when", "how", "all", "one", "two", "not", "but", "out"}


def _source():
    return json.loads(ROSTER_SOURCE.read_text(encoding="utf-8"))


def roster_path():
    candidates = []
    if os.environ.get("SHARED_ENTITY_ROSTER_PATH"):
        candidates.append(pathlib.Path(os.environ["SHARED_ENTITY_ROSTER_PATH"]))
    candidates.append(ROOT.parent / "entity_roster" / "entity-roster.json")
    for path in candidates:
        if path.is_file():
            return path
    raise FileNotFoundError(
        "shared entity roster unavailable; clone djtoler/entity_roster and set "
        "SHARED_ENTITY_ROSTER_PATH to entity-roster.json"
    )


def roster(path=None):
    path = pathlib.Path(path) if path else roster_path()
    source = _source()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != source["sha256"]:
        raise ValueError(f"shared entity roster digest mismatch: {digest}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("registryId") != source["registryId"]:
        raise ValueError("shared entity roster registryId mismatch")
    if str(data.get("registryVersion")) != str(source["registryVersion"]):
        raise ValueError("shared entity roster version mismatch")
    names = [entity["canonicalName"] for entity in data["entities"]]
    aliases = {}
    ids = {}
    types = {}
    alias_review = {}
    for entity in data["entities"]:
        name = entity["canonicalName"]
        ids[name] = entity["id"]
        types[name] = entity["type"]
        for alias in entity.get("aliases", []):
            surface = alias["value"]
            prior = aliases.setdefault(surface.casefold(), name)
            if prior != name:
                raise ValueError(f"shared roster alias collision: {surface}")
            alias_review[surface] = alias["reviewState"]
    meta = {
        "_count": len(names),
        "_snapshotAt": data.get("generatedAt", "")[:10],
        "_registryId": data["registryId"],
        "_registryVersion": str(data["registryVersion"]),
        "_source": source,
        "_aliases": aliases,
        "_aliasReview": alias_review,
        "_entityIds": ids,
        "_entityTypes": types,
    }
    return names, meta


def _index(surfaces):
    """token -> the roster names containing it. Built once, pure."""
    tok = collections.defaultdict(set)
    for surface, canonical in surfaces.items():
        for t in re.split(r"[\s\-]+", surface):
            if len(t) >= MIN_TOKEN and not t.isdigit() and t.lower() not in STOP:
                tok[t.lower()].add(canonical)
    return tok


def _capitalised(text, start, end):
    """The matched span must look like a name in the source, not a common word.

    Six roster names are ordinary English words. "in the future" must not become
    the artist Future.
    """
    return text[start:end][:1].isupper()


def extract(text, names=None, aliases=None, entity_ids=None, entity_types=None):
    """-> {'entities': [...], 'ambiguous': [{'token','candidates'}], 'spans': {...}}

    `entities` is what a brief may ask for. `ambiguous` is what a human must rule
    on; it is deliberately NOT merged into entities, because an entity resolved
    by guess is worse than an entity missed — a missed one shows up as a gap and
    gets sourced, a wrong one gets a photo of the wrong person picked for it.
    """
    if names is None:
        names, meta = roster()
        aliases = meta["_aliases"]
        entity_ids = meta["_entityIds"]
        entity_types = meta["_entityTypes"]
    aliases = aliases or {}
    entity_ids = entity_ids or {}
    entity_types = entity_types or {}
    surfaces = {name: name for name in names}
    for surface_key, canonical in aliases.items():
        # roster() casefolds alias keys for collision checking; the authored
        # casing is not identity-significant for matching.
        surfaces[surface_key] = canonical
    tok = _index(surfaces)
    taken = [False] * len(text)
    found, spans = [], {}

    # 1 — full names, longest first
    for surface in sorted(surfaces, key=len, reverse=True):
        canonical = surfaces[surface]
        for m in re.finditer(re.escape(surface), text, re.I):
            if any(taken[m.start():m.end()]):
                continue
            if not _capitalised(text, m.start(), m.end()):
                continue
            for i in range(m.start(), m.end()):
                taken[i] = True
            found.append(canonical)
            spans.setdefault(canonical, []).append(text[m.start():m.end()])

    # 2, 3 and 4 — leftover words.
    # The token pattern INCLUDES hyphens, so "Jay-Z" is one word and not the
    # token "Jay". Splitting on the hyphen took beat 30-30a's "Jay-Z's year
    # seventeen", found "Jay" unique to "Jay Rock", and returned the wrong
    # artist with no signal at all — the inverse of the defect this file exists
    # to fix, and worse, because it was silent.
    ambiguous, unknown = [], []
    for m in re.finditer(r"[A-Za-z][A-Za-z'$.\-]{%d,}" % (MIN_TOKEN - 1), text):
        if any(taken[m.start():m.end()]):
            continue
        word = m.group(0)
        # the possessive belongs to the sentence, not the name: "Jay-Z's" is Jay-Z
        if word.lower().endswith("'s"): word = word[:-2]
        word = word.strip(".'-")
        cands = tok.get(word.lower())
        if not _capitalised(text, m.start(), m.end()):
            continue
        if not cands:
            # A capitalised word the roster does not know. REPORTED, because a
            # gazetteer's failure mode is silence: Jay-Z is discussed in the
            # narration and is not among the 109, and nothing said so.
            # MID-SENTENCE capitalisation only. "Number", "Seven", "Pick" and
            # "Start" are capitalised solely because they open a sentence; a
            # name is capitalised wherever it appears. This is what separates
            # `Markie` — the Biz Markie the user said was missing — from the 14
            # ordinary words that sat beside it in the first version.
            before = text[:m.start()].rstrip()
            sentence_initial = (not before) or before[-1] in ".!?:;\u2014-"
            if word.lower() not in STOP and not sentence_initial:
                unknown.append({"text": word, "at": m.start()})
            continue
        if len(cands) == 1:
            name = next(iter(cands))
            for i in range(m.start(), m.end()):
                taken[i] = True
            found.append(name)
            spans.setdefault(name, []).append(word)
        else:
            ambiguous.append({"token": word, "candidates": sorted(cands)})

    seen, out = set(), []
    for n in found:
        if n not in seen:
            seen.add(n)
            out.append(n)
    refs = [
        {
            "entityId": entity_ids[name],
            "canonicalName": name,
            "entityType": entity_types.get(name),
            "surfaces": spans.get(name, []),
        }
        for name in sorted(out) if name in entity_ids
    ]
    return {"entities": sorted(out), "entityRefs": refs, "ambiguous": ambiguous,
            "unknown": unknown, "spans": spans}


def main(argv):
    names, meta = roster()
    if "--beats" in argv:
        beats = json.load(open(BEATS))
        served = json.load(open(PICKS))["beats"]
        tot = amb = 0
        print(f"roster {meta['_count']} names, snapshot {meta['_snapshotAt']}\n")
        for pid in sorted(beats):
            for b in beats[pid]:
                k = f"{pid}-{b['id']}"
                if k not in served:
                    continue
                r = extract(
                    b["quote"] + " " + (b.get("entity_kind") or ""),
                    names,
                    aliases=meta["_aliases"],
                    entity_ids=meta["_entityIds"],
                    entity_types=meta["_entityTypes"],
                )
                if r["entities"] or r["ambiguous"]:
                    tot += len(r["entities"])
                    amb += len(r["ambiguous"])
                    print(f"   {k:8} {', '.join(r['entities']) or '—'}")
                    for a in r["ambiguous"]:
                        print(f"            AMBIGUOUS {a['token']!r}: {a['candidates']}")
        print(f"\n   {tot} entity mention(s), {amb} ambiguous token(s) needing a ruling")
        return 0
    text = " ".join(a for a in argv[1:] if not a.startswith("--"))
    if not text:
        print(__doc__)
        return 2
    r = extract(
        text,
        names,
        aliases=meta["_aliases"],
        entity_ids=meta["_entityIds"],
        entity_types=meta["_entityTypes"],
    )
    print(json.dumps(r, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
