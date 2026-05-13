from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .core.plan import summarize_plan


def build_dry_run_report(
    *,
    registry: dict[str, Any],
    plan: list[dict[str, Any]],
    registry_path: str,
    validation_issues: list[dict[str, Any]] | None = None,
    link_state: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "product": registry.get("product", "blender-linked-part-version-manager"),
        "registryPath": registry_path,
        "validationIssues": validation_issues or [],
        "summary": summarize_plan(plan),
        "plan": plan,
        "linkState": link_state or [],
        "safety": {
            "autoSaveBlend": False,
            "autoPush": False,
            "blockedStatuses": ["local-dirty", "conflict-risk", "broken-link"],
        },
    }


def write_json_report(path: str | Path, report: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
