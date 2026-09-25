"""Build a timed visual contract. Narration in, obligations out.

No media is retrieved here and no template is considered. Every timing number
is measured from the aligned audio; claims, roles and events come from the seed.
"""
import json, os
from . import data, phrase

SEEDS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "seeds/slice.json")

# Corpus reference points. Descriptive, never a budget (user ruling 2026-09-16).
CORPUS = {"p25": 6.0, "median": 9.0, "p75": 14.0, "infographic_median": 16.5}
READABLE_FLOOR = 1.5
CHANGE_CEILING = 6.8


def _seed(pid):
    with open(SEEDS) as f:
        return json.load(f)[pid]


def build(pid):
    seed = _seed(pid)
    case = data.cases()[pid]
    tim = data.timing()[pid]
    text = data.passages_md()[pid]
    start, end = tim["startSeconds"], tim["endSeconds"]

    events = []
    for ev in seed["visualEvents"]:
        r = phrase.resolve(ev["triggerPhrase"], start, end)
        rec = dict(ev)
        if r["found"]:
            rec["triggerOffsetSeconds"] = round(r["startSeconds"] - start, 2)
            rec["measuredStartSeconds"] = r["startSeconds"]
            rec["matchConfidence"] = r["ratio"]
            rec["matchedTranscript"] = r["matchedText"]
            rec["resolved"] = True
        else:
            rec["resolved"] = False
            rec["resolutionFailure"] = r
        rec.setdefault("toleranceSeconds", 0.25)
        events.append(rec)

    holds = [rl.get("legibilityRequirement", {}).get("minimumOnScreenSeconds")
             for rl in seed["requiredMedia"]]
    holds = [h for h in holds if h]
    min_hold = max(holds) if holds else READABLE_FLOOR

    # How many internal changes the container owes across this duration.
    dur = tim["durationSeconds"]
    owed = max(1, int(dur / CHANGE_CEILING + 0.999))
    resolved = [e for e in events if e.get("resolved")]

    # Evidence that needs to finish talking extends the unit.
    needs_extension = []
    shot_by_id = {s["shotId"]: s for s in tim["shotTimings"]}
    for rl in seed["requiredMedia"]:
        lr = rl.get("legibilityRequirement") or {}
        need = lr.get("minimumOnScreenSeconds")
        shot = rl.get("shotId")
        if not need or not shot or shot not in shot_by_id:
            continue
        avail = shot_by_id[shot]["durationSeconds"]
        if need > avail:
            needs_extension.append({"roleId": rl["roleId"], "shotId": shot,
                                    "availableSeconds": avail, "needsSeconds": need,
                                    "shortfallSeconds": round(need - avail, 2),
                                    "resolution": "extend the shot; narration yields so the proof can complete"})

    # COR-0004 standing exception: continuous testimony or performance, where the
    # absence of change is the treatment rather than a defect.
    CONTINUOUS = {"talking_head", "performance"}
    fams = {r.get("mediaFamily") for r in seed["requiredMedia"]}
    continuous_exception = None
    if fams & CONTINUOUS:
        continuous_exception = {
            "applies": True,
            "reason": f"Media family {sorted(fams & CONTINUOUS)} is continuous; the unit runs as long as the source needs.",
            "effect": "The change budget does not apply."}

    strictest = "decorative_media_allowed"
    order = ["exact_source_required", "exact_event_or_entity_required",
             "representative_media_allowed", "decorative_media_allowed"]
    for c in seed["claims"]:
        if order.index(c["evidenceObligation"]) < order.index(strictest):
            strictest = c["evidenceObligation"]

    return {
        "contractId": f"year-seventeen:P{pid}",
        "schemaVersion": 1,
        "scriptRef": {"scriptId": "year-seventeen", "sectionId": case["label"],
                      "passageIndex": int(pid)},
        "narration": {"text": text,
                      "measuredTranscript": phrase.transcript(start, end)},
        "timing": {
            "timingSource": "measured_audio",
            "audioStartSeconds": start,
            "audioEndSeconds": end,
            "audioDurationSeconds": dur,
            "wordAlignmentCoverage": tim["wordAlignmentCoverage"],
            "recordedShots": tim["shotTimings"],
            "acceptableDurationSeconds": {"min": round(dur, 2), "target": round(dur, 2),
                                          "max": None,
                                          "note": "Descriptive. Corpus median 9.0s, p75 14.0s. "
                                                  "Never a cap: the evidence sets the length."},
            "durationPolicy": {"mode": "elastic", "evidenceMustComplete": True,
                               "narrationYields": bool(needs_extension),
                               "extensionRequired": needs_extension},
            "minimumReadableHoldSeconds": min_hold,
            "internalChangeBudget": {
                "enforcement": "advisory_only",
                "requiredChanges": owed,
                "secondsPerChangeCeiling": CHANGE_CEILING,
                "eventsAvailable": len(resolved),
                "satisfied": len(resolved) >= owed,
                "standingException": continuous_exception,
                "note": ("Advisory. May suggest splitting a unit, but never rejects a candidate "
                         "and never forces a split. Overridden whenever the content needs the time."),
            },
        },
        "takeaway": seed["takeaway"],
        "narrationJob": case["input"].get("job"),
        "claims": seed["claims"],
        "strictestEvidenceObligation": strictest,
        "entities": seed["entities"],
        "focalEntityCount": seed["focalEntityCount"],
        "entityRelationship": seed["entityRelationship"],
        "requiredMedia": seed["requiredMedia"],
        "visualEvents": events,
        "prohibitions": seed["prohibitions"],
        "successConditions": seed["successConditions"],
        "failureConditions": seed["failureConditions"],
        "readingLoad": seed.get("readingLoad", "normal"),
        "scriptConflict": seed.get("scriptConflict"),
        "proposedDecomposition": seed.get("proposedDecomposition"),
        "groundTruth": {"desired": case["desired"], "shots": case["shots"],
                        "fallback": case["fallback"],
                        "allowedKinds": case["input"].get("allowedKinds"),
                        "allowedTemplateIds": case["input"].get("allowedTemplateIds"),
                        "preferredTemplateIds": case["input"].get("preferredTemplateIds"),
                        "presentation": case["input"].get("presentation")},
        "provenance": {"createdBy": "astra prototype vertical slice",
                       "rulesetVersion": "0.2.0-prototype",
                       "authoredFields": ["claims", "entities", "requiredMedia",
                                          "visualEvents", "prohibitions",
                                          "successConditions", "failureConditions"],
                       "measuredFields": ["all timing values", "event offsets"],
                       "humanReviewed": False},
    }
