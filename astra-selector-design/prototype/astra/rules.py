"""Active rule resolution: project snapshot plus local overlay.

Nothing here reads the live project rules or writes to them. The base snapshot
is a local read-only copy; the overlay holds locally approved corrections and is
capped at project scope. Setting a correction's status to anything but "active"
reverts it, and the base rule applies again.
"""
import json, os, re, functools

RULES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "rules")

BASE_TRIGGERS = {
    "spatial_relationship_first":
        r"\b(gap|distance|overlap|outlier|fall[s]?|falling|drop[s]?|rank|apart|"
        r"ahead|behind|above|below|further|farther)\b",
}


@functools.lru_cache(maxsize=None)
def base():
    with open(os.path.join(RULES_DIR, "base-rules.snapshot.json")) as f:
        snap = json.load(f)
    return {r["id"]: {"rule": r["rule"], "version": "1.0.0-project",
                      "trigger": BASE_TRIGGERS.get(r["id"])}
            for r in snap["rules"]}


@functools.lru_cache(maxsize=None)
def overlay():
    path = os.path.join(RULES_DIR, "local-overlay.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)["corrections"]


@functools.lru_cache(maxsize=None)
def active():
    """Base rules with any active local correction applied on top."""
    out = dict(base())
    for cor in overlay():
        if cor.get("status") != "active":
            continue
        ar = cor["activeRule"]
        rid = ar["ruleId"]
        if rid not in out:
            out[rid] = {}
        out[rid] = {"rule": cor["proposedPromotion"]["proposedRule"],
                    "version": ar["version"],
                    "trigger": ar.get("triggerPattern"),
                    "baseTrigger": BASE_TRIGGERS.get(rid),
                    "correctionId": cor["correctionId"],
                    "scope": cor["scope"]["assertedScope"]}
    return out


def matches(rule_id, text):
    """Does `text` trigger this rule? Returns (bool, matched terms, source)."""
    r = active().get(rule_id)
    if not r:
        return False, [], "unknown rule"
    pats = [p for p in (r.get("baseTrigger"), r.get("trigger")) if p]
    if not pats:
        pats = [BASE_TRIGGERS.get(rule_id)] if BASE_TRIGGERS.get(rule_id) else []
    hits, source = [], None
    for p in pats:
        found = sorted({m.group(0).lower() for m in re.finditer(p, text, re.I)})
        if found:
            hits += found
            source = "base" if p == r.get("baseTrigger") and source is None else (source or "overlay")
    return bool(hits), sorted(set(hits)), (source or "none")


def provenance():
    return {"baseRuleCount": len(base()),
            "activeCorrections": [c["correctionId"] for c in overlay() if c.get("status") == "active"],
            "revertedCorrections": [c["correctionId"] for c in overlay() if c.get("status") != "active"],
            "maximumScope": "project",
            "writesToProject": False}
