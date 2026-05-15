from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from ..core.registry import build_registry_part_candidate

REFERENCE_NAME_PREFIXES = ("ref", "reference")
IGNORED_OBJECT_NAMES = {"camera", "floor", "light"}
PRODUCTION_NAME_HINTS = (
    "armature",
    "body",
    "base_body",
    "face",
    "head",
    "hair",
    "cloth",
    "clothes",
    "costume",
    "wear",
    "mesh",
    "rig",
)


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
        "availableCollections": [],
        "availableObjects": [],
        "recommendedCollection": None,
        "recommendedObjects": [],
        "linkMode": None,
        "linkedCollection": None,
        "linkedObjects": [],
        "actions": [],
        "failed": [],
        "warnings": [],
    }
    inspection = inspect_linkable_data_from_file(bpy_module, resolved, base_dirs=base_dirs)
    for key in ("availableCollections", "availableObjects", "recommendedCollection", "recommendedObjects", "warnings"):
        result[key] = inspection[key]
    if inspection["failed"]:
        result["failed"].extend(inspection["failed"])
        return result

    selection = _select_link_target(
        collection_name,
        resolved,
        inspection["availableCollections"],
        inspection["availableObjects"],
    )
    if selection["failed"]:
        result["failed"].extend(selection["failed"])
        return result
    result["linkMode"] = selection["mode"]
    result["linkedCollection"] = selection["targetCollection"]
    result["linkedObjects"] = selection["objects"]

    if dry_run:
        result["actions"].append("link-collection-preview")
        if selection["mode"] == "objects":
            result["actions"].append("link-production-objects-preview")
        return result

    try:
        with bpy_module.data.libraries.load(resolved, link=True) as (data_from, data_to):
            if selection["mode"] == "collection":
                data_to.collections = [selection["collection"]]
            else:
                data_to.objects = list(selection["objects"])
        parent = target_collection or getattr(getattr(bpy_module, "context", None), "collection", None)
        if selection["mode"] == "collection":
            linked_collections = [collection for collection in getattr(data_to, "collections", []) if collection]
            if not linked_collections:
                result["failed"].append({"path": resolved, "error": "Blender did not return a linked collection."})
                return result
            linked_collection = linked_collections[0]
            if parent is not None and _link_child_collection(parent, linked_collection):
                result["actions"].append("linked-collection-to-scene-tree")
            result["linkedCollection"] = linked_collection.name
        else:
            linked_objects = [obj for obj in getattr(data_to, "objects", []) if obj]
            if not linked_objects:
                result["failed"].append({"path": resolved, "error": "Blender did not return linked objects."})
                return result
            if parent is not None:
                object_collection = _ensure_object_target_collection(
                    bpy_module,
                    parent,
                    selection["targetCollection"],
                )
                for linked_object in linked_objects:
                    if _link_object_to_collection(object_collection, linked_object):
                        result["actions"].append("linked-object-to-scene-tree")
            result["linkedObjects"] = [getattr(obj, "name", "") for obj in linked_objects]
        result["actions"].append("linked-library-loaded")
    except Exception as exc:  # pragma: no cover - depends on Blender runtime
        result["failed"].append({"path": resolved, "error": str(exc)})
    return result


def inspect_linkable_data_from_file(
    bpy_module: Any,
    filepath: str,
    *,
    base_dirs: Iterable[str | Path] | None = None,
) -> dict[str, Any]:
    resolved = _resolve_target_path(bpy_module, filepath, base_dirs=base_dirs)
    result: dict[str, Any] = {
        "filepath": resolved,
        "availableCollections": [],
        "availableObjects": [],
        "recommendedCollection": None,
        "recommendedObjects": [],
        "warnings": [],
        "failed": [],
    }
    if not Path(resolved).exists():
        result["failed"].append({"path": resolved, "error": "File does not exist."})
        return result
    try:
        with bpy_module.data.libraries.load(resolved, link=True) as (data_from, data_to):
            result["availableCollections"] = _name_list(getattr(data_from, "collections", []))
            result["availableObjects"] = _name_list(getattr(data_from, "objects", []))
    except Exception as exc:  # pragma: no cover - depends on Blender runtime
        result["failed"].append({"path": resolved, "error": str(exc)})
        return result

    result["recommendedCollection"] = _recommended_collection(result["availableCollections"])
    result["recommendedObjects"] = _recommended_objects(result["availableObjects"])
    if result["availableCollections"] and not result["recommendedCollection"]:
        result["warnings"].append(
            "Only generic or reference-like collections were found; production objects will be preferred when possible."
        )
    if not result["availableCollections"] and not result["availableObjects"]:
        result["failed"].append({"path": resolved, "error": "No linkable collection or object found in .blend file."})
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


