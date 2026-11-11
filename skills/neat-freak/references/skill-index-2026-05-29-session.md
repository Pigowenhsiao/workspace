# 2026-05-29 Session — 知識庫整頓 + Skill 更新

## 本次發現：路徑參照衝突

**觀察**：審視現有文件時發現 `AGENTS.md` 第 103-104 行紀錄 Vault 路徑為 `~/Documents/Obsidian`，但磁碟上的實際目錄名是 `~/Documents/Pigo_Obsidian`。記憶系統（`memory/P0-core.md`）早已正確記錄 `~/Documents/Pigo_Obsidian`，但 AGENTS.md 遲遲未同步。

**修復動作**：
1. 比對確認差異（`~/Documents/Obsidian` vs `~/Documents/Pigo_Obsidian`）
2. Patch AGENTS.md 兩處路徑
3. Auto-sync 機制已將修正傳遞至 `AGENT/AGENTS.md`
4. Commit `793832e2` 並 push 至 origin/main

**為什麼舊檢查抓不到**：
- Step 1 的 `find -name "*.md"` 只列舉檔案，不比對檔案間的內容邏輯一致性
- 舊的相對時間 / 版本號 grep、dangling entries 檢查都不涉及路徑字串的 cross-document 驗證

## Skill 更新：新增 Pattern CC

**新增位置**：`SKILL.md` 腐蝕圖譜（在 Pattern T 前插入）

**內容**：路徑參照衝突的發現、診斷、修復流程。Key insight：
- 路徑衝突不同於 dangling file（檔案層級 vs 事實層級）
- 舊檢查不涉及 cross-document 邏輯一致性
- 只報 warning，不自動修改——需要人工裁決

## 清理：移除重複的 Pattern Z2 段落

原 SKILL.md 有一段重複的 Pattern Z2（與 Pattern S/Z 的 EXTRA 確認流程重疊），已移除。
保留真正的 Z2 content 在腐蝕圖譜的位置（S/Z 系列之後），但移除中間那段重複的「觸發 + 確診結果」block。

## 口徑確認

| 指標 | 值 | 狀態 |
|------|-----|------|
| sync-check.py | All clean（Pattern Z EXTRA 皆為正當 tracked content） | ✓ |
| skill-index-check.py | 580 actual, header match, 0 dangling | ✓ |
| Branch | ahead 0, behind 0，完全同步 | ✓ |
| Git 工作樹 | 乾淨 | ✓ |

## 結論

1. Vault 路徑衝突已修復並推送
2. Pattern CC 已寫入腐蝕圖譜（路徑參照 cross-document 驗證缺失）
3. Skill 重複內容已清理