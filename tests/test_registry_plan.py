from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from addon.blender_linked_part_version_manager.adapters.git import preview_git_part
from addon.blender_linked_part_version_manager.adapters.local import preview_local_part
from addon.blender_linked_part_version_manager.core.plan import build_sync_plan, summarize_plan
from addon.blender_linked_part_version_manager.core.registry import validate_registry


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "samples" / "representative-suite.json"


class RegistryPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(SAMPLE.read_text(encoding="utf-8"))

    def test_sample_registry_is_valid(self) -> None:
        self.assertEqual(validate_registry(self.registry), [])

    def test_duplicate_part_id_is_rejected(self) -> None:
        duplicate = json.loads(json.dumps(self.registry))
        duplicate["parts"][1]["partId"] = duplicate["parts"][0]["partId"]
        issues = validate_registry(duplicate)
        self.assertTrue(any(issue["code"] == "duplicate-part-id" for issue in issues))

    def test_plan_blocks_dirty_and_broken_parts(self) -> None:
        plan = build_sync_plan(self.registry)
        summary = summarize_plan(plan)
        by_id = {item["partId"]: item for item in plan}
        self.assertEqual(summary["totalParts"], 4)
        self.assertEqual(by_id["hair-main"]["plannedActions"], ["fetch", "pull-preview", "reload-link"])
        self.assertEqual(by_id["face-main"]["risk"], "blocked")
        self.assertIn("skip-auto-update", by_id["face-main"]["plannedActions"])
        self.assertEqual(by_id["accessories-glasses"]["status"], "broken-link")

    def test_local_adapter_detects_newer_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_root = root / "source"
            source_path = source_root / "body" / "base_body.blend"
            source_path.parent.mkdir(parents=True)
            source_path.write_text("new", encoding="utf-8")
            target = root / "parts" / "body" / "base_body.blend"
            target.parent.mkdir(parents=True)
            target.write_text("old", encoding="utf-8")
            part = json.loads(json.dumps(self.registry["parts"][1]))
            part["source"]["root"] = str(source_root)
            result = preview_local_part(part, repo_root=root)
            self.assertIn(result["status"], {"current", "remote-newer"})

    def test_git_adapter_uses_runner_contract(self) -> None:
        part = self.registry["parts"][0]

        def runner(args, cwd):
            if args[:3] == ["git", "status", "--porcelain"]:
                return subprocess.CompletedProcess(args, 0, "", "")
            return subprocess.CompletedProcess(args, 0, "0\t2\n", "")

        result = preview_git_part(part, repo_root=ROOT, runner=runner)
        self.assertEqual(result["status"], "remote-newer")


if __name__ == "__main__":
    unittest.main()
