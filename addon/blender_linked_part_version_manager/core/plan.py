from __future__ import annotations

from typing import Any

BLOCKED_STATUSES = {"local-dirty", "conflict-risk", "broken-link", "missing-link"}
KNOWN_STATUSES = {
    "current",
    "remote-newer",
    "local-dirty",
    "missing-link",
    "broken-link",
    "conflict-risk",
    "unknown",
}


def build_sync_plan(
    registry: dict[str, Any],
    *,
    link_state: list[dict[str, Any]] | None = None,
    adapter_results: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    link_by_part = {item.get("partId"): item for item in link_state or [] if item.get("partId")}
    adapter_by_part = adapter_results or {}
    plan: list[dict[str, Any]] = []
    for part in registry.get("parts", []):
        part_id = part.get("partId")
        link_entry = link_by_part.get(part_id)
        adapter_entry = adapter_by_part.get(part_id)
        status = classify_part(part, link_entry=link_entry, adapter_entry=adapter_entry)
        plan.append(
            {
                "partId": part_id,
                "partTag": part.get("partTag"),
                "owner": part.get("owner"),
                "status": status,
                "risk": classify_risk(status),
                "plannedActions": planned_actions_for(status, part),
                "messages": messages_for(status, part),
                "part": {
                    "blendPath": part.get("blendPath"),
                    "linkedCollection": part.get("linkedCollection"),
                    "source": part.get("source"),
                },
            }
        )
    return plan


def classify_part(
    part: dict[str, Any],
    *,
    link_entry: dict[str, Any] | None = None,
    adapter_entry: dict[str, Any] | None = None,
) -> str:
    if adapter_entry and adapter_entry.get("status") in KNOWN_STATUSES:
        return str(adapter_entry["status"])
    if link_entry and link_entry.get("status") in KNOWN_STATUSES:
        return str(link_entry["status"])
    expected = part.get("expectedStatus")
    if expected in KNOWN_STATUSES:
        return str(expected)
    return "unknown"


def classify_risk(status: str) -> str:
    if status in {"local-dirty", "conflict-risk", "broken-link"}:
        return "blocked"
    if status == "missing-link":
        return "manual"
    if status == "remote-newer":
        return "low"
    if status == "current":
        return "none"
    return "review"


def planned_actions_for(status: str, part: dict[str, Any]) -> list[str]:
    if status == "current":
        return []
    if status == "remote-newer":
        source_type = (part.get("source") or {}).get("type")
        if source_type == "local":
            return ["copy-preview", "reload-link"]
        return ["fetch", "pull-preview", "reload-link"]
    if status == "missing-link":
        return ["create-link-preview"]
    if status == "broken-link":
        return ["repair-path-required"]
    if status == "local-dirty":
        return ["skip-auto-update", "publish-or-stash-required"]
    if status == "conflict-risk":
        return ["skip-auto-update", "manual-conflict-review"]
    return ["manual-review"]


def messages_for(status: str, part: dict[str, Any]) -> list[str]:
    label = part.get("displayName") or part.get("partId")
    if status == "current":
        return [f"{label} is current."]
    if status == "remote-newer":
        return [f"{label} has an update candidate. Review dry-run before reload."]
    if status == "local-dirty":
        return [f"{label} has local work. Automatic pull/reload is disabled."]
    if status == "conflict-risk":
        return [f"{label} may conflict with local work. Manual review is required."]
    if status == "missing-link":
        return [f"{label} is in the registry but not linked in the integration file."]
    if status == "broken-link":
        return [f"{label} points to a missing linked .blend path."]
    return [f"{label} needs manual review."]


def summarize_plan(plan: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "totalParts": len(plan),
        "currentParts": sum(1 for item in plan if item["status"] == "current"),
        "updateCandidates": sum(1 for item in plan if item["status"] == "remote-newer"),
        "blockedParts": sum(1 for item in plan if item["risk"] == "blocked"),
        "manualParts": sum(1 for item in plan if item["risk"] in {"manual", "review"}),
    }
