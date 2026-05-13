from __future__ import annotations

from pathlib import Path
from typing import Any


def inspect_linked_libraries(bpy_module: Any, registry: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    libraries = []
    for library in getattr(getattr(bpy_module, "data", None), "libraries", []):
        filepath = getattr(library, "filepath", "")
        libraries.append(
            {
                "filepath": filepath,
                "resolvedPath": _abspath(bpy_module, filepath),
                "status": "current" if Path(_abspath(bpy_module, filepath)).exists() else "broken-link",
            }
        )

    if not registry:
        return libraries

    state_by_path = {_normalize(item["resolvedPath"]): item for item in libraries}
    part_states = []
    for part in registry.get("parts", []):
        blend_path = _normalize(_abspath(bpy_module, part.get("blendPath", "")))
        state = state_by_path.get(blend_path)
        part_states.append(
            {
                "partId": part.get("partId"),
                "blendPath": part.get("blendPath"),
                "status": state["status"] if state else "missing-link",
                "linkedCollection": part.get("linkedCollection"),
            }
        )
    return part_states


def reload_linked_libraries(bpy_module: Any, target_paths: list[str], *, dry_run: bool = True) -> dict[str, Any]:
    targets = {_normalize(_abspath(bpy_module, path)) for path in target_paths}
    result = {"dryRun": dry_run, "reloaded": [], "skipped": [], "failed": []}
    for library in getattr(getattr(bpy_module, "data", None), "libraries", []):
        resolved = _normalize(_abspath(bpy_module, getattr(library, "filepath", "")))
        if resolved not in targets:
            result["skipped"].append(resolved)
            continue
        if dry_run:
            result["reloaded"].append(resolved)
            continue
        try:
            library.reload()
            result["reloaded"].append(resolved)
        except Exception as exc:  # pragma: no cover - depends on Blender runtime
            result["failed"].append({"path": resolved, "error": str(exc)})
    return result


def _abspath(bpy_module: Any, path: str) -> str:
    if not path:
        return ""
    path_api = getattr(bpy_module, "path", None)
    if path_api and hasattr(path_api, "abspath"):
        return path_api.abspath(path)
    return str(Path(path).resolve())


def _normalize(path: str) -> str:
    return str(Path(path).resolve()).replace("\\", "/").lower()
