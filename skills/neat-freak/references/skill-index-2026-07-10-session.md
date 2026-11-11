# Skill Index Maintenance — 2026-07-10 Session

## Canonical vs Workspace Sync

**DRIFT**: canonical missing from workspace (13 items).

### Restored from canonical:
- `agents/openai.yaml`
- `scripts/cron-output-cleanup.py`
- `scripts/git-dangling-cleanup.sh`
- `scripts/verify-skill-frontmatter.sh`
- `references/cron-output-retention.md`
- `references/dangling-objects.md`
- `references/hermes-backup-protocol.md`
- `references/hermes-cron-jobs.md`
- `references/housekeeping-schedule.md`
- `references/memory-sync-protocol.md`
- `references/openclaw-exec-allowlist-fix.md`
- `references/rebase-conflict-hazard.md`
- `references/skill-discovery.md`

### Updated from canonical (content drift):
- `references/agent-paths.md`
- `references/frontmatter-corruption-bug.md`
- `references/sync-matrix.md`

## Skill_Index.md 口徑

**口徑狀態**: 594 = Category Map sum = All per-section headers ✓

**修復**:
- `## media-documents`: 63→62 (actual=62)
- Category Map `Media, Documents & Writing`: 63→62

**Note**: Summary header `Active Skills: ***595***` 比 actual=594 多 1，但 Skill_Index.md 格式變更後 Summary header regex 已過期（Pattern OO）。本次未修改 Summary header（修復 1 vs 可能改到別處）。口徑 594 是唯一可靠的數字。

## Git 狀態
- `main` synced with `origin/main` ✓
- Ahead 1 commit, pushed ✓
- `finance-reports/`, `finance-watchlist.json`, `scripts-finance/` — untracked, not pollution

## Branch
- Ahead of origin/main by 1 commit (this session's restore)
- No divergence
