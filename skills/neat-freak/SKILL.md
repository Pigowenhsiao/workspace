---
name: neat-freak
description: 潔癖級知識整理與工作區同步助手。會話結束後對專案文件和 Agent 記憶進行潔癖級審查與同步，確保知識體系不因時間而腐壞。核心職責：vault ↔ git 同步、記憶框架健康度、Agent skills 一致性檢查、懸垂物件清理。
---

# Neat Freak — 潔癖級工作區同步

> 觸發關鍵字：`neat-freak`、`跑一下`、`潔癖同步`、`vault 整潔`、`整理工作區`

## Description

潔癖級知識整理與工作區同步助手。會話結束後對專案文件和 Agent 記憶進行潔癖級審查與同步，確保知識體系不因時間而腐壞。

核心職責：
- **Vault ↔ Git 同步**：確保 vault 乾淨（無 uncommitted，無 dangling objects）
- **記憶框架健康度**：檢查 `~/.hermes/memory/` 與 Codex memory 同步狀態
- **Agent Skills 一致性**：確認 Agent repo skills 與文檔同步，無腐敗 drift
- **Cron Output 清理**：執行 7-day retention 清理，移除過期輸出檔
- **懸垂物件處理**：清理 git dangling objects，保持 repo 健康

---

## Execution Checklist

執行 neat-freak 時，依序完成以下項目：

### Phase 1 — Vault Git Health

- [ ] `cd ~/Documents/Pigo_Obsidian && git status --short`
- [ ] 如有 uncommitted → `git add -A && git commit -m "chore: pre-neat-freak sync"` 並 push
- [ ] `git fsck --full --no-progress 2>&1 | grep dangling` → 如有，執行 `bash ~/.hermes/skills/neat-freak/scripts/git-dangling-cleanup.sh ~/Documents/Pigo_Obsidian`
- [ ] 驗證乾淨：`git fsck --full --no-progress 2>&1 | grep dangling` → 無輸出

### Phase 2 — Memory Sync

- [ ] `diff ~/.hermes/memory/P0-core.md ~/Documents/Agent/memory/P0-core.md && echo "P0 SYNC-OK" || echo "P0 DIFT"`
- [ ] `diff ~/.hermes/memory/P1-90days.md ~/Documents/Agent/memory/P1-90days.md && echo "P1 SYNC-OK" || echo "P1 DIFF"`
- [ ] `diff ~/.hermes/memory/P2-30days.md ~/Documents/Agent/memory/P2-30days.md && echo "P2 SYNC-OK" || echo "P2 DIFF"`
- [ ] 如有 DIFF → 以 `~/.hermes/memory/` 為準，同步到 `~/Documents/Agent/memory/`，並 commit
- [ ] **Trailing newline 注意**：`diff` 報告 identical 但比對失敗時，檢查檔案結尾是否有 `\n`（見 `references/memory-sync-protocol.md`）

### Phase 3 — Skills Consistency

- [ ] `ls ~/Documents/Agent/skills/neat-freak/SKILL.md` → 確認 workspace 副本存在
- [ ] 驗證 frontmatter：`head -5 ~/Documents/Agent/skills/neat-freak/SKILL.md` 確認 `name: neat-freak`
  - ⚠️ **已知 bug（兩種 pattern）:**
    - **Pattern A**: `name: hermes-cron-jobs`（sync 時被 hermes-cron-jobs 內容覆寫）
    - **Pattern B**: 檔案以 `import json` 開頭（Python import 殘留，見 `references/frontmatter-corruption-bug.md`）
  - 如發現任一 pattern → 以 canonical 覆蓋後 `git -C ~/Documents/Agent add -A && git commit`
- [ ] 比對 canonical vs workspace：`diff ~/.hermes/skills/neat-freak/SKILL.md ~/Documents/Agent/skills/neat-freak/SKILL.md`
- [ ] 如有 drift 且以 canonical 為準 → 同步並 commit

### Phase 4 — Cron Output Retention

- [ ] 檢查：`for d in ~/.hermes/cron/output/*/; do count=$(ls "$d"/*.md 2>/dev/null | wc -l); echo "$(basename $d): $count files"; done`
- [ ] 超過 500 檔的 job 目錄 → 執行 `python3 ~/.hermes/skills/neat-freak/scripts/cron-output-cleanup.py`
- [ ] 驗證：重新計算 count，確認刪除後數量合理

### Phase 5 — Hermes Backup (if scheduled)

- [ ] 確認備份腳本存在且可執行：`ls ~/.hermes/scripts/hermes-backup.sh`
  - 如不存在 → **略過此 phase**，於回報中標記 ⚠️ 告知 Pigo 備份機制未設定
- [ ] 執行備份：`bash ~/.hermes/scripts/hermes-backup.sh`
- [ ] 驗證備份產出存在於預期路徑

---

## jobs.json Structure

Location: `~/.hermes/cron/jobs.json`

Top-level key is `"jobs"` (array), NOT a dict keyed by job name.

```python
import json
with open('/home/pigo/.hermes/cron/jobs.json') as f:
    d = json.load(f)
# d['jobs'] is the list of job objects
```

