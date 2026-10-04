#!/usr/bin/env python3
"""Build a self-contained editor-review evidence package for root-cause analysis.

This exporter is intentionally descriptive. It preserves editor evidence and
diagnostic context but never converts comments into global matching rules.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
POLISH = ROOT.parent
ABANDONED = POLISH / "astra-visual-selector"
SCENE_APPROVED = POLISH / "ae-template-automation" / "scene-library" / "approved"


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pointer_token(value: object) -> str:
    return str(value).replace("~", "~0").replace("/", "~1")


def text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def first(*values: object) -> object | None:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def candidate_gallery_index() -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    paths = list((ROOT / "reports").glob("*candidate-gallery.json"))
    paths += list((ABANDONED / "reports").glob("*candidate-gallery.json"))
    for path in sorted(paths):
        try:
            data = load(path)
        except (OSError, json.JSONDecodeError):
            continue
        for task in data.get("tasks", []):
            task_id = task.get("taskId") or task.get("id")
            if not task_id:
                continue
            for candidate in task.get("candidates", []):
                candidate_id = candidate.get("candidateId") or candidate.get("id")
                if candidate_id:
                    index[(str(task_id), str(candidate_id))] = {
                        "packageId": data.get("packageId"),
                        "task": {
                            k: task.get(k) for k in (
                                "taskId", "sourceBeatId", "quote", "operation",
                                "primaryOperation", "presentationOperations",
                                "requirements", "candidateStatus"
                            ) if task.get(k) is not None
                        },
                        "candidate": {
                            k: candidate.get(k) for k in (
                                "candidateId", "name", "condition",
                                "bindingProvenance", "candidateMatchingProvenance"
                            ) if candidate.get(k) is not None
                        },
                    }
    return index


def source_candidates() -> list[Path]:
    paths: set[Path] = set()
    for base in (ROOT, ABANDONED):
        for pattern in (
            "reports/*candidate-review*.json",
            "reports/ordered-visual-route-decisions.json",
            "reports/carousel-slideshow-editor-alignment-review-*.json",
            "grammar/beat-review-export-*.json",
            "grammar/pairing-notes.json",
            "grammar/astra-media-review-recovered-decisions-*.json",
            "grammar/visual-task-timing-reviews.json",
            "treatment-requirements/current-exact-batch/review-decisions*.json",
            "treatment-requirements/pilot-*/review-*.json",
        ):
            paths.update(p for p in base.glob(pattern) if p.is_file())
    for name in (
        "template-review-notes.json",
        "infographic-review-notes.json",
        "infographic-review-results-2026-09-30.json",
        "archive3-review-decisions.json",
        "embedding-review-decisions.json",
        "evaluation-feedback.json",
    ):
        path = SCENE_APPROVED / name
        if path.exists():
            paths.add(path)
    return sorted(paths)


def source_label(path: Path) -> str:
    try:
        return str(path.relative_to(POLISH))
    except ValueError:
        return str(path)


def base_record(kind: str, authorship: str, scope: str, status: object,
                comment: object, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    record = {
        "evidenceType": kind,
        "authorship": authorship,
        "scope": scope,
        "status": str(status) if status not in (None, "") else None,
        "comment": text(comment),
        "selectionAuthorized": False,
        "renderingAuthorized": False,
    }
    if payload:
        record.update({k: v for k, v in payload.items() if v not in (None, "", [], {})})
    return record


def parse_candidate_review(data: dict[str, Any], gallery: dict[tuple[str, str], dict[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    out = []
    for key, value in (data.get("decisions") or {}).items():
        if not isinstance(value, dict):
            continue
        task_id, candidate_id = value.get("taskId"), value.get("candidateId")
        context = gallery.get((str(task_id), str(candidate_id)), {})
        record = base_record(
            "candidate_acceptability", "human", "template_candidate",
            value.get("status"), value.get("comment"), {
                "packageId": first(data.get("packageId"), context.get("packageId")),
                "taskId": task_id,
                "candidateId": candidate_id,
                "reviewer": value.get("reviewer"),
                "revision": value.get("revision"),
                "updatedAt": value.get("updatedAt"),
                "context": context or None,
            })
        # A persisted blank/unreviewed row is still review-session evidence and
        # must remain visible rather than being silently treated as absent.
        out.append((f"/decisions/{pointer_token(key)}", record))
    return out


def parse_beat_export(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    out = []
    for index, beat in enumerate(data.get("beats") or []):
        review = beat.get("userReview")
        if not isinstance(review, dict):
            continue
        comment = review.get("note") or ""
        status = review.get("rating")
        record = base_record("beat_review", "human_verbatim_recovered", "story_beat",
            status, comment, {
                "beatId": beat.get("beat"), "quote": beat.get("quote"),
                "presentationJob": beat.get("job"), "entities": beat.get("entities"),
                "review": review, "templateDecisions": beat.get("templates"),
                "pairings": beat.get("pairings"), "priorNotes": beat.get("priorNotes"),
            })
        out.append((f"/beats/{index}/userReview", record))
    return out


def parse_pairing_notes(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    out = []
    beats = data.get("beats") or []
    rows = beats.values() if isinstance(beats, dict) else beats
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not text(row.get("note")):
            continue
        out.append((f"/beats/{index}", base_record("template_media_pairing", "human_verbatim_recovered", "story_beat", None, row.get("note"), {
            "beatId": row.get("beat"), "pairings": row.get("pairs"), "updatedAt": row.get("updatedAt")
        })))
    return out


def parse_media_recovery(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    out = []
    briefs = ((data.get("notes") or {}).get("briefs") or {})
    for beat_id, brief in briefs.items():
        if text(brief.get("note")):
            out.append((f"/notes/briefs/{pointer_token(beat_id)}/note", base_record(
                "media_eligibility", "human_verbatim_recovered", "story_beat", None, brief.get("note"), {"beatId": beat_id})))
        for entity, note in (brief.get("entityNotes") or {}).items():
            if text(note):
                out.append((f"/notes/briefs/{pointer_token(beat_id)}/entityNotes/{pointer_token(entity)}", base_record(
                    "media_eligibility", "human_verbatim_recovered", "media_asset", None, note,
                    {"beatId": beat_id, "entityId": entity})))
    return out


def parse_timing(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    out = []
    for index, row in enumerate(data.get("reviews") or []):
        editor = row.get("editorReview") or {}
        if not editor:
            continue
        out.append((f"/reviews/{index}/editorReview", base_record(
            "timing_boundary", "human", "timing", editor.get("status"), editor.get("decision"), {
                "beatId": row.get("sourceBeatId"), "updatedAt": editor.get("approvedAt"),
                "boundary": row.get("boundary"), "taskSpans": row.get("taskSpans"),
                "measurementEvidence": row.get("measurementEvidence")
            })))
    return out


def parse_decision_map(data: dict[str, Any], key_name: str) -> list[tuple[str, dict[str, Any]]]:
    out = []
    decisions = data.get(key_name) or {}
    if not isinstance(decisions, dict):
        return out
    for key, value in decisions.items():
        if not isinstance(value, dict):
            continue
        comment = first(value.get("comment"), value.get("note"), value.get("selectionReason"), "")
        status = first(value.get("status"), value.get("decision"), value.get("route"))
        candidate = first(value.get("candidateId"), value.get("id"), key)
        kind = "route_decision" if value.get("route") else "template_capability_review"
        scope = "route" if value.get("route") else "template_candidate"
        out.append((f"/{key_name}/{pointer_token(key)}", base_record(kind,
            "derived_from_human" if value.get("reviewer") == "human_prior_decision" else "human",
            scope, status, comment, {
                "taskId": value.get("taskId"), "beatId": value.get("beatId"),
                "candidateId": candidate, "reviewer": value.get("reviewer"),
                "revision": value.get("revision"), "updatedAt": value.get("updatedAt"),
                "decisionPayload": value,
            })))
    return out


def parse_notes_map(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    out = []
    for key, value in (data.get("notes") or {}).items():
        if not isinstance(value, dict):
            continue
        note = value.get("note")
        status = first(value.get("status"), value.get("decision"))
        if text(note) or status:
            out.append((f"/notes/{pointer_token(key)}", base_record(
                "template_capability_review", "human", "template_capability", status, note,
                {"candidateId": first(value.get("id"), key), "reviewer": value.get("reviewer"),
                 "revision": value.get("revision"), "updatedAt": value.get("updatedAt")})))
    return out


def parse_feedback(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    out = []
    for key, value in (data.get("feedback") or {}).items():
        if isinstance(value, dict) and text(value.get("comment")):
            out.append((f"/feedback/{pointer_token(key)}", base_record(
                "matching_output_feedback", "human", "story_beat", None, value.get("comment"), {
                    "beatId": key, "passageId": value.get("passageId"), "shotId": value.get("shotId"),
                    "revision": value.get("revision"), "updatedAt": value.get("updatedAt")
                })))
    return out


def parse_pilot(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    direction = data.get("verbatimEditorDirection")
    if isinstance(direction, list):
        direction = "\n\n".join(text(item) for item in direction if text(item))
    if not text(direction):
        return []
    return [("/verbatimEditorDirection", base_record(
        "treatment_review", "human", "template_candidate", data.get("decision"), direction, {
            "taskId": data.get("taskId"), "candidateId": data.get("candidateId"),
            "updatedAt": data.get("reviewedAt"), "approvedTreatment": data.get("approvedTreatment")
        }))]


def parse_infographic_results(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    out = []
    for index, row in enumerate(data.get("results") or []):
        if not isinstance(row, dict) or not text(row.get("response")):
            continue
        out.append((f"/results/{index}", base_record(
            "template_capability_review", "human", "template_capability", None,
            row.get("response"), {
                "candidateId": row.get("templateId"), "revision": row.get("revision"),
                "updatedAt": row.get("respondedAt"),
                "context": {k: row.get(k) for k in ("title", "originalName", "paths") if row.get(k) is not None}
            })))
    return out


def parse_carousel(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    quote = data.get("quote")
    results = data.get("results")
    comment = quote if text(quote) else json.dumps(results, ensure_ascii=False, sort_keys=True)
    return [("/", base_record("template_timing_review", "human", "template_capability",
        data.get("finalDisposition"), comment, {
            "candidateId": data.get("familyId"), "updatedAt": data.get("reviewedAt"),
            "reviewPasses": {k: data.get(k) for k in ("results", "secondPass", "thirdPass", "oneSecondCorrectionReview") if data.get(k) is not None}
        }))]


def parser_for(path: Path, data: dict[str, Any], gallery: dict[tuple[str, str], dict[str, Any]]) -> tuple[str, list[tuple[str, dict[str, Any]]]]:
    name = path.name
    if "candidate-review" in name:
        return "candidate_review", parse_candidate_review(data, gallery)
    if name.startswith("beat-review-export"):
        return "beat_review_export", parse_beat_export(data)
    if name == "pairing-notes.json":
        return "pairing_notes", parse_pairing_notes(data)
    if name.startswith("astra-media-review-recovered-decisions"):
        return "media_review_recovery", parse_media_recovery(data)
    if name == "visual-task-timing-reviews.json":
        return "timing_reviews", parse_timing(data)
    if name == "evaluation-feedback.json":
        return "evaluation_feedback", parse_feedback(data)
    if name.startswith("infographic-review-results"):
        return "infographic_review_results", parse_infographic_results(data)
    if name.startswith("carousel-slideshow-editor-alignment-review"):
        return "carousel_timing_review", parse_carousel(data)
    if name.startswith("review-") and "pilot-" in str(path.parent):
        return "treatment_pilot_review", parse_pilot(data)
    if "notes" in data:
        return "notes_map", parse_notes_map(data)
    if "decisions" in data:
        return "decision_map", parse_decision_map(data, "decisions")
    return "unsupported", []


def stable_record_key(record: dict[str, Any]) -> str:
    identity = {k: record.get(k) for k in (
        "evidenceType", "authorship", "scope", "status", "comment", "packageId",
        "taskId", "beatId", "candidateId", "entityId", "revision", "updatedAt"
    )}
    return hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def build(generated_at: str) -> dict[str, Any]:
    gallery = candidate_gallery_index()
    by_sha: dict[str, list[Path]] = defaultdict(list)
    for path in source_candidates():
        by_sha[digest(path)].append(path)

    records_by_key: dict[str, dict[str, Any]] = {}
    sources = []
    for sha, aliases in sorted(by_sha.items(), key=lambda item: source_label(item[1][0])):
        canonical = sorted(aliases, key=lambda p: (0 if ROOT in p.parents else 1, source_label(p)))[0]
        data = load(canonical)
        if not isinstance(data, dict):
            parser_name, parsed = "unsupported", []
        else:
            parser_name, parsed = parser_for(canonical, data, gallery)
        source_id = "src_" + sha[:16]
        for pointer, record in parsed:
            ref = {"sourceId": source_id, "jsonPointer": pointer}
            key = stable_record_key(record)
            if key in records_by_key:
                records_by_key[key]["sourceRefs"].append(ref)
            else:
                record["sourceRefs"] = [ref]
                record["evidenceId"] = "ev_" + key[:16]
                records_by_key[key] = record
        sources.append({
            "sourceId": source_id,
            "sha256": sha,
            "canonicalPath": source_label(canonical),
            "aliases": [source_label(path) for path in sorted(aliases) if path != canonical],
            "parser": parser_name,
            "recordCount": len(parsed),
        })

    records = sorted(records_by_key.values(), key=lambda row: row["evidenceId"])
    type_counts = Counter(row["evidenceType"] for row in records)
    author_counts = Counter(row["authorship"] for row in records)
    package_counts = Counter(row.get("packageId") for row in records if row.get("packageId"))
    unresolved_context = sum(
        1 for row in records
        if row["evidenceType"] == "candidate_acceptability" and not row.get("context")
    )
    return {
        "schemaVersion": "astra-matching-review-evidence@1",
        "purpose": "Verbatim and explicitly derived editor evidence for cross-layer matching root-cause analysis.",
        "generatedAt": generated_at,
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "usageBoundary": {
            "allowed": "Cite evidence IDs while diagnosing Story, Data, Media and Matching inputs, contracts and outputs.",
            "forbidden": "Do not promote a scoped comment into a global rule, select a template or authorize rendering without reconciliation."
        },
        "counts": {
            "uniqueRecords": len(records),
            "sources": len(sources),
            "sourceAliases": sum(len(source["aliases"]) for source in sources),
            "byEvidenceType": dict(sorted(type_counts.items())),
            "byAuthorship": dict(sorted(author_counts.items())),
            "byPackage": dict(sorted(package_counts.items())),
            "candidateReviewsWithoutGalleryContext": unresolved_context,
        },
        "sources": sources,
        "records": records,
        "excludedClasses": [
            {"class": "workflow_review_logs", "reason": "Governance checkpoints are not editor assessment of a beat/template match."},
            {"class": "model_review_and_evaluation_outputs", "reason": "Machine judgments remain diagnostic inputs and are not labeled as editor evidence."},
            {"class": "render_and_native_test_reviews", "reason": "Render-fidelity evidence is outside this first matching/root-cause package unless it also appears in a template capability decision."},
            {"class": "footage_inventory_without_editor_decisions", "reason": "Inventory rows without a saved editor status or note contain no review evidence."}
        ]
    }


def validate(package: dict[str, Any]) -> None:
    assert package["schemaVersion"] == "astra-matching-review-evidence@1"
    assert package["selectionAuthorized"] is False
    assert package["renderingAuthorized"] is False
    ids = [row["evidenceId"] for row in package["records"]]
    assert len(ids) == len(set(ids))
    source_ids = {row["sourceId"] for row in package["sources"]}
    for row in package["records"]:
        assert row["selectionAuthorized"] is False
        assert row["renderingAuthorized"] is False
        assert row["sourceRefs"]
        assert all(ref["sourceId"] in source_ids for ref in row["sourceRefs"])
        # Some recovered beat reviews contain only boolean media/B-roll rulings
        # or saved pairings. Their empty prose is itself faithful source data.
        assert row["comment"] or row["status"] or row.get("review") or row.get("pairings")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "astra-matching-review-evidence-20261004.json")
    parser.add_argument("--generated-at", default=dt.datetime.now(dt.timezone.utc).isoformat())
    args = parser.parse_args()
    package = build(args.generated_at)
    validate(package)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"output": str(args.output), "counts": package["counts"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
