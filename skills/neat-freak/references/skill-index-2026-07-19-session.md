# Skill-Index / Vault Ingest Session — 2026-07-19

## 執行摘要

**目標**：cron job 驅動的 vault frontmatter 乾淨度檢查——用 `verify-vault-ingest.py` 的 FAIL count 判斷是否需要執行 neat-freak。

**結果**：FAIL 3283，systemic plateau，status note 已寫入 `00-Inbox/neat-freak-status-20260719.md`。

## 發現的兩個新問題

### 1. Cron pre-check 邏輯根本性缺陷

**症狀**：`verify-vault-ingest.py` exit code 永遠是 0，即使 FAIL 3283。cron job 用 `echo "---EXIT=$?---"` 抓 exit code，永遠得到 0。

**根因**：`verify-vault-ingest.py` 的 summary line（`FAIL: 3283`）是最後一行，exit code 0 表示「成功執行完畢」，不是「0 failures」。兩者之間沒有因果關係。

**原始 pre-check 邏輯（壞掉了）**：
```bash
python3 12-Meta/scripts/verify-vault-ingest.py 2>&1 | tail -5
echo "---EXIT=$?---"
# 永遠得到 EXIT=0，即使 FAIL 3283
```

**第二層缺陷**：`grep -c "^\[FAIL\]"` 永遠返回 0，因為 FAIL lines 是 `  [FAIL]`（2-space indent），不是 `  [FAIL]` at line start。正確 pattern 是 `grep -c "  \[FAIL\]"`。

**正確的 pre-check 做法**（適用於 cron 環境）：
```python
import subprocess
result = subprocess.run(
    ['python3', '12-Meta/scripts/verify-vault-ingest.py'],
    capture_output=True, text=True,
    cwd='/Users/pigo/Documents/Pigo_Obsidian'
)
# Count unique failing files (2-space indent, not line-start)
fail_count = result.stdout.count('  [FAIL]')
summary_line = [l for l in result.stdout.split('\n') if 'FAIL:' in l][0]
print(summary_line)
print(f'Total FAIL entries: {fail_count}')
```

**Pattern QQ 只覆蓋了「為什麼 summary 行存在」，沒說清楚 cron pre-check 怎麼正確實作**——需要補充。

### 2. Subdirectory STATUS_ALL.md frontmatter exemption gap

**症狀**：9 個 subdirectory `STATUS_ALL.md`（如 `01.1-TEST STUDY/STATUS_ALL.md`）FAIL "no frontmatter block"。

**根因**：`verify-vault-ingest.py` 的 exemption 只覆蓋 vault root 的 `STATUS_ALL.md`（判斷 `len(parts) == idx+2`），沒有覆蓋 subdirectory 的。

**為什麼不是 vault root 問題**：vault root `STATUS_ALL.md` 的 parts 是 `('Users', 'pigo', 'Documents', 'Pigo_Obsidian', 'STATUS_ALL.md')`，長度 5，qualifies for exemption。但 `01.1-TEST STUDY/STATUS_ALL.md` 的 parts 包含 `01.1-TEST STUDY`，不qualify。

**Pattern PP 的 exemption 判斷邏輯**（2026-07-13 已applied）：
```python
no_fm_allowed = {"index.md", "log.md", "AGENTS.md", "CLAUDE.md", "README.md", "NOTE.md"}
# 缺少 "STATUS_ALL.md" — 但問題不是 root-level，是 subdirectory
```

**修復方向**：在 exemption check 裡對 `STATUS_ALL.md` 和 `log.md` 也加上 subdirectory-level exemption（只要 basename 匹配就 exempt，不管深度）。

## FAIL 組成（2026-07-19）

| 類型 | Count |
|------|-------|
| missing classification_path | 2533 |
| missing source_url | 1874 |
| missing status | 1282 |
| missing title | 1060 |
| no frontmatter block | 291 |
| **Unique failing files** | **3283** |

291 個 "no frontmatter block" 包括：
- 158 個 `README.md` 檔案（各目錄下）
- 9 個 subdirectory `STATUS_ALL.md`
- 剩餘為 `log.md` 和其他 config 檔

## 口徑追蹤

| Date | FAIL | Notes |
|------|------|-------|
| 2026-07-13 | 3378 | systemic gap |
| 2026-07-10 | 3524 | policy gap identified |
| 2026-07-19 | 3283 | plateau confirmed (-95 from 07-13, likely subdirectory STATUS_ALL added) |

3283 vs 3378 = -95，可能是陸續有 intake workflow 淨化了一些檔案，但不是 systematic fix。

## 建議的 next action

1. **修補 verify-vault-ingest.py**：`STATUS_ALL.md` 和 `log.md` basename-level exemption（不論深度）
2. **修補 cron pre-check**：用 Python count FAIL entries，不靠 exit code 和簡單 grep
3. **系統性 intake frontmatter**：對 ~2785 個 "other" 內容檔案做 batch frontmatter addition
