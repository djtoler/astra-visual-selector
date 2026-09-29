import copy
import unittest

from reconcile_passes import reconcile


def capacity(text):
    return {
        "compositions": [{
            "compositionPath": "Main",
            "totalIndependentVisualMediaInputs": 0,
            "maxSimultaneouslyEnabledRecursiveVisualInputs": 0,
            "maxSimultaneouslyEnabledRecursiveTextFields": 1,
            "durationSeconds": 1,
            "frameRate": 30,
            "frameCount": 30,
            "workAreaStartSeconds": 0,
            "workAreaDurationSeconds": 1,
            "workAreaFrameCount": 30,
            "recursiveEditableTextFields": [1],
        }],
        "mediaSlots": [],
        "textFields": [{
            "compositionPath": "Main",
            "layerIndex": 1,
            "layerName": "Title",
            "enabled": True,
            "text": text,
        }],
    }


class ReconciliationTests(unittest.TestCase):
    def test_line_endings_do_not_change_text_field_availability(self):
        result = reconcile(capacity("one\ntwo"), capacity("one\rtwo"))
        self.assertTrue(result["textFieldIdentitySetExact"])
        self.assertEqual(result["textValueMismatchCount"], 0)

    def test_sample_text_mismatch_is_retained_separately(self):
        result = reconcile(capacity("first key"), capacity("current key"))
        self.assertTrue(result["textFieldIdentitySetExact"])
        self.assertEqual(result["textValueMismatchCount"], 1)

    def test_ae_folder_edge_whitespace_does_not_create_false_path_mismatch(self):
        static = capacity("same")
        native = copy.deepcopy(static)
        static["compositions"][0]["compositionPath"] = "Edit/Text /Scene 01"
        static["textFields"][0]["compositionPath"] = "Edit/Text /Scene 01"
        static["mediaSlots"] = [{"path": "Edit/Text /Scene 01"}]
        native["compositions"][0]["compositionPath"] = "Edit/Text/Scene 01"
        native["textFields"][0]["compositionPath"] = "Edit/Text/Scene 01"
        native["mediaSlots"] = [{"path": "Edit/Text/Scene 01"}]

        result = reconcile(static, native)

        self.assertTrue(result["compositionPathSetExact"])
        self.assertTrue(result["mediaSlotPathSetExact"])
        self.assertTrue(result["textFieldIdentitySetExact"])

    def test_distinct_paths_that_normalize_to_same_identity_fail_closed(self):
        static = capacity("same")
        native = capacity("same")
        duplicate = copy.deepcopy(static["compositions"][0])
        static["compositions"][0]["compositionPath"] = "Edit/Text/Scene 01"
        duplicate["compositionPath"] = "Edit/Text /Scene 01"
        static["compositions"].append(duplicate)

        with self.assertRaisesRegex(ValueError, "collide"):
            reconcile(static, native)


if __name__ == "__main__":
    unittest.main()
