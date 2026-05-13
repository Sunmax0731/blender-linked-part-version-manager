from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_TAGS = {"Hair", "Body", "Face", "Accessories", "Clothes", "Rig", "Props"}
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


def load_registry_file(path: str | Path) -> dict[str, Any]:
    registry_path = Path(path)
    with registry_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_registry_file(path: str | Path, registry: dict[str, Any]) -> None:
    registry_path = Path(path)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
