#!/usr/bin/env python3
"""Calibrate conservative clip-to-native-composition mapping proposals.

Prediction is deliberately isolated from verified mappings and raw native
timelines.  Gold mappings and native timelines are evaluation inputs only.
This module never writes the production mapping sidecar or emits `verified`.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .clip_technical_coverage import _semantic_rows


ROOT = Path(__file__).resolve().parents[1]
POLISH_ROOT = ROOT.parent
DEFAULT_REQUEST = ROOT / "clip-mapping-calibration" / "request.json"
DEFAULT_REPORT = ROOT / "reports" / "clip-mapping-calibration.json"

STOP_WORDS = {
    "edit", "edited", "editing", "comp", "comps", "composition", "final",
    "main", "scene", "scenes", "render", "media", "placeholder", "other",
    "others", "project", "elements", "slideshow", "carousel", "photo",
    "photos", "text", "title", "titles", "template", "templates", "review",
    "source", "horizontal", "vertical", "full", "frame", "frames",
}


def _read(path: Path) -> Any:
    return json.loads(Path(path).read_text())


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _resolve(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def validate_request(request: dict[str, Any]) -> None:
    if request.get("activationState") != "calibration_review_only":
        raise ValueError("calibration must remain review-only")
    if request.get("promoteMappings") is not False:
        raise ValueError("calibration cannot promote mappings")
    if request.get("renderingAuthorized") is not False:
        raise ValueError("calibration cannot authorize rendering")
    predictor = request.get("predictorSources") or {}
    evaluation = request.get("evaluationSources") or {}
    if "verifiedMappings" in predictor:
        raise ValueError("verified answers cannot be a predictor source")
    for group_name, group in (("predictor", predictor), ("evaluation", evaluation)):
        for name, source in group.items():
            path = _resolve(source["path"])
            if not path.is_file():
                raise ValueError(f"{group_name} source missing: {name}: {path}")
            actual = _sha(path)
            if actual != source.get("sha256"):
                raise ValueError(f"{group_name} source changed: {name}: {actual}")
    replay_ids = request.get("replaySceneIds") or []
    if len(replay_ids) != len(set(replay_ids)) or not replay_ids:
        raise ValueError("replay scene IDs must be unique and non-empty")
    excluded_ids = request.get("prospectiveExcludedIds") or []
    if len(excluded_ids) != len(set(excluded_ids)):
        raise ValueError("prospective exclusion IDs must be unique")
    if set(replay_ids) & set(excluded_ids):
        raise ValueError("replay and prospective exclusion IDs must not overlap")
    if int(request.get("prospectiveSampleSize", 0)) < 30:
        raise ValueError("prospective sample must contain at least 30 clips")


def _load_prediction_inputs(request: dict[str, Any]) -> tuple[list[dict], dict, dict]:
    sources = request["predictorSources"]
    review = _read(_resolve(sources["reviewCatalog"]["path"]))
    approved = _read(_resolve(sources["approvedCatalog"]["path"]))
    links = _read(_resolve(sources["technicalFamilyLinks"]["path"]))
    technical = _read(_resolve(sources["technicalIndex"]["path"]))
    rows = _semantic_rows(review, approved)
    by_clip = {row["clipId"]: row for row in rows}
    if len(by_clip) != len(rows):
        raise ValueError("semantic inputs contain duplicate clip IDs")
    return rows, {row["familyId"]: row for row in links["links"]}, {
        row["id"]: row for row in technical["projects"]
    }


def _tokens(value: str | None) -> set[str]:
    return {
        token for token in re.findall(r"[a-z]+", (value or "").lower())
        if len(token) > 2 and token not in STOP_WORDS
    }


def _clip_ordinal(clip_id: str) -> int | None:
    match = re.search(r"--(?:scene|review)(?:-v\d+)?-(\d+)", clip_id)
    return int(match.group(1)) if match else None


def _numbers(value: str) -> list[int]:
    return [int(item) for item in re.findall(r"(?<!\d)(\d{1,3})(?!\d)", value)]


def _is_output_candidate(comp: dict[str, Any]) -> bool:
    path = comp["path"]
    lower = path.lower()
    if any(marker in lower for marker in (
        "/edit/", "/media/", "placeholder", "precomp", "other comps", "elements/",
    )):
        return False
    has_capacity = (
        comp.get("totalIndependentVisualMediaInputs", 0) > 0
        or comp.get("recursiveEditableTextFields", 0) > 0
    )
    output_name = re.search(
        r"(final|render|main|scene[_ ]?\d+|carousel \d+|bar chart \d+|"
        r"counter \d+|seq_?\d+|gallery pro|scrolling_screen|number count|"
        r"comparison list)",
        lower,
    )
    return bool(has_capacity and output_name)


def predict_clip(
    clip: dict[str, Any],
    link: dict[str, Any] | None,
    projects: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    base = {
        "clipId": clip["clipId"],
        "familyId": clip["familyId"],
        "status": "abstain",
        "evidenceClass": "no_safe_structural_candidate",
        "proposedComposition": None,
        "alternatives": [],
    }
    if not link or link.get("projectId") not in projects:
        base["evidenceClass"] = "project_not_linked"
        return base
    project = projects[link["projectId"]]
    candidates = [row for row in project["compositions"] if _is_output_candidate(row)]
    base["projectId"] = project["id"]
    base["candidateCount"] = len(candidates)
    description_tokens = _tokens(clip["semantic"].get("description"))
    lexical: list[tuple[int, float, dict[str, Any], list[str]]] = []
    for candidate in candidates:
        path_tokens = _tokens(candidate["path"])
        overlap = sorted(description_tokens & path_tokens)
        if len(overlap) >= 2:
            lexical.append((
                len(overlap),
                len(overlap) / max(1, len(path_tokens)),
                candidate,
                overlap,
            ))
    lexical.sort(key=lambda item: (item[0], item[1], -item[2]["id"]), reverse=True)
    if lexical and (len(lexical) == 1 or lexical[0][:2] > lexical[1][:2]):
        best = lexical[0]
        base.update({
            "status": "proposed",
            "evidenceClass": "semantic_path_unique",
            "proposedComposition": {"id": best[2]["id"], "path": best[2]["path"]},
            "evidence": {"overlappingTokens": best[3]},
            "alternatives": [
                {"id": row[2]["id"], "path": row[2]["path"]}
                for row in lexical[1:4]
            ],
        })
        return base
    ordinal = _clip_ordinal(clip["clipId"])
    ordinal_matches = [
        candidate for candidate in candidates
        if ordinal is not None and ordinal in _numbers(candidate["path"].split("/")[-1])
    ]
    if len(ordinal_matches) == 1:
        candidate = ordinal_matches[0]
        base.update({
            "status": "proposed",
            "evidenceClass": "ordinal_terminal_unique",
            "proposedComposition": {"id": candidate["id"], "path": candidate["path"]},
            "evidence": {"clipOrdinal": ordinal},
            "alternatives": [],
        })
        return base
    if len(candidates) == 1:
        candidate = candidates[0]
        base.update({
            "status": "proposed",
            "evidenceClass": "single_output_unique",
            "proposedComposition": {"id": candidate["id"], "path": candidate["path"]},
            "evidence": {"outputCandidateCount": 1},
            "alternatives": [],
        })
        return base
    base["alternatives"] = [
        {"id": row["id"], "path": row["path"]} for row in candidates[:8]
    ]
    return base


def _category(row: dict[str, Any]) -> str:
    value = f"{row['familyId']} {(row['semantic'].get('description') or '')}".lower()
    if "carousel" in value:
        return "carousel"
    if any(token in value for token in ("documentary", "history")):
        return "documentary_multi_scene"
    if any(token in value for token in (
        "text", "title", "typography", "lyric", "counter", "number", "search", "infographic",
    )):
        return "text_data"
    if any(token in value for token in ("screen", "mockup", "contact")):
        return "screen_contact"
    return "slideshow_photo"


def select_prospective_sample(
    rows: list[dict[str, Any]],
    replay_ids: set[str],
    excluded_ids: set[str],
    linked_families: set[str],
    size: int,
) -> list[str]:
    eligible = [
        row for row in rows
        if row["clipId"] not in replay_ids
        and row["clipId"] not in excluded_ids
        and row["familyId"] in linked_families
    ]
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in sorted(eligible, key=lambda item: (item["familyId"], item["clipId"])):
        buckets[_category(row)].append(row)
    categories = [
        "carousel", "documentary_multi_scene", "text_data", "screen_contact", "slideshow_photo",
    ]
    chosen: list[str] = []
    family_counts: Counter[str] = Counter()
    while len(chosen) < size:
        progressed = False
        for category in categories:
            for row in buckets[category]:
                if row["clipId"] in chosen or family_counts[row["familyId"]] >= 2:
                    continue
                chosen.append(row["clipId"])
                family_counts[row["familyId"]] += 1
                progressed = True
                break
            if len(chosen) >= size:
                break
        if not progressed:
            break
    if len(chosen) != size:
        raise ValueError(f"could not select {size} prospective clips; found {len(chosen)}")
    return chosen


def _score_predictions(
    predictions: list[dict[str, Any]],
    gold: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    by_class: dict[str, list[dict[str, Any]]] = defaultdict(list)
    rows: list[dict[str, Any]] = []
    for prediction in predictions:
        answer = gold.get(prediction["clipId"])
        if not answer:
            raise ValueError(f"missing gold label: {prediction['clipId']}")
        proposed = prediction.get("proposedComposition")
        exact = bool(
            proposed
            and proposed["id"] == answer["compositionId"]
            and proposed["path"] == answer["compositionPath"]
        )
        result = {
            "clipId": prediction["clipId"],
            "familyId": prediction["familyId"],
            "evidenceClass": prediction["evidenceClass"],
            "predictionStatus": prediction["status"],
            "proposedComposition": proposed,
            "goldComposition": {
                "id": answer["compositionId"],
                "path": answer["compositionPath"],
            },
            "exactMatch": exact,
        }
        rows.append(result)
        by_class[prediction["evidenceClass"]].append(result)
    classes: dict[str, Any] = {}
    for name, class_rows in sorted(by_class.items()):
        proposed_rows = [row for row in class_rows if row["predictionStatus"] == "proposed"]
        correct = sum(row["exactMatch"] for row in proposed_rows)
        families = sorted({row["familyId"] for row in proposed_rows})
        errors = [row["clipId"] for row in proposed_rows if not row["exactMatch"]]
        precision = correct / len(proposed_rows) if proposed_rows else None
        eligible = bool(
            proposed_rows and not errors and len(proposed_rows) >= 3 and len(families) >= 2
        )
        classes[name] = {
            "predictions": len(proposed_rows),
            "correct": correct,
            "errors": errors,
            "precision": precision,
            "families": families,
            "eligibleAfterReplay": eligible,
        }
    proposed_count = sum(row["predictionStatus"] == "proposed" for row in rows)
    correct_count = sum(row["exactMatch"] for row in rows)
    return {
        "total": len(rows),
        "proposed": proposed_count,
        "abstained": len(rows) - proposed_count,
        "correct": correct_count,
        "errors": proposed_count - correct_count,
        "precision": correct_count / proposed_count if proposed_count else None,
        "coverage": proposed_count / len(rows) if rows else 0,
        "byEvidenceClass": classes,
        "rows": rows,
    }


def _raw_report_index(search_root: Path) -> dict[str, tuple[Path, dict[str, Any]]]:
    reports: dict[str, tuple[Path, dict[str, Any]]] = {}
    patterns = ("**/raw/*.json", "**/raw-static/*.json")
    for pattern in patterns:
        for path in sorted(Path(search_root).glob(pattern)):
            try:
                value = _read(path)
            except (OSError, json.JSONDecodeError):
                continue
            sha = value.get("sourceSha256") if isinstance(value, dict) else None
            compositions = value.get("compositions") if isinstance(value, dict) else None
            if not sha or not isinstance(compositions, list) or not compositions:
                continue
            if not any(isinstance(row, dict) and "layers" in row for row in compositions):
                continue
            current = reports.get(sha)
            native_rank = 1 if "/raw/" in str(path) else 0
            current_rank = 1 if current and "/raw/" in str(current[0]) else 0
            if current is None or native_rank > current_rank:
                reports[sha] = (path, value)
    return reports


def _timeline_label(
    clip: dict[str, Any],
    project: dict[str, Any],
    raw_entry: tuple[Path, dict[str, Any]] | None,
) -> dict[str, Any]:
    if raw_entry is None:
        return {"status": "unresolved", "reason": "raw_native_report_missing"}
    start = clip["semantic"].get("sourceStartSeconds")
    end = clip["semantic"].get("sourceEndSeconds")
    if start is None or end is None:
        return {"status": "unresolved", "reason": "source_timestamps_missing"}
    raw_path, raw = raw_entry
    project_comps = {row["id"]: row for row in project["compositions"]}
    masters: list[tuple[int, dict[str, Any], list[dict[str, Any]]]] = []
    for composition in raw["compositions"]:
        if not isinstance(composition, dict):
            continue
        layers = [
            layer for layer in (composition.get("layers") or [])
            if isinstance(layer, dict)
            and layer.get("enabled", True)
            and layer.get("sourceId") in project_comps
            and layer.get("outPoint", 0) > layer.get("inPoint", 0)
        ]
        distinct = {layer["sourceId"] for layer in layers}
        if len(distinct) < 2:
            continue
        path = (composition.get("path") or composition.get("name") or "").lower()
        name_score = 0
        if "preview" in path:
            name_score = 100
        elif "render" in path:
            name_score = 80
        elif "master" in path:
            name_score = 70
        elif "final" in path:
            name_score = 60
        if not name_score:
            continue
        masters.append((name_score, composition, layers))
    if not masters:
        return {
            "status": "unresolved",
            "reason": "native_master_timeline_missing",
            "rawReport": {"path": str(raw_path), "sha256": _sha(raw_path)},
        }
    masters.sort(key=lambda item: (item[0], item[1].get("duration", 0)), reverse=True)
    best_score = masters[0][0]
    best = [row for row in masters if row[0] == best_score]
    if len(best) != 1:
        return {
            "status": "unresolved",
            "reason": "multiple_native_master_timelines",
            "rawReport": {"path": str(raw_path), "sha256": _sha(raw_path)},
        }
    _, master, layers = best[0]
    midpoint = (float(start) + float(end)) / 2
    active = [
        layer for layer in layers
        if float(layer["inPoint"]) <= midpoint < float(layer["outPoint"])
    ]
    source_ids = sorted({layer["sourceId"] for layer in active})
    if len(source_ids) != 1:
        return {
            "status": "unresolved",
            "reason": "native_timeline_not_unique_at_clip_midpoint",
            "midpointSeconds": midpoint,
            "activeSourceIds": source_ids,
            "masterComposition": {"id": master.get("id"), "path": master.get("path")},
            "rawReport": {"path": str(raw_path), "sha256": _sha(raw_path)},
        }
    composition = project_comps[source_ids[0]]
    return {
        "status": "timeline_label",
        "composition": {"id": composition["id"], "path": composition["path"]},
        "midpointSeconds": midpoint,
        "masterComposition": {"id": master.get("id"), "path": master.get("path")},
        "rawReport": {"path": str(raw_path), "sha256": _sha(raw_path)},
    }


def build_report(request: dict[str, Any]) -> dict[str, Any]:
    validate_request(request)
    rows, links, projects = _load_prediction_inputs(request)
    by_clip = {row["clipId"]: row for row in rows}
    replay_ids = request["replaySceneIds"]
    missing = sorted(set(replay_ids) - set(by_clip))
    if missing:
        raise ValueError(f"replay clips absent from semantic inputs: {missing}")
    replay_predictions = [
        predict_clip(by_clip[clip_id], links.get(by_clip[clip_id]["familyId"]), projects)
        for clip_id in replay_ids
    ]
    gold_doc = _read(_resolve(request["evaluationSources"]["verifiedMappings"]["path"]))
    gold = {row["sceneId"]: row for row in gold_doc["mappings"]}
    replay = _score_predictions(replay_predictions, gold)

    sample_ids = select_prospective_sample(
        rows,
        set(replay_ids),
        set(request.get("prospectiveExcludedIds") or []),
        set(links),
        int(request["prospectiveSampleSize"]),
    )
    prospective_predictions = [
        predict_clip(by_clip[clip_id], links.get(by_clip[clip_id]["familyId"]), projects)
        for clip_id in sample_ids
    ]
    prediction_lock_sha256 = hashlib.sha256(
        json.dumps(
            prospective_predictions,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    raw_index = _raw_report_index(Path(request["nativeReportSearchRoot"]))
    prospective_rows: list[dict[str, Any]] = []
    class_metrics: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"predictions": 0, "labeled": 0, "correct": 0, "errors": []}
    )
    for prediction in prospective_predictions:
        clip = by_clip[prediction["clipId"]]
        link = links.get(clip["familyId"])
        project = projects.get(link.get("projectId")) if link else None
        label = (
            _timeline_label(clip, project, raw_index.get(project["sourceProjectSha256"]))
            if project else {"status": "unresolved", "reason": "project_not_linked"}
        )
        proposed = prediction.get("proposedComposition")
        exact = None
        if proposed and label["status"] == "timeline_label":
            exact = proposed == label["composition"]
        row = {
            **prediction,
            "category": _category(clip),
            "nativeTimelineEvaluation": label,
            "exactMatchWhenLabeled": exact,
        }
        prospective_rows.append(row)
        if prediction["status"] == "proposed":
            metric = class_metrics[prediction["evidenceClass"]]
            metric["predictions"] += 1
            if exact is not None:
                metric["labeled"] += 1
                metric["correct"] += int(exact)
                if not exact:
                    metric["errors"].append(prediction["clipId"])
    prospective_classes: dict[str, Any] = {}
    for name, metric in sorted(class_metrics.items()):
        precision = metric["correct"] / metric["labeled"] if metric["labeled"] else None
        replay_class = replay["byEvidenceClass"].get(name, {})
        trusted = bool(
            replay_class.get("eligibleAfterReplay")
            and metric["labeled"] >= 3
            and not metric["errors"]
        )
        prospective_classes[name] = {
            **metric,
            "precisionOnTimelineLabeledSubset": precision,
            "trusted": trusted,
        }
    trusted_classes = sorted(
        name for name, metric in prospective_classes.items() if metric["trusted"]
    )
    return {
        "schemaVersion": 1,
        "activationState": "calibration_review_only",
        "promoteMappings": False,
        "renderingAuthorized": False,
        "sourceHashes": {
            group: {
                name: source["sha256"] for name, source in request[group].items()
            }
            for group in ("predictorSources", "evaluationSources")
        },
        "guardrails": {
            "predictorReadsVerifiedMappings": False,
            "predictionsCanEmitVerified": False,
            "precisionRequired": 1.0,
            "minimumReplayPredictionsPerClass": 3,
            "minimumReplayFamiliesPerClass": 2,
            "minimumProspectiveTimelineLabelsPerClass": 3,
        },
        "replay": replay,
        "prospective": {
            "sampleSize": len(sample_ids),
            "sampleIds": sample_ids,
            "predictionLockSha256": prediction_lock_sha256,
            "categoryCounts": dict(sorted(Counter(row["category"] for row in prospective_rows).items())),
            "predictions": prospective_rows,
            "byEvidenceClass": prospective_classes,
        },
        "decision": {
            "trustedEvidenceClasses": trusted_classes,
            "bulkMappingTrusted": bool(trusted_classes),
            "nextSafeBatchSize": 0 if not trusted_classes else 30,
            "reason": (
                "At least one structural evidence class passed both replay and prospective gates."
                if trusted_classes else
                "No evidence class passed the zero-error replay and prospective gates; bulk mapping remains proposal-only."
            ),
        },
    }


def validate_report(report: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    expected = build_report(request)
    if report != expected:
        raise ValueError("saved calibration report differs from deterministic rebuild")
    if any(
        row.get("status") not in {"proposed", "abstain"}
        for row in [
            *report["prospective"]["predictions"],
        ]
    ):
        raise ValueError("calibration prediction emitted a prohibited status")
    for name in report["decision"]["trustedEvidenceClasses"]:
        replay = report["replay"]["byEvidenceClass"][name]
        prospective = report["prospective"]["byEvidenceClass"][name]
        if replay["errors"] or prospective["errors"]:
            raise ValueError("evidence class with an error cannot be trusted")
    return {
        "replayTotal": report["replay"]["total"],
        "replayProposed": report["replay"]["proposed"],
        "replayErrors": report["replay"]["errors"],
        "prospectiveSample": report["prospective"]["sampleSize"],
        "trustedEvidenceClasses": report["decision"]["trustedEvidenceClasses"],
        "bulkMappingTrusted": report["decision"]["bulkMappingTrusted"],
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "validate"))
    parser.add_argument("--request", type=Path, default=DEFAULT_REQUEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    request = _read(args.request)
    if args.command == "build":
        report = build_report(request)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(dumps(report))
        print(dumps(validate_report(report, request)), end="")
    else:
        print(dumps(validate_report(_read(args.output), request)), end="")


if __name__ == "__main__":
    main()
