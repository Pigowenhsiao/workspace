# neat-freak session — 2026-10-29 (第十九 run)

## 摘要

本次跑 5 Phase，全綠。

- **Phase 1（Vault Git Health）**：60 檔 uncommitted 修改 → 驗證為**上游 YAML quote-fixer 的成果**（HEAD 全部 60 檔 YAML invalid → worktree 全部 valid，0 regression）→ commit + push 成功（`8786fdc10..a7ab6477c`）。`git fsck --full` 無輸出，無 dangling。
- **Phase 2（Memory Sync）**：P0-core.md / P1-90days.md / P2-30days.md 三檔 byte-identical，無需同步。
- **Phase 3（Skills Consistency）**：`sync-check.py` CLEAN、`skill-index-check.py` ✓ ALL CLEAN（760 = header = 8 sections）、purpose cell 語意比對 0 mismatch、兩棵樹 frontmatter 0 invalid、內容 diff 0 檔。刪除 1 個 canonical 內嵌重複 skill。
- **Phase 4（Cron Output Retention）**：各 job output 目錄最多 50 檔，遠低於 500 門檻，不需清理。
- **Phase 5（Hermes Backup）**：手動執行 `hermes-backup.sh` 成功（`hermes_2026-10-29_012631.tar.gz`），並驗證 tarball 涵蓋 config.yaml / auth.json / kanban.db / cron/jobs.json / memory/P0-core.md / skills/neat-freak/SKILL.md。

---

## 新 Pattern：UUU — 「工作樹修改」要先分類為「修復」還是「污染」再 commit

### 觀察

Vault working tree 有 60 檔 uncommitted 修改。若照 Phase 1 指示直接 `git add -A` + commit，
就是**未經驗證就接受上游的批次改寫**——這正是 Pattern RR（批次改寫掉 frontmatter key 首字元）
的入口。

### 本次的正確做法

commit 前先用獨立 Python 做**修復前後對照量測**（Pattern RR 的預防手段）：

```python
def parse(text):
    lines = text.split('\n')
    if not lines or lines[0].strip() != '---': return None, 'NOFENCE'
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            try: return yaml.safe_load('\n'.join(lines[1:i])), None
            except Exception as e: return None, str(e)[:90]
    return None, 'NOCLOSE'

# 對每個 changed file：解析 worktree 版本 + `git show HEAD:<file>` 版本
# → 分成 FIXED（HEAD invalid → worktree valid）/ REGRESSED / UNCHANGED
```

實測結果：**head invalid = 60、worktree invalid = 0、regressions = 0** → 判定為
「上游 quote-fixer 的修復成果」，可安全 commit。

### 教訓

Phase 1 的「若有 uncommitted 則 add + commit + push」必須加一道**前置量測**：
批次改寫的檔案數量越大，越要先確認它是修復還是破壞。
量測成本（數秒）遠低於事後回滾成本（canonical 樹無 git 時不可逆）。

### 附帶觀察：本次 quote-fixer 的修正型態

| 症狀 | 修正 |
|------|------|
| `title: [安裝教程]...`（裸 `[` 開頭被當 flow sequence） | 加引號 |
| `handle: @xiaoxiaodong01` | 加引號 |
| `title: "..." — @Pluvio9yte`（裸文字 + 全形破折號） | 加引號 + `#` 註解化尾端 |
| `location: "path/"---`（closing fence 被吞進 value） | escape 引號 + fence 復原 |
| `processed_by: "llm-wiki"status: filed`（兩 key 併行） | escape 內層引號 |
| `C:\Users\...` 內反斜線 | escape 為 `\\` |

---

## 新 Pattern：VVV — canonical 樹的同名重複：**「只有 1 個可安全刪」是常態，不是例外**

### 觀察

canonical 樹（`~/.hermes/skills/`，排除 `.archive/` 與巢狀 `.hermes/skills/`）有
**803 個 name、93 個 name 對應多個目錄**。

