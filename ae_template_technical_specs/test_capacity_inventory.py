import unittest
from pathlib import Path

from capacity_inventory import LIBRARY_ROOT, package_key, raw_class


class InventoryClassificationTests(unittest.TestCase):
    def path(self, relative):
        return LIBRARY_ROOT / relative

    def test_primary_project(self):
        path = self.path("09 Slideshows/Example/Main.aep")
        self.assertEqual(raw_class(path, LIBRARY_ROOT), "primary_candidate")
        self.assertEqual(package_key(path, LIBRARY_ROOT), "09 Slideshows/Example")

    def test_autosave(self):
        path = self.path("05 Titles/Example/Adobe After Effects Auto-Save/Main auto-save 1.aep")
        self.assertEqual(raw_class(path, LIBRARY_ROOT), "autosave")

    def test_duplicate_review(self):
        path = self.path("_duplicates-review/Example/Main.aep")
        self.assertEqual(raw_class(path, LIBRARY_ROOT), "duplicate_review")

    def test_converted_tree(self):
        path = self.path("01 Data/Example/Main (converted)_AME/tmpAEtoAMEProject-#MAIN.aep")
        self.assertEqual(raw_class(path, LIBRARY_ROOT), "converted")

    def test_working_copy(self):
        path = self.path("Documents & Screens/Example/inspection-working-copy.aep")
        self.assertEqual(raw_class(path, LIBRARY_ROOT), "working_copy")


if __name__ == "__main__":
    unittest.main()
