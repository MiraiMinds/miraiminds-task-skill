#!/usr/bin/env python3
"""Helper commands for the MiraiMinds /task skill.

Claude runs these through the launcher in ../bin (`tt` or `tt.cmd`) for the jobs
the tracker MCP server cannot do: saving the connection key from a pop-up,
working-day maths, the offline outbox, uploading local screenshots and building
WhatsApp links. Every command prints one JSON object on stdout.

The connection key is stored in ~/.miraiminds/task/credentials.json and is never
printed. The MCP server reads it through serve.py, so ~/.claude.json holds no secret.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import platform
import re
import shutil
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SKILL_DIR = SCRIPTS.parent
TEAM = json.loads((SKILL_DIR / "config" / "team.json").read_text(encoding="utf-8"))
SERVER = TEAM["mcp_server_name"]

HOME = Path.home()
DATA_DIR = HOME / ".miraiminds" / "task"
CREDENTIALS = DATA_DIR / "credentials.json"
CONFIG = DATA_DIR / "config.json"
STATE = DATA_DIR / "state.json"
INSTALL = DATA_DIR / "install.json"
OUTBOX = DATA_DIR / "outbox"

DAY_KEYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".heic"}


# --------------------------------------------------------------------------- files


def read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path: Path, data, private: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    if private and os.name != "nt":
        os.chmod(tmp, 0o600)
    try:
        os.replace(tmp, path)
    except PermissionError:
        # Windows refuses the swap while another process holds the file open.
        path.write_text(tmp.read_text(encoding="utf-8"), encoding="utf-8")
        tmp.unlink(missing_ok=True)


def out(**data) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def claude_json_path() -> Path:
    custom = os.environ.get("CLAUDE_CONFIG_DIR")
    if custom and (Path(custom) / ".claude.json").exists():
        return Path(custom) / ".claude.json"
    return HOME / ".claude.json"


def load_key() -> str | None:
    return (read_json(CREDENTIALS, {}) or {}).get("api_key")


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------- network


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi  # present in the plane-mcp-server environment

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def api(path: str, key: str, timeout: int = 20):
    url = f"{TEAM['tracker_url']}/api/v1/{path.lstrip('/')}"
    req = urllib.request.Request(url, headers={"X-API-Key": key, "User-Agent": "miraiminds-task-skill"})
    with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
        raw = resp.read()
        return json.loads(raw) if raw else None


def reachable(url: str, timeout: int = 6) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": "miraiminds-task-skill"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()):
            return True
    except urllib.error.HTTPError:
        return True  # the server answered, even if with an error page
    except Exception:
        return False


def net_status() -> dict:
    tracker = reachable(f"{TEAM['tracker_url']}/api/instances/")
    internet = tracker or reachable("https://www.google.com") or reachable("https://1.1.1.1")
    return {"internet": internet, "tracker": tracker}


# --------------------------------------------------------------------------- environment


def surface() -> str:
    entry = os.environ.get("CLAUDE_CODE_ENTRYPOINT", "").lower()
    if "vscode" in entry or os.environ.get("TERM_PROGRAM") == "vscode" or os.environ.get("VSCODE_PID"):
        return "vscode"
    if "desktop" in entry:
        return "desktop"
    if entry == "cli":
        return "terminal"
    return "unknown"


# --------------------------------------------------------------------------- dates


def _team_tz() -> timezone:
    off = TEAM["team_time"]["utc_offset"]
    sign = -1 if off.startswith("-") else 1
    hours, minutes = off.lstrip("+-").split(":")
    return timezone(sign * timedelta(hours=int(hours), minutes=int(minutes)))


def _hhmm(value: str) -> time:
    h, m = value.split(":")
    return time(int(h), int(m))


def _holiday(d: date) -> str | None:
    for h in TEAM.get("holidays", []):
        if h.get("date") == d.isoformat():
            return h.get("name") or "a holiday"
    return None


def is_working_day(d: date) -> bool:
    return DAY_KEYS[d.weekday()] in TEAM["working_days"] and not _holiday(d)


def next_working_day(d: date) -> date:
    d += timedelta(days=1)
    while not is_working_day(d):
        d += timedelta(days=1)
    return d


def add_working_days(d: date, n: int) -> date:
    for _ in range(max(n, 1)):
        d = next_working_day(d)
    return d


def short_date(d: date) -> str:
    return f"{DAY_KEYS[d.weekday()]} {d.day} {MONTHS[d.month - 1]}"


def day_label(d: date, today: date) -> str:
    gap = (d - today).days
    if gap == 0:
        return "today"
    if gap == 1:
        return "tomorrow"
    if 1 < gap <= 6:
        return DAY_NAMES[d.weekday()]
    return short_date(d)


def when_info() -> dict:
    now = datetime.now(_team_tz())
    today = now.date()
    start, end = _hhmm(TEAM["working_hours"]["start"]), _hhmm(TEAM["working_hours"]["end"])
    holiday = _holiday(today)

    if not is_working_day(today):
        status = "holiday" if holiday else "weekend"
    elif now.time() < start:
        status = "before_hours"
    elif now.time() >= end:
        status = "after_hours"
    else:
        status = "working"

    client_now = datetime.now().astimezone()
    same_time = client_now.utcoffset() == now.utcoffset()
    back = today if status in ("working", "before_hours") else next_working_day(today)
    review_by = add_working_days(today, TEAM.get("review_turnaround_working_days", 1))
    back_label = day_label(back, today)
    on_back = back_label if back_label in ("today", "tomorrow") else f"on {back_label}"

    if status == "working":
        promise = f"The team will look at it by {day_label(review_by, today)}."
    elif status == "before_hours":
        their = "" if same_time else " their time"
        promise = f"The team starts at {TEAM['working_hours']['start']}{their} and will look at it today."
    elif status == "after_hours":
        promise = f"The team has finished for the day. They'll look at it {on_back} morning."
    elif status == "holiday":
        promise = f"The team is off today for {holiday}. They'll look at it {on_back} morning."
    else:
        promise = f"The team is off for the weekend. They'll look at it {on_back} morning."

    return {
        "team_now": f"{DAY_NAMES[now.weekday()]} {now.day} {MONTHS[now.month - 1]} {now.year}, {now.strftime('%H:%M')}",
        "team_time": TEAM["team_time"]["label"],
        "today": short_date(today) + f" {today.year}",
        "weekday": DAY_NAMES[today.weekday()],
        "team_status": status,
        "holiday": holiday,
        "team_back": on_back,
        "review_by": day_label(review_by, today),
        "next_working_day": day_label(next_working_day(today), today),
        "promise": promise,
        "client_now": client_now.strftime("%H:%M"),
        "client_same_time_as_team": same_time,
    }


def since_label(iso: str | None) -> str | None:
    if not iso:
        return None
    seen = datetime.fromisoformat(iso).astimezone().date()
    today = datetime.now().astimezone().date()
    gap = (today - seen).days
    if gap <= 0:
        return "since earlier today"
    if gap == 1:
        return "since yesterday"
    if gap <= 6:
        return f"since {DAY_NAMES[seen.weekday()]}"
    return f"since {seen.day} {MONTHS[seen.month - 1]}"


# --------------------------------------------------------------------------- stages


def describe_stage(name: str, group: str) -> dict:
    lowered = name.lower()
    if "test" in lowered:
        return {"key": "testing", "plain": "ready for you to check"}
    if "hold" in lowered:
        return {"key": "on_hold", "plain": "on hold for now"}
    return {
        "backlog": {"key": "not_started", "plain": "on the list, not started yet"},
        "unstarted": {"key": "planned", "plain": "planned, starting soon"},
        "started": {"key": "in_progress", "plain": "the team is working on it"},
        "completed": {"key": "finished", "plain": "finished"},
        "cancelled": {"key": "stopped", "plain": "stopped"},
    }.get(group, {"key": "other", "plain": name})


INTAKE_STATUS = {
    -2: "the team is reviewing it",
    -1: "the team decided not to go ahead (see their note)",
    0: "parked for later",
    1: "accepted, it's on the team's list",
    2: "the team already has this one",
}


def fetch_projects(key: str) -> list[dict]:
    data = api(f"workspaces/{TEAM['workspace_slug']}/projects/?per_page=100", key)
    rows = data.get("results", data) if isinstance(data, dict) else data
    return [
        {"id": p["id"], "identifier": p["identifier"], "name": p["name"], "intake_enabled": bool(p.get("intake_view"))}
        for p in rows
        if p.get("is_member") and not p.get("archived_at")
    ]


def fetch_stages(key: str, project_id: str) -> list[dict]:
    data = api(f"workspaces/{TEAM['workspace_slug']}/projects/{project_id}/states/", key)
    rows = data.get("results", data) if isinstance(data, dict) else data
    return [{"id": s["id"], "name": s["name"], "group": s["group"], **describe_stage(s["name"], s["group"])} for s in rows]


def select_project(key: str, cfg: dict, project: dict) -> dict:
    cfg["project"] = project
    cfg["stages"] = fetch_stages(key, project["id"])
    write_json(CONFIG, cfg)
    return {
        "project": project,
        "has_testing_stage": any(s["key"] == "testing" for s in cfg["stages"]),
        "intake_enabled": project["intake_enabled"],
    }


# --------------------------------------------------------------------------- MCP registration


def mcp_entry() -> dict:
    python = (read_json(INSTALL, {}) or {}).get("python") or sys.executable
    return {"type": "stdio", "command": python, "args": [str(SCRIPTS / "serve.py")], "env": {}}


def mcp_registered() -> bool:
    data = read_json(claude_json_path(), {}) or {}
    return SERVER in (data.get("mcpServers") or {})


def register_mcp() -> dict:
    path = claude_json_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        return {"ok": False, "reason": "claude_config_unreadable"}
    servers = data.setdefault("mcpServers", {})
    entry = mcp_entry()
    if servers.get(SERVER) == entry:
        return {"ok": True, "changed": False}
    backup = path.with_name(path.name + ".miraiminds-backup")
    if path.exists() and not backup.exists():
        shutil.copy2(path, backup)
    servers[SERVER] = entry
    write_json(path, data)
    return {"ok": True, "changed": True}


# --------------------------------------------------------------------------- key pop-up

_POPUP_TEXT = "Paste your connection key here, then click Connect."
_POPUP_TITLE = f"{TEAM['company']} tracker"

_WINDOWS_FORM = r"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()
$f = New-Object System.Windows.Forms.Form
$f.Text = '__TITLE__'
$f.ClientSize = New-Object System.Drawing.Size(440, 140)
$f.StartPosition = 'CenterScreen'
$f.TopMost = $true
$f.FormBorderStyle = 'FixedDialog'
$f.MaximizeBox = $false
$f.MinimizeBox = $false
$l = New-Object System.Windows.Forms.Label
$l.Text = '__TEXT__'
$l.AutoSize = $true
$l.Location = New-Object System.Drawing.Point(16, 18)
$t = New-Object System.Windows.Forms.TextBox
$t.UseSystemPasswordChar = $true
$t.Location = New-Object System.Drawing.Point(16, 48)
$t.Width = 408
$ok = New-Object System.Windows.Forms.Button
$ok.Text = 'Connect'
$ok.Location = New-Object System.Drawing.Point(244, 92)
$ok.DialogResult = 'OK'
$cancel = New-Object System.Windows.Forms.Button
$cancel.Text = 'Cancel'
$cancel.Location = New-Object System.Drawing.Point(336, 92)
$cancel.DialogResult = 'Cancel'
$f.AcceptButton = $ok
$f.CancelButton = $cancel
$f.Controls.AddRange(@($l, $t, $ok, $cancel))
$f.Add_Shown({ $f.Activate(); $t.Focus() })
if ($f.ShowDialog() -eq 'OK') { [Console]::Out.Write($t.Text) } else { exit 3 }
"""


