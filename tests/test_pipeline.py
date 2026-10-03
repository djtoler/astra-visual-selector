#!/usr/bin/env python3
"""Tests for the deterministic layer.

Every test here exists because a real defect got through. The comment on each names
the defect, so the suite reads as a record of what has actually gone wrong.

    python3 tests/test_pipeline.py          run everything
    python3 -m unittest tests.test_pipeline -v
"""
import collections, json, os, pathlib, re, shutil, subprocess, sys, tempfile, unittest, warnings
warnings.simplefilter('ignore', ResourceWarning)

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "match-trial"))
sys.path.insert(0, str(ROOT / "pipeline"))
import candidates as C

BINDINGS = json.load(open(ROOT / "grammar" / "bindings.json"))


def pool_or_skip(case):
    """The template pool lives in Codex's tree, which can be unreadable. A test that
    cannot run must SKIP with a reason, never error — "cannot run" and "is broken"
    must not look the same in a test report."""
    try:
        return C.load()
    except (PermissionError, FileNotFoundError) as e:
        case.skipTest(f"template pool unreadable ({type(e).__name__}) — "
                      f"needs read access to the scene library")


def reachable(shot):
    """Every record a reviewer can select on this beat.

    The expander (LOG 0054) puts the rest of a family behind a control on the scene
    that represents it, so a sibling is selectable without occupying a slate slot.
    Seven of the user's pass-2 picks were siblings, and every test that checked
    "is this selection still in the slate" read `options` alone and called them lost.
    """
    ids = {o["id"] for o in shot["options"]}
    return ids | {i["id"] for o in shot["options"] for i in (o.get("siblings") or [])}


def expected_spatial():
    """Spatial scenes = the approved list's own count PLUS any registered locally.

    Was a literal 5, then a literal 9, then the list's count alone — and each
    broke the next time one was added. two-floors is local, so the list does not
    know about it. A count that can change belongs to its sources, all of them.
    """
    n = json.load(open(C.approved_path())).get("counts", {}).get(
        "cinematic3dTemplates", 0)
    f = ROOT / "grammar" / "local-templates.json"
    if f.exists():
        n += sum(1 for r in json.load(open(f))["records"]
                 if r.get("kind") in C.SPATIAL_KINDS)
    return n


def rec(rid, axes=None, mech=""):
    return {"id": rid, "axes": axes or {}, "mechanism": mech,
            "provenance": {"verdict": "clear"}}


class Tolerance(unittest.TestCase):
    """Slot counts never disqualify; tolerance is +/-33%."""

    def test_six_admits_four_through_eight(self):
        self.assertEqual(C.bounds(6), (4, 8))

    def test_small_counts_keep_a_minimum_delta_of_one(self):
        self.assertEqual(C.bounds(1), (0, 2))
        self.assertEqual(C.bounds(2), (1, 3))

    def test_missing_capacity_is_unknown_never_dropped(self):
        # "unknowns never disqualify" — a standing rule, easy to regress
        out = C.shape([rec("a")], 6)
        self.assertEqual(out[0][1], "unknown")

    def test_exact_and_within_are_distinguished(self):
        self.assertEqual(C.shape([rec("a", {"subjects": 6})], 6)[0][1], "exact")
        self.assertEqual(C.shape([rec("a", {"subjects": 7})], 6)[0][1], "within")
        self.assertEqual(C.shape([rec("a", {"subjects": 99})], 6)[0][1], "outside")

    def test_every_subject_axis_is_considered_not_the_first(self):
        # defect: only the first capacity key was read, so a record whose second
        # axis matched was scored "outside". Both axes here are subject counts;
        # a secondary axis matching is a different case, see SubjectAxes.
        self.assertEqual(C.shape([rec("a", {"entities": 99, "heroes": 6})], 6)[0][1],
                         "exact")


class SubjectAxes(unittest.TestCase):
    """Only a count of SUBJECTS answers "can this hold the N things the beat names"."""

    GRID = {"id": "grid", "axes": {"entities": 15, "display_columns": 5,
                                   "metrics": 1, "csv_rows": 15}}

    def test_a_fifteen_entity_grid_is_not_feasible_for_a_one_entity_beat(self):
        # defect (2026-09-20): it passed on metrics:1. 22% of all feasible matches
        # qualified on an axis that was not a subject count. LOG 0013.
        self.assertEqual(C.shape([self.GRID], 1)[0][1], "outside")

    def test_it_is_feasible_for_a_beat_that_wants_fifteen(self):
        self.assertEqual(C.shape([self.GRID], 15)[0][1], "exact")

    def test_plumbing_only_capacity_reads_as_unknown_not_outside(self):
        # declaring metrics and csv_rows says nothing about how many things it holds
        r = {"id": "x", "axes": {"metrics": 9, "csv_rows": 11}}
        self.assertEqual(C.shape([r], 3)[0][1], "unknown")

    def test_capacity_band_ignores_plumbing(self):
        # csv_rows 11 made a two-subject scene read as "several"
        r = {"id": "y", "axes": {"subjects": 2, "metrics": 9, "csv_rows": 11}}
        self.assertEqual(C.capacity_band(r), "few")

    def test_an_unclassified_axis_raises_rather_than_defaulting(self):
        with self.assertRaises(ValueError):
            C.subject_axes({"id": "z", "axes": {"wingspan_in_cubits": 3}})

    def test_the_whole_pool_is_classified(self):
        self.assertEqual(C.unclassified_axes(pool_or_skip(self)), [])

    def test_no_feasible_match_in_the_corpus_rests_on_a_secondary_axis(self):
        beats = [x for v in json.load(open(ROOT / "pipeline" / "beats-all.json")).values()
                 for x in v]
        pool = {r["id"]: r for r in pool_or_skip(self)}
        for b in beats:
            n = b.get("entity_count")
            if not isinstance(n, int) or n < 1: continue
            rows = [pool[r["id"]] for r in BINDINGS.get(b["job"], []) if r["id"] in pool]
            for rec, verdict, hits in C.shape(rows, n):
                if verdict in ("exact", "within"):
                    for k, _ in hits:
                        self.assertIn(C._axis_base(k), C.SUBJECT_AXES,
                                      f"beat {b['id']} matched {rec['id']} on {k}")


class MatchCut(unittest.TestCase):
    """A match cut is derived from measured capability, never from a family name."""

    @classmethod
    def setUpClass(cls):
        try:    cls.pool = {r["id"]: r for r in C.load()}
        except (PermissionError, FileNotFoundError): cls.pool = None
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        cls.shots = ({f"{x['passage']}-{x['beat']}": x for x in json.load(open(f))}
                     if f.exists() else {})
        p = ROOT / "grammar" / "picks.json"
        cls.picks = json.load(open(p))["beats"] if p.exists() else {}

    def setUp(self):
        if self.pool is None:
            self.skipTest("template pool unreadable — needs the scene library")

    def test_a_record_with_no_capability_is_never_claimed(self):
        # the signature is measured; an unmeasured template must not be guessed into it
        self.assertFalse(C.is_match_cut({"id": "22_single_measurement"}, self.pool))
        self.assertFalse(C.is_match_cut({"id": "nope"}, self.pool))

    def test_the_signature_is_all_three_conditions(self):
        base = {"carries": ["identity"], "media_slots": 10,
                "staging": "reveals_in_turn", "structure": "sequence"}
        self.assertTrue(C.is_match_cut({"id": "x", "capability": base}))
        for drop in ({"carries": ["identity", "magnitude"]}, {"media_slots": 2},
                     {"staging": "builds_up"}, {"structure": "single"}):
            self.assertFalse(C.is_match_cut({"id": "x", "capability": {**base, **drop}}),
                             f"still matched with {drop}")

    def test_it_finds_the_families_the_user_named(self):
        # beat 30a: "this should've selected one of the carousels or a roll match cut"
        named = {"archive3-carousel-galleries-loop-animation-2",
                 "archive3-looped-slideshow-background",
                 "archive3-carousel-photo-logo-reveal-2026-09-13-12-24-28-utc"}
        found = {C._family(r) for r in C.match_cut_pool(self.pool)}
        self.assertTrue(named <= found, f"missing {named - found}")

    def mc_in(self, key):
        b = self.shots.get(key) or {}
        return [o["id"] for o in b.get("options", []) if C.is_match_cut(self.pool[o["id"]])]

    def test_an_admission_is_never_made_on_a_beat_the_user_did_not_flag(self):
        # the rawBroll admission path must stay opt-in even though most vessels now
        # arrive as ordinary bindings
        if not self.shots: self.skipTest("shotlist.capacity.json not built")
        # Resolve the flag the way shotlist resolves it: picks.json OR a hand-set
        # entry in beat-flags.json. This test read picks.json alone and fired on 02b,
        # correctly — the flag source and the consumer had diverged. The guard is
        # "opt-in only", and 02b IS opted in, through the other file.
        flagged = {k for k, b in self.picks.items() if b.get("rawBroll")}
        fl = ROOT / "grammar" / "beat-flags.json"
        if fl.exists():
            flagged |= {k for k, v in (json.load(open(fl)).get("beats") or {}).items()
                        if v.get("rawBroll")}
        self.assertTrue(flagged, "no beat flagged raw b-roll — has picks.json gone stale?")
        for k, s in self.shots.items():
            if k in flagged: continue
            self.assertEqual([o for o in s["options"] if o.get("verdict") == "match-cut"],
                             [], f"{k} was not flagged but got an admission")

    def test_a_match_cut_survives_the_capacity_filter(self):
        # beat 30a asserts ONE thing (Jay-Z absent) and wants a crowd on screen.
        # A vessel's slots hold sourced footage, not the beat's entities, so
        # entity_count must not govern it.
        if not self.shots: self.skipTest("shotlist.capacity.json not built")
        self.assertTrue(self.mc_in("30-30a"), "capacity filter removed every vessel")

    def test_a_match_cut_is_not_capped_as_a_slideshow(self):
        """The cap must not be what removes a vessel. The USER may.

        Was: assert more than SLIDE_MAX vessels survive on 30a. That held until the
        user judged the beat in pass 2 and rejected five of them — after which only
        two remain, and the test failed on the user doing their job. The number was
        never the invariant; the invariant is that the SLIDESHOW CAP is not what
        withheld them.
        """
        if not self.shots: self.skipTest("shotlist.capacity.json not built")
        rejected = set(self.picks.get("30-30a", {}).get("rejected") or [])
        pool = {r["id"]: r for r in pool_or_skip(self)}
        vessels = {r["id"] for r in C.match_cut_pool(pool)}
        # THE DEFECT THIS GUARDS, precisely: on 2026-09-21 beat 30a took 43 rows in
        # and put 4 out, and ALL 17 vessels were dropped because three
        # history-slideshow families filled SLIDE_MAX first. Zero reached the user.
        #
        # It is NOT a defect that most vessels are absent now. The slate is 10 wide,
        # 23 families compete for it, and the user has rejected five. A vessel
        # losing to the limit is the limit working. The regression is vessels
        # reaching ZERO while the admission claims to have fired.
        x = self.shots["30-30a"]
        note = x.get("floodNote") or ""
        self.assertIn("match-cut vessel(s) are admitted", note,
                      "the b-roll admission did not fire on a flagged beat")
        got = vessels & reachable(x)
        self.assertGreater(len(got), 0,
                           f"the admission fired and not one of {len(vessels)} "
                           f"vessels reached the slate — LOG 0030 is back")
        self.assertTrue(got - rejected or not (vessels - rejected),
                        "every reachable vessel is one the user already rejected")

    def test_no_user_selection_ever_falls_out_of_its_slate(self):
        # a pick is the strongest evidence in the system. A rebind dropped one on
        # 2026-09-21 and the slate stopped showing it. LOG 0031.
        if not self.shots: self.skipTest("shotlist.capacity.json not built")
        lost = [(k, i) for k, b in self.picks.items()
                for i in b.get("selected") or []
                if i not in reachable(self.shots[k])]
        self.assertEqual(lost, [], f"{len(lost)} user selections no longer shown")

    def test_every_user_selection_is_a_binding_that_survives_a_rerun(self):
        import bind
        named = bind._user_named()
        for k, b in self.picks.items():
            for i in b.get("selected") or []:
                self.assertIn(i, named.get(b["job"], []), f"{k}: {i} not user-named")

    def test_assert_without_data_beats_reach_a_vessel(self):
        # the job scored 0/12 in review because nothing in its slate could hold footage
        if not self.shots: self.skipTest("shotlist.capacity.json not built")
        aw = [k for k, s in self.shots.items() if s["job"] == "assert_without_data"]
        self.assertTrue(aw)
        for k in aw:
            self.assertTrue(self.mc_in(k), f"{k} still has no match-cut option")


class CapacityIsNotAGate(unittest.TestCase):
    """FACTS 2.7: a slot count is not static. Capacity ranks, it never excludes.

    Synthetic records throughout, so this runs without the scene library.
    """

    def rows(self):
        return [{"id": "big--scene-001",  "axes": {"slots_at_once": 20},
                 "provenance": {"verdict": "clear"}},
                {"id": "right--scene-001", "axes": {"slots_at_once": 4},
                 "provenance": {"verdict": "clear"}},
                {"id": "near--scene-001",  "axes": {"slots_at_once": 5},
                 "provenance": {"verdict": "clear"}}]

    def test_a_poor_fit_is_ranked_last_not_removed(self):
        import shotlist
        rows, note = shotlist.capacity_rank({"entity_count": 4}, self.rows(), {})
        self.assertEqual(len(rows), 3, "capacity must never drop a record")
        fits = {r["id"]: r["_capfit"] for r in rows}
        self.assertEqual(fits["right--scene-001"], "exact")
        self.assertEqual(fits["near--scene-001"], "within")
        self.assertEqual(fits["big--scene-001"], "outside")
        self.assertIn("re-cuttable", note)

    def test_the_slate_puts_the_good_fit_first_and_still_shows_the_rest(self):
        import shotlist
        rows, _ = shotlist.capacity_rank({"entity_count": 4}, self.rows(), {})
        slate = [r["id"] for r in C.diversify(rows, limit=12)[0]]
        self.assertEqual(len(slate), 3, "a poor fit was excluded, not ranked")
        self.assertEqual(slate[0], "right--scene-001")
        self.assertEqual(slate[-1], "big--scene-001")

    def test_a_beat_whose_options_are_all_poor_fits_still_gets_a_slate(self):
        import shotlist
        rows = [{"id": "big--scene-001", "axes": {"slots_at_once": 20},
                 "provenance": {"verdict": "clear"}}]
        rows, note = shotlist.capacity_rank({"entity_count": 2}, rows, {})
        self.assertEqual(len(rows), 1)
        self.assertIn("Every option is beyond", note)
        self.assertEqual(len(C.diversify(rows, limit=12)[0]), 1)

    def test_a_match_cut_vessel_is_not_ranked_by_the_beats_count(self):
        # its slots hold sourced footage, not the beat's entities
        rows = [{"id": "v--scene-001", "axes": {"slots_at_once": 15},
                 "provenance": {"verdict": "match-cut"}}]
        import shotlist
        rows, _ = shotlist.capacity_rank({"entity_count": 1}, rows, {})
        self.assertEqual(rows[0]["_capfit"], "footage")


class PriorRejections(unittest.TestCase):
    """Never show a human an option they already rejected for that beat."""

    @classmethod
    def setUpClass(cls):
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        cls.shots = ({f"{x['passage']}-{x['beat']}": x for x in json.load(open(f))}
                     if f.exists() else {})
        p = ROOT / "grammar" / "picks.json"
        cls.picks = json.load(open(p))["beats"] if p.exists() else {}

    def test_no_slate_reshows_a_rejected_option(self):
        # measured before the fix: 77 of 328 options were repeats. LOG 0041.
        if not self.shots: self.skipTest("shotlist not built")
        for k, s in self.shots.items():
            rej = set(self.picks.get(k, {}).get("rejected") or [])
            if not rej: continue
            shown = {o["id"] for o in s["options"]}
            repeats = shown & rej
            # TWO permitted cases, and the note must name whichever applies:
            #   every candidate was rejected, so an empty slate is worse; or
            #   the user NAMED this record for this beat, which is a current
            #   instruction and outranks a past verdict.
            if repeats:
                note = s.get("floodNote") or ""
                ok = ("rejected in an earlier pass" in note
                      or "named it for this beat directly" in note)
                self.assertTrue(ok, f"{k} re-shows {len(repeats)} rejected options "
                                    f"without saying why")

    def test_exclusion_is_per_beat_not_global(self):
        import shotlist
        rows = [{"id": "a"}, {"id": "b"}]
        picks = {"01-01": {"rejected": ["a"]}}
        kept, _ = shotlist.drop_prior_rejections({"id": "01", "_passage": "01"}, rows, picks)
        self.assertEqual([r["id"] for r in kept], ["b"])
        # a different beat is untouched
        kept2, _ = shotlist.drop_prior_rejections({"id": "02", "_passage": "02"}, rows, picks)
        self.assertEqual([r["id"] for r in kept2], ["a", "b"])

    def test_a_fully_rejected_beat_shows_them_rather_than_nothing(self):
        import shotlist
        rows = [{"id": "a"}, {"id": "b"}]
        picks = {"01-01": {"rejected": ["a", "b"]}}
        kept, note = shotlist.drop_prior_rejections({"id": "01", "_passage": "01"}, rows, picks)
        self.assertEqual(len(kept), 2)
        self.assertIn("rejected in an earlier pass", note)

    def test_no_user_selection_was_lost(self):
        if not self.shots: self.skipTest("shotlist not built")
        for k, b in self.picks.items():
            shown = reachable(self.shots[k])
            for i in b.get("selected") or []:
                self.assertIn(i, shown, f"{k}: dropping rejections lost your pick {i}")


class Spatial(unittest.TestCase):
    """A spatial scene holds any number of things; a huge beat routes to one."""

    def test_a_spatial_scene_fits_any_count(self):
        sp = [r for r in pool_or_skip(self) if C.is_spatial(r)]
        # was a literal 5. The approved list says 9 and the user confirmed 9; four
        # were held behind selectorEligible=false until they were calibrated
        # (LOG 0059). A count that can change belongs to its source.
        self.assertEqual(len(sp), expected_spatial(), "spatial count changed")
        for n in (1, 93, 5000):
            self.assertEqual(C.shape([sp[0]], n)[0][1], "unlimited")

    def test_unlimited_counts_as_feasible(self):
        self.assertIn("unlimited", C.FEASIBLE)

    def test_the_threshold_is_exclusive_at_twenty(self):
        self.assertFalse(C.needs_spatial(20))
        self.assertTrue(C.needs_spatial(21))
        self.assertFalse(C.needs_spatial(None))

    def test_big_beats_rank_spatial_first_and_exclude_nothing(self):
        """Spatial ADMITS and RANKS. It has not excluded since LOG 0042.

        Was: assert every option on a spatial-routed beat is spatial. That is the
        behaviour the user overruled — "this shouldnt be a rule! spatial templates
        can do any number of things. we said this already" — when route_spatial
        stopped being a hard filter and became a ranker. The test kept asserting
        exclusivity and kept passing, because it read pipeline/shotlist.json: the
        NON-capacity output, which no step of the workflow writes. The shipping
        artifact is shotlist.capacity.json. Found 2026-09-22, LOG 0078.

        What must hold now is ranking, not exclusivity: on a routed beat, every
        spatial option sorts ahead of every flat one.
        """
        import shotlist
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        if not f.exists(): self.skipTest("shotlist not built")
        shots = json.load(open(f))
        pool = {r["id"]: r for r in pool_or_skip(self)}
        routed = [s for s in shots if s.get("spatialRoute")]
        self.assertTrue(routed, "no beat over 20 slots — has the corpus changed?")
        # The invariant is ADMISSION. Order is decided by encoding fit first and
        # capacity second, by design, so a flat template that CARRIES what the beat
        # needs may legitimately outrank a spatial one that does not — beat 13-13a
        # does exactly that. Asserting spatial-sorts-first would re-impose the
        # priority the encoding handshake was built to override.
        for s in routed:
            ids = [o["id"] for o in s["options"]]
            self.assertTrue(any(C.is_spatial(pool[i]) for i in ids),
                            f"beat {s['passage']}-{s['beat']} is spatial-routed but "
                            f"no spatial scene reached the slate: {ids}")

    def test_the_non_capacity_output_is_not_what_anything_reads(self):
        # The guard for the defect above: a test asserting on shotlist.json is
        # asserting on an artifact the workflow never regenerates.
        src = (ROOT / "tests" / "test_pipeline.py").read_text()
        # Match the READ, not any mention — the first version of this guard matched
        # its own assertion string and failed on itself.
        bad = re.findall(r'open\(ROOT / "pipeline" / "shotlist\.json"\)', src)
        self.assertEqual(bad, [],
                         f"{len(bad)} test(s) read the non-capacity output; the "
                         f"shipping artifact is shotlist.capacity.json")

    def test_a_route_with_no_bound_spatial_scene_is_flagged(self):
        shots = json.load(open(ROOT / "pipeline" / "shotlist.capacity.json"))
        for s in shots:
            if s.get("needsTemplateSource"):
                self.assertIn("MAY NEED TEMPLATE SOURCE", s["floodNote"])


class Family(unittest.TestCase):
    """A template family is the id minus its scene/review suffix."""

    def test_all_four_suffix_shapes_collapse(self):
        # defect (2026-09-20): the regex missed --review-v2-001, so four siblings
        # read as four families and took a third of the enumerate slate
        for rid, fam in [
            ("modern-photo-slideshow-envato--scene-004", "modern-photo-slideshow-envato"),
            ("text-list-carousel--review-007",            "text-list-carousel"),
            ("archive3-carousel-galleries-2--review-v2-001", "archive3-carousel-galleries-2"),
            ("archive3-infographic-bar-charts--review-3b", "archive3-infographic-bar-charts"),
        ]:
            self.assertEqual(C._family(rid), fam, rid)

    def test_a_bare_id_is_its_own_family(self):
        self.assertEqual(C._family("22_single_measurement"), "22_single_measurement")

    def test_no_bound_id_has_an_unrecognised_suffix(self):
        ids = {r["id"] for rows in BINDINGS.values() for r in rows}
        odd = [i for i in ids if "--" in i and C._family(i) == i]
        self.assertEqual(odd, [], f"unrecognised id shape: {odd[:5]}")


class Diversify(unittest.TestCase):
    """The two caps the user set: one per template family, four per cluster."""

    def slates(self):
        return {j: C.diversify(rows, 12, 425)[0] for j, rows in BINDINGS.items()}

    def test_at_most_one_scene_per_family_in_every_job(self):
        for job, slate in self.slates().items():
            c = collections.Counter(C._family(r) for r in slate)
            worst = c.most_common(1)[0] if c else ("", 0)
            self.assertLessEqual(worst[1], C.FAM_MAX, f"{job}: {worst[0]} x{worst[1]}")

    def test_fam_max_is_actually_read(self):
        # defect (LOG 0010): FAM_MAX was declared and never used — one-per-family came
        # from the loop breaking, so setting it to 2 silently did nothing.
        rows = [rec(f"pack--scene-{i:03d}") for i in range(5)]
        real = C.FAM_MAX
        try:
            C.FAM_MAX = 1
            self.assertEqual(len(C.diversify(rows, limit=12)[0]), 1)
            C.FAM_MAX = 2
            self.assertEqual(len(C.diversify(rows, limit=12)[0]), 2)
            C.FAM_MAX = 3
            self.assertEqual(len(C.diversify(rows, limit=12)[0]), 3)
        finally:
            C.FAM_MAX = real

    def test_fam_max_never_exceeded_on_the_real_corpus(self):
        for job, rows in BINDINGS.items():
            c = collections.Counter(C._family(r) for r in C.diversify(rows, 12, 425)[0])
            worst = c.most_common(1)[0] if c else ("", 0)
            self.assertLessEqual(worst[1], C.FAM_MAX, f"{job}: {worst[0]} x{worst[1]}")

    def test_no_slate_carries_more_than_slide_max_slideshow_scenes(self):
        for job, rows in BINDINGS.items():
            slate = C.diversify(rows, 12, 425)[0]
            n = sum(1 for r in slate if C.is_slideish(r))
            self.assertLessEqual(n, C.SLIDE_MAX, f"{job}: {n} slide-ish entries")

    def test_the_cap_is_hard_the_slate_goes_short_rather_than_padding(self):
        rows = [{"id": f"photo-slideshow-{i}--review-001", "axes": {},
                 "provenance": {"verdict": "clear"}} for i in range(9)]
        slate, _, note = C.diversify(rows, limit=12)
        self.assertEqual(len(slate), C.SLIDE_MAX)
        self.assertIn("withheld", note)

    def test_slideish_matching_is_loose_on_purpose(self):
        # taste is not locked to an exact name; a pack nobody has named yet must still
        # read as slide-ish. LOG 0022.
        for fam in ("photo-slideshow-vertical-v3--review-001",
                    "some-new-carousel-pack--scene-004",
                    "brand-new-gallery-thing--review-002"):
            self.assertTrue(C.is_slideish({"id": fam}), fam)
        for fam in ("24_dense_vertical_bars", "counters-envato--scene-001",
                    "truth-population-field", "archive3-infographic-bar-charts--review-001"):
            self.assertFalse(C.is_slideish({"id": fam}), fam)

    def test_a_clear_binding_outranks_a_conditional_one_inside_a_family(self):
        cond = {"id": "p--scene-001", "axes": {}, "provenance": {"verdict": "conditional"}}
        clear = {"id": "p--scene-002", "axes": {}, "provenance": {"verdict": "clear"}}
        self.assertEqual(C.diversify([cond, clear], limit=12)[0][0]["id"], "p--scene-002")

    def test_caps_apply_even_when_the_pool_is_under_the_limit(self):
        # defect (2026-09-20): `if len(rows) <= limit: return rows` short-circuited
        # ahead of all clustering, so small jobs were never diversified at all
        rows = [rec(f"pack--scene-{i:03d}", mech=f"idea {i}") for i in range(5)]
        slate, _, _ = C.diversify(rows, limit=12)
        self.assertEqual(len(slate), 1, "five siblings of one family must yield one")

    def test_slate_never_exceeds_the_limit(self):
        for job, slate in self.slates().items():
            self.assertLessEqual(len(slate), 12, job)

    def test_every_slate_member_came_from_the_input(self):
        for job, rows in BINDINGS.items():
            ids = {r["id"] for r in rows}
            for r in C.diversify(rows, 12, 425)[0]:
                self.assertIn(r["id"], ids, job)

    def test_deterministic_across_runs(self):
        for job, rows in BINDINGS.items():
            a = [r["id"] for r in C.diversify(rows, 12, 425)[0]]
            b = [r["id"] for r in C.diversify(list(reversed(rows)), 12, 425)[0]]
            self.assertEqual(a, b, f"{job}: input order changed the slate")

    def test_clustering_is_gone(self):
        # removed 2026-09-20: its cap never fired, and disabling it entirely moved 12
        # slate rows across 4 of 20 jobs. LOG 0016.
        for name in ("cluster_mechanisms", "cluster_index", "_jaccard", "_mech_tokens",
                     "CLUSTER_MAX", "CLUSTER_TH", "_overrides"):
            self.assertFalse(hasattr(C, name), f"{name} survived the removal")

    def test_a_short_slate_says_why(self):
        slate, _, note = C.diversify(BINDINGS["inversion"], 12, 425)
        self.assertLess(len(slate), 12)
        self.assertIn("families", note or "")


class Motion(unittest.TestCase):
    """A watchable clip outranks a still of equal standing, and never excludes it.

    LOG 0041, update 3. 40% of the live slate was stills — unrendered infographics.
    A still hides the thing being judged.
    """

    def pair(self):
        still = rec("aaa-still--scene-001")
        moving = rec("zzz-moving--scene-001")
        moving["clip"] = "zzz-moving--scene-001.mp4"
        return still, moving

    def test_a_family_with_a_clip_is_visited_before_one_without(self):
        still, moving = self.pair()
        slate, _, _ = C.diversify([still, moving], limit=1, corpus_size=425)
        self.assertEqual([r["id"] for r in slate], ["zzz-moving--scene-001"])

    def test_motion_ranks_and_never_excludes(self):
        still, moving = self.pair()
        slate, _, _ = C.diversify([still, moving], limit=10, corpus_size=425)
        self.assertEqual(len(slate), 2)
        self.assertEqual(slate[0]["id"], "zzz-moving--scene-001")

    def test_the_motion_key_is_actually_read(self):
        # The guard LOG 0010 taught us to write: neutralise has_motion and the order
        # must revert to the alphabetical fallback. If it does not, the key is a no-op
        # and this test is watching the loop rather than the rule.
        still, moving = self.pair()
        real = C.has_motion
        try:
            C.has_motion = lambda r, pool_index=None: True
            slate, _, _ = C.diversify([still, moving], limit=1, corpus_size=425)
        finally:
            C.has_motion = real
        self.assertEqual([r["id"] for r in slate], ["aaa-still--scene-001"])


class SlateNote(unittest.TestCase):
    """A slate shorter than the limit must say why, and the reason must be true."""

    @classmethod
    def setUpClass(cls):
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        cls.shots = json.load(open(f)) if f.exists() else []

    def test_a_short_slate_does_not_blame_the_library_when_the_library_had_enough(self):
        # defect (2026-09-21): the note read "the library has only 17 families" on a
        # 6-option slate at limit 10. The slide cap ended it, not the library.
        rows = [rec(f"photo-slideshow-{i}--scene-001") for i in range(20)]
        slate, _, note = C.diversify(rows, limit=10, corpus_size=425)
        self.assertLess(len(slate), 10)
        self.assertNotIn("the library has only", note)
        self.assertIn("slideshow cap", note)

    def test_a_genuinely_small_library_is_still_reported_as_such(self):
        """When the job really is thin, say so — but only from the BOUND count.

        Was: assert the note contains "the library has only 3 families". That
        sentence was computed from the post-rejection rows, so on 04-04 it read
        "only 2 families" for a job bound across 8. LOG 0077 replaced it. The
        rule this test guards is unchanged: a genuinely small library must still
        be reported as one. What changed is where the number may come from.
        """
        rows = [{"id": f"t{i}", "_fit": 0, "_enc": 0} for i in range(3)]
        idx = {f"t{i}": {"id": f"t{i}", "template": f"fam{i}"} for i in range(3)}
        _sl, _fl, note = C.diversify(rows, limit=10, pool_index=idx, bound_families=3)
        self.assertIn("3 families are bound to this job", note)
        self.assertIn("all of them reached this beat", note)
        self.assertNotIn("the library has only", note)

    def test_a_shortfall_caused_by_rejections_is_not_blamed_on_the_library(self):
        # 8 families bound, 2 survived to this beat. The note must name the
        # removal, not the library. This is the 04-04 case exactly.
        rows = [{"id": f"t{i}", "_fit": 0, "_enc": 0} for i in range(2)]
        idx = {f"t{i}": {"id": f"t{i}", "template": f"fam{i}"} for i in range(2)}
        _sl, _fl, note = C.diversify(rows, limit=10, pool_index=idx, bound_families=8)
        self.assertIn("8 families are bound to this job, 2 reached this beat", note)
        self.assertIn("not missing from the library", note)

    def test_every_short_slate_in_the_live_shotlist_names_a_true_reason(self):
        if not self.shots: self.skipTest("shotlist not built")
        limit = max(len(b["options"]) for b in self.shots)
        for b in self.shots:
            n = len(b["options"])
            if n >= limit: continue
            note = b.get("floodNote") or ""
            m = re.search(r"the library has only (\d+) famil", note)
            self.assertTrue(note, f"{b['passage']}-{b['beat']}: {n} options, no reason given")
            if m:
                self.assertLess(int(m.group(1)), limit,
                                f"{b['passage']}-{b['beat']}: blames a library of "
                                f"{m.group(1)} families for a slate of {n} at limit {limit}")


class SpatialRanksNeverExcludes(unittest.TestCase):
    """A high entity count admits spatial scenes and ranks them first. It never
    excludes the flat templates. LOG 0042 — the last hard capacity gate."""

    def pool(self):
        return {"sp": {"id": "sp", "kind": "cinematic_3d"},
                "flat": {"id": "flat", "kind": "slideshow"}}

    def test_a_bound_spatial_scene_does_not_remove_the_flat_ones(self):
        import shotlist
        bound = [{"id": "sp"}, {"id": "flat"}]
        rows, note = shotlist.route_spatial({"entity_count": 93}, bound, self.pool())
        self.assertEqual({r["id"] for r in rows}, {"sp", "flat"})
        self.assertNotIn("spatial scenes only", note)

    def test_with_no_bound_spatial_scene_the_unbound_ones_are_added_not_substituted(self):
        import shotlist
        bound = [{"id": "flat"}]
        rows, note = shotlist.route_spatial({"entity_count": 93}, bound, self.pool())
        self.assertEqual([r["id"] for r in rows], ["sp", "flat"])
        self.assertIn("MAY NEED TEMPLATE SOURCE", note)

    def test_a_beat_under_the_threshold_is_untouched(self):
        import shotlist
        bound = [{"id": "flat"}]
        rows, note = shotlist.route_spatial({"entity_count": 4}, bound, self.pool())
        self.assertIs(rows, bound)
        self.assertIsNone(note)

    def test_the_spatial_scene_still_ranks_first_after_the_gate_is_gone(self):
        # the whole justification for deleting the filter: capacity_rank already
        # sorts it. If this fails, the gate was doing work and must come back.
        import shotlist
        pool = self.pool()
        bound = [{"id": "flat", "axes": {"subjects": 8}}, {"id": "sp"}]
        ranked, _n = shotlist.capacity_rank({"entity_count": 93}, bound, pool)
        rows, _ = shotlist.route_spatial({"entity_count": 93}, ranked, pool)
        FIT = {"exact": 0, "unlimited": 0, "footage": 0, "within": 1,
               "unknown": 2, "outside": 3}
        got = {r["id"]: FIT.get(r.get("_capfit"), 2) for r in rows}
        self.assertLess(got["sp"], got["flat"],
                        f"spatial must outrank a flat template for 93 things: {got}")

    def test_no_live_slate_is_shortened_by_the_route(self):
        """Every spatial-routed beat's size is explained by the family cap alone.

        Fails on the pre-fix shotlist: beat 13a read "20 bound ... showing 1".
        Beat 03 legitimately shows 2 — it has 2 families — so the assertion is
        `showing == min(families, limit)`, not a floor on the count.
        """
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        if not f.exists(): self.skipTest("shotlist not built")
        shots = json.load(open(f))
        limit = max(len(b["options"]) for b in shots)
        for b in shots:
            if not b.get("spatialRoute"): continue
            k, note = f"{b['passage']}-{b['beat']}", b.get("floodNote") or ""
            self.assertNotIn("routed to spatial scenes only", note, k)
            # Wording changed in LOG 0077 ("N bound across" -> "N candidate(s)
            # here across"). This regex silently stopped matching and the test fell
            # through to a DIFFERENT assertion, reporting "short and unexplained" on
            # a beat whose behaviour had not changed at all. Accept both spellings
            # so a future rewording fails loudly here instead of elsewhere.
            m = re.search(r"(\d+) (?:bound across|candidate\(s\) here across) "
                          r"(\d+) template families; showing (\d+)", note)
            if not m:
                # diversify emits the family accounting only when it has something to
                # explain. No accounting means a full slate, which is the strongest
                # possible evidence the route starved nothing.
                self.assertEqual(len(b["options"]), limit, f"{k}: short and unexplained")
                continue
            _bound, fams, showing = (int(x) for x in m.groups())
            self.assertEqual(showing, min(fams, limit),
                             f"{k}: showing {showing} of {fams} families at limit {limit}")


