#!/usr/bin/env python3
"""Match existing templates and Production Ready media independently per VisualTask."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "match-trial"))
sys.path.insert(0, str(ROOT / "pipeline"))

import candidates as C  # noqa: E402
import media_candidates as M  # noqa: E402
from matching_contract_gate import enforce_contracts  # noqa: E402

DEFAULT_TASKS = ROOT / "grammar" / "visual-tasks.json"
DEFAULT_BINDINGS = ROOT / "grammar" / "bindings.json"
DEFAULT_OUTPUT = ROOT / "reports" / "visualtask-match-pilot-28-28.json"


OPERATION_PRIORITY = (
    "lyric_presentation", "transformation", "relationship_intro",
    "evidence_presentation", "comparison", "data_explanation", "item_sequence",
    "subject_profile", "milestone_reveal", "archival_progression",
    "event_narration", "rhetorical_question", "concept_statement",
)

DATA_CARRIES = frozenset({
    "magnitude", "difference", "rank", "change_over_time", "parity",
    "share_of_whole", "derivation", "aggregate", "absence", "overlap",
})


def _operation_text(record: dict[str, Any]) -> str:
    capability = record.get("capability") or {}
    parts = [
        record.get("title"), record.get("description"), record.get("useWhen"),
        capability.get("asserts"), capability.get("structure"), capability.get("staging"),
        " ".join(capability.get("carries") or []),
    ]
    return " ".join(str(part) for part in parts if part).lower()


def presentation_contract(task: dict[str, Any]) -> dict[str, Any]:
    """Return a template-neutral communication contract for one exact task."""
    supplied_operations = list(dict.fromkeys(task.get("presentationOperations") or ["concept_statement"]))
    operations = [op for op in OPERATION_PRIORITY if op in supplied_operations]
    operations.extend(op for op in supplied_operations if op not in operations)
    entity_count = int(task.get("entityCount") or 0)
    values = task.get("values") or []
    cohorts = task.get("cohortRefs") or []
    obligations = task.get("obligations") or []
    quote = str(task.get("quote") or "")
    needs_text = bool(
        task.get("taskRole") == "attributed_quote" or
        any(row.get("needsOnScreenText") for row in obligations)
    )
    quantitative = bool(values or cohorts or re.search(
        r"\b(?:\d+(?:\.\d+)?|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|percent|percentage|half|double|triple)\b",
        quote.lower(),
    ))
    supplied_primary = task.get("primaryPresentationOperation")
    if supplied_primary and supplied_primary not in operations:
        raise ValueError(f"primary presentation operation is not in task operations: {supplied_primary}")
    primary = supplied_primary or next((op for op in OPERATION_PRIORITY if op in operations), operations[0])
    lowered_quote = quote.lower()
    evidence_kind = None
    if any(term in lowered_quote for term in (
        "track list", "tracklist", "article", "headline", "wikipedia", "reddit",
        "critics", "mockery", "reviewers",
    )):
        evidence_kind = "document_screen"
    elif any(term in lowered_quote for term in ("interview", "footage", "you just heard")):
        evidence_kind = "source_footage_or_document"
    return {
        "operations": operations,
        "primaryOperation": primary,
        "entityCount": entity_count,
        "hasCohort": bool(cohorts),
        "hasTypedValues": bool(values),
        "quantitativeClaim": quantitative,
        "evidenceKind": evidence_kind,
        "needsOnScreenText": needs_text,
        "mustBePerceptible": list(task.get("mustBePerceptible") or []),
        "wouldBeALie": [
            text for obligation in obligations for text in obligation.get("wouldBeALie") or []
        ],
    }


def _capability_values(record: dict[str, Any], field: str) -> set[str]:
    return set((record.get("capability") or {}).get(field) or [])


def _supports_operation(operation: str, record: dict[str, Any],
                        contract: dict[str, Any]) -> list[str] | None:
    """Return the exact structured evidence for admission, or ``None``.

    Descriptive text is deliberately limited to evidence/document recognition,
    where the current catalog has no dedicated capability field. Generic family
    words never admit a record.
    """
    capability = record.get("capability") or {}
    scope = record.get("scope")
    if scope and not (scope == "lyrics" and operation == "lyric_presentation"):
        return None
    if operation == "lyric_presentation" and scope == "lyrics":
        return ["scope:lyrics", "approved_scoped_template"]
    if not capability:
        return None
    structure = capability.get("structure")
    staging = capability.get("staging")
    carries = _capability_values(record, "carries")
    readable = _capability_values(record, "readable")
    implies = _capability_values(record, "implies") - {"none"}
    non_identity_carries = carries - {"identity", "membership", "none"}
    media_slots = int(capability.get("media_slots") or 0)
    text_slots = int(capability.get("text_slots") or 0)
    slots_total = int(capability.get("slots_total") or 0)

    if operation == "transformation":
        capacity = max(media_slots, slots_total)
        if contract["hasTypedValues"]:
            supported = carries & {"change_over_time", "difference"}
            if supported:
                return sorted([f"carries:{value}" for value in supported])
        elif ("identity" in carries and structure in {"pair", "sequence"} and capacity >= 2 and
                not (carries & DATA_CARRIES) and
                not (readable & {"exact_value", "proportion", "difference", "rank"})):
            return [f"structure:{structure}", "carries:identity", f"subject_capacity:{capacity}"]
    elif operation == "subject_profile":
        if ("identity" in carries and not non_identity_carries and media_slots >= 1 and
                structure in {"single", "sequence"} and not (implies - {"chronology"})):
            return ["carries:identity", f"structure:{structure}", f"media_slots:{media_slots}"]
    elif operation == "relationship_intro":
        capacity = max(media_slots, slots_total)
        quantitative_readables = readable & {"exact_value", "proportion", "difference", "rank"}
        quantitative_carries = carries & (DATA_CARRIES - {"parity"})
        misleading_implications = implies - {"equality", "chronology"}
        if ("identity" in carries and capacity >= 2 and
                structure in {"pair", "list", "grid", "sequence", "grouped_clusters"} and
                not quantitative_readables and not quantitative_carries and
                not misleading_implications):
            return ["carries:identity", f"structure:{structure}", f"subject_capacity:{capacity}"]
    elif operation == "item_sequence":
        if "identity" in carries and structure in {"sequence", "list", "grid", "grouped_clusters"} and max(media_slots, slots_total) >= 2:
            return ["carries:identity", f"structure:{structure}", f"staging:{staging}"]
    elif operation == "archival_progression":
        if ("change_over_time" in carries or "chronology" in implies or
                ("identity" in carries and not non_identity_carries and
                 structure == "sequence" and staging == "reveals_in_turn")):
            return [f"structure:{structure}", f"staging:{staging}"] + sorted(
                [f"carries:{value}" for value in carries & {"identity", "change_over_time"}] +
                [f"implies:{value}" for value in implies & {"chronology"}]
            )
    elif operation == "evidence_presentation":
        evidence_terms = (
            ("article", "document", "webpage", "screen", "newspaper")
            if contract.get("evidenceKind") == "document_screen"
            else ("article", "document", "webpage", "screen", "newspaper", "source", "evidence", "quote")
        )
        operation_text = _operation_text(record)
        matched = next((term for term in evidence_terms
                        if re.search(rf"\b{re.escape(term)}\b", operation_text)), None)
        if matched and (readable & {"statement", "label", "exact_value"} or text_slots >= 1):
            return [f"evidence_descriptor:{matched}", f"structure:{structure}", f"text_slots:{text_slots}"]
    elif operation == "milestone_reveal":
        if ("identity" in carries and not non_identity_carries and
                structure in {"single", "sequence"} and
                (readable & {"label", "statement"} or text_slots >= 1) and
                not (implies - {"chronology"})):
            return ["carries:identity", f"structure:{structure}", "readable:label_or_statement"]
    elif operation == "data_explanation":
        supported = carries & DATA_CARRIES
        if supported or "exact_value" in readable:
            return sorted([f"carries:{value}" for value in supported] + (["readable:exact_value"] if "exact_value" in readable else []))
    elif operation == "comparison":
        supported = carries & {"difference", "parity", "rank", "overlap"}
        if supported or (structure == "pair" and "identity" in carries):
            return sorted([f"carries:{value}" for value in supported] or ["structure:pair", "carries:identity"])
    elif operation == "event_narration":
        if ("identity" in carries and media_slots >= 1 and structure in {"single", "sequence"} and
                not non_identity_carries and not implies and
                not (readable & {"exact_value", "proportion", "difference", "rank"})):
            return ["carries:identity", f"structure:{structure}", f"media_slots:{media_slots}"]
    elif operation in {"concept_statement", "rhetorical_question"}:
        if (structure == "single" and not non_identity_carries and not implies and
                ("statement" in readable or text_slots >= 1)):
            return ["structure:single", "readable:statement" if "statement" in readable else f"text_slots:{text_slots}"]
    return None


def _presentation_candidates(task: dict[str, Any], pool: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    contract = presentation_contract(task)
    # Secondary operations explain the task, but unioning every operation turns
    # an incidental year or phrase into permission for unrelated families. One
    # primary communication requirement controls admission; alternatives for
    # mixed payloads are represented as route/split review, not a broad union.
    for operation_index, operation in enumerate([contract["primaryOperation"]]):
        for record in pool.values():
            if record["id"] in seen:
                continue
            evidence = _supports_operation(operation, record, contract)
            if not evidence:
                continue
            rows.append({
                "id": record["id"],
                "name": record.get("description"),
                "provenance": {
                    "source": "structured-presentation-contract",
                    "operation": operation,
                    "evidence": evidence,
                    "scope": "retrieval_only_not_fit",
                },
                # Stable operation precedence only; never a fit or confidence score.
                "_rel": len(contract["operations"]) - operation_index,
            })
            seen.add(record["id"])
    return rows


def _read(path: Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _source(path: Path) -> dict[str, Any]:
    path = Path(path)
    return {"path": path.resolve().relative_to(ROOT.resolve()).as_posix(), "sha256": _sha(path), "bytes": path.stat().st_size}


def template_candidates(
    task: dict[str, Any], bindings: dict[str, Any], pool: dict[str, Any],
    *, exhaustive_families: bool = False,
) -> list[dict[str, Any]]:
    """Retrieve a deterministic, task-scoped template slate.

    This is the reusable consumer shared by the source-beat pilot and the full
    StoryPackage batch runner. It retrieves candidates; it does not decide fit,
    selection, treatment, or render eligibility.
    """
    enforce_contracts("visualtask_matching.template_candidates")
    if (task.get("routeDisposition") or {}).get("templateEligible") is False:
        return []
    job = task["job"]
    contract = presentation_contract(task)
    structured_mode = bool(task.get("presentationOperations"))
    rows = _presentation_candidates(task, pool) if structured_mode else [
        dict(row) for row in bindings.get(job) or [] if row.get("id") in pool
    ]
    relevance = task.get("candidateRelevance") or {}
    for row in rows:
        if row["id"] in relevance:
            # Contract-operation precedence remains primary; local semantic
            # relevance only orders candidates inside that compatible tier.
            row["_rel"] = (row.get("_rel") or 0) * 10 + relevance[row["id"]]
            row["provenance"]["relevanceOrdering"] = {
                "source": "local-macos-natural-language",
                "scope": "ordering_only_not_admission_or_fit",
            }
    # In the new structured path, legacy bindings are secondary evidence only. They
    # may enrich provenance for an already-compatible record, but never enlarge a
    # new story's candidate pool. Older frozen VisualTasks without presentation
    # operations retain their legacy replay path until they are migrated.
    legacy = {row.get("id"): row for row in bindings.get(job) or []}
    for row in rows:
        if structured_mode and row["id"] in legacy:
            row["provenance"]["legacyJobBinding"] = {
                "job": job,
                "provenance": legacy[row["id"]].get("provenance"),
            }
    seen = {row["id"] for row in rows}
    for admission in task.get("templateAdmissions") or []:
        template_id = admission.get("id")
        if template_id not in pool:
            raise ValueError(f"task admission references unavailable template: {task['id']}: {template_id}")
        if template_id not in seen:
            rows.insert(0, {
                "id": template_id,
                "name": pool[template_id].get("description"),
                "provenance": {**admission, "verdict": "user-named"},
                "_rel": 100000,
            })
            seen.add(template_id)
    if C.needs_spatial(task.get("entityCount")):
        for record in pool.values():
            if C.is_spatial(record) and record["id"] not in seen:
                rows.append({"id": record["id"], "name": record.get("description"), "provenance": {"source": "spatial-route", "reason": "20+ VisualTask identity demand"}})
                seen.add(record["id"])
    display_limit = task.get("candidateDisplayLimit", 10)
    slideshow_limit = task.get("slideshowDisplayLimit", C.SLIDE_MAX)
    ranked = C.diversify(
        rows,
        limit=max(len(rows), 1) if exhaustive_families else display_limit,
        corpus_size=len(pool),
        pool_index=pool,
        slide_max=None if exhaustive_families else slideshow_limit,
        honor_global_picks=not task.get("ignorePriorSelections", False),
    )[0]
    # Explicit task-scoped editor requests must survive the family representative
    # and slideshow display caps. They remain unvalidated and authorize nothing.
    by_id = {row["id"]: row for row in rows}
    for admission in reversed(task.get("templateAdmissions") or []):
        template_id = admission["id"]
        if template_id in {row["id"] for row in ranked}:
            continue
        admitted = by_id[template_id]
        family = C._family(admitted)
        same_family_index = next(
            (index for index, row in enumerate(ranked) if C._family(row) == family), None)
        if same_family_index is not None:
            ranked.pop(same_family_index)
        ranked.insert(0, admitted)
        if not exhaustive_families and len(ranked) > display_limit:
            ranked.pop()
    return [{
        "candidateId": row["id"],
        "name": row.get("name") or pool[row["id"]].get("description"),
        "condition": row.get("condition"),
        "bindingProvenance": row.get("provenance"),
        "candidateMatchingProvenance": {
            "scope": "visual_task", "taskId": task["id"], "matchingJob": job,
            "taskRole": task["taskRole"], "quote": task["quote"],
            "displayIdentityCount": len((task.get("entities") or {}).get("displayEligible") or []),
            "perceptibilityConstraints": task.get("mustBePerceptible") or [],
            "presentationOperations": task.get("presentationOperations") or [],
            "presentationContract": contract,
            "ignoredPriorStorySelections": bool(task.get("ignorePriorSelections")),
            "candidateDisplayLimit": display_limit,
            "relevanceOrderingApplied": bool(relevance),
            "retrievalMode": "structured_presentation_contract" if structured_mode else "legacy_visualtask_replay",
        },
    } for row in ranked]


# Backward-compatible name for existing callers while they move to the public
# task-scoped consumer above.
_template_candidates = template_candidates


def _summarize_media(task: dict[str, Any], pool: dict[str, Any]) -> dict[str, Any]:
    entities = list((task.get("entities") or {}).get("displayEligible") or [])
    provenance = {"scope": "visual_task", "taskId": task["id"], "quote": task["quote"]}
    if not entities:
        return {
            "status": "no_entity_media_demand", "entities": [], "groupCandidateIds": [],
            "individualCandidateIds": {}, "gaps": [],
            "candidateMatchingProvenance": {**provenance, "reason": "No display-eligible identities; sibling media is not inherited."},
        }
    resolved = M.resolve(entities, pool=pool, quote=task["quote"])
    return {
        "status": "resolved_with_gaps" if resolved.get("gaps") else "resolved",
        "entities": entities,
        "groupCandidateIds": [row["id"] for row in (resolved.get("group") or [])[:8]],
        "individualCandidateIds": {entity: [row["id"] for row in rows[:8]] for entity, rows in (resolved.get("individual") or {}).items()},
        "gaps": resolved.get("gaps") or [],
        "candidateMatchingProvenance": {**provenance, "identitySource": "VisualTask displayEligible identities", "resolver": "existing Production Ready media_candidates.resolve"},
    }


def build(*, source_beat: str, tasks_path: Path = DEFAULT_TASKS, bindings_path: Path = DEFAULT_BINDINGS) -> dict[str, Any]:
    tasks_artifact = _read(tasks_path)
    if tasks_artifact.get("activationState") != "review_only_not_connected":
        raise ValueError("VisualTask matching input must remain review-only")
    tasks = [row for row in tasks_artifact.get("tasks") or [] if row.get("sourceBeatId") == source_beat]
    if not tasks:
        raise ValueError(f"no VisualTasks for source beat: {source_beat}")
    bindings = _read(bindings_path)
    template_pool = {row["id"]: row for row in C.load(content_class="*")}
    media_pool = M.load()
    rows = [{
        "taskId": task["id"], "sourceBeatId": source_beat, "ordinal": task["ordinal"],
        "taskRole": task["taskRole"], "matchingJob": task["job"], "quote": task["quote"],
        "continuityGroup": task.get("continuityGroup"),
        "templateCandidates": template_candidates(task, bindings, template_pool),
        "mediaCandidates": _summarize_media(task, media_pool),
    } for task in tasks]
    artifact = {
        "schemaVersion": 1, "purpose": "Review-only independent template and media matching per VisualTask",
        "activationState": "review_only_not_connected", "selectionAuthorized": False,
        "renderingAuthorized": False, "sourceBeatId": source_beat,
        "sources": {"visualTasks": _source(tasks_path), "bindings": _source(bindings_path)}, "tasks": rows,
    }
    validate(artifact, verify_sources=False)
    return artifact


def validate(artifact: dict[str, Any], *, verify_sources: bool = True) -> None:
    if artifact.get("activationState") != "review_only_not_connected":
        raise ValueError("VisualTask matching must remain review-only")
    if artifact.get("selectionAuthorized") is not False or artifact.get("renderingAuthorized") is not False:
        raise ValueError("VisualTask matching cannot authorize selection or rendering")
    rows = artifact.get("tasks") or []
    if len({row.get("taskId") for row in rows}) != len(rows):
        raise ValueError("duplicate matched VisualTask")
    for row in rows:
        for candidate in row.get("templateCandidates") or []:
            provenance = candidate.get("candidateMatchingProvenance") or {}
            if provenance.get("scope") != "visual_task" or provenance.get("taskId") != row.get("taskId"):
                raise ValueError("template candidate lacks VisualTask provenance")
        provenance = (row.get("mediaCandidates") or {}).get("candidateMatchingProvenance") or {}
        if provenance.get("scope") != "visual_task" or provenance.get("taskId") != row.get("taskId"):
            raise ValueError("media result lacks VisualTask provenance")
    if verify_sources:
        for source in (artifact.get("sources") or {}).values():
            path = ROOT / source["path"]
            if not path.is_file() or _sha(path) != source["sha256"]:
                raise ValueError("VisualTask matching source is missing or stale")
        replay = build(source_beat=artifact["sourceBeatId"], tasks_path=ROOT / artifact["sources"]["visualTasks"]["path"], bindings_path=ROOT / artifact["sources"]["bindings"]["path"])
        if dumps(replay) != dumps(artifact):
            raise ValueError("VisualTask matching does not replay from bound inputs")


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-beat", required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        validate(_read(args.output)); print("VisualTask matching passed."); return 0
    artifact = build(source_beat=args.source_beat)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(dumps(artifact), encoding="utf-8")
    print(dumps(artifact), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
