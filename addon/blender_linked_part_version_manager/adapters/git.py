from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Callable

Runner = Callable[[list[str], Path], subprocess.CompletedProcess[str]]


def preview_git_part(
    part: dict[str, Any],
    *,
    repo_root: str | Path = ".",
    runner: Runner | None = None,
) -> dict[str, Any]:
    source = part.get("source") or {}
    if source.get("type") != "git":
        return _result("git", part, "unknown", "review", ["Part source is not git."])

    root = Path(repo_root)
    run = runner or _run
    relative_path = str(source.get("path") or part.get("blendPath") or "")
    status = run(["git", "status", "--porcelain", "--", relative_path], root)
    if status.returncode != 0:
        return _result("git", part, "unknown", "review", [_stderr(status) or "git status failed."])
    if status.stdout.strip():
        return _result("git", part, "local-dirty", "blocked", ["Local git changes are present for this part."])

    branch = str(source.get("branch") or "main")
    remote = str(source.get("remote") or "origin")
    rev = run(["git", "rev-list", "--left-right", "--count", f"HEAD...{remote}/{branch}"], root)
    if rev.returncode == 0:
        left_right = rev.stdout.strip().split()
        if len(left_right) == 2 and left_right[1] != "0":
            return _result("git", part, "remote-newer", "low", [f"{remote}/{branch} has newer commits."])
    return _result("git", part, "current", "none", ["Git source is current or no remote delta was detected."])


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)


def _result(adapter: str, part: dict[str, Any], status: str, risk: str, messages: list[str]) -> dict[str, Any]:
    return {
        "adapter": adapter,
        "partId": part.get("partId"),
        "status": status,
        "risk": risk,
        "messages": messages,
    }


def _stderr(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stderr or result.stdout or "").strip()
