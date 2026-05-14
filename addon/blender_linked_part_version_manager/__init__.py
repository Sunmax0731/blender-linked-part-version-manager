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

from .blender.link import inspect_linked_libraries, reload_linked_libraries
from .core.plan import build_sync_plan, summarize_plan
from .core.registry import load_registry_file, validate_registry
from .report import build_dry_run_report, write_json_report


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

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "registry_path")
        layout.prop(self, "report_path")


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
        registry = load_registry_file(Path(bpy.path.abspath(prefs.registry_path)))
        link_state = inspect_linked_libraries(bpy)
        plan = build_sync_plan(registry, link_state=link_state)
        target_paths = [
            item["part"]["blendPath"]
            for item in plan
            if "reload-link" in item["plannedActions"] and item["risk"] != "blocked"
        ]
        result = reload_linked_libraries(bpy, target_paths, dry_run=self.dry_run)
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
        layout.prop(prefs, "report_path")
        preview = getattr(context.scene, "blpvm_preview_json", "")
        if preview:
            box = layout.box()
            for line in preview.splitlines()[:12]:
                box.label(text=line[:100])


classes = (
    BLPVM_Preferences,
    BLPVM_OT_validate_registry,
    BLPVM_OT_build_sync_preview,
    BLPVM_OT_reload_links,
    BLPVM_PT_registry_panel,
)


def register():
    if bpy is None:
        return
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.blpvm_preview_json = bpy.props.StringProperty(name="BLPVM Preview JSON", default="")


def unregister():
    if bpy is None:
        return
    if hasattr(bpy.types.Scene, "blpvm_preview_json"):
        del bpy.types.Scene.blpvm_preview_json
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
