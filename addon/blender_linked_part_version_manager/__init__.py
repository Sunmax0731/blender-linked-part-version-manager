from __future__ import annotations

bl_info = {
    "name": "Blender Linked Part Version Manager",
    "author": "Sunmax0731",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Linked Parts",
    "description": "Preview and validate linked part registries before refreshing Blender Link libraries.",
    "category": "Pipeline",
}

import json
from pathlib import Path

try:
    import bpy
except ImportError:  # pragma: no cover - normal unit-test path outside Blender
    bpy = None

from .blender.link import (
    inspect_linked_libraries,
    link_collection_from_file,
    reload_linked_libraries,
    resolve_target_paths,
    scan_linked_registry_parts,
)
from .core.plan import build_sync_plan, summarize_plan
from .core.registry import (
    ALLOWED_UPDATE_POLICIES,
    DEFAULT_TAG_ORDER,
    build_registry_part_candidate,
    load_registry_file,
    registry_from_parts,
    validate_registry,
    write_registry_file,
)
from .report import build_dry_run_report, write_json_report


AUTO_RELOAD_STATUSES = {"current", "remote-newer"}
_AUTO_RELOAD_RUNNING = False
_AUTO_RELOAD_MTIMES: dict[str, int] = {}
TAG_ITEMS = tuple((tag, tag, "") for tag in DEFAULT_TAG_ORDER)
SOURCE_TYPE_ITEMS = (("local", "local", ""), ("git", "git", ""))
UPDATE_POLICY_ITEMS = tuple((policy, policy, "") for policy in sorted(ALLOWED_UPDATE_POLICIES))


class BLPVM_Preferences(bpy.types.AddonPreferences if bpy else object):
    bl_idname = __name__

    registry_path: bpy.props.StringProperty(  # type: ignore[union-attr]
        name="Registry Path",
        subtype="FILE_PATH",
        default="samples/representative-suite.json",
    ) if bpy else ""

    report_path: bpy.props.StringProperty(  # type: ignore[union-attr]
        name="Report Path",
        subtype="FILE_PATH",
        default="dist/blender-dry-run-report.json",
    ) if bpy else ""

    auto_reload_interval: bpy.props.FloatProperty(  # type: ignore[union-attr]
        name="Auto Reload Interval",
        description="Seconds between saved linked .blend file checks",
        default=2.0,
        min=0.5,
        max=60.0,
    ) if bpy else 2.0

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "registry_path")
        layout.prop(self, "report_path")
        layout.prop(self, "auto_reload_interval")


class BLPVM_RegistryPartItem(bpy.types.PropertyGroup if bpy else object):
    part_id: bpy.props.StringProperty(name="partId") if bpy else ""  # type: ignore[union-attr]
    part_tag: bpy.props.EnumProperty(name="partTag", items=TAG_ITEMS, default="Props") if bpy else "Props"  # type: ignore[union-attr]
    display_name: bpy.props.StringProperty(name="displayName") if bpy else ""  # type: ignore[union-attr]
    blend_path: bpy.props.StringProperty(name="blendPath", subtype="FILE_PATH") if bpy else ""  # type: ignore[union-attr]
    linked_collection: bpy.props.StringProperty(name="linkedCollection") if bpy else ""  # type: ignore[union-attr]
    owner: bpy.props.StringProperty(name="owner", default="unassigned") if bpy else "unassigned"  # type: ignore[union-attr]
    source_type: bpy.props.EnumProperty(name="source.type", items=SOURCE_TYPE_ITEMS, default="local") if bpy else "local"  # type: ignore[union-attr]
    source_root: bpy.props.StringProperty(name="source.root", default=".") if bpy else "."  # type: ignore[union-attr]
    source_path: bpy.props.StringProperty(name="source.path") if bpy else ""  # type: ignore[union-attr]
    source_remote: bpy.props.StringProperty(name="source.remote", default="origin") if bpy else "origin"  # type: ignore[union-attr]
    source_branch: bpy.props.StringProperty(name="source.branch", default="main") if bpy else "main"  # type: ignore[union-attr]
    version_ref: bpy.props.StringProperty(name="versionRef", default="local") if bpy else "local"  # type: ignore[union-attr]
    update_policy: bpy.props.EnumProperty(name="updatePolicy", items=UPDATE_POLICY_ITEMS, default="manual") if bpy else "manual"  # type: ignore[union-attr]


