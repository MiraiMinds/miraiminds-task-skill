#!/usr/bin/env python3
"""Start the tracker MCP server with the saved connection key.

Claude launches this as the `miraiminds-tracker` MCP server. It reads the key from
~/.miraiminds/task/credentials.json, so the key never sits in ~/.claude.json, and
then hands over to plane-mcp-server's own stdio entry point in this process.
"""

import os
import sys
import warnings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings("ignore")  # the connector's dependencies print deprecation notices on start

from tt import TEAM, load_key  # noqa: E402

key = load_key()
if not key:
    sys.stderr.write("MiraiMinds tracker: no connection key saved yet. Type /task to connect.\n")
    sys.exit(1)

os.environ["PLANE_API_KEY"] = key
os.environ["PLANE_WORKSPACE_SLUG"] = TEAM["workspace_slug"]
os.environ["PLANE_BASE_URL"] = TEAM["tracker_url"]
os.environ.setdefault("LOG_PAYLOADS", "false")

from plane_mcp.__main__ import main  # noqa: E402

sys.argv = ["plane-mcp-server", "stdio"]
main()