Each job object fields:
- `id`: unique string
- `name`: display name
- `prompt`: execution prompt (or path to script for script-based jobs)
- `skills`: list of skill names to load
- `skill`: primary skill name (null if script-based)
- `model`: model name (e.g. "MiniMax-M2.7") or null
- `provider`: provider name or null
- `script`: shell script content — **only for prompt-based jobs using `bash <script>`**
  - For script-based execution, prefer an external `.sh` file; see "Critical pattern" below
- `no_agent`: bool — true means pure script, no LLM
- `schedule`: `{"kind": "cron", "expr": "0 0 * * *", "display": "0 0 * * *"}`
- `schedule_display`: cron expression string
- `repeat`: `{"times": null, "completed": N}` — completed count
- `enabled`: bool
- `state`: "scheduled" | "paused" | ...
- `last_run_at`: ISO timestamp
- `last_status`: "ok" | "error" | ...
- `last_error`: error message string
- `deliver`: "telegram" | "origin" | ...
- `origin`: `{"platform": "telegram", "chat_id": "...", "chat_name": "..."}`

## Output Directory

Each job has an output dir under `~/.hermes/cron/output/<job-id>/` containing timestamped `.md` files with job run outputs.

## Health Check Command

```bash
# List all jobs with schedule + enabled + last_status
python3 -c "
import json
with open('/home/pigo/.hermes/cron/jobs.json') as f:
    d = json.load(f)
for j in d['jobs']:
    print(f\"{j['name']}: schedule={j['schedule_display']} last={j.get('last_status','?')} enabled={j['enabled']}\")"
```

## Cron Job Patterns (Pigo's Setup)

| Name | Schedule | Model | Skills | Deliver |
|------|----------|-------|--------|---------|
| 每日晨報 | `0 0 * * *` | default | none | telegram |
| Hermes 每日備份 | `0 0 * * *` | default | none | telegram |
| HF Daily Papers | `0 1 * * *` | default | hermes-agent | telegram |
| 每日精選晚報 | `0 12 * * *` | MiniMax-M2.7 | hermes-agent, article-to-obsidian-knowledge | origin |
| 週更新 superpowers+GSD+gstack | `0 1 * * 1` | MiniMax-M2.7 | none | origin |
| Vault 整潔同步（neat-freak） | `0 16 * * *` | default | neat-freak | origin |
| Kanban 每日清理 | `0 0 * * *` | (prompt-based) | none | origin |
| Kanban Parallel Dispatcher | (interval) | default | kanban-worker | origin |

## Rebase Conflict Hazard — Agent Repo Push

> **已知的危險模式（2026-06-08 發現）**
> `git pull --rebase` → conflict → `git rebase --skip` 會**靜默丟棄本地 commit**，導致 push 報 "Everything up-to-date" 但變更實際上已消失。
>
> 詳見 `references/rebase-conflict-hazard.md`。

## Critical Pattern: no_agent Script-Based Jobs

**The "Script not found" failure mode (root cause)**:

Hermes cron engine interprets `script` field content as the path to a shell script to execute.
If you put multi-line bash content directly in `script`, the engine treats the first line of
that content as the script path — so a `script` starting with `#!/bin/bash` becomes an attempt
to execute `/home/pigo/.hermes/scripts/#!/bin/bash`, which fails with "Script not found".

**Correct pattern**:
1. Extract script content to a real file (e.g. `~/.hermes/scripts/kanban-daily-cleanup.sh`)
2. Make it executable: `chmod +x ~/.hermes/scripts/<name>.sh`
3. Set `no_agent: null` and use `prompt: "bash /path/to/script.sh"` instead of `script: ...`
4. Verify: run `bash /path/to/script.sh` standalone first, then confirm cron job status becomes `ok`

**Why this matters**: A job with `no_agent: true` and embedded `script` content will silently
fail on every run if the script starts with a shebang. The error is "Script not found" because
the shebang line is being interpreted as a file path.

---

## Reference Index

| File | Topic |
|------|-------|
| `references/dangling-objects.md` | Git dangling objects 成因、清理流程、`git gc` 行為澄清 |
| `references/memory-sync-protocol.md` | Hermes ↔ Codex 記憶同步 protocol、trailing newline 陷阱 |
| `references/cron-output-retention.md` | Cron output 7-day retention、Python cleanup script |
| `references/frontmatter-corruption-bug.md` | Workspace sync 後 frontmatter 被覆寫的 bug 與預防 |
| `references/rebase-conflict-hazard.md` | Rebase-skip 導致 commit 靜默消失的危險模式 |
| `references/hermes-cron-jobs.md` | jobs.json 結構、health check command、cron patterns |
| `references/skill-discovery.md` | Skill 存在性驗證、Skill_Index.md 行數陷阱、embedded .git 偵測 |
| `references/sync-matrix.md` | 變更影響矩陣、記憶層/程式碼層/文件層同步範圍 |
| `references/agent-paths.md` | 各 Agent 平台（Claude Code/Codex/OpenClaw/OpenCode）路徑速查 |
| `references/openclaw-exec-allowlist-fix.md` | OpenClaw safeBins + safeBinProfiles 二層修復（與 neat-freak 相關但非核心） |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/git-dangling-cleanup.sh` | 完整 dangling object 清理（reflog expire + gc --prune=now） |
| `scripts/cron-output-cleanup.py` | Cron output 7-day retention cleanup（Python，避免 approval prompt） |
| `scripts/verify-skill-frontmatter.sh` | 驗證 skill SKILL.md frontmatter 是否正確（預防 corruption bug） |
