# Neat-Freak SKILL.md Frontmatter Corruption Bug

## Symptom

Two corruption patterns observed:

**Pattern A — hermes-cron-jobs overwrite (2026-06-01):**
```yaml
---
name: hermes-cron-jobs           # WRONG — should be "neat-freak"
description: Pigo's Hermes cron...  # WRONG — should describe Neat Freak
---
# Hermes Cron Job Reference          # WRONG — should be "# Neat Freak —..."
```

**Pattern B — Python import residue (2026-06-25):**
```yaml
---
import json          # WRONG — first line should be "name: neat-freak"
import json          # repeated
[177 more lines]
```
The workspace file starts with `import json` on the first line after `---`, as if Python code was prepended to the YAML frontmatter.

## Root Cause

This is NOT a git merge conflict. The body of the skill was correctly copied — only the frontmatter is corrupted.

Likely cause: the sync script (`sync-to-workspace.sh`) or a previous copy operation wrote a stale cached version of the file's header, or the workspace copy was never properly updated after some content was accidentally merged into the skill body.

## Detection

**Do NOT rely on `head` alone** — it can render misleading output through pipe/TTY layers even when the file is fine.

1. Fast check — `diff` canonical vs workspace (authoritative):
   ```bash
   diff ~/.hermes/skills/neat-freak/SKILL.md ~/Documents/Agent/skills/neat-freak/SKILL.md
   ```
2. If diff says identical but you still see weird output → verify with `cat`, `od -c`, `sed -n '4,8p'`, or `wc -l`
3. Correct frontmatter should be:
   ```yaml
   ---
   name: neat-freak
   description: 潔癖級知識整理與工作區同步助手...
   ---
   ```

## Fix (per incidents 2026-06-01 and 2026-06-25)

**Always treat canonical (`~/.hermes/skills/neat-freak/`) as source of truth.**

1. Force-overwrite from canonical:
   ```bash
   cp ~/.hermes/skills/neat-freak/SKILL.md ~/Documents/Agent/skills/neat-freak/SKILL.md
   ```
2. Confirm identical:
   ```bash
   diff ~/.hermes/skills/neat-freak/SKILL.md ~/Documents/Agent/skills/neat-freak/SKILL.md
   ```
3. If `diff` shows "identical" but git still reports nothing to commit — this means the index already matches the working tree. Use `git -C ~/Documents/Agent add -A` to force re-staging, then commit.
4. Commit with message: `fix: overwrite corrupted neat-freak SKILL.md from canonical`

**NOTE on git add pitfall:** `git add` without `-f` may not re-stage an unchanged-looking file. Always verify with `diff` after the cp, then use `git -C ~/Documents/Agent add -A` if needed.

## Recurring Nature

- Pattern A first observed: 2026-05-22 (skill-index session corruption)
- Pattern A second occurrence: 2026-06-01 (Agent repo sync)
- Pattern B observed: 2026-06-25 (routine neat-freak sync)
- Pattern: every time canonical → workspace sync happens, workspace `SKILL.md` frontmatter gets corrupted

## Diagnostic Pitfall — `head` Can Lie (2026-06-25)

**Symptom:** `head -5` shows `import json` corruption but other tools (`cat`, `od`, `sed`, `tail`, `wc -l`, `diff`) show the file is actually fine.

**Root cause:** `head` can render misleading output through a pipe/TTY display layer when the shell context is complex. The file content itself is correct — `diff`, `cat`, `od -c`, `sed -n '4,8p'`, and `tail` all showed correct content. The `head` display was the red herring.

**Correct diagnostic sequence:**
1. `diff canonical workspace` — first check, fast, authoritative
2. If diff says identical but `head` shows weirdness → verify with `cat`, `od -c`, `sed -n '4,8p'`, or `wc -l`
3. Never trust `head` output alone when it contradicts `diff`
4. After confirming identical, still use `git add -A` to re-stage (git index vs working tree issue)

## Prevention

After any `cp` or `sync-to-workspace.sh` run targeting `neat-freak`, **always verify frontmatter before committing**, and always `diff` canonical vs workspace to confirm identical.
