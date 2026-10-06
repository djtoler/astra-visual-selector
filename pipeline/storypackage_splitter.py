#!/usr/bin/env python3
"""Derive review-only VisualTask proposals from validated StoryPackage job proposals."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from collections import Counter, defaultdict

try:
    from .matching_contract_gate import enforce_contracts
except ImportError:
    from matching_contract_gate import enforce_contracts


QUESTION_WORDS = ("who ", "what ", "why ", "how ", "when ", "where ", "which ", "is ", "are ", "can ", "could ", "did ", "does ", "would ", "should ")
CONTRAST_STARTS = ("but ", "however ", "yet ", "meanwhile ", "instead ", "on the other hand ")
OPERATION_PRIORITY = (
    "lyric_presentation", "transformation", "relationship_intro",
    "evidence_presentation", "comparison", "data_explanation", "item_sequence",
    "subject_profile", "milestone_reveal", "archival_progression",
    "event_narration", "rhetorical_question", "concept_statement",
)


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _presentation_operations(*, text: str, claim_rows: list[dict[str, Any]]) -> list[str]:
    """Derive reusable visual operations without naming a template or family."""
    lowered = " ".join(text.lower().split())
    refs = set().union(*(_display_entities(row) for row in claim_rows)) if claim_rows else set()
    values = [value for row in claim_rows for value in row.get("values") or []]
    cohorts = [ref for row in claim_rows for ref in row.get("cohortRefs") or []]
    operations: list[str] = []
    if any(term in lowered for term in (
        "the lyrics", "these lyrics", "lyric says", "lyrics say", "the hook:",
        "comes in with the hook", "song starts out with", "verse starts",
    )):
        operations.append("lyric_presentation")
    if (re.search(r"\b(?:go|went|going|move|moved|moving|transition|transitioned|evolve|evolved|rise|rose|fall|fell)\b.{0,35}\bfrom\b.{1,80}\bto\b", lowered) or
            re.search(r"\bbefore\b.{0,80}\b(?:understand|know)\b.{0,80}\bmeet\b", lowered) or
            any(term in lowered for term in (
                "before and after", "used to be", "became known as", "turned into",
                "transformed into", "meet his former", "meet her former",
            ))):
        operations.append("transformation")
    if ("who is " in lowered or "who was " in lowered or "his name was " in lowered or
            "her name was " in lowered or "known as " in lowered or "meet " in lowered):
        operations.append("subject_profile")
    if any(term in lowered for term in (
        " cousin", " friend", " father", " mother", " mentor", " relationship",
        "worked with", "working with", "met him", "met her", "took me in",
    )) and len(refs) >= 1:
        operations.append("relationship_intro")
    if (cohorts or len(refs) >= 3 or any(term in lowered for term in (
        "roster", "list of", "a total of", "each of", "all of them",
        "these artists", "those artists", "people like", "members included",
        "track list", "the following", "one by one", "these mixtapes",
        "these albums", "these releases", "both songs", "both tracks",
    ))):
        operations.append("item_sequence")
    if any(term in lowered for term in (
        " years later", "months later", "before long", "over the next", "eventually",
        "later ", "then ", "after ", "before ", "from 19", "from 20", "in 19", "in 20",
        "dropped out", "released", "signed",
    )) or ("grew up" in lowered and not re.search(r"\bif you grew up\b", lowered)):
        operations.append("archival_progression")
    if any(term in lowered for term in (
        "according to", "wikipedia", "reddit", "article", "interview", "footage",
        "you just heard", "the quote", "the caption", "the lyrics", "the song starts",
        "track list", "critics", "mockery", "reviewers",
    )) or re.search(r"\bheadlines?\b", lowered):
        operations.append("evidence_presentation")
    if any(term in lowered for term in (
        "finally", "cemented", "breakthrough", "became", "made it", "number one",
        "ready", "first time", "the top", "iconic", "biggest", "most streamed",
    )):
        operations.append("milestone_reveal")
    quantitative_terms = (
        "percent", "percentage", "streamed", "streams", "monthly listeners",
        "rank", "ranking", "number one", "number two", "top ",
        "total", "combined", "less than", "million", "billion",
        "zero ", "times",
    )
    quantified_fans = bool(re.search(r"\b(?:\d[\d,.]*|hundred|thousand|million|billion)\s+(?:\w+\s+)?fans\b", lowered))
    if values or cohorts or quantified_fans or any(re.search(r"\b" + re.escape(term.strip()) + r"\b", lowered) for term in quantitative_terms):
        operations.append("data_explanation")
    if len(refs) >= 2 and "more than a little" not in lowered and any(term in lowered for term in (
        "more than", "less than", "against", "versus", "compared", "outweigh",
        "bigger than", "same as", "different from",
    )):
        operations.append("comparison")
    stripped = lowered.lstrip("'\"“”")
    if "?" in text:
        operations.append("rhetorical_question")
    if any(term in lowered for term in (
        "was ", "were ", "happened", "went ", "came ", "got ", "shot ", "died",
        "lost ", "won ", "made ", "created ", "recorded ", "joined ",
        "dropped out",
    )) or re.search(r"\bleft\s+(?!floor\b|panel\b|side\b|column\b|axis\b|threshold\b|bound\b)", lowered):
        operations.append("event_narration")
    if not operations:
        operations.append("concept_statement")
    return _unique(operations)


def _derived_job(*, text: str, claim_rows: list[dict[str, Any]], operations: list[str]) -> str:
    lowered = text.lower()
    refs = set().union(*(_display_entities(row) for row in claim_rows)) if claim_rows else set()
    values = [value for row in claim_rows for value in row.get("values") or []]
    cohorts = [ref for row in claim_rows for ref in row.get("cohortRefs") or []]
    if "rhetorical_question" in operations:
        return "pose_a_question"
    if cohorts:
        return "proportion_of_cohort" if values else "enumerate"
    if values and len(refs) > 1:
        return "parallel_instances"
    if values:
        return "derived_quantity"
    if "item_sequence" in operations:
        return "enumerate"
    if "archival_progression" in operations or "event_narration" in operations:
        return "narrate_an_event"
    if any(term in lowered for term in ("means ", "defined as", "refers to", "the rule", "in other words")):
        return "define_terms"
    return "assert_without_data"


def _display_entities(claim: dict[str, Any]) -> set[str]:
    return {
        ref.get("entity") for ref in claim.get("entityRefs") or []
        if ref.get("entity") and ref.get("display") in {"required", "eligible"}
    }


def _payload_signature(rows: list[dict[str, Any]]) -> tuple[Any, ...]:
    # Numeric magnitude alone may vary within one coherent rank/cohort display.
    # Unit, measure label, basis/role, and represented medium cannot vary silently.
    measures = sorted({(str(v.get("unit")), str(v.get("label")), str(v.get("basis")))
                       for row in rows for v in row.get("values") or []})
    cohorts = sorted({json.dumps(ref, sort_keys=True) for row in rows for ref in row.get("cohortRefs") or []})
    return tuple(measures), tuple(cohorts)


def _representations_conflict(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> bool:
    def represented(rows):
        return {ref["entity"]: set(ref["representedBy"]) for row in rows
                for ref in row.get("entityRefs") or [] if ref.get("entity") and ref.get("representedBy")}
    a, b = represented(left), represented(right)
    return any(not (a[entity] & b[entity]) for entity in a.keys() & b.keys())


def _materialize_span(adapter: dict[str, Any], claim_rows: list[dict[str, Any]], span: dict[str, Any]) -> str:
    start, length = span.get("start"), span.get("len")
    if type(start) is not int or type(length) is not int or start < 0 or length <= 0:
        raise ValueError("proposal source span requires nonnegative codepoint start and positive length")
    end = start + length
    script = (adapter.get("script") or {}).get("text")
    intervals = []
    for row in claim_rows:
        source = row.get("span") or {}
        lo, size = source.get("start"), source.get("len")
        if type(lo) is not int or type(size) is not int or lo < 0 or size <= 0 or len(row.get("text", "")) != size:
            raise ValueError("claim source span/text is invalid")
        if script is not None and script[lo:lo + size] != row["text"]:
            raise ValueError("claim text differs from bound script span")
        intervals.append((lo, lo + size, row["text"]))
    if not intervals or start < min(lo for lo, _, _ in intervals) or end > max(hi for _, hi, _ in intervals):
        raise ValueError("proposal span exceeds intended source claims")
    result = []
    for position in range(start, end):
        chars = {text[position - lo] for lo, hi, text in intervals if lo <= position < hi}
        if len(chars) > 1:
            raise ValueError("overlapping source claim text conflicts")
        if chars:
            result.append(next(iter(chars)))
        elif script is not None and position < len(script) and script[position].isspace():
            result.append(script[position])
        else:
            raise ValueError("proposal span includes unbound source characters")
    return "".join(result)


def _primary_operation(text: str, claim_rows: list[dict[str, Any]]) -> str:
    operations = _presentation_operations(text=text, claim_rows=claim_rows)
    if ("rhetorical_question" in operations and
            not any(operation in operations for operation in (
                "subject_profile", "relationship_intro", "evidence_presentation",
                "lyric_presentation",
            ))):
        return "rhetorical_question"
    lowered = text.lower()
    if ("event_narration" in operations and
            any(term in lowered for term in ("shot ", "died", "dropped out", "lost ", "won ")) and
            not any(operation in operations for operation in (
                "lyric_presentation", "transformation", "relationship_intro",
                "evidence_presentation", "comparison", "data_explanation", "item_sequence",
            ))):
        return "event_narration"
    return next((operation for operation in OPERATION_PRIORITY if operation in operations), operations[0])


def _split_claim_segments(claim: dict[str, Any]) -> list[dict[str, Any]]:
    """Split a claim only at a strong, source-exact visual pivot."""
    text = claim.get("text", "")
    # "not just X, but also Y" changes the visual payload from the first scope
    # to the enlarged second scope. Keep both source spans exact and readable.
    match = re.search(r",\s+(?=but\s+also\b)", text, flags=re.IGNORECASE)
    if not match or "not just" not in text[:match.start()].lower():
        return [{"claimIds": [claim["claimId"]], "text": text, "span": claim.get("span"),
                 "strongBoundary": False}]
    pieces = [(0, match.end()), (match.end(), len(text))]
    rows = []
    source_span = claim.get("span") or {}
    for start, end in pieces:
        segment = text[start:end]
        absolute_start = source_span.get("start")
        span = None
        if absolute_start is not None:
            span = {"start": absolute_start + start, "len": len(segment)}
        rows.append({"claimIds": [claim["claimId"]], "text": segment, "span": span,
                     "strongBoundary": True})
    return rows


def _semantic_units(*, beat: dict[str, Any], claim_ids: list[str],
                    claims: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Derive review-sized visual moments inside one narrator beat.

    Claim boundaries are evidence, not automatic task boundaries. Adjacent
    claims with one visual payload merge; a claim may split at a strong scope
    expansion. Punctuation alone never creates a task.
    """
    atomic = [segment for claim_id in claim_ids
              for segment in _split_claim_segments(claims[claim_id])]
    units: list[dict[str, Any]] = []
    for segment in atomic:
        if units:
            prior = units[-1]
            prior_rows = [claims[claim_id] for claim_id in prior["claimIds"]]
            current_rows = [claims[claim_id] for claim_id in segment["claimIds"]]
            prior_text = prior["text"].strip()
            current_text = segment["text"].strip()
            shared_entities = set().union(*(_display_entities(row) for row in prior_rows)) & set().union(
                *(_display_entities(row) for row in current_rows))
            question_setup_pair = bool(
                prior_text.endswith("?") and shared_entities and
                len(prior_text) + len(current_text) <= 100 and
                _payload_signature(prior_rows) == _payload_signature(current_rows) and
                not _representations_conflict(prior_rows, current_rows) and
                current_text.lower().startswith(("well ", "well,", "of course ", "you ", "that ", "this "))
            )
            prior_entities = set().union(*(_display_entities(row) for row in prior_rows))
            current_entities = set().union(*(_display_entities(row) for row in current_rows))
            same_payload = bool(
                not prior.get("strongBoundary") and not segment.get("strongBoundary") and
                not current_text.lower().startswith(CONTRAST_STARTS) and
                _primary_operation(prior_text, prior_rows) == _primary_operation(current_text, current_rows) and
                _payload_signature(prior_rows) == _payload_signature(current_rows) and
                not _representations_conflict(prior_rows, current_rows) and
                len(prior_text) + len(current_text) <= 260 and
                (bool(prior_entities & current_entities) or (not prior_entities and not current_entities))
            )
            if question_setup_pair or same_payload:
                prior["claimIds"] = _unique(prior["claimIds"] + segment["claimIds"])
                prior["text"] = f"{prior_text} {current_text}"
                if prior.get("span") and segment.get("span"):
                    start = prior["span"]["start"]
                    end = segment["span"]["start"] + segment["span"]["len"]
                    prior["span"] = {"start": start, "len": end - start}
                continue
        units.append(dict(segment))
    if units and all(unit.get("span") for unit in units):
        beat_span = beat.get("span") or {}
        full_beat = (
            claim_ids == list(beat.get("claimIds") or []) and
            isinstance(beat_span.get("start"), int) and isinstance(beat_span.get("len"), int)
        )
        range_start = beat_span.get("start") if full_beat else units[0]["span"]["start"]
        range_end = (beat_span.get("start", 0) + beat_span.get("len", 0)) if full_beat else (
            units[-1]["span"]["start"] + units[-1]["span"]["len"])
        narration = beat.get("narration", "")
        for index, unit in enumerate(units):
            start = range_start if index == 0 else unit["span"]["start"]
            end = units[index + 1]["span"]["start"] if index + 1 < len(units) else range_end
            unit["span"] = {"start": start, "len": end - start}
            if full_beat:
                local_start = start - beat_span["start"]
                local_end = end - beat_span["start"]
                unit["text"] = narration[local_start:local_end]
        if full_beat and "".join(unit["text"] for unit in units) != narration:
            raise ValueError(f"semantic task spans do not reconstruct source beat: {beat.get('beatId')}")
    return units


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(adapter: dict[str, Any], *, source_path: Path) -> dict[str, Any]:
    contract_receipt = enforce_contracts("storypackage_splitter.build")
    receipt = adapter.get("storyHandoffReceipt") or {}
    if receipt.get("accepted") is not True:
        raise ValueError("splitter requires an accepted StoryPackage adapter receipt")
    if adapter.get("selectionAuthorized") is not False or adapter.get("renderingAuthorized") is not False:
        raise ValueError("StoryPackage adapter cannot authorize selection or rendering")
    try:
        from .storypackage_adapter import validate as validate_adapter
    except ImportError:
        from storypackage_adapter import validate as validate_adapter
    adapter_validation = validate_adapter(adapter, source_path=source_path)

    claims = {row["claimId"]: row for row in adapter.get("claims") or []}
    beats = {row["beatId"]: row for row in adapter.get("beats") or []}
    obligations = adapter.get("obligations") or []
    continuity = adapter.get("continuity") or []
    covered: set[str] = set()
    tasks = []

    def task_from_claims(*, task_id: str, proposal_id: str, job: str,
                         provenance: dict[str, Any], claim_ids: list[str],
                         proposal_span: dict[str, Any] | None = None,
                         task_text: str | None = None,
                         speaker_derived: bool = False,
                         semantic_derived: bool = False,
                         advisory_proposal_ids: list[str] | None = None) -> dict[str, Any]:
        missing = [claim_id for claim_id in claim_ids if claim_id not in claims]
        if missing:
            raise ValueError(f"job proposal references unknown claims: {missing}")
        claim_rows = [claims[claim_id] for claim_id in claim_ids]
        beat_ids = list(dict.fromkeys(row["beatId"] for row in claim_rows))
        source_beats = []
        for beat_id in beat_ids:
            beat = beats.get(beat_id) or {}
            source_beats.append({
                "beatId": beat_id,
                "speaker": beat.get("speaker") or {"role": "narrator"},
                "section": beat.get("section"),
                "span": beat.get("span"),
            })
        exact_text = (task_text if task_text is not None else
                      _materialize_span(adapter, claim_rows, proposal_span) if proposal_span is not None else
                      " ".join(row.get("text", "") for row in claim_rows))
        presentation_operations = _presentation_operations(text=exact_text, claim_rows=claim_rows)
        primary_operation = _primary_operation(exact_text, claim_rows)
        # A supported structured relationship is stronger than incidental verbs
        # in its prose. Use existing operations without changing Story's job.
        source_operation = {"intersection_of_sets": "data_explanation",
                            "proportion_of_cohort": "data_explanation"}.get(job)
        if source_operation:
            presentation_operations = _unique(presentation_operations + [source_operation])
            primary_operation = source_operation
        route_disposition = {
            # A rhetorical question may ultimately use only B-roll/cutout, but
            # semantics alone cannot suppress existing text-capable templates.
            # Preserve both routes until exact editor evidence decides otherwise.
            "templateEligible": True,
            "brollFallbackAvailable": True,
            "preferredTreatment": (
                "template_or_broll_with_text_question"
                if primary_operation == "rhetorical_question"
                else "template_or_broll"
            ),
            "reason": (
                "unreviewed_question_route_preserves_template_and_broll_options"
                if primary_operation == "rhetorical_question"
                else "template_and_broll_options_preserved"
            ),
            "mixedPayloadReviewRequired": len(presentation_operations) > 1,
            "selectionAuthorized": False,
            "renderingAuthorized": False,
        }
        return {
            "taskProposalId": task_id,
            "jobProposalId": proposal_id,
            "job": job,
            "jobProvenance": provenance,
            "claimIds": claim_ids,
            "reviewKeys": sorted({
                key for row in claim_rows for key in row.get("reviewKeys") or []
            }),
            "claimSpans": [
                {"claimId": row["claimId"], "beatId": row["beatId"], "span": row["span"]}
                for row in claim_rows
            ],
            "proposalSpan": proposal_span,
            "taskText": exact_text,
            "lanes": [{"claimId": row["claimId"], "lane": row["lane"]} for row in claim_rows],
            "entityRefs": [
                {"claimId": row["claimId"], **ref}
                for row in claim_rows for ref in row.get("entityRefs") or []
            ],
            "cohortRefs": [
                {"claimId": row["claimId"], **ref}
                for row in claim_rows for ref in row.get("cohortRefs") or []
            ],
            "values": [
                {"claimId": row["claimId"], **value}
                for row in claim_rows for value in row.get("values") or []
            ],
            "obligations": [
                row for row in obligations if set(row["claimIds"]) & set(claim_ids)
            ],
            "continuity": [
                row for row in continuity if set(row["claimIds"]) & set(claim_ids)
            ],
            "sourceBeats": source_beats,
            "speakerDerived": speaker_derived,
            "semanticDerived": semantic_derived,
            "advisoryJobProposalIds": advisory_proposal_ids or [],
            "presentationOperations": presentation_operations,
            "primaryPresentationOperation": primary_operation,
            "routeDisposition": route_disposition,
            "semanticDerivation": {
                "source": "matching_semantic_splitter" if semantic_derived else "story_job_proposal_plus_matching_context",
                "templateNeutral": True,
                "templateSelected": False,
            },
            "activationState": "proposal_requires_editor_review",
        }

    proposals = adapter.get("jobProposals") or []
    proposal_count_by_claim = Counter(
        claim_id for proposal in proposals for claim_id in proposal.get("claimIds", []))
    proposal_jobs_by_beat: dict[str, set[str]] = defaultdict(set)
    for proposal in proposals:
        for claim_id in proposal.get("claimIds", []):
            proposal_jobs_by_beat[claims[claim_id]["beatId"]].add(proposal.get("job"))
    advisory_by_beat: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for proposal in proposals:
        claim_ids = proposal["claimIds"]
        proposal_beat_ids = _unique([claims[claim_id]["beatId"] for claim_id in claim_ids])
        full_beat_claim_ids = _unique([
            claim_id for beat_id in proposal_beat_ids
            for claim_id in (beats.get(beat_id) or {}).get("claimIds", [])
        ])
        materialize = bool(
            proposal.get("span") or len(claim_ids) > 1 or
            any(proposal_count_by_claim[claim_id] > 1 for claim_id in claim_ids) or
            any(len(proposal_jobs_by_beat[beat_id]) > 1 for beat_id in proposal_beat_ids) or
            set(claim_ids) == set(full_beat_claim_ids)
        )
        if not materialize:
            for beat_id in proposal_beat_ids:
                advisory_by_beat[beat_id].append(proposal)
            continue
        covered.update(claim_ids)
        tasks.append(task_from_claims(
            task_id=f"{adapter['story']['storyId']}.proposal.{proposal['proposalId']}",
            proposal_id=proposal["proposalId"],
            job=proposal["job"],
            provenance=proposal["provenance"],
            claim_ids=claim_ids,
            proposal_span=proposal.get("span"),
        ))

    gaps = list(adapter.get("gaps") or [])
    for claim_id, claim in claims.items():
        if claim.get("status") == "unverified":
            gaps.append({"gap": "source_fact_unverified", "claim": claim_id,
                         "reason": "Source claim is unverified; semantic materialization does not verify its facts or resolve its alternatives."})
    speaker_routes = []
    for beat in sorted(beats.values(), key=lambda row: row.get("order", 0)):
        speaker = beat.get("speaker") or {"role": "narrator"}
        role = speaker.get("role", "narrator")
        claim_ids = beat.get("claimIds") or []
        if role == "quote":
            uncovered = [claim_id for claim_id in claim_ids if claim_id not in covered]
            if uncovered:
                proposal_id = f"speaker-quote-{beat['beatId']}"
                tasks.append(task_from_claims(
                    task_id=f"{adapter['story']['storyId']}.proposal.{proposal_id}",
                    proposal_id=proposal_id,
                    job="attributed_quote",
                    provenance={
                        "source": "validated_speaker_role",
                        "reviewState": "proposed",
                    },
                    claim_ids=uncovered,
                    proposal_span=beat.get("span"),
                    speaker_derived=True,
                ))
                covered.update(uncovered)
            speaker_routes.append({
                "beatId": beat["beatId"],
                "role": "quote",
                "route": "attributed_quote_template",
                "templateMatchingEligible": True,
                "speaker": speaker,
                "timing": {
                    "sourceTimestampIsDuration": False,
                    "durationAvailable": bool(speaker.get("duration") or speaker.get("sourceEndTimestamp")),
                },
            })
            if not speaker.get("source"):
                gaps.append({
                    "gap": "quote_attribution_source_missing",
                    "beat": beat["beatId"],
                    "reason": "Quote-card routing requires a structured attribution source; none was supplied.",
                })
        elif role == "clip":
            covered.update(claim_ids)
            speaker_routes.append({
                "beatId": beat["beatId"],
                "role": "clip",
                "route": "source_footage_primary",
                "templateMatchingEligible": False,
                "speaker": speaker,
                "obligations": [
                    row for row in obligations if set(row["claimIds"]) & set(claim_ids)
                ],
                "timing": {
                    "sourceTimestampIsDuration": False,
                    "durationAvailable": bool(speaker.get("duration") or speaker.get("sourceEndTimestamp")),
                },
            })
            if not (speaker.get("duration") or speaker.get("sourceEndTimestamp")):
                gaps.append({
                    "gap": "source_clip_end_timing_missing",
                    "beat": beat["beatId"],
                    "reason": "A source start timestamp cannot determine the clip duration or end point.",
                })

    # StoryPackage job proposals are optional advice. Derive review-sized
    # semantic moments within each remaining narrator beat instead of either
    # suppressing its claims or collapsing the whole beat into one choice.
    for beat in sorted(beats.values(), key=lambda row: row.get("order", 0)):
        speaker = beat.get("speaker") or {"role": "narrator"}
        if speaker.get("role", "narrator") != "narrator":
            continue
        claim_ids = [claim_id for claim_id in beat.get("claimIds") or [] if claim_id not in covered]
        if not claim_ids:
            continue
        advisory = advisory_by_beat.get(beat["beatId"], [])
        advisory_jobs = _unique([row.get("job") for row in advisory])
        for index, unit in enumerate(_semantic_units(beat=beat, claim_ids=claim_ids, claims=claims), 1):
            claim_rows = [claims[claim_id] for claim_id in unit["claimIds"]]
            operations = _presentation_operations(text=unit["text"], claim_rows=claim_rows)
            derived_job = _derived_job(
                text=unit["text"], claim_rows=claim_rows, operations=operations)
            unit_advisory = [row for row in advisory if set(row.get("claimIds") or []) & set(unit["claimIds"])]
            unit_advisory_jobs = _unique([row.get("job") for row in unit_advisory])
            if len(unit_advisory_jobs) == 1:
                derived_job = unit_advisory_jobs[0]
            proposal_id = f"matching-derived-{beat['beatId']}-{index:02d}"
            tasks.append(task_from_claims(
                task_id=f"{adapter['story']['storyId']}.proposal.{proposal_id}",
                proposal_id=proposal_id,
                job=derived_job,
                provenance={
                    "source": "matching_semantic_splitter",
                    "reviewState": "proposed",
                    "evidence": "Source-exact semantic units; merges require compatible typed measures/cohorts and non-conflicting representations. Editorial alternatives remain unreviewed.",
                },
                claim_ids=unit["claimIds"],
                proposal_span=unit.get("span"),
                task_text=unit["text"],
                semantic_derived=True,
                advisory_proposal_ids=[row["proposalId"] for row in unit_advisory],
            ))
        covered.update(claim_ids)

    uncovered_claims = set(claims) - covered
    for claim_id in sorted(uncovered_claims):
        gaps.append({
            "gap": "semantic_route_unresolved",
            "claim": claim_id,
            "reason": "The matching semantic splitter could not assign this claim to a narrator, quote, or source-footage route.",
        })
    source_path = Path(source_path).resolve()
    return {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": 1,
        "story": adapter["story"],
        "packageId": adapter["packageId"],
        "source": {"path": str(source_path), "sha256": _sha(source_path)},
        "adapterValidation": adapter_validation,
        "taskProposals": tasks,
        "speakerRoutes": speaker_routes,
        "gaps": gaps,
        "activationState": "review_only_not_connected",
        "selectionAuthorized": False,
        "renderingAuthorized": False,
        "granularityPolicy": {
            "owner": "matching_layer",
            "claimBoundaryIsEvidenceNotTaskBoundary": True,
            "splitOnCommunicationPayloadChange": True,
            "punctuationAloneCanSplit": False,
            "exactCompleteSourceCoverageRequired": True,
        },
        "counts": {
            "claims": len(claims),
            "jobProposals": len(adapter.get("jobProposals") or []),
            "taskProposals": len(tasks),
            "speakerDerivedTaskProposals": sum(bool(row["speakerDerived"]) for row in tasks),
            "semanticDerivedTaskProposals": sum(bool(row["semanticDerived"]) for row in tasks),
            "sourceClipRoutes": sum(row["role"] == "clip" for row in speaker_routes),
            "quoteRoutes": sum(row["role"] == "quote" for row in speaker_routes),
            "uncoveredClaims": len(uncovered_claims),
            "typedGaps": len(gaps),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("adapter", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    artifact = build(json.loads(args.adapter.read_text()), source_path=args.adapter)
    args.output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps(artifact["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
