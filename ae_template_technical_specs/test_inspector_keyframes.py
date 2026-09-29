from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent


class InspectorKeyframeCaptureTests(unittest.TestCase):
    def test_native_inspector_captures_opacity_and_time_remap_key_values(self):
        source = (ROOT / "vendor/capacity-inspector/documentary.jsx").read_text()
        self.assertIn("time:p.keyTime(ki)", source)
        self.assertIn("value:p.keyValue(ki)", source)
        self.assertIn("names[i][0] === 'opacity' ? keyframedPropertyState", source)
        self.assertIn("row.timeRemap = keyframedPropertyState", source)

    def test_keyframes_are_only_emitted_when_present(self):
        source = (ROOT / "vendor/capacity-inspector/documentary.jsx").read_text()
        self.assertIn("if (keys.length) state.keyframes = keys", source)


if __name__ == "__main__":
    unittest.main()
