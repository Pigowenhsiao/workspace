#!/usr/bin/env python3
"""Block dangerous commands before they execute in Codex."""
import json
import re
import os
import sys

DANGEROUS_PATTERNS = [
    (r"rm\s+-rf\s+/", "Recursive delete from root"),
    (r"rm\s+-rf\s+/(home|root|usr|etc|var|opt|mnt|sys|proc)", "Recursive delete of system directory"),
    (r"git\s+push\s+.*--force", "Force push to remote"),
    (r"git\s+reset\s+--hard", "Hard git reset (loses uncommitted changes)"),
    (r"git\s+rebase\s+-(i|interactive)\s+HEAD", "Interactive rebase from HEAD"),
    (r"DROP\s+(TABLE|DATABASE|INDEX)", "SQL DROP command"),
    (r"TRUNCATE\s+", "SQL TRUNCATE command"),
    (r"DELETE\s+FROM\s+\w+\s*;", "SQL DELETE without WHERE"),
    (r"curl\s+.*\|\s*(bash|sh|zsh|fish)", "Curl + pipe to shell (pipeline injection risk)"),
    (r"wget\s+.*\|\s*(bash|sh|zsh|fish)", "Wget + pipe to shell (pipeline injection risk)"),
    (r":\(\)\s*:\s*;", "Fork bomb"),
    (r"chmod\s+-R?\s*777", "World-writable permissions"),
    (r"chown\s+.*-R?\s+[0-9]+:[0-9]+", "Recursive ownership change"),
    (r">\s*/etc/", "Write to system file"),
    (r">\s*/sys/", "Write to sys filesystem"),
    (r"dd\s+.*of=/dev/(sd|nvme|hd)", "Direct disk write"),
    (r"shutdown|halt|poweroff|init\s+0", "System shutdown"),
    (r"mkfs", "Format filesystem"),
    (r":\!|eval\s+\$\(", "Eval injection pattern"),
    (r"cat\s+/etc/passwd", "Reading system passwd file"),
]

TAINTED_ENV_VARS = [
    "GITHUB_TOKEN", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "AWS_SECRET", "STRIPE_KEY", "SECRET", "PRIVATE_KEY",
]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # Don't block if can't parse

    tool_name = data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Check for tainted env vars being exported
    for var in TAINTED_ENV_VARS:
        if re.search(rf'\b{var}\b', command):
            print(f"[block_dangerous] WARNING: '{var}' appears in command", file=sys.stderr)
            # Not blocking, just warning

    # Check dangerous patterns
    for pattern, description in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            msg = (
                f"[block_dangerous] BLOCKED: {description}\n"
                f"  Command: {command}\n"
                f"  Reason: This pattern '{pattern}' is blocked for safety.\n"
                f"  Suggestion: Use a safer alternative or confirm with user."
            )
            print(msg, file=sys.stderr)
            sys.exit(2)  # Exit code 2 = block this action

    sys.exit(0)


if __name__ == "__main__":
    main()
