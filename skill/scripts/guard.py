#!/usr/bin/env python3
"""Safety rules for the MiraiMinds /task skill (a Claude Code PreToolUse hook).

- Tracker tools: only the actions a client needs, and only on the client's own
  project. Anything else is blocked, whatever Claude has been asked to do.
- The skill's own helper (bin/tt) and its outbox files are approved without a
  permission prompt, so clients are never asked to judge technical commands.
- Every other tool call is left alone.

Prints nothing for calls it doesn't care about. If something unexpected goes
wrong while checking a tracker call, that call is blocked.
"""

import json
import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path.home() / ".miraiminds" / "task"
CONFIG = DATA_DIR / "config.json"
OUTBOX = DATA_DIR / "outbox"
TEAM = json.loads((SKILL_DIR / "config" / "team.json").read_text(encoding="utf-8"))
PREFIX = f"mcp__{TEAM['mcp_server_name']}__"

ALLOWED = {
    "member": {"me", "list_project"},
    "project": {"retrieve"},
    "workitem": {"list", "retrieve", "retrieve_by_identifier", "search"},
    "intake": {"create", "list", "retrieve"},
    "workitem_comment": {"list", "retrieve", "create"},
    "workitem_link": {"list", "create"},
    "workitem_attachment": {"list", "read", "download_url", "upload_from_url"},
    "workitem_activity": {"list", "retrieve"},
    "workitem_relation": {"list"},
    "state": {"list"},
    "label": {"list"},
    "cycle": {"list", "retrieve", "list_workitems"},
    "module": {"list", "retrieve", "list_workitems"},
    "milestone": {"list", "retrieve", "list_workitems"},
    "page": {"list", "retrieve"},
}
# Needed to check the connection, before a project has been chosen.
NO_PROJECT_NEEDED = {("member", "me")}

LAUNCHER = re.compile(
    r"""^\s*(?:&\s*|bash\s+)?(?:"(?P<q>[^"]+)"|'(?P<s>[^']+)'|(?P<p>[^\s"']+))(?P<args>\s.*)?$""",
    re.S,
)
UNSAFE_ARGS = re.compile(r"[`$;|&<>\r\n]")


def decide(decision: str, reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def to_path(raw: str) -> Path:
    raw = os.path.expanduser(raw)
    git_bash = re.match(r"^/([a-zA-Z])/(.*)$", raw)
    if git_bash and os.name == "nt":
        raw = f"{git_bash.group(1)}:/{git_bash.group(2)}"
    return Path(raw)


def same_file(raw: str, target: Path) -> bool:
    try:
        return to_path(raw).resolve() == target.resolve()
    except OSError:
        return False


def is_helper_command(command: str) -> bool:
    match = LAUNCHER.match(command or "")
    if not match or UNSAFE_ARGS.search(match.group("args") or ""):
        return False
    raw = match.group("q") or match.group("s") or match.group("p")
    return same_file(raw, SKILL_DIR / "bin" / "tt") or same_file(raw, SKILL_DIR / "bin" / "tt.cmd")


def is_outbox_file(file_path: str) -> bool:
    path = to_path(file_path or "").resolve()
    return path.suffix == ".json" and path.parent == OUTBOX.resolve()


def tracker_decision(tool: str, args: dict) -> tuple[str, str]:
    name, action = tool[len(PREFIX) :], str(args.get("action") or "")
    if action not in ALLOWED.get(name, set()):
        return "deny", (
            f"'{name} {action}' is not available in the client's /task skill. "
            "Ask the team with a comment or a new request instead."
        )
    if (name, action) in NO_PROJECT_NEEDED:
        return "allow", "MiraiMinds /task"
    try:
        project = json.loads(CONFIG.read_text(encoding="utf-8")).get("project") or {}
    except (FileNotFoundError, json.JSONDecodeError):
        project = {}
    if not project.get("id"):
        return "deny", "No project is chosen yet. Finish connecting first (tt project set <project>)."
    if (name, action) == ("workitem", "search"):
        return "allow", "MiraiMinds /task"
    if (name, action) == ("workitem", "retrieve_by_identifier"):
        ref = str(args.get("workitem_identifier") or "").upper()
        if ref.startswith(project["identifier"].upper() + "-"):
            return "allow", "MiraiMinds /task"
        return "deny", "That reference number belongs to a different project."
    if args.get("project_id") != project["id"]:
        return "deny", f"Only the client's own project can be used: project_id must be {project['id']}."
    return "allow", "MiraiMinds /task"


def main() -> None:
    try:
        event = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return
    tool = event.get("tool_name") or ""
    args = event.get("tool_input") or {}

    if tool.startswith(PREFIX):
        try:
            decision = tracker_decision(tool, args)
        except Exception:
            decision = ("deny", "The /task safety check could not run, so this tracker action was stopped.")
        decide(*decision)
        return

    try:
        if tool in ("Bash", "PowerShell") and is_helper_command(args.get("command", "")):
            decide("allow", "MiraiMinds /task helper")
        elif tool == "Write" and is_outbox_file(args.get("file_path", "")):
            decide("allow", "MiraiMinds /task saved request")
    except Exception:
        pass


if __name__ == "__main__":
    main()
