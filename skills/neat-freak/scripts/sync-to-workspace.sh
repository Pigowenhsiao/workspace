#!/bin/bash
# Sync canonical neat-freak to workspace sync copy
# Usage: bash scripts/sync-to-workspace.sh
CANONICAL=~/.hermes/skills/neat-freak
WORKSPACE=~/Documents/Agent/skills/neat-freak

cp "$CANONICAL/SKILL.md" "$WORKSPACE/SKILL.md"
for ref in "$CANONICAL"/references/*.md; do
  cp "$ref" "$WORKSPACE/references/"
done
for scr in "$CANONICAL"/scripts/*.py; do
  cp "$scr" "$WORKSPACE/scripts/"
done
echo "Done. Commit with: git -C ~/Documents/Agent add skills/neat-freak/ && git -C ~/Documents/Agent commit -m 'sync neat-freak from canonical'"
