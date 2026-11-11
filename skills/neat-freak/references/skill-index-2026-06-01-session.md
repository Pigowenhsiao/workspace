# Skill Index Session — 2026-06-01

## 口徑確認

- 獨立 Python 驗證: Skill_Index.md = **486 rows**，header = 486（口徑 self-consistent，base 錯）
- 磁碟 SKILL.md: **600 個**（不含 vendor/archive/.system）
- 差額: **114 個** skills 未列入 index

## 發現的問題

1. **sync-check.py DRIFT（已確診為正當 sync content）**
   - EXTRA in workspace: agents/, references/Readme.md, scripts/Readme.md
   - `git ls-files` 確認全部為 origin/main tracked content → 保留
   - 2026-05-22 Pattern Z 已記錄此為正當組合

2. **script `Actual rows: 0` 虛假信號（已知 CRITICAL bug）**
   - `check_header_drift()` 的 regex 匹配不到 `- Active Skills: N` 格式
   - 依舊報告 `✓ ALL CLEAN` 卻同時 `Actual rows: 0`
   - 已記錄於腐蝕圖譜 Pattern AA，長期修復方向已知（函式重構）

3. **Pi-AGENTS.md OpenSpec block**
   - 條件式描述（「當工作在含 openspec/ 的專案內」），非強設引用
   - 不是 Pattern 22（OPENSPEC block 陳屍）——已確認無需刪除

4. **AGENT/Readme.md 的 dated backup 列表**
   - 如實列出 `AGENTS_2026-05-02.md`、`AGENTs.md.20260501`、`AGENTS.md.20260430`
   - 符合 Pattern GG（Primary Read Targets 包含已封存備份）→ 這不是問題
   - AGENT/Readme.md 的 Primary Read Targets 只有 `AGENTS.md`，未引用 dated backup

5. **name.md / func.md 非 orphan**
   - 為 Active workspace 文件，非 orphan

## 未處理

- **Skill_Index.md 口徑落後 114 個**：需完整重建，屬於 Skill Library Maintenance 專門 session
- 涉及路徑格式化（三層巢狀 → 兩層）、新增 114 個 rows、重算 header

## 結論

本次 session 為被動審查，無文件變更。Branch 乾淨、口徑 drift 0（對自己）、無相對時間殘留。發現的問題已記錄至腐蝕圖譜。