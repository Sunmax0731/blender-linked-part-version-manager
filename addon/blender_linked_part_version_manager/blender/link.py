from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from ..core.registry import build_registry_part_candidate

REFERENCE_NAME_PREFIXES = ("ref", "reference")
EXPLICIT_OBJECT_CATEGORIES = {"reference-image", "light", "camera"}
AUTO_OBJECT_CATEGORIES = {"model", "rig", "generic-object"}
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
        "availableObjectDetails": [],
        "sourceLinkedLibraries": [],
        "recommendedCollection": None,
        "recommendedObjects": [],
        "recommendedObjectDetails": [],
        "explicitObjectDetails": [],
        "excludedObjectDetails": [],
        "linkMode": None,
        "linkedCollection": None,
        "linkedLibraries": [],
        "indirectLinkedLibraries": [],
        "linkedObjects": [],
        "actions": [],
        "failed": [],
        "warnings": [],
    }
    inspection = inspect_linkable_data_from_file(bpy_module, resolved, base_dirs=base_dirs)
    for key in (
        "availableCollections",
        "availableObjects",
        "availableObjectDetails",
        "sourceLinkedLibraries",
        "recommendedCollection",
        "recommendedObjects",
        "recommendedObjectDetails",
        "explicitObjectDetails",
        "excludedObjectDetails",
        "warnings",
    ):
        result[key] = inspection[key]
    if inspection["failed"]:
        result["failed"].extend(inspection["failed"])
        return result

    selection = _select_link_target(
        collection_name,
        resolved,
        inspection["availableCollections"],
        inspection["availableObjects"],
        inspection["availableObjectDetails"],
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
        before_libraries = _library_paths_by_normalized_path(bpy_module)
        with bpy_module.data.libraries.load(resolved, link=True) as (data_from, data_to):
            if selection["mode"] == "collection":
                data_to.collections = [selection["collection"]]
            else:
                data_to.objects = list(selection["objects"])
        _fill_linked_library_report(
            result,
            bpy_module,
            before_libraries,
            resolved,
            inspection["sourceLinkedLibraries"],
        )
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
        if result["indirectLinkedLibraries"]:
            result["actions"].append("indirect-linked-libraries-loaded")
    except Exception as exc:  # pragma: no cover - depends on Blender runtime
        result["failed"].append({"path": resolved, "error": str(exc)})
    return result


def link_collections_from_file(
    bpy_module: Any,
    filepath: str,
    collection_names: list[str],
    *,
    dry_run: bool = True,
    target_collection: Any | None = None,
    base_dirs: Iterable[str | Path] | None = None,
) -> dict[str, Any]:
    resolved = _resolve_target_path(bpy_module, filepath, base_dirs=base_dirs)
    requested_collections = _unique_nonempty(collection_names)
    result: dict[str, Any] = {
        "dryRun": dry_run,
        "filepath": resolved,
        "requestedCollections": requested_collections,
        "availableCollections": [],
        "availableObjects": [],
        "availableObjectDetails": [],
        "sourceLinkedLibraries": [],
        "recommendedCollection": None,
        "recommendedObjects": [],
        "recommendedObjectDetails": [],
        "explicitObjectDetails": [],
        "excludedObjectDetails": [],
        "linkMode": "collections" if requested_collections else None,
        "linkedCollection": requested_collections[0] if requested_collections else None,
        "linkedCollections": [],
        "linkedLibraries": [],
        "indirectLinkedLibraries": [],
        "linkedObjects": [],
        "actions": [],
        "failed": [],
        "warnings": [],
    }
    inspection = inspect_linkable_data_from_file(bpy_module, resolved, base_dirs=base_dirs)
    for key in (
        "availableCollections",
        "availableObjects",
        "availableObjectDetails",
        "sourceLinkedLibraries",
        "recommendedCollection",
        "recommendedObjects",
        "recommendedObjectDetails",
        "explicitObjectDetails",
        "excludedObjectDetails",
        "warnings",
    ):
        result[key] = inspection[key]
    if inspection["failed"]:
        result["failed"].extend(inspection["failed"])
        return result
    if not requested_collections:
        result["failed"].append({"path": resolved, "error": "No collection targets were selected."})
        return result

    missing = [name for name in requested_collections if name not in inspection["availableCollections"]]
    if missing:
        result["failed"].append(
            {
                "path": resolved,
                "error": (
                    f"Requested collection(s) not found: {', '.join(missing)}. "
                    f"Available collections: {', '.join(inspection['availableCollections']) or '(none)'}."
                ),
            }
        )
        return result

    if dry_run:
        result["linkedCollections"] = list(requested_collections)
        result["actions"].append("link-collections-preview")
        return result

    try:
        before_libraries = _library_paths_by_normalized_path(bpy_module)
        with bpy_module.data.libraries.load(resolved, link=True) as (data_from, data_to):
            data_to.collections = list(requested_collections)
        _fill_linked_library_report(
            result,
            bpy_module,
            before_libraries,
            resolved,
            inspection["sourceLinkedLibraries"],
        )
        linked_collections = [collection for collection in getattr(data_to, "collections", []) if collection]
        linked_by_name = {getattr(collection, "name", ""): collection for collection in linked_collections}
        missing_from_blender = [name for name in requested_collections if name not in linked_by_name]
        if missing_from_blender:
            result["failed"].append(
                {
                    "path": resolved,
                    "error": f"Blender did not return linked collection(s): {', '.join(missing_from_blender)}.",
                }
            )
            return result
        parent = target_collection or getattr(getattr(bpy_module, "context", None), "collection", None)
        for name in requested_collections:
            linked_collection = linked_by_name[name]
            if parent is not None and _link_child_collection(parent, linked_collection):
                result["actions"].append("linked-collection-to-scene-tree")
            result["linkedCollections"].append(getattr(linked_collection, "name", ""))
        result["actions"].append("linked-library-loaded")
        if result["indirectLinkedLibraries"]:
            result["actions"].append("indirect-linked-libraries-loaded")
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
        "availableObjectDetails": [],
        "sourceLinkedLibraries": [],
        "recommendedCollection": None,
        "recommendedObjects": [],
        "recommendedObjectDetails": [],
        "explicitObjectDetails": [],
        "excludedObjectDetails": [],
        "warnings": [],
        "failed": [],
    }
    if not Path(resolved).exists():
        result["failed"].append({"path": resolved, "error": "File does not exist."})
        return result
    try:
        with bpy_module.data.libraries.load(resolved, link=True) as (data_from, data_to):
            result["availableCollections"] = _name_list(getattr(data_from, "collections", []))
            object_details = _object_candidate_details(getattr(data_from, "objects", []))
            result["availableObjects"] = [detail["name"] for detail in object_details]
            result["availableObjectDetails"] = object_details
            result["sourceLinkedLibraries"] = _library_reference_details(
                bpy_module,
                getattr(data_from, "libraries", []),
                resolved,
            )
    except Exception as exc:  # pragma: no cover - depends on Blender runtime
        result["failed"].append({"path": resolved, "error": str(exc)})
        return result

    result["recommendedCollection"] = _recommended_collection(result["availableCollections"])
    result["recommendedObjectDetails"] = [
        detail for detail in result["availableObjectDetails"] if detail["autoRecommended"]
    ]
    result["recommendedObjects"] = [detail["name"] for detail in result["recommendedObjectDetails"]]
    result["explicitObjectDetails"] = [
        detail
        for detail in result["availableObjectDetails"]
        if detail["supported"] and not detail["autoRecommended"]
    ]
    result["excludedObjectDetails"] = [
        detail for detail in result["availableObjectDetails"] if not detail["supported"]
    ]
    if result["availableCollections"] and not result["recommendedCollection"]:
        result["warnings"].append(
            "Only generic or reference-like collections were found; production objects will be preferred when possible."
        )
    if result["explicitObjectDetails"]:
        result["warnings"].append(
            "Non-model object candidates are available for explicit linking only: "
            + _format_object_detail_list(result["explicitObjectDetails"])
            + "."
        )
    if result["excludedObjectDetails"]:
        result["warnings"].append(
            "Unsupported helper object candidates were excluded: "
            + _format_object_detail_list(result["excludedObjectDetails"])
            + "."
        )
    if result["sourceLinkedLibraries"]:
        result["warnings"].append(
            "Source .blend contains linked library dependencies: "
            + _format_library_detail_list(result["sourceLinkedLibraries"])
            + "."
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


def _library_paths_by_normalized_path(bpy_module: Any) -> dict[str, str]:
    paths: dict[str, str] = {}
    data = getattr(bpy_module, "data", None)
    for library in getattr(data, "libraries", []):
        filepath = getattr(library, "filepath", "")
        resolved = _abspath(bpy_module, filepath)
        if resolved:
            paths[_normalize(resolved)] = resolved
    return paths


def _fill_linked_library_report(
    result: dict[str, Any],
    bpy_module: Any,
    before_libraries: dict[str, str],
    source_path: str,
    source_linked_libraries: list[dict[str, str]],
) -> None:
    source_normalized = _normalize(source_path)
    dependency_paths = {_normalize(item["resolvedPath"]) for item in source_linked_libraries if item.get("resolvedPath")}
    dependency_by_filepath = {item.get("filepath", ""): item for item in source_linked_libraries}
    for entry in _current_library_entries(bpy_module, before_libraries):
        source_dependency = dependency_by_filepath.get(entry["filepath"])
        if source_dependency and entry["filepath"].startswith("//"):
            entry = {**entry, "resolvedPath": source_dependency["resolvedPath"]}
        normalized = _normalize(entry["resolvedPath"])
        if normalized == source_normalized:
            result.setdefault("linkedLibraries", []).append({**entry, "linkRole": "direct"})
        elif normalized in dependency_paths or entry["loadState"] == "new":
            result.setdefault("indirectLinkedLibraries", []).append({**entry, "linkRole": "indirect"})


def _current_library_entries(bpy_module: Any, before_libraries: dict[str, str]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    data = getattr(bpy_module, "data", None)
    seen: set[str] = set()
    for library in getattr(data, "libraries", []):
        filepath = getattr(library, "filepath", "")
        resolved = _abspath(bpy_module, filepath)
        if not resolved:
            continue
        normalized = _normalize(resolved)
        if normalized in seen:
            continue
        seen.add(normalized)
        entries.append(
            {
                "filepath": filepath,
                "resolvedPath": resolved,
                "loadState": "existing" if normalized in before_libraries else "new",
            }
        )
    return entries


def _library_reference_details(
    bpy_module: Any,
    libraries: Any,
    source_path: str,
) -> list[dict[str, str]]:
    details = []
    for library in libraries or []:
        filepath = _library_reference_path(library)
        resolved = _resolve_library_reference_path(bpy_module, filepath, source_path)
        if not resolved:
            continue
        details.append({"filepath": filepath, "resolvedPath": resolved})
    return details


def _library_reference_path(library: Any) -> str:
    if isinstance(library, str):
        return library
    return str(getattr(library, "filepath", "") or getattr(library, "name", "") or "")


def _resolve_library_reference_path(bpy_module: Any, filepath: str, source_path: str) -> str:
    if not filepath:
        return ""
    if filepath.startswith("//"):
        return str((Path(source_path).parent / filepath[2:]).resolve())
    if Path(filepath).is_absolute():
        return str(Path(filepath).resolve())
    return _abspath(bpy_module, filepath)


def _select_link_target(
    requested_collection: str,
    filepath: str,
    available_collections: list[str],
    available_objects: list[str],
    available_object_details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    requested = (requested_collection or "").strip()
    recommended_collection = _recommended_collection(available_collections)
    object_details = available_object_details or _object_candidate_details(available_objects)
    object_details_by_name = {detail["name"]: detail for detail in object_details}
    recommended_objects = _recommended_objects(object_details)
    explicit_objects = [
        detail["name"]
        for detail in object_details
        if detail["supported"] and not detail["autoRecommended"]
    ]
    excluded_objects = [
        f"{detail['name']} ({detail['category']})"
        for detail in object_details
        if not detail["supported"]
    ]
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
            detail = object_details_by_name.get(requested, _object_candidate_detail(requested))
            if not detail["supported"]:
                result["failed"].append(
                    {
                        "path": filepath,
                        "error": (
                            f"Requested object '{requested}' is not supported for linking "
                            f"({detail['category']}: {detail['reason']})."
                        ),
                    }
                )
                return result
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
                    f"Recommended objects: {', '.join(recommended_objects) or '(none)'}. "
                    f"Explicit object candidates: {', '.join(explicit_objects) or '(none)'}. "
                    f"Excluded objects: {', '.join(excluded_objects) or '(none)'}."
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
                "Set linkedCollection to an explicit supported object name, or move the target model into a named collection. "
                f"Explicit object candidates: {', '.join(explicit_objects) or '(none)'}. "
                f"Excluded objects: {', '.join(excluded_objects) or '(none)'}."
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


def _recommended_objects(object_values: list[Any]) -> list[str]:
    details = object_values if _looks_like_object_details(object_values) else _object_candidate_details(object_values)
    return [detail["name"] for detail in details if detail["autoRecommended"]]


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


def _object_candidate_details(values: Any) -> list[dict[str, Any]]:
    return [
        detail
        for detail in (_object_candidate_detail(value) for value in values or [])
        if detail["name"]
    ]


def _object_candidate_detail(value: Any) -> dict[str, Any]:
    name = value if isinstance(value, str) else getattr(value, "name", "")
    normalized = _label_key(name)
    explicit_type = "" if isinstance(value, str) else str(getattr(value, "type", "") or "")
    empty_display_type = "" if isinstance(value, str) else str(getattr(value, "empty_display_type", "") or "")
    blender_type = explicit_type.upper() or _infer_object_type(normalized)
    category = _object_category(normalized, blender_type, empty_display_type.upper())
    supported = category in AUTO_OBJECT_CATEGORIES or category in EXPLICIT_OBJECT_CATEGORIES
    auto_recommended = supported and category in AUTO_OBJECT_CATEGORIES
    return {
        "name": name,
        "type": blender_type,
        "category": category,
        "supported": supported,
        "autoRecommended": auto_recommended,
        "selection": "auto" if auto_recommended else "explicit" if supported else "excluded",
        "reason": _object_candidate_reason(category),
    }


def _infer_object_type(normalized_name: str) -> str:
    if not normalized_name:
        return "UNKNOWN"
    if "light" in normalized_name or normalized_name.startswith("lamp"):
        return "LIGHT"
    if "camera" in normalized_name or normalized_name in {"cam", "main_cam"}:
        return "CAMERA"
    if _is_reference_like_name(normalized_name) or "reference" in normalized_name or "image" in normalized_name:
        return "EMPTY_IMAGE"
    if "armature" in normalized_name or "rig" in normalized_name:
        return "ARMATURE"
    if any(hint in normalized_name for hint in PRODUCTION_NAME_HINTS):
        return "MESH"
    return "OBJECT"


def _object_category(normalized_name: str, blender_type: str, empty_display_type: str) -> str:
    if not normalized_name:
        return "unsupported"
    if "floor" in normalized_name:
        return "floor-helper"
    if blender_type == "LIGHT":
        return "light"
    if blender_type == "CAMERA":
        return "camera"
    if blender_type in {"EMPTY_IMAGE", "IMAGE"} or (
        blender_type == "EMPTY" and empty_display_type == "IMAGE"
    ) or _is_reference_like_name(normalized_name):
        return "reference-image"
    if blender_type == "ARMATURE" or "armature" in normalized_name or "rig" in normalized_name:
        return "rig"
    if blender_type in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
        return "model"
    if any(hint in normalized_name for hint in PRODUCTION_NAME_HINTS):
        return "model"
    if blender_type in {"OBJECT", "UNKNOWN"}:
        return "generic-object"
    return "unsupported"


def _object_candidate_reason(category: str) -> str:
    return {
        "model": "production model object can be selected automatically",
        "rig": "rig object can be selected automatically with model targets",
        "generic-object": "generic object can be selected automatically when no stronger type is available",
        "reference-image": "reference image object requires explicit user selection",
        "light": "light object requires explicit user selection",
        "camera": "camera object requires explicit user selection",
        "floor-helper": "floor helper is not a safe link target",
        "unsupported": "object type is not supported by the link target policy",
    }.get(category, "object type is not supported by the link target policy")


def _format_object_detail_list(details: list[dict[str, Any]]) -> str:
    return ", ".join(f"{detail['name']} ({detail['type']}/{detail['category']})" for detail in details) or "(none)"


def _format_library_detail_list(details: list[dict[str, str]]) -> str:
    return ", ".join(detail.get("filepath") or detail.get("resolvedPath") or "" for detail in details) or "(none)"


def _looks_like_object_details(values: list[Any]) -> bool:
    return bool(values) and all(isinstance(value, dict) and "name" in value for value in values)


def _is_reference_like_name(normalized_name: str) -> bool:
    for prefix in REFERENCE_NAME_PREFIXES:
        if normalized_name == prefix or normalized_name.startswith(f"{prefix}_") or normalized_name.startswith(f"{prefix}-"):
            return True
    return normalized_name.startswith("ref") and len(normalized_name) > 3 and not normalized_name[3].isalpha()


def _same_label(left: str, right: str) -> bool:
    return _label_key(left) == _label_key(right)


def _unique_nonempty(values: list[str]) -> list[str]:
    unique_values: list[str] = []
    seen: set[str] = set()
    for value in values:
        name = (value or "").strip()
        if not name or name in seen:
            continue
        seen.add(name)
        unique_values.append(name)
    return unique_values


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
