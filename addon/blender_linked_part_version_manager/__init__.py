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

from .blender.link import inspect_linked_libraries, reload_linked_libraries, resolve_target_paths
from .core.plan import build_sync_plan, summarize_plan
from .core.registry import load_registry_file, validate_registry
from .report import build_dry_run_report, write_json_report


AUTO_RELOAD_STATUSES = {"current", "remote-newer"}
_AUTO_RELOAD_RUNNING = False
_AUTO_RELOAD_MTIMES: dict[str, int] = {}


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
        base_dirs = [registry_path.parent, registry_path.parent.parent]
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
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


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
    base_dirs = [registry_path.parent, registry_path.parent.parent]
    return prefs, registry_path, base_dirs, _auto_reload_target_paths(plan)


def _reset_auto_reload_mtimes(context):
    _AUTO_RELOAD_MTIMES.clear()
    prefs = context.preferences.addons[__name__].preferences
    registry_path = Path(bpy.path.abspath(prefs.registry_path))
    registry = load_registry_file(registry_path)
    plan = build_sync_plan(registry, link_state=inspect_linked_libraries(bpy))
    base_dirs = [registry_path.parent, registry_path.parent.parent]
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
