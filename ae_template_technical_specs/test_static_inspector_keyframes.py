from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent


class StaticInspectorKeyframeCaptureTests(unittest.TestCase):
    def test_static_inspector_captures_opacity_and_time_remap_key_values(self):
        source = (ROOT / "static_inspect.py").read_text()
        self.assertIn('capture_keyframes=field == "opacity"', source)
        self.assertIn('"ADBE Time Remapping"', source)
        self.assertIn('"time": keyframe.time', source)
        self.assertIn('"value": json_value(keyframe.value)', source)

    def test_static_keyframes_are_only_emitted_when_present(self):
        source = (ROOT / "static_inspect.py").read_text()
        self.assertIn("if capture_keyframes and keyframes:", source)


if __name__ == "__main__":
    unittest.main()
