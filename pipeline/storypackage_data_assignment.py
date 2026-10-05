#!/usr/bin/env python3
"""Resolve StoryPackage data assignments from existing, hash-bound data snapshots."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any

try:
    from .matching_contract_gate import enforce_contracts
except ImportError:
    from matching_contract_gate import enforce_contracts

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
# The public Matching-agent path binds data handoffs in its task contract. This
# legacy assignment command retains a home-relative compatibility fallback for
# its historical fixture suite; callers can and should pin ASTRA_DATA_ROOT.
DATA_ROOT = Path(os.environ.get(
    "ASTRA_DATA_ROOT", Path.home() / "yt001data" / "hiphop_content_system" / "data"))
DEFAULT_QUEUE = ROOT / "reports" / "storypackage-02-data-handoff-queue.json"
DEFAULT_PACKAGE = WORKSPACE / "patterns-storypackage-review" / "architecture" / "storypackage" / "year-seventeen.storypackage-0.2.json"
DEFAULT_OUTPUT = ROOT / "reports" / "storypackage-02-data-assignments.json"
SOURCE_PATHS = {
    "queue": DEFAULT_QUEUE,
    "storyPackage": DEFAULT_PACKAGE,
    "spotifyStreams": DATA_ROOT / "spotify_streams.csv",
    "spotifySongs": DATA_ROOT / "spotify_songs.csv",
    "cohortMetrics": DATA_ROOT / "cohort_metrics.csv",
    "cohortMembership": DATA_ROOT / "rapper_cohort_2009_2020.csv",
    "discography": DATA_ROOT / "discography.csv",
    "counterfactualRankings": DATA_ROOT / "historical" / "derived" / "counterfactual_rankings.csv",
    "catalogConcentration": DATA_ROOT / "historical" / "derived" / "catalog_concentration.csv",
    "historicalCoverage": DATA_ROOT / "historical" / "coverage.csv",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path) -> Any:
    return json.loads(path.read_text())


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _number(value: str) -> int | float:
    parsed = float(value)
    return int(parsed) if parsed.is_integer() else parsed


def _field_digest(field: dict[str, Any]) -> str:
    body = {key: value for key, value in field.items() if key != "fieldSha256"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode()).hexdigest()


def _validate_field(field: dict[str, Any], sources: dict[str, Any], *, verify_sources: bool) -> bool:
    receipt = field.get("receipt") or {}
    source = sources.get(receipt.get("source")) or {}
    if not source or receipt.get("sourcePath") != source.get("path") or receipt.get("sourceSha256") != source.get("sha256"):
        raise ValueError("source receipt is stale: field digest/path mismatch")
    if field.get("fieldSha256") is not None and field["fieldSha256"] != _field_digest(field):
        raise ValueError("field value/receipt mutation")
    transform = receipt.get("transform")
    if transform and "never coerce absence to zero" in transform:
        value = field.get("value")
        if not isinstance(value, dict) or value.get("availability") != "unavailable" or value.get("value") is not None:
            raise ValueError("typed absence value cannot become zero")
        return False
    if not verify_sources:
        return False
    path = Path(source["path"])
    if not path.is_file() or _sha(path) != source["sha256"]:
        raise ValueError("source receipt is stale")
    # Only established source operations may prove a fact. Unsupported legacy
    # transforms remain readable but unverified; a body hash alone proves no value.
    if transform not in {"exact CSV numeric value", "count matching rows"}:
        return False
    selector = receipt.get("selector")
    columns = receipt.get("columns") or []
    if not isinstance(selector, dict) or not selector or not columns:
        raise ValueError("field receipt lacks selector/columns")
    rows = _csv(path)
    if not rows or any(column not in rows[0] for column in [*selector, *columns]):
        raise ValueError("field source columns/selector mismatch")
    selected = [row for row in rows if all(row[key] == str(value) for key, value in selector.items())]
    if transform == "exact CSV numeric value":
        if len(selected) != 1 or len(columns) != 1 or selected[0][columns[0]] == "":
            raise ValueError("field source selector does not identify a measured value")
        expected = _number(selected[0][columns[0]])
    else:
        expected = len(selected)
    if isinstance(field.get("value"), bool) or field.get("value") != expected:
        raise ValueError("field value does not replay from source receipt")
    return True


class AssignmentContext:
    def __init__(self, source_paths: dict[str, Path]):
        missing = [str(path) for path in source_paths.values() if not path.is_file()]
        if missing:
            raise ValueError(f"declared data source is missing: {missing}")
        self.paths = source_paths
        self.hashes = {name: _sha(path) for name, path in source_paths.items()}
        self.stream_rows = _csv(source_paths["spotifyStreams"])
        self.streams = {row["artist"]: row for row in self.stream_rows}
        self.chart = [row for row in self.stream_rows if row["status"] == "ok"]
        self.song_rows = _csv(source_paths["spotifySongs"])
        self.songs: dict[str, list[int]] = {}
        for row in self.song_rows:
            self.songs.setdefault(row["artist"], []).append(int(row["streams"]))
        for values in self.songs.values():
            values.sort(reverse=True)
        self.metrics = {row["artist"]: row for row in _csv(source_paths["cohortMetrics"])}
        self.membership = _csv(source_paths["cohortMembership"])
        self.discography = _csv(source_paths["discography"])
        self.counterfactual = {row["artist"]: row for row in _csv(source_paths["counterfactualRankings"])}
        self.concentration = {row["artist"]: row for row in _csv(source_paths["catalogConcentration"])}
        self.historical_coverage = _csv(source_paths["historicalCoverage"])

    def receipt(self, source: str, *, selector: Any, columns: list[str], transform: str) -> dict[str, Any]:
        return {
            "source": source,
            "sourcePath": str(self.paths[source]),
            "sourceSha256": self.hashes[source],
            "selector": selector,
            "columns": columns,
            "transform": transform,
        }

    def field(self, field_id: str, value: Any, unit: str, source: str, *,
              selector: Any, columns: list[str], transform: str,
              encodings: list[str], subject: str | None = None,
              population: str | None = None, basis: str | None = None) -> dict[str, Any]:
        row = {
            "fieldId": field_id,
            "value": value,
            "unit": unit,
            "encodings": encodings,
            "receipt": self.receipt(source, selector=selector, columns=columns, transform=transform),
        }
        if subject is not None:
            row["subject"] = subject
        if population is not None:
            row["population"] = population
        if basis is not None:
            row["basis"] = basis
        row["fieldSha256"] = _field_digest(row)
        return row

    def stream(self, artist: str, column: str) -> int | float:
        row = self.streams.get(artist)
        if not row or row.get("status") != "ok" or not row.get(column):
            raise KeyError(artist)
        return _number(row[column])

    def top(self, artist: str, count: int = 1) -> int:
        values = self.songs.get(artist) or []
        if len(values) < count:
            raise KeyError(artist)
        return sum(values[:count])

    def weighted(self, artist: str) -> float:
        return float(self.stream(artist, "streams_lead")) + 0.5 * float(self.stream(artist, "streams_feature"))


def _gap(kind: str, message: str, *, encodings: list[str], subject: str | None = None,
         claim_ids: list[str] | None = None, details: dict[str, Any] | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"kind": kind, "message": message, "encodings": encodings}
    if subject:
        row["subject"] = subject
    if claim_ids:
        row["claimIds"] = claim_ids
    if details:
        row["details"] = details
    return row


def _stream_field(ctx: AssignmentContext, artist: str, column: str, field_id: str,
                  unit: str, encodings: list[str]) -> dict[str, Any]:
    return ctx.field(field_id, ctx.stream(artist, column), unit, "spotifyStreams",
                     selector={"artist": artist, "status": "ok"}, columns=[column],
                     transform="exact CSV numeric value", encodings=encodings, subject=artist,
                     population="chart-93")


def _top_share(ctx: AssignmentContext, artist: str, count: int, field_id: str,
               encodings: list[str]) -> dict[str, Any]:
    total = ctx.stream(artist, "streams_total")
    return ctx.field(field_id, ctx.top(artist, count) / total, "ratio", "spotifySongs",
                     selector={"artist": artist, "topN": count}, columns=["artist", "streams"],
                     transform=f"sum top {count} streams / spotify_streams.streams_total",
                     encodings=encodings, subject=artist, population="artist catalog",
                     basis=f"numerator={ctx.top(artist, count)}; denominator={total}")


def _cohort_members(year: int) -> list[str]:
    if year == 2009:
        return ["Wale", "B.o.B", "Curren$y", "Kid Cudi"]
    if year == 2010:
        return ["J. Cole", "Nipsey Hussle", "Wiz Khalifa", "Big Sean", "Freddie Gibbs", "Jay Rock", "Nicki Minaj"]
    raise ValueError("unsupported story cohort year")


def _chart_streak(ctx: AssignmentContext, artist: str) -> tuple[list[int], int]:
    years = sorted({int(row["year"]) for row in ctx.discography
                    if row["artist"] == artist and row["year"].isdigit()
                    and any(row.get(column) for column in ("us_peak", "us_rnb_peak", "us_rap_peak"))})
    best: list[int] = []
    for year in years:
        run = [year]
        while run[-1] + 1 in years:
            run.append(run[-1] + 1)
        if len(run) > len(best):
            best = run
    return best, len(best)


def _assignment_values(ctx: AssignmentContext, task_id: str, claim_ids: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    fields: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    chart_rank_daily = sorted(ctx.chart, key=lambda row: int(row["daily_total"]), reverse=True)
    chart_rank_total = sorted(ctx.chart, key=lambda row: int(row["streams_total"]), reverse=True)

    if task_id in {"01-01.subject", "02-02b.currensy_catalog"}:
        daily = ctx.stream("Drake", "daily_total")
        currensy = ctx.stream("Curren$y", "streams_total")
        fields.extend([
            _stream_field(ctx, "Drake", "daily_total", "drake.daily_streams", "streams/day", ["magnitude", "change_over_time"]),
            ctx.field("drake.streams_per_second", daily / 86400, "streams/second", "spotifyStreams",
                      selector={"artist": "Drake", "status": "ok"}, columns=["daily_total"],
                      transform="daily_total / 86400", encodings=["derivation", "magnitude"], subject="Drake"),
            _stream_field(ctx, "Curren$y", "streams_total", "currensy.catalog_streams", "streams", ["magnitude"]),
            ctx.field("currensy.catalog_equivalent_drake_days", currensy / daily, "days", "spotifyStreams",
                      selector={"artists": ["Curren$y", "Drake"], "status": "ok"},
                      columns=["streams_total", "daily_total"],
                      transform="Curren$y streams_total / Drake daily_total", encodings=["derivation", "magnitude"],
                      subject="Curren$y", basis=f"{currensy} / {daily}"),
        ])
    elif task_id == "03-03.opening_chart":
        values = [{"artist": row["artist"], "dailyStreams": int(row["daily_total"]), "rank": index + 1}
                  for index, row in enumerate(chart_rank_daily)]
        fields.append(ctx.field("chart93.daily_stream_rank", values, "ranked series", "spotifyStreams",
                                selector={"status": "ok"}, columns=["artist", "daily_total"],
                                transform="filter status=ok; sort daily_total descending; one-based rank",
                                encodings=["rank", "magnitude"], population="chart-93"))
    elif task_id == "04-04.main":
        future = ctx.stream("Future", "daily_total")
        travis = ctx.stream("Travis Scott", "daily_total")
        drake = ctx.stream("Drake", "daily_total")
        fields.extend([
            _stream_field(ctx, "Future", "daily_total", "future.daily_streams", "streams/day", ["magnitude"]),
            _stream_field(ctx, "Travis Scott", "daily_total", "travis_scott.daily_streams", "streams/day", ["magnitude"]),
            _stream_field(ctx, "Drake", "daily_total", "drake.daily_streams", "streams/day", ["magnitude"]),
            ctx.field("future_travis.combined_daily_streams", future + travis, "streams/day", "spotifyStreams",
                      selector={"artists": ["Future", "Travis Scott"], "status": "ok"}, columns=["daily_total"],
                      transform="sum daily_total", encodings=["aggregate", "magnitude"], population="two artists"),
            ctx.field("drake.edge_over_future_travis", drake - future - travis, "streams/day", "spotifyStreams",
                      selector={"artists": ["Drake", "Future", "Travis Scott"], "status": "ok"}, columns=["daily_total"],
                      transform="Drake - Future - Travis Scott daily_total", encodings=["difference"], subject="Drake"),
        ])
    elif task_id == "05-05a.main":
        rank = next(index + 1 for index, row in enumerate(chart_rank_daily) if row["artist"] == "Drake")
        fields.append(ctx.field("drake.daily_stream_rank", rank, "rank", "spotifyStreams",
                                selector={"status": "ok", "artist": "Drake"}, columns=["artist", "daily_total"],
                                transform="sort status=ok daily_total descending; one-based rank",
                                encodings=["rank"], subject="Drake", population="chart-93"))
    elif task_id == "08-08.main":
        total = ctx.stream("Drake", "streams_total")
        feature = ctx.stream("Drake", "streams_feature")
        fields.extend([
            _stream_field(ctx, "Drake", "tracks_total", "drake.catalog_track_count", "tracks", ["magnitude"]),
            ctx.field("drake.feature_stream_share", feature / total, "ratio", "spotifyStreams",
                      selector={"artist": "Drake", "status": "ok"}, columns=["streams_feature", "streams_total"],
                      transform="streams_feature / streams_total", encodings=["share_of_whole"], subject="Drake"),
            ctx.field("drake.elapsed_years_since_2009", 17, "elapsed years", "discography",
                      selector={"artist": "Drake", "chartYears": [2009, 2026]}, columns=["artist", "year", "us_peak", "us_rnb_peak", "us_rap_peak"],
                      transform="latest chart year - first year of uninterrupted 2009-2026 run",
                      encodings=["change_over_time"], subject="Drake"),
        ])
    elif task_id == "09-09.main":
        for artist, slug in (("Latto", "latto"), ("Jay Rock", "jay_rock"), ("Ab-Soul", "ab_soul")):
            fields.append(_top_share(ctx, artist, 1, f"{slug}.top_song_share", ["identity", "magnitude", "share_of_whole"]))
        biz = ctx.concentration["Biz Markie"]
        fields.append(ctx.field("biz_markie.top_song_share", float(biz["top1_share"]), "ratio", "catalogConcentration",
                                selector={"artist": "Biz Markie"}, columns=["artist", "streams_observed", "top1_share"],
                                transform="established historical_corpus catalog concentration output",
                                encodings=["identity", "magnitude", "share_of_whole"], subject="Biz Markie",
                                population="artist catalog", basis=f"{biz['tracks_observed']} observed tracks; {biz['streams_observed']} streams"))
    elif task_id == "11-11a.main":
        fields.extend([
            _top_share(ctx, "Drake", 1, "drake.top_song_share", ["share_of_whole", "magnitude", "difference"]),
            _top_share(ctx, "Drake", 10, "drake.top_10_share", ["share_of_whole", "magnitude", "difference"]),
        ])
    elif task_id == "11-11b.main":
        fields.append(_top_share(ctx, "Future", 10, "future.top_10_share", ["share_of_whole", "difference", "magnitude"]))
    elif task_id in {"12-12a.main", "12-12b.main"}:
        artists = ["Ab-Soul", "Latto", "Jay Rock"] if task_id == "12-12a.main" else ["Macklemore", "Drake"]
        for artist in artists:
            source_row = ctx.counterfactual[artist]
            old_rank = int(source_row["original_rank"])
            new_rank = int(source_row["adjusted_rank"])
            loss = int(source_row["removed_top_track_streams"])
            slug = artist.lower().replace(" ", "_").replace("-", "_").replace("$", "s")
            fields.append(ctx.field(f"{slug}.top_song_removed", {
                "originalRank": old_rank, "newRank": new_rank, "rankDrop": new_rank - old_rank,
                "removedStreams": loss, "retainedShare": float(source_row["retained_share"]),
            }, "rank-removal result", "counterfactualRankings", selector={"artist": artist},
                columns=["artist", "removed_top_track_streams", "retained_share", "original_rank", "adjusted_rank", "rank_change"],
                transform="established historical_corpus derive_counterfactual output; rankDrop=adjusted_rank-original_rank",
                encodings=["change_over_time", "difference", "magnitude"], subject=artist, population="114 artists in canonical historical metric set"))
    elif task_id in {"13-13a.main", "13-13b.main"}:
        billion_counts = {row["artist"]: sum(value >= 1_000_000_000 for value in ctx.songs.get(row["artist"], [])) for row in ctx.chart}
        if task_id == "13-13a.main":
            fields.extend([
                ctx.field("drake.billion_stream_song_count", billion_counts["Drake"], "songs", "spotifySongs",
                          selector={"artist": "Drake"}, columns=["artist", "streams"],
                          transform="count streams >= 1,000,000,000", encodings=["aggregate", "magnitude", "rank"], subject="Drake"),
                ctx.field("chart93.zero_billion_song_artists", sum(value == 0 for value in billion_counts.values()), "artists", "spotifySongs",
                          selector={"artists": "chart-93"}, columns=["artist", "streams"],
                          transform="per artist count streams >= 1bn; count equals zero", encodings=["aggregate", "magnitude"], population="chart-93"),
            ])
        else:
            fields.append(ctx.field("chart93.catalogs_under_30b", sum(int(row["streams_total"]) < 30_000_000_000 for row in ctx.chart), "artists", "spotifyStreams",
                                    selector={"status": "ok"}, columns=["artist", "streams_total"],
                                    transform="count streams_total < 30,000,000,000", encodings=["share_of_whole", "magnitude"], population="chart-93"))
    elif task_id == "14-14.main":
        next_five = [row["artist"] for row in chart_rank_total[1:6]]
        drake_top10 = ctx.top("Drake", 10)
        comparison = sum(ctx.top(artist, 1) for artist in next_five)
        fields.extend([
            ctx.field("drake.top_10_streams", drake_top10, "streams", "spotifySongs", selector={"artist": "Drake", "topN": 10},
                      columns=["artist", "streams"], transform="sum top 10", encodings=["identity", "magnitude"], subject="Drake"),
            ctx.field("next_five.top_song_sum", comparison, "streams", "spotifySongs", selector={"artists": next_five, "topNPerArtist": 1},
                      columns=["artist", "streams"], transform="sum each artist's largest song", encodings=["identity", "magnitude"], population="next five artists by catalog streams"),
        ])
    elif task_id == "16-16.main":
        for year in (2009, 2010):
            members = _cohort_members(year)
            fields.append(ctx.field(f"xxl_{year}.story_members", members, "entity list", "cohortMembership",
                                    selector={"Cohort_Year": str(year), "Source": ["XXL Freshman (selected)", "Declined XXL invite"], "storyClaimSubset": members},
                                    columns=["Cohort_Year", "Artist", "Source"],
                                    transform="retain exact members named by approved claims",
                                    encodings=["membership"], population=f"XXL {year} story subset"))
    elif task_id in {"18-18.main", "19-19.main"}:
        members = _cohort_members(2010)
        values = [{"artist": artist, "weightedStreams": ctx.weighted(artist)} for artist in members]
        total = sum(row["weightedStreams"] for row in values)
        fields.extend([
            ctx.field("xxl_2010.weighting_rule", {"leadOrCoLead": 1.0, "featureOrRemix": 0.5}, "weights", "storyPackage",
                      selector={"claimIds": ["c3-provoke-3.1", "c3-provoke-3.2", "c3-provoke-3.3"]}, columns=["claims.text"],
                      transform="approved story rule represented as typed coefficients; not numeric evidence",
                      encodings=["aggregate", "membership"], population="XXL 2010 story subset"),
            ctx.field("xxl_2010.weighted_members", values, "streams", "spotifyStreams", selector={"artists": members, "status": "ok"},
                      columns=["streams_lead", "streams_feature"], transform="streams_lead + 0.5 * streams_feature per artist",
                      encodings=["aggregate", "membership", "magnitude"], population="seven named peers"),
            ctx.field("xxl_2010.weighted_total", total, "streams", "spotifyStreams", selector={"artists": members, "status": "ok"},
                      columns=["streams_lead", "streams_feature"], transform="sum(streams_lead + 0.5 * streams_feature)",
                      encodings=["aggregate", "magnitude"], population="seven named peers"),
            _stream_field(ctx, "Drake", "streams_lead", "drake.lead_streams", "streams", ["magnitude"]),
        ])
    elif task_id == "20-20.main":
        for artist in ("Travis Scott", "Kendrick Lamar", "Post Malone", "Future"):
            slug = artist.lower().replace(" ", "_")
            fields.append(_stream_field(ctx, artist, "streams_total", f"{slug}.catalog_streams", "streams", ["identity", "magnitude"]))
    elif task_id == "21-21a.main":
        drake_lead = ctx.stream("Drake", "streams_lead")
        peer_max = max(int(row["streams_total"]) for row in ctx.chart if row["artist"] != "Drake")
        fields.append(ctx.field("drake.lead_catalog_edge_over_largest_peer", drake_lead - peer_max, "streams", "spotifyStreams",
                                selector={"subject": "Drake", "comparison": "largest non-Drake status=ok catalog"},
                                columns=["streams_lead", "streams_total"], transform="Drake streams_lead - max(non-Drake streams_total)",
                                encodings=["rank", "difference", "magnitude"], subject="Drake", population="chart-93"))
        for artist in ("Drake", "Future", "Young Thug"):
            value = int(float(ctx.metrics[artist]["feature_credits"]))
            slug = artist.lower().replace(" ", "_")
            fields.append(ctx.field(f"{slug}.feature_credits", value, "credits", "cohortMetrics",
                                    selector={"artist": artist}, columns=["feature_credits"], transform="exact CSV numeric value",
                                    encodings=["rank", "magnitude"], subject=artist))
    elif task_id == "21-21b.main":
        feature = ctx.stream("Drake", "streams_feature")
        credits = int(float(ctx.metrics["Drake"]["feature_credits"]))
        fields.extend([
            _stream_field(ctx, "Drake", "streams_feature", "drake.feature_streams", "streams", ["derivation", "magnitude"]),
            ctx.field("drake.feature_streams_per_credit", feature / credits, "streams/credit", "cohortMetrics",
                      selector={"artist": "Drake"}, columns=["feature_credits", "spotify_feature"],
                      transform="spotify_feature / feature_credits", encodings=["derivation", "magnitude"], subject="Drake"),
        ])
    elif task_id == "22-22.main":
        members = _cohort_members(2009) + _cohort_members(2010)
        total = sum(ctx.weighted(artist) for artist in members)
        drake = ctx.weighted("Drake")
        fields.extend([
            ctx.field("xxl_2009_2010.weighted_total", total, "streams", "spotifyStreams", selector={"artists": members, "status": "ok"},
                      columns=["streams_lead", "streams_feature"], transform="sum(streams_lead + 0.5 * streams_feature)",
                      encodings=["aggregate", "difference"], population="eleven named peers"),
            ctx.field("xxl_2009_2010.edge_over_drake", total / drake - 1, "ratio", "spotifyStreams", selector={"peerArtists": members, "subject": "Drake"},
                      columns=["streams_lead", "streams_feature"], transform="peer weighted total / Drake weighted total - 1",
                      encodings=["difference", "aggregate"], subject="Drake", population="eleven named peers"),
        ])
    elif task_id == "24-24.main":
        streak, _ = _chart_streak(ctx, "Drake")
        fields.append(ctx.field("drake.elapsed_years_since_streak_start", max(streak) - min(streak), "elapsed years", "discography",
                                selector={"artist": "Drake", "charted": True}, columns=["year", "us_peak", "us_rnb_peak", "us_rap_peak"],
                                transform="last year - first year of maximum uninterrupted chart-year run",
                                encodings=["change_over_time"], subject="Drake", basis=f"{min(streak)}-{max(streak)}"))
    elif task_id in {"25-25a.main", "25-25b.main"}:
        values = []
        for artist in ("Drake", "J. Cole"):
            years, count = _chart_streak(ctx, artist)
            values.append({"artist": artist, "years": years, "consecutiveYears": count})
        fields.append(ctx.field("chart_streak.leaders", values, "entity streak list", "discography",
                                selector={"artists": ["Drake", "J. Cole"], "charted": True}, columns=["artist", "year", "us_peak", "us_rnb_peak", "us_rap_peak"],
                                transform="maximum uninterrupted sequence of years containing any US chart peak",
                                encodings=["change_over_time", "membership"], population="named comparison"))
    elif task_id == "26-26.main":
        sections = {"single": "lead_singles", "studio_album": "albums", "feature_single": "guest_features", "mixtape": "mixtapes"}
        for section, slug in sections.items():
            count = sum(row["artist"] == "Drake" and row["section"] == section and row["us_peak"] == "1" for row in ctx.discography)
            fields.append(ctx.field(f"drake.number_one_{slug}", count, "number-one releases", "discography",
                                    selector={"artist": "Drake", "section": section, "us_peak": "1"}, columns=["artist", "section", "us_peak"],
                                    transform="count matching rows", encodings=["magnitude"], subject="Drake"))
    elif task_id == "27-27.main":
        for artist in ("Post Malone", "XXXTentacion", "Kendrick Lamar", "Ty Dolla $ign", "Young Thug", "21 Savage"):
            slug = artist.lower().replace(" ", "_").replace("$", "s")
            fields.extend([
                _stream_field(ctx, artist, "streams_lead", f"{slug}.lead_streams", "streams", ["difference", "membership"]),
                _stream_field(ctx, artist, "streams_feature", f"{slug}.feature_streams", "streams", ["difference", "membership"]),
            ])
    elif task_id == "29-29a.main":
        for artist in ("Lil Baby", "Drake"):
            value = int(float(ctx.metrics[artist]["units_primary_per_year"]))
            slug = artist.lower().replace(" ", "_")
            fields.append(ctx.field(f"{slug}.primary_units_per_year", value, "certified units/year", "cohortMetrics",
                                    selector={"artist": artist}, columns=["units_primary_per_year"], transform="exact CSV numeric value",
                                    encodings=["difference"], subject=artist))
    elif task_id == "30-30a.main":
        coverage = next(row for row in ctx.historical_coverage
                        if row["capability"] == "Historical snapshots"
                        and row["selected_use"] == "Detect unusually slow decay")
        fields.append(ctx.field("jay_z.year_17_daily_meter", {
            "availability": "unavailable",
            "value": None,
            "coverageStatus": coverage["status"],
            "reason": coverage["note"],
        }, "typed absence", "historicalCoverage",
            selector={"capability": coverage["capability"], "selected_use": coverage["selected_use"]},
            columns=["capability", "selected_use", "status", "evidence_rows", "note"],
            transform="represent documented missing historical time series as unavailable; never coerce absence to zero",
            encodings=["absence"], subject="Jay-Z", basis="Current Spotify totals are one as-of observation, not reconstructed history."))
    else:
        gaps.append(_gap("recipe_missing", "No deterministic assignment recipe exists for this queued task.",
                         encodings=[], claim_ids=claim_ids))
    return fields, gaps


def build(*, queue: dict[str, Any] | None = None, package: dict[str, Any] | None = None,
          source_paths: dict[str, Path] | None = None) -> dict[str, Any]:
    contract_receipt = enforce_contracts("storypackage_data_assignment.build")
    paths = dict(SOURCE_PATHS if source_paths is None else source_paths)
    ctx = AssignmentContext(paths)
    queue_data = queue if queue is not None else _json(paths["queue"])
    package_data = package if package is not None else _json(paths["storyPackage"])
    if queue_data.get("packageId") != package_data.get("packageId"):
        raise ValueError("data queue and StoryPackage identity differ")
    results = []
    for assignment in queue_data.get("assignments") or []:
        fields, gaps = _assignment_values(ctx, assignment["taskId"], assignment["claimIds"])
        status = "resolved" if not gaps else ("partial" if fields else "blocked")
        results.append({
            "taskId": assignment["taskId"],
            "reviewKey": assignment["reviewKey"],
            "claimIds": assignment["claimIds"],
            "jobProposalIds": assignment["jobProposalIds"],
            "requiredEncodings": assignment["requiredEncodings"],
            "typedFields": fields,
            "gaps": gaps,
            "status": status,
        })
    counts = {
        "assignments": len(results),
        "resolved": sum(row["status"] == "resolved" for row in results),
        "partial": sum(row["status"] == "partial" for row in results),
        "blocked": sum(row["status"] == "blocked" for row in results),
        "typedFields": sum(len(row["typedFields"]) for row in results),
        "typedGaps": sum(len(row["gaps"]) for row in results),
    }
    complete = counts["partial"] == 0 and counts["blocked"] == 0 and counts["assignments"] == len(queue_data.get("assignments") or [])
    return {
        "contractEnforcementReceipt": contract_receipt,
        "schemaVersion": 1,
        "packageId": queue_data["packageId"],
        "purpose": "Deterministic typed data assignments for StoryPackage-linked VisualTasks",
        "sources": {name: {"path": str(path), "sha256": ctx.hashes[name]} for name, path in paths.items()},
        "assignments": results,
        "counts": counts,
        "dataHandoffComplete": complete,
        "selectionAuthorized": False,
        "renderingAuthorized": False,
    }


def validate(artifact: dict[str, Any], *, verify_sources: bool = True) -> dict[str, Any]:
    rows = artifact.get("assignments") or []
    if len({row.get("taskId") for row in rows}) != len(rows):
        raise ValueError("assignment results are duplicated")
    if any(row.get("status") not in {"resolved", "partial", "blocked"} for row in rows):
        raise ValueError("assignment has unsupported status")
    if any(not row.get("typedFields") and not row.get("gaps") for row in rows):
        raise ValueError("assignment has neither typed fields nor typed gaps")
    if any(not field.get("receipt", {}).get("sourceSha256") for row in rows for field in row.get("typedFields") or []):
        raise ValueError("resolved field lacks source receipt")
    verified_fields = {}
    unresolved_fields = []
    for row in rows:
        for field in row.get("typedFields") or []:
            if _validate_field(field, artifact.get("sources") or {}, verify_sources=verify_sources):
                verified_fields.setdefault(row["taskId"], []).append(field["fieldId"])
            else:
                unresolved_fields.append({"taskId": row["taskId"], "fieldId": field["fieldId"],
                                          "status": "unresolved", "owner": "data"})
        covered = {encoding for field in row.get("typedFields") or [] for encoding in field.get("encodings") or []}
        covered.update(encoding for gap in row.get("gaps") or [] for encoding in gap.get("encodings") or [])
        if not set(row.get("requiredEncodings") or []).issubset(covered):
            raise ValueError("required encoding lacks a typed field or gap")
    unresolved = any(row["status"] != "resolved" for row in rows)
    if artifact.get("dataHandoffComplete") == unresolved:
        raise ValueError("data handoff completion state is inconsistent")
    if artifact.get("selectionAuthorized") is not False or artifact.get("renderingAuthorized") is not False:
        raise ValueError("data assignments cannot authorize selection or rendering")
    if verify_sources:
        for source in artifact.get("sources", {}).values():
            path = Path(source["path"])
            if not path.is_file() or _sha(path) != source["sha256"]:
                raise ValueError("source receipt is stale")
    return {"dataHandoffComplete": artifact["dataHandoffComplete"], **artifact["counts"],
            "verifiedFields": verified_fields, "unresolvedFields": unresolved_fields,
            "coverageVerified": bool(rows) and not unresolved_fields and not unresolved}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "validate"))
    args = parser.parse_args()
    if args.command == "build":
        artifact = build()
        DEFAULT_OUTPUT.write_text(json.dumps(artifact, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
        print(json.dumps(validate(artifact, verify_sources=False), sort_keys=True))
    else:
        print(json.dumps(validate(_json(DEFAULT_OUTPUT)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