class NarrationTotal(unittest.TestCase):
    """The narration length is read, never written down."""

    def test_no_hardcoded_total_in_the_run_summary(self):
        # defect (2026-09-21): `of 823.5s` was a literal. The narration is 480.9s, so
        # coverage printed 53% when it was 91%, and the gap was quoted all session.
        src = (ROOT / "pipeline" / "shotlist.py").read_text()
        # the literal survives in the comment explaining it; what must not survive is
        # a total baked into the output.
        self.assertNotIn("of 823.5s", src)
        self.assertIn("narration_seconds()", src)

    def test_the_total_matches_the_timing_file(self):
        import shotlist
        try:
            got = shotlist.narration_seconds()
        except (PermissionError, FileNotFoundError) as e:
            self.skipTest(f"timing file unreadable ({type(e).__name__})")
        self.assertAlmostEqual(got, 480.9, places=1)


class ReelSegmenter(unittest.TestCase):
    """Cutting a vendor demo reel into candidate designs. LOG 0047.

    These reels have no hard cuts, so the holds are found from bursts of low-threshold
    transition activity. The tuning is the part that can silently go wrong, so it is
    the part under test — against synthetic transition lists, not against ffmpeg.
    """

    def seg(self):
        sys.path.insert(0, str(ROOT / "pipeline"))
        import segment_reel
        return segment_reel

    def test_a_burst_of_transitions_is_one_event_not_many(self):
        S = self.seg()
        # an animate-in fires several frames in a row; that is ONE boundary
        ts = [1.0, 1.1, 1.2, 1.3, 10.0, 10.1]
        hs = S.holds(ts, 20.0, 2.0)
        self.assertEqual(len(hs), 2, f"burst not collapsed: {hs}")

    def test_a_hold_shorter_than_the_threshold_is_not_offered(self):
        S = self.seg()
        ts = [1.0, 2.0, 3.0, 4.0]          # nothing sits still for 2s
        self.assertEqual(S.holds(ts, 5.0, 2.0), [])

    def test_the_tail_after_the_last_transition_counts_as_a_hold(self):
        S = self.seg()
        hs = S.holds([1.0], 10.0, 2.0)
        self.assertIn((1.0, 10.0), hs)

    def test_tuning_lands_in_the_target_band_when_it_can(self):
        S = self.seg()
        # a reel with a design change every ~5s for 60s
        ts = [float(t) for t in range(5, 60, 5)]
        mh, n = S.tune(ts, 60.0)
        self.assertTrue(S.TARGET[0] <= n <= S.TARGET[1],
                        f"tuned to {mh}s giving {n} holds, outside {S.TARGET}")

    def test_a_fixed_threshold_would_have_under_sampled_the_grunge_reel(self):
        # the defect that forced per-reel tuning: at a fixed 2.0s the grunge reel
        # gave 4 candidates and dropped its body-text block. Its real transition
        # times, measured 2026-09-21.
        S = self.seg()
        ts = [1.6, 3.3, 3.43, 3.57, 3.7, 3.83, 5.47, 6.5, 7.37, 9.0, 9.93, 11.77,
              15.8, 21.37, 21.97, 22.17, 22.2, 24.13, 24.27, 24.4, 29.2, 29.7, 30.0,
              30.37, 30.5, 31.0, 31.13, 31.27, 31.4, 31.53, 31.63, 31.67, 32.7,
              32.83, 32.97, 33.33, 33.6, 33.73, 34.0, 34.37, 34.5, 34.63, 34.77,
              34.9, 35.03, 35.17, 35.33, 36.37]
        self.assertLess(len(S.holds(ts, 45.47, 2.0)), 6, "fixed 2.0s should starve it")
        mh, n = S.tune(ts, 45.47)
        self.assertGreaterEqual(n, 8, f"tuning should recover it, got {n} at {mh}s")


class MeasuredClipWins(unittest.TestCase):
    """A record's clip is the one that was WATCHED, not the vendor's whole reel.

    LOG 0051. `sourcePath` is the full demo reel. For three Archive 3 records it was
    the pool's clip — a 29s, a 52s and a 45s reel standing in for a 3s, 10s and 4s
    scene. A review UI would have played the reel, and handoff 025 shipped those reel
    paths to Codex, who caught it on a read-only preflight. 66 of 375 differed.
    """

    def test_the_pool_clip_is_the_measured_clip_wherever_one_exists(self):
        pool = {r["id"]: r for r in pool_or_skip(self)}
        cap = json.load(open(ROOT / "grammar" / "capability.json"))
        bad = []
        for rid, r in pool.items():
            cp = (cap.get(rid) or {}).get("clip_path")
            if cp and r.get("clip") and os.path.abspath(r["clip"]) != os.path.abspath(cp):
                bad.append(rid)
        self.assertEqual(bad, [], f"pool clip is not the measured clip: {bad[:5]}")

    def test_no_pooled_clip_is_a_whole_vendor_reel(self):
        # the shape of the defect, independent of the fix: a scene cut and a demo
        # reel are not interchangeable, and the reel names itself
        pool = {r["id"]: r for r in pool_or_skip(self)}
        reels = [rid for rid, r in pool.items()
                 if (r.get("clip") or "").endswith("preview_540p_crf22_higher_quality.mp4")
                 and "--" in rid]
        self.assertEqual(reels, [], f"scene records pointing at a whole reel: {reels[:5]}")


class LocalTemplates(unittest.TestCase):
    """Templates on this side of the tree reach the pool. LOG 0049.

    approved-list.json is in Codex's tree and this side never writes it, so without
    the sidecar a template the user hands over has no route into the pool at all.
    """

    def pool(self):
        return {r["id"]: r for r in pool_or_skip(self)}

    def test_a_measured_sidecar_record_reaches_the_pool(self):
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no local templates")
        cap = json.load(open(ROOT / "grammar" / "capability.json"))
        # a SCOPED record stays out of the default pool even once measured — it
        # is admitted per beat by admit_scoped, which is the whole point of
        # SCOPE.md. Check it against the all-scopes load instead.
        want = {r["id"] for r in json.load(open(f))["records"] if r["id"] in cap}
        if not want: self.skipTest("none measured yet")
        everything = {r["id"] for r in C.load(content_class="*")}
        self.assertEqual(want - everything, set(),
                         "measured sidecar records missing from the pool")

    def test_an_unmeasured_record_is_pending_not_present(self):
        """The rule two tests collided over.

        Loader.test_every_record_has_a_description requires every pool record to have
        one, because PROMPT-bind judges the description and an empty one is unjudgeable.
        Claude is not allowed to write a description from a contact sheet. Both hold
        only if an unmeasured record is NOT IN THE POOL — pending, and listed as such,
        so "not yet measured" never looks like "not there".
        """
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no local templates")
        cap = json.load(open(ROOT / "grammar" / "capability.json"))
        unmeasured = {r["id"] for r in json.load(open(f))["records"] if r["id"] not in cap}
        pool = self.pool()
        self.assertEqual(unmeasured & set(pool), set(), "unmeasured record in the pool")
        self.assertEqual(set(C.local_pending()), unmeasured,
                         "pending list does not match what is unmeasured")

    def test_a_sidecar_id_can_receive_its_first_capability_record(self):
        """The deadlock Codex found in handoff 025, before any paid call.

        _local() holds a record out of the pool until it is measured, and
        ingest_capability.py gated on the pool — so a sidecar record could never
        receive its FIRST measurement. Held out for lacking one, unmeasurable for
        being held out.
        """
        sys.path.insert(0, str(ROOT / "pipeline"))
        import ingest_capability as I
        pending = C.local_pending()
        if not pending: self.skipTest("nothing pending")
        src = (ROOT / "pipeline" / "ingest_capability.py").read_text()
        self.assertIn("local_pending()", src,
                      "ingest gates on the pool alone — sidecar ids cannot bootstrap")
        self.assertTrue(hasattr(I, "validate"))

    def test_bootstrap_does_not_open_the_selection_gate(self):
        # the other half of Codex's instruction: "Do not weaken the candidate-pool
        # gate." Ingest may accept an id that selection must still refuse.
        cap = json.load(open(ROOT / "grammar" / "capability.json"))
        for rid in C.local_pending():
            self.assertNotIn(rid, cap, "local_pending is stale")
            self.assertNotIn(rid, self.pool(), f"{rid} reached the pool unmeasured")

    def test_a_pooled_local_record_took_its_description_from_the_measurement(self):
        cap = json.load(open(ROOT / "grammar" / "capability.json"))
        for rid, r in self.pool().items():
            if not r.get("local"): continue
            self.assertTrue(r.get("description"), f"{rid} in the pool with no description")
            self.assertIn(rid, cap, f"{rid} in the pool but never measured")

    def test_a_clip_override_attaches_without_creating_a_record(self):
        """Attaching a clip and registering a template are different things.

        base-single-billboard is IN the approved list and carries only a PNG, so the
        video pass could never see it. Registering the render as a local TEMPLATE
        put an approved record into local_pending() and broke both tests guarding
        the pending gate. A clip override patches the existing record instead.
        """
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no local templates")
        ovr = json.load(open(f)).get("clipOverrides") or {}
        if not ovr: self.skipTest("no clip overrides")
        pool = self.pool()
        for rid, o in ovr.items():
            self.assertIn(rid, pool, f"{rid} override targets a record not in the pool")
            self.assertEqual(pool[rid]["clip"], o["clip"], f"{rid} override not applied")
            self.assertNotIn(rid, C.local_pending(),
                             f"{rid} is an approved record and must not be pending")
            self.assertTrue((o.get("provenance") or {}).get("reason"),
                            f"{rid} override has no reason recorded")

    def test_a_local_clip_exists_on_disk(self):
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no local templates")
        for r in json.load(open(f))["records"]:
            self.assertTrue(pathlib.Path(r["clip"]).exists(),
                            f"{r['id']}: sidecar names a clip that is not there")

    def test_every_local_clip_has_a_poster(self):
        # dropping a poster is not a size lever — CLAUDE.md. A <video> with no
        # poster is a black rectangle until played.
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no local templates")
        for r in json.load(open(f))["records"]:
            # a record may name its poster outright — needed when the clip lives in
            # Codex's tree and no frame can be grabbed from this side
            jpg = pathlib.Path(r.get("poster") or (r["clip"][:-4] + ".jpg"))
            self.assertTrue(jpg.exists(), f"{r['id']}: clip with no poster")

    def test_every_cut_matches_the_span_it_claims(self):
        """A cut that silently lands somewhere else is the worst kind of wrong:
        the record says 20-23s, the reviewer judges something from 40s, and the
        binding is made against a clip nobody meant."""
        import subprocess
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no local templates")
        for r in json.load(open(f))["records"]:
            if not r.get("sourceSpan"): continue      # a whole-file clip override
            a, b = r["sourceSpan"]
            out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                  "format=duration", "-of", "csv=p=0", r["clip"]],
                                 capture_output=True, text=True)
            if not out.stdout.strip(): self.skipTest("ffprobe unavailable")
            self.assertAlmostEqual(float(out.stdout), b - a, delta=0.6,
                                   msg=f"{r['id']}: cut is not {b-a:.1f}s")

    def test_a_user_intent_never_becomes_a_description(self):
        """The user labels a pack with what they reached for it to do — DERIVATION,
        OVERLAP. That is an intent and evidence of nothing about what it carries.

        The sidecar must never carry a pre-written description: it comes from the
        measurement's `asserts`, so the label cannot become the text a binding is
        judged on.
        """
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no local templates")
        for r in json.load(open(f))["records"]:
            if not r.get("userIntent"): continue
            self.assertIsNone(r.get("description"),
                              f"{r['id']}: description written before measurement")

    def test_a_reading_that_agrees_with_the_label_is_marked_provisional(self):
        """The unsound test this replaces, and why.

        I first asserted that a userIntent must NEVER appear in the record's
        `carries`. That fires when the label is RIGHT: ai-flowchart is labelled
        DERIVATION and genuinely carries derivation — connector lines make "this
        came from that" visible in the form. The test would have forced a wrong
        classification to stay green, which is worse than no test.

        String equality cannot detect whether a label CAUSED a classification. What
        can be checked is that any reading Claude made is marked as Claude's, so an
        agreement with the label is always traceable and always replaceable.
        """
        cap = json.load(open(ROOT / "grammar" / "capability.json"))
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no local templates")
        labels = {r["id"]: r["userIntent"].lower()
                  for r in json.load(open(f))["records"] if r.get("userIntent")}
        for rid, label in labels.items():
            c = cap.get(rid)
            if c is None: continue
            if label in [x.lower() for x in (c.get("carries") or [])]:
                self.assertTrue(c.get("provisional") or c.get("prompt_sha256"),
                                f"{rid} carries its own label with no provenance "
                                f"saying who decided that")

    def test_a_claude_visual_record_says_so(self):
        cap = json.load(open(ROOT / "grammar" / "capability.json"))
        for rid, c in cap.items():
            if c.get("source") != "claude-visual": continue
            self.assertTrue(c.get("provisional"), f"{rid} not marked provisional")
            self.assertIsNone(c.get("prompt_sha256"),
                              f"{rid} claims a prompt sha it did not come from")
            self.assertIn("not measured", (c.get("provenance_note") or "").lower())

    def test_the_sidecar_records_where_each_span_came_from(self):
        # two of the six spans are timecodes the user typed, four are candidates they
        # picked in the gallery. Both are their choice; the provenance must say which.
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no local templates")
        for r in json.load(open(f))["records"]:
            self.assertIn(r.get("spanSource"), ("user", "segmenter"), r["id"])
            self.assertEqual((r.get("provenance") or {}).get("source"), "user", r["id"])
            self.assertTrue((r.get("provenance") or {}).get("reason"), r["id"])


class RankIsComparative(unittest.TestCase):
    """`carries: rank` means who is AHEAD, never the order things arrive in.

    LOG 0050. Ten of fifteen records carrying `rank` are scrolling text lists whose
    `implies` omits ranking and competition entirely. The model was following the
    prompt, which said "their order is only apparent from where they sit". A
    scrolling list satisfies that and asserts nothing about who beats whom.

    Real supply for `rank` is ~5 of 421, and it was reported at 15.
    """

    # EMPTIED 2026-09-21. All ten were re-measured under prompt sha d58028d6 and the
    # new wording removed `rank` from every one of them — 15 carriers became 5, and
    # all 5 survivors imply ranking or competition. The staleness test is what forced
    # this deletion rather than leaving a permanent exemption behind.
    RANK_PENDING_REMEASURE = set()

    def conflated(self):
        f = ROOT / "grammar" / "capability.json"
        if not f.exists(): self.skipTest("no capability records")
        cap = json.load(open(f))
        return {i for i, r in cap.items()
                if "rank" in (r.get("carries") or [])
                and not {"ranking", "competition"} & set(r.get("implies") or [])}

    # The ten that were conflated under the old wording. Re-measured 2026-09-21
    # under sha a975db17; every one came back WITHOUT rank. This is the regression.
    WERE_CONFLATED = {
        "archive3-carousel-flow-loops-2026-09-15-08-02-14-utc--review-004",
        "archive3-dropoff-carousels-2026-09-15-17-30-59-utc--review-003",
        "text-list-carousel--review-001", "text-list-carousel--review-002",
        "text-list-carousel--review-004", "text-list-carousel--review-006",
        "text-list-carousel--review-007", "text-list-carousel--review-008",
        "text-list-carousel--review-009", "text-list-carousel--review-010",
    }

    def test_the_ten_conflated_records_no_longer_carry_rank(self):
        """The concrete regression, replacing a proxy that outlived its defect.

        The cross-field check — `rank` with neither `ranking` nor `competition` in
        `implies` — caught all ten when the prompt was wrong. With the prompt fixed
        it produces a FALSE POSITIVE: 3dz-charts--scene-001 is six bars of differing
        height on a shared baseline, which genuinely carries comparative rank and
        does not imply competition. And the reverse proxy fails too —
        05_measured_height_ruler reveals in turn AND carries real rank, so
        staging is no proxy either.
        There is no cheap structural test for "is this comparative". What can be
        tested is the actual defect: these ten must not carry rank.
        """
        cap = json.load(open(ROOT / "grammar" / "capability.json"))
        back = sorted(i for i in self.WERE_CONFLATED
                      if "rank" in ((cap.get(i) or {}).get("carries") or []))
        self.assertEqual(back, [], f"the scroll/rank conflation returned: {back}")

    def test_the_quarantine_is_empty_and_stays_empty(self):
        """It did its job: it forced the deletion once the re-measure landed."""
        self.assertEqual(self.RANK_PENDING_REMEASURE, set())

    def test_the_prompt_no_longer_defines_rank_as_where_things_sit(self):
        src = (ROOT / "prompts" / "PROMPT-describe-clip.md").read_text()
        self.assertNotIn("their order is only apparent from where they sit", src)
        self.assertIn("COMPARATIVE rank, never sequence position", src)


class Handshake(unittest.TestCase):
    """encoding_rank: does this template encode what the beat needs seen?

    LOG 0053/0054. The mechanism gap, one field lower than Codex found it.
    must_be_perceptible was copied into the shot record AFTER the slate was chosen
    and nothing ever read it.
    """

    def sl(self):
        sys.path.insert(0, str(ROOT / "pipeline"))
        import shotlist
        return shotlist

    POOL = {"has": {"id": "has", "capability": {"carries": ["aggregate", "identity"],
                                                "readable": ["none"]}},
            "part": {"id": "part", "capability": {"carries": ["identity"],
                                                  "readable": ["exact_value"]}},
            "unmeasured": {"id": "unmeasured", "capability": None}}

    def test_a_template_that_encodes_the_requirement_ranks_first(self):
        S = self.sl()
        rows = [{"id": "part"}, {"id": "has"}]
        rows, _ = S.encoding_rank({}, rows, self.POOL, {"carries": {"aggregate"}})
        self.assertLess(dict((r["id"], r["_encfit"]) for r in rows)["has"],
                        dict((r["id"], r["_encfit"]) for r in rows)["part"])

    def test_it_ranks_and_never_excludes(self):
        # the standing rule every other signal here obeys
        S = self.sl()
        rows = [{"id": "part"}, {"id": "has"}, {"id": "unmeasured"}]
        out, _ = S.encoding_rank({}, rows, self.POOL, {"carries": {"aggregate"}})
        self.assertEqual(len(out), 3)

    def test_unmeasured_scores_worse_than_a_measured_miss(self):
        # silence must never outrank a measured answer, in either direction
        S = self.sl()
        rows = [{"id": "part"}, {"id": "unmeasured"}]
        f = {r["id"]: r["_encfit"] for r in
             S.encoding_rank({}, rows, self.POOL, {"carries": {"aggregate"}})[0]}
        self.assertGreater(f["unmeasured"], f["part"])

    def test_a_beat_with_no_recorded_requirement_ranks_nothing(self):
        S = self.sl()
        rows = [{"id": "part"}, {"id": "has"}]
        out, note = S.encoding_rank({}, rows, self.POOL, {})
        self.assertIsNone(note)
        self.assertEqual({r["_encfit"] for r in out}, {0})

    def test_the_note_names_only_what_NOTHING_in_the_slate_carries(self):
        S = self.sl()
        rows = [{"id": "has"}]
        _, note = S.encoding_rank({}, rows, self.POOL,
                                  {"carries": {"aggregate", "overlap"}})
        self.assertIn("overlap", note)
        self.assertNotIn("aggregate", note)   # `has` carries it, so it is not a gap

    def test_readable_counts_as_well_as_carries(self):
        S = self.sl()
        rows = [{"id": "has"}, {"id": "part"}]
        f = {r["id"]: r["_encfit"] for r in
             S.encoding_rank({}, rows, self.POOL, {"readable": {"exact_value"}})[0]}
        self.assertLess(f["part"], f["has"])

    def test_encoding_outranks_capacity_in_the_family_order(self):
        """The ordering claim, not just the annotation.

        A slot count is re-cuttable and rendering happens after selection, so
        capacity is a hint about scale. Whether a template can make the relation
        visible is not adjustable downstream.
        """
        good = rec("enc--scene-001"); good["_encfit"] = 0; good["_capfit"] = "outside"
        bad = rec("cap--scene-001");  bad["_encfit"] = 3;  bad["_capfit"] = "exact"
        slate, _, _ = C.diversify([bad, good], limit=1, corpus_size=425)
        self.assertEqual([r["id"] for r in slate], ["enc--scene-001"],
                         "capacity fit beat encoding fit — the order is wrong")

    def test_no_user_selection_was_lost_to_the_handshake(self):
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        if not f.exists(): self.skipTest("shotlist not built")
        shots = {f"{x['passage']}-{x['beat']}": x for x in json.load(open(f))}
        picks = json.load(open(ROOT / "grammar" / "picks.json"))["beats"]
        lost = [(k, i) for k, v in picks.items() for i in (v.get("selected") or [])
                if i not in reachable(shots[k])]
        self.assertEqual(lost, [], f"handshake ranking lost user picks: {lost}")


class Siblings(unittest.TestCase):
    """The rest of a family rides behind an expander. LOG 0054.

    FAM_MAX=1 was set after a slate came back 7 scenes from one pack. The cap is
    right — but it hid 429 bound siblings across 40 beats, and the user twice said
    "right family, wrong scene" with no way to reach the sibling.
    """

    def test_a_shown_scene_carries_the_rest_of_its_family(self):
        rows = [rec(f"pack--scene-{i:03d}") for i in range(4)]
        slate, _, _ = C.diversify(rows, limit=10, corpus_size=425)
        self.assertEqual(len(slate), 1, "FAM_MAX should still show one")
        self.assertEqual(len(slate[0]["_siblings"]), 3, "the other three are lost")

    def test_the_shown_scene_is_not_its_own_sibling(self):
        rows = [rec(f"pack--scene-{i:03d}") for i in range(3)]
        slate, _, _ = C.diversify(rows, limit=10, corpus_size=425)
        self.assertNotIn(slate[0]["id"], slate[0]["_siblings"])

    def test_siblings_keep_the_within_family_order(self):
        # [0] is the shown one, so the siblings are the same ranking minus the head
        rows = [rec(f"pack--scene-{i:03d}") for i in range(4)]
        slate, _, _ = C.diversify(rows, limit=10, corpus_size=425)
        ranked = sorted(rows, key=lambda r: C._within_family(r))
        self.assertEqual(slate[0]["_siblings"], [r["id"] for r in ranked[1:]])

    def test_a_lone_scene_has_no_siblings(self):
        slate, _, _ = C.diversify([rec("solo--scene-001")], limit=10, corpus_size=425)
        self.assertEqual(slate[0]["_siblings"], [])

    def test_siblings_cost_no_slate_slots(self):
        # the whole point: reachability without spending the cap FAM_MAX protects
        rows = ([rec(f"a--scene-{i:03d}") for i in range(5)] +
                [rec(f"b--scene-{i:03d}") for i in range(5)])
        slate, _, _ = C.diversify(rows, limit=10, corpus_size=425)
        self.assertEqual(len(slate), 2, "one per family, unchanged")
        self.assertEqual(sum(len(r["_siblings"]) for r in slate), 8)

    def test_the_live_slate_reaches_every_bound_scene_of_a_shown_family(self):
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        g = ROOT / "grammar" / "bindings.json"
        if not (f.exists() and g.exists()): self.skipTest("not built")
        grammar = json.load(open(g))
        picks = json.load(open(ROOT / "grammar" / "picks.json"))["beats"]
        for x in json.load(open(f)):
            k = f"{x['passage']}-{x['beat']}"
            shown = {o["id"] for o in x["options"]}
            reach = shown | {i["id"] for o in x["options"]
                             for i in (o.get("siblings") or [])}
            # a scene the user already rejected FOR THIS BEAT is correctly
            # unreachable — drop_prior_rejections removed it before diversify ever
            # saw the family. The expander must not resurrect a rejection.
            reach |= set(picks.get(k, {}).get("rejected") or [])
            fams = {C._family(i) for i in shown}
            missed = [r["id"] for r in (grammar.get(x["job"]) or [])
                      if C._family(r["id"]) in fams and r["id"] not in reach]
            self.assertEqual(missed, [],
                             f"{x['passage']}-{x['beat']}: family on screen but "
                             f"{len(missed)} of its scenes unreachable")

    def test_every_sibling_has_media_in_the_review_ui(self):
        ui = ROOT / "pipeline" / "ui2" / "data.json"
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        if not (ui.exists() and f.exists()): self.skipTest("not built")
        D = json.load(open(ui))
        sibs = {i["id"] for x in json.load(open(f)) for o in x["options"]
                for i in (o.get("siblings") or [])}
        # dropping a clip or a poster is not a size lever — CLAUDE.md
        no_thumb = [i for i in sibs if i in D["hasClip"] and not D["thumbs"].get(i)]
        self.assertEqual(no_thumb, [], f"siblings with a clip and no poster: {no_thumb[:5]}")


class HandSetFlags(unittest.TestCase):
    """A flag set by hand in beat-flags.json takes effect without a review pass.

    LOG 0054(D). The file documents itself as "editable by hand ... so a flag can be
    set WITHOUT running a review pass", but it only merged during ingest_picks, and
    ingest needs a pass directory. A hand-set flag did nothing until the next review.
    """

    def test_shotlist_overlays_beat_flags_on_picks(self):
        src = (ROOT / "pipeline" / "shotlist.py").read_text()
        self.assertIn("beat-flags.json", src,
                      "shotlist never reads the hand-set flags")

    def test_02b_is_flagged_and_the_flag_fired(self):
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        fl = ROOT / "grammar" / "beat-flags.json"
        if not (f.exists() and fl.exists()): self.skipTest("not built")
        flags = json.load(open(fl))["beats"]
        self.assertTrue(flags.get("02-02b", {}).get("rawBroll"))
        x = [b for b in json.load(open(f)) if f"{b['passage']}-{b['beat']}" == "02-02b"][0]
        self.assertIn("Flagged raw b-roll", x["floodNote"] or "",
                      "the flag is set and did not fire")

    def test_every_hand_set_flag_carries_the_user_s_words(self):
        fl = ROOT / "grammar" / "beat-flags.json"
        if not fl.exists(): self.skipTest("no flags")
        SET = {"rawBroll", "needsTextTemplate", "wantsMediaKind"}
        for k, v in json.load(open(fl))["beats"].items():
            flags = [f for f in SET if v.get(f)]
            if not flags:
                continue
            # A blanket `why` covers the entry; a PER-FLAG `<flag>Why` is
            # stronger, because one reason for three flags says which of them it
            # explains. Accept either, require one.
            for f in flags:
                self.assertTrue(v.get("why") or v.get(f + "Why"),
                                f"{k}.{f}: set with no reason recorded")

    def test_the_encoding_requirement_still_outranks_the_admitted_vessels(self):
        """02b needs `magnitude` AND needs to show mixtape covers.

        The b-roll flag serves the second. It must not bury the first: the scene
        that actually carries magnitude has to stay ahead of 25 admitted vessels.
        """
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        if not f.exists(): self.skipTest("not built")
        cap = json.load(open(ROOT / "grammar" / "capability.json"))
        x = [b for b in json.load(open(f)) if f"{b['passage']}-{b['beat']}" == "02-02b"][0]
        first = x["options"][0]["id"]
        self.assertIn("magnitude", (cap.get(first) or {}).get("carries") or [],
                      f"02b ranks {first} first and it does not carry magnitude")


class ScopeKey(unittest.TestCase):
    """A scope restriction must be openable. LOG 0057.

    SCOPE.md restricts three templates by content class on the user's instruction.
    load() admitted them only when content_class matched, and NOTHING in the pipeline
    ever passed one — shotlist, bind and build_review all call load() bare. A hard
    filter whose key is never turned is not a restriction, it is a deletion.
    """

    def sl(self):
        sys.path.insert(0, str(ROOT / "pipeline"))
        import shotlist
        return shotlist

    SCOPED = {"tl": {"id": "tl", "scope": "timelines", "description": "a timeline"},
              "ly": {"id": "ly", "scope": "lyrics", "description": "a lyric card"}}

    def test_a_beat_that_declares_the_class_gets_the_template(self):
        S = self.sl()
        rows, note = S.admit_scoped({"id": "06", "_passage": "06"}, [], self.SCOPED,
                                    {"06-06": {"contentClass": ["timelines"]}})
        self.assertEqual([r["id"] for r in rows], ["tl"])
        self.assertIn("scoped template", note)

    def test_a_beat_that_declares_nothing_gets_nothing(self):
        S = self.sl()
        rows, note = S.admit_scoped({"id": "07", "_passage": "07"}, [], self.SCOPED, {})
        self.assertEqual(rows, [])
        self.assertIsNone(note)

    def test_the_wrong_class_does_not_leak(self):
        S = self.sl()
        rows, _ = S.admit_scoped({"id": "06", "_passage": "06"}, [], self.SCOPED,
                                 {"06-06": {"contentClass": ["timelines"]}})
        self.assertNotIn("ly", [r["id"] for r in rows])

    def test_admission_is_recorded_as_a_user_decision(self):
        S = self.sl()
        rows, _ = S.admit_scoped({"id": "06", "_passage": "06"}, [], self.SCOPED,
                                 {"06-06": {"contentClass": ["timelines"]}})
        self.assertEqual(rows[0]["provenance"]["source"], "user")
        self.assertTrue(rows[0]["provenance"]["reason"])

    def test_it_admits_and_never_removes(self):
        S = self.sl()
        have = [{"id": "x"}, {"id": "y"}]
        rows, _ = S.admit_scoped({"id": "06", "_passage": "06"}, list(have), self.SCOPED,
                                 {"06-06": {"contentClass": ["timelines"]}})
        self.assertEqual([r["id"] for r in rows][:2], ["x", "y"])
        self.assertEqual(len(rows), 3)

    def test_the_star_load_admits_every_scoped_template(self):
        try:
            bare = {r["id"] for r in C.load()}
            allsc = {r["id"] for r in C.load(content_class="*")}
        except (PermissionError, FileNotFoundError) as e:
            self.skipTest(f"template pool unreadable ({type(e).__name__})")
        self.assertTrue(allsc - bare, "no scoped template was admitted by '*'")
        for rid in allsc - bare:
            self.assertIsNotNone(C.scope_of(rid), f"{rid} is not actually scoped")

    def test_06_06_declares_the_timeline_class(self):
        f = ROOT / "grammar" / "beat-flags.json"
        if not f.exists(): self.skipTest("no flags")
        self.assertEqual(json.load(open(f))["beats"]["06-06"]["contentClass"],
                         ["timelines"])


class ReadableVocabulary(unittest.TestCase):
    """Both halves of the handshake must use ONE vocabulary. LOG 0057.

    `label` and `statement` were added 2026-09-21 after 61% of records with text
    slots came back `readable: none` — correctly, because every value in the list
    was a data relation and none of them meant "the text is the message".
    """

    TERMS = {"label", "statement", "exact_value", "ordering", "proportion",
             "difference", "grouping", "position_in_sequence", "none"}
    CARRIES = {"magnitude", "share_of_whole", "rank", "change_over_time", "difference",
               "parity", "aggregate", "derivation", "membership", "overlap", "absence",
               "identity", "none"}
    IMPLIES = {"ranking", "competition", "chronology", "causation", "completeness",
               "equality", "independence", "none"}

    def test_both_prompts_define_the_same_readable_terms(self):
        clip = (ROOT / "prompts" / "PROMPT-describe-clip.md").read_text()
        beat = (ROOT / "prompts" / "PROMPT-perceptible.md").read_text()
        for t in self.TERMS | self.CARRIES | self.IMPLIES:
            self.assertIn(t, clip, f"describe-clip is missing `{t}`")
            self.assertIn(t, beat, f"perceptible is missing `{t}`")

    def test_both_validators_accept_the_same_terms(self):
        sys.path.insert(0, str(ROOT / "pipeline"))
        import ingest_capability as I, classify_perceptible as P
        self.assertEqual(I.READABLE, self.TERMS)
        self.assertEqual(P.READABLE, self.TERMS)
        self.assertEqual(I.CARRIES, self.CARRIES)
        self.assertEqual(P.CARRIES, self.CARRIES)
        self.assertEqual(I.IMPLIES, self.IMPLIES)
        self.assertEqual(P.IMPLIES, self.IMPLIES)

    def test_a_relation_counts_across_the_clip_not_only_in_one_frame(self):
        """The root fix, not the three patches. LOG 0068.

        Every carries definition read as a claim about a single frame while
        everything temporal lived in `staging`, so a relation the clip PERFORMS was
        recorded by neither field. overlap, aggregate and absence were assigned zero
        times across 396 records and three prompt versions.
        """
        clip = (ROOT / "prompts" / "PROMPT-describe-clip.md").read_text()
        self.assertIn("WHETHER IT IS SHOWN IN ONE FRAME OR ACROSS THE CLIP", clip)
        # each of the three must offer a SECOND form, not only the one-frame one.
        # Matching on prose is crude; what it guards is that a definition cannot be
        # narrowed back to a single frame without the test noticing.
        for t, second in (("overlap", "reducing"), ("aggregate", "gathering"),
                          ("absence", "leaving")):
            i = clip.index(f"- `{t}`")
            body = clip[i:clip.index("\n- `", i + 5)].lower()
            self.assertIn(" or ", body, f"`{t}` offers only one form")
            self.assertIn(second, body,
                          f"`{t}` lost its across-the-clip form ({second})")

    def test_the_template_side_and_the_beat_side_cannot_drift(self):
        # the handshake compares these two sets directly; if they differ, a beat can
        # require a term no clip may be given, and the gap is an artifact
        sys.path.insert(0, str(ROOT / "pipeline"))
        import ingest_capability as I, classify_perceptible as P
        self.assertEqual(I.READABLE, P.READABLE, "readable vocabularies diverged")
        self.assertEqual(I.CARRIES, P.CARRIES, "carries vocabularies diverged")


