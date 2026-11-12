# neat-freak session — 2026-11-12 04:00 UTC

## 摘要
每日 neat-freak 五 Phase 巡檢。**本次主要發現並修復一個 monitoring false-negative bug**（watchdog 對 Vault 有 500+ 筆未 commit 變更卻回報 "git status clean"）。Phase 1–5 其餘項目全綠。

## 核心修復：watchdog 的 pipefail + SIGPIPE false negative（Pattern EEEE）

### 症狀
`~/.hermes/scripts/neat-freak-hourly.sh` 對 Vault repo 回報：
```
--- Checking: repo status ---
  ✅ Vault git status clean
```
但實際 `git status --short` 有 **483 筆**變更（218 D + 26 M + 239 ??）。Agent repo 的 `✅ Agent git status clean` 則為真。

### 根因
```bash
set -uo pipefail
...
if git -C "$path" status --short | grep -q .; then
    echo "  ⚠️  $name 有未 commit 的變更"
else
    echo "  ✅ $name git status clean"
fi
```
`grep -q .` 找到第一個 match 就 exit(0)，上游 `git status` 尚未寫完就被關管 → 收到 **SIGPIPE (141)**。
`set -o pipefail` 的規則是「pipeline 的 exit code = 最右邊非零碼」；git 因 SIGPIPE 回 141（非零）→ pipeline 整體非零 → `if` 走 **else** → **有變更卻報 clean**。

關鍵在 `pipefail` 把 SIGPIPE 從「benign」翻轉成「failure」。Agent repo 之所以看起來正常，是因為它當下真的乾淨（0 筆變更 → grep 無 match → git 正常結束 → pipeline 0 → 走 then 分支 → 報 clean，恰好正確）。

### 實測證據（本次 session）
```bash
$ bash -c 'set -uo pipefail; git status --short | grep -q .; echo "pipeline_status=$?"'
pipeline_status=141          # ← 141 = SIGPIPE，被 pipefail 當成失敗

$ bash -c 'if git status --short | grep -q .; then echo NONEMPTY; else echo CLEAN; fi'
CLEAN                        # ← 不帶 pipefail 也是 CLEAN？

$ bash -c 'set -uo pipefail; out=$(git status --short); if [ -n "$out" ]; then echo NONEMPTY; fi'
NONEMPTY                     # ← 收進變數後正確
```
註：不帶 pipefail 時 `grep -q` 的 0 會蓋掉 git 的 141，行為取決於 grep 是否先退出；`set -o pipefail` 是**放大器**，但 bug 的根是 **用 pipe 做存在性判斷**。

### 修法
把輸出收進變數再判斷，完全避開 SIGPIPE：
```bash
CHANGES=$(git -C "$path" status --short)
CHANGE_COUNT=$(printf '%s\n' "$CHANGES" | grep -c . || true)
if [ "$CHANGE_COUNT" -gt 0 ]; then
    echo "  ⚠️  $name 有未 commit 的變更 ($CHANGE_COUNT 筆)"
else
    echo "  ✅ $name git status clean"
fi
```
另加 `WARNED` 計數，讓 Summary 區分「全綠」與「有警告但非致命」——原本有變更時 Summary 仍印「✅ 檢查通過」，警告被埋在輸出中間。

### 為什麼這是重要的 Pattern
1. **watchdog 的綠燈沒有價值**——它對 Vault 這個最大的 repo 從未真正檢查過。cron job `33f50df6ac6b` 連續回報 ok，但 Vault 的真實狀態從未被看見。
2. 這與 **Pattern CCCC**（假雙目標）同源：watchdog 看起來在檢查，實際上檢查邏輯是壞的。**「watchdog 回報綠燈」≠「被監控的對象正常」**。
3. 這與 **Pattern EEE**（dangling tree 可清）、**Pattern FFF**（安全斷言的量詞要實測）同屬「量測方法本身會說謊」的類別。