class BLPVM_UL_registry_parts(bpy.types.UIList if bpy else object):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)
            row.label(text=item.part_tag, icon="LINKED")
            row.label(text=item.display_name or item.part_id or item.blend_path)
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text=item.part_tag)


class BLPVM_OT_scan_current_links(bpy.types.Operator if bpy else object):
    bl_idname = "blpvm.scan_current_links"
    bl_label = "Scan Current Links"
    bl_description = "Scan current linked .blend libraries and create editable registry candidates"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        registry_path = Path(bpy.path.abspath(prefs.registry_path))
        parts = scan_linked_registry_parts(bpy, base_dir=_registry_relative_root(registry_path))
        while len(context.scene.blpvm_registry_parts):
            context.scene.blpvm_registry_parts.remove(0)
        for part in parts:
            _fill_registry_item(context.scene.blpvm_registry_parts.add(), part)
        context.scene.blpvm_registry_index = 0 if parts else -1
        context.scene.blpvm_preview_json = json.dumps({"scannedParts": len(parts)}, ensure_ascii=False, indent=2)
        self.report({"INFO"}, f"Scanned {len(parts)} linked part candidate(s).")
        return {"FINISHED"}


class BLPVM_OT_add_link_candidate(bpy.types.Operator if bpy else object):
    bl_idname = "blpvm.add_link_candidate"
    bl_label = "Add File Candidate"
    bl_description = "Choose a .blend file and add it as an editable local registry candidate"

    filepath: bpy.props.StringProperty(name="Blend File", subtype="FILE_PATH") if bpy else ""  # type: ignore[union-attr]
    linked_collection: bpy.props.StringProperty(name="Linked Collection") if bpy else ""  # type: ignore[union-attr]
    part_tag: bpy.props.EnumProperty(name="partTag", items=TAG_ITEMS, default="Props") if bpy else "Props"  # type: ignore[union-attr]

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        if not self.filepath:
            self.report({"ERROR"}, "Choose a .blend file first.")
            return {"CANCELLED"}
        prefs = context.preferences.addons[__name__].preferences
        registry_path = Path(bpy.path.abspath(prefs.registry_path))
        resolved = Path(bpy.path.abspath(self.filepath))
        blend_path = _display_path_for_registry(resolved, _registry_relative_root(registry_path))
        existing_ids = {item.part_id for item in context.scene.blpvm_registry_parts if item.part_id}
        part = build_registry_part_candidate(
            blend_path,
            linked_collection=self.linked_collection or resolved.stem,
            part_tag=self.part_tag,
            existing_ids=existing_ids,
        )
        item = context.scene.blpvm_registry_parts.add()
        _fill_registry_item(item, part)
        context.scene.blpvm_registry_index = len(context.scene.blpvm_registry_parts) - 1
        context.scene.blpvm_preview_json = json.dumps({"addedCandidate": part}, ensure_ascii=False, indent=2)
        self.report({"INFO"}, f"Added registry candidate: {part['partId']}.")
        return {"FINISHED"}


class BLPVM_OT_remove_registry_part(bpy.types.Operator if bpy else object):
    bl_idname = "blpvm.remove_registry_part"
    bl_label = "Remove Candidate"
    bl_description = "Remove the selected registry candidate from the editable list only"

    def execute(self, context):
        index = context.scene.blpvm_registry_index
        parts = context.scene.blpvm_registry_parts
        if index < 0 or index >= len(parts):
            self.report({"ERROR"}, "No registry candidate is selected.")
            return {"CANCELLED"}
        parts.remove(index)
        context.scene.blpvm_registry_index = min(index, len(parts) - 1)
        self.report({"INFO"}, "Removed registry candidate.")
        return {"FINISHED"}


class BLPVM_OT_save_registry(bpy.types.Operator if bpy else object):
    bl_idname = "blpvm.save_registry"
    bl_label = "Save Registry"
    bl_description = "Save editable registry candidates to the configured Registry Path"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        registry_path = Path(bpy.path.abspath(prefs.registry_path))
        parts = [_registry_item_to_part(item) for item in context.scene.blpvm_registry_parts]
        registry = registry_from_parts(parts, integration_file=_current_blend_display_path(registry_path))
        issues = validate_registry(registry)
        if issues:
            context.scene.blpvm_preview_json = json.dumps({"issues": issues}, ensure_ascii=False, indent=2)
            self.report({"ERROR"}, f"Registry has {len(issues)} issue(s); fix editable fields before saving.")
            return {"CANCELLED"}
        write_registry_file(registry_path, registry)
        context.scene.blpvm_preview_json = json.dumps(
            {"savedRegistry": str(registry_path), "parts": len(parts)},
            ensure_ascii=False,
            indent=2,
        )
        self.report({"INFO"}, f"Saved registry with {len(parts)} part(s).")
        return {"FINISHED"}