class EligibilityOverrides(unittest.TestCase):
    """A user may lift a gate in the approved list; nothing else may. LOG 0059."""

    def test_an_override_is_recorded_with_the_user_s_words(self):
        f = ROOT / "grammar" / "eligibility-overrides.json"
        if not f.exists(): self.skipTest("no overrides")
        for tid, v in json.load(open(f))["admit"].items():
            self.assertTrue(v.get("why"), f"{tid} admitted with no reason recorded")
            self.assertIn("2026-", v["why"], f"{tid}: no date on the decision")

    def test_only_overridden_templates_get_past_the_gate(self):
        try:
            raw = json.load(open(C.approved_path()))["items"]
        except (PermissionError, FileNotFoundError) as e:
            self.skipTest(f"list unreadable ({type(e).__name__})")
        admitted = set(C.eligibility_overrides())
        pool = {r["id"] for r in pool_or_skip(self)}
        for card in raw:
            tid = card.get("templateId")
            gated = (card.get("selectorEligible") is False or
                     str(card.get("catalogStatus") or "").startswith("reference_only"))
            if not gated or tid in admitted: continue
            ids = {s.get("id") for s in (card.get("scenes") or [])} | {tid}
            self.assertEqual(ids & pool, set(), f"{tid} is gated and not overridden")

    def test_the_four_calibrated_layouts_are_in_the_pool(self):
        pool = {r["id"] for r in pool_or_skip(self)}
        for tid in ("catalog-gap-clean", "topographic-cloud", "hologram-stage",
                    "kendrick-red-stage-clean"):
            self.assertIn(tid, pool, f"{tid} was calibrated and is still excluded")

    def test_an_override_does_not_resurrect_a_removed_subsystem_name(self):
        """`_overrides` was the clustering system's, and test_clustering_is_gone
        guards it. Reusing the name made a removal test fail on a live function —
        the test was right and the name was wrong."""
        self.assertFalse(hasattr(C, "_overrides"))
        self.assertTrue(hasattr(C, "eligibility_overrides"))


class LockedTextCorpus(unittest.TestCase):
    """The user narrowed the text corpus and said "nothing else". LOG 0060."""

    KEEP = {"text-list-carousel--review-002", "text-list-carousel--review-003"}

    def pool(self):
        return {r["id"] for r in pool_or_skip(self)}

    def test_only_the_two_named_carousel_scenes_survive(self):
        got = {i for i in self.pool() if i.startswith("text-list-carousel--")}
        self.assertEqual(got, self.KEEP,
                         "the carousel corpus is not what the user locked")

    def test_a_removal_is_recorded_with_the_user_s_words(self):
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no sidecar")
        for rid, v in (json.load(open(f)).get("remove") or {}).items():
            self.assertTrue(v.get("why"), f"{rid} removed with no reason recorded")

    def test_removal_is_not_supersession(self):
        """Two different operations and they must not be conflated.

        `supersedes` swaps one record for another and the replacement is named.
        `remove` takes a record out with nothing in its place. Reading a removal as
        a supersession would leave the pool waiting for a replacement that does not
        exist.
        """
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no sidecar")
        d = json.load(open(f))
        removed = set(d.get("remove") or {})
        superseded = {(r.get("provenance") or {}).get("supersedes")
                      for r in d["records"]} - {None}
        self.assertEqual(removed & superseded, set(),
                         "a record is both removed and superseded")

    def test_the_locked_text_corpus_is_exactly_ten(self):
        """CLOSED at ten, 2026-09-21.

        The user first counted eleven — 5 paper + 3 grunge + 1 glass + 2 carousel —
        then checked and corrected it: "sorry its 002, 006, 007, 008. thast 4".
        Paper is four, so the corpus is ten. It was never eleven; the gallery had
        saved five picks and one of them was a grunge scene, not a paper one.
        Worth the two exchanges: the alternative was inventing a fifth paper scene
        to make an arithmetic error true.
        """
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no sidecar")
        recs = json.load(open(f))["records"]
        by = {}
        for r in recs:
            if "lower-thirds" in r["id"]:
                by[r["id"].split("-lower-thirds")[0]] = by.get(
                    r["id"].split("-lower-thirds")[0], 0) + 1
        self.assertEqual(by, {"grunge": 3, "glass": 1, "paper": 4},
                         f"the locked composition changed: {by}")
        self.assertEqual(sum(by.values()) + len(self.KEEP), 10)

    def test_the_four_paper_scenes_are_the_ones_named(self):
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no sidecar")
        spans = sorted(tuple(r["sourceSpan"]) for r in json.load(open(f))["records"]
                       if r["id"].startswith("paper-lower-thirds"))
        self.assertEqual(spans, [(7.1, 11.17), (29.67, 33.93),
                                 (36.03, 40.4), (42.47, 46.3)],
                         "paper spans are not cand-002/006/007/008")


class CardOnlyRecords(unittest.TestCase):
    """A card with no scenes IS the record, and carries its own selection text.

    LOG 0061. Every cinematic_3d and the layered scene are shaped this way.
    Synthesizing a scene from id+title alone put all ten on title-fallback at 27-59
    characters — and PROMPT-bind judges the description.
    """

    KINDS = ("cinematic_3d", "layered_scene")

    def cards(self):
        # only records that CAME FROM a card. two-floors is a local sidecar record
        # of the same kind and has no card, so it has no selection block to read.
        local = set()
        f = ROOT / "grammar" / "local-templates.json"
        if f.exists():
            local = {r["id"] for r in json.load(open(f))["records"]}
        return [r for r in pool_or_skip(self)
                if r["kind"] in self.KINDS and r["id"] not in local]

    def test_none_of_them_is_judged_on_its_title(self):
        bad = [r["id"] for r in self.cards()
               if r["sources"]["description"] == "title-fallback"]
        self.assertEqual(bad, [], f"card-only records on title-fallback: {bad}")

    def test_the_description_is_long_enough_to_judge(self):
        # "Five-layer single billboard" is 27 characters and is a name, not a
        # description. The real text runs 147-596.
        for r in self.cards():
            self.assertGreater(len(r["description"] or ""), 100,
                               f"{r['id']}: {len(r['description'] or '')}ch")

    def test_they_carry_use_when_and_avoid(self):
        for r in self.cards():
            self.assertTrue(r.get("useWhen"), f"{r['id']} has no useWhen")

    def test_the_video_key_becomes_the_clip_where_one_exists(self):
        # the five truth-* cards name a .mp4 in `video`; the four calibrated
        # layouts name only a .png preview
        got = {r["id"]: bool(r.get("clip")) for r in self.cards()}
        self.assertTrue(got["truth-rank-fall"], "the truth-* video was not picked up")


class SpatialIsAlwaysMotion(unittest.TestCase):
    """User 2026-09-21: "spatial scenes should be treated like video een though its
    just png for some". LOG 0061."""

    def test_every_spatial_scene_counts_as_motion(self):
        pool = {r["id"]: r for r in pool_or_skip(self)}
        sp = [r for r in pool.values() if r["kind"] in C.SPATIAL_KINDS]
        self.assertTrue(sp, "no spatial scenes in the pool")
        for r in sp:
            self.assertTrue(C.has_motion(r, pool),
                            f"{r['id']} read as a still — it is a 3D scene")

    def test_a_spatial_scene_with_no_clip_still_counts(self):
        # the whole point: the PNG is a fact about the preview, not the template
        rec = {"id": "x", "kind": "cinematic_3d"}
        self.assertTrue(C.has_motion(rec, {"x": rec}))

    def test_a_flat_template_with_no_clip_does_not(self):
        rec = {"id": "y", "kind": "infographic"}
        self.assertFalse(C.has_motion(rec, {"y": rec}))

    def test_only_the_unrendered_infographics_are_stills_now(self):
        pool = {r["id"]: r for r in pool_or_skip(self)}
        kinds = {pool[i]["kind"] for i in pool if not C.has_motion(pool[i], pool)}
        self.assertLessEqual(kinds, {"infographic"},
                             f"something other than an unrendered infographic "
                             f"reads as a still: {kinds}")


class CapacityOverrides(unittest.TestCase):
    """Subject capacity the user declared where the card states it only in prose.

    LOG 0062. layerContract says L4 heroes 1-3 and L5 "five-entity CSV row" —
    unparseable into axes without a judgment, so the user made it.
    """

    def test_the_hero_carries_the_declared_capacity(self):
        pool = {r["id"]: r for r in pool_or_skip(self)}
        r = pool.get("base-single-billboard")
        if r is None: self.skipTest("hero not in the pool")
        # the override REPLACES the measured slot axes rather than joining them:
        # the pass saw one render (slots_at_once 4), the user declares the contract
        self.assertEqual(r["axes"], {"heroes": 3, "entities": 10})
        self.assertNotIn("slots_at_once", r["axes"])

    def test_every_override_axis_is_a_classified_subject_axis(self):
        """subject_axes() raises on an unclassified name, deliberately. An override
        that invents an axis would blow up at capacity time, far from the typo."""
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no sidecar")
        for rid, o in (json.load(open(f)).get("capacityOverrides") or {}).items():
            for name in (o.get("axes") or {}):
                self.assertIn(name, C.SUBJECT_AXES,
                              f"{rid}: '{name}' is not a classified subject axis")
            self.assertTrue(o.get("why"), f"{rid}: capacity set with no reason")

    def test_the_hero_fits_the_counts_the_user_named(self):
        pool = {r["id"]: r for r in pool_or_skip(self)}
        r = pool.get("base-single-billboard")
        if r is None: self.skipTest("hero not in the pool")
        self.assertEqual(C.shape([r], 3)[0][1], "exact")
        self.assertEqual(C.shape([r], 10)[0][1], "exact")

    def test_all_nine_spatial_scenes_are_unlimited(self):
        # user 2026-09-21 on the "~12-40 workable" prose: "fix that to unlimited"
        pool = {r["id"]: r for r in pool_or_skip(self)}
        sp = [r for r in pool.values() if r["kind"] in C.SPATIAL_KINDS]
        self.assertEqual(len(sp), expected_spatial())
        for r in sp:
            self.assertEqual(C.shape([r], 40)[0][1], "unlimited", r["id"])


class CapabilityManifest(unittest.TestCase):
    """A manifest may only name an id the receiver can accept. LOG 0066.

    Handoff 029 listed seven text-list-carousel scenes the user had REMOVED from the
    corpus. Their capability records remain as history — correctly — and the builder
    read capability.json directly, so the run would have bought seven clips whose
    results ingest_capability.py must refuse. Codex caught it on preflight, before
    any spend.
    """

    def builder(self):
        sys.path.insert(0, str(ROOT / "pipeline"))
        import build_capability_manifest
        return build_capability_manifest

    def test_the_manifest_names_only_ids_the_receiver_accepts(self):
        try:
            doc = self.builder().build()
        except (PermissionError, FileNotFoundError) as e:
            self.skipTest(f"pool unreadable ({type(e).__name__})")
        known = {r["id"] for r in C.load()} | set(C.local_pending())
        bad = [c["id"] for c in doc["clips"] if c["id"] not in known]
        self.assertEqual(bad, [], f"receiver would refuse: {bad}")

    def test_removed_records_are_excluded_and_counted(self):
        try:
            doc = self.builder().build()
        except (PermissionError, FileNotFoundError) as e:
            self.skipTest(f"pool unreadable ({type(e).__name__})")
        removed = C._removed()
        named = {c["id"] for c in doc["clips"]}
        self.assertEqual(named & removed, set(),
                         "a removed record is in the manifest")
        # excluded, not silently dropped — the count is reported
        self.assertIn("removedFromScope", doc)
        self.assertEqual(set(doc["removedFromScope"]["ids"]) & named, set())

    def test_every_clip_in_the_manifest_exists(self):
        try:
            doc = self.builder().build()
        except (PermissionError, FileNotFoundError) as e:
            self.skipTest(f"pool unreadable ({type(e).__name__})")
        for c in doc["clips"]:
            self.assertTrue(os.path.exists(c["clip"]), f"{c['id']}: {c['clip']}")

    def test_the_live_manifest_on_disk_agrees_with_the_builder(self):
        """A hand-edited manifest is how the last defect shipped."""
        f = ROOT / "handoff" / "outbox" / "031-capability-remeasure-corrected.json"
        if not f.exists(): self.skipTest("no manifest")
        try:
            doc = self.builder().build()
        except (PermissionError, FileNotFoundError) as e:
            self.skipTest(f"pool unreadable ({type(e).__name__})")
        on_disk = json.load(open(f))
        # A manifest is SPENT once its results are ingested: the builder then
        # rightly produces a smaller set, because the work is done. Only compare
        # while it is still outstanding.
        cap = json.load(open(ROOT / "grammar" / "capability.json"))
        outstanding = [c["id"] for c in on_disk["clips"] if c["id"] not in cap]
        if not outstanding:
            self.skipTest("manifest is spent — every id has been ingested")
        self.assertEqual({c["id"] for c in on_disk["clips"]},
                         {c["id"] for c in doc["clips"]},
                         "the manifest on disk is not what the builder produces")


class SupplyCountsOnlySelectable(unittest.TestCase):
    """A capability record for a removed template is history, not supply. LOG 0066."""

    def test_no_supply_figure_counts_an_unselectable_record(self):
        cap = json.load(open(ROOT / "grammar" / "capability.json"))
        pool = {r["id"] for r in pool_or_skip(self)}
        known = pool | set(C.local_pending())
        scoped = {r["id"] for r in C.load(content_class="*")} - pool
        orphans = [i for i in cap if i not in known and i not in scoped]
        # Two legitimate cases, and they are different. A REMOVED record is history
        # and must never be counted as supply. A SCOPED record is live but admitted
        # only to a beat that declares its content class — also not general supply,
        # but for the opposite reason. Anything else is a genuine orphan.
        removed = C._removed()
        for i in orphans:
            self.assertIn(i, removed, f"{i} is an unexpected orphan capability record")


class NoDuplicateDefinitions(unittest.TestCase):
    """A module must not define the same name twice at top level. LOG 0069.

    candidates.py carried a verbatim duplicate of PICKS, _picked_ids, CAPABILITY and
    _capability. Both copies were identical so nothing misbehaved — which is exactly
    why it survived: the second silently wins and the file still works. It was found
    only because an `assert s.count(old) == 1` in an edit script failed, and the
    assert was there by habit rather than design.
    """

    def test_no_module_defines_a_name_twice(self):
        import ast
        for d in ("pipeline", "match-trial"):
            for path in sorted((ROOT / d).glob("*.py")):
                if path.name.startswith("_"): continue
                tree = ast.parse(path.read_text())
                names = []
                for node in tree.body:
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        names.append(node.name)
                    elif isinstance(node, ast.Assign):
                        names += [t.id for t in node.targets
                                  if isinstance(t, ast.Name) and t.id.isupper()]
                dupes = [n for n, c in collections.Counter(names).items() if c > 1]
                self.assertEqual(dupes, [], f"{path.name} defines twice: {dupes}")


class UserCapabilityCorrections(unittest.TestCase):
    """A user correction survives a re-ingest and never masquerades as a measurement.

    LOG 0069. The user watched two-floors and said the overlap is in the clip at the
    end. The final frame confirms it. The pass had no word for it at the time.
    """

    def corrections(self):
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no sidecar")
        c = json.load(open(f)).get("capabilityCorrections") or {}
        if not c: self.skipTest("no corrections")
        return c

    def test_a_correction_is_applied_to_the_capability_record(self):
        cor = self.corrections()
        cap = C._capability()
        for rid, c in cor.items():
            for field, vals in (c.get("add") or {}).items():
                for v in vals:
                    self.assertIn(v, cap[rid][field], f"{rid}: {v} not applied")

    def test_a_correction_lives_outside_capability_json(self):
        """So a re-ingest cannot silently drop it — the whole point."""
        raw = json.load(open(ROOT / "grammar" / "capability.json"))
        for rid in self.corrections():
            self.assertNotIn("userCorrected", raw.get(rid, {}),
                             f"{rid}: the correction was written INTO capability.json")

    def test_a_correction_never_deletes_a_measurement(self):
        """It records what the user saw; it never deletes what was measured, so the
        two stay distinguishable.

        Was: forbid `set` outright, allowing only `add`. That held while every
        correction was a list field. media_slots 0 -> 93 is an integer and `add`
        cannot express it (LOG 0086), so `set` exists for SCALARS and is refused
        on any collection — which is where deleting a measurement would actually
        happen. `remove` and `replace` stay banned entirely.
        """
        cor = self.corrections()
        for rid, c in cor.items():
            self.assertEqual(set(c) & {"remove", "replace"}, set(),
                             f"{rid}: a correction may only `add` or scalar-`set`")
            for field, val in (c.get("set") or {}).items():
                self.assertNotIsInstance(val, (list, dict),
                                         f"{rid}.set.{field} replaces a collection")
            self.assertTrue(c.get("why"), f"{rid}: no reason recorded")
            self.assertEqual(c.get("source"), "user", rid)
            self.assertTrue(c.get("measuredUnder") or c.get("measuredSha"),
                            f"{rid}: does not say which sha it corrects")

    def test_a_corrected_record_says_so(self):
        cap = C._capability()
        for rid in self.corrections():
            self.assertTrue(cap[rid].get("userCorrected"),
                            f"{rid}: correction applied with no marker")


class UserNamedBindings(unittest.TestCase):
    """A binding the user names directly — the standing exception. LOG 0069."""

    def sl(self):
        sys.path.insert(0, str(ROOT / "pipeline"))
        import shotlist
        return shotlist

    POOL = {"a": {"id": "a", "description": "x"}, "b": {"id": "b", "description": "y"}}

    def test_it_admits_and_never_removes(self):
        S = self.sl()
        rows, note = S.admit_user_named({"id": "28", "_passage": "28"},
                                        [{"id": "a"}], self.POOL)
        # no userBindings entry for 28-28 in a synthetic pool -> unchanged
        self.assertEqual([r["id"] for r in rows], ["a"])

    def test_the_live_binding_reaches_beat_28(self):
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        if not f.exists(): self.skipTest("not built")
        x = [b for b in json.load(open(f))
             if f"{b['passage']}-{b['beat']}" == "28-28"][0]
        ids = {o["id"] for o in x["options"]}
        self.assertIn("two-floors", ids, "the scene built for beat 28 is not in it")
        self.assertFalse(x.get("needsEncoding"),
                         "28 still reports an encoding gap it now has supply for")

    def test_an_admission_is_recorded_as_the_user_s(self):
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        if not f.exists(): self.skipTest("not built")
        for b in json.load(open(f)):
            for o in b["options"]:
                if o.get("verdict") == "user-named":
                    self.assertIn("user", (o.get("mechanism") or "") + str(o))

    def test_it_never_writes_into_bindings_json(self):
        """bindings.json is the judgment prompt's output. A user admission lives in
        the sidecar and is applied at slate time, so the grammar stays traceable to
        the run that produced it."""
        f = ROOT / "grammar" / "local-templates.json"
        if not f.exists(): self.skipTest("no sidecar")
        ub = json.load(open(f)).get("userBindings") or {}
        if not ub: self.skipTest("none named")
        g = json.load(open(ROOT / "grammar" / "bindings.json"))
        sh = ROOT / "pipeline" / "shotlist.capacity.json"
        if not sh.exists(): self.skipTest("not built")
        shots = {f"{x['passage']}-{x['beat']}": x for x in json.load(open(sh))}
        # PER JOB, not globally. truth-cohort-attrition is legitimately bound to four
        # other jobs; what must never happen is the ADMISSION being written into the
        # job it is admitted for, because that job's bindings belong to the prompt.
        for beat, spec in ub.items():
            job = shots[beat]["job"]
            bound = {r["id"] for r in (g.get(job) or [])}
            for i in spec.get("admit") or []:
                self.assertNotIn(i, bound,
                                 f"{beat}: {i} was written into the grammar for {job}")


class PartialBindStaysPartial(unittest.TestCase):
    """`--only` must not rewrite the whole grammar. LOG 0071.

    It judged 19 records and rebuilt bindings.json from all 440 judgments in
    bind-raw.json, silently undoing salvage_bindings.py: assert_without_data
    42 -> 257 (59% of the corpus, the exact flood the salvage reverts),
    narrate_an_event 132 -> 218, parallel_instances 50 -> 23, inversion 11 -> 2.
    289 bindings changed on a run that judged nineteen records.
    """

    def test_only_keeps_the_existing_grammar_as_its_base(self):
        src = (ROOT / "pipeline" / "bind.py").read_text()
        self.assertIn("A PARTIAL RUN MUST STAY PARTIAL", src)
        self.assertIn("base = json.load(open(OUT)) if (only and OUT.exists())", src)

    def test_no_job_is_flooded_in_the_live_grammar(self):
        """The invariant salvage_bindings.py enforces, asserted on the result.

        A job bound to more than 40% of the corpus is not discriminating — it will
        return most of the library for any beat with that job.
        """
        g = json.load(open(ROOT / "grammar" / "bindings.json"))
        try:
            corpus = len(C.load())
        except (PermissionError, FileNotFoundError) as e:
            self.skipTest(f"pool unreadable ({type(e).__name__})")
        flooded = {j: len(v) for j, v in g.items() if len(v) * 100 / corpus > 40}
        self.assertEqual(flooded, {}, f"job(s) bound to >40% of the corpus: {flooded}")

    def test_every_binding_still_carries_provenance(self):
        g = json.load(open(ROOT / "grammar" / "bindings.json"))
        for job, rows in g.items():
            for r in rows:
                p = r.get("provenance") or {}
                self.assertTrue(p.get("source"), f"{job}/{r['id']}: no source")
                if p.get("source") == "pipeline":
                    self.assertTrue(p.get("promptSha"), f"{job}/{r['id']}: no sha")
                    self.assertTrue(p.get("runId"), f"{job}/{r['id']}: no runId")


class ReviewUIPassIsolation(unittest.TestCase):
    """A review UI reads and writes ONE collection, named once. LOG 0072.

    On 2026-09-22 the read was pointed at picks_pass2 and the write was missed: it
    used db.doc("picks/"+k), a PATH rather than collection(), so a grep for
    collection( did not find it. The UI read an empty collection and wrote a whole
    40-beat pass into the previous one. Nothing was lost — picks.json and the
    immutable pass file are the record — but the isolation I had claimed was absent.
    """

    UIS = sorted(p for p in (ROOT / "pipeline").glob("*/index.html")
                 if not p.parent.name.startswith("_"))

    @staticmethod
    def code(src):
        """Strip // comment lines. A comment EXPLAINING the old pattern is not the
        old pattern — the first version of this test failed on its own docstring."""
        return "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("//"))

    def test_a_ui_writes_to_every_collection_it_reads(self):
        """The defect: the pass-2 UI read `picks_pass2` and wrote `picks`.

        Was: cap a UI at ONE collection name. That proxied for the real rule and
        broke as soon as a UI legitimately kept three kinds of record —
        media_picks, media_notes, media_corrections — each with one consistent
        name. The invariant is not "one collection", it is READ AND WRITE THE
        SAME ONES. A name that appears on only one side is the original defect.
        """
        for ui in self.UIS:
            src = self.code(ui.read_text())
            names = (re.findall(r'collection\("([^"/]+)"\)', src)
                     + re.findall(r'doc\("([^"/]+)/', src))
            if not names: continue
            once = sorted({n for n in names if names.count(n) == 1})
            self.assertEqual(once, [],
                f"{ui.parent.name}: {once} appears exactly once — a collection is "
                f"read in one place and written in another, so a name that shows "
                f"up once is one half of a pair whose other half has drifted")

    def test_ui2_writes_where_it_reads(self):
        src = self.code((ROOT / "pipeline" / "ui2" / "index.html").read_text())
        self.assertIn('const PASS =', src, "the collection is not a single constant")
        self.assertNotIn('doc("picks/', src, "still writing to the pass-1 collection")


class NamedBeatsPicked(unittest.TestCase):
    """A record named FOR THIS BEAT outranks a family picked somewhere else.

    LOG 0073. `_picked_ids()` is global — every record the user has ever selected
    on any beat. It was 61 after pass 1 and 103 after pass 2, so "this family
    contains a picked record" is becoming true of most families and losing its
    power to discriminate. On beat 24 it outranked a timeline the user had
    explicitly declared for that beat, after they wrote "they absolutely should've
    been in here".
    """

    def test_a_named_record_reaches_its_beat(self):
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        if not f.exists(): self.skipTest("not built")
        shots = {f"{x['passage']}-{x['beat']}": x for x in json.load(open(f))}
        flags = json.load(open(ROOT / "grammar" / "beat-flags.json"))["beats"]
        ub = (json.load(open(ROOT / "grammar" / "local-templates.json"))
              .get("userBindings") or {})
        expect = {k for k, v in flags.items() if v.get("contentClass")} | set(ub)
        for k in sorted(expect):
            x = shots.get(k)
            if x is None: continue
            named = [o for o in x["options"]
                     if o.get("verdict") in ("user-named", "scoped")]
            self.assertTrue(named,
                f"{k} declares a content class or a named binding and shows neither")

    def test_named_outranks_the_global_pick_signal(self):
        named = rec("named--scene-001")
        named["provenance"] = {"verdict": "scoped"}
        other = rec("other--scene-001")
        slate, _, _ = C.diversify([other, named], limit=1, corpus_size=425)
        self.assertEqual([r["id"] for r in slate], ["named--scene-001"])

    def test_the_global_pick_signal_still_orders_unnamed_families(self):
        # named is a tiebreak ABOVE picked, not a replacement for it
        src = (ROOT / "match-trial" / "candidates.py").read_text()
        self.assertIn('not any(r["id"] in picked for r in fams[f])', src)


