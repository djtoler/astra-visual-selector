#!/usr/bin/env python3
"""Run the vertical slice: contract -> retrieval -> slate -> gates -> decision.

Emits JSON per passage plus one readable report. Renders nothing.
"""
import json, os, re, sys
from astra import contract, retrieve, select, data, rules

SLICE = [f"{i:02d}" for i in range(1, 31)]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# Some desired outcomes name a treatment KIND ("inside an AE scene", "artist
# cutout") rather than a layout. Those are satisfied by the matching approved
# template family, whose scenes are named by pack and scene number.
DESIRED_FAMILY = {
    "02": ["magazine_or_document_presentation"],
    "05": ["single_portrait_with_side_text", "portrait_plus_infographic"],
    "10": ["single_portrait_with_side_text", "portrait_plus_infographic"],
    "15": ["magazine_or_document_presentation", "screenshot_or_evidence_presentation"],
    "16": ["magazine_or_document_presentation"],
    "21": ["three_person_portrait"],
    "25": ["two_person_portrait"],
    "29": ["single_portrait_with_side_text", "two_person_portrait"],
}

# Best reading of each case's recorded `desired` outcome, refined by the layouts
# the user named in feedback. Feedback wins where the two differ.
DESIRED_PATTERN = {
    "01": r"counter",
    "02": r"two-point|duration ratio|magazine|document|evidence hold|chronological ledger",
    "04": r"outlier|population field",
    "05": r"portrait|introduction|single-subject|cutout",
    "06": r"chronological ledger",
    "08": r"ledger|table|list|catalog|criteria",
    "09": r"portrait|distribution|metric|value cards|panels",
    "11": r"chronological ledger",
    "13": r"portrait directory|chronological ledger|portrait scatter|dense portrait",
    "16": r"magazine|document|slideshow|history|archive|plate",
    "18": r"photo panels|seven-entry leaderboard",
    "19": r"leaderboard|criteria|four-stage",
    "20": r"outlier|population|two-point|scatter",
    "21": r"three|portrait",
    "22": r"portrait|leaderboard|value|panel",
    "23": r"archival|documentary|slideshow|history|evidence|promo",
    "25": r"cohort attrition|portrait metric matrix|population field|relationship b-roll|two-portrait|two portrait",
    "26": r"table|tier|criteria|ledger|classification",
    "27": r"portrait columns|portrait|paired",
    "28": r"radial|two-portrait",
    "29": r"two-portrait|two portrait",
    "03": r"population field|one-dot-per-entity|outlier",
    "07": r"portrait-topped|people-and-resources|leaderboard|criteria|portrait|magnitude",
    "10": r"chronological ledger",
    "30": r"__refusal_expected__",
    "12": r"rank[- ]loss|before[- ]and[- ]after",
    "14": r"portrait value cards|magnitude bars|portrait columns|pairwise|criteria tables",
    "15": r"evidence hold|document|archival|magazine",
    "17": r"text card",
    "24": r"cohort attrition|attrition",
}


def shots_for(contract):
    """Split a contract into per-shot sub-contracts.

    The project's planningRule is explicit: "Select and validate a template
    independently for each planned shot." A shot inherits the passage's claims
    and prohibitions but carries only its own events and media roles.
    """
    ids = sorted({e.get("shotId") for e in contract["visualEvents"] if e.get("shotId")} |
                 {r.get("shotId") for r in contract["requiredMedia"] if r.get("shotId")})
    if not ids:
        return [("01", contract)]
    order = ["exact_source_required", "exact_event_or_entity_required",
             "representative_media_allowed", "decorative_media_allowed"]
    recorded = {sh["shotId"]: sh for sh in contract["timing"]["recordedShots"]}
    out = []
    for sid in ids:
        sub = dict(contract)
        sub["shotId"] = sid
        sub["visualEvents"] = [e for e in contract["visualEvents"] if e.get("shotId") == sid]
        sub["requiredMedia"] = [r for r in contract["requiredMedia"] if r.get("shotId") == sid] \
            or contract["requiredMedia"]
        names = {n for r in sub["requiredMedia"] for n in (r.get("entityNames") or [])}
        sub["focalEntityCount"] = len(names) if names else contract["focalEntityCount"]
        specs = [r.get("sourceSpecificity") for r in sub["requiredMedia"] if r.get("sourceSpecificity")]
        if specs:
            sub["strictestEvidenceObligation"] = min(specs, key=lambda x: order.index(x)
                                                     if x in order else 9)
        sub["shotBoundary"] = "measured" if sid in recorded else "proposed"
        # A split passage can carry shots with different JOBS, not only different
        # presentations. The passage-level job describes the whole; a shot may do
        # something else. Same reasoning as the approved per-shot presentation rule.
        seed_shots = {x["shotId"]: x for x in
                      (contract.get("proposedDecomposition") or {}).get("shots") or []}
        if seed_shots.get(sid, {}).get("job"):
            sub["narrationJob"] = seed_shots[sid]["job"]
            sub["jobSource"] = "shot-level override"
        sh = recorded.get(sid)
        if sh:
            t = dict(contract["timing"])
            t["audioStartSeconds"] = sh["startSeconds"]
            t["audioEndSeconds"] = sh["endSeconds"]
            t["audioDurationSeconds"] = sh["durationSeconds"]
            sub["timing"] = t
        out.append((sid, sub))
    return out