def _popup_windows() -> tuple[str | None, str]:
    script = _WINDOWS_FORM.replace("__TITLE__", _POPUP_TITLE).replace("__TEXT__", _POPUP_TEXT)
    encoded = base64.b64encode(script.encode("utf-16-le")).decode()
    r = subprocess.run(
        ["powershell", "-NoProfile", "-STA", "-ExecutionPolicy", "Bypass", "-EncodedCommand", encoded],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if r.returncode == 3:
        return None, "cancelled"
    return (r.stdout.strip() or None), ("popup" if r.stdout.strip() else "cancelled")


def _popup_mac() -> tuple[str | None, str]:
    dialog = (
        f'text returned of (display dialog "{_POPUP_TEXT}" default answer "" with hidden answer '
        f'with title "{_POPUP_TITLE}" buttons {{"Cancel", "Connect"}} default button "Connect")'
    )
    r = subprocess.run(["osascript", "-e", "activate", "-e", dialog], capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        return None, "cancelled"
    return (r.stdout.strip() or None), "popup"


def _popup_linux() -> tuple[str | None, str]:
    for cmd in (
        ["zenity", "--password", f"--title={_POPUP_TITLE}"],
        ["kdialog", "--title", _POPUP_TITLE, "--password", _POPUP_TEXT],
    ):
        if shutil.which(cmd[0]):
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            return ((r.stdout.strip() or None), "popup") if r.returncode == 0 else (None, "cancelled")
    import tkinter
    from tkinter import simpledialog

    root = tkinter.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    value = simpledialog.askstring(_POPUP_TITLE, _POPUP_TEXT, show="*", parent=root)
    root.destroy()
    return (value.strip() or None, "popup") if value else (None, "cancelled")


def ask_key_popup() -> tuple[str | None, str]:
    system = platform.system()
    try:
        if system == "Windows":
            return _popup_windows()
        if system == "Darwin":
            return _popup_mac()
        return _popup_linux()
    except Exception:
        return None, "unavailable"


# --------------------------------------------------------------------------- commands


def cmd_start(_args) -> None:
    cfg = read_json(CONFIG, {}) or {}
    state = read_json(STATE, {}) or {}
    project = cfg.get("project")
    out(
        skill_version=TEAM["skill_version"],
        installed=INSTALL.exists(),
        connected=CREDENTIALS.exists(),
        mcp_registered=mcp_registered(),
        user=cfg.get("user"),
        project=project,
        projects_available=len(cfg.get("projects") or []),
        has_testing_stage=any(s.get("key") == "testing" for s in cfg.get("stages") or []),
        outbox=len(list(OUTBOX.glob("*.json"))) if OUTBOX.exists() else 0,
        last_seen=state.get("last_seen"),
        since=since_label(state.get("last_seen")),
        first_visit=not state.get("last_seen"),
        when=when_info(),
        surface=surface(),
        os=platform.system(),
        emergency=TEAM["emergency_contact"],
        tracker_url=TEAM["tracker_url"],
        item_url_template=TEAM["item_url_template"],
        upload_limit_mb=TEAM["upload_limit_mb"],
    )


def cmd_connect(args) -> None:
    key, how = (args.key, "argument") if args.key else ask_key_popup()
    if not key:
        return out(ok=False, reason="popup_unavailable" if how == "unavailable" else "cancelled")
    key = key.strip()
    try:
        me = api("users/me/", key)
        projects = fetch_projects(key)
    except urllib.error.HTTPError as exc:
        return out(ok=False, reason="bad_key" if exc.code in (401, 403) else "tracker_error", status=exc.code)
    except Exception:
        status = net_status()
        return out(ok=False, reason="tracker_unreachable" if status["internet"] else "no_internet")

    write_json(CREDENTIALS, {"api_key": key, "saved_at": now_utc_iso()}, private=True)
    cfg = read_json(CONFIG, {}) or {}
    name = me.get("display_name") or me.get("first_name") or ""
    cfg.update(
        user={"id": me.get("id"), "name": " ".join(filter(None, [me.get("first_name"), me.get("last_name")])) or name, "email": me.get("email")},
        projects=projects,
        connected_at=now_utc_iso(),
    )
    selected = None
    if len(projects) == 1:
        selected = select_project(key, cfg, projects[0])
    else:
        write_json(CONFIG, cfg)
    reg = register_mcp()
    out(
        ok=True,
        user=cfg["user"]["name"],
        projects=[{"identifier": p["identifier"], "name": p["name"], "intake_enabled": p["intake_enabled"]} for p in projects],
        selected=selected,
        mcp_registered=reg.get("ok", False),
        mcp_note=reg.get("reason"),
    )


def cmd_project(args) -> None:
    cfg = read_json(CONFIG, {}) or {}
    projects = cfg.get("projects") or []
    if args.action == "list" or not args.value:
        return out(ok=True, current=cfg.get("project"), projects=projects)
    key = load_key()
    if not key:
        return out(ok=False, reason="not_connected")
    wanted = args.value.strip().lower()
    match = next((p for p in projects if wanted in (p["id"].lower(), p["identifier"].lower(), p["name"].lower())), None)
    if not match:
        return out(ok=False, reason="unknown_project", projects=[p["name"] for p in projects])
    try:
        out(ok=True, **select_project(key, cfg, match))
    except Exception:
        out(ok=False, reason="tracker_unreachable")


def cmd_stages(args) -> None:
    cfg = read_json(CONFIG, {}) or {}
    if args.refresh and cfg.get("project") and load_key():
        try:
            cfg["stages"] = fetch_stages(load_key(), cfg["project"]["id"])
            write_json(CONFIG, cfg)
        except Exception:
            pass
    out(ok=True, stages=cfg.get("stages") or [], intake_status=INTAKE_STATUS)


def cmd_when(_args) -> None:
    out(**when_info())


def cmd_net(_args) -> None:
    out(**net_status())


def cmd_seen(args) -> None:
    state = read_json(STATE, {}) or {}
    if args.action == "set":
        state["last_seen"] = now_utc_iso()
        write_json(STATE, state)
    out(ok=True, last_seen=state.get("last_seen"), since=since_label(state.get("last_seen")))


def cmd_outbox(args) -> None:
    OUTBOX.mkdir(parents=True, exist_ok=True)
    if args.action == "new":
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return out(ok=True, path=str(OUTBOX / f"{stamp}.json"))
    if args.action == "done":
        target = (OUTBOX / Path(args.value or "").name).resolve()
        if target.parent != OUTBOX.resolve() or target.suffix != ".json" or not target.exists():
            return out(ok=False, reason="not_found")
        target.unlink()
        return out(ok=True, removed=target.name)
    items = []
    for f in sorted(OUTBOX.glob("*.json")):
        items.append({"file": f.name, "path": str(f), "draft": read_json(f, {})})
    out(ok=True, count=len(items), items=items)


def cmd_whatsapp(args) -> None:
    contact = TEAM["emergency_contact"]
    digits = re.sub(r"\D", "", contact["phone"])
    link = f"https://wa.me/{digits}"
    if args.text:
        link += "?text=" + urllib.parse.quote(args.text)
    out(ok=True, name=contact["name"], phone=contact["display"], link=link)


def _screenshot_dirs() -> list[Path]:
    names = ["Pictures/Screenshots", "OneDrive/Pictures/Screenshots", "Desktop", "OneDrive/Desktop", "Downloads", "Pictures"]
    dirs = [HOME / n for n in names]
    if platform.system() == "Darwin":
        try:
            custom = subprocess.run(
                ["defaults", "read", "com.apple.screencapture", "location"], capture_output=True, text=True, timeout=5
            ).stdout.strip()
            if custom:
                dirs.insert(0, Path(custom).expanduser())
        except Exception:
            pass
    return [d for d in dirs if d.is_dir()]


def cmd_screenshot(_args) -> None:
    found = []
    cutoff = datetime.now().timestamp() - 7 * 86400
    for folder in _screenshot_dirs():
        try:
            for f in folder.iterdir():
                if f.is_file() and f.suffix.lower() in IMAGE_TYPES and f.stat().st_mtime >= cutoff:
                    found.append(f)
        except OSError:
            continue
    found = sorted(set(found), key=lambda f: f.stat().st_mtime, reverse=True)[:3]
    now = datetime.now().timestamp()
    out(
        ok=True,
        images=[
            {"path": str(f), "name": f.name, "minutes_ago": int((now - f.stat().st_mtime) // 60), "folder": f.parent.name}
            for f in found
        ],
    )


def cmd_upload(args) -> None:
    key = load_key()
    cfg = read_json(CONFIG, {}) or {}
    project_id = args.project or (cfg.get("project") or {}).get("id")
    if not key or not project_id:
        return out(ok=False, reason="not_connected")
    path = Path(args.file).expanduser()
    if not path.is_file():
        return out(ok=False, reason="file_not_found")
    limit = TEAM["upload_limit_mb"] * 1024 * 1024
    if path.stat().st_size > limit:
        return out(ok=False, reason="too_big", limit_mb=TEAM["upload_limit_mb"])
    try:
        from plane import PlaneClient

        client = PlaneClient(base_url=TEAM["tracker_url"], api_key=key)
        client.work_items.attachments.upload_from_bytes(
            workspace_slug=TEAM["workspace_slug"],
            project_id=project_id,
            work_item_id=args.item,
            file_bytes=path.read_bytes(),
            name=path.name,
            content_type=mimetypes.guess_type(path.name)[0] or "application/octet-stream",
        )
    except Exception as exc:
        return out(ok=False, reason="upload_failed", detail=str(exc)[:300])
    out(ok=True, name=path.name)


def cmd_open(args) -> None:
    urls = {"token": TEAM["token_page_url"], "tracker": TEAM["tracker_url"]}
    url = urls.get(args.what, args.what if str(args.what).startswith(TEAM["tracker_url"]) else None)
    if not url:
        return out(ok=False, reason="unknown_page")
    out(ok=webbrowser.open(url), url=url)


def cmd_repair(_args) -> None:
    out(**register_mcp(), connected=CREDENTIALS.exists())


def cmd_uninstall(_args) -> None:
    """Remove the tracker connection, the safety rules and the saved key. Claude then deletes the skill folder."""
    removed = []
    uv = (read_json(INSTALL, {}) or {}).get("uv") or "uv"

    path = claude_json_path()
    data = read_json(path)  # None if missing or unreadable: then leave it alone
    if isinstance(data, dict) and SERVER in (data.get("mcpServers") or {}):
        del data["mcpServers"][SERVER]
        write_json(path, data)
        removed.append("tracker connection")

    settings_path = Path(os.environ.get("CLAUDE_CONFIG_DIR") or HOME / ".claude") / "settings.json"
    settings = read_json(settings_path)
    if isinstance(settings, dict):
        hooks = settings.get("hooks") or {}
        before = hooks.get("PreToolUse") or []
        kept = [
            entry
            for entry in before
            if not any(
                "skills/task/scripts/guard.py" in str(h.get("command", "")).replace("\\", "/")
                for h in entry.get("hooks", [])
            )
        ]
        if len(kept) != len(before):
            if kept:
                hooks["PreToolUse"] = kept
            else:
                hooks.pop("PreToolUse", None)
            if not hooks:
                settings.pop("hooks", None)
            removed.append("safety rules")
        env = settings.get("env") or {}
        if env.get("MCP_TIMEOUT") == "120000":
            env.pop("MCP_TIMEOUT")
            if not env:
                settings.pop("env", None)
        write_json(settings_path, settings)

    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
        removed.append("saved key and settings")

    out(
        ok=True,
        removed=removed,
        next=f'Delete the folder "{SKILL_DIR}", then run: "{uv}" tool uninstall plane-mcp-server',
    )


def cmd_doctor(_args) -> None:
    cfg = read_json(CONFIG, {}) or {}
    status = net_status()
    parts = [
        f"{platform.system()} {platform.release()}",
        f"Claude: {surface()}",
        f"skill {TEAM['skill_version']}",
        f"installed: {'yes' if INSTALL.exists() else 'no'}",
        f"key saved: {'yes' if CREDENTIALS.exists() else 'no'}",
        f"connection added: {'yes' if mcp_registered() else 'no'}",
        f"project: {(cfg.get('project') or {}).get('identifier', 'none')}",
        f"internet: {'yes' if status['internet'] else 'no'}",
        f"tracker reachable: {'yes' if status['tracker'] else 'no'}",
    ]
    out(ok=True, summary=", ".join(parts), **status)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="tt", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("start", help="everything /task needs to know at the start of a run").set_defaults(fn=cmd_start)
    p = sub.add_parser("connect", help="ask for the connection key in a pop-up and connect")
    p.add_argument("--key", help="fallback only: the key, when no pop-up can be shown")
    p.set_defaults(fn=cmd_connect)
    p = sub.add_parser("project", help="list projects or choose the active one")
    p.add_argument("action", choices=["list", "set"])
    p.add_argument("value", nargs="?")
    p.set_defaults(fn=cmd_project)
    p = sub.add_parser("stages", help="the project's stages with plain-language meanings")
    p.add_argument("--refresh", action="store_true")
    p.set_defaults(fn=cmd_stages)
    sub.add_parser("when", help="date, working-day status and what to promise").set_defaults(fn=cmd_when)
    sub.add_parser("net", help="is the internet / the tracker reachable").set_defaults(fn=cmd_net)
    p = sub.add_parser("seen", help="when the client last had a briefing")
    p.add_argument("action", choices=["get", "set"])
    p.set_defaults(fn=cmd_seen)
    p = sub.add_parser("outbox", help="requests saved while the tracker was down")
    p.add_argument("action", choices=["new", "list", "done"])
    p.add_argument("value", nargs="?")
    p.set_defaults(fn=cmd_outbox)
    p = sub.add_parser("whatsapp", help="WhatsApp link to the emergency contact")
    p.add_argument("--text", default="")
    p.set_defaults(fn=cmd_whatsapp)
    sub.add_parser("screenshot", help="the newest pictures in the usual screenshot folders").set_defaults(fn=cmd_screenshot)
    p = sub.add_parser("upload", help="attach a local file to a request")
    p.add_argument("--item", required=True, help="work item id")
    p.add_argument("--file", required=True)
    p.add_argument("--project")
    p.set_defaults(fn=cmd_upload)
    p = sub.add_parser("open", help="open a tracker page in the browser")
    p.add_argument("what", help="token | tracker | a tracker URL")
    p.set_defaults(fn=cmd_open)
    sub.add_parser("repair", help="re-add the tracker connection to Claude").set_defaults(fn=cmd_repair)
    sub.add_parser("doctor", help="one-line summary of what works, for the emergency contact").set_defaults(fn=cmd_doctor)
    sub.add_parser("uninstall", help="remove the connection, safety rules and saved key").set_defaults(fn=cmd_uninstall)

    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
