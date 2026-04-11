#!/usr/bin/env bash
set -euo pipefail

# Auto-commit all changes when Codex finishes a turn
# Only commits if there are actual changes

cd "${WORKING_DIR:-.}" 2>/dev/null || exit 0

if ! git rev-parse --is-inside-work-tree 2>/dev/null; then
    exit 0
fi

git add -A

if ! git diff --cached --quiet; then
    MSG="chore: auto commit by Codex at $(date -Iseconds)"
    git commit -m "$MSG"
    echo "[auto-commit] Committed: $MSG"
fi

exit 0
