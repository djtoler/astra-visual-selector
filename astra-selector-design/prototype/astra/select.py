"""Candidate generation, hard gates, lexicographic ranking, slate construction.

Priority order updated by user ruling 2026-09-16: among candidates that clear
every gate, the better-timed one wins.
"""
import re
from . import data, rules

PRIORITY = ["timingAlignment", "claimCommunication", "factualAccuracy",
            "structuralFit", "styleConsistency", "assetQuality", "polish", "renderCost",
            # Final tiebreak only. When candidates are equal on all eight priorities
            # the order was previously decided by pool position, which is arbitrary.
            # A candidate the user curated into an approved family for this exact job
            # carries more evidence than a generic intent match, so it wins the tie.
            "curation"]

# case.input.presentation is an evaluation constraint in the ground truth, not a hint.
PRESENTATION_FIT = {
    "document": {"direct:evidence_hold": 1.0, "after_effects": 0.7, "infographic": 0.3,
                 "cinematic_3d": 0.1, "direct:archival_cut": 0.8, "direct:text_card": 0.2},
    "text":     {"direct:text_card": 1.0, "after_effects": 0.4, "infographic": 0.3,
                 "cinematic_3d": 0.1, "direct:evidence_hold": 0.4, "direct:archival_cut": 0.2},
    "chart":    {"infographic": 1.0, "cinematic_3d": 0.7, "after_effects": 0.3,
                 "direct:evidence_hold": 0.2, "direct:text_card": 0.2, "direct:archival_cut": 0.1},
    "scatter":  {"cinematic_3d": 1.0, "infographic": 0.8, "after_effects": 0.2,
                 "direct:evidence_hold": 0.1, "direct:text_card": 0.1, "direct:archival_cut": 0.1},
    "portrait": {"after_effects": 0.9, "infographic": 0.7, "cinematic_3d": 0.5,
                 "direct:archival_cut": 0.8, "direct:evidence_hold": 0.3, "direct:text_card": 0.1},
    "cutout":   {"after_effects": 0.9, "infographic": 0.7, "cinematic_3d": 0.5,
                 "direct:archival_cut": 0.7, "direct:evidence_hold": 0.3, "direct:text_card": 0.1},
}


def presentation_fit(candidate, contract):
    pres = contract["groundTruth"].get("presentation")
    if not pres or pres not in PRESENTATION_FIT:
        return None
    # `presentation` is recorded once for a whole passage. A split passage can
    # contain a shot the annotation never described: passage 02 is a document
    # and then a distance comparison. Applying the passage-level value to a later
    # shot would rule out treatments the ground truth never meant to exclude, so
    # it goes neutral there rather than binding.
    if contract.get("shotId") and contract["shotId"] != "01":
        return None
    table = PRESENTATION_FIT[pres]
    return table.get(candidate["templateId"], table.get(candidate["kind"], 0.5))


# COR-0012, narrow approval 2026-09-16. Schedule replacement is available but
# tentative: proven only where a render and hold check exists. Anywhere else the
# candidate is flagged and forced to review rather than assumed to retime cleanly.
SCHEDULE_REPLACEMENT_PROVEN = {
    "07-history-slideshow", "text-list-carousel", "41_five_value_headshots",
}


def schedule_replacement_status(candidate, contract):
    """Does this candidate need its schedule replaced, and is that proven here?"""
    decisive = [e for e in contract["visualEvents"] if e.get("criticality") == "decisive"]
    if len(decisive) < 2 and contract["readingLoad"] != "high":
        return None
    if candidate["kind"] == "direct":
        return None
    proven = candidate.get("templateId") in SCHEDULE_REPLACEMENT_PROVEN
    return {"required": True, "proven": proven,
            "reason": (f"{len(decisive)} decisive cues must land on their phrases, so the "
                       f"native schedule is replaced with a cue schedule."),
            "status": "proven_by_render" if proven else "unproven_on_this_template"}


GATES = ["communicates_claim", "evidence_specificity_honoured", "no_unsupported_implication",
         "evidence_legible", "decisive_events_alignable", "asset_quality_sufficient",
         "not_forcing_a_template", "density_acceptable", "era_consistent"]


def _spatial_first(contract, detail=False):
    """Rule spatial_relationship_first, resolved through the local rule overlay."""
    blob = " ".join([contract["takeaway"]] + [c["text"] for c in contract["claims"]])
    hit, terms, source = rules.matches("spatial_relationship_first", blob)
    if detail:
        return {"fired": hit, "terms": terms, "triggerSource": source,
                "ruleVersion": rules.active()["spatial_relationship_first"]["version"]}
    return hit


