import unittest

from derive_capacity import build_capacity, max_active


class CapacityDerivationTests(unittest.TestCase):
    def test_sub_frame_floating_point_gap_does_not_create_false_overlap_peak(self):
        intervals = {
            "ending": [(0.0, 24.03333333333333)],
            "starting": [(24.033333333333335, 30.0)],
            "continuous": [(0.0, 30.0)],
        }

        self.assertEqual(max_active(intervals), 2)

    def test_nested_placeholder_overlap_and_text(self):
        report = {
            "ok": True,
            "items": [
                {"id": 1, "itemType": "CompItem", "name": "Main", "path": "Main"},
                {"id": 2, "itemType": "CompItem", "name": "Block", "path": "Block"},
                {"id": 3, "itemType": "CompItem", "name": "Placeholder 1", "path": "Edit/Placeholder 1"},
            ],
            "compositions": [
                {"id": 1, "path": "Main", "width": 100, "height": 100, "duration": 5, "fps": 10, "frameDuration": .1, "workAreaStart": 0, "workAreaDuration": 5,
                 "layers": [{"index": 1, "name": "A", "sourceId": 2, "enabled": True, "inPoint": 0, "outPoint": 3, "startTime": 0, "stretch": 100}, {"index": 2, "name": "B", "sourceId": 2, "enabled": True, "inPoint": 2, "outPoint": 5, "startTime": 2, "stretch": 100}]},
                {"id": 2, "path": "Block", "width": 100, "height": 100, "duration": 3, "fps": 10, "frameDuration": .1, "workAreaStart": 0, "workAreaDuration": 3,
                 "layers": [{"index": 1, "name": "Title", "enabled": True, "inPoint": 0, "outPoint": 3, "textField": {"text": "x", "textKind": "point", "font": "A", "fontSize": 12}, "sourceText": {"numKeys": 0}}, {"index": 2, "name": "Placeholder", "sourceId": 3, "enabled": True, "inPoint": 0, "outPoint": 3, "startTime": 0, "stretch": 100}]},
                {"id": 3, "path": "Edit/Placeholder 1", "width": 100, "height": 100, "duration": 3, "fps": 10, "frameDuration": .1, "workAreaStart": 0, "workAreaDuration": 3, "layers": []},
            ],
        }
        result = build_capacity(report)
        main = next(row for row in result["compositions"] if row["compositionPath"] == "Main")
        self.assertEqual(main["totalIndependentVisualMediaInputs"], 1)
        self.assertEqual(main["maxSimultaneouslyEnabledRecursiveVisualInputs"], 1)
        self.assertEqual(len(main["recursiveEditableTextFields"]), 1)
        self.assertEqual(main["frameCount"], 50)

    def test_legacy_edit_media_compositions_are_slots_but_wrappers_are_not(self):
        report = {
            "ok": True,
            "compositions": [
                {"id": 1, "name": "FINAL", "path": "02 FINAL/FINAL", "width": 100, "height": 100, "duration": 10, "fps": 25, "workAreaStart": 0, "workAreaDuration": 10,
                 "layers": [{"index": 1, "name": "Wrapper", "source": "Wrapper", "enabled": True, "inPoint": 0, "outPoint": 10}]},
                {"id": 2, "name": "Wrapper", "path": "03 Other/Wrapper", "width": 100, "height": 100, "duration": 10, "fps": 25, "workAreaStart": 0, "workAreaDuration": 10,
                 "layers": [
                     {"index": 1, "name": "photo 1", "source": "photo 1", "enabled": True, "inPoint": 0, "outPoint": 10},
                     {"index": 2, "name": "Media 01", "source": "Media 01", "enabled": True, "inPoint": 0, "outPoint": 10},
                 ]},
                {"id": 3, "name": "photo 1", "path": "01 EDIT/1 photo/photo 1", "width": 100, "height": 100, "duration": 10, "fps": 25, "workAreaStart": 0, "workAreaDuration": 10, "layers": []},
                {"id": 4, "name": "Media 01", "path": "03 Other/Media 01", "width": 100, "height": 100, "duration": 10, "fps": 25, "workAreaStart": 0, "workAreaDuration": 10, "layers": []},
                {"id": 5, "name": "your logo", "path": "01 EDIT/2 LOGO/your logo", "width": 100, "height": 100, "duration": 10, "fps": 25, "workAreaStart": 0, "workAreaDuration": 10, "layers": []},
                {"id": 6, "name": "Image Wide 10", "path": "03. Other/Footage/Image Wide 10", "width": 100, "height": 100, "duration": 10, "fps": 25, "workAreaStart": 0, "workAreaDuration": 10, "layers": []},
                {"id": 7, "name": "FL_Media_01", "path": "01. Edit Comps/Media/FL_Media/FL_Media_01", "width": 100, "height": 100, "duration": 10, "fps": 25, "workAreaStart": 0, "workAreaDuration": 10, "layers": []},
            ],
        }
        result = build_capacity(report)
        slot_paths = {row["path"] for row in result["mediaSlots"]}
        self.assertEqual(slot_paths, {
            "01 EDIT/1 photo/photo 1",
            "01 EDIT/2 LOGO/your logo",
            "03. Other/Footage/Image Wide 10",
            "01. Edit Comps/Media/FL_Media/FL_Media_01",
        })
        final = next(row for row in result["compositions"] if row["compositionPath"] == "02 FINAL/FINAL")
        self.assertEqual(final["totalIndependentVisualMediaInputs"], 1)
        self.assertEqual(final["maxSimultaneouslyEnabledRecursiveVisualInputs"], 1)

    def test_disabled_reachable_text_is_available_but_not_simultaneously_enabled(self):
        report = {
            "ok": True,
            "compositions": [
                {"id": 1, "name": "Main", "path": "Main", "width": 100, "height": 100, "duration": 5, "fps": 10, "workAreaStart": 0, "workAreaDuration": 5,
                 "layers": [{"index": 1, "name": "your logo", "source": "your logo", "enabled": True, "inPoint": 0, "outPoint": 5}]},
                {"id": 2, "name": "your logo", "path": "01 EDIT/2 LOGO/your logo", "width": 100, "height": 100, "duration": 5, "fps": 10, "workAreaStart": 0, "workAreaDuration": 5,
                 "layers": [{"index": 1, "name": "Optional label", "enabled": False, "inPoint": 0, "outPoint": 5, "text": "Label"}]},
            ],
        }
        result = build_capacity(report)
        main = next(row for row in result["compositions"] if row["compositionPath"] == "Main")
        self.assertEqual(len(main["recursiveEditableTextFields"]), 1)
        self.assertEqual(main["maxSimultaneouslyEnabledRecursiveTextFields"], 0)


if __name__ == "__main__":
    unittest.main()
