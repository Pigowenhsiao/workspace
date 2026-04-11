#!/usr/bin/env python3
"""Log every Bash command to ~/.codex/command_log.txt"""
import json, os, sys
from datetime import datetime, timezone

LOG_FILE = os.path.expanduser("~/.codex/command_log.txt")

try:
    data = json.load(sys.stdin)
    # Extract command from tool_input
    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Determine working directory if available
    cwd = tool_input.get("cwd", os.getcwd())

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] [cwd={cwd}]\n  {command}\n\n")
except Exception as e:
    # Don't block the hook, just log
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}] ERROR: {e}\n")
