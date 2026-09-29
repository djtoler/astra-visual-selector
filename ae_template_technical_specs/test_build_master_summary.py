import unittest

from build_master_summary import unique_project_id


class MasterSummaryTests(unittest.TestCase):
    def test_cross_batch_project_id_collision_uses_source_hash_suffix(self):
        used = set()

        self.assertEqual(unique_project_id("photo-slideshow", "a" * 64, used), "photo-slideshow")
        self.assertEqual(
            unique_project_id("photo-slideshow", "b" * 64, used),
            "photo-slideshow-bbbbbbbb",
        )

    def test_hash_suffixed_collision_fails_closed(self):
        used = {"photo-slideshow", "photo-slideshow-bbbbbbbb"}

        with self.assertRaisesRegex(ValueError, "still collides"):
            unique_project_id("photo-slideshow", "b" * 64, used)


if __name__ == "__main__":
    unittest.main()