### 預防（可推廣）
1. **不要用 pipe 做存在性判斷**：`cmd | grep -q .` 在 `pipefail` 下不可靠。要嘛收進變數，要嘛 `cmd | grep -q . && true`（但這在 pipefail 下仍不可靠），要嘛用 `grep -c` 取數。
2. **watchdog 必須有負向測試**：故意製造一次「被監控對象的異常」，確認 watchdog 真的會紅。本次的做法是：先確認 Vault 實際有 483 筆變更，再看 watchdog 報什麼 → 發現報 clean → 修完再跑 → 報 520 筆。**沒有負向測試的 watchdog 等於沒有 watchdog**（與 Pattern DDDD 的「修完必做負向測試」同一原則）。
3. **新寫 shell script 時，`set -o pipefail` + `grep -q` 組合要逐一檢視**。本機 `~/.hermes/scripts/` 有 9 支 script 帶 `pipefail`，其中只有 `neat-freak-hourly.sh` 使用 `grep -q .` 判斷（已全庫確認唯一）。

### 延伸觀察
- 同時修正 Summary 語意：有警告時印「⚠️ 檢查通過但有 N 項警告」，避免 cron 交付文字讀起來像全綠。
- 修完後實測：Vault 正確回報「⚠️ Vault 有未 commit 的變更 (520 筆)」，Agent 維持「✅ clean」，Summary 為警告式。

## 本次其他觀察

### Vault 內 218 筆「刪除」實為搬移（非資料遺失）
`git status` 顯示 218 筆 ` D` 全在 `00-Inbox/`，逐檔比對後確認是 **Inbox → 08-Learning 分類目錄的搬移**：
- **211 檔**：body + frontmatter 完全相同（僅檔名位置改變）
- **7 檔**：body 相同，差異僅為 frontmatter 新增 `status: filed` / `filed-date` / `location` 與 self-wikilink 路徑改寫
- **零內容遺失**。這是 2026-11-12 vault-deep-clean run 的未提交成果（見 `12-Meta/vault-deep-clean-report-2026-11-12.md`）。

### Vault 仍有 534 筆未 commit 變更 → 不由本次 neat-freak 提交
Vault 在本次巡檢期間**持續被其他行程寫入**（`omp` worker 的 cwd 就是 vault，index.md / LLM-Wiki-Index.md 每分鐘都在改）。判定為**其他 session 的進行中成果**，依「不動其他 session 未 commit 成果」原則，本次不 stage、不 commit、不 push。

### cron job 狀態
22 個 job，**4 個 last_status=error**（延續 2026-11-11 的結論，本次無改善）：
- `fbb0a9e5147b` BensBites 每週精讀 — `RuntimeError: Connection error.`
- `ba23c28aec2c` 每週技能健康度檢查 — `RuntimeError: Connection error.`
- `ed7968b363f1` Kanban 每週日歸檔 — `RuntimeError: Connection error.`
- `0c0aca87f467` 每日精選晚報 — `interrupted`
前三者錯誤字串完全相同，疑似 provider 連線層問題而非各 job 邏輯問題（延續前次結論，本次無新證據）。

### 記憶同步 / skill 一致性 / retention / 備份
- Memory sync：P0-core / P1-90days / P2-30days 三份 `cmp` 逐 byte 相同 ✅
- Skill 一致性：canonical ↔ Agent workspace **與** canonical ↔ OpenClaw workspace 兩份 `sync-check.py` 皆 `RESULT: CLEAN` ✅
- `skill-index-check.py`：`OVERALL: ✓ ALL CLEAN`（761 rows / 582 categories / 32+193+536 全對齊）✅
- Cron output retention：移除 12 個 >7 天舊輸出，各 job ≤50 檔 ✅
- Hermes 備份：`20261112_041319 (2.0G)`，prune 最舊 `20261018_200625`，維持 14 份 ✅

### Agent repo 與 OpenClaw workspace 狀態
- Agent repo：`main` 與 `origin/main` **0/0 完全同步**（前次交接說的「落後 3 commits + 未 push 1 commit」已於昨日被解決，本地 commit `970b508537` 已不存在於歷史——改寫為 `663afbc132`）
- OpenClaw workspace：`master` **ahead of origin/master 3 commits**（`1c8e7b8` / `9ef69ad` / `400daf3`），未 push。另有 52 untracked + 8 M 的其他 session 成果未動。

### 917M dangling 保護 bundle 仍在
`.git/neat-freak-dangling-backup-2026-11-11.bundle`（960,750,291 bytes）+ **21 個** `refs/neat-freak/dangling-backup/2026-11-11/*` 仍在 vault repo 內。磁碟剩 30G / 86%。依約束未刪。
