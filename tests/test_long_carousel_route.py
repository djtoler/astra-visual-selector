import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "match-trial"))
sys.path.insert(0, str(ROOT / "pipeline"))

import candidates as C
import shotlist


def carousel(candidate_id="ae-carousel", *, kind="after_effects", media=12, total=12,
             carries=None):
    return {
        "id": candidate_id,
        "kind": kind,
        "title": "Long media carousel",
        "capability": {
            "structure": "sequence",
            "staging": "reveals_in_turn",
            "carries": carries or ["identity"],
            "media_slots": media,
            "slots_total": total,
        },
    }


class LongCarouselClassification(unittest.TestCase):
    def test_only_capacity_qualified_ae_media_carousel_satisfies(self):
        self.assertTrue(C.is_long_media_carousel(carousel(), 11))
        self.assertFalse(C.is_long_media_carousel(carousel(kind="cinematic_3d"), 11))
        self.assertFalse(C.is_long_media_carousel(carousel(kind="infographic"), 11))
        self.assertFalse(C.is_long_media_carousel(carousel(media=0, total=12), 11))
        self.assertFalse(C.is_long_media_carousel(carousel(media=10, total=10), 11))

    def test_text_carousel_cannot_satisfy_media_roster(self):
        text = carousel("text-list-carousel", media=0, total=20, carries=["none"])
        self.assertFalse(C.is_long_media_carousel(text, 11))


class SpatialAutoAdmission(unittest.TestCase):
    def pool(self):
        return {
            "spatial-a": {"id": "spatial-a", "kind": "cinematic_3d"},
            "spatial-b": {"id": "spatial-b", "kind": "cinematic_3d"},
            "ordinary": {"id": "ordinary", "kind": "after_effects"},
        }

    def test_threshold_includes_twenty(self):
        self.assertFalse(C.needs_spatial(19))
        self.assertTrue(C.needs_spatial(20))

    def test_twenty_plus_adds_every_spatial_and_preserves_other_options(self):
        rows, note = shotlist.route_spatial(
            {"entity_count": 20}, [{"id": "ordinary"}], self.pool()
        )
        self.assertEqual(
            [row["id"] for row in rows],
            ["spatial-a", "spatial-b", "ordinary"],
        )
        self.assertIn("all 2 available spatial", note)

    def test_below_twenty_does_not_force_spatial(self):
        bound = [{"id": "ordinary"}]
        rows, note = shotlist.route_spatial({"entity_count": 11}, bound, self.pool())
        self.assertIs(rows, bound)
        self.assertIsNone(note)

    def test_normal_slate_cap_cannot_hide_an_admitted_spatial_scene(self):
        routed = [{"id": "spatial-a"}, {"id": "spatial-b"}, {"id": "ordinary"}]
        slate, note = shotlist.ensure_all_spatial_options(
            {"entity_count": 20}, [{"id": "spatial-a"}, {"id": "ordinary"}],
            routed, self.pool()
        )
        self.assertEqual([row["id"] for row in slate], [
            "spatial-a", "ordinary", "spatial-b"
        ])
        self.assertIn("past the normal slate cap", note)

    def test_prior_rejection_remains_unavailable_but_every_other_spatial_is_kept(self):
        beat = {"entity_count": 20, "id": "large", "_passage": "20"}
        routed, _ = shotlist.route_spatial(
            beat, [{"id": "ordinary"}], self.pool()
        )
        available, _ = shotlist.drop_prior_rejections(
            beat, routed, {"20-large": {"rejected": ["spatial-b"]}}
        )
        slate, _ = shotlist.ensure_all_spatial_options(
            beat, [{"id": "ordinary"}], available, self.pool()
        )
        self.assertEqual(
            {row["id"] for row in slate}, {"ordinary", "spatial-a"}
        )

    def test_long_carousel_remains_a_batch_treatment_not_an_auto_route(self):
        pool = {
            "ae-carousel": carousel(),
            "ordinary": {"id": "ordinary", "kind": "after_effects"},
        }
        bound = [{"id": "ordinary"}]
        rows, note = shotlist.route_spatial({"entity_count": 11}, bound, pool)
        self.assertIs(rows, bound)
        self.assertIsNone(note)


if __name__ == "__main__":
    unittest.main()
