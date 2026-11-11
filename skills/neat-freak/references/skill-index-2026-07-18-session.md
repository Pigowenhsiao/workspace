# Skill Index — 2026-07-18 Session

## 口徑狀態
- Skill_Index.md: 605 actual skills, header=605, drift=0 ✓
- Dangling references: 0 ✓
- Per-section headers: 8 sections, all match ✓

## 發現問題

### 技能路徑衝突：`neat-freak` 存在於兩處

| 路徑 | 行數 | 備註 |
|------|------|------|
| `~/.hermes/skills/neat-freak/` | 1403 | **canonical（正確）** |
| `~/.hermes/skills/productivity/neat-freak/` | 1395 | 副本，缺「Cron 調用方式」段落 |

差距：8行。canonical 多了「Cron 調用方式」段落（包含 2026-07-17 的路徑衝突警告）。

**影響**：cron job 的 `skills=[neat-freak]` 配置目前正常（指向 canonical），但 bare name 匹配具有隨機性，若系統遍歷順序改變可能匹配到錯誤副本。

**建議修正**：刪除 `productivity/neat-freak/` 目錄，或將 `neat-freak` skill 的 category 從 `productivity` 改為唯一名稱杜絕碰撞。

### Cron Job 現況
- `~/.hermes/cron/jobs.json` 內有 20+ 個 jobs
- 所有 jobs 的 `last_status` 均為 `ok`
- 無 active divergence，無 stash
- Vault (`~/Documents/Pigo_Obsidian`) git-tracked，clean
- Agent (`~/Documents/Agent`) ahead/behind=0，clean

## 記憶框架現況
- `~/.hermes/memory/P0-core.md` — 正常，內容完整
- `~/.hermes/memory/P1-90days.md` — 正常
- `~/.hermes/memory/P2-30days.md` — 正常，P2 項目無過期

## 結論
知識庫整潔，無需立即干預。建議儘早解決 `productivity/neat-freak` 碰撞問題。
