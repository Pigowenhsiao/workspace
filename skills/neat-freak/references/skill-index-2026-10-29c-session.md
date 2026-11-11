# neat-freak 2026-10-29 第二十一 run session

## 摘要

本次 run 修掉兩份真實的 documentation drift，並補上 checker 的兩項 coverage gap。
期間發生一次**嚴重自傷**：編輯 canonical `SKILL.md` 時用了不處理 code fence 的
heading-based 區塊切片，刪掉 1455 行有效內容 → 已從 workspace copy 完整還原。

## 本次修掉的文件 drift

### 1. `docs/Skill_Index.md` — API key subtotal 不一致

- Summary 段落宣稱 `32 需要 / 193 可能需要 / 534 不需要`
- 表格 cell 實際統計 = `32 / 193 / 535`
- `32 + 193 + 534 = 759` ≠ Active Skills `760`
- 修復：`不需要` 534 → 535
- 追查：2026-10-24 新增 `diagnosing-superpowers` 使 Active Skills 759 → 760，
  但 no-key subtotal 未同步更新

### 2. `docs/Skill_Category.md` — 跨文件口徑矛盾無標明

- 14 類功能分類表合計 `581`，`Skill_Index.md` Active Skills 是 `760`
- 兩者口徑本就不同（功能分類 vs 目錄分類），**不是 drift 腐敗**
- 真正問題是兩份文件都沒標明口徑，讀者只會看到矛盾數字
- 修復：加 `Current Verification Notes`，明確 581 = dated snapshot（lower bound），
  live census = `Skill_Index.md` → `Category Map` 的 760
- header 改為 `Generated: 2026-05-20 · Counts refreshed: 2026-10-29`

## checker 加強（`scripts/skill-index-check.py`）

| check | 內容 |
|---|---|
| `[6]` | API key breakdown drift — Summary 的三個 subtotal vs 表格 cell 加總 |
| `[7]` | `Skill_Category.md` table self-consistency — 表內加總 vs 文件自稱的 claim |

Category claim parser 同時接受 `Sum of category counts:` 與 `Table row sum:` 兩種格式。

### 負向測試（確認新 check 真的會抓到）

```
NEGATIVE TEST api_key: [('不需要', 999, 535)]
NEGATIVE TEST category: table_sum 581 claim 777 rows 14
```

canonical 與 workspace checker 已 `cmp` 確認 byte-identical，workspace checker 輸出
`OVERALL: ✓ ALL CLEAN`。

## 自傷與還原（Pattern ZZZ）

**發生什麼**：整理 `SKILL.md` 重複 heading 時，用「找下一個 heading 當區塊結尾」的 helper。
該 helper 沒排除 code fence 內的 heading —— `SKILL.md` 的「同步完成」摘要範例放在
``` fence 內，其中的 `## 同步完成` / `### 記憶變更` / `### 文件變更` 都被當成真 heading，
區塊結尾比預期早數百行 → 刪掉 1455 行。

**還原路徑**：canonical 樹無 git → 從 workspace copy（git HEAD，2336 行）覆蓋回去，
`diff <(git show HEAD:skills/neat-freak/SKILL.md)` 確認 IDENTICAL。
備份 tarball `hermes_2026-10-29_034058.tar.gz`（2325 行）也在，作為次要 recovery source。

**修復後的 fence-aware helper**：

```python
def fence_prefix(lines, idx):
    st = False
    for i in range(idx):
        if lines[i].lstrip().startswith('```'):
            st = not st
    return st

def real_headings(lines):
    return [i for i, l in enumerate(lines)
            if l.startswith('#') and not fence_prefix(lines, i)]

def endof(lines, s):
    for j in range(s + 1, len(lines)):
        if lines[j].startswith('#') and not fence_prefix(lines, j):
            return j
    return len(lines)
```

**刪除前必備的 assert**（anchor 數量不符時立即失敗，不靜默刪錯區塊）：

```python
i_ab = [i for i in real_headings(lines) if lines[i].startswith('### Pattern AB')]
assert len(i_ab) == 2
```

**多集比對驗證**（只比 diff 行數增減會漏掉「刪 N 行同時新增 N 行」）：

```bash
grep -v '^#' old.md | grep -v '^$' | sort | uniq -c > a.txt
grep -v '^#' new.md | grep -v '^$' | sort | uniq -c > b.txt
diff a.txt b.txt
```

## 實際完成的 SKILL.md 結構修復

| 問題 | 修復 |
|---|---|
| `## Pattern KK` 重複 heading（相鄰兩個一模一樣） | 刪掉重複的那個 |
| `## Pattern MM` orphan heading（內容是 07-08 session reference） | 改名為 `## 附：2026-07-08 session 新增參考` |
| orphan stale paragraph（與 07-08 bullet 重複） | 刪除 |
| `### Pattern AB` 重複區塊（全文兩份） | 合併成一份，把 AB2 獨有的「附帶發現」併入 AB1 |
| `## Pattern W` 只有 heading 沒有 body | 補上完整 body（獨立計數原則的四步方法 + 預防） |
| EOF trailing orphan `## Pattern W` | 刪除 |
| 「同步完成」摘要範例被夾在 Pattern AB 之後 | 移回 `### 第三步：實際修改` 段落末尾 |

新增 Pattern：`XXX`（checker 只驗被驗的那幾項）、`YYY`（跨文件口徑矛盾無標明）、
`ZZZ`（heading-based 切片誤刪 code fence 內內容）。

## 其他 Phase 結果

- **Phase 1 Vault**：無 uncommitted change；`git fsck --full` 無輸出；
  `git count-objects -v` → count 0 / in-pack 128003 / packs 2 / garbage 0
- **Phase 2 Memory**：canonical 與 workspace 的 `P0-core.md` / `P1-90days.md` /
  `P2-30days.md` 三檔皆 byte-identical；handoff trees 各 45 entries，無差異
- **Phase 3 Skills**：canonical 850 / workspace 1578 個 `SKILL.md` frontmatter 全部可解析；
  index 760 rows ↔ disk 760 完全一致；92 個同名群組中 0 個符合 safe-to-delete 三條件
- **Phase 4 Cron output**：各目錄檔案數最大 50，低於 500 門檻，未清理
- **Phase 5 Backup**：最新 archive `gzip -t` 通過，含 `config.yaml` / `auth.json` /
  `memory/P0-core.md` / `cron/jobs.json` / `AGENTS.md` / `kanban.db`

## 未處理

- canonical 樹 92 個同名 skill 群組 —— 多為「兩邊都對」的並行版本
  （巢狀自我複本 `X/X`、category 化 richer 副本、上游 bundle vs 本地 fork），
  需人工裁決
- canonical ↔ workspace 29 檔真分歧（平台遷移 / 用途不同，非 drift）