# Keys that count people or things the viewer identifies, in preference order.
ENTITY_KEYS = ["subjects", "entities", "entries", "candidates", "figures", "cards",
               "points", "observations", "packages", "stages"]
PORTRAIT_HINT = re.compile(r"portrait|headshot|photo|cutout|body", re.I)


def portrait_capacity(profile):
    """How many people this layout was DESIGNED to show, and whether it shows faces.

    A grid built for fifteen renders each face at fifteen-up size even when only
    six are supplied, so the designed capacity is what sets portrait size.
    """
    sc = (profile.get("capacity") or {}).get("semantic_counts") or {}
    cap = None
    # Most direct signal when present: how many portraits are actually on screen.
    if isinstance(sc.get("visible_header_portraits"), int):
        cap = sc["visible_header_portraits"]
    if cap is None:
        for k in ENTITY_KEYS:
            if isinstance(sc.get(k), int):
                cap = sc[k]
                break
    if cap is None and isinstance(sc.get("pairs"), int):
        cap = sc["pairs"] * 2 + (sc.get("heroes") or 0)
    if cap is None:
        # group_sizes [5,5,5], table_sizes [10,10], lane_sizes [6,6] and friends
        # describe a layout's compartments; the total is their sum.
        sizes = [v for k, v in sc.items()
                 if k.endswith("_sizes") and isinstance(v, list)
                 and all(isinstance(x, int) for x in v)]
        if sizes:
            cap = sum(sum(v) for v in sizes)
    if cap is None and isinstance(sc.get("heroes"), int):
        # A hero across many periods is a one-entity layout, not an 18-entity one.
        cap = sc["heroes"] + (sc.get("peer_callouts") or 0)
    blob = " ".join(str(profile.get(k)) for k in
                    ("visual_encoding", "data_mapping", "roles", "media", "capacity_summary"))
    return cap, bool(PORTRAIT_HINT.search(blob))


def _cap_range(text):
    """Entity capacity from a profile's capacity_summary.

    These summaries state several different numbers. A "workable" range is the
    real capacity and wins outright; "N entities as shipped" is only the sample
    dataset size and must never be read as a requirement. Reading the shipped
    count as exact rejected a 35-entity layout for holding 12.
    """
    t = str(text)
    m = re.search(r"~?\s*(\d+)\s*[-\u2013\u2014]\s*(\d+)\s*workable", t, re.I)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"(\d+)\s*[-\u2013\u2014]\s*(\d+)\s+(?:\w+\s+){0,3}?entit", t, re.I)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"exactly\s+(\d+)\s+(?:\w+\s+){0,2}?(?:entit|subject|portrait|duration)", t, re.I)
    if m:
        return int(m.group(1)), int(m.group(1))
    m = re.search(r"(?:exactly\s*)?(\d+)\s*(?:entities|subjects)", t, re.I)
    if m:
        n = int(m.group(1))
        # A bare count with "as shipped" nearby is a sample size, not a limit.
        if re.search(r"as shipped", t, re.I):
            return 1, n
        return n, n
    return None, None


def _scatter_candidates(contract):
    out = []
    n = contract["focalEntityCount"]
    for p in data.scatter_profiles():
        lo, hi = _cap_range(p.get("capacity_summary"))
        fits = True if lo is None else (lo <= n <= hi)
        out.append({"kind": "cinematic_3d", "templateId": p.get("layout_id"),
                    "name": p.get("abstract_name"), "intents": p.get("intents") or [],
                    "capacitySummary": p.get("capacity_summary"),
                    "capacityFits": fits, "capacityRange": [lo, hi],
                    "avoidWhen": p.get("avoid_when") or [],
                    "carriesData": not re.search(r"(no|0|zero)\s+measured\s+dimension",
                                                 str(p.get("capacity_summary", "")), re.I)})
    return out