class BLPVM_OT_link_selected_candidate(bpy.types.Operator if bpy else object):
    bl_idname = "blpvm.link_selected_candidate"
    bl_label = "Link Selected Candidate"
    bl_description = "Explicitly link the selected .blend collection into the current Blender tree without saving the file"

    dry_run: bpy.props.BoolProperty(name="Dry Run", default=True) if bpy else True  # type: ignore[union-attr]

    def execute(self, context):
        index = context.scene.blpvm_registry_index
        parts = context.scene.blpvm_registry_parts
        if index < 0 or index >= len(parts):
            self.report({"ERROR"}, "No registry candidate is selected.")
            return {"CANCELLED"}
        item = parts[index]
        prefs = context.preferences.addons[__name__].preferences
        registry_path = Path(bpy.path.abspath(prefs.registry_path))
        result = link_collection_from_file(
            bpy,
            item.blend_path,
            item.linked_collection,
            dry_run=self.dry_run,
            target_collection=context.collection,
            base_dirs=_registry_base_dirs(registry_path),
        )
        context.scene.blpvm_preview_json = json.dumps(result, ensure_ascii=False, indent=2)
        if result["failed"]:
            self.report({"ERROR"}, f"Link candidate failed: {result['failed'][0]['error']}")
            return {"CANCELLED"}
        self.report({"INFO"}, "Link preview ready." if self.dry_run else "Linked selected collection into the scene tree.")
        return {"FINISHED"}


class BLPVM_OT_validate_registry(bpy.types.Operator if bpy else object):
    bl_idname = "blpvm.validate_registry"
    bl_label = "Validate Registry"
    bl_description = "Validate the linked part registry without modifying .blend files"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        registry_path = Path(bpy.path.abspath(prefs.registry_path))
        registry = load_registry_file(registry_path)
        issues = validate_registry(registry)
        if issues:
            self.report({"ERROR"}, f"Registry has {len(issues)} issue(s).")
            context.scene.blpvm_preview_json = json.dumps({"issues": issues}, ensure_ascii=False, indent=2)
            return {"CANCELLED"}
        self.report({"INFO"}, f"Registry OK: {len(registry.get('parts', []))} part(s).")
        context.scene.blpvm_preview_json = json.dumps({"issues": []}, ensure_ascii=False, indent=2)
        return {"FINISHED"}


class BLPVM_OT_build_sync_preview(bpy.types.Operator if bpy else object):
    bl_idname = "blpvm.build_sync_preview"
    bl_label = "Build Sync Preview"
    bl_description = "Create a dry-run sync plan from the registry and current Blender Link state"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        registry_path = Path(bpy.path.abspath(prefs.registry_path))
        report_path = Path(bpy.path.abspath(prefs.report_path))
        registry = load_registry_file(registry_path)
        issues = validate_registry(registry)
        link_state = inspect_linked_libraries(bpy)
        plan = build_sync_plan(registry, link_state=link_state)
        summary = summarize_plan(plan)
        report = build_dry_run_report(
            registry=registry,
            plan=plan,
            registry_path=str(registry_path),
            validation_issues=issues,
            link_state=link_state,
        )
        write_json_report(report_path, report)
        context.scene.blpvm_preview_json = json.dumps(
            {"summary": summary, "reportPath": str(report_path)},
            ensure_ascii=False,
            indent=2,
        )
        if summary["blockedParts"]:
            self.report({"WARNING"}, f"Preview written with {summary['blockedParts']} blocked part(s).")
        else:
            self.report({"INFO"}, "Preview written. No blocked parts.")
        return {"FINISHED"}


