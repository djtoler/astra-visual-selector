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
    def test_ten_people_activates_the_route(self):
        self.assertFalse(C.needs_long_carousel(9))
        self.assertTrue(C.needs_long_carousel(10))
        self.assertTrue(C.needs_long_carousel(11))

    def test_only_capacity_qualified_ae_media_carousel_satisfies(self):
        self.assertTrue(C.is_long_media_carousel(carousel(), 11))
        self.assertFalse(C.is_long_media_carousel(carousel(kind="cinematic_3d"), 11))
        self.assertFalse(C.is_long_media_carousel(carousel(kind="infographic"), 11))
        self.assertFalse(C.is_long_media_carousel(carousel(media=0, total=12), 11))
        self.assertFalse(C.is_long_media_carousel(carousel(media=10, total=10), 11))

    def test_text_carousel_cannot_satisfy_media_roster(self):
        text = carousel("text-list-carousel", media=0, total=20, carries=["none"])
        self.assertFalse(C.is_long_media_carousel(text, 11))


class LongCarouselRoute(unittest.TestCase):
    def test_bound_qualified_carousel_is_preserved(self):
        pool = {
            "ae-carousel": carousel(),
            "ordinary": {"id": "ordinary", "kind": "after_effects"},
        }
        bound = [{"id": "ordinary"}, {"id": "ae-carousel"}]
        rows, note = shotlist.route_long_carousel({"entity_count": 11}, bound, pool)
        self.assertIs(rows, bound)
        self.assertIn("capacity-qualified", note)

    def test_missing_bound_carousel_adds_ae_candidate_only(self):
        pool = {
            "ae-carousel": carousel(),
            "spatial-carousel": carousel("spatial-carousel", kind="cinematic_3d"),
            "infographic-carousel": carousel("infographic-carousel", kind="infographic"),
            "short-carousel": carousel("short-carousel", media=5, total=5),
        }
        rows, note = shotlist.route_long_carousel(
            {"entity_count": 11}, [{"id": "ordinary"}], pool
        )
        self.assertEqual([row["id"] for row in rows], ["ae-carousel", "ordinary"])
        self.assertIn("spatial and infographic scenes do not satisfy", note)


if __name__ == "__main__":
    unittest.main()
