import unittest

from pipeline import entities


class EntityAliasTests(unittest.TestCase):
    def test_alias_resolves_to_canonical_roster_name(self):
        result = entities.extract(
            "Big Pun belongs in the comparison.",
            ["Big Punisher", "Jay-Z"],
            {"Big Pun": "Big Punisher"},
        )
        self.assertEqual(result["entities"], ["Big Punisher"])
        self.assertEqual(result["spans"], {"Big Punisher": ["Big Pun"]})

    def test_alias_target_must_be_canonical(self):
        with self.assertRaisesRegex(ValueError, "unknown canonical"):
            entities.extract("Big Pun", ["Jay-Z"], {"Big Pun": "Big Punisher"})

    def test_story_scoped_ambiguous_surface_can_be_ignored(self):
        result = entities.extract(
            "Pluto was an album.",
            ["Future"],
            {"Pluto": "Future"},
            ignored_surfaces=["Pluto"],
        )
        self.assertEqual(result["entities"], [])

    def test_live_shared_registry_is_v12_and_returns_stable_ids(self):
        names, meta = entities.roster()
        self.assertEqual(meta["_registryVersion"], "12")
        self.assertGreaterEqual(len(names), 467)
        result = entities.extract("Rico Wade and DJ Esco worked with Future.")
        self.assertEqual(
            {row["entityId"] for row in result["entityRefs"]},
            {"person:rico-wade", "person:dj-esco", "person:future"},
        )

    def test_short_or_unreviewed_surfaces_do_not_auto_promote(self):
        self.assertEqual(entities.extract("Sir and Eve met Joe and Ye.")["entities"], [])

    def test_short_surface_requires_explicit_task_context(self):
        result = entities.extract("Eve performed.", allowed_short_surfaces=["Eve"])
        self.assertEqual(result["entities"], ["Eve"])
        self.assertEqual(result["entityRefs"][0]["entityId"], "person:eve")


if __name__ == "__main__":
    unittest.main()