套用 Pattern SSS 的三條件安全刪除檢查（每個檔案都必須存在於 winner 且 sha256 相同）後：

- **SAFE-to-delete：只有 1 個**（`yao-tutorial-skill/yao-tutorial-skill`，3 檔全 byte-identical）
- **UNSAFE：138 個**（loser 有 unique 檔案、或 SKILL.md 內容分歧）

### 為什麼 138 個「不安全」多半其實是**內容不同但都對**的並行版本

逐一檢查後發現三種型態：

1. **巢狀自我複本**（`weather/weather`、`mail-triage/mail-triage`、`inbox-check/inbox-check`）
   — 只有 `SKILL.md` 不同，其餘檔案完全一致
   - `weather/weather`：多了 `triggers:` 欄位 → 較新
   - `mail-triage/mail-triage`：是 **2026-04-29 dedupe 後的 canonical 英文版**，
     內含 `<!-- AGENT_SKILL_DEDUPE_NOTE -->`；而外層 `mail-triage/` 是**後來重寫的中文詳細版**
     （含 himalaya 實戰筆記、LLM-Wiki 格式規範、vault 路徑已遷 `~/Documents/Pigo_Obsidian`）
     → **兩邊都是對的**，刪任一邊都會丟失資訊

2. **category 化副本**（`productivity/pdf` 有 21 個 unique 檔、`productivity/docx` 12 個、
   `productivity/xlsx` 11 個）→ 內含 references/examples，**是 richer 版本**，不能刪

3. **上游 bundle vs 本地 fork**（`openclaw-imports/*` vs top-level）→ 兩套並行生態

### 結論

93 個同名群組裡**只有 1 個**符合「刪了不會丟任何東西」。這與 Pattern SSS 2026-10-28 的結論
（78 個 byte-identical 已刪、6 個 union 合併、88 個留待裁決）一致：
**canonical 樹的同名重複大部分是「多版本並存」，不是「污染」，機械式清理的邊際收益極低。**

### 本次實際動 作

只刪 `~/.hermes/skills/yao-tutorial-skill/yao-tutorial-skill/`（3 檔 byte-identical、
無 unique 檔、備份 tarball 已涵蓋）。刪後 `skill_view(name='yao-tutorial-skill')` 由
ambiguous 轉為 `success: true` ✅

### 預防

1. 跑「canonical 樹重複 name 掃描」時，**預期「可安全刪除數」會很小**。
   若算出 90+ 可刪，先懷疑比對邏輯錯了（應比對**全部檔案**而非只有 SKILL.md）
2. canonical 樹無 git → 刪前必須備份覆蓋（本次 `hermes_2026-10-29_012631.tar.gz` 已涵蓋）
3. 刪除收益應以「`skill_view` 由 ambiguous 轉 success」衡量，而非刪除數量

---

## 檢查工具的補充

### `skill-index-check.py` 的「✓ ALL CLEAN」仍只代表結構一致

本次另跑 purpose cell ↔ frontmatter 語意比對（Pattern RRR 補測腳本）：**0 mismatch**。
但這是**獨立跑的**，checker 本身不涵蓋此項。

### canonical 與 workspace 兩棵樹本次 `diff -rq` 內容分歧 = 0 檔

與 2026-10-28（31 檔分歧、2 檔可同步）相比，兩樹已收斂。neat-freak 自身的
`references/` + `scripts/` + `SKILL.md` 逐檔 `cmp` 亦全部 identical。

---

## 未處理（需人工裁決）

- **canonical 樹 92 個剩餘同名 skill 群組**：內容不同但多數「兩邊都對」，
  刪任一邊都會丟失資訊。需逐一人工判斷要留哪個版本。已列於本次報告。
- **Vault `vendor/` 與 `skill-backups/` 共 21 檔 mojibake（badness 122–2684）**：
  外部 bundle 與歷史備份，不在維護範圍。
