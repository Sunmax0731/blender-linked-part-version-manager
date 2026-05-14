from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from addon.blender_linked_part_version_manager.adapters.git import preview_git_part
from addon.blender_linked_part_version_manager.adapters.local import preview_local_part
from addon.blender_linked_part_version_manager import BLPVM_TRANSLATIONS, _auto_reload_target_paths
from addon.blender_linked_part_version_manager.blender.link import (
    integrate_linked_libraries,
    reload_linked_libraries,
    scan_linked_registry_parts,
)
from addon.blender_linked_part_version_manager.core.plan import build_sync_plan, summarize_plan
from addon.blender_linked_part_version_manager.core.registry import (
    build_registry_part_candidate,
    registry_from_parts,
    validate_registry,
)


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "samples" / "representative-suite.json"


def _status_fixture_registry() -> dict:
    return {
        "schema_version": 1,
        "product": "blender-linked-part-version-manager",
        "integration_file": "integration/character_integration.blend",
        "parts": [
            {
                "partId": "hair-main",
                "partTag": "Hair",
                "displayName": "Main Hair",
                "blendPath": "parts/hair/main_hair.blend",
                "linkedCollection": "CHR_Hair_Main",
                "owner": "artist-a",
                "source": {
                    "type": "git",
                    "remote": "origin",
                    "branch": "main",
                    "path": "parts/hair/main_hair.blend",
                },
                "versionRef": "main",
                "updatePolicy": "manual",
                "expectedStatus": "remote-newer",
            },
            {
                "partId": "body-base",
                "partTag": "Body",
                "displayName": "Base Body",
                "blendPath": "parts/body/base_body.blend",
                "linkedCollection": "CHR_Body_Base",
                "owner": "artist-b",
                "source": {
                    "type": "local",
                    "root": "D:/Shared/CharacterParts",
                    "path": "body/base_body.blend",
                },
                "versionRef": "2026-05-14",
                "updatePolicy": "scheduled",
                "expectedStatus": "current",
            },
            {
                "partId": "face-main",
                "partTag": "Face",
                "displayName": "Main Face",
                "blendPath": "parts/face/main_face.blend",
                "linkedCollection": "CHR_Face_Main",
                "owner": "artist-c",
                "source": {
                    "type": "git",
                    "remote": "origin",
                    "branch": "face",
                    "path": "parts/face/main_face.blend",
                },
                "versionRef": "face",
                "updatePolicy": "manual",
                "expectedStatus": "local-dirty",
            },
            {
                "partId": "accessories-glasses",
                "partTag": "Accessories",
                "displayName": "Glasses",
                "blendPath": "parts/accessories/glasses.blend",
                "linkedCollection": "CHR_ACC_Glasses",
                "owner": "artist-d",
                "source": {
                    "type": "git",
                    "remote": "origin",
                    "branch": "main",
                    "path": "parts/accessories/glasses.blend",
                },
                "versionRef": "main",
                "updatePolicy": "manual",
                "expectedStatus": "broken-link",
            },
        ],
    }


class RegistryPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(SAMPLE.read_text(encoding="utf-8"))
        self.status_registry = _status_fixture_registry()

    def test_sample_registry_is_valid(self) -> None:
        self.assertEqual(validate_registry(self.registry), [])

    def test_duplicate_part_id_is_rejected(self) -> None:
        duplicate = json.loads(json.dumps(self.registry))
        duplicate["parts"][1]["partId"] = duplicate["parts"][0]["partId"]
        issues = validate_registry(duplicate)
        self.assertTrue(any(issue["code"] == "duplicate-part-id" for issue in issues))

    def test_plan_blocks_dirty_and_broken_parts(self) -> None:
        plan = build_sync_plan(self.status_registry)
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
            part = json.loads(json.dumps(self.status_registry["parts"][1]))
            part["source"]["root"] = str(source_root)
            result = preview_local_part(part, repo_root=root)
            self.assertIn(result["status"], {"current", "remote-newer"})

    def test_git_adapter_uses_runner_contract(self) -> None:
        part = self.status_registry["parts"][0]

        def runner(args, cwd):
            if args[:3] == ["git", "status", "--porcelain"]:
                return subprocess.CompletedProcess(args, 0, "", "")
            return subprocess.CompletedProcess(args, 0, "0\t2\n", "")

        result = preview_git_part(part, repo_root=ROOT, runner=runner)
        self.assertEqual(result["status"], "remote-newer")

    def test_reload_matches_project_relative_registry_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            linked_file = root / "parts" / "hair" / "main_hair.blend"
            linked_file.parent.mkdir(parents=True)
            linked_file.write_text("fixture", encoding="utf-8")
            bpy_module = _FakeBpy(root / "integration", ["//../parts/hair/main_hair.blend"])

            result = reload_linked_libraries(
                bpy_module,
                ["parts/hair/main_hair.blend"],
                dry_run=True,
                base_dirs=[root / "samples", root],
            )

            self.assertEqual(result["failed"], [])
            self.assertEqual(len(result["reloaded"]), 1)
            self.assertEqual(result["skipped"], [])

    def test_auto_reload_targets_only_safe_current_or_remote_newer_parts(self) -> None:
        plan = build_sync_plan(self.status_registry)
        self.assertEqual(
            _auto_reload_target_paths(plan),
            ["parts/hair/main_hair.blend", "parts/body/base_body.blend"],
        )

    def test_japanese_ui_translation_table_covers_core_controls(self) -> None:
        ja = BLPVM_TRANSLATIONS["ja_JP"]
        expected_default_strings = {
            "Linked Parts": "リンク部位",
            "Part Registry": "部位レジストリ",
            "Registry Path": "レジストリパス",
            "Report Path": "レポートパス",
            "Auto Reload Interval": "自動リロード間隔",
            "Preview Link": "リンクをプレビュー",
            "Preview Integrate": "統合をプレビュー",
            "Integrate Link": "リンクを統合",
            "Reload Safe Links": "安全なリンクをリロード",
            "Scanned {count} linked part candidate(s).": "リンク済み部位候補を{count}件スキャンしました。",
        }
        for message, translation in expected_default_strings.items():
            self.assertEqual(ja[("*", message)], translation)

        for operator_label in (
            "Scan Current Links",
            "Add File Candidate",
            "Save Registry",
            "Validate Registry",
            "Build Sync Preview",
            "Start Auto Reload",
            "Stop Auto Reload",
            "Integrate Selected Link",
        ):
            self.assertIn(("Operator", operator_label), ja)

    def test_gui_registry_candidate_defaults_are_valid(self) -> None:
        part = build_registry_part_candidate(
            "parts/hair/main_hair.blend",
            linked_collection="CHR_Hair_Main",
        )
        self.assertEqual(part["owner"], "unassigned")
        self.assertEqual(part["source"]["type"], "local")
        self.assertEqual(part["source"]["root"], ".")
        self.assertEqual(part["versionRef"], "local")
        self.assertEqual(part["updatePolicy"], "manual")
        self.assertEqual(validate_registry(registry_from_parts([part])), [])

    def test_scan_linked_libraries_creates_editable_registry_parts(self) -> None:
        root = ROOT
        bpy_module = _FakeBpy(
            root / "integration",
            ["//../parts/hair/main_hair.blend"],
            collections=[("CHR_Hair_Main", 0)],
        )
        parts = scan_linked_registry_parts(bpy_module, base_dir=root)

        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0]["blendPath"], "parts/hair/main_hair.blend")
        self.assertEqual(parts[0]["linkedCollection"], "CHR_Hair_Main")
        self.assertEqual(parts[0]["partTag"], "Hair")
        self.assertEqual(validate_registry(registry_from_parts(parts)), [])

    def test_integrate_linked_libraries_dry_run_reports_target_without_localizing(self) -> None:
        root = ROOT
        bpy_module = _FakeBpy(
            root / "integration",
            ["//../parts/hair/main_hair.blend"],
            collections=[("CHR_Hair_Main", 0)],
        )

        result = integrate_linked_libraries(
            bpy_module,
            ["parts/hair/main_hair.blend"],
            dry_run=True,
            base_dirs=[root / "samples", root],
        )

        self.assertEqual(result["failed"], [])
        self.assertEqual(len(result["integrated"]), 1)
        self.assertEqual(result["integrated"][0]["datablockCount"], 1)
        self.assertIsNotNone(bpy_module.data.collections[0].library)
        self.assertEqual(bpy_module.data.collections[0].make_local_count, 0)

    def test_integrate_linked_libraries_makes_matching_datablocks_local(self) -> None:
        root = ROOT
        bpy_module = _FakeBpy(
            root / "integration",
            ["//../parts/hair/main_hair.blend", "//../parts/body/base_body.blend"],
            collections=[("CHR_Hair_Main", 0), ("CHR_Body_Base", 1)],
        )

        result = integrate_linked_libraries(
            bpy_module,
            ["parts/hair/main_hair.blend"],
            dry_run=False,
            base_dirs=[root / "samples", root],
        )

        self.assertEqual(result["failed"], [])
        self.assertEqual(result["integrated"][0]["localizedCount"], 1)
        self.assertIsNone(bpy_module.data.collections[0].library)
        self.assertIsNotNone(bpy_module.data.collections[1].library)
        self.assertEqual(bpy_module.data.collections[1].make_local_count, 0)

class _FakeLibrary:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.reload_count = 0

    def reload(self) -> None:
        self.reload_count += 1


class _FakeData:
    def __init__(self, filepaths: list[str], collections: list[tuple[str, int]] | None = None) -> None:
        self.filepath = ""
        self.libraries = [_FakeLibrary(filepath) for filepath in filepaths]
        self.collections = [
            _FakeCollection(name, self.libraries[library_index])
            for name, library_index in collections or []
        ]


class _FakeCollection:
    def __init__(self, name: str, library: _FakeLibrary) -> None:
        self.name = name
        self.library = library
        self.make_local_count = 0

    def make_local(self) -> None:
        self.make_local_count += 1
        self.library = None


class _FakePath:
    def __init__(self, blend_dir: Path) -> None:
        self.blend_dir = blend_dir

    def abspath(self, path: str) -> str:
        if path.startswith("//"):
            return str((self.blend_dir / path[2:]).resolve())
        if Path(path).is_absolute():
            return str(Path(path).resolve())
        return str((self.blend_dir / path).resolve())


class _FakeBpy:
    def __init__(self, blend_dir: Path, filepaths: list[str], collections: list[tuple[str, int]] | None = None) -> None:
        self.data = _FakeData(filepaths, collections=collections)
        self.path = _FakePath(blend_dir)


if __name__ == "__main__":
    unittest.main()
