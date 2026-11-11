# neat-freak Session — 2026-10-29 (第二十二 run)

## 摘要

五 Phase 全綠。Vault 914 檔 tag 去重已 commit + push；Agent repo 三個 commit 已 push；
記憶兩棵樹 byte-identical；cron output 無超量；backup 今日 03:00 已跑且四個 `.env` 齊備。

**本次唯一新增的腐敗類型**：Pattern XXXX（見下）——repo-root 副本第三次落後，且
`sync-check.py` 結構性無法偵測 → 已修 checker 補上內容一致性 + repo-root 副本兩項檢查。

---

## Pattern XXXX（2026-10-29 第二十二 run 初發現）：checker 的覆蓋範圍是它「以為」的範圍——repo-root 副本第三次落後

### 觀察

`~/Documents/Agent/neat-freak/SKILL.md`（repo 根的第三份副本）再次落後 canonical：

| 位置 | 行數 |
|------|------|
| `~/.hermes/skills/neat-freak/SKILL.md`（canonical） | 2,435 |
| `~/Documents/Agent/skills/neat-freak/SKILL.md`（workspace copy） | 2,435 ✓ 一致 |
| `~/Documents/Agent/neat-freak/SKILL.md`（**repo 根副本**） | 2,336 ✗ 落後 99 行 |

### 為什麼第三次才抓到

`sync-check.py` 的比對基準是 `canonical_dir()` vs `workspace_dir()`，後者預設為
`~/Documents/Agent/skills/neat-freak`。**repo 根副本在 `skills/` 之外**，不在比對路徑內。

三份副本：

```
canonical    ~/.hermes/skills/neat-freak/SKILL.md        ← 真正的來源
copy A       ~/Documents/Agent/skills/neat-freak/SKILL.md ← sync-check.py 只比這份
copy B       ~/Documents/Agent/neat-freak/SKILL.md        ← 沒有任何檢查看它
```

Pattern TTT（2026-10-29b session）已記錄「repo 根副本第二次落後」，
但那次的處置是**手動同步**（`cp`），沒有修 checker → 同一個坑第三次踩。

### 更深一層：`sync-check.py` 從不比較內容

即使 copy A 的 `SKILL.md` 內容過期（而非僅檔案存在），舊版 checker 也會回報
`RESULT: CLEAN` ——因為它只比對**檔案存在性**（Pattern H item 9、Pattern AAA 早已指出，
但歷次都只寫在 SKILL.md 正文裡，沒有人把它實作進 checker）。

### 修復

canonical `scripts/sync-check.py` 新增兩項檢查：

1. **Content consistency** — 對 canonical 樹下每個檔案做 `read_bytes()` 比對
   （僅對 workspace 也存在的檔案；workspace 缺檔由既有的 MISSING 檢查涵蓋）
2. **Repo-root copy** — 比對 `<WORKSPACE_ROOT>/neat-freak/SKILL.md` 與 canonical，
   過期時顯示兩者行數

新增 `WORKSPACE_ROOT` 環境變數（預設 `~/Documents/Agent`）以支援其他 workspace。

### 驗證（負向測試必做，Pattern QQ）

| 測試 | 期望 | 實測 |
|------|------|------|
| 乾淨狀態 | `RESULT: CLEAN`, exit 0 | ✓ exit 0 |
| canonical 改動但未同步 workspace | CONTENT DIFFERS, exit 1 | ✓ 抓到 `scripts/sync-check.py` |
| repo-root 副本注入 2 行 | STALE + exit 1 | ✓ `STALE — canonical 2435 lines vs repo-root copy 2437 lines` |
| 還原後 | exit 0 | ✓ |

### 預防

1. **checker 的覆蓋範圍要靠「故意破壞」來證明**——negative test 是唯一能證明
   檢查有效的手段（Pattern QQ）
2. **同一份內容存在多份副本時，先列出所有副本位置**，逐一納入比對基準
3. 發現「同一問題第 N 次出現」時，**不要只做第 N 次手動修復**——
   修根因（本次是 checker 覆蓋範圍），否則會有第 N+1 次
4. `sync-check.py` 的比對基準是兩個 `*_dir()` 函式的回傳值；
   任何新增的 skill 副本位置都要同步擴充基準

---

## Phase 執行紀錄

### Phase 1 — Vault Git Health

- 工作樹 914 檔 modified（`152 insertions / 3079 deletions`）
- **量測（Pattern UUU）**：HEAD invalid 0 / worktree invalid 0 / FIXED 0 / REGRESSED 0
- 刪除內容分類：2,705 行為 tag-like 重複項、137 行為空行、16 行為
  inline `tags: [...]` → block style 轉換 → **判定為上游 quote/tag-fixer 的修復成果**
- `git add -A` + commit `ee24e8a60`，`git pull --no-rebase`（落後 2 commits，**檔案零重疊**）
  → clean merge → `git push` → `317a544fd`
- `git fsck --full` 無輸出；`git count-objects -v` → count 0, garbage 0

### Phase 2 — Memory Sync

`~/.hermes/memory/` 與 `~/Documents/Agent/memory/`：
P0-core.md / P1-90days.md / P2-30days.md **byte-identical**（`cmp` 三檔全等），
`handoffs/` 零差異 → **無需同步**。

### Phase 3 — Skills Consistency

- `sync-check.py` → `RESULT: CLEAN`（修補前為 DRIFT 誤判：見 Pattern XXXX 負向測試）
- `skill-index-check.py` → `✓ ALL CLEAN`（760 = header = 8 sections，check [6]/[7] 皆 ✓）
- frontmatter 掃描：canonical 850 檔 / workspace 1,578 檔 → **invalid 0 / 0**
- mojibake 掃描（ftfy `badness > 50` 且 `fix_encoding()` 實際有改動）：**0 命中**
- canonical 同名群組 90 組（`weather` = 3 份）→ 與上季一致，屬 Pattern VVV 的
  「兩邊都對的並行版本」，不機械式刪除
- canonical ↔ workspace 29 個同路徑內容分歧 → 與上季 Pattern TTT 清單**完全相同**
  （Readme.md 用途差異 + x-note 平台遷移），**非 drift，不動**

### Phase 4 — Cron Output Retention

25 個 job 目錄，最大 50 檔（門檻 500）→ **無需清理**。總量 7.1 MB。

### Phase 5 — Hermes Backup

排程 `0 3 * * *`（job `89c411611e6d`），今日 03:00 已跑：
`hermes_2026-10-29_034058.tar.gz`（486 MB，24,855 條目）。
`tar -tzf` 驗證四個憑證檔並存：`./.env`、`./profiles/analysis/.env`、
`./profiles/strata/.env`、`./Documents/.env`；`config.yaml` / `auth.json` /
`cron/jobs.json` / `skills` / `memories` / `AGENTS.md` 皆在。

---

## 未處理

- canonical 樹 90 組同名 skill — Pattern VVV：絕大多數是「兩邊都對」的並行版本
  （巢狀自我複本 `weather/weather`、category 化 richer 副本、上游 bundle vs 本地 fork），
  套用三條件安全刪除後可刪數極小。需人工裁決。
- canonical ↔ workspace 29 檔真分歧 — 平台遷移 / 用途不同，雙向都有獨有內容，
  自動同步會破壞語意。
