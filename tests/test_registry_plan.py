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
    inspect_linkable_data_from_file,
    link_collection_from_file,
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

    def test_linkable_data_prefers_production_objects_over_ref_collection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blend_file = root / "base.blend"
            blend_file.write_text("fixture", encoding="utf-8")
            bpy_module = _FakeBpy(
                root,
                [],
                available_collections=["ref"],
                available_objects=["Armature", "base_body", "base_face", "Camera", "Light", "ref4_side2"],
            )

            result = inspect_linkable_data_from_file(bpy_module, "base.blend", base_dirs=[root])

            self.assertEqual(result["failed"], [])
            self.assertEqual(result["recommendedCollection"], None)
            self.assertEqual(result["recommendedObjects"], ["Armature", "base_body", "base_face"])

    def test_link_candidate_links_production_objects_when_default_collection_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blend_file = root / "base.blend"
            blend_file.write_text("fixture", encoding="utf-8")
            bpy_module = _FakeBpy(
                root,
                [],
                available_collections=["ref"],
                available_objects=["Armature", "base_body", "base_face", "Camera", "Light", "ref4_side2"],
            )

            result = link_collection_from_file(
                bpy_module,
                "base.blend",
                "base",
                dry_run=False,
                base_dirs=[root],
            )

            self.assertEqual(result["failed"], [])
            self.assertEqual(result["linkMode"], "objects")
            self.assertEqual(result["linkedCollection"], "base")
            self.assertEqual(result["linkedObjects"], ["Armature", "base_body", "base_face"])
            target = bpy_module.context.collection.children[0]
            self.assertEqual(target.name, "base")
            self.assertEqual([obj.name for obj in target.objects], ["Armature", "base_body", "base_face"])

    def test_linkable_data_reports_explicit_non_model_candidate_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blend_file = root / "lighting_refs.blend"
            blend_file.write_text("fixture", encoding="utf-8")
            bpy_module = _FakeBpy(
                root,
                [],
                available_collections=["ref"],
                available_objects=[
                    _FakeAvailableObject("ref_front", "EMPTY", empty_display_type="IMAGE"),
                    _FakeAvailableObject("Key_Light", "LIGHT"),
                    _FakeAvailableObject("Floor", "MESH"),
                ],
            )

            result = inspect_linkable_data_from_file(bpy_module, "lighting_refs.blend", base_dirs=[root])

            by_name = {detail["name"]: detail for detail in result["availableObjectDetails"]}
            self.assertEqual(result["recommendedObjects"], [])
            self.assertEqual(by_name["ref_front"]["category"], "reference-image")
            self.assertEqual(by_name["ref_front"]["selection"], "explicit")
            self.assertEqual(by_name["Key_Light"]["category"], "light")
            self.assertEqual(by_name["Key_Light"]["selection"], "explicit")
            self.assertEqual(by_name["Floor"]["category"], "floor-helper")
            self.assertEqual(by_name["Floor"]["selection"], "excluded")
            self.assertIn("ref_front", result["warnings"][1])
            self.assertIn("Floor", result["warnings"][2])

    def test_link_candidate_does_not_implicitly_select_non_model_objects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blend_file = root / "lighting_refs.blend"
            blend_file.write_text("fixture", encoding="utf-8")
            bpy_module = _FakeBpy(
                root,
                [],
                available_collections=["ref"],
                available_objects=[
                    _FakeAvailableObject("ref_front", "EMPTY", empty_display_type="IMAGE"),
                    _FakeAvailableObject("Key_Light", "LIGHT"),
                ],
            )

            result = link_collection_from_file(
                bpy_module,
                "lighting_refs.blend",
                "lighting_refs",
                dry_run=True,
                base_dirs=[root],
            )

            self.assertEqual(result["linkMode"], None)
            self.assertTrue(result["failed"])
            self.assertIn("Explicit object candidates: ref_front, Key_Light", result["failed"][0]["error"])

    def test_link_candidate_links_explicit_light_object(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blend_file = root / "lighting_refs.blend"
            blend_file.write_text("fixture", encoding="utf-8")
            bpy_module = _FakeBpy(
                root,
                [],
                available_collections=["ref"],
                available_objects=[
                    _FakeAvailableObject("ref_front", "EMPTY", empty_display_type="IMAGE"),
                    _FakeAvailableObject("Key_Light", "LIGHT"),
                ],
            )

            result = link_collection_from_file(
                bpy_module,
                "lighting_refs.blend",
                "Key_Light",
                dry_run=False,
                base_dirs=[root],
            )

            self.assertEqual(result["failed"], [])
            self.assertEqual(result["linkMode"], "objects")
            self.assertEqual(result["linkedObjects"], ["Key_Light"])
            target = bpy_module.context.collection.children[0]
            self.assertEqual(target.name, "Key_Light")
            self.assertEqual([obj.name for obj in target.objects], ["Key_Light"])

    def test_link_candidate_rejects_explicit_floor_helper_object(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blend_file = root / "lighting_refs.blend"
            blend_file.write_text("fixture", encoding="utf-8")
            bpy_module = _FakeBpy(
                root,
                [],
                available_collections=["ref"],
                available_objects=[
                    _FakeAvailableObject("Floor", "MESH"),
                ],
            )

            result = link_collection_from_file(
                bpy_module,
                "lighting_refs.blend",
                "Floor",
                dry_run=False,
                base_dirs=[root],
            )

            self.assertEqual(result["linkMode"], None)
            self.assertTrue(result["failed"])
            self.assertIn("not supported", result["failed"][0]["error"])
            self.assertEqual(len(bpy_module.context.collection.children), 0)

    def test_link_candidate_does_not_fallback_to_first_ref_collection_for_missing_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blend_file = root / "base.blend"
            blend_file.write_text("fixture", encoding="utf-8")
            bpy_module = _FakeBpy(
                root,
                [],
                available_collections=["ref"],
                available_objects=["Armature", "base_body"],
            )

            result = link_collection_from_file(
                bpy_module,
                "base.blend",
                "not_in_file",
                dry_run=False,
                base_dirs=[root],
            )

            self.assertEqual(result["linkedCollection"], None)
            self.assertEqual(result["linkedObjects"], [])
            self.assertTrue(result["failed"])
            self.assertEqual(len(bpy_module.context.collection.children), 0)

    def test_link_candidate_links_requested_collection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blend_file = root / "body.blend"
            blend_file.write_text("fixture", encoding="utf-8")
            bpy_module = _FakeBpy(
                root,
                [],
                available_collections=["ref", "CHR_Body_Base"],
                available_objects=["Camera", "Light"],
            )

            result = link_collection_from_file(
                bpy_module,
                "body.blend",
                "CHR_Body_Base",
                dry_run=False,
                base_dirs=[root],
            )

            self.assertEqual(result["failed"], [])
            self.assertEqual(result["linkMode"], "collection")
            self.assertEqual(result["linkedCollection"], "CHR_Body_Base")
            self.assertEqual([child.name for child in bpy_module.context.collection.children], ["CHR_Body_Base"])

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
    def __init__(
        self,
        filepaths: list[str],
        collections: list[tuple[str, int]] | None = None,
        available_collections: list[str] | None = None,
        available_objects: list[str] | None = None,
    ) -> None:
        self.filepath = ""
        self.libraries = _FakeLibraries(
            [_FakeLibrary(filepath) for filepath in filepaths],
            self,
            available_collections=available_collections,
            available_objects=available_objects,
        )
        self.collections = _FakeCollectionContainer([
            _FakeCollection(name, self.libraries[library_index])
            for name, library_index in collections or []
        ])
        self.objects = _FakeObjectContainer()


class _FakeLibraries(list):
    def __init__(
        self,
        libraries: list[_FakeLibrary],
        data: _FakeData,
        *,
        available_collections: list[str] | None = None,
        available_objects: list[str] | None = None,
    ) -> None:
        super().__init__(libraries)
        self._data = data
        self._available_collections = available_collections or []
        self._available_objects = available_objects or []

    def load(self, filepath: str, link: bool = True):
        return _FakeLibraryLoadContext(
            self._data,
            filepath,
            self._available_collections,
            self._available_objects,
        )


class _FakeLibraryLoadContext:
    def __init__(
        self,
        data: _FakeData,
        filepath: str,
        available_collections: list[str],
        available_objects: list[str],
    ) -> None:
        self.data = data
        self.library = _FakeLibrary(filepath)
        self.available_collections = available_collections
        self.available_objects = available_objects
        self.data_to = _FakeDataTo()

    def __enter__(self):
        data_from = _FakeDataFrom(self.available_collections, self.available_objects)
        return data_from, self.data_to

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is not None:
            return False
        self.data.libraries.append(self.library)
        self.data_to.collections = [
            _FakeCollection(name, self.library)
            for name in self.data_to.collections
        ]
        self.data.collections.extend(self.data_to.collections)
        self.data_to.objects = [
            _FakeObject(name, self.library)
            for name in self.data_to.objects
        ]
        self.data.objects.extend(self.data_to.objects)
        return False


class _FakeDataFrom:
    def __init__(self, collections: list[str], objects: list[str]) -> None:
        self.collections = collections
        self.objects = objects


class _FakeDataTo:
    def __init__(self) -> None:
        self.collections: list[str | _FakeCollection] = []
        self.objects: list[str | _FakeObject] = []


class _FakeCollection:
    def __init__(self, name: str, library: _FakeLibrary | None = None) -> None:
        self.name = name
        self.library = library
        self.make_local_count = 0
        self.children = _FakeCollectionContainer()
        self.objects = _FakeObjectContainer()

    def make_local(self) -> None:
        self.make_local_count += 1
        self.library = None


class _FakeObject:
    def __init__(self, name: str, library: _FakeLibrary | None = None) -> None:
        self.name = name
        self.library = library


class _FakeAvailableObject:
    def __init__(self, name: str, object_type: str, empty_display_type: str = "") -> None:
        self.name = name
        self.type = object_type
        self.empty_display_type = empty_display_type


class _FakeCollectionContainer(list):
    def link(self, collection: _FakeCollection) -> None:
        self.append(collection)

    def new(self, name: str) -> _FakeCollection:
        collection = _FakeCollection(name)
        self.append(collection)
        return collection


class _FakeObjectContainer(list):
    def link(self, obj: _FakeObject) -> None:
        self.append(obj)


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
    def __init__(
        self,
        blend_dir: Path,
        filepaths: list[str],
        collections: list[tuple[str, int]] | None = None,
        available_collections: list[str] | None = None,
        available_objects: list[str] | None = None,
    ) -> None:
        self.data = _FakeData(
            filepaths,
            collections=collections,
            available_collections=available_collections,
            available_objects=available_objects,
        )
        self.path = _FakePath(blend_dir)
        self.context = _FakeContext()


class _FakeContext:
    def __init__(self) -> None:
        self.collection = _FakeCollection("Scene Collection")


if __name__ == "__main__":
    unittest.main()
