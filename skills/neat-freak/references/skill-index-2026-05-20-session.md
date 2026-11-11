# Skill_Index 口徑判讀手冊（2026-05-20 session）

## 核心發現

### Skill_Index.md 的兩套數字

Skill_Index.md 和 Skill_Category.md 各自有獨立的 count 系統，數字不同是**常態而非腐敗**：

| 文件 | 計算方式 | 典型數值 |
|------|---------|---------|
| `docs/Skill_Index.md` | 按 section 分組，每個 section 一個 header count + 一個 Summary count（全部 section 加總） | 577（真實 skill 行數）|
| `docs/Skill_Category.md` | 14 類功能分類，每類一個 count，sum=581 | 581（功能分類合計）|

**為什麼數字不同**：同一個 skill，同時屬於一個 Skill_Index section 和一個 category。Skill_Index 的 section 是基於磁碟目錄的「技能叢」（如 `agent-workflows/ `），category 是功能邏輯分類（如「Browser, Web, Search & Social Automation」）。一個 `gstack-*` skill 同時是 `agent-workflows` section 和一個 category，兩套系統各自獨立計數。

### 口徑驗證的獨立 Python 命令

當 skill-index-check.py 的 regex 有 bug（Pattern V），要用獨立的 Python 重新計數：

```python
python3 -c "
import re
content = open('/path/to/docs/Skill_Index.md').read()
rows = re.findall(r'\-\s+\*\*[^*]+\*\*\s+—', content)
print(f'Actual skill rows: {len(rows)}')
"
```

這個 regex 比 script 的 table-cell regex 更魯棒，適用於 Skill_Index.md 的 dash-format 行。

### 兩套口徑各自的正確性標準

- **Skill_Index.md 正確性**：section header 數 = 該 section 內 `-\s+\*\*...—` 行數；Summary header = 所有 section header 之和
- **Skill_Category.md 正確性**：category table 的 count 之和 = table footer 總數；每行 count 與實際 category 行數一致
- **兩者 cross-check**：不要求數字相同，要求各自內部一致

## 本次 session 發現的過期 backup 檔

`docs/Skill_Index.md.bak-2026-05-20`（709 行）→ 已刪除。

**清理原則**：任何 `*.bak-*` 或 `*~` 檔案出現在 workspace 的 untracked 狀態時，直接刪除無需保留。git 已有完整歷史，不需要本地 backup。

## Ahead-only 評估的快速口徑

本次 session ahead by 1（`d04b57ec regenerate Skill_Index.md`），性質為口徑修正，已即時 push。

Pattern U 的觸發時機：口徑修正 commit 做完後，**立即評估立即 push**，不要累積。

## 關於 Skill_Category.md 的 Generated 日期

Skill_Category.md 的 `Generated: YYYY-MM-DD` 是 regenerate 的時間戳，不是 commit 時間。每次磁碟 scan 重刷 Skill_Index.md 時，Skill_Category.md 也應同步更新日期（由 regenerate 流程負責，但 neat-freak pass 時發現日期落後應一併更新）。

## 驗證清單（2026-05-20 起生效）

- [ ] `skill-index-check.py` 報告的口徑是否用獨立 Python 驗證過（不走 script 自己的 regex）
- [ ] `Skill_Category.md` 的 `Generated:` 日期是否與 `Skill_Index.md` 的 `Generated:` 一致（最多差 1 天）
- [ ] workspace 有無 `*.bak-*` 或 `*~` 檔案 → 刪除
- [ ] ahead commits 是否為口徑修正 → 立即 push