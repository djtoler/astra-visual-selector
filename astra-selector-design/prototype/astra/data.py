"""Loaders for every ground-truth source. Read-only; nothing here writes to the project."""
import json, os, re, functools

POLISH = "/Users/dwaynetoler/Documents/ChatGPT/Polish"
NVA    = os.path.join(POLISH, "ae-template-automation/narration-visual-annotations")
LIB    = os.path.join(POLISH, "ae-template-automation/scene-library")
DESIGN = "/Users/dwaynetoler/timeline/astra-selector-design"
MEDIA  = "/Users/dwaynetoler/Media Library"


def _j(path):
    with open(path) as f:
        return json.load(f)


@functools.lru_cache(maxsize=None)
def requirements():
    return _j(os.path.join(NVA, "astra-selector-formula-inputs.json"))


@functools.lru_cache(maxsize=None)
def case_overrides():
    path = os.path.join(DESIGN, "rules/case-overrides.json")
    if not os.path.exists(path):
        return {}
    return _j(path).get("overrides", {})


@functools.lru_cache(maxsize=None)
def cases():
    """Recorded cases with any locally approved override applied at read time.

    The project's own file is never modified; overrides live in
    rules/case-overrides.json and each carries its correction id and approval.
    """
    out = {c["id"]: c for c in _j(os.path.join(NVA, "year-seventeen-30-selector-cases.json"))["cases"]}
    for cid, ov in case_overrides().items():
        if cid not in out:
            continue
        case = json.loads(json.dumps(out[cid]))
        target = case
        parts = ov["field"].split(".")
        for k in parts[:-1]:
            target = target.setdefault(k, {})
        target[parts[-1]] = ov["overrideValue"]
        case["_localOverride"] = {"field": ov["field"], "recorded": ov["recordedValue"],
                                  "applied": ov["overrideValue"],
                                  "correctionId": ov["correctionId"], "reason": ov["reason"]}
        out[cid] = case
    return out


@functools.lru_cache(maxsize=None)
def timing():
    return {p["passageId"]: p for p in _j(os.path.join(NVA, "year-seventeen-narration-timing.json"))["passages"]}


@functools.lru_cache(maxsize=None)
def words():
    """Flat list of {word,start,end} from the whisper alignment."""
    w = _j(os.path.join(NVA, "year-seventeen-narration-whisper.json"))
    out = []
    for seg in w.get("segments", []):
        for wd in seg.get("words") or []:
            out.append({"word": (wd.get("word") or "").strip(),
                        "start": wd.get("start"), "end": wd.get("end")})
    return out


@functools.lru_cache(maxsize=None)
def passages_md():
    """passageId -> verbatim narration from the annotation doc."""
    txt = open(os.path.join(NVA, "year-seventeen-30-passages.md")).read()
    out = {}
    for block in txt.split("\n## ")[1:]:
        pid = block[:2]
        q = re.search(r"^> (.+)$", block, re.M)
        if q:
            out[pid] = q.group(1).strip()
    return out


@functools.lru_cache(maxsize=None)
def feedback():
    return _j(os.path.join(NVA, "feedback-calibration.json"))


@functools.lru_cache(maxsize=None)
def approved_catalog():
    return _j(os.path.join(LIB, "approved/catalog.json"))


@functools.lru_cache(maxsize=None)
def catalog_policy():
    return _j(os.path.join(LIB, "approved-catalog-policy.json"))


@functools.lru_cache(maxsize=None)
def infographic_profiles():
    return _j(os.path.join(POLISH, "infographic-template-system/profiles/catalog.json"))["profiles"]


@functools.lru_cache(maxsize=None)
def scatter_profiles():
    return _j(os.path.join(POLISH, "cinematic-scatter/profiles/catalog.json"))["profiles"]


@functools.lru_cache(maxsize=None)
def ae_motion_profiles():
    """Per-template motion profiles: measured pacing, reading time, style, and a
    GRADED documentary-role vocabulary. Far richer than the approved catalog's
    per-scene records and, until now, unused by this prototype."""
    import glob
    skip = {"catalog.json", "coverage.json", "index.json", "duplicates-and-unresolved.json"}
    out = {}
    for f in glob.glob(os.path.join(POLISH, "ae-template-automation/profiles/*.json")):
        if os.path.basename(f) in skip:
            continue
        try:
            d = _j(f)
        except Exception:
            continue
        if d.get("template_id"):
            out[d["template_id"]] = d
    return out


@functools.lru_cache(maxsize=None)
def template_family_map():
    return _j(os.path.join(NVA, "approved-template-family-map.json"))


@functools.lru_cache(maxsize=None)
def crosswalk():
    return _j(os.path.join(DESIGN, "data/job-vocabulary-crosswalk.json"))


@functools.lru_cache(maxsize=None)
def assets():
    with open(os.path.join(MEDIA, "METADATA/assets.jsonl")) as f:
        return [json.loads(line) for line in f if line.strip()]


@functools.lru_cache(maxsize=None)
def excluded_template_ids():
    pol = catalog_policy()
    out = {e["templateId"] for e in pol.get("excludedInfographicTemplates", [])}
    out |= {e["sourceId"] for e in pol.get("excludedSources", [])}
    return out


def global_rules():
    return {r["id"]: r["rule"] for r in feedback()["globalRules"]}


def passage_feedback(pid):
    """All raw feedback comments recorded against any shot of this passage."""
    raw = feedback()["rawFeedback"]
    return {k: v for k, v in raw.items() if k.split(".")[0] == pid}
