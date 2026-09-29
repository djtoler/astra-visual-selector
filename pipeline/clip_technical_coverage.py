"""Build a deterministic clip-level technical-coverage ledger.

The ledger is deliberately descriptive.  It does not activate matching and it
never substitutes a family or project envelope for an exact composition map.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLISH_ROOT = ROOT.parent
REVIEW_CATALOG = POLISH_ROOT / "ae-template-automation/selector-prototype/intake/review-catalog.json"
APPROVED_CATALOG = POLISH_ROOT / "ae-template-automation/scene-library/approved/catalog.json"
APPROVED_POLICY = POLISH_ROOT / "ae-template-automation/scene-library/approved-catalog-policy.json"
SPEC_LINKS = ROOT / "grammar/ae-template-spec-links.json"
SCENE_MAPPINGS = ROOT / "grammar/ae-scene-composition-mappings.json"
TECHNICAL_INDEX = ROOT / "grammar/ae-template-technical-index.json"
PILOT = ROOT / "reports/carousel-slideshow-clip-native-pilot.json"
OUTPUT = ROOT / "reports/ae-clip-technical-coverage.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source(path: Path) -> dict:
    return {"path": str(path), "sha256": _sha256(path)}


def _semantic_rows(review: dict, approved: dict) -> list[dict]:
    rows: list[dict] = []
    for scene in review["scenes"]:
        rows.append(
            {
                "clipId": scene["id"],
                "familyId": scene["sourceId"],
                "semanticCatalog": "review_catalog",
                "semantic": {
                    "description": scene.get("description"),
                    "previewPath": scene.get("clip"),
                    "sourcePreviewPath": scene.get("sourcePath"),
                    "sourceStartSeconds": scene.get("sourceStartSeconds"),
                    "sourceEndSeconds": scene.get("sourceEndSeconds"),
                    "previewDurationSeconds": scene.get("durationSeconds"),
                },
                "availability": {
                    "status": scene.get("availabilityStatus", "unknown"),
                    "reason": (scene.get("availabilityReview") or {}).get("reason"),
                },
            }
        )
    for template in approved["afterEffects"]:
        for scene in template["scenes"]:
            rows.append(
                {
                    "clipId": scene["id"],
                    "familyId": template["templateId"],
                    "semanticCatalog": "approved_catalog",
                    "semantic": {
                        "description": scene.get("description"),
                        "previewPath": scene.get("video"),
                        "sourcePreviewPath": None,
                        "sourceStartSeconds": None,
                        "sourceEndSeconds": None,
                        "previewDurationSeconds": scene.get("durationSeconds"),
                    },
                    "availability": {
                        "status": "available_for_use",
                        "reason": "Present in the approved After Effects catalog.",
                    },
                }
            )
    return rows


def build_coverage(
    *,
    review_catalog_path: Path = REVIEW_CATALOG,
    approved_catalog_path: Path = APPROVED_CATALOG,
    approved_policy_path: Path = APPROVED_POLICY,
    spec_links_path: Path = SPEC_LINKS,
    scene_mappings_path: Path = SCENE_MAPPINGS,
    technical_index_path: Path = TECHNICAL_INDEX,
    pilot_path: Path = PILOT,
) -> dict:
    paths = [
        Path(review_catalog_path),
        Path(approved_catalog_path),
        Path(approved_policy_path),
        Path(spec_links_path),
        Path(scene_mappings_path),
        Path(technical_index_path),
        Path(pilot_path),
    ]
    review, approved, policy, links_doc, mappings_doc, technical_index, pilot = map(_load, paths)

    rows = _semantic_rows(review, approved)
    clip_ids = [row["clipId"] for row in rows]
    duplicates = sorted(clip_id for clip_id, count in Counter(clip_ids).items() if count > 1)
    if duplicates:
        raise ValueError(f"duplicate clip ids across semantic catalogs: {duplicates}")

    links = {row["familyId"]: row for row in links_doc["links"]}
    projects = {row["id"]: row for row in technical_index["projects"]}
    unknown_projects = sorted(
        {row["projectId"] for row in links.values()} - set(projects)
    )
    if unknown_projects:
        raise ValueError(f"family links refer to unknown technical projects: {unknown_projects}")
    mappings = {row["sceneId"]: row for row in mappings_doc["mappings"]}
    if len(mappings) != len(mappings_doc["mappings"]):
        raise ValueError("duplicate scene mappings")
    pilots = {row["clipId"]: row for row in pilot["clips"]}
    if not set(mappings).issubset(clip_ids) or not set(pilots).issubset(clip_ids):
        raise ValueError("mapping refers to a clip outside the semantic catalogs")

    excluded_sources = {
        row["sourceId"]: row for row in policy.get("excludedSources", [])
    }
    records: list[dict] = []
    for row in sorted(rows, key=lambda item: item["clipId"]):
        family_id = row["familyId"]
        link = links.get(family_id)
        mapping = mappings.get(row["clipId"])
        pilot_row = pilots.get(row["clipId"])

        if family_id == "archive3-carousel-galleries-loop-animation-2":
            technical = {
                "state": "mogrt_not_aep",
                "projectId": None,
                "composition": None,
                "window": None,
                "evidence": excluded_sources[family_id]["reason"],
            }
        elif pilot_row:
            technical = {
                "state": "mapped_composition_window_approximate",
                "projectId": pilot_row["native"]["projectId"],
                "composition": pilot_row["native"]["composition"],
                "window": pilot_row["native"]["window"],
                "evidence": "Validated Carousel Slideshow pilot; composition exact, native window approximate.",
            }
        elif mapping and mapping["status"] == "verified":
            technical = {
                "state": "mapped_verified",
                "projectId": mapping["projectId"],
                "composition": {
                    "id": mapping["compositionId"],
                    "path": mapping["compositionPath"],
                },
                "window": None,
                "evidence": mapping.get("evidence"),
            }
        elif mapping:
            technical = {
                "state": "mapping_ambiguous",
                "projectId": mapping.get("projectId") or (link or {}).get("projectId"),
                "composition": None,
                "window": None,
                "evidence": mapping.get("evidence"),
            }
        elif link:
            technical = {
                "state": "mapping_unverified",
                "projectId": link["projectId"],
                "composition": None,
                "window": None,
                "evidence": link.get("linkEvidence"),
            }
        else:
            technical = {
                "state": "project_unlinked",
                "projectId": None,
                "composition": None,
                "window": None,
                "evidence": None,
            }

        project_id = technical.get("projectId")
        if project_id:
            if project_id not in projects:
                raise ValueError(f"mapping refers to unknown technical project: {project_id}")
            project = projects[project_id]
            technical["projectEvidence"] = {
                "sourceProjectName": project.get("sourceProjectName"),
                "sourceProjectSha256": project.get("sourceProjectSha256"),
                "evidenceStatus": project.get("evidenceStatus"),
                "resultStatus": project.get("resultStatus"),
            }
        else:
            technical["projectEvidence"] = None

        if family_id in excluded_sources:
            decision = excluded_sources[family_id]
            row["availability"] = {
                "status": "excluded",
                "reason": decision["reason"],
                "decisionDate": decision.get("decisionDate"),
            }
        row["technical"] = technical
        records.append(row)

    state_counts = Counter(row["technical"]["state"] for row in records)
    catalog_counts = Counter(row["semanticCatalog"] for row in records)
    family_ids = sorted({row["familyId"] for row in records})
    availability_counts = Counter(row["availability"]["status"] for row in records)
    return {
        "schemaVersion": 1,
        "activationState": "coverage_review_only",
        "sources": {
            "reviewCatalog": _source(paths[0]),
            "approvedCatalog": _source(paths[1]),
            "approvedCatalogPolicy": _source(paths[2]),
            "technicalFamilyLinks": _source(paths[3]),
            "sceneCompositionMappings": _source(paths[4]),
            "technicalIndex": _source(paths[5]),
            "carouselSlideshowPilot": _source(paths[6]),
        },
        "scope": {
            "definition": "Union of every After Effects scene in the current approved catalog and every scene in the current intake review catalog, including explicit exclusions.",
            "clipCount": len(records),
            "familyCount": len(family_ids),
            "familyIds": family_ids,
        },
        "counts": {
            "clips": len(records),
            "families": len(family_ids),
            "bySemanticCatalog": dict(sorted(catalog_counts.items())),
            "byAvailability": dict(sorted(availability_counts.items())),
            "byTechnicalState": dict(sorted(state_counts.items())),
        },
        "clips": records,
    }


def validate_coverage(ledger: dict) -> dict:
    if ledger.get("schemaVersion") != 1:
        raise ValueError("unsupported technical coverage schema")
    if ledger.get("activationState") != "coverage_review_only":
        raise ValueError("coverage ledger must not activate matching")
    records = ledger.get("clips", [])
    ids = [row.get("clipId") for row in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate clip id")
    if ids != sorted(ids):
        raise ValueError("coverage ledger must be sorted by clip id")
    allowed_states = {
        "mapped_verified",
        "mapped_composition_window_approximate",
        "mapping_ambiguous",
        "mapping_unverified",
        "project_unlinked",
        "mogrt_not_aep",
    }
    for row in records:
        state = row.get("technical", {}).get("state")
        if state not in allowed_states:
            raise ValueError(f"invalid technical state: {row.get('clipId')}")
        composition = row["technical"].get("composition")
        if state.startswith("mapped_") and not composition:
            raise ValueError(f"mapped clip lacks a composition: {row['clipId']}")
        if state in {"mapping_unverified", "project_unlinked", "mogrt_not_aep"} and composition:
            raise ValueError(f"unverified clip carries composition capacity: {row['clipId']}")
    expected = build_coverage()
    if ledger != expected:
        raise ValueError("coverage ledger is stale or differs from deterministic source build")
    return ledger["counts"]


def write_coverage(path: Path = OUTPUT) -> dict:
    ledger = build_coverage()
    validate_coverage(ledger)
    Path(path).write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
    return ledger


if __name__ == "__main__":
    write_coverage()
