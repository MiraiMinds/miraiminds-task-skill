#!/usr/bin/env bash
# Installs the MiraiMinds /task skill on macOS and Linux.
# Usage: bash install.sh [repo url]
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="${1:-}"
TEAM="$HERE/skill/config/team.json"
PACKAGE="$(sed -n 's/.*"mcp_server_package": *"\([^"]*\)".*/\1/p' "$TEAM")"
CONTACT_NAME="$(sed -n 's/.*"name": *"\([^"]*\)".*/\1/p' "$TEAM" | head -n 1)"
CONTACT_PHONE="$(sed -n 's/.*"display": *"\([^"]*\)".*/\1/p' "$TEAM" | head -n 1)"

fail() {
  printf '{"ok": false, "reason": "%s", "detail": "%s", "emergency": {"name": "%s", "display": "%s"}}\n' \
    "$1" "${2:-}" "$CONTACT_NAME" "$CONTACT_PHONE"
  exit 1
}

find_uv() {
  for candidate in "$(command -v uv 2>/dev/null || true)" "$HOME/.local/bin/uv" "$HOME/.cargo/bin/uv"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then echo "$candidate"; return; fi
  done
}

# 1. uv (installs Python and the tracker connector; no admin rights needed)
UV="$(find_uv)"
if [ -z "$UV" ]; then
  echo "Installing uv..."
  if command -v curl >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh || fail uv_install_failed "curl installer failed"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO- https://astral.sh/uv/install.sh | sh || fail uv_install_failed "wget installer failed"
  else
    fail uv_install_failed "neither curl nor wget is available"
  fi
  UV="$(find_uv)"
  [ -n "$UV" ] || fail uv_not_found "uv was installed but could not be found"
fi

# 2. The tracker connector, installed once so Claude doesn't wait for a download on every start
echo "Installing the tracker connector ($PACKAGE)..."
"$UV" tool install --force --compile-bytecode "$PACKAGE" || fail connector_install_failed "uv tool install failed"

PYTHON="$("$UV" tool dir)/plane-mcp-server/bin/python"
[ -x "$PYTHON" ] || fail connector_python_missing "$PYTHON"

# 3. Skill files, helper, safety rules
exec "$PYTHON" "$HERE/installer/install.py" --uv "$UV" --source "$SOURCE"