class Timing(unittest.TestCase):
    """Quote-to-timing placement is known-imperfect; it must say so, not hide it."""

    SHOTS = json.load(open(ROOT / "pipeline" / "shotlist.capacity.json"))

    def test_every_shot_carries_a_timing_flags_field(self):
        for s in self.SHOTS:
            self.assertIn("timingFlags", s, s["beat"])

    def test_an_overlapping_span_is_flagged_on_both_beats(self):
        placed = sorted([s for s in self.SHOTS if s.get("start") is not None],
                        key=lambda s: s["start"])
        for a, b in zip(placed, placed[1:]):
            if a["end"] > b["start"] + 0.01:
                self.assertTrue(a["timingFlags"], f"{a['beat']} overlaps but is unflagged")
                self.assertTrue(b["timingFlags"], f"{b['beat']} overlapped but unflagged")

    def test_a_wildly_long_span_is_flagged(self):
        d = sorted(s["duration"] for s in self.SHOTS if s.get("duration"))
        med = d[len(d) // 2]
        for s in self.SHOTS:
            if s.get("duration") and s["duration"] > max(25.0, med * 3):
                self.assertTrue(s["timingFlags"], f"{s['beat']} is {s['duration']}s, unflagged")


class Exceptions(unittest.TestCase):
    """A rule exception must name a family, not match a substring."""

    def test_an_exception_matches_a_family_the_way_a_person_names_it(self):
        # "intro-slideshow" must exempt "intro-slideshow-full-720p". Requiring the full
        # id is rigidity for its own sake — LOG 0022.
        import preflight
        real = preflight.THIN.get("exceptions")
        try:
            preflight.THIN["exceptions"] = ["intro-slideshow"]
            self.assertTrue(preflight.exempt({"id": "intro-slideshow-full-720p--scene-001"}))
            self.assertFalse(preflight.exempt({"id": "photo-slideshow--review-001"}))
        finally:
            preflight.THIN["exceptions"] = real

    def test_an_exception_matching_nothing_fails_preflight(self):
        # defect (LOG 0018): tightening the match silently disabled the user's
        # exception; thin descriptions went 3 -> 11 with nothing reporting why
        import preflight
        pool = pool_or_skip(self)
        real = preflight.THIN.get("exceptions")
        try:
            preflight.THIN["exceptions"] = ["no-such-family"]
            self.assertEqual(preflight.check_exceptions(pool), ["no-such-family"])
            preflight.THIN["exceptions"] = real
            self.assertEqual(preflight.check_exceptions(pool), [],
                             "the configured exceptions do not name real families")
        finally:
            preflight.THIN["exceptions"] = real


class CapabilityIngest(unittest.TestCase):
    """The video pass lands 216+ records at once. Nothing merges unless all validate."""

    @classmethod
    def setUpClass(cls):
        import ingest_capability
        cls.M = ingest_capability
        try:    cls.ids = {r["id"] for r in C.load()}
        except (PermissionError, FileNotFoundError): cls.ids = None
        cls.good = {"id": sorted(cls.ids)[0] if cls.ids else "x", "slots_at_once": 4, "slots_total": 4,
                    "growable": False, "structure": "grid", "staging": "all_at_once",
                    "carries": ["identity"], "readable": ["exact_value"],
                    "implies": ["none"],
                    "asserts": "Presents four subjects together at equal visual weight.",
                    "text_slots": 8, "media_slots": 4, "unclear": []}

    def setUp(self):
        if self.ids is None:
            self.skipTest("template pool unreadable — needs the scene library")

    def bad(self, **over):
        r = dict(self.good); r.update(over); return self.M.validate(r, self.ids)

    def test_a_well_formed_record_passes(self):
        self.assertEqual(self.M.validate(self.good, self.ids), [])

    def test_an_id_outside_the_pool_is_rejected(self):
        self.assertTrue(self.bad(id="not-a-real-record"))

    def test_a_value_outside_the_vocabulary_is_rejected(self):
        self.assertTrue(self.bad(structure="fancy_grid"))
        self.assertTrue(self.bad(staging="slowly"))
        self.assertTrue(self.bad(carries=["vibes"]))
        self.assertTrue(self.bad(implies=["excellence"]))

    def test_an_empty_list_is_rejected_so_silence_and_nothing_differ(self):
        # a model that omits the field and a model that means "carries nothing" must
        # not look identical; ["none"] is the way to say nothing
        self.assertTrue(self.bad(carries=[]))
        self.assertEqual(self.M.validate(dict(self.good, carries=["none"]), self.ids), [])

    def test_none_cannot_be_mixed_with_real_values(self):
        self.assertTrue(self.bad(carries=["none", "magnitude"]))

    def test_slots_total_below_slots_at_once_is_rejected(self):
        self.assertTrue(self.bad(slots_at_once=5, slots_total=2))

    def test_counts_must_be_whole_and_not_negative(self):
        self.assertTrue(self.bad(slots_at_once="four"))
        self.assertTrue(self.bad(slots_at_once=-1))
        self.assertTrue(self.bad(growable="yes"))

    def test_a_rambling_asserts_is_rejected(self):
        self.assertTrue(self.bad(asserts=" ".join(["word"] * 40)))
        self.assertTrue(self.bad(asserts="   "))

    def test_a_disagreement_with_a_declared_capacity_is_reported_not_resolved(self):
        pool = {r["id"]: r for r in pool_or_skip(self)}
        declared = next(r for r in pool.values() if C.subject_axes(r))
        n = max(C.subject_axes(declared).values())
        same = self.M.conflicts(dict(self.good, id=declared["id"], slots_at_once=n,
                                     slots_total=n), pool)
        self.assertIsNone(same)
        far = self.M.conflicts(dict(self.good, id=declared["id"], slots_at_once=n + 50,
                                    slots_total=n + 50), pool)
        self.assertEqual(far["severity"], "MAJOR")

    def test_slot_counts_become_subject_axes_once_ingested(self):
        self.assertIn("slots_at_once", C.SUBJECT_AXES)
        self.assertIn("slots_total", C.SUBJECT_AXES)
        r = {"id": "x", "axes": {"slots_at_once": 4}}
        self.assertEqual(C.shape([r], 4)[0][1], "exact")
        self.assertEqual(C.shape([r], 40)[0][1], "outside")

    def test_measured_slots_supersede_focal_asset_count(self):
        # focalAssetCount counts what is EMPHASISED; slots_at_once counts what is
        # PRESENT. Keeping both would make one record feasible for a 1-entity beat and
        # a 4-entity beat at once — LOG 0013 in a new form.
        both = {"id": "x", "kind": "after_effects",
                "axes": {"focalAssetCount": 1, "slots_at_once": 4, "slots_total": 4}}
        self.assertEqual(C.shape([both], 1)[0][1], "exact",
                         "fixture check: keeping both really does double-match")
        superseded = {"id": "x", "kind": "after_effects",
                      "axes": {"slots_at_once": 4, "slots_total": 4}}
        self.assertEqual(C.shape([superseded], 1)[0][1], "outside")
        self.assertEqual(C.shape([superseded], 4)[0][1], "exact")

    def test_the_pool_loads_with_or_without_the_sidecar(self):
        # the pass may never have run; absence is normal, not an error
        self.assertGreater(len(pool_or_skip(self)), 300)


class Loader(unittest.TestCase):
    """The pool is approved-list.json, and it is read correctly."""

    @classmethod
    def setUpClass(cls):
        try:    cls.pool = C.load()
        except (PermissionError, FileNotFoundError): cls.pool = None

    def setUp(self):
        if self.pool is None:
            self.skipTest("template pool unreadable — needs the scene library")

    def test_pool_is_not_empty_and_ids_are_unique(self):
        self.assertGreater(len(self.pool), 300)
        ids = [r["id"] for r in self.pool]
        self.assertEqual(len(ids), len(set(ids)))

    def test_description_comes_from_the_record_not_the_title(self):
        # defect: the loader read `title`, so the inversion template was judged as
        # "Five horizontal category bars" instead of its real contract. The user
        # called this "enormously load bearing".
        #
        # An unreadable ENRICHMENT file is an environment problem, not a code defect:
        # infographic and cinematic_3d descriptions come from catalog.json, and when
        # that is PermissionError the loader now degrades to the title instead of
        # taking the whole pool down (LOG 0058). Skip in that case, the way
        # pool_or_skip does — "cannot check" and "is broken" must not look the same.
        # The invariant is still enforced the moment the data is actually there.
        missing = next((r["sources"].get("enrichmentMissing") for r in self.pool
                        if r["sources"].get("enrichmentMissing")), None)
        fallback = [r["id"] for r in self.pool if r["sources"]["description"] == "title-fallback"]
        if missing and fallback:
            self.skipTest(f"enrichment unreadable ({'; '.join(missing)}) — "
                          f"{len(fallback)} records degraded to their title")
        self.assertEqual(fallback, [], f"{len(fallback)} records judged on their title")

    def test_a_degraded_record_says_so(self):
        """Degradation must be visible, not silent.

        _optional() lets the pool survive an unreadable enrichment file. The danger
        is that a thin record then looks like a normal one and gets bound on a title.
        Every record carries `sources.enrichmentMissing` naming the file.
        """
        degraded = [r for r in self.pool if r["sources"]["description"] == "title-fallback"]
        for r in degraded:
            if r.get("local"): continue      # local sidecar records have no enrichment
            self.assertTrue(r["sources"].get("enrichmentMissing"),
                            f"{r['id']} fell back to its title and does not say why")

    def test_every_record_has_a_description(self):
        self.assertEqual([r["id"] for r in self.pool if not r["description"]], [])

    def test_ineligible_records_are_excluded(self):
        # defect: selectorEligible:false and catalogStatus reference_only were ignored,
        # putting four unusable records in the pool and seven into the grammar
        # read the list the LOADER reads, not the remote one — approved_path()
        # prefers the local export and the two can differ
        raw = json.load(open(C.approved_path()))["items"]
        # a user override lifts the gate deliberately and is recorded with their
        # words in grammar/eligibility-overrides.json. Everything NOT overridden
        # must still be excluded.
        admitted = set(C.eligibility_overrides())
        banned = set()
        for card in raw:
            if card.get("templateId") in admitted: continue
            if card.get("selectorEligible") is False or \
               str(card.get("catalogStatus") or "").startswith("reference_only"):
                banned.add(card.get("templateId"))
                for sc in (card.get("scenes") or []): banned.add(sc.get("id"))
        self.assertEqual(banned & {r["id"] for r in self.pool}, set())

    def test_scoped_templates_are_held_back_until_their_content_class(self):
        general = {r["id"] for r in C.load()}
        lyrics  = {r["id"] for r in C.load(content_class="lyrics")}
        self.assertTrue(lyrics - general, "scoped templates never admitted")
        self.assertEqual(general - lyrics, set(), "scoping must only add")


class Picks(unittest.TestCase):
    """The user's selections are the only evidence that outranks the pipeline."""

    @classmethod
    def setUpClass(cls):
        f = ROOT / "grammar" / "picks.json"
        cls.data = json.load(open(f)) if f.exists() else None

    def setUp(self):
        if self.data is None: self.skipTest("grammar/picks.json not written yet")

    def test_the_record_says_it_came_from_the_user(self):
        self.assertEqual(self.data["provenance"]["source"], "user")
        self.assertIn("rule", self.data["provenance"])

    def test_every_selected_and_rejected_id_was_actually_shown(self):
        for k, b in self.data["beats"].items():
            shown = set(b["shown"])
            self.assertTrue(set(b["selected"]) <= shown, f"{k} selected something unshown")
            self.assertTrue(set(b["rejected"]) <= shown, f"{k} rejected something unshown")

    def test_selected_and_rejected_never_overlap(self):
        for k, b in self.data["beats"].items():
            self.assertFalse(set(b["selected"]) & set(b["rejected"]), k)

    def test_rejection_is_derived_only_where_the_user_judged(self):
        """A zero-pick beat must not become silent rejections of things the user
        never ruled on — UNLESS a pass recorded them saying it did.

        Was: assert every zero-pick beat has zero rejections. That is the right
        rule for an AMBIGUOUS zero, which is what it was written for. Pass 3's
        zero was not ambiguous: "anything that got passed was a judgement not a
        unintentional skip... everything else was of no value." So the assertion
        is now that a zero-pick rejection must be TRACEABLE to a pass whose
        provenance carries that ruling — never merely present. LOG 0080.
        """
        authorised = set()
        for pf in sorted((ROOT / "grammar" / "passes").glob("pass-*.json")):
            d = json.load(open(pf))
            if d.get("provenance", {}).get("passedIsJudged"):
                authorised |= set(d["beats"])
        for k, b in self.data["beats"].items():
            if b["selected"]:
                continue
            if b["rejected"]:
                self.assertIn(k, authorised,
                              f"{k} has {len(b['rejected'])} derived rejects, no "
                              f"picks, and no pass where the user said passing "
                              f"was a judgement")
            else:
                self.assertTrue(b["noneAcceptable"], k)

    def test_a_judged_beat_accounts_for_every_option_shown(self):
        for k, b in self.data["beats"].items():
            if b["selected"]:
                # `shown` now includes siblings behind the expander, and a rejection is
                # derived only for what was ON SCREEN — never for an unopened sibling.
                # So the sum is <= shown by design, and the real invariants are that
                # it never exceeds it and the two sets never overlap.
                self.assertLessEqual(len(b["selected"]) + len(b["rejected"]),
                                     len(b["shown"]), k)
                self.assertEqual(set(b["rejected"]) & set(b["selected"]), set(), k)

    def test_every_id_is_a_real_pool_record(self):
        # a removed record stays in HISTORY — the user judged it before taking it
        # out of the corpus, and rewriting the past to match the present would
        # destroy the evidence the rejection is based on. LOG 0060.
        # content_class="*" for the same reason ingest_picks needs it (LOG 0079):
        # bare load() hides the 9 scope-restricted templates, and the user picked
        # a scoped timeline scene on 06-06 and 24-24 in pass 3. Validating against
        # the narrow pool calls a real selection a phantom.
        try:
            pool = {r["id"] for r in C.load(content_class="*")} | C._removed()
        except (PermissionError, FileNotFoundError):
            self.skipTest("template pool unreadable")
        for k, b in self.data["beats"].items():
            for i in b["selected"] + b["rejected"]:
                self.assertIn(i, pool, f"{k}: {i}")

    def test_no_selection_was_lost_to_a_removal(self):
        """A removal may orphan a REJECTION. It must never orphan a SELECTION.

        Taking a record out of the corpus is the user's call, but a pick is the
        ground truth this system is measured against. If a lock ever removes
        something the user had chosen, that is a contradiction to surface, not
        absorb. Measured on the 2026-09-21 text lock: 2 shown, 2 rejected, 0
        selected.
        """
        gone = C._removed()
        lost = [(k, i) for k, b in self.data["beats"].items()
                for i in b["selected"] if i in gone]
        self.assertEqual(lost, [], f"a removal orphaned a user selection: {lost}")

    def test_every_beat_carries_both_manual_flags(self):
        for k, b in self.data["beats"].items():
            self.assertIn("rawBroll", b, k)
            self.assertIn("needsTextTemplate", b, k)

    def test_the_text_flag_is_set_where_it_was_recorded(self):
        # detection, not retrieval: the system's job is to say a beat wants a text
        # treatment. Three text templates are unprocessed; this records where they go.
        flagged = {k for k, b in self.data["beats"].items() if b["needsTextTemplate"]}
        self.assertTrue(flagged, "no beat flagged — has beat-flags.json gone stale?")
        for k in flagged:
            self.assertIn(self.data["beats"][k]["job"],
                          ("define_terms", "pose_a_question", "equivalence_restatement"),
                          f"{k} flagged for text but its job is not a text-ish job")

    def test_a_flag_naming_an_unknown_beat_is_reported(self):
        # a typo in beat-flags.json must not silently do nothing — the failure mode
        # this project keeps paying for
        import ingest_capability  # noqa
        import ingest_picks
        f = ROOT / "grammar" / "beat-flags.json"
        real = f.read_text()
        try:
            d = json.loads(real); d["beats"]["99-zz"] = {"needsTextTemplate": True}
            f.write_text(json.dumps(d))
            _, problems = ingest_picks.build(str(ROOT / "picks/capacity/picks_capacity"))
            self.assertTrue(any("99-zz" in p for p in problems), "typo went unreported")
        finally:
            f.write_text(real)

    def test_none_acceptable_beats_are_a_finding_not_a_gap(self):
        none = [k for k, b in self.data["beats"].items() if b["noneAcceptable"]]
        self.assertTrue(none, "no unacceptable beats — has the file gone stale?")
        for k in none:
            self.assertEqual(self.data["beats"][k]["selected"], [])


class DefectLog(unittest.TestCase):
    """no-drifting/LOG.txt must be readable by no-drifting/check.py.

    On 2026-09-21 entries 0041 and 0042 were appended without the 80-char separator
    check.py splits on. Both were absorbed into 0040's block and vanished from
    --index; an entry marked STATUS open did not appear in the open list. The log is
    the mechanism that stops a defect recurring, and it had silently stopped seeing
    its two newest entries. Same failure mode as ever: the non-match said nothing.
    """

    LOG = ROOT / "no-drifting" / "LOG.txt"
    SEP = "=" * 80

    def raw(self):
        if not self.LOG.exists(): self.skipTest("no log")
        return self.LOG.read_text()

    def test_every_entry_header_is_preceded_by_a_separator(self):
        blocks = self.raw().split(self.SEP)
        for b in blocks:
            hdrs = re.findall(r"^\[(\d{4})\]", b, re.M)
            self.assertLessEqual(len(hdrs), 1,
                                 f"entries sharing one block, so check.py sees only "
                                 f"the first: {hdrs}")

    def test_check_py_finds_every_entry_in_the_file(self):
        on_disk = set(re.findall(r"^\[(\d{4})\]", self.raw(), re.M))
        sys.path.insert(0, str(ROOT / "no-drifting"))
        import check
        parsed = {e["n"] for e in check.entries()}
        self.assertEqual(on_disk - parsed, set(),
                         "entries in the file that check.py cannot see")

    def test_entry_numbers_are_unique_and_contiguous(self):
        ns = [int(x) for x in re.findall(r"^\[(\d{4})\]", self.raw(), re.M)]
        self.assertEqual(len(ns), len(set(ns)), "duplicate entry number")
        self.assertEqual(ns, sorted(ns), "entries out of order")


class HardRules(unittest.TestCase):
    """CLAUDE.md's hard rules cannot be silently dropped by a later edit.

    CLAUDE.md has no mechanical consumer — it is read by Claude at the start of a
    session and nowhere else — so an edit that deletes a rule produces no error and
    no diff anyone runs. Each of these was written after a real defect; losing one
    loses the defect with it.
    """

    DOC = ROOT / "CLAUDE.md"
    EXPECTED = [
        "run the consumer",
        "no drifting",
        "working agreement",
        "measured or estimated, say which",
        "the pipeline decides, not Claude",
    ]

    def sections(self):
        if not self.DOC.exists(): self.skipTest("no CLAUDE.md")
        return re.findall(r"^## HARD RULE — (.+)$", self.DOC.read_text(), re.M)

    def test_every_hard_rule_is_present(self):
        self.assertEqual(self.sections(), self.EXPECTED,
                         "a hard rule was dropped, renamed or reordered")

    def test_no_hard_rule_is_an_empty_heading(self):
        src = self.DOC.read_text() if self.DOC.exists() else self.skipTest("no doc")
        for name in self.EXPECTED:
            body = src.split(f"## HARD RULE — {name}", 1)[1].split("\n## ", 1)[0]
            self.assertGreater(len(body.strip()), 200,
                               f"'{name}' is a heading with no rule under it")

    def test_each_hard_rule_says_why_it_exists(self):
        # a rule with no defect behind it is drift, by the no-drifting rule's own
        # standard. Every one of these was written after something went wrong.
        src = self.DOC.read_text() if self.DOC.exists() else self.skipTest("no doc")
        for name in self.EXPECTED:
            body = src.split(f"## HARD RULE — {name}", 1)[1].split("\n## ", 1)[0]
            self.assertRegex(body, r"(Why this exists|Why this rule exists|2026-09-\d\d)",
                             f"'{name}' does not say what it was written after")


class SystemDoc(unittest.TestCase):
    """SYSTEM.md is the guiding document. It went stale within hours of being written
    because nothing checked it, and the handoff told a reviewer to read it first."""

    DOC = ROOT / "SYSTEM.md"

    def test_the_binding_count_matches_reality(self):
        live = sum(len(v) for v in BINDINGS.values())
        txt = self.DOC.read_text()
        m = re.search(r"`grammar/bindings\.json` — (\d+) bindings", txt)
        self.assertIsNotNone(m, "SYSTEM.md no longer states a binding count")
        self.assertEqual(int(m.group(1)), live,
                         f"SYSTEM.md says {m.group(1)} bindings, live is {live}")

    def test_it_does_not_describe_a_filter_that_now_ranks(self):
        # capacity stopped excluding on 2026-09-21; the doc said otherwise for hours
        txt = self.DOC.read_text()
        self.assertNotIn("drops records outside", txt)

    def test_every_stage_declares_a_status(self):
        stages = re.findall(r"^## \d+\. .*$", self.DOC.read_text(), re.M)
        self.assertGreaterEqual(len(stages), 10)
        for st in stages:
            self.assertTrue(any(k in st for k in ("BUILT", "PARTIAL", "ASSUMED", "MISSING")),
                            f"stage with no status: {st[:60]}")


class TemplateFacts(unittest.TestCase):
    """No paid run may depend on a claim nobody has ruled on."""

    REG = ROOT / "grammar" / "TEMPLATE-FACTS.md"

    def test_the_register_exists(self):
        self.assertTrue(self.REG.exists(), "grammar/TEMPLATE-FACTS.md is missing")

    def test_every_claim_carries_a_status(self):
        rows = [l for l in self.REG.read_text().splitlines()
                if l.startswith("| ") and re.match(r"^\| \d+\.\d+ ", l)]
        self.assertGreater(len(rows), 10, "register looks empty")
        for r in rows:
            self.assertTrue(any(s in r for s in
                            ("VERIFIED", "ASSERTED", "DISPUTED", "UNKNOWN", "FALSE")),
                            f"claim with no status: {r[:70]}")

    def test_no_claim_is_left_unsettled_without_being_logged(self):
        # DISPUTED or UNKNOWN blocks any paid run that depends on it, so their
        # presence must be deliberate and visible, never a leftover
        rows = [l for l in self.REG.read_text().splitlines()
                if re.match(r"^\| \d+\.\d+ ", l)]
        open_claims = [r.split("|")[1].strip() for r in rows
                       if "DISPUTED" in r or "UNKNOWN" in r]
        if open_claims:
            self.assertIn("STATUS      open", (ROOT / "no-drifting" / "LOG.txt").read_text(),
                          f"unsettled claims {open_claims} with nothing open in the log")

    def test_a_disputed_claim_is_not_asserted_as_fact_in_a_live_prompt(self):
        # 1.5 "templates are pre-rendered" contradicts 3.1. It may appear in a prompt
        # only if that prompt is retired or the phrasing is quoted as disputed.
        live = {"PROMPT-bind.md", "PROMPT-beats.md", "PROMPT-describe-clip.md"}
        for p in (ROOT / "prompts").glob("*.md"):
            if p.name not in live: continue
            txt = p.read_text().lower()
            self.assertNotIn("templates are pre-rendered", txt,
                             f"{p.name} asserts disputed claim 1.5")


class Salvage(unittest.TestCase):
    """Merging two binding runs is a rule, never a taste."""

    def setUp(self):
        import salvage_bindings
        self.M = salvage_bindings

    def job(self, n, tag="x"):
        return [{"id": f"{tag}{i}", "provenance": {"source": "pipeline"}} for i in range(n)]

    def test_a_job_the_new_run_floods_reverts(self):
        out, _ = self.M.merge({"j": self.job(40, "old")}, {"j": self.job(300, "new")}, 421)
        self.assertEqual(out["j"][0]["id"], "old0")

    def test_a_job_the_new_run_collapses_reverts(self):
        out, _ = self.M.merge({"j": self.job(11, "old")}, {"j": self.job(1, "new")}, 421)
        self.assertEqual(out["j"][0]["id"], "old0")

    def test_a_small_drop_is_not_a_collapse(self):
        out, _ = self.M.merge({"j": self.job(34, "old")}, {"j": self.job(24, "new")}, 421)
        self.assertEqual(out["j"][0]["id"], "new0")

    def test_a_job_that_merely_grows_keeps_the_new_run(self):
        out, _ = self.M.merge({"j": self.job(7, "old")}, {"j": self.job(25, "new")}, 421)
        self.assertEqual(out["j"][0]["id"], "new0")

    def test_a_job_already_flooded_before_is_not_reverted_for_it(self):
        # reverting to an equally flooded run fixes nothing
        out, _ = self.M.merge({"j": self.job(300, "old")}, {"j": self.job(310, "new")}, 421)
        self.assertEqual(out["j"][0]["id"], "new0")

    def test_the_live_grammar_has_no_flooded_job(self):
        pool = pool_or_skip(self)
        for j, rows in BINDINGS.items():
            pct = len(rows) * 100 / len(pool)
            self.assertLessEqual(pct, C.FLOOD_PCT, f"{j} is {pct:.0f}% of the corpus")


class Metrics(unittest.TestCase):
    """A metric that cannot explain its own movement is worse than no metric."""

    @classmethod
    def setUpClass(cls):
        f = ROOT / "grammar" / "metrics.json"
        cls.series = json.load(open(f)) if f.exists() else []

    def test_every_entry_records_the_system_it_measured(self):
        self.assertTrue(self.series, "metrics.json is empty")
        for e in self.series:
            for k in ("date", "kind", "label", "state", "metrics"):
                self.assertIn(k, e)
            for k in ("bindPromptSha", "bindings", "capabilityRecords"):
                self.assertIn(k, e["state"], f"{e['label']}: state missing {k}")

    def test_only_a_review_entry_claims_an_acceptance_rate(self):
        # a slate entry describes what is OFFERED; nobody judged it, so it must not
        # report a rate as though someone had
        for e in self.series:
            if e["kind"] == "slate":
                self.assertNotIn("acceptancePct", e["metrics"], e["label"])
            else:
                self.assertIn("acceptancePct", e["metrics"], e["label"])

    def test_a_review_entry_measures_the_slate_that_was_judged(self):
        # mixing the judged slate with the current one produces an unreadable number:
        # slots offered today against a rate earned on a different slate. LOG 0035.
        for e in self.series:
            if e["kind"] != "review": continue
            m = e["metrics"]
            self.assertEqual(m["accepted"] + m["rejected"] <= m["optionSlots"], True,
                             f"{e['label']}: judged more options than the slate held")

    def test_the_recorded_pass_is_immutable(self):
        d = ROOT / "grammar" / "passes"
        if not d.exists(): self.skipTest("no pass recorded yet")
        passes = sorted(d.glob("pass-*.json"))
        self.assertTrue(passes, "no immutable pass record written")
        live = json.load(open(ROOT / "grammar" / "picks.json"))["beats"]
        # picks.json is the MERGE across every pass, so it no longer equals the last
        # one — it must CONTAIN each. A pass file is the immutable record of what a
        # human was shown and chose; picks.json is the accumulated current state.
        # Rejections and selections do not expire, so the merge only ever grows.
        for pf in passes:
            old = json.load(open(pf))["beats"]
            for k, v in old.items():
                self.assertLessEqual(set(v["shown"]), set(live[k]["shown"]),
                                     f"{pf.name} {k}: picks.json lost options that "
                                     f"pass recorded as shown")
                self.assertLessEqual(set(v["selected"]), set(live[k]["selected"]),
                                     f"{pf.name} {k}: picks.json lost a selection")

    def test_a_pass_file_is_never_rewritten(self):
        """Two passes exist and each must still describe its own slate.

        pass-2026-09-21 was judged on ui3-capacity, pass-2026-09-22 on ui2 with 219
        options. If a later ingest ever rewrote the earlier file, the two would have
        the same `shown` and every metric derived from pass 1 would silently move.
        """
        d = ROOT / "grammar" / "passes"
        passes = sorted(d.glob("pass-*.json"))
        if len(passes) < 2: self.skipTest("only one pass")
        a = json.load(open(passes[0]))["beats"]
        b = json.load(open(passes[-1]))["beats"]
        same = [k for k in a if k in b and a[k]["shown"] == b[k]["shown"]]
        self.assertLess(len(same), len(a),
                        "every beat has identical `shown` in both passes — one file "
                        "was probably rewritten by the other's ingest")


class Provenance(unittest.TestCase):
    """The HARD RULE, enforced rather than written down."""

    REQUIRED = ("promptSha", "model", "runId", "verdict", "mechanism", "evidence")

    def test_every_binding_is_traceable(self):
        bad = []
        for job, rows in BINDINGS.items():
            for r in rows:
                p = r.get("provenance") or {}
                if p.get("source") == "user": continue
                if [f for f in self.REQUIRED if not p.get(f)]: bad.append((job, r["id"]))
        self.assertEqual(bad[:5], [], f"{len(bad)} bindings without provenance")

    def test_every_bound_id_exists_in_the_pool(self):
        pool = {r["id"] for r in pool_or_skip(self)} | {r["id"] for r in C.load(content_class="lyrics")}
        missing = sorted({r["id"] for rows in BINDINGS.values() for r in rows} - pool)
        self.assertEqual(missing, [], f"bound but not in the pool: {missing[:5]}")


class Runner(unittest.TestCase):
    """Transport defects that cost real money."""

    def test_max_tokens_default_covers_a_full_batch(self):
        # defect: max_tokens=8000 against batches needing ~18,200 — every batch
        # would have truncated, silently, mid-JSON
        import inspect, run
        default = inspect.signature(run.ask).parameters["max_tokens"].default
        self.assertGreaterEqual(default, 32000)

    def test_truncation_is_detected_not_swallowed(self):
        import run
        src = inspect_source(run.ask)
        self.assertIn("max_tokens", src)
        self.assertIn("stop_reason", src)
        self.assertIn("raise", src)


class Imports(unittest.TestCase):
    """No module does work when imported."""

    def test_runners_are_guarded(self):
        # defect: bind.py called main() at import; a measurement script imported it
        # and started an unauthorised paid run
        runners = sorted(p for p in (ROOT / "pipeline").glob("*.py")
                         if not p.name.startswith("_"))
        self.assertTrue(runners, "no runners found — has the glob gone stale?")
        for path in runners:
            name, src = path.name, path.read_text()
            if "def main(" not in src and "__main__" not in src:
                continue                      # covered by the AST test below
            guard = re.search(r'^if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', src, re.M)
            self.assertIsNotNone(guard, f"{name} has no __main__ guard")
            body = src[:guard.start()]
            self.assertIsNone(re.search(r"^\s*(main|run)\(\)", body, re.M),
                              f"{name} calls main() at import")

    def test_no_module_does_work_at_top_level(self):
        """The hole the guard test left open.

        segment_reel.py had NO main() and NO __main__, so the check above hit its
        `continue` and exempted it — while the entire script was top-level code, which
        is the worst case, not the safe one. Importing it in a test re-cut 34 clips.
        Same defect class as rerun.py (LOG 0021), through the exemption rather than
        past the guard.
        """
        import ast
        OK = (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef,
              ast.ClassDef, ast.Assign, ast.AnnAssign, ast.If, ast.Try, ast.Expr)
        for path in sorted((ROOT / "pipeline").glob("*.py")):
            if path.name.startswith("_"): continue
            tree = ast.parse(path.read_text())
            for node in tree.body:
                if isinstance(node, ast.Expr):
                    # a docstring is fine, and so is sys.path setup — every runner
                    # here needs match-trial on the path before it can import
                    # candidates. Any OTHER bare call is work.
                    if isinstance(node.value, ast.Constant): continue
                    src = ast.unparse(node.value)
                    self.assertTrue(src.startswith(("sys.path.", "warnings.")),
                        f"{path.name}:{node.lineno} calls {src[:60]} at import")
                    continue
                self.assertIsInstance(node, OK,
                    f"{path.name}:{node.lineno} runs {type(node).__name__} at import")


class ReviewUIs(unittest.TestCase):
    """The video rule in CLAUDE.md, enforced rather than written down."""

    # pipeline/_retired/* is superseded work, kept for reference and not held to the rules
    UIS = sorted(p for p in (ROOT / "pipeline").glob("*/index.html")
                 if not p.parent.name.startswith("_"))

    def test_there_are_review_uis_to_check(self):
        self.assertTrue(self.UIS, "no review UI found — has the glob gone stale?")

    def test_no_ui_ships_a_forbidden_video_control(self):
        # rule (2026-09-20): one small play button, nothing else. `controls` gives the
        # viewer volume, scrubber, fullscreen and download; `loop` and `autoplay` take
        # the decision away from the reviewer.
        for ui in self.UIS:
            src = ui.read_text()
            for bad in (" controls", "loop", "autoplay"):
                if bad in src:
                    self.fail(f"{ui.parent.name}/index.html uses {bad.strip()!r} on its video")

    def test_any_ui_with_video_has_a_play_button(self):
        for ui in self.UIS:
            src = ui.read_text()
            if "<video" not in src: continue
            # matcher was double-quote only and failed lt-pick, which builds its
            # markup in a JS template using single quotes. The rule is about the
            # button existing, not about how the attribute is quoted.
            if not re.search(r'class=["\']play["\']', src):
                self.fail(f"{ui.parent.name}/index.html has video but no play button")

    def test_every_video_element_declares_a_poster(self):
        # rule (2026-09-20): a <video> with no poster is a black rectangle until played,
        # so a grid of them cannot be skimmed
        for ui in self.UIS:
            for tag in re.findall(r"<video\b[^>]*>", ui.read_text()):
                if "poster=" not in tag:
                    self.fail(f"{ui.parent.name}/index.html has a <video> with no poster")

    def test_built_review_data_gives_every_clip_a_poster(self):
        for name, ck, pk in (("clusters-ui", "clips", "posters"),
                             ("ui2", "hasClip", "thumbs")):
            f = ROOT / "pipeline" / name / "data.json"
            if not f.exists(): continue
            d = json.load(open(f))
            clipped = [k for k, v in d[ck].items() if v]
            missing = [k for k in clipped if not d[pk].get(k)]
            self.assertEqual(missing[:5], [], f"{name}: {len(missing)} clips with no poster")

    def test_a_condition_is_shown_as_text_not_a_badge(self):
        # 208 of 211 conditions are FILL INSTRUCTIONS — how to use a template, not
        # whether you may. The reviewer saw a badge reading "has condition" and never
        # the sentence, on 130 of 277 options. LOG 0040.
        live = ROOT / "pipeline" / "ui2" / "index.html"
        if not live.exists(): self.skipTest("ui2 absent")
        txt = live.read_text()
        self.assertNotIn('>has condition<', txt, "condition still rendered as a badge")
        self.assertIn("o.condition?", txt, "condition text is not rendered at all")

    def test_the_frozen_pass_slate_is_never_rebuilt(self):
        # ingest_picks reads ui3-capacity/data.json as the record of what was shown
        src = (ROOT / "pipeline" / "build_review.py").read_text()
        self.assertNotIn('"ui3-capacity" if', src,
                         "build_review can still overwrite the frozen pass slate")

    def test_every_ui_runs_in_strict_mode(self):
        # the frozen-db-doc bug: a silent failed write cost twelve versions
        for ui in self.UIS:
            if '"use strict"' not in ui.read_text():
                self.fail(f"{ui.parent.name}/index.html is not in strict mode")


def inspect_source(fn):
    import inspect
    return inspect.getsource(fn)


class ProfileCorrections(unittest.TestCase):
    """The prose a card ships with can be WRONG, and PROMPT-bind reads that prose.

    kendrick-red-stage-clean shipped asserting, in ten separate fields, that no
    quantity may appear in the frame. The user ruled on 2026-09-22: "remove the
    kendrick avoid list. its wrong. numbers are ok." The shipped demo prints no
    numbers; that is the SAMPLE, not the mechanic, and the standing rule is judge
    the mechanic. Until this hook existed there was no way to correct a card's
    prose: capabilityCorrections fixes a MEASURED record, clipOverrides a path,
    capacityOverrides an axis. None of them reach `avoid`, `description` or
    `encoding` — the three fields the binding prompt actually reads.

    approved-list.json is a generated export and is never edited by hand, so the
    correction lives in the sidecar with the user's words, like every other one.
    """

    def test_correction_clears_the_avoid_list(self):
        pool = {r["id"]: r for r in C.load(content_class="*")}
        r = pool["kendrick-red-stage-clean"]
        self.assertEqual(r["avoid"], [],
                         "user removed this avoid list outright; it must load empty")

    def test_no_field_the_prompt_reads_still_forbids_numbers(self):
        # The avoid list was only one of ten places the claim was written. A fix
        # that clears `avoid` and leaves `encoding` saying "no numbers anywhere in
        # the frame" changes nothing, because PROMPT-bind judges the DESCRIPTION.
        pool = {r["id"]: r for r in C.load(content_class="*")}
        r = pool["kendrick-red-stage-clean"]
        banned = ("no numbers", "no quantity", "encodes no data", "displays no data",
                  "not measurements", "nothing in this scene encodes a quantity")
        # Check the WHOLE block the prompt is handed, not a field list written by
        # hand. The first version of this test named description/encoding/useWhen
        # and passed while CAVEATS still read "THIS LAYOUT DISPLAYS NO DATA" —
        # the same defect one field over. Rendering the real block cannot go stale
        # when bind.block() grows a field.
        sys.path.insert(0, str(ROOT / "pipeline"))
        import bind
        text = bind.block(r).lower()
        for b in banned:
            self.assertNotIn(b, text,
                             f"the block PROMPT-bind receives still carries the "
                             f"withdrawn claim: {b!r}")

    def test_a_correction_naming_an_unknown_record_raises(self):
        # Recurring failure mode: a non-match said nothing. A correction whose id
        # is misspelled or whose record was later removed must fail loudly, not
        # sit in the file doing nothing.
        with self.assertRaises(KeyError):
            C.apply_profile_corrections(
                [{"id": "real-one", "avoid": ["x"]}],
                {"not-in-the-pool": {"avoid": []}})

    def test_correction_may_only_touch_known_fields(self):
        with self.assertRaises(ValueError):
            C.apply_profile_corrections(
                [{"id": "real-one", "avoid": ["x"]}],
                {"real-one": {"slotsAtOnce": 4}})


class NotesReportObservationsNotCauses(unittest.TestCase):
    """User ruling 2026-09-22: "we are replicating taste and in the early stages,
    come stuff will not have an answer just yet."

    Both short-slate notes asserted a CAUSE they never established. The
    observations under them were true; the inferences were false, and the
    inferences are what made them actionable in the wrong direction — both read
    as "go buy more templates."

      flood note   observed  2 shown, 7 rejected here, 8 families BOUND
                   asserted  "the library has only 2 families for this job"
      needsEncoding observed no option in THIS SLATE carries aggregate
                   asserted  "NOTHING HERE HAS" — corpus-level, and false:
                             48_playoff_path_summary carries it and was shown
                             on all five one_vs_aggregate beats and rejected.

    This is the measured-or-estimated rule applied to explanations. LOG 0077.
    """

    @classmethod
    def setUpClass(cls):
        f = ROOT / "pipeline" / "shotlist.capacity.json"
        cls.shots = ({f"{x['passage']}-{x['beat']}": x for x in json.load(open(f))}
                     if f.exists() else {})
        cls.B = json.load(open(ROOT / "grammar" / "bindings.json"))

    def test_no_note_blames_the_library_for_a_rejection_shortfall(self):
        # LOG 0040 fixed this once by checking len(fams) < limit. It recurred
        # because `fams` is counted AFTER drop_prior_rejections: on 04-04 the note
        # said 2 families when the job is bound across 8.
        if not self.shots: self.skipTest("shotlist not built")
        import candidates as C
        pool = {r["id"]: r for r in C.load(content_class="*")}
        bad = []
        for k, x in self.shots.items():
            note = x.get("floodNote") or ""
            if "the library has only" not in note: continue
            fams = {pool[r["id"]]["template"]
                    for r in self.B.get(x.get("job"), []) if r["id"] in pool}
            m = re.search(r"the library has only (\d+) famil", note)
            if m and int(m.group(1)) < len(fams):
                bad.append(f"{k}: note claims {m.group(1)} families, {len(fams)} bound")
        self.assertEqual(bad, [], "\n".join(bad))

    def test_needsencoding_never_claims_absence_for_something_the_corpus_carries(self):
        if not self.shots: self.skipTest("shotlist not built")
        import candidates as C
        cap = C._capability()
        owned = set()
        for c in cap.values():
            owned |= set(c.get("carries") or []) | set(c.get("readable") or [])
        bad = []
        for k, x in self.shots.items():
            note = x.get("floodNote") or ""
            if "NOTHING HERE HAS" not in note: continue
            for t in (x.get("requiredEncoding") or []):
                if t in owned:
                    bad.append(f"{k}: note says nothing has {t!r}; the corpus carries it")
        self.assertEqual(bad, [], "\n".join(bad))


class SubsetPassCannotClaimNoneAcceptable(unittest.TestCase):
    """A pass that showed only PART of a beat's slate cannot say "nothing was
    acceptable" — it never showed the rest.

    Pass 3 (ui4-unseen) showed only the 104 cards the user had never seen, with
    their existing pick displayed alongside but not selectable. On beat 20-20 they
    picked nothing and wrote "something like that could've worked but whats here is
    fine" — a beat that IS served. ingest_picks sets noneAcceptable = not sel, and
    noneAcceptable is the one field the merge does NOT union: the new pass wins.
    Ingesting without this flag would mark a served beat unserved, and
    `noneAcceptable` is what the whole "a beat with no selection is a finding"
    rule keys off. LOG 0079.
    """

    def test_subset_flag_exists(self):
        src = (ROOT / "pipeline" / "ingest_picks.py").read_text()
        self.assertIn("--subset", src,
                      "ingest_picks has no way to record a partial-slate pass")

    def test_a_subset_pass_carries_none_acceptable_forward(self):
        import ingest_picks as IP
        prev = {"20-20": {"selected": ["already-good"], "noneAcceptable": False},
                "23-23": {"selected": [], "noneAcceptable": True}}
        fresh = {"20-20": {"selected": [], "noneAcceptable": True},
                 "23-23": {"selected": [], "noneAcceptable": True}}
        out = IP.carry_none_acceptable(fresh, prev, subset=True)
        self.assertFalse(out["20-20"]["noneAcceptable"],
                         "a served beat was marked unserved by a subset pass")
        self.assertTrue(out["23-23"]["noneAcceptable"],
                        "a genuinely unserved beat must stay unserved")

    def test_a_full_pass_is_untouched_by_the_helper(self):
        # The guard must not weaken a normal pass, where zero picks really does
        # mean nothing in the slate was good enough.
        import ingest_picks as IP
        prev = {"x": {"selected": ["a"], "noneAcceptable": False}}
        fresh = {"x": {"selected": [], "noneAcceptable": True}}
        self.assertTrue(IP.carry_none_acceptable(fresh, prev, subset=False)
                        ["x"]["noneAcceptable"])


class IngestAcceptsScopedPicks(unittest.TestCase):
    """The ingest validated selections against C.load() bare, which HIDES the 9
    scope-restricted templates. So a user pick of any scoped template was reported
    "not in the pool" and the whole ingest refused to write.

    Hit on pass 3: the user picked
    archive3-search-bar-business-timeline-...--scene-001 on beats 06-06 and 24-24
    and wrote "DEFINITLY SHOULDVE been shown this". 24-24 is the beat whose pass-2
    note read "the timeline template clips... they absolutely should've been in
    here". The slate admits scoped templates per beat, so the checker has to use
    the same universe the slate was built from. LOG 0079.
    """

    def test_ingest_checks_against_the_scoped_pool(self):
        src = (ROOT / "pipeline" / "ingest_picks.py").read_text()
        self.assertIn('C.load(content_class="*")', src,
                      "ingest validates picks against a pool that hides scoped "
                      "templates; every scoped pick reads as invalid")

    def test_the_two_pools_actually_differ(self):
        # Proves the test above can fail for the right reason: if bare and "*"
        # were the same set, the assertion would be guarding nothing.
        bare = {r["id"] for r in pool_or_skip(self)}
        star = {r["id"] for r in C.load(content_class="*")}
        self.assertTrue(star - bare,
                        "no scoped templates exist — this guard is vacuous")

    def test_beat_flags_outside_a_subset_pass_are_not_problems(self):
        src = (ROOT / "pipeline" / "ingest_picks.py").read_text()
        self.assertIn("SUBSET", src.upper())
        # the manual-flag cross-check must be conditioned, not unconditional
        i = src.index("names unknown beat")
        window = src[max(0, i - 400):i]
        self.assertIn("subset", window.lower(),
                      "the beat-flags cross-check fires on every beat outside a "
                      "subset pass's slate, which is every flag by design")


class MergeKeepsBeatsOutsideThePass(unittest.TestCase):
    """The merge dropped every beat the current pass did not judge.

        merged = data                      # only this pass's beats
        for k, v in merged["beats"].items():
            old_b = prev.get(k)
            if not old_b: continue
            ...union...

    Beats in `prev` and not in `data` are never re-added, so picks.json becomes
    whatever the latest pass covered. Passes 1 and 2 each judged all 40 beats, so
    it never fired. Pass 3 judged 8, and the write took picks.json from
    40 beats / 103 selected / 327 rejected to 8 / 21 / 59 — a real loss, caught
    only because the run prints its totals and a backup existed. LOG 0079.

    picks.json is the CURRENT STATE merged across every pass. A beat nobody looked
    at this time keeps exactly what it had.
    """

    def test_a_pass_covering_one_beat_keeps_the_others(self):
        import ingest_picks as IP
        prev = {"01-01": {"selected": ["a"], "rejected": ["b"], "shown": ["a", "b"],
                          "note": "keep me", "noneAcceptable": False},
                "02-02": {"selected": ["c"], "rejected": [], "shown": ["c"],
                          "note": None, "noneAcceptable": False}}
        fresh = {"02-02": {"selected": ["d"], "rejected": ["e"], "shown": ["d", "e"],
                           "note": "new", "noneAcceptable": False}}
        out = IP.merge_beats(fresh, prev)
        self.assertIn("01-01", out, "a beat outside the pass was dropped")
        self.assertEqual(out["01-01"]["selected"], ["a"])
        self.assertEqual(out["01-01"]["note"], "keep me")
        # and the judged beat still unions
        self.assertEqual(sorted(out["02-02"]["selected"]), ["c", "d"])

    def test_the_live_file_never_shrinks_below_forty_beats(self):
        f = ROOT / "grammar" / "picks.json"
        if not f.exists(): self.skipTest("no picks.json")
        b = json.load(open(f))["beats"]
        self.assertGreaterEqual(len(b), 40,
                                f"picks.json has {len(b)} beats; the script has 40")


class PassingIsAJudgementWhenTheUserSaysSo(unittest.TestCase):
    """The standing rule is that a beat with ZERO picks must never be read as
    rejecting everything — the user may simply have found the whole slate
    irrelevant, and inventing 10 rejections from silence is not evidence.

    That rule protects against an AMBIGUOUS zero. Pass 3's zero was not ambiguous.
    User, 2026-09-22: "anything that got passed was a judgement not a unintentional
    skip. i selected what i wanted, commented when needed. everything else was of
    no value." Only the user can collapse that ambiguity, so it is a flag they
    authorise per pass, never a default and never inferred. LOG 0080.
    """

    def test_zero_picks_still_derives_nothing_by_default(self):
        import ingest_picks as IP
        self.assertEqual(IP.derive_rejections(shown=["a", "b"], sel=[]), [],
                         "silence was read as rejection without the user saying so")

    def test_the_flag_makes_a_pass_a_rejection(self):
        import ingest_picks as IP
        self.assertEqual(
            IP.derive_rejections(shown=["a", "b"], sel=[], passed_is_judged=True),
            ["a", "b"])

    def test_a_beat_with_picks_is_unaffected_by_the_flag(self):
        import ingest_picks as IP
        for flag in (False, True):
            self.assertEqual(
                IP.derive_rejections(shown=["a", "b", "c"], sel=["b"],
                                     passed_is_judged=flag),
                ["a", "c"])

    def test_the_flag_never_turns_a_served_beat_into_a_gap(self):
        # Rejecting the unseen cards on a beat the user is happy with must not
        # touch noneAcceptable — that is what --subset carries forward. The two
        # flags have to compose.
        import ingest_picks as IP
        prev = {"20-20": {"selected": ["held"], "noneAcceptable": False}}
        fresh = {"20-20": {"selected": [], "rejected": ["x", "y"],
                           "noneAcceptable": True}}
        out = IP.carry_none_acceptable(fresh, prev, subset=True)
        self.assertFalse(out["20-20"]["noneAcceptable"])
        self.assertEqual(out["20-20"]["rejected"], ["x", "y"])


class PassRulingsApplyRetroactively(unittest.TestCase):
    """The user can tell us what an ALREADY-INGESTED pass meant.

    "any pass weve done and i didnt not accept or comment on, should be
    considered a reject" — 2026-09-22. Passes 1 and 2 recorded zero rejections on
    their zero-pick beats, per the standing rule protecting an ambiguous zero.
    The user says their zeros were never ambiguous. A pass file is immutable and
    records what the ingest produced, so the clarification lives in
    grammar/pass-rulings.json with their words. LOG 0081.
    """

    def test_a_ruling_never_rejects_something_the_user_selected(self):
        import apply_pass_rulings as A
        picks = {"x": {"selected": ["keep"], "rejected": []}}
        passes = {"p.json": {"beats": {"x": {"selected": [],
                                             "shown": ["keep", "drop"]}}}}
        out = self._run(A, picks, passes)
        self.assertEqual(out["x"]["rejected"], ["drop"])
        self.assertIn("keep", out["x"]["selected"])

    def test_a_beat_the_pass_never_judged_is_untouched(self):
        import apply_pass_rulings as A
        picks = {"x": {"selected": [], "rejected": []}}
        passes = {"p.json": {"beats": {"y": {"selected": [], "shown": ["a"]}}}}
        self.assertEqual(self._run(A, picks, passes)["x"]["rejected"], [])

    def test_a_missing_pass_file_raises_rather_than_doing_nothing(self):
        # "a non-match said nothing" — a ruling naming a pass that is not there
        # must be loud, not a silent no-op.
        import apply_pass_rulings as A, tempfile, pathlib
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                A.passed_is_judged({}, {"passedIsJudged": {"_appliesTo": ["nope.json"]}},
                                   pathlib.Path(d))

    def test_the_live_ruling_is_recorded_with_the_users_words(self):
        f = ROOT / "grammar" / "pass-rulings.json"
        self.assertTrue(f.exists())
        r = json.load(open(f))["passedIsJudged"]
        self.assertTrue(r["_quote"].strip(), "a ruling with no quote is an opinion")
        for name in r["_appliesTo"]:
            self.assertTrue((ROOT / "grammar" / "passes" / name).exists(), name)

    def _run(self, A, picks, passes):
        import tempfile, pathlib, json as J
        with tempfile.TemporaryDirectory() as d:
            dp = pathlib.Path(d)
            for n, v in passes.items(): (dp / n).write_text(J.dumps(v))
            out, _ = A.passed_is_judged(
                picks, {"passedIsJudged": {"_appliesTo": list(passes)}}, dp)
            return out


class StoryClassificationSample(unittest.TestCase):
    """The taxonomy test buys a SAMPLE, so the sample decides what it measures.

    The 274 units run in timeline order. Taking the first 30 samples the opening
    six minutes of one documentary and answers "does the taxonomy cover an
    introduction" — not the question being paid for. 18 rhetorical functions
    appear across the reference; the sample keeps their proportions. LOG 0082.
    """

    def items(self, n_per):
        out = []
        for fn, n in n_per.items():
            for i in range(n):
                out.append({"row": f"{fn}{i}", "start": len(out),
                            "rhetoricalFunction": fn})
        return out

    def test_every_function_survives_the_sample(self):
        import classify_story as CS
        items = self.items({"evidence": 65, "claim": 48, "answer": 1, "hook": 4})
        got = CS.sample(items, 30)
        self.assertEqual(len(got), 30)
        self.assertEqual({i["rhetoricalFunction"] for i in got},
                         {"evidence", "claim", "answer", "hook"},
                         "a rare rhetorical function was rounded out of the sample")

    def test_the_sample_is_not_just_the_first_n(self):
        import classify_story as CS
        items = self.items({"a": 20, "b": 20, "c": 20})
        got = CS.sample(items, 9)
        self.assertNotEqual([i["row"] for i in got], [i["row"] for i in items[:9]])
        self.assertEqual(len({i["rhetoricalFunction"] for i in got}), 3)

    def test_asking_for_everything_returns_everything_in_order(self):
        import classify_story as CS
        items = self.items({"a": 3, "b": 2})
        self.assertIs(CS.sample(items, None), items)
        self.assertIs(CS.sample(items, 99), items)

    def test_a_null_job_without_a_reason_is_rejected(self):
        # The whole run exists to read "no job fits". A null job with no
        # missing_job is the model shrugging, and in the output it is
        # indistinguishable from a genuine gap in the taxonomy.
        import classify_story as CS
        want = {"row": "r", "narrationCue": "he kept going"}
        bad = CS.validate({"row": "r", "job": None, "missing_job": "",
                           "media_kind": "broll", "staging_carries_it": False,
                           "evidence": "he kept going"}, want)
        self.assertTrue(any("missing_job" in b for b in bad), bad)
        ok = CS.validate({"row": "r", "job": None,
                          "missing_job": "a mood held across a passage",
                          "media_kind": "broll", "staging_carries_it": False,
                          "evidence": "he kept going"}, want)
        self.assertEqual(ok, [])

    def test_evidence_must_quote_what_we_sent(self):
        import classify_story as CS
        want = {"row": "r", "narrationCue": "he kept going"}
        bad = CS.validate({"row": "r", "job": "narrate_an_event", "missing_job": None,
                           "media_kind": "broll", "staging_carries_it": False,
                           "evidence": "the model's own summary of the beat"}, want)
        self.assertTrue(any("not a span" in b for b in bad), bad)

    def test_an_invented_job_is_rejected(self):
        import classify_story as CS
        want = {"row": "r", "narrationCue": "x"}
        bad = CS.validate({"row": "r", "job": "vibe_setting", "missing_job": None,
                           "media_kind": "broll", "staging_carries_it": False,
                           "evidence": "x"}, want)
        self.assertTrue(any("not one of the twenty" in b for b in bad), bad)


class StoryRunnerParsesWhatThePromptAsksFor(unittest.TestCase):
    """Two defects that cost $0.20 and 12 of 30 records on the calibration run.
    Both mine, neither the model's. LOG 0082.

    (a) PROMPT-classify-reference.md says output a `{"beats":[...]}` wrapper. The
        runner appended "Output one JSON object per line, nothing else." The model
        obeyed whichever it liked; when it obeyed the PROMPT, the line
        `{"beats": [` hit json.loads and raised at char 10 and the whole batch
        was lost. 3 batches, 10 records.
    (b) The runner SENDS a composite line — "rhetoricalFunction / claimType —
        viewerTakeaway" — then validated the model's quote against the atomic
        source fields, which never contain the composite. 5 records rejected for
        quoting exactly what they were shown.
    """

    def test_the_wrapper_the_prompt_asks_for_parses(self):
        import classify_story as CS
        reply = '{"beats": [\n{"row":"A","job":"enumerate"},\n{"row":"B","job":null}\n]}'
        self.assertEqual([r["row"] for r in CS.parse(reply)], ["A", "B"])

    def test_line_delimited_still_parses(self):
        import classify_story as CS
        reply = '{"row":"A","job":"enumerate"}\n{"row":"B","job":null}'
        self.assertEqual([r["row"] for r in CS.parse(reply)], ["A", "B"])

    def test_a_fenced_wrapper_parses(self):
        import classify_story as CS
        reply = '```json\n{"beats":[{"row":"A"}]}\n```'
        self.assertEqual([r["row"] for r in CS.parse(reply)], ["A"])

    def test_nothing_parseable_returns_empty_not_a_crash(self):
        import classify_story as CS
        self.assertEqual(CS.parse("I could not classify these."), [])

    def test_evidence_is_checked_against_what_was_actually_sent(self):
        # The model quoting the composite line it was shown must PASS.
        import classify_story as CS
        want = {"row": "r", "narrationCue": "he kept going",
                "rhetoricalFunction": "contrast", "claimType": "contradiction",
                "viewerTakeaway": "Future publicly distances himself"}
        rec = {"row": "r", "job": "inversion", "missing_job": None,
               "media_kind": "broll", "staging_carries_it": False,
               "evidence": "contrast / contradiction — Future publicly distances himself"}
        self.assertEqual(CS.validate(rec, want), [])

    def test_an_invented_quote_still_fails(self):
        import classify_story as CS
        want = {"row": "r", "narrationCue": "he kept going"}
        rec = {"row": "r", "job": "narrate_an_event", "missing_job": None,
               "media_kind": "broll", "staging_carries_it": False,
               "evidence": "a summary the model wrote itself about perseverance"}
        self.assertTrue(any("not a span" in b for b in CS.validate(rec, want)))


class SpatialMarkersCarryPortraits(unittest.TestCase):
    """media_slots: 0 on a spatial was the DEMO RENDER, not the template.

    User 2026-09-22: "each node on top of a stick will be a headshot or quarter
    img of an artist" and "all spatials plot people". Four records measured
    media_slots 0 while placing 2-93 markers; the two that already showed
    portraits measured media_slots == slots_at_once exactly. So the zeros are
    bare-marker demos, and the correction is deterministic rather than a guess.

    capabilityCorrections was ADD-ONLY, which unions list fields and cannot
    express 0 -> 93 on an integer. `set` is the scalar form, and it is deliberately
    separate so an add can never silently overwrite a measurement. LOG 0086.
    """

    MARKER = {"truth-population-field", "two-floors", "truth-rank-fall",
              "truth-ratio-days"}

    def test_set_replaces_a_scalar_and_add_still_unions(self):
        cap = {"r": {"media_slots": 0, "carries": ["magnitude"]}}
        corr = {"r": {"set": {"media_slots": 93},
                      "add": {"carries": ["difference"]},
                      "why": "x"}}
        out = C.apply_capability_corrections(cap, corr)
        self.assertEqual(out["r"]["media_slots"], 93)
        self.assertEqual(out["r"]["carries"], ["difference", "magnitude"])

    def test_set_refuses_a_list_field(self):
        # `set` on a list would delete a measurement, which is what add-only
        # exists to prevent. Scalars only.
        with self.assertRaises(ValueError):
            C.apply_capability_corrections(
                {"r": {"carries": ["a"]}}, {"r": {"set": {"carries": ["b"]}}})

    def test_every_marker_spatial_now_needs_media(self):
        cap = C._capability()
        for rid in self.MARKER:
            rec = cap.get(rid)
            if not rec: continue
            self.assertEqual(rec.get("media_slots"), rec.get("slots_at_once"),
                             f"{rid}: one portrait per marker")

    def test_the_correction_creates_no_new_match_cut_vessels(self):
        # is_match_cut() keys on media_slots >= 6 AND carries == ["identity"].
        # Raising media_slots must not manufacture a vessel: these records carry
        # magnitude and difference, not identity alone. If that ever changes,
        # this fails rather than quietly widening the b-roll admission.
        pool = {r["id"]: r for r in C.load(content_class="*")}
        for rid in self.MARKER:
            r = pool.get(rid)
            if not r: continue
            self.assertFalse(C.is_match_cut(r),
                             f"{rid} became a match-cut vessel via media_slots")


class MediaEvidenceUsesARealFallbackBoundary(unittest.TestCase):
    """Identity tags/faces win before captions or project labels are admitted.

    "Drake Year 17 - Instagram" is on 118 assets as an ingest/project label. A
    contains-match on "drake" hits every one, including photos of other people
    entirely. That is systematic noise, not the incidental contamination the user
    accepted — it would cost 118 W presses on the very first brief.

    A weak source may still be useful when it is all the library has.  It must be
    a fallback pool, though, not a lower-ranked card shuffled back into the same
    review slate as confirmed identity evidence.  User review 2026-09-25.

    AMENDED 2026-09-25 by user ruling: that fallback applies to CAPTIONS only. A
    project label is excluded outright — see the note above the two inverted tests.
    """

    def rec(self, **kw):
        base = {"id": "a", "media_type": "image", "tags": [], "people": [],
                "captions": [], "derivatives": [], "framing": None,
                "is_group": False, "has_cutout": False}
        base.update(kw)
        import media_candidates as M
        base["_hay"] = M.norm(" ".join(
            [t["tag"] for t in base["tags"]] + base["people"] + base["captions"]))
        return base

    def test_a_content_tag_prevents_project_fallback_from_entering_the_pool(self):
        import media_candidates as M
        proj = self.rec(id="a_project",
                        tags=[{"tag": "Drake Year 17 - Instagram", "source": "ingest"}])
        cont = self.rec(id="b_content",
                        tags=[{"tag": "drake", "source": "subject-tag"}])
        out = M.resolve(["drake"], pool={"a_project": proj, "b_content": cont},
                        wrong=set())
        self.assertEqual([r["id"] for r in out["individual"]["drake"]],
                         ["b_content"])

    def test_a_content_tag_prevents_caption_fallback_from_entering_the_pool(self):
        import media_candidates as M
        caption = self.rec(id="a_caption", captions=["Drake walks into the arena"])
        tagged = self.rec(id="b_tagged",
                          tags=[{"tag": "drake", "source": "subject-tag"}])
        out = M.resolve(["drake"], pool={"a_caption": caption, "b_tagged": tagged},
                        wrong=set())
        self.assertEqual([r["id"] for r in out["individual"]["drake"]],
                         ["b_tagged"])

    def test_caption_is_used_when_no_identity_evidence_exists(self):
        import media_candidates as M
        caption = self.rec(id="caption", captions=["Drake walks into the arena"])
        out = M.resolve(["drake"], pool={"caption": caption}, wrong=set())
        self.assertEqual([r["id"] for r in out["individual"]["drake"]],
                         ["caption"])

    def test_delivery_identity_is_primary_evidence(self):
        import media_candidates as M
        delivered = self.rec(id="delivered", delivered_identities=["Drake"])
        delivered["_hay"] = M.norm("Drake")
        caption = self.rec(id="caption", captions=["Drake walks into the arena"])
        out = M.resolve(["drake"], pool={"caption": caption, "delivered": delivered},
                        wrong=set())
        self.assertEqual([r["id"] for r in out["individual"]["drake"]],
                         ["delivered"])
        self.assertTrue(M._why(delivered, "drake").startswith("identity:"))

    # ---- OVERRULED 2026-09-25 -------------------------------------------------
    # Two tests here asserted that a project label is returned as a ranked weak
    # match: test_a_project_match_says_it_is_a_project and
    # test_a_project_match_is_still_returned ("a weak match must rank, not vanish").
    # The user ruled the opposite: "Drake Year 17 - Instagram. shouldnt be a tag.
    # that add garbage to the canidates. i seen this frst hand. projects shouldnt
    # be tags at all."
    #
    # This does NOT overturn "ranks, never excludes". That rule says every SIGNAL
    # orders candidates and none removes them. A project folder name is not a
    # signal about what an asset shows — it records which batch imported it — so
    # there is nothing to rank. Caption evidence is still a ranked fallback and is
    # still covered, by test_caption_is_used_when_no_identity_evidence_exists.
    # The two tests are inverted below rather than deleted, so the reversal stays
    # visible to whoever reads this class next.

    def test_a_project_name_claims_no_evidence_at_all(self):
        import media_candidates as M
        proj = self.rec(tags=[{"tag": "Drake Year 17 - Instagram",
                               "source": "ingest"}])
        self.assertIsNone(M._evidence(proj, "drake"))
        self.assertFalse(M._why(proj, "drake").startswith("project:"),
                         "a project label is still claiming to be evidence")

    def test_a_project_name_is_not_returned_even_as_a_last_resort(self):
        import media_candidates as M
        # a REAL ingestion project, so the derived set recognises it
        self.assertIn(M.norm("Drake and Jay-Z together collection"), M.projects(),
                      "fixture is not a registered project; the test would be vacuous")
        proj = self.rec(tags=[{"tag": "Drake and Jay-Z together collection",
                               "source": "ingest"}])
        out = M.resolve(["drake", "jay"], pool={"a": proj}, wrong=set())
        self.assertEqual(out["group"], [], "a project label produced a group match")
        self.assertEqual(out["individual"]["drake"], [])
        # and the absence is REPORTED as a sourcing gap, never silently empty
        self.assertEqual(sorted(out["gaps"]), ["drake", "jay"])

    def test_a_strong_group_prevents_a_weak_group_from_entering_the_pool(self):
        import media_candidates as M
        strong = self.rec(id="b_strong", people=["Drake", "Jay-Z"])
        weak = self.rec(id="a_weak", people=["Drake"],
                        tags=[{"tag": "Jay-Z fan collection", "source": "ingest"}])
        out = M.resolve(["drake", "jay-z"],
                        pool={"b_strong": strong, "a_weak": weak}, wrong=set())
        self.assertEqual([r["id"] for r in out["group"]], ["b_strong"])

    def test_a_w_correction_removes_it_for_that_entity_only(self):
        import media_candidates as M
        r = self.rec(id="x", people=["Jay Rock"])
        pool = {"x": r}
        self.assertEqual(len(M.resolve(["jay"], pool=pool, wrong=set())
                             ["individual"]["jay"]), 1)
        out = M.resolve(["jay"], pool=pool, wrong={("x", "jay")})
        self.assertEqual(out["individual"]["jay"], [])
        self.assertEqual(out["gaps"], ["jay"], "a corrected-away entity is a GAP")


class GridCapacityIsTheCardNotTheRender(unittest.TestCase):
    """09_artist_field_grid measured 27 and holds 30.

    User 2026-09-22: "the grids we have as a template and Equal-weight identity
    grid has room for up to 30." Corroborated by the card's OWN axes, which
    declare entities: 30 and csv_rows: 30 — the video pass counted 27 because
    that is what one render put on screen. FACTS 2.9: a measurement observes one
    instance, the declaration describes the template.

    media_slots moves with it: every cell in an identity grid is a portrait, the
    same rule the spatials were corrected under (LOG 0086). LOG 0088.
    """

    def test_the_grid_holds_thirty(self):
        cap = C._capability()
        rec = cap.get("09_artist_field_grid")
        if not rec: self.skipTest("record not in capability.json")
        self.assertEqual(rec.get("slots_at_once"), 30)
        self.assertEqual(rec.get("slots_total"), 30)

    def test_every_cell_is_a_portrait(self):
        cap = C._capability()
        rec = cap.get("09_artist_field_grid")
        if not rec: self.skipTest("record not in capability.json")
        self.assertEqual(rec.get("media_slots"), rec.get("slots_at_once"),
                         "an identity grid needs one portrait per cell")

    def test_the_cards_own_axes_back_the_number(self):
        # The guard against this being a bare declaration: if the card ever stops
        # saying 30, the override needs re-justifying rather than standing on
        # nothing.
        pool = {r["id"]: r for r in C.load(content_class="*")}
        r = pool.get("09_artist_field_grid")
        if not r: self.skipTest("record not in pool")
        ax = r.get("axes") or {}
        self.assertEqual(ax.get("entities"), 30,
                         "the card no longer declares 30; re-justify the override")


class MediaSlatesSpreadInsteadOfSorting(unittest.TestCase):
    """Ranking by a facet buries the facet. Spread across it instead.

    Measured on the first real pass: every entity appearing on more than one
    brief got an IDENTICAL top-8 — Drake on four briefs, the same eight cards
    four times ("keep seeing same drake imgs"). Video was 11% of what was shown
    against 25% of the library, because `has_cutout` ranked second and no clip
    has a cutout. Framing came back full_body 71 to headshot 6 ("these are all
    full body").

    Same defect the template side had with FAM_MAX, one layer down: sorting by a
    property makes the top of the list homogeneous in that property. LOG 0090.
    """

    def recs(self, spec):
        import media_candidates as M
        out = []
        for i, (mt, fr, cut) in enumerate(spec):
            out.append({"id": f"r{i:02}", "media_type": mt, "framing": fr,
                        "has_cutout": cut, "tags": [], "people": [], "captions": [],
                        "derivatives": [], "_hay": "", "is_group": False})
        return out

    def test_video_survives_into_the_visible_set(self):
        import media_candidates as M
        # 12 cutout images then 4 clips: a plain sort shows zero clips in 8.
        recs = self.recs([("image", "full_body", True)] * 12 + [("video", None, False)] * 4)
        got = M.spread(recs, 8)
        self.assertTrue(any(r["media_type"] == "video" for r in got),
                        "no clip reached the visible set")

    def test_framing_is_not_all_one_kind(self):
        import media_candidates as M
        recs = self.recs([("image", "full_body", True)] * 10
                         + [("image", "headshot", True)] * 4)
        got = M.spread(recs, 8)
        self.assertGreater(len({r["framing"] for r in got}), 1,
                           "every visible card has the same framing")

    def test_a_second_brief_does_not_repeat_the_first(self):
        import media_candidates as M
        recs = self.recs([("image", "full_body", True)] * 20)
        first = M.spread(recs, 8)
        second = M.spread(recs, 8, used={r["id"] for r in first})
        overlap = {r["id"] for r in first} & {r["id"] for r in second}
        self.assertLess(len(overlap), 4,
                        f"{len(overlap)} of 8 repeated from the previous brief")

    def test_spread_never_drops_a_candidate_it_was_given(self):
        # Ranks, never excludes — the standing rule. Asking for more than exists
        # returns everything, in some order, losing nothing.
        import media_candidates as M
        recs = self.recs([("image", "full_body", True), ("video", None, False)])
        self.assertEqual({r["id"] for r in M.spread(recs, 99)},
                         {r["id"] for r in recs})

    def test_order_is_stable_for_the_same_input(self):
        import media_candidates as M
        recs = self.recs([("image", "full_body", True), ("video", None, False),
                          ("image", "headshot", False)])
        self.assertEqual([r["id"] for r in M.spread(recs, 3)],
                         [r["id"] for r in M.spread(recs, 3)])


class AMediaPickSurvivesAReshuffle(unittest.TestCase):
    """A selection is a decision. A reshuffle may not take it away.

    Adding spread() to fix the repeated-Drake problem moved cards, and 4 of the
    user's 14 picks fell out — two below the 16-card window, two not shipped at
    all because the rotation pushed them past the 28 shipped for that brief.

    This is LOG 0031 on the media side: "a rebind silently dropped a binding the
    user had validated and the slate stopped showing their pick." The template
    side has had a test for it since; the media side did not. LOG 0090.
    """

    def test_every_recorded_pick_is_shipped_or_explicitly_displaced(self):
        f = ROOT / "pipeline" / "ui5-media" / "data.json"
        pf = ROOT / "grammar" / "media-picks.json"
        if not (f.exists() and pf.exists()): self.skipTest("not built")
        D = json.load(open(f))
        import media_candidates as M
        picks = M.picked()          # ONE reader for the file's shape
        by = {b["brief"]: b for b in D["briefs"]}
        lost = []
        for key, ids in picks.items():
            brief, tier = key.split("::", 1)
            b = by.get(brief)
            if not b: continue
            cards = (b["group"] if tier == "group"
                     else b["individual"].get(tier[2:], []))
            have = {c["id"] for c in cards}
            lost += [f"{key}:{i[:12]}" for i in ids if i not in have]
        displaced = {f"{x['brief']}::{x['tier']}:{x['assetId'][:12]}"
                     for x in D.get("displacedPicks", [])}
        self.assertEqual(set(lost), displaced,
                         "a prior pick was silently lost or falsely displaced")

    def test_a_displaced_pick_is_preserved_but_never_reintroduced(self):
        """Displaced from ITS TIER — not banished from the review.

        The first version asserted two things that were true when only one reason
        existed: that every reason is "not_in_production_ready", and that a
        displaced asset appears on NO card anywhere. Both broke on 2026-09-26 when
        the builder started recording the second shape of loss.
        A pick can now be displaced because its TIER stopped applying — 28-28's
        group tier asks for one asset carrying ten entities, which no photograph
        does (LOG 0117) — while the asset itself stays a perfectly good candidate
        for the entity it actually shows. Banishing it would throw away a usable
        asset to satisfy a bookkeeping rule.
        """
        f = ROOT / "pipeline" / "ui5-media" / "data.json"
        if not f.exists(): self.skipTest("not built")
        D = json.load(open(f))
        by = {b["brief"]: b for b in D["briefs"]}
        for x in D.get("displacedPicks", []):
            self.assertTrue(str(x.get("reason") or "").strip(),
                            "a displaced pick carries no reason")
            b = by.get(x["brief"])
            if not b: continue
            tier = x["tier"]
            here = ({c["id"] for c in b["group"]} if tier == "group"
                    else {c["id"] for c in b["individual"].get(tier[2:], [])})
            self.assertNotIn(x["assetId"], here,
                             f"{x['assetId'][:12]} was displaced from {x['brief']}"
                             f"::{tier} and is still on that slate")

    def test_every_unshippable_pick_is_recorded_as_displaced(self):
        # The point of the list: a pick that cannot ship must never vanish quietly.
        import media_candidates as M
        f = ROOT / "pipeline" / "ui5-media" / "data.json"
        if not f.exists(): self.skipTest("not built")
        D = json.load(open(f))
        by = {b["brief"]: b for b in D["briefs"]}
        known = {(d["brief"], d["tier"], d["assetId"]) for d in D.get("displacedPicks", [])}
        lost = []
        for key, ids in M.picked().items():
            brief, tier = key.split("::", 1)
            b = by.get(brief)
            if not b: continue
            here = ({c["id"] for c in b["group"]} if tier == "group"
                    else {c["id"] for c in b["individual"].get(tier[2:], [])})
            lost += [(brief, tier, i) for i in ids
                     if i not in here and (brief, tier, i) not in known]
        self.assertEqual(lost, [], f"{len(lost)} pick(s) silently unshipped")

    def test_spread_keeps_a_pinned_record_even_when_rotated_out(self):
        import media_candidates as M
        recs = [{"id": f"r{i:02}", "media_type": "image", "framing": "full_body",
                 "has_cutout": True} for i in range(30)]
        # r29 is last and `used` pushes it further back; pinning must beat both
        got = M.spread(recs, 8, used={"r29"}, pin={"r29"})
        self.assertIn("r29", [r["id"] for r in got], "a pinned pick was rotated out")
        self.assertEqual(got[0]["id"], "r29", "a pin should lead, not merely survive")


class MediaReviewCarriesDecisionContext(unittest.TestCase):
    """A lettered beat side is not understandable without its siblings/templates."""

    def data(self):
        f = ROOT / "pipeline" / "ui5-media" / "data.json"
        if not f.exists(): self.skipTest("review not built")
        return json.load(open(f))

    def test_lettered_sides_share_one_family_and_expose_each_other(self):
        D = self.data()
        by = {b["brief"]: b for b in D["briefs"]}
        a, b = by["02-02a"], by["02-02b"]
        self.assertEqual(a["segmentFamily"], "02-02")
        self.assertEqual(b["segmentFamily"], "02-02")
        sib = {x["brief"]: x for x in a["pairedSides"]}["02-02b"]
        direction = (sib.get("mediaDirection") or "").lower()
        self.assertIn("mixtape", direction)
        self.assertIn("jetlife", direction.replace(" ", ""))
        self.assertIn("features", direction)

    def test_existing_template_previews_are_shipped_not_recreated(self):
        D = self.data()
        previews = D.get("templatePreviews") or {}
        for tid in ("06-the-history--scene-001",
                    "archive3-looped-slideshow-background--review-001"):
            self.assertIn(tid, previews)
            self.assertTrue(previews[tid].get("poster"), f"{tid}: no poster")
        self.assertTrue(previews["archive3-looped-slideshow-background--review-001"].get("clip"))

    def test_review_pages_complete_segment_families(self):
        D = self.data()
        self.assertEqual(D.get("segmentFamiliesPerPage"), 2)
        html = (ROOT / "pipeline" / "ui5-media" / "index.html").read_text()
        self.assertIn('id="prevPage"', html)
        self.assertIn('id="nextPage"', html)
        self.assertIn("segmentFamily", html)
        self.assertIn("templatePreviews", html)
        self.assertIn("class='brieflayout'", html)
        self.assertIn("class='template-grid'", html)
        self.assertIn('<meta charset="utf-8">', html.lower())


class GazetteerEntityExtraction(unittest.TestCase):
    """Entity extraction is a LOOKUP, not a model call. LOG 0091.

    The names here are what statistical NER gets wrong — Curren$y splits at the
    $, 21 Savage reads as CARDINAL + noun. And a model can normalise a name into
    something that is not it, after which every downstream lookup misses. A
    roster match cannot hallucinate.
    """

    # Deliberately mirrors the LIVE roster's shape: Jay-Z is ABSENT (the real
    # roster is 109 streaming-era artists and does not carry him), and
    # "Chance the Rapper" is present so the article "the" is genuinely a shared
    # token. An earlier fixture had Jay-Z in and Chance out, which made two of
    # these tests pass without the condition ever arising.
    NAMES = ["Jay Rock", "Kendrick Lamar", "Curren$y", "Ty Dolla $ign",
             "21 Savage", "Kid Cudi", "Kid Ink", "Future", "Ab-Soul",
             "Freddie Gibbs", "Young Thug", "Chance the Rapper",
             "Ski Mask the Slump God"]

    def ex(self, text):
        import entities as E
        return E.extract(text, self.NAMES)

    def test_longest_match_wins(self):
        # THE defect this replaces: a seed pulled "Jay" from "Jay Rock" and sent
        # the brief to 68 Jay-Z photos.
        r = self.ex("Ab-Soul falls twenty-eight places. Jay Rock, twelve.")
        self.assertIn("Jay Rock", r["entities"])
        self.assertNotIn("Jay-Z", r["entities"])

    def test_punctuated_names_survive(self):
        r = self.ex("Curren$y was on the cover, and Ty Dolla $ign guested.")
        self.assertEqual(sorted(r["entities"]), ["Curren$y", "Ty Dolla $ign"])

    def test_a_leading_number_is_part_of_the_name(self):
        self.assertIn("21 Savage", self.ex("21 Savage has four.")["entities"])

    def test_a_unique_token_resolves_to_its_full_name(self):
        # the narration says Kendrick; the roster says Kendrick Lamar
        r = self.ex("Kendrick, Post Malone and Travis Scott have five each.")
        self.assertIn("Kendrick Lamar", r["entities"])

    def test_an_ambiguous_token_is_reported_not_guessed(self):
        # "Kid" belongs to Kid Cudi AND Kid Ink. Guessing puts the wrong person
        # on screen, and a wrong entity is the one failure review cannot correct.
        r = self.ex("Kid was on that cover too.")
        self.assertEqual(r["entities"], [])
        self.assertEqual(r["ambiguous"][0]["candidates"], ["Kid Cudi", "Kid Ink"])

    def test_a_common_word_lowercase_is_not_an_artist(self):
        # six roster names are ordinary English words
        self.assertEqual(self.ex("nobody knows what the future holds")["entities"], [])
        self.assertIn("Future", self.ex("Near the top, Future.")["entities"])

    def test_extraction_is_stable(self):
        t = "Curren$y, Jay Rock and Kendrick were on it."
        self.assertEqual(self.ex(t), self.ex(t))

    def test_a_hyphenated_name_is_not_split_into_a_roster_match(self):
        """The inverse of the bug this class exists to fix, and worse.

        Beat 30-30a says "There's no daily meter for Jay-Z's year seventeen."
        This fixture deliberately omits Jay-Z. Tokenising on whitespace alone
        must never take "Jay" and silently return Jay Rock.
        """
        r = self.ex("There's no daily meter for Jay-Z's year seventeen.")
        self.assertNotIn("Jay Rock", r["entities"])

    def test_a_name_the_roster_lacks_is_REPORTED(self):
        # Unknown must be visible, never silent.
        r = self.ex("The set also featured Testperson Neverindexed.")
        self.assertIn("Neverindexed", [u["text"] for u in r["unknown"]])

    def test_an_article_is_never_an_entity_token(self):
        # "the" belongs to Chance the Rapper and Ski Mask the Slump God, so it
        # was reported ambiguous on 5 of 24 beats. It is an article.
        r = self.ex("The rappers on that cover came up together.")
        self.assertEqual(r["ambiguous"], [])

    def test_the_live_roster_is_a_dated_snapshot(self):
        # a shared registry that drifts silently is worse than none
        import entities as E
        names, meta = E.roster()
        self.assertTrue(meta.get("_snapshotAt"), "no snapshot date")
        self.assertEqual(len(names), meta["_count"])
        self.assertEqual(meta["_registryId"], "registry:hiphop-research-engine-csv-v1")
        self.assertEqual(meta["_registryVersion"], "11")
        self.assertEqual(meta["_source"]["authority"], "djtoler/entity_roster")

    def test_names_are_deduped_on_a_normalised_key(self):
        # JAY-Z / Jay-Z / jay z must be ONE entry, or a brief asks for the same
        # person twice and the slate splits.
        import entities as E
        import media_candidates as M
        names, _ = E.roster()
        seen = {}
        for n in names:
            k = M.norm(n)
            self.assertNotIn(k, seen, f"{n!r} and {seen.get(k)!r} are one name")
            seen[k] = n

    def test_stale_shared_roster_digest_fails_closed(self):
        import entities as E
        source = E.roster_path()
        with tempfile.TemporaryDirectory() as td:
            changed = pathlib.Path(td) / "entity-roster.json"
            changed.write_bytes(source.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                E.roster(changed)


class ReviewShowsTheProcessedDerivative(unittest.TestCase):
    """The review showed raw imports, not the assets that would actually be placed.

    User 2026-09-22 on brief 15-15: "there are nearly completely irrelevant and
    you're pulling from somwehere that has the pre-processed images. these are
    even before they're been cropped."

    Correct. media_candidates read assets.canonical_path — the immutable
    10_ORIGINALS import — while 347 cutouts, 201 previews and 146 glow-cutouts
    sat unused. 90 of the 165 cards on screen had a cutout that was not shown.
    Judging a raw import is judging something that will never be placed. LOG 0093.

    The original is still the IDENTITY and the provenance; only what is displayed
    changes.
    """

    def rec(self, derivs):
        return {"id": "a", "path": "/orig.jpg", "derivatives": derivs}

    def test_a_cutout_is_preferred_over_the_raw_original(self):
        import media_candidates as M
        r = self.rec([{"type": "cutout", "path": "/cut.png"}])
        self.assertEqual(M.display_path(r), "/cut.png")

    def test_the_original_is_still_carried(self):
        # provenance and identity stay with the canonical file
        import media_candidates as M
        r = self.rec([{"type": "cutout", "path": "/cut.png"}])
        self.assertEqual(r["path"], "/orig.jpg")

    def test_kept_original_means_do_not_substitute(self):
        # the user ticked "Keep original — do not run this image through the
        # processing pipeline". Honouring a cutout over that would override a
        # decision they already made.
        import media_candidates as M
        r = self.rec([{"type": "kept-original", "path": "/keep.jpg"},
                      {"type": "preview", "path": "/prev.png"}])
        self.assertEqual(M.display_path(r), "/orig.jpg")

    def test_preview_beats_nothing_but_loses_to_cutout(self):
        import media_candidates as M
        self.assertEqual(M.display_path(self.rec(
            [{"type": "preview", "path": "/p.png"}])), "/p.png")
        self.assertEqual(M.display_path(self.rec(
            [{"type": "preview", "path": "/p.png"},
             {"type": "cutout", "path": "/c.png"}])), "/c.png")

    def test_a_VIDEO_never_gets_a_still_substituted(self):
        """The defect LOG 0093 introduced, caught by running the consumer.

        A video's `preview` derivative is a STILL. display_path() returned it,
        the builder transcoded a single PNG into an mp4, and 57 of 73 clips came
        out 0.04 SECONDS LONG — one frame, 3.5 KB, unplayable as a clip. 245 of
        325 videos were affected. A derivative substitution is only valid when it
        is the same medium. LOG 0100.
        """
        import media_candidates as M
        r = {"id": "v", "media_type": "video", "path": "/clip.mov",
             "derivatives": [{"type": "preview", "path": "/still.jpg"}]}
        self.assertEqual(M.display_path(r), "/clip.mov")

    def test_a_video_may_still_take_a_video_derivative(self):
        import media_candidates as M
        r = {"id": "v", "media_type": "video", "path": "/clip.mov",
             "derivatives": [{"type": "preview", "path": "/smaller.mp4"}]}
        self.assertEqual(M.display_path(r), "/smaller.mp4")

    def test_no_live_clip_is_a_single_frame(self):
        # the backstop: if a transcode ever produces a still-as-clip again, this
        # fails rather than shipping 57 unplayable cards
        import subprocess, glob, os
        d = ROOT / "pipeline" / "ui5-media" / "media"
        if not d.exists(): self.skipTest("review not built")
        bad = []
        for f in sorted(glob.glob(str(d / "*.mp4")))[:80]:
            out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                  "format=duration", "-of", "csv=p=0", f],
                                 capture_output=True, text=True).stdout.strip()
            try:
                if float(out) < 1.0: bad.append(os.path.basename(f))
            except ValueError:
                bad.append(os.path.basename(f) + " (unreadable)")
        self.assertEqual(bad, [], f"{len(bad)} clip(s) under 1 second")

    def test_no_derivative_falls_back_to_the_original(self):
        import media_candidates as M
        self.assertEqual(M.display_path(self.rec([])), "/orig.jpg")

    def test_the_live_pool_serves_derivatives_where_they_exist(self):
        import media_candidates as M, os
        try:
            pool = M.load()
        except FileNotFoundError:
            self.skipTest("media library not present")
        sub = [r for r in pool.values() if M.display_path(r) != r["path"]]
        self.assertTrue(sub, "no asset serves a derivative; the fix is not wired")
        for r in sub[:40]:
            self.assertTrue(os.path.exists(M.display_path(r)),
                            f"{r['id']}: display path does not exist")