def decide(c, binding, slate_info):
    slate = slate_info["slate"]
    triggers, reasons = [], []
    sc = c.get("scriptConflict")
    if sc:
        triggers.append("script_conflict")
        reasons.append(f'{sc["conflict"]} {sc["resolution"]}')
    if binding["anyMissing"]:
        triggers.append("assets_missing")
        reasons.append(f"Unbound: {', '.join(binding['missingAssets'])}.")
    if binding["dataRolesOutstanding"]:
        triggers.append("evidence_insufficient")
        reasons.append(f"Verified values still required for: {', '.join(binding['dataRolesOutstanding'])}.")
    if c["timing"]["durationPolicy"]["extensionRequired"]:
        e = c["timing"]["durationPolicy"]["extensionRequired"][0]
        reasons.append(f"Shot {e['shotId']} must extend {e['shortfallSeconds']}s so {e['roleId']} can complete.")
    if len(slate) >= 2:
        a = [slate[0]["scores"][p] for p in select.PRIORITY]
        b = [slate[1]["scores"][p] for p in select.PRIORITY]
        if a == b:
            triggers.append("candidates_close")
            reasons.append("Top two candidates are tied on every priority level.")
    if any(s["unknowns"] for s in slate[:1]):
        triggers.append("low_confidence")
        reasons.append(f"Winner has unresolved gates: {', '.join(slate[0]['unknowns'])}.")
    if len(slate) < 4:
        reasons.append(f"Only {len(slate)} meaningfully different valid treatments exist; the slate is not padded.")

    action = "require_user_review" if triggers else "auto_advance"
    if "assets_missing" in triggers or "evidence_insufficient" in triggers:
        action = "blocked_missing_assets"
    if "script_conflict" in triggers:
        action = "blocked_script_conflict"
    return {"action": action,
            "winnerRank": 1 if slate else None,
            "confidence": {"value": None, "method": "uncalibrated_prior",
                           "calibrationSampleSize": 0,
                           "note": "Auto-advance disabled by policy until calibrated against approved and rejected decisions."},
            "escalationTriggers": sorted(set(triggers)),
            "reasons": reasons}


def run(pid):
    c = contract.build(pid)
    shots = []
    for sid, sub in shots_for(c):
        sb = retrieve.bind(sub)
        ss = select.build_slate(sub, sb)
        shots.append({"shotId": sid, "boundary": sub.get("shotBoundary", "measured"),
                      "focalEntityCount": sub["focalEntityCount"],
                      "durationSeconds": sub["timing"]["audioDurationSeconds"],
                      "events": [e["eventId"] for e in sub["visualEvents"]],
                      "binding": sb, "slate": ss})
    b = retrieve.bind(c)
    # The passage-level slate is the first shot's, kept for the summary view.
    s = shots[0]["slate"]
    d = decide(c, b, s)
    d["shotCount"] = len(shots)
    all_names = [str(x["name"]) for sh in shots for x in sh["slate"]["slate"]]
    expect_refusal = DESIRED_PATTERN[pid] == r"__refusal_expected__"
    if expect_refusal:
        refused = d["action"] == "blocked_script_conflict"
        gt = {"desired": c["groundTruth"]["desired"], "successCriterion": "refusal",
              "desiredInSlate": refused, "desiredAtRank": 1 if refused else None,
              "refused": refused, "recordedFallback": c["groundTruth"]["fallback"]}
        return {"ruleProvenance": rules.provenance(), "shots": shots, "contract": c,
                "binding": b, "slate": s, "decision": d, "groundTruthCheck": gt}
    pat = re.compile(DESIRED_PATTERN[pid], re.I)
    fams = set(DESIRED_FAMILY.get(pid, []))
    # A multi-shot passage satisfies its desired outcome if ANY shot's slate holds it.
    ranks = []
    for sh in shots:
        for x in sh["slate"]["slate"]:
            if pat.search(str(x["name"])) or (x.get("approvedFamily") in fams):
                ranks.append(x["rank"])
    return {"ruleProvenance": rules.provenance(), "shots": shots,
            "contract": c, "binding": b, "slate": s, "decision": d,
            "groundTruthCheck": {"desired": c["groundTruth"]["desired"],
                                 "desiredInSlate": bool(ranks),
                                 "desiredAtRank": ranks[0] if ranks else None,
                                 "recordedFallback": c["groundTruth"]["fallback"]}}


