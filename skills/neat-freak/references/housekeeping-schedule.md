# Housekeeping Schedule

## Daily Tasks (自動化 via Cron)

| Time | Task | Job Name | Verification |
|------|------|----------|--------------|
| `0 0 * * *` | Hermes backup | Hermes 每日備份 | 檢查 backup 產出存在 |
| `0 16 * * *` | Vault 整潔同步 | Vault 整潔同步（neat-freak） | `git fsck --full` clean |
| `0 0 * * *` | Kanban 清理 | Kanban 每日清理 | job status = ok |

## Weekly Tasks (手動觸發)

| Trigger | Task | Command |
|---------|------|---------|
| 週末 | Cron output 總清理 | `python3 ~/.hermes/skills/neat-freak/scripts/cron-output-cleanup.py` |
| 週末 | Memory sync 複檢 | `diff ~/.hermes/memory/*.md ~/Documents/Agent/memory/*.md` |
| 週末 | Skills drift check | `diff ~/.hermes/skills/<name>/SKILL.md ~/Documents/Agent/skills/<name>/SKILL.md` |

## Monthly Tasks (手動觸發)

| Task | Command |
|------|---------|
| Hermes skills git gc | `cd ~/.hermes/skills && git gc --prune=now` |
| Backup restore 驗證 | 見 `hermes-backup-protocol.md` |
| Skill_Index.md 行數驗證 | `SKILL_COUNT=$(ls ~/Documents/Agent/skills/ \| grep -v "^\." \| wc -l)` |

## On-Demand Tasks

| 情況 | Task | Command |
|------|------|---------|
| Push 被 rejected | 檢查 rebase hazard | `git log --oneline origin/main..HEAD` |
| `Script not found` cron 失敗 | 檢查 script path | 確認 job prompt 為 `bash /path/to/script.sh`，非 `script` 欄位 |
| 記憶 drift | 同步記憶 | 以 `~/.hermes/memory/` 為準同步到 Codex |
| Frontmatter corruption | 驗證並修復 | `bash ~/.hermes/skills/neat-freak/scripts/verify-skill-frontmatter.sh <name>` |
| Dangling objects 多 | 清理 | `bash ~/.hermes/skills/neat-freak/scripts/git-dangling-cleanup.sh <repo>` |

## Retention Policy

| 類型 | Retention | 處理方式 |
|------|-----------|---------|
| Cron output `.md` | 7 days | `cron-output-cleanup.py` |
| Hermes backup | 30 days | 季度清理過舊 backup 目錄 |
| Git reflog | — | 在 `git-dangling-cleanup.sh` 中清理 |
| skill-backup | — | 由 curator 管理，不手動處理 |