class FramingComesFromTheTemplate(unittest.TestCase):
    """A slot's framing is a property of the TEMPLATE, not of the beat.

    The most repeated note in media pass 1:
      09-09 "we may need a way to determine if we need quarter/headshots,
             fullbody or 3quarter"
      28-28 "image tags need a way to match template capability. it should only
             be quarter, headshot or no no size specified images... spatial
             needs only those for the nodes"
      04-04 "these are all full body, need to update media lib with travis
             headshots or quarter body"
    User 2026-09-22: "hero asks for halfbody or full or 3quarter body."

    And the tag vocabulary was inconsistent: '3quarter' (9 assets) and
    'Three Quarter' (5) are the same framing under two names, and
    media_candidates mapped 'quarter' to three_quarter — quarter is TIGHTER
    than half, not wider. LOG 0094.
    """

    def test_the_scale_is_ordered_tightest_to_widest(self):
        import media_candidates as M
        self.assertEqual(M.FRAMING_SCALE,
                         ("headshot", "quarter", "half", "three_quarter", "full"))

    def test_both_spellings_of_three_quarter_normalise(self):
        import media_candidates as M
        self.assertEqual(M.framing_of("3quarter"), "three_quarter")
        self.assertEqual(M.framing_of("Three Quarter"), "three_quarter")
        self.assertEqual(M.framing_of("3/4"), "three_quarter")

    def test_quarter_is_not_three_quarter(self):
        # the bug: 'quarter' was mapped to three_quarter, so 8 tight crops were
        # offered to slots wanting a wide shot and vice versa
        import media_candidates as M
        self.assertEqual(M.framing_of("quarter"), "quarter")
        self.assertNotEqual(M.framing_of("quarter"), M.framing_of("3quarter"))

    def test_half_and_upper_body_are_one_framing(self):
        import media_candidates as M
        self.assertEqual(M.framing_of("half"), M.framing_of("Upper Body"))

    def test_subject_count_tags_are_not_framing(self):
        # 'Group' and 'Person Photo' say how many, not how close
        import media_candidates as M
        self.assertIsNone(M.framing_of("Group"))
        self.assertIsNone(M.framing_of("Person Photo"))

    def test_a_hero_wants_half_or_wider(self):
        import media_candidates as M
        want = M.framing_wanted("base-single-billboard")
        self.assertEqual(sorted(want), ["full", "half", "three_quarter"])

    def test_a_spatial_node_wants_tight_crops(self):
        import media_candidates as M
        want = M.framing_wanted("truth-population-field")
        self.assertEqual(sorted(want), ["headshot", "quarter"])

    def test_framing_RANKS_and_never_excludes(self):
        # house rule. A wrong-framing asset sorts last; it does not vanish,
        # because a slot count is a hint and a crop is an editing decision.
        import media_candidates as M
        recs = [{"id": "wide", "media_type": "image", "framing": "full",
                 "has_cutout": False, "_hay": "drake", "derivatives": [],
                 "tags": [], "people": ["Drake"], "captions": []},
                {"id": "tight", "media_type": "image", "framing": "headshot",
                 "has_cutout": False, "_hay": "drake", "derivatives": [],
                 "tags": [], "people": ["Drake"], "captions": []}]
        out = M.resolve(["drake"], pool={r["id"]: r for r in recs}, wrong=set(),
                        wants=("headshot", "quarter"))
        ids = [r["id"] for r in out["individual"]["drake"]]
        self.assertEqual(ids[0], "tight", "the right framing must lead")
        self.assertIn("wide", ids, "the wrong framing must still be reachable")

    def test_an_untagged_asset_is_not_punished(self):
        # 436 of 506 assets carry no framing tag. Ranking them last would hide
        # most of the library behind a tag nobody has applied yet.
        import media_candidates as M
        recs = [{"id": "none", "media_type": "image", "framing": None,
                 "has_cutout": False, "_hay": "drake", "derivatives": [],
                 "tags": [], "people": ["Drake"], "captions": []},
                {"id": "wrong", "media_type": "image", "framing": "full",
                 "has_cutout": False, "_hay": "drake", "derivatives": [],
                 "tags": [], "people": ["Drake"], "captions": []}]
        out = M.resolve(["drake"], pool={r["id"]: r for r in recs}, wrong=set(),
                        wants=("headshot",))
        self.assertEqual([r["id"] for r in out["individual"]["drake"]][0], "none")