def _infographic_candidates(contract):
    excluded = data.excluded_template_ids()
    out = []
    n = contract["focalEntityCount"]
    for p in data.infographic_profiles():
        tid = p.get("template_id")
        if tid in excluded:
            continue
        lo, hi = _cap_range(p.get("capacity_summary"))
        sub = (p.get("capacity") or {}).get("semantic_counts", {}).get("subjects")
        if sub is not None:
            lo = hi = sub
        fits = True if lo is None else (lo <= n <= hi)
        pcap, shows_faces = portrait_capacity(p)
        slack = (pcap - n) if (pcap is not None and n) else None
        out.append({"kind": "infographic", "templateId": tid,
                    "name": p.get("abstract_name"), "intents": p.get("intents") or [],
                    "capacitySummary": p.get("capacity_summary"),
                    "capacityFits": fits, "capacityRange": [lo, hi],
                    "designedForEntities": pcap, "showsPortraits": shows_faces,
                    "capacitySlack": slack,
                    "avoidWhen": p.get("avoid_when") or [], "carriesData": True})
    return out


def _ae_candidates(contract):
    cw = data.crosswalk()["jobs"].get(contract["narrationJob"], {})
    want = set(cw.get("sceneFunction") or [])
    excluded = data.excluded_template_ids()
    # Ground truth may name the templates allowed for this shot. Honour it.
    allowed_ids = contract["groundTruth"].get("allowedTemplateIds")
    out = []
    for t in data.approved_catalog()["afterEffects"]:
        if t["templateId"] in excluded:
            continue
        if allowed_ids and t["templateId"] not in allowed_ids:
            continue
        prof = data.ae_motion_profiles().get(t["templateId"]) or {}
        roles = prof.get("documentary_roles") or {}
        pacing = prof.get("pacing") or {}
        read = (pacing.get("usable_reading_time_s") or {})
        style = prof.get("style") or {}
        mc = t.get("mediaCompatibility") or {}
        accepts = set(mc.get("accepts") or [])
        template_carries_data = bool(accepts & {"numeric_data", "data"})
        for s in t.get("scenes", []):
            if want and s.get("function") not in want:
                continue
            sc = s.get("selectionContract") or {}
            out.append({"kind": "after_effects", "templateId": t["templateId"],
                        "sceneId": s["id"], "name": f'{t["title"]} · {s["name"]}',
                        "function": s.get("function"),
                        "focalEntityCount": s.get("focalEntityCount"),
                        "nativeDurationSeconds": sc.get("nativeDurationSeconds"),
                        "retimeAllowed": sc.get("retimeAllowed"),
                        "acceptedMedia": sc.get("acceptedMedia"),
                        "appropriateNarration": sc.get("appropriateNarration"),
                        "avoidWhen": sc.get("avoidWhen") or [],
                        "acceptedMediaTypes": sorted(accepts),
                        "hasProfile": bool(prof),
                        "documentaryRoles": {"primary": roles.get("primary") or [],
                                             "secondary": roles.get("secondary") or [],
                                             "weak": roles.get("weak") or [],
                                             "notSupported": roles.get("not_supported") or []},
                        "usableReadingTimeSeconds": read.get("median"),
                        "usableReadingTimeMin": read.get("min"),
                        "stylePace": style.get("pace"), "styleDensity": style.get("density"),
                        "narrationSuitability": (prof.get("narration") or {}).get("suitability"),
                        "capacityFits": (s.get("focalEntityCount") is None) or None,
                        "carriesData": template_carries_data or
                                       "numeric" in str(s.get("assetPresentation") or "").lower()})
    return out


# The approved template family map is a curated, user-approved routing source
# that the scene `function` axis does not reproduce. Presentation and entity
# count select the family; the family names its scenes directly.
FAMILY_BY_PRESENTATION = {
    "document": ["magazine_or_document_presentation", "screenshot_or_evidence_presentation"],
    "portrait": ["single_portrait_with_side_text", "portrait_plus_infographic"],
    "cutout":   ["single_portrait_with_side_text", "portrait_plus_infographic"],
}
FAMILY_BY_ENTITIES = {2: "two_person_portrait", 3: "three_person_portrait",
                      4: "four_or_five_slot_sequence", 5: "four_or_five_slot_sequence"}


