#!/usr/bin/env bash
# verify-skill-frontmatter.sh
# Verifies that a skill's SKILL.md frontmatter is correct.
# Usage: ./verify-skill-frontmatter.sh <skill-name> [skill-dir]
# Example: ./verify-skill-frontmatter.sh neat-freak ~/.hermes/skills/neat-freak/

set -euo pipefail

SKILL_NAME="${1:-}"
SKILL_DIR="${2:-}"

if [[ -z "$SKILL_NAME" ]]; then
    echo "Usage: $0 <skill-name> [skill-dir]" >&2
    exit 1
fi

# Determine the skill directory
if [[ -z "$SKILL_DIR" ]]; then
    # Try canonical locations
    for dir in \
        "$HOME/.hermes/skills/${SKILL_NAME}" \
        "$HOME/Documents/Agent/skills/${SKILL_NAME}"; do
        if [[ -d "$dir" ]]; then
            SKILL_DIR="$dir"
            break
        fi
    done
fi

if [[ -z "$SKILL_DIR" || ! -d "$SKILL_DIR" ]]; then
    echo "ERROR: Cannot find skill directory for '$SKILL_NAME'" >&2
    exit 1
fi

SKILL_FILE=""
for f in "$SKILL_DIR/SKILL.md" "$SKILL_DIR/Skill.md"; do
    if [[ -f "$f" ]]; then
        SKILL_FILE="$f"
        break
    fi
done

if [[ -z "$SKILL_FILE" ]]; then
    echo "ERROR: No SKILL.md found in $SKILL_DIR" >&2
    exit 1
fi

echo "[verify] Checking frontmatter: $SKILL_FILE"

# Extract name from frontmatter (line 2: "name: value")
FRONT_NAME=$(sed -n '2s/^name: //p' "$SKILL_FILE")
FRONT_NAME="${FRONT_NAME//$'\r'/}"  # strip any CR

# Extract description from frontmatter (line 3: "description: value")
FRONT_DESC=$(sed -n '3s/^description: //p' "$SKILL_FILE")
FRONT_DESC="${FRONT_DESC//$'\r'/}"

if [[ "$FRONT_NAME" != "$SKILL_NAME" ]]; then
    echo "ERROR: frontmatter name='$FRONT_NAME', expected '$SKILL_NAME'" >&2
    echo "       File: $SKILL_FILE" >&2
    echo "       Symptom: likely frontmatter corruption after workspace sync" >&2
    echo "       Fix: cp canonical SKILL.md and manually restore frontmatter name" >&2
    exit 1
fi

if [[ -z "$FRONT_DESC" ]]; then
    echo "WARN: description is empty in frontmatter" >&2
fi

echo "[OK] frontmatter verified: name=$FRONT_NAME"
echo "[OK] description: ${FRONT_DESC:0:60}..."
exit 0