class FramingRulesFromTheUser(unittest.TestCase):
    """31 per-template rulings, and three templates where framing does not apply.

    User 2026-09-23: "31/34 templates done. the undone 3 are for documents,
    screenshots and videos." FRAMING IS A PROPERTY OF PERSON MEDIA — a slot
    holding a screenshot has no headshot/quarter/half. Those three are DECIDED
    as not-applicable, which is a third state alongside decided-with-a-want and
    undecided. LOG 0095.
    """

    def rules(self):
        return json.load(open(ROOT / "grammar" / "framing-rules.json"))

    def test_every_want_is_on_the_scale(self):
        R = self.rules()
        scale = set(R["_scale"])
        for tid, r in R["byId"].items():
            self.assertLessEqual(set(r["wants"]), scale, f"{tid} wants an unknown framing")
        for kind, r in R["byKind"].items():
            self.assertLessEqual(set(r["wants"]), scale, f"{kind} wants an unknown framing")

    def test_wants_are_stored_tightest_to_widest(self):
        # the user ticks in whatever order they click; stored order must be the
        # scale, or two identical rules read as different
        R = self.rules()
        for tid, r in R["byId"].items():
            self.assertEqual(r["wants"],
                             sorted(r["wants"], key=R["_scale"].index), tid)

    def test_any_is_distinguishable_from_undecided(self):
        # `wants: []` means "looked, no preference". ABSENT means "not looked at".
        # They rank identically today and mean different things; losing the
        # distinction would make a finished review look unfinished.
        R = self.rules()
        anys = [t for t, r in R["byId"].items() if not r["wants"]]
        self.assertTrue(anys, "no ANY rulings recorded")
        for t in anys:
            self.assertTrue(R["byId"][t].get("decided"),
                            f"{t}: empty wants with no `decided` flag is ambiguous")

    def test_not_applicable_names_its_templates_and_its_reason(self):
        R = self.rules()
        na = R["notApplicable"]
        self.assertTrue(na["templates"], "no templates recorded")
        self.assertIn("person", na["_why"].lower())
        for t in na["templates"]:
            self.assertNotIn(t, R["byId"],
                             f"{t} is both ruled and not-applicable")

    def test_a_not_applicable_template_wants_nothing(self):
        import media_candidates as M
        R = self.rules()
        for t in R["notApplicable"]["templates"]:
            self.assertEqual(M.framing_wanted(t, "after_effects"), (),
                             f"{t}: framing does not apply, so nothing is wanted")

    def test_a_per_template_rule_beats_its_kind(self):
        # 34_superteam_bar_compare is an infographic with an explicit ruling;
        # a kind-level default must not override what the user said about the
        # specific template.
        import media_candidates as M
        self.assertEqual(sorted(M.framing_wanted("34_superteam_bar_compare",
                                                 "infographic")),
                         ["headshot", "quarter"])


class MediaKindIsASeparateAxis(unittest.TestCase):
    """What KIND of media a slot takes, as distinct from how close it crops.

    Three separate findings arrived at the same gap from different directions:
      * user 2026-09-23: "the undone 3 are for documents, screenshots and
        videos" — framing does not describe a screenshot
      * briefs 02-02a and 18-18 want the XXL Freshman cover; 06-06 and 08-08
        want album covers. Not people, so the entity gazetteer cannot hold them
      * brief 23-23: "screenshots in a document template"

    Framing answers HOW CLOSE. This answers WHAT IT IS. LOG 0096.
    """

    def rec(self, **kw):
        base = {"id": "a", "media_type": "image", "people": [], "tags": [],
                "faces": 0, "captions": [], "derivatives": [], "framing": None}
        base.update(kw)
        return base

    def test_a_video_is_footage(self):
        import media_candidates as M
        self.assertEqual(M.kind_of(self.rec(media_type="video")), "footage")

    def test_a_named_face_is_a_person(self):
        import media_candidates as M
        self.assertEqual(M.kind_of(self.rec(people=["Drake"])), "person")

    def test_an_UNNAMED_detected_face_is_still_a_person(self):
        # 131 assets have a detected face nobody has labelled. They are
        # photographs of people whatever we call them, and treating them as
        # unknown would strand them.
        import media_candidates as M
        self.assertEqual(M.kind_of(self.rec(faces=2)), "person")

    def test_an_article_or_ocr_tag_is_a_document(self):
        import media_candidates as M
        for tag in ("Article Or Post", "OCR Extracted"):
            self.assertEqual(
                M.kind_of(self.rec(tags=[{"tag": tag, "source": "subject-tag"}])),
                "document")

    def test_artwork_is_its_own_kind(self):
        import media_candidates as M
        self.assertEqual(M.kind_of(self.rec(
            tags=[{"tag": "Drake Views album artwork official", "source": "subject-tag"}])),
            "artwork")

    def test_a_person_beats_a_weaker_signal(self):
        # an article ABOUT someone, with their face in it, is still a document;
        # but a portrait tagged into a project called "... article" is a person.
        # Face evidence is stronger than a tag phrase.
        import media_candidates as M
        r = self.rec(people=["Drake"],
                     tags=[{"tag": "Article Or Post", "source": "ingest"}])
        self.assertEqual(M.kind_of(r), "person")

    def test_no_signal_is_unknown_not_a_guess(self):
        import media_candidates as M
        self.assertIsNone(M.kind_of(self.rec()))

    def test_kind_RANKS_and_never_excludes(self):
        import media_candidates as M
        recs = [self.rec(id="doc", tags=[{"tag": "Drake", "source": "subject-tag"},
                                               {"tag": "OCR Extracted", "source": "subject-tag"}],
                         _hay="drake"),
                self.rec(id="per", people=["Drake"], _hay="drake")]
        for r in recs: r.setdefault("has_cutout", False)
        out = M.resolve(["drake"], pool={r["id"]: r for r in recs}, wrong=set(),
                        kinds=("document",))
        ids = [r["id"] for r in out["individual"]["drake"]]
        self.assertEqual(ids[0], "doc")
        self.assertIn("per", ids, "the wrong kind must still be reachable")

    def test_the_three_not_applicable_templates_want_a_kind(self):
        import media_candidates as M
        for t in ("screen-mockup-rfx--review-002", "scrolling-screen--review-001"):
            self.assertTrue(M.kind_wanted(t),
                            f"{t}: framing does not apply, so a kind must")


class BeatMediaKindIsDeclaredNotExtracted(unittest.TestCase):
    """The beat does not say what media it wants. The user does.

    Two extraction methods were built and MEASURED against the user's own
    answers before this was accepted (LOG 0098):
      * a 633-title work gazetteer from the RIAA files found ONE true positive
        across 40 beats — `Views` — and every guard strong enough to suppress
        the noise (X from "XXL", BE from "number", YE from "played") also
        suppressed it
      * a work-noun signal (catalog, song, record, cover, class...) reached
        100% recall at 20% PRECISION, because the whole script is about a
        catalog
    The narration says "Big back catalog". Deciding that album covers serve it
    is taste, and no extractor recovers a judgment that was never written down.
    So it is declared, in the file that already holds per-beat declarations.
    """

    def flags(self):
        return json.load(open(ROOT / "grammar" / "beat-flags.json"))

    def test_every_declaration_carries_the_users_words(self):
        F = self.flags()
        for beat, b in F["beats"].items():
            if "wantsMediaKind" not in b: continue
            why = b.get("wantsMediaKindWhy") or ""
            self.assertIn("User", why, f"{beat}: no attribution")
            self.assertIn('"', why, f"{beat}: no quote — a declaration without "
                                    f"their words is my opinion wearing their name")

    def test_every_kind_is_in_the_vocabulary(self):
        import media_candidates as M
        F = self.flags()
        for beat, b in F["beats"].items():
            for k in (b.get("wantsMediaKind") or []):
                self.assertIn(k, M.MEDIA_KINDS, f"{beat}: {k!r} is not a media kind")

    def test_the_flag_is_documented_where_the_others_are(self):
        F = self.flags()
        self.assertIn("wantsMediaKind", F["_flags"])
        self.assertIn("DECLARED", F["_flags"]["wantsMediaKind"])

    def test_declared_beats_reach_the_briefs(self):
        # media-briefs.json is the INPUT; wantsKind is computed into the BUILT
        # data.json. Checking the input was checking a file that never carries
        # the field — a test that could only ever fail.
        f = ROOT / "pipeline" / "ui5-media" / "data.json"
        if not f.exists(): self.skipTest("review not built")
        D = json.load(open(f))
        F = self.flags()
        declared = {k for k, b in F["beats"].items() if b.get("wantsMediaKind")}
        briefs = {b["brief"] for b in D["briefs"]}
        carried = {b["brief"] for b in D["briefs"] if b.get("wantsKind")}
        missing = sorted((declared & briefs) - carried)
        self.assertEqual(missing, [],
                         f"declared on {missing} but the brief does not carry it")


class ProductionReadyIsAuthoritative(unittest.TestCase):
    """The user's lifecycle gate delivers identity and kind. Stop inferring them.

    50_COMPLETED/Production Ready is "the authoritative lifecycle-approved Media
    Library delivery" — 566 assets across 8 category folders, a By Person view
    with 38 named people, per-asset tags, and a verification block that checks
    every category's asset ids against its files.

    Before this, kind_of() INFERRED kind from tag phrases and a face count, and
    identity came from a loose contains-match. Both were best-effort against a
    library where 907 assets had provenance tags only. A manifest that states
    both, and verifies itself, outranks anything derived. LOG 0099.
    """

    MAN = ("/Users/dwaynetoler/Media Library/50_COMPLETED/"
           "Production Ready/manifest.json")

    def man(self):
        import os
        if not os.path.exists(self.MAN):
            self.skipTest("production-ready delivery not present")
        return json.load(open(self.MAN))

    def test_the_delivery_verifies_itself(self):
        # never trust a manifest that does not check its own claims
        v = self.man()["verification"]
        for cat, c in v["category_checks"].items():
            self.assertTrue(c["passed"], f"{cat} failed its own check")
            self.assertTrue(c["asset_ids_match"], f"{cat}: ids do not match files")
        # AMENDED 2026-09-26: this read v["cutout_glow_sets_match"] and broke when
        # the manifest regenerated at 05:24 without that key — the flag was absent,
        # not false, while the condition was plainly true in the same file. The
        # claim is checkable from the manifest's own categories, so it is CHECKED
        # here rather than read, which is also stronger: a computed answer beats a
        # self-report, and catches a manifest that disagrees with itself. LOG 0125.
        d = self.man()
        cut = {i["asset_id"] for i in d["categories"].get("Cutouts", [])}
        glow = {i["asset_id"] for i in d["categories"].get("Glow Cutouts", [])}
        self.assertEqual(cut, glow,
                         f"{len(cut - glow)} cutout-only, {len(glow - cut)} glow-only")
        if v.get("cutout_glow_sets_match") is not None:
            self.assertTrue(v["cutout_glow_sets_match"],
                            "the manifest says the sets differ but they match")
        self.assertTrue(v["protected_catalog_counts_unchanged"],
                        "the delivery changed the protected catalog")

    def test_an_unverified_delivery_fails_closed(self):
        import copy, media_candidates as M
        broken = copy.deepcopy(self.man())
        first = next(iter(broken["verification"]["category_checks"].values()))
        first["passed"] = False
        with self.assertRaises(ValueError):
            M.validate_delivery_manifest(broken)

    def test_the_selectable_pool_is_exactly_the_delivered_asset_set(self):
        """Lifecycle authority is a boundary, not a metadata overlay.

        A blocked, trashed or otherwise undelivered catalog row must not return
        to a beat merely because an older tag still matches its entity.
        """
        import media_candidates as M
        delivered = set(M.delivery())
        pool = set(M.load())
        self.assertEqual(pool, delivered,
                         f"pool has {len(pool - delivered)} undelivered and "
                         f"misses {len(delivered - pool)} delivered assets")

    def test_every_display_is_the_exact_approved_delivery_file(self):
        """The reviewed derivative, not another registered derivative, is used."""
        import media_candidates as M, os
        pool = M.load()
        wrong = []
        for aid, delivered in M.delivery().items():
            # A USER APPROVAL is admitted by delivery() but is not a delivery: it
            # confers no approved bytes, because nothing approved any (LOG 0119).
            # Holding it to this rule would make the user's own override look like
            # a defect.
            if delivered.get("userApproved"):
                continue
            path = delivered.get("path")
            if not path or aid not in pool or not os.path.exists(path):
                wrong.append(aid)
                continue
            if not os.path.samefile(pool[aid]["display"], path):
                wrong.append(aid)
        self.assertEqual(wrong, [],
                         f"{len(wrong)} assets do not use their approved bytes")

    def test_category_maps_onto_our_media_kinds(self):
        import media_candidates as M
        for cat, kind in M.CATEGORY_KIND.items():
            self.assertIn(kind, M.MEDIA_KINDS, f"{cat} -> {kind!r} is not a kind")
        self.assertEqual(set(M.CATEGORY_KIND), set(self.man()["categories"]),
                         "a delivered category has no kind mapping")

    def test_a_delivered_kind_beats_an_inferred_one(self):
        # an Article with a face in it is a DOCUMENT. Inference said person.
        import media_candidates as M
        rec = {"id": "x", "media_type": "image", "people": ["Drake"], "faces": 2,
               "tags": [], "captions": [], "derivatives": []}
        self.assertEqual(M.kind_of(rec), "person")
        self.assertEqual(M.kind_of(rec, delivered="document"), "document")

    def test_identity_aliases_resolve_to_the_roster(self):
        # the By Person folders carry informal and misspelled names
        import media_candidates as M
        for folder, want in (("macklamore", "Macklemore"), ("Nipsey", "Nipsey Hussle"),
                             ("Pusha", "Pusha T"), ("Busta", "Busta Rhymes"),
                             ("Freddie", "Freddie Gibbs"), ("Snoop", "Snoop Dogg")):
            self.assertEqual(M.resolve_identity(folder), want, folder)

    def test_unidentified_is_not_an_identity(self):
        import media_candidates as M
        self.assertIsNone(M.resolve_identity("_unidentified"))

    def test_delivered_identity_reaches_the_pool(self):
        import media_candidates as M
        pool = M.load()
        with_id = [r for r in pool.values() if r.get("delivered_identities")]
        self.assertTrue(with_id, "the delivery's identities are not loaded")
        # and Macklemore, a GAP in the media pass, is now findable
        out = M.resolve(["Macklemore"], pool=pool, wrong=set())
        self.assertTrue(out["individual"]["Macklemore"],
                        "Macklemore was delivered and is still a gap")

class TheSnapshotIsTheSameLibrary(unittest.TestCase):
    """A session with no Media Library mounted must resolve the SAME candidates.

    THE PROBLEM. 17 absolute paths under 3 local roots. A cloud session has none
    of them, so the deterministic layer — which never opens a pixel — cannot run
    off this machine at all. Measured 2026-09-25: the media is 11 GB, the metadata
    the code actually reads is 25 MB.

    WHY THIS IS THE RIGHT TEST. A fallback that answers with LESS is worse than
    one that fails, because a short candidate list is indistinguishable from a
    thin library, and the whole objective is landing the right media on the beat.
    So this does not assert "the snapshot loads" — it asserts the snapshot
    produces byte-identical ranked ids to the live catalog, per entity, in order.
    Written after a first version of this check compared res["candidates"], a key
    resolve() does not return, and passed on 0 == 0 for five artists.
    """
    NOLIB = None

    @classmethod
    def setUpClass(cls):
        import tempfile
        cls.NOLIB = tempfile.mkdtemp(prefix="astra-nolib-")

    def _run(self, snippet, env=None):
        import json, os, subprocess, sys
        e = dict(os.environ)
        e["PYTHONPATH"] = str(ROOT / "pipeline") + os.pathsep + e.get("PYTHONPATH", "")
        e.update(env or {})
        r = subprocess.run([sys.executable, "-c", snippet], capture_output=True,
                           text=True, env=e, cwd=str(ROOT))
        self.assertIn("@@", r.stdout, f"child failed:\n{r.stdout[-800:]}\n{r.stderr[-2000:]}")
        return json.loads(r.stdout.split("@@", 1)[1])

    SNIP = ('import sys, json; sys.path.insert(0, "pipeline")\n'
            'import media_candidates as M, paths as P\n'
            'rows = M.load()\n'
            'out = {"source": M.SOURCE, "pathsSays": P.source(),\n'
            '       "rows": len(rows), "ids": sorted(rows), "r": {},\n'
            '       "full": {k: {f: v[f] for f in sorted(v) if f != "_hay"}\n'
            '                for k, v in rows.items()},\n'
            '       "hay": {k: len(v["_hay"]) for k, v in rows.items()}}\n'
            'for ents in (["Drake"], ["Kendrick Lamar"], ["Nipsey Hussle"], ["Jay Rock"],\n'
            '             ["Drake", "Kendrick Lamar"]):\n'
            '    res = M.resolve(ents, pool=rows)\n'
            '    out["r"]["+".join(ents)] = {\n'
            '        "group": [c["id"] for c in res.get("group") or []],\n'
            '        "individual": {e: [c["id"] for c in v]\n'
            '                       for e, v in (res.get("individual") or {}).items()}}\n'
            'print("@@" + json.dumps(out))\n')

    def test_the_snapshot_is_not_stale(self):
        # The library is actively being tagged — +2,440 tags arrived between two
        # exports 30 minutes apart on 2026-09-25. Staleness is the expected
        # condition, not an exotic one, so it gets its own named test with a
        # one-line remedy. Before this it surfaced as a 2.3 MB assertEqual diff
        # on the equivalence test, which says nothing about what to do.
        import sqlite3
        import paths as PATHS
        snap = PATHS.snapshot()
        self.assertIsNotNone(snap, "no snapshot — run pipeline/export_library.py --write")
        db_path = PATHS.library_db()
        if not db_path:
            self.skipTest("no live library mounted to compare against")
        db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        live = {"assets": next(db.execute("select count(*) from assets"))[0],
                "tags": next(db.execute("select count(*) from tags"))[0]}
        have = {k: snap["_counts"][k] for k in ("assets", "tags")}
        self.assertEqual(have, live,
                         f"snapshot is STALE (taken {snap.get('_generatedAt')}): "
                         f"{have} vs live {live}. Run: "
                         "python3 pipeline/export_library.py --write")

    def test_a_snapshot_session_resolves_the_identical_candidates(self):
        live = self._run(self.SNIP)
        snap = self._run(self.SNIP, {"ASTRA_MEDIA_LIBRARY": self.NOLIB})
        # M.SOURCE is set by the reader that actually ran. Asserting
        # paths.source() instead let a build with a hardcoded library path pass
        # this while reading the live catalog — the two agreed by accident.
        self.assertEqual(live["source"], "live")
        self.assertEqual(snap["source"], "snapshot",
                         "the no-library run still read rows from the local catalog")
        self.assertEqual(snap["pathsSays"], "snapshot")
        self.assertEqual(live["ids"], snap["ids"], "the pools differ")
        compared = 0
        for k in live["r"]:
            compared += (len(live["r"][k]["group"])
                         + sum(len(v) for v in live["r"][k]["individual"].values()))
            self.assertEqual(live["r"][k], snap["r"][k],
                             f"{k} resolves differently from the snapshot")
        # the guard against the 0 == 0 pass that shipped the first version
        self.assertGreater(compared, 100,
                           "compared almost nothing — the queries came back empty")

        # EVERY FIELD OF EVERY ROW, not a sample. Added because deleting all
        # 12,517 library tag rows from the snapshot reader did NOT fail the
        # version above: the five probe queries match on `people` and delivered
        # identities and never read a tag, so a reader that silently dropped the
        # tags looked identical. Tags carry framing, grouping and most of the
        # match evidence, so that is the exact loss this whole test exists to
        # catch, and it slipped through a check that read "ALL IDENTICAL".
        if live["full"] != snap["full"]:
            diff = [k for k in live["full"] if live["full"][k] != snap["full"].get(k)]
            self.fail(f"{len(diff)} of {len(live['full'])} rows differ between the "
                      f"live catalog and the snapshot, e.g. {diff[:3]}. If the "
                      "library was tagged since the export, this is staleness, not "
                      "a reader defect — run pipeline/export_library.py --write and "
                      "see test_the_snapshot_is_not_stale.")
        self.assertEqual(live["hay"], snap["hay"], "the match haystacks differ")
        tagged = sum(len(r["tags"]) for r in live["full"].values())
        self.assertGreater(tagged, 3000,
                           f"only {tagged} tags in the compared pool — the "
                           "comparison is not exercising the tag surface")

    def test_the_snapshot_carries_the_verification_block_not_a_summary(self):
        # A flattened `verification_passed: true` would let the snapshot path pass
        # a gate the live path has to earn. The gate must be the SAME gate.
        import json
        import media_candidates as M
        import paths as PATHS
        snap = PATHS.snapshot()
        self.assertIsNotNone(snap, "no snapshot — run pipeline/export_library.py --write")
        d = snap.get("delivery")
        self.assertTrue(d, "the snapshot has no delivery")
        M.validate_delivery_manifest(d)          # raises if the block is missing
        v = d["verification"]
        self.assertEqual(set(v["category_checks"]), set(d["categories"]))
        # cutout_glow_sets_match is NOT asserted here. The manifest regenerated
        # 2026-09-26T05:24 dropped the flag entirely, and the validator now COMPUTES
        # the claim from the categories instead of reading it — 261 Cutouts, 261
        # Glow Cutouts, zero on either side alone. Asserting the flag would hold the
        # snapshot to a self-report the manifest no longer makes. LOG 0125.
        for key in ("person_view_covers_cutouts",
                    "protected_catalog_counts_unchanged", "source_media_unchanged"):
            self.assertIs(v.get(key), True, key)
        cut = {i["asset_id"] for i in d["categories"].get("Cutouts", [])}
        glow = {i["asset_id"] for i in d["categories"].get("Glow Cutouts", [])}
        self.assertEqual(cut, glow, "the snapshot's cutout and glow sets differ")

    def test_no_library_and_no_snapshot_raises_instead_of_returning_empty(self):
        # The one thing worse than a stale pool is an EMPTY pool reported as a
        # pool. Both absent must be an exception, never `{}`.
        out = self._run(
            'import sys, json; sys.path.insert(0, "pipeline")\n'
            'import media_candidates as M\n'
            'try:\n'
            '    M.load(); print("@@" + json.dumps({"raised": None, "msg": ""}))\n'
            'except Exception as e:\n'
            '    print("@@" + json.dumps({"raised": type(e).__name__, "msg": str(e)}))\n',
            {"ASTRA_MEDIA_LIBRARY": self.NOLIB,
             "ASTRA_SNAPSHOT": self.NOLIB + "/does-not-exist.json"})
        self.assertEqual(out["raised"], "FileNotFoundError",
                         "an absent library AND absent snapshot returned a pool")
        # and it must name the MISSING SOURCES. The first version of this passed
        # on an unrelated error from delivery(), which fires first and says the
        # manifest is missing — true, but it points at the wrong thing and left
        # the guard this test claims to cover unreachable.
        self.assertIn("no media source", out["msg"])
        self.assertIn("snapshot", out["msg"])

    def test_every_local_root_is_overridable(self):
        # 17 hardcoded paths were the actual blocker. Each root reads its env var.
        import os
        import paths as PATHS
        for var, fn in (("ASTRA_MEDIA_LIBRARY", PATHS.library_root),
                        ("ASTRA_POLISH", PATHS.polish_root),
                        ("ASTRA_SNAPSHOT", PATHS.snapshot_path)):
            before = fn()
            os.environ[var] = "/tmp/astra-override-probe"
            try:
                self.assertEqual(str(fn()), "/tmp/astra-override-probe",
                                 f"{var} is ignored")
            finally:
                del os.environ[var]
            self.assertEqual(fn(), before, f"{var} leaked after being unset")


