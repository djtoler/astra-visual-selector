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


if __name__ == "__main__":
    unittest.main()