class BLPVM_OT_start_auto_reload(bpy.types.Operator if bpy else object):
    bl_idname = "blpvm.start_auto_reload"
    bl_label = "Start Auto Reload"
    bl_description = "Poll saved linked .blend files and reload changed safe links automatically"

    def execute(self, context):
        global _AUTO_RELOAD_RUNNING
        _AUTO_RELOAD_RUNNING = True
        _reset_auto_reload_mtimes(context)
        if not bpy.app.timers.is_registered(_auto_reload_timer):
            prefs = context.preferences.addons[__name__].preferences
            bpy.app.timers.register(_auto_reload_timer, first_interval=float(prefs.auto_reload_interval))
        context.scene.blpvm_auto_reload_status = "Auto Reload running. Unsaved source edits are not visible until saved."
        self.report({"INFO"}, "Auto Reload started.")
        return {"FINISHED"}


class BLPVM_OT_stop_auto_reload(bpy.types.Operator if bpy else object):
    bl_idname = "blpvm.stop_auto_reload"
    bl_label = "Stop Auto Reload"
    bl_description = "Stop automatic saved linked .blend reload polling"

    def execute(self, context):
        global _AUTO_RELOAD_RUNNING
        _AUTO_RELOAD_RUNNING = False
        if bpy.app.timers.is_registered(_auto_reload_timer):
            bpy.app.timers.unregister(_auto_reload_timer)
        context.scene.blpvm_auto_reload_status = "Auto Reload stopped."
        self.report({"INFO"}, "Auto Reload stopped.")
        return {"FINISHED"}


class BLPVM_OT_reload_links(bpy.types.Operator if bpy else object):
    bl_idname = "blpvm.reload_links"
    bl_label = "Reload Safe Links"
    bl_description = "Reload linked libraries only for non-blocked parts after preview"

    dry_run: bpy.props.BoolProperty(  # type: ignore[union-attr]
        name="Dry Run",
        default=True,
    ) if bpy else True

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        registry_path = Path(bpy.path.abspath(prefs.registry_path))
        registry = load_registry_file(registry_path)
        link_state = inspect_linked_libraries(bpy)
        plan = build_sync_plan(registry, link_state=link_state)
        target_paths = [
            item["part"]["blendPath"]
            for item in plan
            if "reload-link" in item["plannedActions"] and item["risk"] != "blocked"
        ]
        base_dirs = _registry_base_dirs(registry_path)
        result = reload_linked_libraries(bpy, target_paths, dry_run=self.dry_run, base_dirs=base_dirs)
        context.scene.blpvm_preview_json = json.dumps(result, ensure_ascii=False, indent=2)
        if result["failed"]:
            self.report({"ERROR"}, f"Reload failed for {len(result['failed'])} library path(s).")
            return {"CANCELLED"}
        self.report({"INFO"}, f"Reload {'previewed' if self.dry_run else 'completed'} for {len(result['reloaded'])} path(s).")
        return {"FINISHED"}


class BLPVM_PT_registry_panel(bpy.types.Panel if bpy else object):
    bl_label = "Part Registry"
    bl_idname = "BLPVM_PT_registry_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Linked Parts"

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons[__name__].preferences
        layout.prop(prefs, "registry_path")
        row = layout.row(align=True)
        row.operator("blpvm.scan_current_links", icon="VIEWZOOM")
        row.operator("blpvm.save_registry", icon="CHECKMARK")
        if hasattr(context.scene, "blpvm_registry_parts"):
            layout.template_list(
                "BLPVM_UL_registry_parts",
                "",
                context.scene,
                "blpvm_registry_parts",
                context.scene,
                "blpvm_registry_index",
                rows=4,
            )
            selected = _selected_registry_item(context)
            row = layout.row(align=True)
            row.operator("blpvm.add_link_candidate", icon="FILE_FOLDER")
            row.operator("blpvm.remove_registry_part", icon="REMOVE")
            row = layout.row(align=True)
            row.operator("blpvm.link_selected_candidate", text="Preview Link", icon="LINKED").dry_run = True
            row.operator("blpvm.link_selected_candidate", text="Link Candidate", icon="LINKED").dry_run = False
            if selected:
                box = layout.box()
                box.prop(selected, "part_id")
                box.prop(selected, "part_tag")
                box.prop(selected, "display_name")
                box.prop(selected, "blend_path")
                box.prop(selected, "linked_collection")
                box.prop(selected, "owner")
                box.prop(selected, "source_type")
                if selected.source_type == "git":
                    box.prop(selected, "source_remote")
                    box.prop(selected, "source_branch")
                    box.prop(selected, "source_path")
                    box.prop(selected, "version_ref")
                else:
                    box.prop(selected, "source_root")
                    box.prop(selected, "source_path")
                    box.prop(selected, "version_ref")
                box.prop(selected, "update_policy")
        row = layout.row(align=True)
        row.operator("blpvm.validate_registry", icon="CHECKMARK")
        row.operator("blpvm.build_sync_preview", icon="VIEWZOOM")
        row = layout.row(align=True)
        row.operator("blpvm.reload_links", text="Preview Reload", icon="FILE_REFRESH").dry_run = True
        row.operator("blpvm.reload_links", text="Reload Safe Links", icon="CHECKMARK").dry_run = False
        row = layout.row(align=True)
        row.operator("blpvm.start_auto_reload", icon="PLAY")
        row.operator("blpvm.stop_auto_reload", icon="PAUSE")
        layout.prop(prefs, "auto_reload_interval")
        layout.prop(prefs, "report_path")
        status = getattr(context.scene, "blpvm_auto_reload_status", "")
        if status:
            layout.label(text=status[:100], icon="INFO")
        preview = getattr(context.scene, "blpvm_preview_json", "")
        if preview:
            box = layout.box()
            for line in preview.splitlines()[:12]:
                box.label(text=line[:100])


