# Skill_Index.md 完整重建 session（2026-06-29）

## TL;DR

- **目標**：從 520 條 dangling/unlisted 落後狀態 → 605 條 0 落差
- **方法**：Pattern EE 觸發完整重建（incremental 修復歷史證明無效）
- **結果**：commit `c21198e5 docs: full rebuild Skill_Index.md from disk inventory (520 → 605)`
- **Pigo 數字低估**：他說 134 落後，實測 484 dangling + 584 unlisted = 1068 雙向落差

## 觸發信號

Pigo 訊息原文：
> "Skill_Index.md 口徑落後磁碟 134 個 skills（index 520 vs 磁碟 654）：這是 upstream 重構遺留的 400+ dangling rows 累積問題，屬於 Pattern EE 等級，需一次完整重建才能解決，不適合在單次 session 修補（每次修復只動一個 dangling 的做法已被歷史證明無效）"

關鍵觸發詞：
- 「**一次完整重建才能解決**」→ Pattern EE 嚴重
- 「**不適合在單次 session 修補**」→ incremental 不可行
- 「**歷史證明單次修補無效**」→ 過去有嘗試失敗記錄

## 完整重建流程（驗證過的 pattern）

### Step 0：備份（不可逆保護）
```bash
cp docs/Skill_Index.md docs/Skill_Index.md.bak-$(date +%Y%m%d-%H%M%S)
```
備份檔 commit 進去（pattern GG dated backup 適用），未來回溯用。

### Step 1：磁碟盤點 → 01-disk-inventory.json
```python
# 用 frontmatter 解析 + API key 偵測 + 排除政策
# 排除: SKILL.merged.md, references/, examples/
# 結果: 605 active skills
```

### Step 2：分類政策決策 → 選 A2-改2

| 選項 | 結果 | 評估 |
|---|---|---|
| A1 沿用 14 類 | 最小變動 | 14 類過細，且部分類別已無對應 skill |
| A2 純一級目錄 | 73 個 category（18% 是裸型）| 可讀性差 |
| **A2-改2 一級目錄 + Root-level** | **13 大分類 + 63 散落型** | **推薦** |
| A3 完全照磁碟 | 跟舊政策打架 | 破壞性 |
| A4 全部平鋪 | 失去分類導航 | 受眾（新人）找不到 |

**A2-改2 最終分布**：
- agent-workflows: 136
- science-data: 110
- media-documents: 66
- finance-skill-pack: 64
- knowledge-vault: 38
- engineering-review + git-devops + design-frontend-visual + browser-web-social: 92
- manual-review + matt-writing-research-lab + business-finance + learning-personas + utilities-local + punk-skills: 36
- Root-level Skills: 63

### Step 3：平行 dispatch subagent

**踩坑 1**：`max_concurrent_children=3` hard cap。一開始嘗試派 7 個 task，系統拒絕。

**正確切片**：8 組拆成 3+3+1+1（單獨派 G8 跟 G1）：
- Batch 1: G2, G3, G4 (110+66+64 = 240 條)
- Batch 2: G5, G6, G7 (38+92+36 = 166 條)
- 單派 G1 (136 條)
- 單派 G8 (63 條)

**踩坑 2**：單派 G8 時，**single-task `delegate_task` 的 result 沒回到對話**（subagent 跑完了，但完成訊息沒冒上來）。詳見 `subagent-dispatch` SKILL Pattern 6。

**恢復方式**：自己用 `execute_code` 跑 G8 的邏輯（純機械格式化，無需 LLM 判斷），產出 `03-rows-G8.md`。

### Step 4：merge_index.py 主線程合併

**踩坑 3**：subagent G4/G7 多了 column header 行（`| name | path | description | api_key |`）跟 markdown separator（`| --- | --- | --- | --- |`）。導致 raw count 多 1-2 行。

**修復**：merge script 加 `is_data_row()` 過濾：
- 用 `re.match` 過濾 `| name | path | description | api_key |`
- 用 cell 內容是否全為 `-` 過濾 separator

**merge script 必備的三個 column-header tolerance**：
- `| name | path | description | api_key |`（subagent 額外加的）
- `| --- | --- | --- | --- |`（markdown 標準 separator）
- Category Map 區段的 3 欄表格（`| Category | Count | Skills From |`）

### Step 5：驗證

