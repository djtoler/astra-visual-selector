import tempfile
import unittest
from pathlib import Path

from run_native_batch import resolve_from, sha256_file


class NativeBatchTests(unittest.TestCase):
    def test_relative_paths_resolve_from_manifest_or_job_directory(self):
        base = Path("/tmp/capacity/jobs")
        self.assertEqual(resolve_from(base, "../raw/report.json"), Path("/tmp/capacity/raw/report.json").resolve())

    def test_hashes_file_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.aep"
            path.write_bytes(b"capacity")
            self.assertEqual(sha256_file(path), "ec21b3b973a3a0e7050392031862848f7a19272ca8a820aed64c56d1d26e8db1")


if __name__ == "__main__":
    unittest.main()