classes = (
    BLPVM_Preferences,
    BLPVM_RegistryPartItem,
    BLPVM_UL_registry_parts,
    BLPVM_OT_scan_current_links,
    BLPVM_OT_add_link_candidate,
    BLPVM_OT_remove_registry_part,
    BLPVM_OT_save_registry,
    BLPVM_OT_link_selected_candidate,
    BLPVM_OT_validate_registry,
    BLPVM_OT_build_sync_preview,
    BLPVM_OT_start_auto_reload,
    BLPVM_OT_stop_auto_reload,
    BLPVM_OT_reload_links,
    BLPVM_PT_registry_panel,
)


def register():
    if bpy is None:
        return
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.blpvm_preview_json = bpy.props.StringProperty(name="BLPVM Preview JSON", default="")
    bpy.types.Scene.blpvm_auto_reload_status = bpy.props.StringProperty(name="BLPVM Auto Reload Status", default="")
    bpy.types.Scene.blpvm_registry_parts = bpy.props.CollectionProperty(type=BLPVM_RegistryPartItem)
    bpy.types.Scene.blpvm_registry_index = bpy.props.IntProperty(name="BLPVM Registry Index", default=-1)


def unregister():
    if bpy is None:
        return
    global _AUTO_RELOAD_RUNNING
    _AUTO_RELOAD_RUNNING = False
    if bpy.app.timers.is_registered(_auto_reload_timer):
        bpy.app.timers.unregister(_auto_reload_timer)
    if hasattr(bpy.types.Scene, "blpvm_preview_json"):
        del bpy.types.Scene.blpvm_preview_json
    if hasattr(bpy.types.Scene, "blpvm_auto_reload_status"):
        del bpy.types.Scene.blpvm_auto_reload_status
    if hasattr(bpy.types.Scene, "blpvm_registry_parts"):
        del bpy.types.Scene.blpvm_registry_parts
    if hasattr(bpy.types.Scene, "blpvm_registry_index"):
        del bpy.types.Scene.blpvm_registry_index
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


def _fill_registry_item(item, part: dict) -> None:
    item.part_id = part.get("partId", "")
    item.part_tag = part.get("partTag", "Props")
    item.display_name = part.get("displayName", "")
    item.blend_path = part.get("blendPath", "")
    item.linked_collection = part.get("linkedCollection", "")
    item.owner = part.get("owner", "unassigned")
    source = part.get("source") or {}
    item.source_type = source.get("type", "local")
    item.source_root = source.get("root", ".")
    item.source_path = source.get("path", part.get("blendPath", ""))
    item.source_remote = source.get("remote", "origin")
    item.source_branch = source.get("branch", "main")
    item.version_ref = part.get("versionRef", "local")
    item.update_policy = part.get("updatePolicy", "manual")