| 指標 | 結果 |
|---|---|
| Paths in new index | 605 |
| Active SKILL.md on disk | 605 |
| Dangling (index → no disk) | 0 |
| Unlisted (disk → no index) | 0 |
| Duplicate paths | 0 |
| API key sum (header 30+115+460) | 605 |
| Categories (header) | 8 |

**驗證腳本坑**：第一版用 `line.split('|')` 嚴格計數 cell 數，遇到 description 含 escaped pipe `\|` 的 row 會算成 6 cells 而不是 5，導致 20 條 row 被當成無效。**改用寬鬆解析（找任何 cell 結尾是 `/SKILL.md` 的就是 path）** 才正確。

### Step 6：commit

```bash
git -C ~/Documents/Agent add docs/Skill_Index.md \
    docs/Skill_Index.md.bak-20260629-132619 \
    docs/.index-rebuild/ .gitignore
git -C ~/Documents/Agent commit -m "docs: full rebuild Skill_Index.md from disk inventory (520 → 605)"
```

**commit 內容決策**：
- ✅ commit：`docs/Skill_Index.md`、`docs/Skill_Index.md.bak-20260629-132619`、`docs/.index-rebuild/`（事實快照 + 8 組 input + 8 組 row + merge script）
- ❌ gitignore：`docs/.index-audit-report.md`（ad-hoc diagnostic, regenerable）
- **不 push**（per vault/repo convention）

## 給下次同類任務的 checklist

```
[ ] 1. 驗證 Pigo 的數字（不要照單全收）
[ ] 2. 備份並把備份 commit 進去
[ ] 3. 盤點磁碟 → JSON（排除政策先講清楚）
[ ] 4. 決策 A1/A2/A2-改2/A3/A4，給 Pigo 拍板
[ ] 5. 切片：每組 60-110 條，按目錄結構分組
[ ] 6. 派 subagent：嚴守 max_concurrent_children=3
[ ] 7. 避免 single-task dispatch（會丟 result 通知）
[ ] 8. merge script 必備 column-header tolerance
[ ] 9. 驗證：dangling/unlisted/duplicates 都要 0
[ ] 10. commit 含備份 + 工作目錄；ad-hoc diagnostic 進 .gitignore
[ ] 11. 不 push（per vault convention）
```

## 跟現有 Pattern 的關聯

- **Pattern EE**（Skill_Index 整體腐敗）：本次 1068 雙向落差確認為「嚴重」等級
- **Pattern N**（dangling 路徑可能過時）：本次用磁碟事實重建取代靜態清單
- **Pattern U**（ahead-only 不 push 慣性）：本次只 commit，沒 push，等 Pigo 拍板
- **Pattern GG**（dated backup 該 commit）：本次備份檔 `Skill_Index.md.bak-20260629-132619` commit 進去
- **Pattern AA**（script format vs actual 不一致）：本次新 index 換格式，舊的 `skill-index-check.py` regex 全部失效，下次跑會全錯。需重構。
- **新 Pattern II 觸發條件**：當 Pigo 訊息含「完整重建」/「單次修補無效」/「Pattern EE 等級」等關鍵詞，自動進入完整重建流程

## 重要副產物

### `docs/.index-rebuild/`
- `01-disk-inventory.json` — 605 條磁碟事實快照（最重要，未來審計用）
- `02-input-G*.json` — 8 組切片 input
- `03-rows-G*.md` — 8 組 subagent 產出的 row files
- `merge_index.py` — 可重跑的合併腳本

### `.gitignore` 變更
```diff
+# Ad-hoc index audit report (one-shot diagnostic, regenerable)
+docs/.index-audit-report.md
```

## 跟 Pigo 的互動觀察

1. **他給的數字常偏低**：134 → 實測 1068（低估 7.9×）。下次同類問題，先驗證再動作。
2. **他要的決策點是 2-4 個、有預設值**：給他 A2-改2 加說明，他會直接說「go」不再追問。
3. **他不喜歡被再問**：規劃時把 4 個 yes/no 問題預設填好，他回「go」就一次到位。
4. **他會自己說「this is the trigger」**：訊息明確標出 Pattern EE 等級，不需我們從零識別。
5. **他不喜歡我說「好，我修」這種空話**：要真的驗證數字、給出 plan、標風險，他才信任。