def _family_candidates(contract):
    """Scenes named by the approved template family map for this shot."""
    # Entity count is a harder constraint than presentation: a two-entity shot
    # needs a two-person layout, whatever the passage's presentation says. So the
    # entity-matched family is listed first and scores higher on curation.
    byent = FAMILY_BY_ENTITIES.get(contract.get("focalEntityCount"))
    fams = ([byent] if byent else []) + \
           [f for f in FAMILY_BY_PRESENTATION.get(contract["groundTruth"].get("presentation"), [])
            if f != byent]
    if not fams:
        return []
    families = data.template_family_map()["families"]
    out, seen = [], set()
    for fam in fams:
        for cand in (families.get(fam) or {}).get("candidates") or []:
            name = cand if isinstance(cand, str) else cand.get("name")
            tid = cand.get("template_id") if isinstance(cand, dict) else name.split(" · ")[0]
            if not name or name in seen:
                continue
            seen.add(name)
            out.append({"kind": "after_effects", "templateId": tid, "sceneId": name,
                        "name": name, "approvedFamily": fam,
                        "familyMatchedOn": "entity_count" if fam == byent else "presentation",
                        "intents": [],
                        "capacityFits": True, "carriesData": False,
                        "designedForEntities": contract.get("focalEntityCount"),
                        "capacitySlack": 0, "showsPortraits": "portrait" in fam or "person" in fam,
                        "placedBy": f"approved family: {fam}"})
    return out


def _direct_candidates(contract):
    """Not using a template is always a candidate."""
    return [
        {"kind": "direct", "templateId": "direct:evidence_hold",
         "name": "Evidence hold with highlight", "carriesData": False, "capacityFits": True},
        {"kind": "direct", "templateId": "direct:archival_cut",
         "name": "Archival or interview cut", "carriesData": False, "capacityFits": True},
        {"kind": "direct", "templateId": "direct:text_card",
         "name": "Low-motion text card", "carriesData": False, "capacityFits": True,
         "motionActivity": "calm_readable"},
    ]


def generate(contract):
    allowed = contract["groundTruth"].get("allowedKinds") or []
    pool = []
    if not allowed or "cinematic_3d" in allowed:
        pool += _scatter_candidates(contract)
    if not allowed or "infographic" in allowed:
        pool += _infographic_candidates(contract)
    if not allowed or "after_effects" in allowed:
        pool += _ae_candidates(contract)
        pool += _family_candidates(contract)
    pool += _direct_candidates(contract)
    for c in pool:
        c["spatialPreferred"] = _spatial_first(contract) and c["kind"] == "cinematic_3d"
    return pool