def _registry_item_to_part(item) -> dict:
    source_path = item.source_path or item.blend_path
    if item.source_type == "git":
        source = {
            "type": "git",
            "remote": item.source_remote or "origin",
            "branch": item.source_branch or "main",
            "path": source_path,
        }
    else:
        source = {
            "type": "local",
            "root": item.source_root or ".",
            "path": source_path,
        }
    return {
        "partId": item.part_id,
        "partTag": item.part_tag,
        "displayName": item.display_name,
        "blendPath": item.blend_path,
        "linkedCollection": item.linked_collection,
        "owner": item.owner or "unassigned",
        "source": source,
        "versionRef": item.version_ref or ("main" if item.source_type == "git" else "local"),
        "updatePolicy": item.update_policy or "manual",
    }


def _selected_registry_item(context):
    index = context.scene.blpvm_registry_index
    parts = context.scene.blpvm_registry_parts
    if index < 0 or index >= len(parts):
        return None
    return parts[index]


def _registry_relative_root(registry_path: Path) -> Path:
    if registry_path.parent.name.lower() == "samples":
        return registry_path.parent.parent
    return registry_path.parent


def _registry_base_dirs(registry_path: Path) -> list[Path]:
    root = _registry_relative_root(registry_path)
    return [registry_path.parent, root]


def _display_path_for_registry(path: Path, base_dir: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(base_dir.resolve()).as_posix()
    except ValueError:
        return str(resolved).replace("\\", "/")


def _current_blend_display_path(registry_path: Path) -> str | None:
    filepath = getattr(getattr(bpy, "data", None), "filepath", "")
    if not filepath:
        return None
    return _display_path_for_registry(Path(bpy.path.abspath(filepath)), _registry_relative_root(registry_path))


def _auto_reload_target_paths(plan):
    return [
        item["part"]["blendPath"]
        for item in plan
        if item["status"] in AUTO_RELOAD_STATUSES and item["risk"] != "blocked"
    ]


def _safe_auto_reload_context():
    prefs = bpy.context.preferences.addons[__name__].preferences
    registry_path = Path(bpy.path.abspath(prefs.registry_path))
    registry = load_registry_file(registry_path)
    plan = build_sync_plan(registry, link_state=inspect_linked_libraries(bpy))
    base_dirs = _registry_base_dirs(registry_path)
    return prefs, registry_path, base_dirs, _auto_reload_target_paths(plan)


def _reset_auto_reload_mtimes(context):
    _AUTO_RELOAD_MTIMES.clear()
    prefs = context.preferences.addons[__name__].preferences
    registry_path = Path(bpy.path.abspath(prefs.registry_path))
    registry = load_registry_file(registry_path)
    plan = build_sync_plan(registry, link_state=inspect_linked_libraries(bpy))
    base_dirs = _registry_base_dirs(registry_path)
    for normalized, resolved in resolve_target_paths(bpy, _auto_reload_target_paths(plan), base_dirs=base_dirs).items():
        path = Path(resolved)
        if path.exists():
            _AUTO_RELOAD_MTIMES[normalized] = path.stat().st_mtime_ns


def _auto_reload_timer():
    if not _AUTO_RELOAD_RUNNING:
        return None
    try:
        prefs, _registry_path, base_dirs, target_paths = _safe_auto_reload_context()
        changed_paths = []
        for normalized, resolved in resolve_target_paths(bpy, target_paths, base_dirs=base_dirs).items():
            path = Path(resolved)
            if not path.exists():
                continue
            mtime = path.stat().st_mtime_ns
            previous = _AUTO_RELOAD_MTIMES.get(normalized)
            _AUTO_RELOAD_MTIMES[normalized] = mtime
            if previous is not None and mtime > previous:
                changed_paths.append(resolved)

        if changed_paths:
            result = reload_linked_libraries(bpy, changed_paths, dry_run=False)
            bpy.context.scene.blpvm_preview_json = json.dumps({"autoReload": result}, ensure_ascii=False, indent=2)
            bpy.context.scene.blpvm_auto_reload_status = f"Auto Reload reloaded {len(result['reloaded'])} file(s)."
            _redraw_viewports()
        else:
            bpy.context.scene.blpvm_auto_reload_status = "Auto Reload watching saved linked .blend files."
        return float(prefs.auto_reload_interval)
    except Exception as exc:  # pragma: no cover - depends on Blender runtime context
        bpy.context.scene.blpvm_auto_reload_status = f"Auto Reload error: {exc}"
        return 5.0


def _redraw_viewports():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


if __name__ == "__main__":
    register()