class NoFileIsLostToAKeyCollision(unittest.TestCase):
    """An R2 key that two different files share loses one of them, silently.

    THE PROBLEM, measured 2026-09-25 before any upload: `media/<id>/<role><ext>`
    gave 2023 keys for 2275 file references, and 244 keys held more than one
    distinct file. output/cutouts and output/quality-cutouts are both
    derivative_type `cutout` — 440,621 and 1,074,025 bytes for one asset. Under
    one key the later upload wins, and which one that is depends on iteration
    order, so the better cutout can vanish without a message.

    WHY IT MATTERS TO THE OBJECTIVE. The key is how a cloud session reaches the
    pixels. A lost cutout is a candidate that cannot be shown on a beat, and the
    loss is invisible — the manifest still lists the asset.

    The first version dropped BOTH the harmless and the harmful case with
    `if k in seen: return`, and reported neither.
    """

    def _pool(self, tmp):
        import os
        def w(name, body):
            f = os.path.join(tmp, name)
            with open(f, "wb") as fh: fh.write(body)
            return f
        return {
            # same type, DIFFERENT bytes — must become two keys
            "aaa": {"id": "aaa", "display": w("a_disp.png", b"A" * 10),
                    "path": w("a_orig.jpg", b"O" * 10),
                    "derivatives": [{"type": "cutout", "path": w("a_c1.png", b"1" * 10)},
                                    {"type": "cutout", "path": w("a_c2.png", b"2" * 4000)}]},
            # same type, SAME bytes in two places — must collapse to one key
            "bbb": {"id": "bbb", "display": w("b_disp.png", b"B" * 10),
                    "path": w("b_orig.jpg", b"P" * 10),
                    "derivatives": [{"type": "preview", "path": w("b_p1.png", b"same" * 9)},
                                    {"type": "preview", "path": w("b_p2.png", b"same" * 9)}]},
        }

    def test_two_different_files_never_share_one_key(self):
        import tempfile
        import r2_sync as R
        with tempfile.TemporaryDirectory() as tmp:
            items, collisions = R.plan("originals", pool=self._pool(tmp))
        keys = [i["key"] for i in items]
        self.assertEqual(len(keys), len(set(keys)), "a key is used twice")
        cut = sorted(i["key"] for i in items if i["role"] == "cutout")
        self.assertEqual(len(cut), 2, f"a cutout was dropped: {cut}")
        self.assertEqual(len(collisions), 1, "the real collision was not reported")
        for k in cut:
            self.assertRegex(k, r"cutout-[0-9a-f]{8}\.png$",
                             "the split keys carry no content discriminator")

    def test_byte_identical_files_collapse_to_one_key(self):
        import tempfile
        import r2_sync as R
        with tempfile.TemporaryDirectory() as tmp:
            items, collisions = R.plan("originals", pool=self._pool(tmp))
        prev = [i for i in items if i["role"] == "preview"]
        self.assertEqual(len(prev), 1, "identical files were uploaded twice")
        self.assertEqual(prev[0].get("duplicates"), 1, "the collapse was not reported")
        # and a collapse is NOT a collision — it must not be flagged as one
        self.assertNotIn("preview", " ".join(k for k, _ in collisions))

    def test_the_display_tier_key_needs_no_content_hash(self):
        # display_path() returns exactly one file per asset, so the display tier
        # is collision-free and its key is derivable from the asset id alone.
        # That is what lets the UIs build a URL without a manifest lookup.
        import media_candidates as M
        import r2_sync as R
        items, collisions = R.plan("display")
        self.assertEqual(collisions, [], "the display tier collides")
        keys = [i["key"] for i in items]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(keys), len(M.load()), "an asset has no display key")
        for i in items[:50]:
            self.assertEqual(i["key"], R.key_for(i["asset_id"], "display", i["local"]),
                             "a display key is not derivable")

    def test_push_is_refused_without_configuration(self):
        """Spend is the user's decision. No credential, no upload, non-zero exit.

        The first version of this set ASTRA_R2_PROFILE to a bogus name, which did
        nothing once r2_sync read .env directly — so the test would have uploaded
        1.46 GB to the real bucket. It withholds the ENV FILE now, which is the
        actual credential source.
        """
        import subprocess
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as fh:
            fh.write("# deliberately empty\n")
            empty = fh.name
        e = dict(os.environ)
        e["ASTRA_ENV_FILE"] = empty
        r = subprocess.run([sys.executable, "pipeline/r2_sync.py", "--push"],
                           capture_output=True, text=True, cwd=str(ROOT), env=e)
        os.unlink(empty)
        self.assertEqual(r.returncode, 1, "a push with no credentials exited 0")
        self.assertIn("REFUSING to push", r.stdout)
        self.assertNotIn("sent", r.stdout.lower().replace("present", ""))

    def test_push_needs_confirm_as_well(self):
        # --push alone must not spend, even with every credential valid.
        import subprocess
        r = subprocess.run([sys.executable, "pipeline/r2_sync.py", "--push"],
                           capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(r.returncode, 1, "--push alone exited 0")
        self.assertIn("needs --confirm", r.stdout)


class EveryTemplatePreviewCarriesAPoster(unittest.TestCase):
    """A template shown without a poster is a black rectangle on the card.

    THE PROBLEM, measured 2026-09-25: 6 of 47 template previews in ui5-media had
    poster: None while their clip existed on disk. build_media_review's
    template_previews() read only .thumbcache and never fell back to the source,
    so beats 01-01, 06-06, 11-11a, 12-12a, 21-21a, 24-24, 27-27 and 28-28 showed
    nothing where the treatment should be. The user reported the template side of
    the review was wrong before this was found.

    WHY IT MATTERS. CLAUDE.md: "Every clip carries a thumbnail... a grid of them
    shows nothing and the page cannot be skimmed", and the poster is explicitly
    not a size lever. The beat's framing want comes FROM the chosen template, so a
    reviewer judging media against an invisible template is judging blind.
    """

    def test_no_preview_is_posterless_while_its_clip_exists(self):
        f = ROOT / "pipeline" / "ui5-media" / "data.json"
        if not f.exists(): self.skipTest("not built")
        D = json.load(open(f))
        tp = D.get("templatePreviews") or {}
        self.assertTrue(tp, "the review carries no template previews at all")
        sys.path.insert(0, str(ROOT / "match-trial"))
        import candidates as C
        pool = {r["id"]: r for r in C.load(content_class="*")}
        cap = C._capability()
        recoverable = []
        for tid, item in tp.items():
            if (item or {}).get("poster"): continue
            src = (pool.get(tid) or {}).get("clip")
            still = (cap.get(tid) or {}).get("still_path")
            if (src and os.path.exists(src)) or (still and os.path.exists(still)):
                recoverable.append(tid)
        self.assertEqual(recoverable, [],
                         f"{len(recoverable)} template(s) render as a black "
                         f"rectangle although a frame is extractable: {recoverable}")

    def test_it_recovers_a_poster_with_an_EMPTY_cache(self):
        """The real test, because a warm cache hides the defect.

        The first version of this rebuilt the review and checked the output. But
        the fix writes the recovered posters INTO .thumbcache, so the cache-only
        code then passes too — the test stopped being able to fail the moment the
        fix ran once, and would only have caught this on a fresh machine. This
        points template_previews at an empty cache directory instead, which is the
        state any clone starts in.
        """
        import importlib, tempfile
        sys.path.insert(0, str(ROOT / "pipeline"))
        bmr = importlib.import_module("build_media_review")
        briefs = json.load(open(ROOT / "grammar" / "media-briefs.json"))["briefs"]
        # one brief whose template has a clip on disk and is worth a poster
        sys.path.insert(0, str(ROOT / "match-trial"))
        import candidates as C
        pool = {r["id"]: r for r in C.load(content_class="*")}
        pick = None
        for b in briefs:
            for t in (b.get("selectedTemplates") or []):
                c = (pool.get(t["id"]) or {}).get("clip")
                if c and os.path.exists(c):
                    pick = b
                    break
            if pick: break
        self.assertIsNotNone(pick, "no brief has a template with a clip on disk")
        with tempfile.TemporaryDirectory() as cache, tempfile.TemporaryDirectory() as ui:
            old_cache, old_ui = bmr.TEMPLATE_CACHE, bmr.UI
            bmr.TEMPLATE_CACHE = pathlib.Path(cache)
            bmr.UI = pathlib.Path(ui)
            try:
                out = bmr.template_previews([pick])
            finally:
                bmr.TEMPLATE_CACHE, bmr.UI = old_cache, old_ui
        want = [t["id"] for t in pick["selectedTemplates"]
                if (pool.get(t["id"]) or {}).get("clip")
                and os.path.exists(pool[t["id"]]["clip"])]
        for tid in want:
            self.assertTrue((out.get(tid) or {}).get("poster"),
                            f"{tid} came back posterless from an empty cache "
                            "although its clip is on disk")


class AProjectNameIsNotEvidence(unittest.TestCase):
    """A folder name must never make an asset a candidate for the artist in it.

    USER RULING 2026-09-25: "Drake Year 17 - Instagram. shouldnt be a tag. that
    add garbage to the canidates. i seen this frst hand. projects shouldnt be tags
    at all."

    Measured: 2,254 of 14,957 tag rows are an ingestion project name; 825 of them
    sit on assets in the selectable pool, 12% of that pool's tags. The project
    `Drake Year 17 - Instagram` alone put 96 assets into reach of any Drake query
    through the normalised contains rule.

    HONEST SCOPE. On the library and briefs as they stand this removes ZERO
    candidates, because resolve() computes `primary or all_matches` and every
    entity currently has primary evidence, so the weak tier is never consulted.
    It bites in the GAP case — an entity with no tag, face or delivered identity —
    which is exactly where a wrong candidate does the most damage, because there is
    nothing better beside it for the reviewer to prefer. These tests therefore
    exercise the weak tier directly instead of asserting a count that does not move.
    """

    def _asset(self, aid, tags, captions=(), people=(), delivered=()):
        import media_candidates as M
        r = {"id": aid, "media_type": "image", "ext": ".jpg", "width": 800,
             "height": 800, "duration": None, "path": f"/x/{aid}.jpg",
             "tags": [{"tag": t, "source": s} for t, s in tags],
             "people": list(people), "captions": list(captions),
             "derivatives": [], "faces": 0,
             "delivered_identities": list(delivered), "delivered_kind": "person",
             "delivered_categories": ["Full Images"]}
        r["framing"] = None; r["is_group"] = False; r["has_cutout"] = False
        r["kind"] = "person"; r["display"] = r["path"]
        return r

    def test_a_project_tag_alone_makes_no_candidate(self):
        import media_candidates as M
        proj = sorted(M.projects())
        self.assertTrue(proj, "no ingestion projects were derived from the library")
        # the real project name the user named, in its real stored form
        real = next((p for p in proj if "drakeyear17" in p), None)
        self.assertIsNotNone(real, f"the named project is not in the derived set: {proj[:5]}")
        rec = self._asset("p1", [("Drake Year 17 - Instagram", "ingest"),
                                 ("Instagram", "ingest")])
        self.assertIsNone(M._evidence(rec, "Drake"),
                          "a project folder name is being treated as evidence of Drake")
        self.assertFalse(M.matches(rec, "Drake", set()))
        # and it must not reach the slate even when Drake has nothing else
        out = M.resolve(["Drake"], pool={"p1": rec}, wrong=set())
        self.assertEqual([c["id"] for c in out["individual"]["Drake"]], [],
                         "a project-only asset reached the slate in the gap case")
        self.assertIn("Drake", out["gaps"], "the gap was hidden rather than reported")

    def test_a_non_project_ingest_tag_keeps_its_EXISTING_weight(self):
        """The ruling removes project names. It does not re-weight anything else.

        An earlier version of this asserted ("tag", "Drake") — i.e. that every
        non-project ingest tag was promoted to primary evidence. That broke
        MediaEvidenceUsesARealFallbackBoundary, and correctly: an unregistered
        collection-style tag like "Jay-Z fan collection" is not in
        ingestions.project, so promotion made it primary identity evidence for
        Jay-Z. Stronger than before, on the strength of a folder name — the exact
        failure the ruling exists to stop.
        """
        import media_candidates as M
        rec = self._asset("p2", [("Drake", "ingest"), ("Headshot", "ingest")])
        ev = M._evidence(rec, "Drake")
        self.assertEqual(ev, ("project", "Drake"),
                         "a non-project ingest tag changed weight")
        self.assertNotIn(ev[0], M.PRIMARY_EVIDENCE)
        # and a registered project name yields nothing at all, at any weight
        rec2 = self._asset("p3", [("Drake Year 17 - Instagram", "ingest")])
        self.assertIsNone(M._evidence(rec2, "Drake"))

    def test_the_project_set_is_derived_not_hardcoded(self):
        # 19 of the 30 current projects are dated batch names, so a hand-written
        # deny list goes stale on the next import.
        import media_candidates as M
        src = (ROOT / "pipeline" / "media_candidates.py").read_text()
        self.assertIn("from ingestions", src.replace("\n", " "),
                      "the project set is not derived from ingestions.project")
        self.assertGreater(len(M.projects()), 20)

    def test_a_suppressed_claim_cannot_return_through_the_caption(self):
        # asset 54e95e16b8 is a Kendrick Lamar birthday post that name-drops Jay-Z
        # and Kanye West. The library suppressed both from caption-entity; the raw
        # caption still says both, so dropping the tag alone let the identical
        # claim back in.
        import media_candidates as M
        claims = M.suppressed_claims()
        self.assertTrue(claims, "the library's tag_suppressions are not being read")
        hit = [(a, e) for a, e in claims if e == M.norm("Jay-Z")]
        self.assertTrue(hit, "the Jay-Z suppression is not among the claims")
        aid = hit[0][0]
        rec = self._asset(aid, [("Compton", "caption-location")],
                          captions=["... joining the ranks of Hip Hop entrepreneurs "
                                    "such as Jay-Z and Kanye West ..."])
        self.assertIsNone(M._evidence(rec, "Jay-Z"),
                          "a suppressed entity came back via the raw caption")
        # an entity the library did NOT suppress on that asset is unaffected
        self.assertEqual(M._evidence(rec, "Compton"), ("tag", "Compton"))

    def test_tag_suppressions_are_historical_so_no_load_filter_is_kept(self):
        """Guards the FINDING, and would fail if the library changed behaviour.

        A filter dropping suppressed tags at load was written first and then
        deleted: measured 2026-09-25, 0 of the 39 tag_suppressions rows still exist
        in `tags`, so it removed nothing and its test could not fail. If the
        library ever starts leaving suppressed tags in place, this fails and the
        filter becomes necessary — which is the only reason to assert it.
        """
        import sqlite3
        import paths as PATHS
        if not PATHS.library_db(): self.skipTest("no live library")
        db = sqlite3.connect(f"file:{PATHS.library_db()}?mode=ro", uri=True)
        still = list(db.execute(
            "select s.asset_id, s.tag from tag_suppressions s join tags t "
            "on t.asset_id=s.asset_id and t.tag=s.tag and t.source=s.source"))
        self.assertEqual(still, [],
                         f"{len(still)} suppressed tag(s) are back in `tags` — "
                         "_rows_live now needs the suppression filter that was "
                         "removed as a no-op")


class AUserTagIsANamedBinding(unittest.TestCase):
    """The user tags an asset; that is evidence, and it must carry their words.

    USER RULING 2026-09-25: "go ahead and tag big sean." Asset 514d9283165f is
    their recorded pick for Big Sean on beat 16-16, but its only machine evidence
    was a caption that is an import filename — LOG 0104's gate correctly held it
    out of the primary tier. The asset already carried a tag `sean`, which never
    matched: the contains rule is `entity in tag`, and "bigsean" is not inside
    "sean". That asymmetry is deliberate — a bare `sean` could be Sean Paul.

    A TAG, NOT AN EXCEPTION. An exception fixes one card on one beat. A tag gives
    the asset real evidence and makes it findable on every future beat naming him.
    It lives in grammar/media-tags.json because the Media Library is read-only from
    this side, the same split as media-corrections.json.
    """

    def test_the_users_tag_becomes_primary_evidence(self):
        """Asserts the OUTCOME, not which tag delivered it.

        The first version asserted _evidence == ("tag", "Big Sean") — the exact
        string of the tag added here. That broke the moment bidirectional matching
        landed (LOG 0115), because the asset's own `sean` tag now reaches Big Sean
        directly and is found first. The test was right about the behaviour and
        wrong to pin the mechanism.
        WORTH RECORDING: this user tag is now REDUNDANT. It was a workaround for a
        matching bug, and the bug is fixed. It is kept because the user asked for it
        by name and it carries their words, but nothing depends on it.
        """
        import media_candidates as M
        rows = M.load()
        aid = "514d9283165faa83445e507f"
        self.assertIn(aid, rows, "the Big Sean pick is not in the pool")
        ev = M._evidence(rows[aid], "Big Sean")
        self.assertIsNotNone(ev, "the Big Sean pick has no evidence at all")
        self.assertIn(ev[0], M.PRIMARY_EVIDENCE)
        offered = {c["id"] for c in
                   M.resolve(["Big Sean"], pool=rows)["individual"].get("Big Sean", [])}
        self.assertIn(aid, offered, "the user's pick is still not offered")
        # and the sidecar is still well-formed and still names this asset
        self.assertIn(aid, M.user_tags())

    def test_a_user_tag_without_the_users_words_is_refused(self):
        # A named binding records their words (CLAUDE.md, HARD RULE). A tag with no
        # words is indistinguishable from one Claude invented.
        import importlib, json as _json, tempfile
        import media_candidates as M
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            _json.dump({"tags": [{"assetId": "x", "tag": "Drake"}]}, fh)
            bad = fh.name
        old, M._UTAGS = M.USER_TAGS, None
        M.USER_TAGS = pathlib.Path(bad)
        try:
            with self.assertRaises(ValueError) as cm:
                M.user_tags()
            self.assertIn("words", str(cm.exception))
        finally:
            M.USER_TAGS, M._UTAGS = old, None
            os.unlink(bad)

    def test_a_user_tag_on_an_undelivered_asset_is_a_finding(self):
        # Silently ignoring it would hide that they tagged something the delivery
        # boundary excludes — the same class as the 2 picks in LOG 0107.
        import json as _json, tempfile
        import media_candidates as M
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            _json.dump({"tags": [{"assetId": "deadbeef" * 3, "tag": "Drake",
                                  "words": "test"}]}, fh)
            bad = fh.name
        old, M._UTAGS = M.USER_TAGS, None
        M.USER_TAGS = pathlib.Path(bad)
        try:
            with self.assertRaises(ValueError) as cm:
                M.load()
            self.assertIn("absent from the selectable pool", str(cm.exception))
        finally:
            M.USER_TAGS, M._UTAGS = old, None
            os.unlink(bad)


class TheR2ManifestMatchesWhatWasUploaded(unittest.TestCase):
    """Offline: the manifest must describe the plan it claims to have sent.

    NO NETWORK IN THIS TEST. The live verification was done once, at upload:
    557 of 557 objects, 1.46 GB, zero missing, zero size mismatches, zero extras,
    and one object fetched over the public URL returning 200 and its exact byte
    count. Re-running that on every suite invocation would make the suite slow and
    dependent on someone else's uptime.

    What this guards is the thing that CAN drift silently: the manifest is what a
    review UI resolves an asset id through, so a manifest disagreeing with the plan
    means a card pointing at a key that is not there.
    """

    def test_every_planned_display_asset_has_a_manifest_key(self):
        f = ROOT / "grammar" / "r2-manifest.json"
        if not f.exists(): self.skipTest("nothing uploaded yet")
        m = json.load(open(f))
        sys.path.insert(0, str(ROOT / "pipeline"))
        import r2_sync as R
        items, collisions = R.plan("display")
        self.assertEqual(collisions, [])
        planned = {i["asset_id"]: i["key"] for i in items}
        # STALE AND WRONG ARE DIFFERENT. The pool grows when the user approves an
        # asset, so a manifest that predates the approval is missing keys and the
        # remedy is one push. A manifest that maps an asset to a DIFFERENT key than
        # the plan is a card pointing at the wrong bytes, and that is a defect.
        for aid, key in m["keys"].items():
            if aid in planned:
                self.assertEqual(key, planned[aid],
                                 f"{aid[:12]} is uploaded under the wrong key")
        missing = sorted(set(planned) - set(m["keys"]))
        self.assertEqual(missing, [],
                         f"{len(missing)} planned asset(s) are not uploaded — run "
                         "python3 pipeline/r2_sync.py --push --confirm")
        self.assertEqual(m["_failed"], 0, "the upload reported failures")
        self.assertEqual(m["_sent"] + m["_skipped"], len(planned))

    def test_the_manifest_key_is_derivable_from_the_asset_id(self):
        # This is what lets a UI build a URL without carrying a lookup table.
        f = ROOT / "grammar" / "r2-manifest.json"
        if not f.exists(): self.skipTest("nothing uploaded yet")
        m = json.load(open(f))
        for aid, key in list(m["keys"].items())[:50]:
            self.assertTrue(key.startswith(f"media/{aid}/display."),
                            f"{key} is not derivable from {aid}")

    def test_the_public_base_is_recorded(self):
        f = ROOT / "grammar" / "r2-manifest.json"
        if not f.exists(): self.skipTest("nothing uploaded yet")
        m = json.load(open(f))
        self.assertTrue(m.get("_publicBase", "").startswith("https://"),
                        "no public base url recorded — a UI cannot build a URL")

    def test_a_public_fetch_sends_a_browser_user_agent(self):
        # pub-*.r2.dev is behind Cloudflare bot protection: Python-urllib's default
        # agent gets 403 "error code: 1010", which reads exactly like the bucket
        # not being public and sends the reader after the wrong bug.
        src = (ROOT / "pipeline" / "r2_client.py").read_text()
        self.assertIn("BROWSER_UA", src)
        fn = src.split("def fetch_public", 1)[1].split("\n\n", 1)[0]
        self.assertIn("User-Agent", fn)


class TheBeatsOwnWordsRankCandidates(unittest.TestCase):
    """An entity match says WHO. It never says what the beat is about.

    THE PROBLEM, measured 2026-09-25 and reported by the user first: beat 15-15 is
    "In 2010, XXL offered him a spot on the Freshman cover." The XXL cover asset is
    correctly tagged — 2010, xxl, freshmen, magazine cover — and it came back as
    candidate 124 of 127 for Drake, 96 places below a slate that shows 28. The user:
    "we have the magazine referenced in the media library somewhere". It was there
    the whole time; nothing in the ranking knew the beat was ABOUT XXL, only that
    it mentioned Drake, and 127 assets mention Drake.

    THE SIGNAL IS LITERAL, NOT SEMANTIC. Count the words the beat's quote and the
    asset's tags share. No model, no embedding, reproducible. Measured across the
    127: the cover scores 3 and the next best scores 1, with 111 scoring zero.

    IT RANKS, IT NEVER EXCLUDES — the standing rule. A zero-overlap asset keeps its
    place behind the ones that overlap; it is not removed. Project names are
    excluded from the comparison for the same reason they are excluded from
    evidence (LOG 0109): a batch folder shares words with a beat by accident.
    """

    def test_a_beat_about_xxl_ranks_THE_COVER_THE_USER_NAMED_first(self):
        """Pinned to the user's ruling, not to Claude's guess.

        The first version asserted f2b1dd416a43 — the Drake and Nicki duo cover —
        because that is what the ranking surfaced when only it was tagged `drake`.
        LOG 0113 flagged at the time that it was probably the wrong cover, and it
        was: the user named 2fad290bd62e, the 2010 Freshman cover he is NOT on, and
        ruled that Drake and Nicki be tagged on both as a CONNECTION (LOG 0118).
        The ranking was always right; the asset it could reach was not.
        """
        import media_candidates as M
        rows = M.load()
        briefs = json.load(open(ROOT / "grammar" / "media-briefs.json"))["briefs"]
        b = next(x for x in briefs if x["brief"] == "15-15")
        named = json.load(open(ROOT / "grammar" / "xxl-covers.json"))["covers"]
        want = next(c["assetId"] for c in named
                    if c["issue"] == "2010 XXL Freshman cover")
        self.assertIn(want, rows, "the cover the user named is not in the pool")
        ids = [c["id"] for c in
               M.resolve(["Drake"], pool=rows, quote=b["quote"])["individual"]["Drake"]]
        self.assertIn(want, ids, "the named cover is not even a candidate")
        rank = ids.index(want) + 1
        self.assertEqual(rank, 1,
                         f"the cover the user named ranks {rank} of {len(ids)}")

    def test_it_ranks_and_never_excludes(self):
        import media_candidates as M
        rows = M.load()
        plain = M.resolve(["Drake"], pool=rows)["individual"]["Drake"]
        ranked = M.resolve(["Drake"], pool=rows,
                           quote="In 2010, XXL offered him a spot on the Freshman "
                                 "cover.")["individual"]["Drake"]
        self.assertEqual(sorted(c["id"] for c in plain),
                         sorted(c["id"] for c in ranked),
                         "the quote signal dropped a candidate instead of reordering")

    def test_a_project_name_cannot_score(self):
        # "Drake Year 17 - Instagram" shares `drake` and `17` with half the script.
        import media_candidates as M
        rec = {"id": "x", "tags": [{"tag": "Drake Year 17 - Instagram",
                                    "source": "ingest"}], "captions": []}
        self.assertEqual(M.quote_overlap("Drake in year seventeen, 17 years in",
                                         rec), 0)

    def test_no_quote_changes_nothing(self):
        import media_candidates as M
        rows = M.load()
        a = [c["id"] for c in M.resolve(["Drake"], pool=rows)["individual"]["Drake"]]
        b = [c["id"] for c in M.resolve(["Drake"], pool=rows, quote="")
             ["individual"]["Drake"]]
        self.assertEqual(a, b, "an absent quote must be a no-op, not a reshuffle")


class TagMatchingRunsBothDirections(unittest.TestCase):
    """A shorter tag must reach a longer entity name, without guessing.

    USER RULING 2026-09-26: "we need more generous tag matching, shouldnt be case
    sensitive and should be contains, not exact match."

    It was already case-insensitive and already contains — but one way round only,
    entity inside tag. So norm("J. Cole") = "jcole" never matched the tag `cole`,
    and the 2010 XXL Freshman cover, whose OCR tags are `cole` and `nipsey`,
    reached NO beat in the entire script (LOG 0114). Third instance this session of
    an asset present, correctly machine-tagged, and unreachable.

    THE REVERSE DIRECTION IS THE DANGEROUS ONE, so it is constrained twice:
      TOKENS, NOT SUBSTRINGS. `rick` is inside `kendricklamar`; a raw reverse
        substring puts a Rick Ross tag on Kendrick Lamar.
      ROSTER-UNIQUE TOKENS ONLY. Any token at a length floor brings `jay` to Jay
        Rock on 72 assets, `lil` to Lil Baby on 10, `big` to Big Sean on 9 — the
        exact tokens entities.py refuses to resolve because they belong to several
        roster names. No length constant appears anywhere; the roster decides.
    Measured over the 25 entities in this script: +32 candidates, all correct.
    """

    def _rec(self, tags):
        return {"id": "t", "tags": [{"tag": t, "source": "subject-tag"} for t in tags],
                "people": [], "captions": [], "delivered_identities": []}

    def test_a_partial_name_tag_now_reaches_the_full_entity(self):
        import media_candidates as M
        self.assertEqual(M._evidence(self._rec(["cole"]), "J. Cole"), ("tag", "cole"))
        self.assertEqual(M._evidence(self._rec(["nipsey"]), "Nipsey Hussle"),
                         ("tag", "nipsey"))
        self.assertEqual(M._evidence(self._rec(["KENDRICK"]), "Kendrick Lamar"),
                         ("tag", "KENDRICK"))   # case-insensitive, as asked

    def test_it_never_matches_a_substring_across_a_name_boundary(self):
        # `rick` sits inside `kendricklamar`. Tokens stop it; raw contains does not.
        import media_candidates as M
        self.assertIsNone(M._evidence(self._rec(["Rick"]), "Kendrick Lamar"))
        self.assertIsNone(M._evidence(self._rec(["Rick Ross"]), "Kendrick Lamar"))

    def test_an_ambiguous_token_still_refuses_to_guess(self):
        # `jay` belongs to Jay Rock AND Jay-Z; `lil` and `big` to many. Guessing
        # puts the wrong person on screen, the one failure review cannot correct.
        import media_candidates as M
        for tok, ent in (("jay", "Jay Rock"), ("lil", "Lil Baby"),
                         ("big", "Big Sean"), ("kid", "Kid Cudi")):
            self.assertIsNone(M._evidence(self._rec([tok]), ent),
                              f"the ambiguous token {tok!r} resolved to {ent}")

    def test_a_content_class_word_is_not_a_name(self):
        # "Article Or Post" put `post` on Post Malone across 48 assets.
        import media_candidates as M
        self.assertTrue(M.is_class_tag("Article Or Post"))
        self.assertIsNone(M._evidence(self._rec(["Article Or Post"]), "Post Malone"))
        self.assertIsNone(M._evidence(self._rec(["Social Post"]), "Post Malone"))

    def test_the_2010_freshman_cover_now_reaches_a_beat(self):
        # The asset the user identified, which matched nothing before this.
        import media_candidates as M
        rows = M.load()
        aid = next((k for k in rows if k.startswith("2fad290bd62e")), None)
        self.assertIsNotNone(aid, "the 2010 Freshman cover is not in the pool")
        for ent in ("J. Cole", "Nipsey Hussle"):
            got = {c["id"] for c in
                   M.resolve([ent], pool=rows)["individual"].get(ent, [])}
            self.assertIn(aid, got, f"the 2010 cover does not reach {ent}")

    def test_the_contamination_it_would_have_caused_did_not_happen(self):
        # Jay Rock and Post Malone are the two entities the rejected designs broke.
        import media_candidates as M
        rows = M.load()
        self.assertLessEqual(
            len(M.resolve(["Jay Rock"], pool=rows)["individual"]["Jay Rock"]), 6,
            "Jay Rock picked up the ambiguous `jay` token")
        self.assertLessEqual(
            len(M.resolve(["Post Malone"], pool=rows)["individual"]["Post Malone"]), 8,
            "Post Malone picked up `post` from a content-class tag")


class ASpatialNodeHoldsAPersonNotAnArticle(unittest.TestCase):
    """A marker on a stem is a person. It was being offered memes.

    USER RULING, brief 28-28, 2026-09-25: "memes and articles shouldnt be here.
    image tags need a way to match template capability. it should only be quarter,
    headshot or no no size specified images all but out, available here. spatial
    needs only those for the noe." And earlier: "all spatials plot people", "each
    node on top of a stick will be a headshot or quarter img of an artist".

    Measured: the 6 cinematic_3d templates carry a FRAMING rule from those same
    words — headshot, quarter — and no KIND rule at all, so kind_wanted() returned
    () and kfit() was a no-op. Beat 28-28's Drake tier came back 28 cards: 18
    document, 5 artwork, 5 person.

    RANKS, NEVER EXCLUDES. A document is not removed; it sorts behind every person
    and every asset whose kind is unknown, which pushes it off the 16-card window
    without hiding it from a reviewer who goes looking.
    """

    def test_a_spatial_template_wants_a_person(self):
        import media_candidates as M
        for tid in ("truth-cohort-attrition", "two-floors", "truth-rank-fall"):
            self.assertEqual(M.kind_wanted(tid, "cinematic_3d"), ("person",),
                             f"{tid} declares no kind")

    def test_the_rule_quotes_the_user(self):
        # A factual claim about a template belongs in the register with its source,
        # never as a bare constant (CLAUDE.md).
        rules = json.load(open(ROOT / "grammar" / "media-kind-rules.json"))
        why = ((rules.get("byKind") or {}).get("cinematic_3d") or {}).get("why", "")
        self.assertIn("memes and articles", why,
                      "the spatial kind rule does not carry the user's words")

    def test_beat_28_28_stops_leading_with_documents(self):
        import media_candidates as M
        rows = M.load()
        briefs = json.load(open(ROOT / "grammar" / "media-briefs.json"))["briefs"]
        b = next(x for x in briefs if x["brief"] == "28-28")
        wants = tuple(sorted({f for t in b["selectedTemplates"]
                              for f in M.framing_wanted(t["id"], t.get("kind"))}))
        kinds = tuple(sorted({k for t in b["selectedTemplates"]
                              for k in M.kind_wanted(t["id"], t.get("kind"))}))
        self.assertEqual(kinds, ("person",), "28-28 still wants no particular kind")
        out = M.resolve(b["entities"], pool=rows, wants=wants, kinds=kinds,
                        quote=b["quote"])
        top = out["individual"]["Drake"][:8]
        self.assertTrue(top, "no Drake candidates at all")
        docs = [c for c in top if (c.get("kind") or M.kind_of(c)) == "document"]
        self.assertEqual(docs, [],
                         f"{len(docs)} of the first 8 cards are still documents")

    def test_a_document_is_ranked_last_not_deleted(self):
        # The standing rule is rank, never exclude — the library must stay visible.
        import media_candidates as M
        rows = M.load()
        plain = {c["id"] for c in
                 M.resolve(["Drake"], pool=rows)["individual"]["Drake"]}
        ranked = {c["id"] for c in
                  M.resolve(["Drake"], pool=rows, kinds=("person",))
                  ["individual"]["Drake"]}
        self.assertEqual(plain, ranked, "the kind rule DELETED candidates")


class AFreshmanCoverIsNotAStandardCover(unittest.TestCase):
    """OCR reads every word on a page, including the ones that are not about it.

    USER 2026-09-26: "2010 xxl freshman cover is different fron 2010 xxl cover...
    theyre on the standard but the beat calls for freshman cover."

    Measured before the fix: all three XXL assets scored IDENTICALLY, 3 each, on
    ['2010','xxl'], for every beat that asks for one of them. Two causes, both the
    OCR being faithful to the page rather than wrong:
      EVERY cover was tagged BOTH 2009 and 2010 — each issue prints the other year
        somewhere on it.
      The STANDARD 2010 issue was tagged `freshmen`, because its cover lines
        mention the class. True text, false metadata.
    And `freshman` never met `freshmen` regardless: the stemmer strips a trailing
    `s`, and that pair differs by a vowel. It is an irregular plural, so it is
    declared in QUOTE_SYNONYMS rather than stemmed — a stemmer loose enough to fold
    it would mangle names.
    """

    def _cover(self, issue):
        import json as _j
        for c in _j.load(open(ROOT / "grammar" / "xxl-covers.json"))["covers"]:
            if c["issue"] == issue: return c["assetId"]
        self.fail(f"no cover recorded as {issue!r}")

    def test_freshman_and_freshmen_are_the_same_word(self):
        import media_candidates as M
        self.assertEqual(M._qtok("Freshman cover"), M._qtok("freshmen covers"))

    def test_the_standard_cover_no_longer_claims_to_be_a_freshman_cover(self):
        import media_candidates as M
        rows = M.load()
        std = self._cover("Drake and Nicki Minaj duo cover")
        tags = {M.norm(t["tag"]) for t in rows[std]["tags"]}
        self.assertNotIn("freshmen", tags, "the standard issue still claims freshmen")
        self.assertNotIn("2009", tags, "the 2010 standard issue still claims 2009")

    def test_each_freshman_beat_ranks_its_own_year_first(self):
        import media_candidates as M
        rows = M.load()
        briefs = {b["brief"]: b for b in
                  json.load(open(ROOT / "grammar" / "media-briefs.json"))["briefs"]}
        for beat, ent, issue in (("15-15", "Drake", "2010 XXL Freshman cover"),
                                 ("02-02a", "Curren$y", "2009 XXL Freshman cover")):
            want = self._cover(issue)
            b = briefs[beat]
            ids = [c["id"] for c in M.resolve([ent], pool=rows, quote=b["quote"])
                   ["individual"].get(ent, [])]
            self.assertIn(want, ids, f"{issue} is not a candidate on {beat}")
            self.assertEqual(ids.index(want) + 1, 1,
                             f"{beat} does not rank {issue} first")

    def test_the_standard_cover_scores_below_the_freshman_one(self):
        import media_candidates as M
        rows = M.load()
        b = next(x for x in json.load(open(ROOT / "grammar" / "media-briefs.json"))
                 ["briefs"] if x["brief"] == "15-15")
        fresh = M.quote_overlap(b["quote"], rows[self._cover("2010 XXL Freshman cover")],
                                ("Drake",))
        std = M.quote_overlap(b["quote"],
                              rows[self._cover("Drake and Nicki Minaj duo cover")],
                              ("Drake",))
        self.assertGreater(fresh, std,
                           "the standard cover still scores as high as the Freshman one")


class AnApprovalAdmitsAndNeverDelivers(unittest.TestCase):
    """The user can wave an asset past their gate. It is still not a delivery.

    USER 2026-09-26: "pass both wiz and kendrick in, theyre approved, anyone else
    gated is approved too", then the correction: "wait, i meant who was with wiz and
    kendrick gated you said 8. not a full 100+ approval." Claude had read the first
    as all 256 gate-blocked assets and admitted 247 of them.
    """

    def test_it_is_scoped_to_the_eight_not_the_whole_gate(self):
        d = json.load(open(ROOT / "grammar" / "approved-overrides.json"))
        self.assertEqual(len(d["approved"]), 8,
                         "the approval is not scoped to the eight the user meant")
        reasons = {r for a in d["approved"] for r in a["gateSaid"]}
        self.assertEqual(reasons,
                         {"no current registered cutout has a passing pre-clean "
                          "quality receipt"},
                         "the approval reaches assets gated for another reason")

    def test_an_approved_asset_carries_no_delivered_identity(self):
        # The delivery is what confers identity, kind and category. An approval is
        # explicitly not a delivery, so it must confer none of them.
        import media_candidates as M
        rows = M.load()
        d = json.load(open(ROOT / "grammar" / "approved-overrides.json"))
        for a in d["approved"]:
            r = rows.get(a["assetId"])
            if not r: continue
            self.assertEqual(r.get("delivered_identities") or [], [],
                             f"{a['assetId'][:12]} was given a delivered identity")
            self.assertEqual(r.get("delivered_categories") or [], [])

    def test_both_of_the_users_blocked_picks_are_in_the_pool(self):
        import media_candidates as M
        rows = M.load()
        for a8, who in (("4330073a1f5a", "Wiz Khalifa"), ("07e917c62e76", "Kendrick")):
            self.assertTrue(any(k.startswith(a8) for k in rows),
                            f"the {who} pick is still outside the pool")

    def test_a_rejected_cutout_is_flagged_not_hidden(self):
        # 3 of the 8 had their cutout REJECTED, not merely unreviewed. The asset is
        # admitted; the bad derivative must stay identifiable.
        d = json.load(open(ROOT / "grammar" / "approved-overrides.json"))
        rejected = [a for a in d["approved"] if a.get("cutoutRejected")]
        self.assertEqual(len(rejected), 3)
        for a in rejected:
            self.assertEqual(a["cutoutReview"], "reject")


class ASlotIsAnEntityNotARank(unittest.TestCase):
    """The join: which asset fills which slot, per beat, per chosen template.

    THE GAP, measured 2026-09-26: 19 of 40 beats carried BOTH a template pick and
    media picks, and nothing in the tree put them together. shotlist.py is
    template-only, build_media_review.py is media-only. The one artifact the whole
    system exists to produce did not exist.

    THE FIRST VERSION ASSIGNED BY FRAMING ALONE and was wrong in a way that looked
    fine: beat 20-20 is "Travis Scott, sixty-seven billion. Kendrick, fifty-seven.
    Post Malone, fifty-six. Future, fifty-four" against a five-bar list. The slot
    order IS the data order, so ranking by framing put Kendrick's photo on Travis's
    bar. Picks already carry their entity in the tier key, so the mapping was free
    and I had simply not used it.

    IT PROPOSES, IT DOES NOT DECIDE. The user pairs in the UI and their pairing
    outranks this, on the same standing as a pick.
    """

    def _pairings(self):
        f = ROOT / "grammar" / "pairings.json"
        if not f.exists(): self.skipTest("not built")
        return json.load(open(f))

    def test_each_slot_names_the_entity_it_serves(self):
        d = self._pairings()
        b = d["beats"].get("20-20")
        self.assertIsNotNone(b, "beat 20-20 has no pairing")
        p = next((x for x in b["proposed"] if x["templateId"] == "32_record_height_bars"), None)
        self.assertIsNotNone(p, "the bar list is not among 20-20's templates")
        named = [s["forEntity"] for s in p["slots"] if s["forEntity"]]
        self.assertEqual(named[:4], b["entities"][:4],
                         "slots do not follow the order the beat names its entities")
        for s in p["slots"]:
            if s["forEntity"] and s["asset"]:
                self.assertIn(s["asset"], M_picks_for(s["forEntity"], "20-20"),
                              f"slot for {s['forEntity']} holds an asset picked for "
                              "someone else")

    def test_a_surplus_of_slots_is_a_recut_not_a_shortfall(self):
        # Standing rule: "an 8-slot template can be re-cut to 6 or 10, so declared
        # capacity is a hint about scale, never a gate." Calling it a shortfall
        # would invent a problem the user has already ruled is not one.
        d = self._pairings()
        src = (ROOT / "pipeline" / "pair.py").read_text()
        self.assertNotIn('"shortfall"', src, "pair.py still reports a shortfall")
        self.assertIn("recutTo", src)
        any_recut = [p for b in d["beats"].values() for p in b["proposed"] if p["recutTo"]]
        self.assertTrue(any_recut, "no template reports a re-cut — is the field wired?")
        for p in any_recut:
            self.assertLess(p["recutTo"], p["mediaSlots"])

    def test_an_asset_that_fits_nowhere_is_reported_not_dropped(self):
        d = self._pairings()
        for name, b in d["beats"].items():
            placed = {s["asset"] for p in b["proposed"] for s in p["slots"] if s["asset"]}
            for p in b["proposed"]:
                accounted = placed | set(p["unplaced"])
                for a in b["pickedAssets"]:
                    if a in M_pool():
                        self.assertIn(a, accounted,
                                      f"{name}: picked asset {a[:12]} is neither "
                                      "placed nor reported unplaced")

    def test_a_repeat_is_allowed_but_only_after_every_distinct_asset(self):
        """OVERRULED 2026-09-26. This test forbade a repeat outright.

        The user on 25-25b: "j Cole in the middle image and 2 instances of the mag
        cover on outside portraits... we need some paring logic that can facilitate
        something like that." The prohibition was mine and was never a rule —
        grammar/MERGE.md already says "fill unused slots with declared loop repeats,
        never by inventing an entity", which is the opposite.
        What survives is the part that was worth guarding: variety comes first. A
        repeat may only appear once every distinct asset has a slot, and it must be
        MARKED, so a reviewer can tell a deep library from a looping one.
        """
        d = self._pairings()
        for name, b in d["beats"].items():
            for p in b["proposed"]:
                firsts = [s["asset"] for s in p["slots"]
                          if s["asset"] and not s.get("repeat")]
                self.assertEqual(len(firsts), len(set(firsts)),
                                 f"{name}/{p['templateId']} repeats before every "
                                 "distinct asset is placed")
                for s in p["slots"]:
                    if s.get("repeat"):
                        self.assertIn(s["asset"], firsts,
                                      "a repeat names an asset that has no slot of "
                                      "its own")

    def test_a_user_pairing_survives_a_rerun(self):
        # The user's pairing has the standing of a pick. A rebuild must not erase it.
        import subprocess
        f = ROOT / "grammar" / "pairings.json"
        if not f.exists(): self.skipTest("not built")
        before = json.load(open(f))
        before.setdefault("user", {})["__probe__"] = {"templateId": "t", "slots": []}
        f.write_text(json.dumps(before, indent=1))
        try:
            subprocess.run([sys.executable, "pipeline/pair.py", "--write"],
                           capture_output=True, text=True, cwd=str(ROOT))
            after = json.load(open(f))
            self.assertIn("__probe__", after.get("user") or {},
                          "a rerun discarded the user's pairings")
        finally:
            d = json.load(open(f))
            (d.get("user") or {}).pop("__probe__", None)
            f.write_text(json.dumps(d, indent=1, ensure_ascii=False))


def M_pool():
    import media_candidates as M
    return M.load()


def M_picks_for(entity, beat):
    import media_candidates as M
    return M.picked().get(f"{beat}::e:{entity}") or []


class HeadshotAndQuarterAreOneClass(unittest.TestCase):
    """USER RULING 2026-09-26: "we shiiuld treat headshot and quarter as the same
    for now."

    They are adjacent on the scale — quarter is head-and-chest, headshot is
    head-and-shoulders — and only 20 assets in the pool carry either tag, split 11
    and 9. Splitting hairs between them costs candidates on the tightest-cropping
    templates, which are the spatial scenes that need them most.

    DECLARED AS AN EQUIVALENCE, not collapsed in FRAMING_TAGS. The underlying tags
    stay as the library wrote them, the scale keeps five values, and lifting the
    ruling is deleting one line. Collapsing the vocabulary would have thrown away
    a distinction the user may want back.
    """

    def test_either_satisfies_a_template_asking_for_the_other(self):
        import media_candidates as M
        self.assertTrue(M.framing_matches("quarter", ("headshot",)))
        self.assertTrue(M.framing_matches("headshot", ("quarter",)))

    def test_it_does_not_reach_across_the_rest_of_the_scale(self):
        import media_candidates as M
        for f in ("half", "three_quarter", "full"):
            self.assertFalse(M.framing_matches(f, ("headshot",)), f)
            self.assertFalse(M.framing_matches("headshot", (f,)), f)

    def test_unknown_framing_is_still_unknown_not_a_match(self):
        # 430 of 565 pool assets carry no framing tag. They must rank in the
        # MIDDLE, never as a match and never last.
        import media_candidates as M
        self.assertIsNone(M.framing_matches(None, ("headshot",)))

    def test_the_underlying_tags_are_untouched(self):
        import collections
        import media_candidates as M
        c = collections.Counter(r["framing"] for r in M.load().values())
        self.assertGreater(c.get("headshot", 0), 0, "headshot was collapsed away")
        self.assertGreater(c.get("quarter", 0), 0, "quarter was collapsed away")
        self.assertEqual(len(M.FRAMING_SCALE), 5, "the scale lost a value")

    def test_both_readers_use_the_same_rule(self):
        # resolve() and pair.py ranked framing independently. Two copies of one
        # rule is how they drift.
        src = (ROOT / "pipeline" / "pair.py").read_text()
        self.assertIn("M.framing_matches", src,
                      "pair.py ranks framing with its own copy of the rule")


class TheContextIsTheScriptNotTheBeats(unittest.TestCase):
    """The review page's "script context" was built out of the beats themselves.

    build_full_review.narration() read the `>` blockquotes from the passages
    annotation file and concatenated them. Those blockquotes ARE the beats, so
    the two sentences either side of a beat were just the neighbouring beats.
    The user: "is that the script or the beats? i want the script! i need to see
    where things fit in the whole thing" — and then, on the script to use:
    "this is the script that should be used ... the other one was too choppy."

    The probe is a sentence v2.1 has that no beat quote contains. Under the old
    builder no such sentence could appear in any context, because the corpus was
    the beat quotes and nothing else.
    """

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "pipeline"))
        import script_map
        cls.SM = script_map
        cls.shots = {f"{x['passage']}-{x['beat']}": x for x in
                     json.load(open(ROOT / "pipeline" / "shotlist.capacity.json"))}
        cls.keys = sorted(cls.shots)
        cls.L, cls.rows = script_map.load()
        cls.byb = {r["beat"]: r for r in cls.rows}

    def test_context_carries_narration_no_beat_contains(self):
        probe = "catalogs that barely register"
        self.assertFalse(any(probe in v["quote"] for v in self.shots.values()),
                         "probe must not be inside any beat, or it proves nothing")
        before, _ = self.L.context("04-04")
        self.assertIn(probe, before,
                      "04-04's preceding context is connective script prose")

    def test_every_beat_is_mapped(self):
        self.assertEqual(set(self.byb), set(self.keys))
        for k in self.keys:
            self.assertTrue(self.byb[k]["cycle"], f"{k} has no cycle")

    def test_anchors_run_forward_only(self):
        """21 beats are reworded and placed by overlap. Unconstrained, 23, 24 and
        25a collapsed onto one paragraph."""
        at = [self.byb[k]["charStart"] for k in self.keys]
        for i in range(1, len(at)):
            self.assertGreaterEqual(at[i], at[i - 1],
                                    f"{self.keys[i]} anchors before {self.keys[i-1]}")

    def test_cycles_appear_in_script_order(self):
        seen = []
        for k in self.keys:
            c = self.byb[k]["cycle"]
            if not seen or seen[-1] != c:
                self.assertNotIn(c, seen, f"{c} is revisited at {k}")
                seen.append(c)
        self.assertEqual(seen[0], "CYCLE 1 — THE TAP")
        self.assertEqual(len(seen), 6, "v2.1 has six cycles")

    def test_beat_15_lands_in_cycle_3_where_the_script_puts_it(self):
        """REGRESSION. 15-15 is verbatim the first line of CYCLE 3 / PROVOKE, and
        it was reported in CYCLE 2 / RECONCILE. Cause: `[^.!?]*[.!?]+` includes
        the space after the previous full stop, so the sentence opening a
        paragraph starts one char before the paragraph, and snapping the span
        back to it moved the beat across the cycle boundary. One character."""
        r = self.byb["15-15"]
        self.assertTrue(r["cycle"].startswith("CYCLE 3"), r["cycle"])
        self.assertEqual(r["section"], "PROVOKE")

    def test_sentence_spans_exclude_leading_whitespace(self):
        t = "One. Two. Three."
        spans = self.SM.sentences(t)
        for a, b in spans:
            self.assertFalse(t[a].isspace(), f"span at {a} starts on whitespace")
        self.assertEqual([t[a:b] for a, b in spans], ["One.", "Two.", "Three."])

    def test_every_envelope_starts_on_a_sentence_boundary(self):
        """The rendered envelope is whole sentences, so the context never stops
        mid-clause. Before snapping, 21-21a's began "got. He gets accused..." —
        "got" being the tail of the previous sentence."""
        starts = {a for a, _ in self.SM.sentences(self.L.full)}
        for k in self.keys:
            self.assertIn(self.byb[k]["sentStart"], starts,
                          f"{k}'s envelope does not start on a sentence boundary")

    def test_what_the_page_shows_is_contiguous_script(self):
        """THE DEFECT THIS EXISTS TO STOP. The page used to render
        before + beat.quote + after, splicing the beat's terse quote where the
        script's own words go. Beats 02-02a and 02-02b SHARE one script sentence
        — "Curren$y was on the 2009 XXL Freshman cover, and every song he has
        ever put on the platform ... twenty-four days." — so on 02-02a the splice
        dropped 02-02b's half and the page read "Curren$y was on the 2009 XXL
        Freshman cover" then jumped to "Here are ninety-three rappers". The user:
        "how do we jump from freshman cover to here are 93 rappers? this is
        exatcly what I was rying to avoid."

        A window is now before + mid + after, and that must be a REAL SUBSTRING
        of the narration for every beat. The old shape cannot satisfy this on any
        beat whose quote is not verbatim — 21 of 40 — nor on either half of a
        shared sentence.
        """
        for k in self.keys:
            w = self.L.window(k)
            joined = " ".join(x for x in (w["before"], w["mid"], w["after"]) if x)
            self.assertIn(joined, self.L.full,
                          f"{k}: what the page shows is not contiguous script")

    def test_the_highlight_is_inside_the_envelope_and_is_the_beat(self):
        """The mark has to land on this beat's words, not the whole sentence —
        that is what keeps 02-02a and 02-02b distinguishable when they share
        one."""
        for k in self.keys:
            w = self.L.window(k)
            self.assertGreaterEqual(w["hlStart"], 0, k)
            self.assertLessEqual(w["hlStart"] + w["hlLen"], len(w["mid"]), k)
            self.assertGreater(w["hlLen"], 0, f"{k} highlights nothing")
        a, b = self.L.window("02-02a"), self.L.window("02-02b")
        self.assertEqual(a["mid"], b["mid"], "they share one sentence")
        ha = a["mid"][a["hlStart"]:a["hlStart"] + a["hlLen"]]
        hb = b["mid"][b["hlStart"]:b["hlStart"] + b["hlLen"]]
        self.assertNotEqual(ha, hb, "each half must mark its own words")
        self.assertIn("Freshman cover", ha)
        self.assertIn("twenty-four days", hb)

    def test_the_page_never_splices_the_quote_into_the_prose(self):
        page = (ROOT / "pipeline" / "ui13-review" / "index.html").read_text()
        self.assertNotIn("esc(b.before)", page,
                         "the old before/quote/after splice must be gone")
        self.assertIn("function scriptHtml(", page)

    def test_a_user_override_wins_and_is_marked(self):
        ovp = ROOT / "grammar" / "beat-script-map.overrides.json"
        had = ovp.read_text() if ovp.exists() else None
        try:
            ovp.write_text(json.dumps({"beats": [
                {"beat": "01-01", "cycle": "CYCLE 9 — TEST", "section": "X"}]}))
            rows = self.SM.build()[0]
            r = next(x for x in rows if x["beat"] == "01-01")
            self.assertEqual(r["cycle"], "CYCLE 9 — TEST")
            self.assertEqual(r["source"], "user",
                             "a user row must be traceable as one")
        finally:
            if had is None: ovp.unlink(missing_ok=True)
            else: ovp.write_text(had)
            self.SM.build()

    def test_the_map_names_the_script_it_was_built_from(self):
        d = json.loads((ROOT / "grammar" / "beat-script-map.json").read_text())
        self.assertIn("v2.1", d["_script"])


