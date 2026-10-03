import unittest

from tools.reconcile_entity_rosters import reconcile


class ReconcileEntityRostersTests(unittest.TestCase):
    def test_keeps_sources_distinct_and_resolves_explicit_alias(self):
        data = {
            "entities": [
                {"id": "person:jay-z", "type": "person", "canonicalName": "Jay-Z", "aliases": []},
                {"id": "person:big-pun", "type": "person", "canonicalName": "Big Pun", "aliases": []},
                {"id": "org:label", "type": "organization", "canonicalName": "Label", "aliases": []},
            ]
        }
        matching = {"names": ["JAY Z", "Big Punisher", "Artist Only"], "aliases": {"Big Pun": "Big Punisher"}}
        result = reconcile(
            data,
            matching,
            data_source={"path": "data"},
            matching_source={"path": "matching"},
            generated_at="2026-10-03T00:00:00Z",
        )
        self.assertTrue(result["acceptance"]["passed"])
        self.assertEqual(result["counts"]["aligned"], 2)
        self.assertEqual(result["counts"]["aliasMatches"], 1)
        self.assertEqual(result["counts"]["dataOnly"], 1)
        self.assertEqual(result["counts"]["matchingOnly"], 1)
        self.assertFalse(result["policy"]["automaticPromotion"])

    def test_rejects_canonical_normalization_collisions(self):
        data = {
            "entities": [
                {"id": "person:a", "type": "person", "canonicalName": "A-B", "aliases": []},
                {"id": "person:b", "type": "person", "canonicalName": "AB", "aliases": []},
            ]
        }
        with self.assertRaisesRegex(ValueError, "normalized-key collision"):
            reconcile(
                data,
                {"names": ["AB"], "aliases": {}},
                data_source={},
                matching_source={},
                generated_at="2026-10-03T00:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()
