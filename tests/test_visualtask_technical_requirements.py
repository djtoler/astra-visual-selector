import copy
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VisualTaskTechnicalRequirements(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pipeline import visualtask_requirements

        cls.subject = visualtask_requirements
        cls.artifact = visualtask_requirements.build_requirements()

    def task(self, task_id):
        return next(row for row in self.artifact["tasks"] if row["taskId"] == task_id)

    def test_all_tasks_are_encoded_and_exact_timing_is_counted(self):
        self.assertEqual(self.artifact["counts"]["visualTasks"], 41)
        self.assertEqual(self.artifact["counts"]["exactTaskAudioSpans"], 39)
        self.assertEqual(self.artifact["counts"]["unresolvedTaskAudioSpans"], 2)

    def test_unsplit_task_uses_saved_source_beat_timing(self):
        task = self.task("02-02a.main")
        self.assertEqual(task["timingRequirement"]["status"], "exact_source_beat_span")
        self.assertEqual(task["timingRequirement"]["exactTaskAudioSpan"]["durationSeconds"], 3.1)
        self.assertEqual(task["dataRequirements"]["status"], "exact_source_beat_encodings")

    def test_split_task_does_not_invent_timing_or_allocate_encoding(self):
        task = self.task("28-28.overlap")
        self.assertEqual(task["timingRequirement"]["status"], "unresolved_split_task_span")
        self.assertIsNone(task["timingRequirement"]["exactTaskAudioSpan"])
        self.assertEqual(task["dataRequirements"]["status"], "source_beat_only_not_task_allocated")

    def test_display_identities_are_not_called_media_slots(self):
        task = self.task("03-03.opening_chart")
        self.assertEqual(task["contentRequirements"]["displayIdentityCount"], 93)
        self.assertIsNone(task["mediaRequirements"]["requiredSlotCount"])
        self.assertEqual(task["mediaRequirements"]["status"], "unresolved_treatment_dependent")

    def test_text_and_typed_data_requirements_remain_honestly_unknown(self):
        task = self.task("09-09.main")
        self.assertIsNone(task["textRequirements"]["requiredFieldCount"])
        self.assertIsNone(task["dataRequirements"]["requiredTypedFields"])
        self.assertEqual(task["dataRequirements"]["requiredEncodings"], ["identity", "magnitude"])

    def test_missing_source_beat_fails_closed(self):
        slate = json.loads((ROOT / "pipeline" / "shotlist.capacity.json").read_text())
        slate = [row for row in slate if not (row["passage"] == "02" and row["beat"] == "02a")]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "slate.json"
            path.write_text(json.dumps(slate))
            with self.assertRaisesRegex(ValueError, "no baseline source beat"):
                self.subject.build_requirements(slate_path=path)

    def test_consumer_rejects_stale_source_hash(self):
        broken = copy.deepcopy(self.artifact)
        broken["sources"]["visualTasks"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source is missing or stale"):
            self.subject.validate_requirements(broken)

    def test_build_is_deterministic_and_written_artifact_is_consumable(self):
        first = self.subject.dumps(self.subject.build_requirements())
        second = self.subject.dumps(self.subject.build_requirements())
        self.assertEqual(first, second)
        written = json.loads((ROOT / "grammar" / "visual-task-technical-requirements.json").read_text())
        self.assertEqual(self.subject.validate_requirements(written), written["counts"])


if __name__ == "__main__":
    unittest.main()
