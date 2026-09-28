import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from zip_inventory import build_inventory


class ZipInventoryTests(unittest.TestCase):
    def test_ignores_appledouble_project_entries(self):
        with tempfile.TemporaryDirectory() as folder:
            archive_path = Path(folder) / "archive.zip"
            with ZipFile(archive_path, "w") as archive:
                archive.writestr("Pack/Main.aep", b"project")
                archive.writestr("__MACOSX/Pack/._Main.aep", b"metadata")
            inventory = build_inventory(archive_path)
            self.assertEqual(inventory["summary"]["rawProjectFiles"], 1)
            self.assertEqual(inventory["projects"][0]["entryPath"], "Pack/Main.aep")


if __name__ == "__main__":
    unittest.main()