def integrate_linked_libraries(
    bpy_module: Any,
    target_paths: list[str],
    *,
    dry_run: bool = True,
    base_dirs: Iterable[str | Path] | None = None,
) -> dict[str, Any]:
    targets = {_normalize(_resolve_target_path(bpy_module, path, base_dirs=base_dirs)) for path in target_paths}
    data = getattr(bpy_module, "data", None)
    result: dict[str, Any] = {
        "dryRun": dry_run,
        "outputFile": _current_output_file(bpy_module),
        "targets": sorted(targets),
        "integrated": [],
        "skipped": [],
        "warnings": [],
        "failed": [],
    }
    linked_ids = _ids_by_library(bpy_module)
    matched_targets: set[str] = set()
    for library in getattr(data, "libraries", []):
        resolved = _normalize(_abspath(bpy_module, getattr(library, "filepath", "")))
        if resolved not in targets:
            result["skipped"].append(resolved)
            continue
        matched_targets.add(resolved)
        datablocks = linked_ids.get(resolved, [])
        entry: dict[str, Any] = {
            "path": resolved,
            "datablockCount": len(datablocks),
            "datablocks": [
                {"type": block_type, "name": getattr(block, "name", "")}
                for block_type, block in datablocks
            ],
        }
        if dry_run:
            result["integrated"].append(entry)
            continue

        localized = 0
        for block_type, block in datablocks:
            make_local = getattr(block, "make_local", None)
            if not callable(make_local):
                result["warnings"].append(
                    {
                        "path": resolved,
                        "type": block_type,
                        "name": getattr(block, "name", ""),
                        "warning": "Datablock does not expose make_local().",
                    }
                )
                continue
            try:
                make_local()
                localized += 1
            except Exception as exc:  # pragma: no cover - depends on Blender runtime
                result["failed"].append(
                    {
                        "path": resolved,
                        "type": block_type,
                        "name": getattr(block, "name", ""),
                        "error": str(exc),
                    }
                )
        entry["localizedCount"] = localized
        result["integrated"].append(entry)

    for target in sorted(targets - matched_targets):
        result["failed"].append(
            {
                "path": target,
                "error": "Linked library is not present in the current Blender file.",
            }
        )
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


def _select_link_target(
    requested_collection: str,
    filepath: str,
    available_collections: list[str],
    available_objects: list[str],
) -> dict[str, Any]:
    requested = (requested_collection or "").strip()
    recommended_collection = _recommended_collection(available_collections)
    recommended_objects = _recommended_objects(available_objects)
    fallback_name = Path(filepath).stem
    result: dict[str, Any] = {
        "mode": None,
        "collection": None,
        "objects": [],
        "targetCollection": None,
        "failed": [],
    }

    if requested:
        if requested in available_collections:
            result.update({"mode": "collection", "collection": requested, "targetCollection": requested})
            return result
        if requested in available_objects:
            result.update({"mode": "objects", "objects": [requested], "targetCollection": requested})
            return result
        if _same_label(requested, fallback_name) and recommended_collection:
            result.update(
                {
                    "mode": "collection",
                    "collection": recommended_collection,
                    "targetCollection": recommended_collection,
                }
            )
            return result
        if _same_label(requested, fallback_name) and recommended_objects:
            result.update({"mode": "objects", "objects": recommended_objects, "targetCollection": requested})
            return result
        result["failed"].append(
            {
                "path": filepath,
                "error": (
                    f"Requested collection '{requested}' was not found. "
                    f"Available collections: {', '.join(available_collections) or '(none)'}. "
                    f"Recommended collection: {recommended_collection or '(none)'}. "
                    f"Recommended objects: {', '.join(recommended_objects) or '(none)'}."
                ),
            }
        )
        return result

    if recommended_collection:
        result.update(
            {
                "mode": "collection",
                "collection": recommended_collection,
                "targetCollection": recommended_collection,
            }
        )
        return result
    if recommended_objects:
        result.update({"mode": "objects", "objects": recommended_objects, "targetCollection": fallback_name})
        return result

    result["failed"].append(
        {
            "path": filepath,
            "error": (
                "No production collection or object could be selected automatically. "
                "Set linkedCollection explicitly or move the target model into a named collection."
            ),
        }
    )
    return result


