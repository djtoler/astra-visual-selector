#!/usr/bin/env python3
"""Prepare and validate provider-independent, review-only semantic split proposals."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1
REVIEW_ONLY = "review_only_not_connected"


def read(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _closed(value: Any, required: set[str], optional: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    keys = set(value)
    missing = required - keys
    extra = keys - required - optional
    if missing:
        raise ValueError(f"{label} missing fields: {sorted(missing)}")
    if extra:
        raise ValueError(f"{label} has unsupported fields: {sorted(extra)}")


def _distinct_nonempty(rows: list[dict[str, Any]], key: str, label: str) -> set[str]:
    values = [row.get(key) for row in rows]
    if any(not isinstance(value, str) or not value for value in values):
        raise ValueError(f"{label} requires nonempty {key}")
    if len(values) != len(set(values)):
        raise ValueError(f"{label} contains duplicate {key}")
    return set(values)


def _string_set(value: Any, label: str) -> set[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{label} must contain nonempty strings")
    if len(value) != len(set(value)):
        raise ValueError(f"{label} contains duplicates")
    return set(value)


def _review_only(value: dict[str, Any], label: str) -> None:
    if value.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError(f"unsupported {label} schema version")
    if value.get("activationState") != REVIEW_ONLY:
        raise ValueError(f"{label} must remain review-only")
    if value.get("selectionAuthorized") is not False or value.get("renderingAuthorized") is not False:
        raise ValueError(f"{label} cannot authorize selection or rendering")


def validate_inputs(
    story: dict[str, Any],
    vocabulary: dict[str, Any],
    roster: dict[str, Any],
    editor_context: dict[str, Any],
) -> dict[str, Any]:
    _closed(story, {
        "schemaVersion", "storyId", "namespace", "activationState",
        "selectionAuthorized", "renderingAuthorized", "beats",
    }, set(), "StoryPackage")
    _review_only(story, "StoryPackage")
    if not isinstance(story["storyId"], str) or not story["storyId"]:
        raise ValueError("StoryPackage requires storyId")
    if not isinstance(story["namespace"], str) or not story["namespace"]:
        raise ValueError("StoryPackage requires namespace")
    beats = story["beats"]
    if not isinstance(beats, list) or not beats:
        raise ValueError("StoryPackage requires beats")

    _closed(vocabulary, {
        "schemaVersion", "vocabularyVersion", "activationState", "selectionAuthorized",
        "renderingAuthorized", "jobs", "taskRoles", "mediaKinds", "dataRequirementKinds",
    }, set(), "task vocabulary")
    _review_only(vocabulary, "task vocabulary")
    jobs = vocabulary["jobs"]
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("task vocabulary requires jobs")
    for row in jobs:
        _closed(row, {"id", "definition"}, set(), "task vocabulary job")
    job_ids = _distinct_nonempty(jobs, "id", "task vocabulary jobs")
    for field in ("taskRoles", "mediaKinds", "dataRequirementKinds"):
        values = vocabulary[field]
        if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
            raise ValueError(f"task vocabulary {field} must contain strings")
        if len(values) != len(set(values)):
            raise ValueError(f"task vocabulary {field} contains duplicates")

    _closed(roster, {
        "schemaVersion", "rosterVersion", "activationState", "selectionAuthorized",
        "renderingAuthorized", "entities", "cohorts",
    }, set(), "roster context")
    _review_only(roster, "roster context")
    if not isinstance(roster["entities"], list) or not isinstance(roster["cohorts"], list):
        raise ValueError("roster entities and cohorts must be lists")
    for row in roster["entities"]:
        _closed(row, {"id", "name"}, set(), "roster entity")
    entity_ids = _distinct_nonempty(roster["entities"], "id", "roster entities")
    for row in roster["cohorts"]:
        _closed(row, {"id", "version", "label", "memberEntityRefs"}, set(), "roster cohort")
        if not _string_set(row["memberEntityRefs"], "cohort memberEntityRefs") <= entity_ids:
            raise ValueError("roster cohort references unknown entity")
    cohort_ids = _distinct_nonempty(roster["cohorts"], "id", "roster cohorts")

    _closed(editor_context, {
        "schemaVersion", "contextVersion", "storyId", "activationState",
        "selectionAuthorized", "renderingAuthorized", "entries",
    }, set(), "editor context")
    _review_only(editor_context, "editor context")
    if editor_context["storyId"] != story["storyId"]:
        raise ValueError("editor context belongs to another story")
    if not isinstance(editor_context["entries"], list):
        raise ValueError("editor context entries must be a list")
    for row in editor_context["entries"]:
        _closed(row, {"id", "scope", "beatIds", "directive", "priority"}, set(), "editor context entry")
        if row["scope"] not in {"story", "beat"} or row["priority"] != "editor":
            raise ValueError("editor context scope or priority is invalid")
        _string_set(row["beatIds"], "editor context beatIds")
    context_ids = _distinct_nonempty(editor_context["entries"], "id", "editor context entries")
    context_by_id = {row["id"]: row for row in editor_context["entries"]}

    beat_ids = _distinct_nonempty(beats, "id", "StoryPackage beats")
    ordinals = [row.get("ordinal") for row in beats]
    if any(not isinstance(value, int) or value < 1 for value in ordinals) or len(ordinals) != len(set(ordinals)):
        raise ValueError("StoryPackage beat ordinals must be distinct positive integers")
    for row in beats:
        _closed(row, {
            "id", "ordinal", "text", "entityRefs", "cohortRefs", "truthConstraints",
            "prohibitions", "dataRequirements", "editorContextRefs",
            "perceptibilityConstraints", "continuityGroup",
        }, set(), "StoryPackage beat")
        if not isinstance(row["text"], str) or not row["text"]:
            raise ValueError("StoryPackage beat requires text")
        if not _string_set(row["entityRefs"], "beat entityRefs") <= entity_ids:
            raise ValueError(f"beat references unknown entity: {row['id']}")
        if not _string_set(row["cohortRefs"], "beat cohortRefs") <= cohort_ids:
            raise ValueError(f"beat references unknown cohort: {row['id']}")
        if not _string_set(row["editorContextRefs"], "beat editorContextRefs") <= context_ids:
            raise ValueError(f"beat references unknown editor context: {row['id']}")
        for context_id in row["editorContextRefs"]:
            context = context_by_id[context_id]
            if context["scope"] == "beat" and row["id"] not in context["beatIds"]:
                raise ValueError(f"beat references inapplicable editor context: {row['id']}")
        for field in ("truthConstraints", "prohibitions"):
            if not isinstance(row[field], list):
                raise ValueError(f"beat {field} must be a list")
            for item in row[field]:
                _closed(item, {"id", "text"}, set(), f"beat {field} entry")
            _distinct_nonempty(row[field], "id", f"beat {field}")
        if not isinstance(row["dataRequirements"], list):
            raise ValueError("beat dataRequirements must be a list")
        for item in row["dataRequirements"]:
            _closed(item, {"id", "kind", "description"}, set(), "beat data requirement")
            if item["kind"] not in vocabulary["dataRequirementKinds"]:
                raise ValueError(f"beat uses unknown data requirement kind: {row['id']}")
        _distinct_nonempty(row["dataRequirements"], "id", "beat data requirements")
        if not isinstance(row["perceptibilityConstraints"], list) or any(
            not isinstance(value, str) or not value for value in row["perceptibilityConstraints"]
        ):
            raise ValueError("beat perceptibilityConstraints must contain strings")

    for entry in editor_context["entries"]:
        if entry["scope"] == "story" and entry["beatIds"]:
            raise ValueError("story-scoped editor context cannot name beat IDs")
        if entry["scope"] == "beat" and (not entry["beatIds"] or not set(entry["beatIds"]) <= beat_ids):
            raise ValueError("beat-scoped editor context references unknown beat")
    return {
        "beats": len(beats), "jobs": len(job_ids), "entities": len(entity_ids),
        "cohorts": len(cohort_ids), "editorContextEntries": len(context_ids),
    }


def _source(path: Path) -> dict[str, Any]:
    resolved = Path(path).resolve()
    try:
        stored = resolved.relative_to(ROOT).as_posix()
    except ValueError:
        stored = resolved.as_posix()
    return {"path": stored, "sha256": sha256(resolved), "bytes": resolved.stat().st_size}


def prepare_request(
    story: dict[str, Any],
    vocabulary: dict[str, Any],
    roster: dict[str, Any],
    editor_context: dict[str, Any],
    *,
    sources: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    validate_inputs(story, vocabulary, roster, editor_context)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "requestId": f"{story['namespace']}:{story['storyId']}:semantic-split:v1",
        "purpose": "Provider-independent semantic VisualTask split proposal",
        "reviewState": "awaiting_external_proposal",
        "activationState": REVIEW_ONLY,
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "sources": sources or {},
        "input": {
            "storyPackage": story,
            "taskVocabulary": vocabulary,
            "rosterContext": roster,
            "editorContext": editor_context,
        },
        "responseContract": {
            "schemaVersion": SCHEMA_VERSION,
            "oneProposalPerBeat": True,
            "exactCompleteNonoverlappingCharacterSpans": True,
            "humanApprovalRequiredBeforeActivation": True,
        },
    }


def prepare_request_from_files(
    story_path: Path, vocabulary_path: Path, roster_path: Path, editor_context_path: Path
) -> dict[str, Any]:
    paths = {
        "storyPackage": Path(story_path),
        "taskVocabulary": Path(vocabulary_path),
        "rosterContext": Path(roster_path),
        "editorContext": Path(editor_context_path),
    }
    values = {key: read(path) for key, path in paths.items()}
    return prepare_request(
        values["storyPackage"], values["taskVocabulary"], values["rosterContext"],
        values["editorContext"], sources={key: _source(path) for key, path in paths.items()},
    )


def validate_request(request: dict[str, Any], *, verify_sources: bool = True) -> None:
    _closed(request, {
        "schemaVersion", "requestId", "purpose", "reviewState", "activationState",
        "selectionAuthorized", "renderingAuthorized", "sources", "input", "responseContract",
    }, set(), "semantic split request")
    _review_only(request, "semantic split request")
    if request["reviewState"] != "awaiting_external_proposal":
        raise ValueError("semantic split request review state is invalid")
    _closed(request["input"], {"storyPackage", "taskVocabulary", "rosterContext", "editorContext"}, set(), "request input")
    validate_inputs(
        request["input"]["storyPackage"], request["input"]["taskVocabulary"],
        request["input"]["rosterContext"], request["input"]["editorContext"],
    )
    expected_contract = {
        "schemaVersion": SCHEMA_VERSION,
        "oneProposalPerBeat": True,
        "exactCompleteNonoverlappingCharacterSpans": True,
        "humanApprovalRequiredBeforeActivation": True,
    }
    _closed(request["responseContract"], set(expected_contract), set(), "response contract")
    if request["responseContract"] != expected_contract:
        raise ValueError("semantic split response contract was weakened")
    if verify_sources:
        required = {"storyPackage", "taskVocabulary", "rosterContext", "editorContext"}
        if set(request["sources"]) != required:
            raise ValueError("semantic split request sources are incomplete")
        for key in sorted(required):
            source = request["sources"][key]
            _closed(source, {"path", "sha256", "bytes"}, set(), "request source")
            path = Path(source["path"])
            path = path if path.is_absolute() else ROOT / path
            if not path.is_file() or sha256(path) != source["sha256"] or path.stat().st_size != source["bytes"]:
                raise ValueError(f"semantic split source is missing or stale: {key}")
            if dumps(read(path)) != dumps(request["input"][key]):
                raise ValueError(f"semantic split embedded input differs from source: {key}")


def _validate_exact_spans(text: str, tasks: list[dict[str, Any]], beat_id: str) -> None:
    cursor = 0
    for task in tasks:
        span = task["span"]
        start, end = span["start"], span["end"]
        if not isinstance(start, int) or not isinstance(end, int) or start != cursor or end <= start or end > len(text):
            raise ValueError(f"proposal spans must be exact, complete and nonoverlapping: {beat_id}")
        if task["quote"] != text[start:end]:
            raise ValueError(f"proposal quote does not match exact source span: {beat_id}")
        cursor = end
    if cursor != len(text):
        raise ValueError(f"proposal spans must be exact, complete and nonoverlapping: {beat_id}")


def validate_response(
    response: dict[str, Any], request: dict[str, Any], *, verify_sources: bool = True
) -> dict[str, int]:
    validate_request(request, verify_sources=verify_sources)
    _closed(response, {
        "schemaVersion", "requestId", "requestSha256", "reviewState", "activationState",
        "selectionAuthorized", "renderingAuthorized", "humanApproval", "beatProposals",
    }, set(), "semantic split response")
    _review_only(response, "semantic split response")
    if response["requestId"] != request["requestId"]:
        raise ValueError("semantic split response request ID mismatch")
    if response["requestSha256"] != sha256_bytes(dumps(request).encode("utf-8")):
        raise ValueError("semantic split response request hash mismatch")
    if response["reviewState"] != "external_proposal_unreviewed":
        raise ValueError("semantic split response cannot claim review or approval")
    _closed(response["humanApproval"], {"status", "reviewer", "reviewedAt"}, set(), "human approval")
    if response["humanApproval"] != {"status": "pending", "reviewer": None, "reviewedAt": None}:
        raise ValueError("semantic split response cannot invent human approval")

    inputs = request["input"]
    story = inputs["storyPackage"]
    vocabulary = inputs["taskVocabulary"]
    roster = inputs["rosterContext"]
    editor_context = inputs["editorContext"]
    beats = {row["id"]: row for row in story["beats"]}
    jobs = {row["id"] for row in vocabulary["jobs"]}
    roles = set(vocabulary["taskRoles"])
    media_kinds = set(vocabulary["mediaKinds"])
    entity_ids = {row["id"] for row in roster["entities"]}
    cohort_ids = {row["id"] for row in roster["cohorts"]}
    context_ids = {row["id"] for row in editor_context["entries"]}
    proposals = response["beatProposals"]
    if not isinstance(proposals, list):
        raise ValueError("beatProposals must be a list")
    proposal_ids = _distinct_nonempty(proposals, "sourceBeatId", "beat proposals")
    if proposal_ids != set(beats):
        raise ValueError("semantic split response must assess every beat exactly once")

    task_keys: list[str] = []
    split_count = 0
    for proposal in proposals:
        _closed(proposal, {
            "sourceBeatId", "sourceTextSha256", "recommendation", "rationale", "tasks",
        }, set(), "beat proposal")
        beat = beats[proposal["sourceBeatId"]]
        if not isinstance(proposal["rationale"], str) or not proposal["rationale"]:
            raise ValueError(f"beat proposal lacks rationale: {beat['id']}")
        if proposal["sourceTextSha256"] != sha256_bytes(beat["text"].encode("utf-8")):
            raise ValueError(f"beat proposal source text hash mismatch: {beat['id']}")
        tasks = proposal["tasks"]
        if not isinstance(tasks, list) or not tasks:
            raise ValueError(f"beat proposal requires tasks: {beat['id']}")
        if proposal["recommendation"] not in {"keep_single", "split"}:
            raise ValueError(f"invalid split recommendation: {beat['id']}")
        if (proposal["recommendation"] == "keep_single" and len(tasks) != 1) or (
            proposal["recommendation"] == "split" and len(tasks) < 2
        ):
            raise ValueError(f"split recommendation disagrees with task count: {beat['id']}")
        split_count += proposal["recommendation"] == "split"
        _validate_exact_spans(beat["text"], tasks, beat["id"])

        allocated = {
            "entityRefs": set(), "cohortRefs": set(), "truthConstraintRefs": set(),
            "prohibitionRefs": set(), "dataRequirementRefs": set(),
            "editorContextRefs": set(), "perceptibilityConstraints": set(),
        }
        allowed = {
            "entityRefs": set(beat["entityRefs"]),
            "cohortRefs": set(beat["cohortRefs"]),
            "truthConstraintRefs": {row["id"] for row in beat["truthConstraints"]},
            "prohibitionRefs": {row["id"] for row in beat["prohibitions"]},
            "dataRequirementRefs": {row["id"] for row in beat["dataRequirements"]},
            "editorContextRefs": set(beat["editorContextRefs"]),
            "perceptibilityConstraints": set(beat["perceptibilityConstraints"]),
        }
        for task in tasks:
            _closed(task, {
                "taskKey", "span", "quote", "visualJob", "taskRole", "takeaway", "reason",
                "entityRefs", "cohortRefs", "truthConstraintRefs", "prohibitionRefs",
                "dataRequirementRefs", "editorContextRefs", "requiredMediaKinds",
                "perceptibilityConstraints",
            }, set(), "semantic split task")
            _closed(task["span"], {"start", "end"}, set(), "semantic split span")
            task_keys.append(task["taskKey"])
            if not all(isinstance(task[field], str) and task[field] for field in ("taskKey", "takeaway", "reason")):
                raise ValueError(f"semantic split task lacks key, takeaway or reason: {beat['id']}")
            if task["visualJob"] not in jobs or task["taskRole"] not in roles:
                raise ValueError(f"semantic split task uses unknown job or role: {beat['id']}")
            if not _string_set(task["requiredMediaKinds"], "task requiredMediaKinds") <= media_kinds:
                raise ValueError(f"semantic split task uses unknown media kind: {beat['id']}")
            reference_domains = {
                "entityRefs": entity_ids, "cohortRefs": cohort_ids,
                "editorContextRefs": context_ids,
            }
            for field, domain in reference_domains.items():
                if not _string_set(task[field], f"task {field}") <= domain:
                    raise ValueError(f"semantic split task has unknown {field}: {beat['id']}")
            for field in allocated:
                values = _string_set(task[field], f"task {field}")
                if not values <= allowed[field]:
                    raise ValueError(f"semantic split task imports out-of-beat {field}: {beat['id']}")
                allocated[field].update(values)
        for field in allocated:
            if allocated[field] != allowed[field]:
                raise ValueError(f"semantic split proposal loses source {field}: {beat['id']}")

    if len(task_keys) != len(set(task_keys)):
        raise ValueError("semantic split response contains duplicate taskKey")
    return {
        "sourceBeats": len(beats),
        "keepSingle": len(beats) - split_count,
        "proposedSplits": split_count,
        "proposedTasks": len(task_keys),
        "humanApprovalPending": len(beats),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--story-package", type=Path, required=True)
    prepare_parser.add_argument("--task-vocabulary", type=Path, required=True)
    prepare_parser.add_argument("--roster-context", type=Path, required=True)
    prepare_parser.add_argument("--editor-context", type=Path, required=True)
    prepare_parser.add_argument("--output", type=Path, required=True)
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--request", type=Path, required=True)
    validate_parser.add_argument("--response", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        artifact = prepare_request_from_files(
            args.story_package, args.task_vocabulary, args.roster_context, args.editor_context
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(dumps(artifact), encoding="utf-8")
        print(dumps(artifact), end="")
    else:
        print(json.dumps(validate_response(read(args.response), read(args.request)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
