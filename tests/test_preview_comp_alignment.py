import unittest

import numpy as np

from pipeline import preview_comp_alignment as subject


class PreviewCompAlignment(unittest.TestCase):
    def test_recovers_known_sample_offset(self):
        rng = np.random.default_rng(7)
        native = rng.normal(size=(40, 12)).astype(np.float32)
        clip = native[11:21].copy()
        result = subject.align_samples(clip, native, 0.2)
        self.assertEqual(result["startSecondsApprox"], 2.2)
        self.assertEqual(result["endSecondsApprox"], 4.2)

    def test_rejects_clip_longer_than_native(self):
        with self.assertRaisesRegex(ValueError, "longer"):
            subject.align_samples(np.zeros((4, 2)), np.zeros((3, 2)), 0.2)


if __name__ == "__main__":
    unittest.main()
