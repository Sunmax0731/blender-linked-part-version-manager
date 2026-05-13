from __future__ import annotations

from pathlib import Path
from typing import Any


def preview_local_part(part: dict[str, Any], *, repo_root: str | Path = ".") -> dict[str, Any]:
    source = part.get("source") or {}
    if source.get("type") != "local":
        return _result(part, "unknown", "review", ["Part source is not local."])

    root = Path(str(source.get("root") or ""))
    source_path = root / str(source.get("path") or "")
    target_path = Path(repo_root) / str(part.get("blendPath") or "")
    if not source_path.exists():
        return _result(part, "broken-link", "blocked", [f"Local source path is missing: {source_path}"])
    if not target_path.exists():
        return _result(part, "remote-newer", "low", ["Local source exists and target part file is missing."])
    if source_path.stat().st_mtime > target_path.stat().st_mtime:
        return _result(part, "remote-newer", "low", ["Local source is newer than the target part file."])
    return _result(part, "current", "none", ["Local source is not newer than the target part file."])


def _result(part: dict[str, Any], status: str, risk: str, messages: list[str]) -> dict[str, Any]:
    return {
        "adapter": "local",
        "partId": part.get("partId"),
        "status": status,
        "risk": risk,
        "messages": messages,
    }
