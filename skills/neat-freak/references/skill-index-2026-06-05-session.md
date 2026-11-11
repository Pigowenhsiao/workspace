# Skill Index — 2026-06-05 Session

## 口徑驗證
- Skill_Index.md header: **517**（drift=0，header 與 actual rows 完全吻合）
- 磁碟上實際 SKILL.md: **599 個**（不含 vendor/archive/.system/.agents/）
- 口徑差額: 599 - 517 = **82 個** skills 未列入
- **全部 517 個 index 路徑全部 dangling**：路徑格式為 `../skills/mattpocock-skills/skills/X`（三層巢狀），磁碟為 `skills/X`（兩層）

## 本次發現
- **Pattern II 新增**：Readme.md mojibake corruption（UTF-8 double-encoding）
  - 受損範圍：lines 93-111（Communication / 執行策略 / 執行環境 三區段）
  - 腐蝕機制：UTF-8 編碼的中文被錯誤以 Latin-1 解讀後再次編碼
  - 修復：patch 18 行，精確置換為正確繁體中文
  - 源頭：歷史上某個非 UTF-8 環境寫入

## Canonical ↔ Workspace Sync 狀態
- sync-check.py DRIFT: agents/, references/Readme.md, scripts/Readme.md → 全為 origin/main tracked content，正當
- canonical vs workspace 內容 diff: 完全一致，無需 restore

## Branch 狀態
- ahead=0 behind=0，乾淨同步

## 其他檢查結果
- AGENTS.md 規範一致性：各 subdirectory AGENTS.md 的 STATUS 規範與根目錄一致（Pattern FF ✓）
- 記憶系統：P0-core / P1-90days / P2-30days 無過期/衝突
- 相對時間殘留：無
- 版本範例陳屍：無（dated Status 歸檔檔案除外，Pattern DD 已確認不修改）
- AGENTS_2026-05-02.md 被 Agent/Readme.md 標記為「已封存備份，勿作為 active 目標」，符合 Pattern GG，無需修復

## 提交記錄
- `eef85b10` fix: Readme.md mojibake corruption lines 93-111（已 push）
