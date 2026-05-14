from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from ..core.registry import build_registry_part_candidate


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


def scan_linked_registry_parts(
    bpy_module: Any,
    *,
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = []
    existing_ids: set[str] = set()
    data = getattr(bpy_module, "data", None)
    library_collections = _collections_by_library(bpy_module)
    for library in getattr(data, "libraries", []):
        filepath = getattr(library, "filepath", "")
        resolved = _abspath(bpy_module, filepath)
        blend_path = _display_path(resolved, base_dir)
        collection_names = library_collections.get(_normalize(resolved)) or [Path(resolved).stem]
        for collection_name in collection_names:
            parts.append(
                build_registry_part_candidate(
                    blend_path,
                    linked_collection=collection_name,
                    existing_ids=existing_ids,
                )
            )
    return parts


def link_collection_from_file(
    bpy_module: Any,
    filepath: str,
    collection_name: str = "",
    *,
    dry_run: bool = True,
    target_collection: Any | None = None,
    base_dirs: Iterable[str | Path] | None = None,
) -> dict[str, Any]:
    resolved = _resolve_target_path(bpy_module, filepath, base_dirs=base_dirs)
    result: dict[str, Any] = {
        "dryRun": dry_run,
        "filepath": resolved,
        "requestedCollection": collection_name,
        "linkedCollection": None,
        "actions": [],
        "failed": [],
    }
    if not Path(resolved).exists():
        result["failed"].append({"path": resolved, "error": "File does not exist."})
        return result
    if dry_run:
        result["actions"].append("link-collection-preview")
        return result

    try:
        with bpy_module.data.libraries.load(resolved, link=True) as (data_from, data_to):
            available = list(getattr(data_from, "collections", []))
            selected = collection_name if collection_name in available else (available[0] if available else "")
            if not selected:
                result["failed"].append({"path": resolved, "error": "No collection found in linked .blend file."})
                return result
            data_to.collections = [selected]
        linked_collections = list(getattr(data_to, "collections", []))
        if not linked_collections:
            result["failed"].append({"path": resolved, "error": "Blender did not return a linked collection."})
            return result
        linked_collection = linked_collections[0]
        parent = target_collection or getattr(getattr(bpy_module, "context", None), "collection", None)
        if parent is not None:
            existing = {child.name for child in getattr(parent, "children", [])}
            if linked_collection.name not in existing:
                parent.children.link(linked_collection)
                result["actions"].append("linked-collection-to-scene-tree")
        result["linkedCollection"] = linked_collection.name
        result["actions"].append("linked-library-loaded")
    except Exception as exc:  # pragma: no cover - depends on Blender runtime
        result["failed"].append({"path": resolved, "error": str(exc)})
    return result


def reload_linked_libraries(
    bpy_module: Any,
    target_paths: list[str],
    *,
    dry_run: bool = True,
    base_dirs: Iterable[str | Path] | None = None,
) -> dict[str, Any]:
    targets = {_normalize(_resolve_target_path(bpy_module, path, base_dirs=base_dirs)) for path in target_paths}
    result = {"dryRun": dry_run, "targets": sorted(targets), "reloaded": [], "skipped": [], "failed": []}
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


def resolve_target_paths(
    bpy_module: Any,
    target_paths: list[str],
    *,
    base_dirs: Iterable[str | Path] | None = None,
) -> dict[str, str]:
    resolved_paths = {}
    for target_path in target_paths:
        resolved = _resolve_target_path(bpy_module, target_path, base_dirs=base_dirs)
        resolved_paths[_normalize(resolved)] = resolved
    return resolved_paths


def _abspath(bpy_module: Any, path: str) -> str:
    if not path:
        return ""
    path_api = getattr(bpy_module, "path", None)
    if path_api and hasattr(path_api, "abspath"):
        return path_api.abspath(path)
    return str(Path(path).resolve())


def _resolve_target_path(bpy_module: Any, path: str, *, base_dirs: Iterable[str | Path] | None = None) -> str:
    target = Path(path)
    if target.is_absolute():
        return str(target.resolve())
    for base_dir in base_dirs or []:
        candidate = Path(base_dir) / path
        if candidate.exists():
            return str(candidate.resolve())
    return _abspath(bpy_module, path)


def _collections_by_library(bpy_module: Any) -> dict[str, list[str]]:
    data = getattr(bpy_module, "data", None)
    collections: dict[str, list[str]] = {}
    for collection in getattr(data, "collections", []):
        library = getattr(collection, "library", None)
        if library is None:
            continue
        resolved = _normalize(_abspath(bpy_module, getattr(library, "filepath", "")))
        collections.setdefault(resolved, []).append(getattr(collection, "name", ""))
    return collections


def _display_path(path: str, base_dir: str | Path | None = None) -> str:
    resolved = Path(path).resolve()
    if base_dir:
        try:
            return resolved.relative_to(Path(base_dir).resolve()).as_posix()
        except ValueError:
            pass
    return str(resolved).replace("\\", "/")


def _normalize(path: str) -> str:
    return str(Path(path).resolve()).replace("\\", "/").lower()
