# Pattern GG (refined): Dated STATUS files in docs/ — active content vs archived backup

## 觀察

在 `~/Documents/Agent/docs/` 底下發現 8 個 `STATUS_2026-04-*.md` 檔案：
- `STATUS_2026-04-08_llm-wiki-unified-ingest-notion-first-sync.md`
- `STATUS_2026-04-14_agent_pull_commit_push.md`
- `STATUS_2026-04-14_gitignore_tmp_x_article.md`
- `STATUS_2026-04-14_obsidian_skill_set_sync_and_push.md`
- `STATUS_agent_cookie_first_auth_policy_sync.md`
- `STATUS_codexskills_gstack_reorganization.md`
- `STATUS_obsidian_deep_reorganization.md`
- `STATUS_obsidian_docs_and_files_deep_reorganization.md`

每個檔案都含有實質性工作內容（具體的變更、驗證結果、下一步），但因為含日期後綴而**未被 STATUS_ALL.md 收錄**，淪為事實上的 orphan history。

## 與 Pattern DD 的區別

| 類型 | 位置 | 檔名格式 | 內容性質 | 處理方式 |
|------|------|----------|----------|----------|
| Pattern DD（已封存備份） | `Agent/AGENTS_2026-05-02.md` | 含 `YYYY-MM-DD` 後綴 | 明確標記為歷史截圖 | **不修改**，保留原樣 |
| **本次案例（active content orphan）** | `docs/STATUS_2026-04-*.md` | 含 `YYYY-MM-DD` 後綴 | 實質工作紀錄 | **合併進 STATUS_ALL.md**，刪除原文 |

**判斷關鍵**：
- `AGENTS_2026-05-02.md` 這類是「某個時間點的狀態截圖」，內容本身是完整的歷史狀態
- `docs/STATUS_2026-04-*.md` 這類是「工作中的變更記錄」，只是剛好用了 dated 檔名
- 前者體現「當時是這樣的」，後者體現「這個人做了什麼」
- **工作紀錄類**（後者）應該整合進無日期的 STATUS_ALL.md，確保歷史不被碎片化

## 修復流程（已實戰驗證）

```bash
# Step 1: 找出 docs/ 下所有 dated STATUS 檔案
ls ~/Documents/Agent/docs/STATUS_2026-*.md 2>/dev/null

# Step 2: 確認每個檔案內容是否為實質工作記錄
# （而非狀態截圖）
for f in ~/Documents/Agent/docs/STATUS_2026-*.md; do
  echo "=== $(basename "$f") ==="
  grep -A3 "## 本次變更\|## 你做了甚麼變更" "$f" | head -8
done

# Step 3: 檢查內容是否已存在於 STATUS_ALL.md
# （避免重複整合）
grep -c "2026-04-08_llm-wiki\|2026-04-14_agent_pull" \
  ~/Documents/Agent/STATUS_ALL.md

# Step 4: 若不存在，逐個 append 到 STATUS_ALL.md
# 格式：移除檔名中的日期後綴，保留 ## 層級章節結構
# 必要章節：## 本次變更 / ## 驗證結果 / ## 若仍失敗 / ## 下一步

# Step 5: 刪除已合併的 dated 檔案
rm ~/Documents/Agent/docs/STATUS_2026-*.md

# Step 6: git add + commit + push
```

## 為什麼不直接刪除

直接刪除會丟失 8 個有價值的工作記錄。這些是：
- 2026-04-08 llm-wiki 單一入口改造記錄
- 2026-04-14 gitignore 收尾、Obsidian skill set sync、git pull/commit/push 記錄
- agent cookie-first auth policy sync 記錄
- CodexSkills gstack 重組、Obsidian deep reorganization 記錄

都是實際發生過的重要變更，不應因為「檔名有日期」就當作廢棄物。

## 預防

每次完成工作並寫入 dated STATUS 檔案後，**當次 session 就要評估是否直接整合進 STATUS_ALL.md**，不要累積到下次 clean-up 才處理。
