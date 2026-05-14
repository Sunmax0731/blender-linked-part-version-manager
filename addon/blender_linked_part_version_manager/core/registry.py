from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DEFAULT_TAG_ORDER = ("Hair", "Body", "Face", "Accessories", "Clothes", "Rig", "Props")
DEFAULT_TAGS = set(DEFAULT_TAG_ORDER)
ALLOWED_UPDATE_POLICIES = {"manual", "scheduled", "disabled"}
ALLOWED_SOURCE_TYPES = {"git", "local"}
REQUIRED_PART_FIELDS = {
    "partId",
    "partTag",
    "blendPath",
    "linkedCollection",
    "owner",
    "source",
    "versionRef",
    "updatePolicy",
}
DEFAULT_OWNER = "unassigned"
DEFAULT_SOURCE_TYPE = "local"
DEFAULT_SOURCE_ROOT = "."
DEFAULT_VERSION_REF = "local"
DEFAULT_UPDATE_POLICY = "manual"


def load_registry_file(path: str | Path) -> dict[str, Any]:
    registry_path = Path(path)
    with registry_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_registry_file(path: str | Path, registry: dict[str, Any]) -> None:
    registry_path = Path(path)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def registry_from_parts(
    parts: list[dict[str, Any]],
    *,
    product: str = "blender-linked-part-version-manager",
    integration_file: str | None = None,
) -> dict[str, Any]:
    registry: dict[str, Any] = {
        "schema_version": 1,
        "product": product,
        "parts": parts,
    }
    if integration_file:
        registry["integration_file"] = integration_file
    return registry


def build_registry_part_candidate(
    blend_path: str,
    *,
    linked_collection: str = "",
    part_id: str = "",
    part_tag: str = "",
    display_name: str = "",
    owner: str = DEFAULT_OWNER,
    source: dict[str, Any] | None = None,
    version_ref: str = DEFAULT_VERSION_REF,
    update_policy: str = DEFAULT_UPDATE_POLICY,
    existing_ids: set[str] | None = None,
) -> dict[str, Any]:
    label = display_name or _display_name_from_collection(linked_collection) or Path(blend_path).stem
    tag = part_tag if part_tag in DEFAULT_TAGS else infer_part_tag(linked_collection, blend_path, label)
    candidate_id = unique_part_id(part_id or f"{tag}-{label}", existing_ids=existing_ids)
    source_value = source or {
        "type": DEFAULT_SOURCE_TYPE,
        "root": DEFAULT_SOURCE_ROOT,
        "path": blend_path,
    }
    return {
        "partId": candidate_id,
        "partTag": tag,
        "displayName": label,
        "blendPath": blend_path,
        "linkedCollection": linked_collection or label,
        "owner": owner or DEFAULT_OWNER,
        "source": source_value,
        "versionRef": version_ref or DEFAULT_VERSION_REF,
        "updatePolicy": update_policy or DEFAULT_UPDATE_POLICY,
    }


def infer_part_tag(*values: str) -> str:
    haystack = " ".join(value or "" for value in values).lower()
    aliases = {
        "Accessories": ("accessories", "accessory", "acc", "glasses", "weapon"),
        "Clothes": ("clothes", "cloth", "shirt", "pants", "shoe", "wear"),
        "Body": ("body", "base_body", "skin", "hand", "leg"),
        "Face": ("face", "head", "eye", "mouth", "expr"),
        "Hair": ("hair", "brow", "lash"),
        "Rig": ("rig", "armature", "constraint", "driver"),
        "Props": ("props", "prop", "stand", "base"),
    }
    for tag in DEFAULT_TAG_ORDER:
        if any(alias in haystack for alias in aliases[tag]):
            return tag
    return "Props"


def unique_part_id(value: str, *, existing_ids: set[str] | None = None) -> str:
    base_id = _slugify(value) or "part"
    if existing_ids is None:
        return base_id
    candidate = base_id
    suffix = 2
    while candidate in existing_ids:
        candidate = f"{base_id}-{suffix}"
        suffix += 1
    existing_ids.add(candidate)
    return candidate


def validate_registry(registry: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not isinstance(registry, dict):
        return [{"severity": "error", "code": "registry-not-object", "message": "Registry root must be an object."}]

    if registry.get("schema_version") != 1:
        issues.append({"severity": "error", "code": "schema-version", "message": "schema_version must be 1."})

    parts = registry.get("parts")
    if not isinstance(parts, list) or not parts:
        issues.append({"severity": "error", "code": "parts-required", "message": "parts must be a non-empty array."})
        return issues

    seen_part_ids: set[str] = set()
    for index, part in enumerate(parts):
        if not isinstance(part, dict):
            issues.append(_issue(index, "part-not-object", "Part entry must be an object."))
            continue

        missing = sorted(field for field in REQUIRED_PART_FIELDS if not part.get(field))
        for field in missing:
            issues.append(_issue(index, "missing-field", f"Missing required field: {field}."))

        part_id = str(part.get("partId", ""))
        if part_id in seen_part_ids:
            issues.append(_issue(index, "duplicate-part-id", f"Duplicate partId: {part_id}."))
        if part_id:
            seen_part_ids.add(part_id)

        tag = str(part.get("partTag", ""))
        if tag and tag not in DEFAULT_TAGS:
            issues.append(_issue(index, "unknown-tag", f"Unknown partTag: {tag}."))

        update_policy = str(part.get("updatePolicy", ""))
        if update_policy and update_policy not in ALLOWED_UPDATE_POLICIES:
            issues.append(_issue(index, "unknown-update-policy", f"Unknown updatePolicy: {update_policy}."))

        source = part.get("source")
        if not isinstance(source, dict):
            issues.append(_issue(index, "source-not-object", "source must be an object."))
            continue

        source_type = str(source.get("type", ""))
        if source_type and source_type not in ALLOWED_SOURCE_TYPES:
            issues.append(_issue(index, "unknown-source-type", f"Unknown source.type: {source_type}."))

        if source_type == "git":
            for field in ("remote", "branch", "path"):
                if not source.get(field):
                    issues.append(_issue(index, "git-source-field", f"Git source requires {field}."))
        if source_type == "local":
            for field in ("root", "path"):
                if not source.get(field):
                    issues.append(_issue(index, "local-source-field", f"Local source requires {field}."))

    return issues


def _issue(index: int, code: str, message: str) -> dict[str, str]:
    return {
        "severity": "error",
        "code": code,
        "partIndex": str(index),
        "message": message,
    }


def _display_name_from_collection(value: str) -> str:
    if not value:
        return ""
    tokens = [token for token in re.split(r"[_\-\s]+", value) if token and token.upper() != "CHR"]
    return " ".join(token.capitalize() for token in tokens)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-+", "-", slug)
