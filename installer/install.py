#!/usr/bin/env python3
"""Install or update the MiraiMinds /task skill for Claude Code.

Run by install.ps1 / install.sh with the Python that lives inside the
plane-mcp-server tool environment. Safe to run again: it replaces the skill files,
keeps the client's saved key and settings, and re-points the tracker connection
at the new files.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_SRC = REPO / "skill"
MARKER = ".miraiminds-task"
GUARD_MATCHER = "Bash|PowerShell|Write|mcp__miraiminds-tracker__.*"
# The connector can take 15-60 s to start on a slow or busy laptop; Claude's default limit is 30 s.
MCP_TIMEOUT_MS = 120000


def posix(path) -> str:
    return str(path).replace("\\", "/")


def copy_skill(dest: Path) -> list[str]:
    notes = []
    if dest.exists():
        if (dest / MARKER).exists():
            shutil.rmtree(dest)
        else:
            backup = dest.with_name(f"task.backup-{time.strftime('%Y%m%d-%H%M%S')}")
            dest.rename(backup)
            notes.append(f"An older skill called 'task' was moved to {backup}")
    shutil.copytree(SKILL_SRC, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "bin"))
    (dest / MARKER).write_text("Installed by the MiraiMinds /task installer.\n", encoding="utf-8")
    return notes


def write_launchers(dest: Path, python: str) -> None:
    bin_dir = dest / "bin"
    bin_dir.mkdir(exist_ok=True)
    tt = dest / "scripts" / "tt.py"
    sh = bin_dir / "tt"
    sh.write_text(f'#!/usr/bin/env bash\nexec "{posix(python)}" "{posix(tt)}" "$@"\n', encoding="utf-8", newline="\n")
    if os.name != "nt":
        sh.chmod(0o755)
    (bin_dir / "tt.cmd").write_text(f'@echo off\r\n"{python}" "{tt}" %*\r\n', encoding="utf-8", newline="")


def update_settings(claude_dir: Path, python: str, dest: Path) -> dict:
    """Add the safety hook and a longer MCP start-up timeout to the user's Claude settings."""
    path = claude_dir / "settings.json"
    try:
        settings = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        return {"ok": False, "reason": "settings_unreadable"}

    env = settings.setdefault("env", {})
    try:
        current = int(env.get("MCP_TIMEOUT") or 0)
    except ValueError:
        current = 0
    if current < MCP_TIMEOUT_MS:
        env["MCP_TIMEOUT"] = str(MCP_TIMEOUT_MS)

    command = f'"{posix(python)}" "{posix(dest / "scripts" / "guard.py")}"'
    hooks = settings.setdefault("hooks", {})
    kept = [
        entry
        for entry in hooks.get("PreToolUse", [])
        if not any("skills/task/scripts/guard.py" in posix(h.get("command", "")) for h in entry.get("hooks", []))
    ]
    kept.append({"matcher": GUARD_MATCHER, "hooks": [{"type": "command", "command": command, "timeout": 15}]})
    hooks["PreToolUse"] = kept

    backup = path.with_name("settings.json.miraiminds-backup")
    if path.exists() and not backup.exists():
        shutil.copy2(path, backup)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"ok": True}


def warm_up(python: str) -> float | None:
    """Load the connector once, so its first real start (after the restart) is faster."""
    started = time.time()
    try:
        subprocess.run(
            [python, "-W", "ignore", "-c", "import plane_mcp.__main__"],
            capture_output=True,
            timeout=300,
            check=True,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    return round(time.time() - started, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uv", required=True)
    parser.add_argument("--source", default="")
    args = parser.parse_args()

    python = sys.executable
    claude_dir = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    dest = claude_dir / "skills" / "task"

    notes = copy_skill(dest)
    write_launchers(dest, python)

    sys.path.insert(0, str(dest / "scripts"))
    import tt

    previous = tt.read_json(tt.INSTALL, {}) or {}
    tt.write_json(
        tt.INSTALL,
        {
            "skill_version": tt.TEAM["skill_version"],
            "python": python,
            "uv": args.uv,
            "skill_dir": str(dest),
            "source": args.source or previous.get("source", ""),
            "installed_at": previous.get("installed_at") or tt.now_utc_iso(),
            "updated_at": tt.now_utc_iso(),
        },
    )
    hook = update_settings(claude_dir, python, dest)
    mcp = tt.register_mcp() if tt.CREDENTIALS.exists() else {"ok": True, "pending": "connect"}
    warmup = warm_up(python)

    ok = hook.get("ok") and mcp.get("ok")
    print(
        json.dumps(
            {
                "ok": bool(ok),
                "skill_version": tt.TEAM["skill_version"],
                "skill_dir": str(dest),
                "helper": posix(dest / "bin" / "tt"),
                "already_connected": tt.CREDENTIALS.exists(),
                "safety_hook": hook,
                "tracker_connection": mcp,
                "connector_warmup_seconds": warmup,
                "notes": notes,
                "next": (
                    f"Read {posix(dest / 'SKILL.md')}, then {posix(dest / 'flows' / 'setup.md')}, "
                    "and continue the setup with the user from 'Step 1: Connect'."
                ),
                "emergency": tt.TEAM["emergency_contact"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
