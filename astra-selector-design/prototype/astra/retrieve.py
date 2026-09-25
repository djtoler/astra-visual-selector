"""Bind media roles to real assets, or name what is missing.

Local Media Library first, per answer 17_asset_sourcing_order. Nothing weak is
ever substituted: a role that cannot be filled is reported as missing with the
exact thing that has to be found.
"""
import re
from . import data
from .data import MEDIA

CUTOUT_HINT = re.compile(r"cutout", re.I)

# A claim the documentary itself makes (its own editorial rule, its own stated
# test) can legitimately be authored. Anything about the outside world cannot.
SELF_SOURCED = re.compile(
    r"documentary'?s? own|the documentary'?s? stated|own stated editorial|"
    r"stated editorial rule|our own|the script'?s own", re.I)


def _blob(rec):
    parts = [str(rec.get("embedding_text") or ""),
             " ".join(str(t) for t in (rec.get("tags") or [])),
             str(rec.get("canonical_path") or "")]
    for ing in rec.get("ingestions") or []:
        parts += [str(ing.get("source_path") or ""), str(ing.get("project") or ""),
                  str(ing.get("original_filename") or "")]
    parts.append(str(rec.get("derivatives") or ""))
    return " ".join(parts)


def find(term):
    pat = re.compile(re.escape(term).replace(r"\ ", r"[\s\-_]*"), re.I)
    return [r for r in data.assets() if pat.search(_blob(r))]


YEAR = re.compile(r"\b(19[5-9]\d|20[0-4]\d)\b")


def _years(rec):
    """Years asserted by an asset's own metadata. Dimensions and ids are excluded."""
    parts = [" ".join(str(t) for t in (rec.get("tags") or []))]
    for ing in rec.get("ingestions") or []:
        parts += [str(ing.get("source_path") or ""), str(ing.get("original_filename") or ""),
                  str(ing.get("project") or "")]
    return set(YEAR.findall(" ".join(parts)))


def _summarise(recs):
    out = {"count": len(recs), "image": 0, "video": 0, "cutout": 0, "examples": []}
    for r in recs:
        out[r.get("media_type", "image")] = out.get(r.get("media_type", "image"), 0) + 1
        if CUTOUT_HINT.search(_blob(r)):
            out["cutout"] += 1
    years = set()
    for r in recs:
        years |= _years(r)
    out["assertedYears"] = sorted(years)
    for r in recs[:3]:
        out["examples"].append({"assetId": r["asset_id"], "type": r.get("media_type"),
                                "dimensions": f'{r.get("width")}x{r.get("height")}'})
    return out


def bind_role(role, entities, claims=None):
    """Return a binding record for one required media role."""
    names = role.get("entityNames")
    if names is None:
        names = [e["name"] for e in entities] if role.get("editorialRole") in ("identity", "subject") else []

    per_entity, missing = {}, []
    for n in names:
        hits = find(n)
        per_entity[n] = _summarise(hits)
        if not hits:
            missing.append(n)

    # Roles that need a specific artifact rather than a person
    artifact_terms = []
    cr = (role.get("contentRequirement") or "")
    for m in re.finditer(r"\b(XXL|Freshman|So Far Gone|ICEMAN|HABIBTI)\b", cr):
        artifact_terms.append(m.group(1))
    artifacts = {t: _summarise(find(t)) for t in set(artifact_terms)}
    missing += [t for t, s in artifacts.items() if s["count"] == 0]

    needs_data = role.get("mediaFamily") == "data_or_number"
    # sourceCandidates live on the claims per the contract schema, so consult both.
    cand_text = " ".join(role.get("sourceCandidates") or [])
    for cl in (claims or []):
        cand_text += " " + " ".join(cl.get("sourceCandidates") or [])
    self_sourced = bool(SELF_SOURCED.search(cand_text))

    status = "bound_local"
    if needs_data:
        status = "data_required"
    elif missing:
        status = "missing" if len(missing) == len(names or [1]) else "partially_bound"
    elif not names and not artifacts:
        # An exact-source proof role about the outside world can never be authored.
        if role.get("sourceSpecificity") == "exact_source_required" and not self_sourced:
            status = "missing"
            missing.append(f'a source for {role["roleId"]}')
        else:
            status = "generated_or_authored"

    # Citation ruling 2026-09-16: record the source for every proof role.
    # Never used to filter a container; recorded so the handoff can carry it.
    if needs_data:
        provenance, source_ref = "unknown", "verified dataset, not yet bound"
    elif status in ("bound_local", "partially_bound"):
        provenance, source_ref = "media_library", MEDIA
    elif status == "generated_or_authored":
        provenance, source_ref = "generated", "authored from the documentary's own stated rule"
    elif status == "missing":
        provenance, source_ref = "unknown", "NOT YET SOURCED"
    else:
        provenance, source_ref = "unknown", None

    return {"roleId": role["roleId"],
            "attributionPolicy": "record_only",
            "provenance": provenance,
            "sourceRef": source_ref,
            "sourceCandidates": role.get("sourceCandidates"),
            "editorialRole": role["editorialRole"],
            "sourceSpecificity": role["sourceSpecificity"],
            "mediaFamily": role.get("mediaFamily"),
            "status": status,
            "perEntity": per_entity,
            "artifacts": artifacts,
            "missing": sorted(set(missing)),
            "note": ("Values must come from the verified dataset, not the Media Library."
                     if needs_data else None)}


def bind(contract):
    bindings = [bind_role(r, contract["entities"], contract.get("claims"))
                for r in contract["requiredMedia"]]
    missing = sorted({m for b in bindings for m in b["missing"]})
    return {"bindings": bindings,
            "evidenceSources": [{"roleId": b["roleId"], "provenance": b["provenance"],
                                 "sourceRef": b["sourceRef"], "onScreenCredit": False}
                                for b in bindings if b["editorialRole"] == "proof"],
            "missingAssets": missing,
            "anyMissing": bool(missing),
            "dataRolesOutstanding": [b["roleId"] for b in bindings if b["status"] == "data_required"]}
