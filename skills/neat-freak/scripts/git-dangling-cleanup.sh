#!/usr/bin/env bash
# git-dangling-cleanup.sh
# Complete dangling object cleanup for a git repo.
# Usage: ./git-dangling-cleanup.sh /path/to/repo
# Verification: run fsck --full after; dangling objects should be gone.

set -euo pipefail

# === Frontmatter Verification ===
verify_frontmatter() {
  local file="$1"
  local expected_name="$2"
  local actual_name
  actual_name=$(sed -n '2s/^name: //p' "$file")
  if [[ "$actual_name" != "$expected_name" ]]; then
    echo "[SYNC ERROR] $file frontmatter corrupted: name='$actual_name', expected='$expected_name'" >&2
    echo "[SYNC ERROR] Run: skill_manage patch '$expected_name' frontmatter manually" >&2
    return 1
  fi
  echo "[OK] $file frontmatter verified: name=$actual_name"
}

REPO="${1:-.}"

echo "[dangling-cleanup] Starting full cleanup for: $REPO"
cd "$REPO"

echo "[dangling-cleanup] Step 1: expire all reflog entries..."
git reflog expire --expire=now --all

echo "[dangling-cleanup] Step 2: garbage collect with aggressive prune..."
git gc --aggressive --prune=now

echo "[dangling-cleanup] Step 3: verify with fsck..."
if git fsck --full --no-progress 2>&1 | grep -q "dangling"; then
    echo "[dangling-cleanup] WARN: dangling objects still present after cleanup"
    git fsck --full --no-progress 2>&1 | grep "dangling"
    exit 1
else
    echo "[dangling-cleanup] OK: no dangling objects"
fi