def gate(candidate, contract, binding):
    """Every hard gate, evaluated. pass / fail / unknown with a reason."""
    res = {}
    n = contract["focalEntityCount"]
    strict = contract["strictestEvidenceObligation"]

    if candidate.get("capacityFits") is False:
        res["communicates_claim"] = ("fail", f"Capacity {candidate.get('capacityRange')} cannot hold {n} focal entities.")
    elif candidate.get("capacityFits") is None:
        res["communicates_claim"] = ("unknown", "Scene record has no focalEntityCount; capacity cannot be checked.")
    else:
        res["communicates_claim"] = ("pass", "Capacity admits the focal entity count.")

    needs_data = any(b["status"] == "data_required" for b in binding["bindings"])
    if needs_data and not candidate.get("carriesData"):
        res["communicates_claim"] = ("fail", "The passage carries verified values and this container encodes no data.")

    if strict == "exact_source_required" and candidate["kind"] == "direct" and "text_card" in candidate["templateId"]:
        res["evidence_specificity_honoured"] = ("pass", "Rules text is the documentary's own statement, not an external source.") \
            if contract["narrationJob"] == "evidence" and not contract["entities"] else \
            ("fail", "A text card restates a claim instead of presenting its source.")
    elif strict == "exact_source_required":
        res["evidence_specificity_honoured"] = ("pass", "Container can present the sourced values or artifact.")
    else:
        res["evidence_specificity_honoured"] = ("pass", "Obligation is below exact-source.")

    sc = contract.get("scriptConflict")
    if sc and (sc.get("desiredVisualRequires") or 0) > (sc.get("narrationSupports") or 0):
        supports = sc.get("narrationSupports")
        designed = candidate.get("designedForEntities")
        cap_hi = (candidate.get("capacityRange") or [None, None])[0]
        need = designed if designed is not None else cap_hi
        if need is not None and supports is not None and need > supports:
            res["no_unsupported_implication"] = ("fail",
                f"Container is built for {need} entities. The narration names {supports}. "
                f"Filling it would assert {need - supports} people the script never mentions.")
            return {g: {"result": res[g][0], "explanation": res[g][1]} for g in GATES if g in res}

    if binding["anyMissing"]:
        res["no_unsupported_implication"] = ("unknown",
            f"Unbound entities would have to be represented somehow: {binding['missingAssets']}.")
    else:
        res["no_unsupported_implication"] = ("pass", "Every named entity has an asset or an authored value.")

    hold = contract["timing"]["minimumReadableHoldSeconds"]
    # A template's own profile states its MEASURED usable reading time. That beats
    # both the raw scene duration and the corpus-derived floor, because scene
    # durations include shared transition handles and the usable core is shorter.
    usable = candidate.get("usableReadingTimeSeconds")
    dur = candidate.get("nativeDurationSeconds")
    if usable is not None:
        if usable < hold:
            res["evidence_legible"] = ("fail",
                f"Profile measures {usable}s of usable reading time; this shot needs {hold}s.")
        else:
            res["evidence_legible"] = ("pass",
                f"Profile measures {usable}s usable reading time against a {hold}s requirement.")
    elif dur is not None and dur < hold:
        res["evidence_legible"] = ("fail", f"Native duration {dur}s is below the {hold}s readable hold.")
    else:
        res["evidence_legible"] = ("pass", f"Duration admits the {hold}s readable hold.")

    # User ruling 2026-09-16: a role a profile marks not_supported is a FLAG that
    # forces review, never an automatic rejection. Six templates mark `quote`
    # unsupported, which is too much exclusion to apply without testing it.
    cwr = data.crosswalk()["jobs"].get(contract["narrationJob"], {}).get("documentaryRoles") or []
    dr = candidate.get("documentaryRoles")
    if dr and cwr:
        unsup = set(cwr) & set(dr["notSupported"])
        if unsup and not (set(cwr) & set(dr["primary"] + dr["secondary"])):
            candidate["roleWarning"] = {
                "unsupportedRoles": sorted(unsup), "jobNeeds": cwr,
                "source": "the template's own profile, documentary_roles.not_supported",
                "effect": "flagged and forced to review; not rejected"}

    decisive = [e for e in contract["visualEvents"] if e.get("criticality") == "decisive"]
    unresolved = [e for e in decisive if not e.get("resolved")]
    if unresolved:
        res["decisive_events_alignable"] = ("fail", f"{len(unresolved)} decisive events did not resolve to a timestamp.")
    elif candidate["kind"] == "after_effects":
        res["decisive_events_alignable"] = ("unknown",
            "Scene record carries no internal event beats, so alignment cannot be computed.")
    else:
        res["decisive_events_alignable"] = ("pass",
            f"{len(decisive)} decisive events resolved; container schedules elements to phrases.")

    part = [b for b in binding["bindings"] if b["status"] == "partially_bound"]
    res["asset_quality_sufficient"] = ("unknown", f"{len(part)} roles only partially bound.") if part \
        else ("pass", "No unbound identity roles.")

    if contract["readingLoad"] == "high" and candidate.get("motionActivity") != "calm_readable":
        if candidate["kind"] in ("after_effects", "infographic", "cinematic_3d"):
            res["not_forcing_a_template"] = ("fail",
                "Reading load is high and this container's motion activity is unrecorded or active. "
                "User rejection on this passage: scenes not made for reading.")
        else:
            res["not_forcing_a_template"] = ("pass", "Direct treatment.")
    else:
        res["not_forcing_a_template"] = ("pass", "No stronger direct treatment is being displaced.")

    lo, hi = candidate.get("capacityRange", [None, None])
    if hi and n and hi > n * 3:
        res["density_acceptable"] = ("unknown", f"Container holds up to {hi} but the passage has {n}; portrait legibility at capacity is unrecorded.")
    else:
        res["density_acceptable"] = ("pass", "Density proportionate to the entity count.")

    pf = presentation_fit(candidate, contract)
    if pf is not None and pf <= 0.2:
        res["communicates_claim"] = ("fail",
            f"Ground truth records presentation '{contract['groundTruth'].get('presentation')}'; "
            f"this container serves it poorly.")

    # COR-0003: hard gate. Fail when a bound asset contradicts the era; unknown
    # while unbound, because an era cannot be checked before an asset exists.
    # Era evidence comes from assertedYears, collected from tags, filenames and
    # source paths. Never from image dimensions or asset ids.
    eras = [(r["roleId"], r["eraConstraint"]) for r in contract["requiredMedia"]
            if r.get("eraConstraint")]
    if not eras:
        res["era_consistent"] = ("pass", "No era constraint recorded.")
    else:
        conflicts, checkable = [], False
        for role_id, era in eras:
            bd = next((x for x in binding["bindings"] if x["roleId"] == role_id), None)
            if not bd or bd["status"] in ("missing", "data_required"):
                continue
            want = set(re.findall(r"(?:19|20)\d{2}", str(era)))
            seen = set()
            for summary in (list(bd.get("perEntity", {}).values())
                            + list(bd.get("artifacts", {}).values())):
                seen |= set(summary.get("assertedYears") or [])
            if not want or not seen:
                continue
            checkable = True
            if not (want & seen):
                conflicts.append(f"{role_id}: needs {era}, bound assets assert {sorted(seen)}")
        if conflicts:
            res["era_consistent"] = ("fail", "; ".join(conflicts))
        elif checkable:
            res["era_consistent"] = ("pass", "Bound assets assert a year inside the constraint.")
        else:
            res["era_consistent"] = ("unknown",
                f"Era constraints {[e for _, e in eras]} cannot be confirmed: "
                f"no asset asserts a year yet.")

    return {g: {"result": res[g][0], "explanation": res[g][1]} for g in GATES if g in res}