class AStalePolishMirrorStopsTheRun(unittest.TestCase):
    """A local copy of Codex's tree must fail loudly when it falls behind.

    The Polish tree became unreadable on 2026-09-26 (LOG 0126), so the pool is
    read from a mirror under ~/timeline. paths.py's own docstring names the
    danger: "the failure mode this file exists to prevent is not a missing file,
    it is a present-but-stale one." When Codex regenerates approved-list.json,
    a mirror keeps serving the old pool and every slate built from it is wrong
    with nothing saying so.

    What makes this checkable: macOS denies read() on a TCC-protected file but
    still permits stat(). Measured — open() on catalog.json raised
    PermissionError while stat() returned 1.29 MB. mtime and size are enough.
    """

    def setUp(self):
        sys.path.insert(0, str(ROOT / "pipeline"))
        import paths
        self.paths = paths
        paths._checked.clear()
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.src = self.tmp / "source"; self.mir = self.tmp / "mirror"
        for d in (self.src, self.mir):
            (d / "ae-template-automation" / "scene-library").mkdir(parents=True)
        self.rel = pathlib.Path("ae-template-automation/scene-library/pool.json")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        self.paths._checked.clear()

    def _write(self, which, text, mtime):
        p = (self.src if which == "src" else self.mir) / self.rel
        p.write_text(text)
        os.utime(p, (mtime, mtime))

    def test_a_matching_copy_is_fresh(self):
        self._write("src", '{"a":1}', 1000)
        self._write("mir", '{"a":1}', 1000)
        v, rows = self.paths.mirror_status(self.mir, self.src)
        self.assertEqual(v, "fresh", rows)

    def test_a_newer_source_is_stale(self):
        """Codex regenerated the pool; the mirror still holds yesterday's."""
        self._write("mir", '{"a":1}', 1000)
        self._write("src", '{"a":2}', 9000)
        v, rows = self.paths.mirror_status(self.mir, self.src)
        self.assertEqual(v, "stale", rows)

    def test_a_same_age_but_different_size_is_stale(self):
        """cp -p preserves mtime, so mtime alone would call this fresh."""
        self._write("mir", '{"a":1}', 1000)
        self._write("src", '{"a":1,"b":2}', 1000)
        v, _ = self.paths.mirror_status(self.mir, self.src)
        self.assertEqual(v, "stale")

    def test_an_unreachable_source_is_unverified_not_fresh(self):
        """The honest answer when the source cannot be stat'd at all. Calling
        this "fresh" is the claim the mirror is not entitled to make."""
        self._write("mir", '{"a":1}', 1000)
        v, rows = self.paths.mirror_status(self.mir, self.tmp / "gone")
        self.assertEqual(v, "unverified", rows)

    def test_one_unknown_among_fresh_files_is_not_fresh(self):
        """Partial knowledge is not freshness."""
        self._write("src", '{"a":1}', 1000)
        self._write("mir", '{"a":1}', 1000)
        orphan = self.mir / "ae-template-automation" / "orphan.json"
        orphan.write_text("{}")
        v, _ = self.paths.mirror_status(self.mir, self.src)
        self.assertNotEqual(v, "fresh")

    def test_polish_root_refuses_to_return_a_stale_mirror(self):
        """The guard sits in polish_root(), which scene_library() and narration()
        both call, so no consumer can route around it."""
        self._write("mir", '{"a":1}', 1000)
        self._write("src", '{"a":2}', 9000)
        old = dict(os.environ)
        try:
            os.environ["ASTRA_POLISH"] = str(self.mir)
            os.environ["ASTRA_POLISH_SOURCE"] = str(self.src)
            with self.assertRaises(SystemExit) as cm:
                self.paths.scene_library()
            self.assertIn("STALE POLISH MIRROR", str(cm.exception))
        finally:
            os.environ.clear(); os.environ.update(old)

    def test_it_inspects_the_mirror_in_use_not_the_default_path(self):
        """Found by running it. mirror_status() defaulted to mirror_root()
        (~/timeline/polish-mirror) while a live mirror sat on ASTRA_POLISH, so
        the report said "absent" with a stale mirror in use. A guard that
        inspects the wrong directory is worse than none: its silence reads as
        a pass."""
        self._write("mir", '{"a":1}', 1000)
        self._write("src", '{"a":2,"b":3}', 9000)
        old = dict(os.environ)
        try:
            os.environ["ASTRA_POLISH"] = str(self.mir)
            os.environ["ASTRA_POLISH_SOURCE"] = str(self.src)
            os.environ["ASTRA_POLISH_MIRROR"] = str(self.tmp / "not-the-one-in-use")
            v, rows = self.paths.mirror_status()      # no arguments, as main() calls it
            self.assertEqual(v, "stale", rows)
        finally:
            os.environ.clear(); os.environ.update(old)

    def test_the_real_tree_is_never_checked_against_itself(self):
        old = dict(os.environ)
        try:
            os.environ["ASTRA_POLISH"] = str(self.src)
            os.environ["ASTRA_POLISH_SOURCE"] = str(self.src)
            self.assertEqual(self.paths.polish_root(), self.src)
        finally:
            os.environ.clear(); os.environ.update(old)


class ThePolishMirrorIsContentAddressed(unittest.TestCase):
    """The mirror is verified against GitHub blob shas, not mtimes.

    Codex's tree is github.com/djtoler/Polish, pushed to daily. A git blob sha
    says a file IS the same file; an mtime only approximates it, and a `cp`
    resets it. polish_sync computes the sha itself on every fetched byte, so a
    truncated or substituted download cannot be written into the mirror.
    """

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "pipeline"))
        import polish_sync
        cls.PS = polish_sync

    def test_blob_sha_is_gits_own_object_id(self):
        """Verified against a known git hash-object result: the empty blob."""
        self.assertEqual(self.PS.blob_sha(b""),
                         "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")
        self.assertEqual(self.PS.blob_sha(b"hello\n"),
                         "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_a_length_only_check_would_not_catch_substitution(self):
        """Why the sha and not the size: same length, different bytes."""
        a, b = b'{"pool":"v1"}', b'{"pool":"v2"}'
        self.assertEqual(len(a), len(b))
        self.assertNotEqual(self.PS.blob_sha(a), self.PS.blob_sha(b))

    def test_every_fetched_file_names_its_consumer(self):
        """A file with no consumer does not belong in the mirror. 4.5 MB is
        fetched out of a 338 MB repo precisely because the list is justified."""
        self.assertTrue(self.PS.FILES)
        for path, why in self.PS.FILES.items():
            self.assertTrue(why and len(why) > 12,
                            f"{path} is fetched with no stated consumer")

    def test_the_manifest_records_the_commit_it_came_from(self):
        m = self.PS.MANIFEST
        if not m.exists():
            self.skipTest("mirror not fetched in this environment")
        d = json.loads(m.read_text())
        for k in ("repo", "ref", "commit", "fetchedAt", "files"):
            self.assertIn(k, d, "the mirror must say what it is a copy of")
        self.assertEqual(set(d["files"]), set(self.PS.FILES))


class BrollAddsToMediaOrReplacesIt(unittest.TestCase):
    """B-roll is an add-on OR a replacement, and media toggles independently.

    The user asked for this twice. 2026-09-26, first: "allow b-roll to be used as
    addition to template/media or in place of media." The build made the checkbox
    SWAP one list for the other, which allowed replacement and made addition
    unreachable — measured on the old function, there is no value of the flag
    that yields media AND b-roll. Second: "clicking b-roll should toggle media on
    or off. i specifically asked for earlier, that broll be an optional add on or
    replacement of media if not media is selected but broll is still paired with
    a template."

    The assertions run the ACTUAL functions extracted from the shipped page, not
    a copy of them, so the test cannot pass against a page that lost the change.
    """

    PAGE = ROOT / "pipeline" / "ui13-review" / "index.html"
    HARNESS = ROOT / "tests" / "brollstate.mjs"

    def test_the_shipped_page_satisfies_every_source_combination(self):
        if not shutil.which("node"):
            self.skipTest("node not available")
        out = subprocess.run(["node", str(self.HARNESS), str(self.PAGE)],
                             capture_output=True, text=True)
        rows = json.loads(out.stdout or "[]")
        self.assertTrue(rows, out.stderr[:400])
        bad = [r for r in rows if not r["ok"]]
        self.assertFalse(bad, "\n".join(
            f"{r['what']}: got {r['got']} want {r['want']}" for r in bad))
        # the four combinations, named, so a reader sees what is guaranteed
        for what in ("default is media only", "add-on unions and dedupes",
                     "replacement is b-roll only", "both off yields nothing",
                     "b-roll on leaves media on",
                     "old record: checked box meant replacement",
                     "the record keeps how many clips were on offer",
                     "none of 5 is a sourcing request, distinct from none of 0",
                     "the record's shape is fixed"):
            self.assertIn(what, [r["what"] for r in rows])

    def test_the_sourcing_verdict_reaches_the_record(self):
        """"add an additional button that says no eligible b-roll, to track
        sourcing needs" — a button whose verdict never leaves the page tracks
        nothing, so the shape of the saved record is part of the feature."""
        page = self.PAGE.read_text()
        self.assertIn("id='nob'", page, "the button must exist")
        self.assertIn("noBroll", page)
        self.assertIn("brollOffered", page,
                      "the count on offer is what makes the verdict actionable")
        self.assertIn("if (v.noBroll) nob[v.beat] = true;", page,
                      "the verdict must survive a reload")

    def test_the_page_no_longer_swaps_one_list_for_the_other(self):
        """The old shape, verbatim, must be gone — it is what made add-on
        impossible."""
        page = self.PAGE.read_text()
        self.assertNotIn("broll[b.beat] ? b.broll : b.media", page)
        self.assertIn("function pool(", page)
        self.assertIn("function adopt(", page)


class TheIssueRegisterQuotesTheUserExactly(unittest.TestCase):
    """grammar/issues_matching_layer.json cites the user's words as evidence.

    A paraphrase that hardens into a rule is the failure CLAUDE.md names: "Their
    note is the evidence; do not paraphrase it into a rule without showing the
    quote." So every quoted fragment must appear verbatim in that beat's own
    review note, and every beat cited must exist. The issues themselves are
    PLAUSIBLE, not verified — that label is asserted here too, because an
    unverified analysis that loses its label reads as a finding.
    """

    @classmethod
    def setUpClass(cls):
        cls.reg = json.loads((ROOT / "grammar" / "issues_matching_layer.json").read_text())
        p = ROOT / "grammar" / "beat-review-export-2026-09-27.json"
        cls.ex = json.loads(p.read_text())
        cls.notes = {b["beat"]: ((b["userReview"] or {}).get("note") or "")
                     for b in cls.ex["beats"]}

    @staticmethod
    def _n(s):
        return re.sub(r"\s+", " ", s).strip()

    def test_every_quoted_fragment_is_verbatim(self):
        checked = 0
        for i in self.reg["issues"]:
            for q in i["userWords"]:
                note = self._n(self.notes.get(q["beat"], ""))
                self.assertTrue(note, f"{i['id']} cites {q['beat']}, which has no note")
                # "..." or an ellipsis marks an elision; each fragment must be real
                for fr in [x.strip() for x in re.split(r"\.\.\.|\u2026",
                                                      self._n(q["words"])) if x.strip()]:
                    checked += 1
                    self.assertIn(fr, note,
                                  f"{i['id']} {q['beat']}: not the user's words")
        self.assertGreater(checked, 20, "the register should cite the user throughout")

    def test_every_cited_beat_exists(self):
        have = {b["beat"] for b in self.ex["beats"]}
        for i in self.reg["issues"]:
            for b in i["beats"] + [q["beat"] for q in i["userWords"]]:
                self.assertIn(b, have, f"{i['id']} cites unknown beat {b}")

    def test_a_count_never_disagrees_with_its_own_list(self):
        """PI-03 said 6 beats and listed 7. A number that contradicts the list
        beside it costs the whole register its credibility."""
        for i in self.reg["issues"]:
            if i["beats"]:
                self.assertGreaterEqual(
                    i["beatsAffected"], len(i["beats"]),
                    f"{i['id']} claims {i['beatsAffected']} but lists {len(i['beats'])}")

    def test_the_register_declares_itself_unverified(self):
        self.assertIn("PLAUSIBLE", self.reg["_status"].upper())
        self.assertIn("not evidence", self.reg["_whyPlausible"])
        self.assertTrue(self.reg["_withdrawn"],
                        "the withdrawn measurement must stay on the record")

    def test_the_export_carries_the_register(self):
        """The section has to reach the file that gets pushed, not just its
        sidecar."""
        self.assertIn("issues_matching_layer", self.ex)
        self.assertEqual(len(self.ex["issues_matching_layer"]["issues"]),
                         self.ex["_counts"]["issuesMatchingLayer"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