def main():
    os.makedirs(OUT, exist_ok=True)
    results = {}
    for pid in SLICE:
        results[pid] = run(pid)
        with open(os.path.join(OUT, f"passage-{pid}.json"), "w") as f:
            json.dump(results[pid], f, indent=1)

    lines = ["# Vertical slice — five passages, end to end", "",
             "Contract, retrieval, four-candidate slate, gates, decision. Nothing rendered.",
             "Every timing value is measured from the aligned audio. Claims, media roles and",
             "events are authored and marked as such in each contract's `provenance` block.", ""]
    cov = sum(1 for r in results.values() if r["groundTruthCheck"]["desiredInSlate"])
    top = sum(1 for r in results.values() if r["groundTruthCheck"]["desiredAtRank"] == 1)
    refusals = [p for p, r in results.items() if r["decision"]["action"] == "blocked_script_conflict"]
    import re as _re
    _base = json.load(open(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "data/approved-candidates-per-passage.json")))
    def _n(x): return _re.sub(r"[^a-z0-9]+", " ", str(x).lower()).strip()
    agree = 0
    for _pid, _r in results.items():
        _mine = {_n(x["name"]) for sh in _r.get("shots", []) for x in sh["slate"]["slate"]}
        if _mine & {_n(n) for n in _base.get(_pid, [])}:
            agree += 1
    prov = rules.provenance()
    lines += [f"**Slate coverage {cov}/{len(SLICE)}. Desired outcome ranked first in {top}/{len(SLICE)}.**", "",
              f'Rules: {prov["baseRuleCount"]} from the project snapshot, '
              f'{len(prov["activeCorrections"])} active local correction'
              f'{"" if len(prov["activeCorrections"]) == 1 else "s"} '
              f'({", ".join(prov["activeCorrections"]) or "none"}). '
              f'Maximum scope {prov["maximumScope"]}; nothing is written to the project.', "",
              f'**Agreement with the prior selector: {agree}/{len(SLICE)}.** That compares against the literal '
              f'candidate lists in `year-seventeen-30-selector-results.md` rather than a reading of each '
              f'`desired` sentence. Neither number alone is the score: the user corrected the prior selector '
              f'on several passages, so diverging from it is sometimes right.', "",
              "| Passage | Job | Audio | Events resolved | Slate | Desired at | Decision |",
              "|---|---|---|---|---|---|---|"]
    for pid, r in results.items():
        c, s, d = r["contract"], r["slate"], r["decision"]
        ev = c["visualEvents"]
        res = sum(1 for e in ev if e.get("resolved"))
        lines.append(f'| {pid} {c["scriptRef"]["sectionId"]} | {c["narrationJob"]} | '
                     f'{c["timing"]["audioDurationSeconds"]}s | {res}/{len(ev)} | '
                     f'{len(s["slate"])} | {r["groundTruthCheck"]["desiredAtRank"] or "not in slate"} | '
                     f'{d["action"]} |')
    lines.append("")

    for pid, r in results.items():
        c, b, s, d = r["contract"], r["binding"], r["slate"], r["decision"]
        lines += [f'## Passage {pid} — {c["scriptRef"]["sectionId"]}', "",
                  f'> {c["narration"]["text"]}', "",
                  f'**Job** {c["narrationJob"]} · **Takeaway** {c["takeaway"]}', "",
                  f'**Audio** {c["timing"]["audioStartSeconds"]}–{c["timing"]["audioEndSeconds"]}s '
                  f'({c["timing"]["audioDurationSeconds"]}s, alignment coverage '
                  f'{c["timing"]["wordAlignmentCoverage"]}) · '
                  f'**Strictest obligation** {c["strictestEvidenceObligation"]}', "",
                  "### Phrase-aligned events", "",
                  "| Event | Trigger phrase | Measured offset | Match | Criticality |",
                  "|---|---|---|---|---|"]
        for e in c["visualEvents"]:
            if e.get("resolved"):
                lines.append(f'| {e["eventId"]} | "{e["triggerPhrase"]}" | +{e["triggerOffsetSeconds"]}s | '
                             f'{e["matchConfidence"]} | {e["criticality"]} |')
            else:
                lines.append(f'| {e["eventId"]} | "{e["triggerPhrase"]}" | unresolved | — | {e["criticality"]} |')
        dp = c["timing"]["durationPolicy"]
        lines += ["", f'**Duration policy** {dp["mode"]}, evidence must complete. ']
        if dp["extensionRequired"]:
            for e in dp["extensionRequired"]:
                lines.append(f'Shot {e["shotId"]} holds {e["availableSeconds"]}s but {e["roleId"]} '
                             f'needs {e["needsSeconds"]}s. **Extend by {e["shortfallSeconds"]}s; narration yields.**')
        else:
            lines.append("No extension required.")

        lines += ["", "### Media roles", "", "| Role | Editorial role | Specificity | Status | Missing |", "|---|---|---|---|---|"]
        for bd in b["bindings"]:
            lines.append(f'| {bd["roleId"]} | {bd["editorialRole"]} | {bd["sourceSpecificity"]} | '
                         f'{bd["status"]} | {", ".join(bd["missing"]) or "—"} |')

        sd = s["spatialFirstDetail"]
        spatial = (f' · spatial_relationship_first fired via **{sd["triggerSource"]}** rule '
                   f'{sd["ruleVersion"]} on {", ".join(sd["terms"])}') if sd["fired"] else ""
        lines += ["", f'### Candidates — {s["viableCount"]} viable of {s["poolSize"]}, '
                      f'{s["rejectedCount"]} gate-rejected{spatial}', "",
                  "| Rank | Kind | Container | Placed by | Unresolved gates |", "|---|---|---|---|---|"]
        for cand in s["slate"]:
            lines.append(f'| {cand["rank"]} | {cand["kind"]} | {cand["name"]} | '
                         f'{cand.get("placedBy", "rank")} | '
                         f'{", ".join(cand["unknowns"]) or "none"} |')

        if b.get("evidenceSources"):
            lines += ["", "### Evidence sources recorded", "",
                      "Source recorded for every proof role. On-screen credit is an editorial choice per scene, never a gate.", "",
                      "| Role | Provenance | Source | On-screen credit |", "|---|---|---|---|"]
            for esrc in b["evidenceSources"]:
                lines.append(f'| {esrc["roleId"]} | {esrc["provenance"]} | {esrc["sourceRef"] or "—"} | '
                             f'{"yes" if esrc["onScreenCredit"] else "editorial choice"} |')
        lines += ["", f'**Decision** `{d["action"]}` · confidence `{d["confidence"]["method"]}`', ""]
        for reason in d["reasons"]:
            lines.append(f'- {reason}')
        lines += ["", f'**Ground truth** desired: _{r["groundTruthCheck"]["desired"]}_ — '
                      f'{"in slate at rank " + str(r["groundTruthCheck"]["desiredAtRank"]) if r["groundTruthCheck"]["desiredInSlate"] else "NOT IN SLATE"}. '
                      f'Recorded fallback: _{r["groundTruthCheck"]["recordedFallback"]}_.', ""]

    with open(os.path.join(OUT, "SLICE-REPORT.md"), "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUT}/SLICE-REPORT.md and {len(results)} passage JSON files")
    print(f"slate coverage {cov}/{len(SLICE)}, desired ranked first {top}/{len(SLICE)}"
          + (f", refused on script conflict: {refusals}" if refusals else ""))


if __name__ == "__main__":
    main()