def score(candidate, contract, gates):
    n = contract["focalEntityCount"]
    # Timing alignment is priority 1, so any deduction here is decisive under
    # lexicographic comparison. An UNKNOWN must not be scored worse than a PASS:
    # every After Effects scene reports unknown because no scene record carries
    # internal event beats, which would make them structurally unable to ever win.
    # The uncertainty is carried by the decision, which escalates on unknowns.
    _al = gates.get("decisive_events_alignable", {}).get("result")
    align = 0.0 if _al == "fail" else 1.0
    # Claim communication asks whether the viewer gets the takeaway. The recorded
    # presentation is a structural property and is applied in structuralFit only.
    comm = 1.0 if gates.get("communicates_claim", {}).get("result") == "pass" else \
           (0.5 if gates.get("communicates_claim", {}).get("result") == "unknown" else 0.0)
    fact = 1.0 if not contract["requiredMedia"] else \
           (0.6 if gates.get("no_unsupported_implication", {}).get("result") == "unknown" else 1.0)
    capacity = 1.0 if candidate.get("capacityFits") else (0.4 if candidate.get("capacityFits") is None else 0.0)
    cw = data.crosswalk()["jobs"].get(contract["narrationJob"], {})
    want = set(cw.get("infographicIntents", []) + cw.get("scatterIntents", []))
    # Entity count modulates the job. Quantifying ONE thing and quantifying seven
    # named things side by side are different visual jobs: the second is inherently
    # comparative whatever the case file calls it. Passage 18 lists seven artists
    # with values and sums them, and is recorded as quantify.
    if (contract.get("focalEntityCount") or 0) >= 3 and contract["narrationJob"] in ("quantify", "timeline", "sequence"):
        cmp_cw = data.crosswalk()["jobs"].get("compare", {})
        want |= set(cmp_cw.get("infographicIntents", []) + cmp_cw.get("scatterIntents", []))
        want |= {"rank", "leaderboard"}
    have = set(candidate.get("intents") or [])
    overlap = len(want & have)
    if candidate.get("approvedFamily"):
        # The family map is the user's own statement of what serves this job.
        # A curated candidate carries full intent fit rather than the no-tags default.
        intent_fit = 1.0
    elif not have:
        intent_fit = 0.55
    elif overlap == 0:
        intent_fit = 0.40
    elif overlap == 1:
        intent_fit = 0.92
    else:
        intent_fit = 1.0
    pf = presentation_fit(candidate, contract)
    pf = 0.7 if pf is None else pf
    # Declared intent is the stronger structural signal; the recorded presentation
    # weights it rather than overriding it.
    struct = round(capacity * (0.62 * intent_fit + 0.38 * pf), 3)

    # Portrait legibility: a layout designed for many faces renders each one small,
    # whatever you put in it. Prefer the tightest fit that still holds the entities.
    # User ruling on passage 14: "nice size portraits given that were only talking
    # about a handful of artists."
    # A portrait requirement is carried by the media family, not by the editorial
    # role. Passage 07 needs portraits under a "subject" role, passage 14 under
    # "identity"; both are portrait passages.
    needs_portraits = any(r.get("mediaFamily") == "portrait_still"
                          for r in contract["requiredMedia"])
    if needs_portraits and candidate.get("showsPortraits") is False:
        struct = round(struct * 0.6, 3)
        candidate["portraitFit"] = "layout shows no portraits but the contract needs them"
    if candidate.get("showsPortraits") and candidate.get("capacitySlack") is not None:
        slack = candidate["capacitySlack"]
        if slack < 0:
            fit = 0.0                       # cannot hold them at all
        elif slack == 0:
            fit = 1.0                       # exact fit, largest faces
        else:
            fit = max(0.35, 1.0 - 0.09 * slack)
        struct = round(struct * fit, 3)
        candidate["portraitFit"] = round(fit, 2)
    style = 0.75
    if candidate.get("spatialPreferred"):
        style = min(1.0, style + 0.2)
    asset = 0.4 if contract["requiredMedia"] and any(
        b["status"] in ("missing", "partially_bound") for b in []) else 0.7
    return {"timingAlignment": round(align, 2), "claimCommunication": round(comm, 2),
            "factualAccuracy": round(fact, 2), "structuralFit": round(struct, 2),
            "styleConsistency": round(style, 2), "assetQuality": asset,
            "polish": 0.7, "renderCost": 0.8 if candidate["kind"] != "cinematic_3d" else 0.5,
            "curation": (1.0 if candidate.get("familyMatchedOn") == "entity_count"
                         else 0.9 if candidate.get("approvedFamily") else 0.0)}