def _recommended_collection(collection_names: list[str]) -> str | None:
    scored = sorted(
        ((_collection_score(name), index, name) for index, name in enumerate(collection_names)),
        key=lambda item: (-item[0], item[1]),
    )
    if not scored or scored[0][0] <= 0:
        return None
    return scored[0][2]


def _recommended_objects(object_names: list[str]) -> list[str]:
    return [name for name in object_names if _object_score(name) > 0]


def _collection_score(name: str) -> int:
    normalized = _label_key(name)
    if not normalized or _is_reference_like_name(normalized):
        return -100
    if normalized in {"collection", "scene collection"}:
        return 0
    score = 10
    if any(hint in normalized for hint in PRODUCTION_NAME_HINTS):
        score += 80
    return score


def _object_score(name: str) -> int:
    normalized = _label_key(name)
    if not normalized:
        return -100
    if normalized in IGNORED_OBJECT_NAMES or _is_reference_like_name(normalized):
        return -100
    score = 10
    if any(hint in normalized for hint in PRODUCTION_NAME_HINTS):
        score += 40
    return score


def _is_reference_like_name(normalized_name: str) -> bool:
    for prefix in REFERENCE_NAME_PREFIXES:
        if normalized_name == prefix or normalized_name.startswith(f"{prefix}_") or normalized_name.startswith(f"{prefix}-"):
            return True
    return normalized_name.startswith("ref") and len(normalized_name) > 3 and not normalized_name[3].isalpha()


def _same_label(left: str, right: str) -> bool:
    return _label_key(left) == _label_key(right)


def _label_key(value: str) -> str:
    return (value or "").replace("-", "_").replace(" ", "_").lower()


def _name_list(values: Any) -> list[str]:
    names = []
    for value in values or []:
        if isinstance(value, str):
            name = value
        else:
            name = getattr(value, "name", "")
        if name:
            names.append(name)
    return names


def _link_child_collection(parent: Any, linked_collection: Any) -> bool:
    children = getattr(parent, "children", None)
    if children is None:
        return False
    existing = {getattr(child, "name", "") for child in children}
    if getattr(linked_collection, "name", "") in existing:
        return False
    children.link(linked_collection)
    return True


def _ensure_object_target_collection(bpy_module: Any, parent: Any, collection_name: str) -> Any:
    children = getattr(parent, "children", None)
    if children is not None:
        for child in children:
            if getattr(child, "name", "") == collection_name:
                return child
    collections = getattr(getattr(bpy_module, "data", None), "collections", None)
    new_collection = collections.new(collection_name) if hasattr(collections, "new") else None
    if new_collection is None:
        return parent
    if children is not None:
        children.link(new_collection)
    return new_collection


def _link_object_to_collection(collection: Any, linked_object: Any) -> bool:
    objects = getattr(collection, "objects", None)
    if objects is None:
        return False
    existing = {getattr(obj, "name", "") for obj in objects}
    if getattr(linked_object, "name", "") in existing:
        return False
    objects.link(linked_object)
    return True


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


def _ids_by_library(bpy_module: Any) -> dict[str, list[tuple[str, Any]]]:
    data = getattr(bpy_module, "data", None)
    ids: dict[str, list[tuple[str, Any]]] = {}
    container_names = (
        "collections",
        "objects",
        "meshes",
        "materials",
        "armatures",
        "actions",
        "curves",
        "cameras",
        "lights",
        "images",
        "node_groups",
        "textures",
        "fonts",
        "worlds",
        "lattices",
        "metaballs",
        "speakers",
        "volumes",
    )
    for container_name in container_names:
        for block in getattr(data, container_name, []):
            library = getattr(block, "library", None)
            if library is None:
                continue
            resolved = _normalize(_abspath(bpy_module, getattr(library, "filepath", "")))
            ids.setdefault(resolved, []).append((container_name, block))
    return ids


def _current_output_file(bpy_module: Any) -> str:
    filepath = getattr(getattr(bpy_module, "data", None), "filepath", "")
    if not filepath:
        return "current-unsaved-blender-session"
    return _abspath(bpy_module, filepath)


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