def rank(cands):
    return sorted(cands, key=lambda c: tuple(-c["scores"][p] for p in PRIORITY))


def build_slate(contract, binding, size=4):
    pool = generate(contract)
    evaluated = []
    for c in pool:
        g = gate(c, contract, binding)
        c = dict(c)
        c["gateResults"] = g
        c["scores"] = score(c, contract, g)
        c["hardFail"] = [k for k, v in g.items() if v["result"] == "fail"]
        c["unknowns"] = [k for k, v in g.items() if v["result"] == "unknown"]
        if c.get("roleWarning"):
            c["unknowns"] = sorted(set(c["unknowns"]) | {"documentary_role_unsupported"})
        sr = schedule_replacement_status(c, contract)
        if sr:
            c["scheduleReplacement"] = sr
            if not sr["proven"]:
                c["unknowns"] = sorted(set(c["unknowns"]) | {"schedule_replacement_unproven"})
        evaluated.append(c)

    viable = [c for c in evaluated if not c["hardFail"]]
    rejected = [c for c in evaluated if c["hardFail"]]
    ranked = rank(viable)

    # spatial_relationship_first: when the rule fires, gate-passing spatial
    # candidates are placed before ordinary comparison charts. It changes
    # precedence, never gate outcomes.
    slate, seen = [], set()
    if _spatial_first(contract):
        for c in ranked:
            if c["kind"] == "cinematic_3d" and c["templateId"] not in seen:
                c["placedBy"] = "spatial_relationship_first"
                slate.append(c); seen.add(c["templateId"])
                break

    # four_distinct_options asks for four different template IDs. When the ground
    # truth restricts the shot to fewer templates than that, the letter of the rule
    # is unsatisfiable, so distinctness falls back to different scenes inside the
    # allowed template. The intent, four real choices, is preserved.
    allowed_ids = contract["groundTruth"].get("allowedTemplateIds") or []
    scene_level = 0 < len(allowed_ids) < size
    for c in ranked:
        key = c.get("sceneId") or c["templateId"] if scene_level else c["templateId"]
        if key in seen:
            continue
        seen.add(key)
        c.setdefault("placedBy", "rank" if not scene_level else "rank (scene-level distinctness)")
        slate.append(c)
        if len(slate) == size:
            break

    # include_infographic when infographics are allowed for the shot
    allowed = contract["groundTruth"].get("allowedKinds") or []
    if (not allowed or "infographic" in allowed) and not any(c["kind"] == "infographic" for c in slate):
        for c in ranked:
            if c["kind"] == "infographic" and c["templateId"] not in seen:
                if slate:
                    slate[-1] = c
                else:
                    slate.append(c)
                seen.add(c["templateId"])
                break

    for i, c in enumerate(slate, 1):
        c["rank"] = i
    return {"slate": slate, "viableCount": len(viable),
            "spatialFirstDetail": _spatial_first(contract, detail=True),
            "ruleProvenance": rules.provenance(),
            "rejectedCount": len(rejected), "poolSize": len(evaluated),
            "rejectedSample": sorted(rejected, key=lambda c: c["name"] or "")[:6],
            "spatialFirstApplied": _spatial_first(contract)}
