# neat-freak session — 2026-10-24f（cron `539040a91ad2`，第 12 run）

**Job:** Vault 整潔同步（neat-freak）· 5-Phase · cron `539040a91ad2`
**Result:** Vault 完全乾淨且與 origin 同步；memory 鏡像 0 差異；canonical ↔ Agent repo
`neat-freak` 雙軌 0 diff；`skill-index-check.py` ✓ ALL CLEAN（759）；
Agent repo **3 個 dangling tree 清乾淨**（`git fsck --full` 全無輸出）；
**Hermes Backup 的 `[WARN] 複製失敗` 根因修正**（tar 取代 cp -r）；
cron output 全 < 500 門檻（0 個需清理）。

## 各 Phase 結果

| Phase | 項目 | 結果 |
|---|---|---|
| 1 | Vault `git status` | working tree 乾淨，與 `origin/main` 一致 ✅ |
| 1 | Vault stash | `git stash list` 空 ✅ |
| 1 | Vault dangling objects | `git fsck --full` 完全無輸出；`count-objects -v` count=0 ✅ |
| 2 | memory 鏡像 | `diff -rq ~/.hermes/memory/ ~/Documents/Agent/memory/` → **零差異**（P0/P1/P2 + dreaming + handoffs 全 SAME）✅ |
| 2 | memory 更新 | P0-core.md 的 key 量詞改寫（見 Pattern IIII）✅ |
| 3 | `sync-check.py` | ✓ CLEAN（references / scripts 結構、__pycache__ 皆無 drift）✅ |
| 3 | 內容一致性 | canonical ↔ workspace `references/` + `scripts/` 逐檔 `diff` → **0 diff** ✅ |
| 3 | `skill-index-check.py` | ✓ ALL CLEAN（759 = header = 8 sections；0 dangling；0 purpose corruption）✅ |
| 3 | skills 全域交集 | canonical 1104 / repo 1607 個 SKILL.md；同 relpath 交集 57，內容差異 **0** ✅ |
| 3 | Agent repo dangling | **3 個 dangling tree** → `reflog expire --expire=now --all && git gc --prune=now` → fsck 全無輸出 ✅ |
| 3 | Agent repo 分歧 | 落後 1（upstream `6e74f17d` x-agent enrichment）→ `git merge origin/main` **無衝突** ✅ |
| 4 | cron output | 50 / 50 / 7 檔，全 < 500；cleanup script 移除 0 個 ✅ |
| 5 | Hermes Backup | 03:00 排程執行成功，但有 `[WARN] 複製失敗` → **根因已修正並驗證** ✅ |

## Pattern IIII（2026-10-24 第十二 run 初發現）：量詞要分「引入點」與「繼承點」——同一個 key 有兩個不同的數字

**觀察**：記憶 P0-core.md 寫「確認含 key 的 3 個 commit」。本次實測發現這句話**兩個數字都對，
但用途不同**，若不區分會導致錯誤的清理範圍估算。

**實測**：
- **3 個 commit「引入」key**（`git log -S<key>` = 差異比對）：`b861b654` / `9477a6ae` / `18eb1284`
- **88 個 commit 的 tree「含」key**（`git grep -E 'sk-(cp|CMM)-[A-Za-z0-9_-]{60,}' <commit> --`）

**差異機制**：key 一旦進入某個 commit 的 tree，**所有後續 descendant commit 的 tree 都會繼承它**，
直到某個 commit 把它 sanitize 掉。所以「引入點」數（3）≠「繼承點」數（88）。

**用途對應**：
| 數字 | 意義 | 用途 |
|---|---|---|
| 3 | 污染源頭 | rewrite 時需要重寫的**最小** commit 集合 |
| 88 | 會被 push 出去的**物件範圍** | 決定「push 是否會帶 key 上遠端」 |

**預防**：
1. 寫「N 個 commit 含 X」之前，先問是**引入**（`-S`）還是**包含**（tree 比對）
2. 用 `git grep -E <pattern> <commit> --` 時**必須把 commit 放在 `--` 之前**；
   寫成 `git grep -E <pat> -E <commit> --` 會讓第二個 `-E` 把 commit 吃掉，**靜默回傳 0 命中**
   （本次第一次掃描就栽在這裡，得出「沒有 key」的錯誤結論）
3. 驗證 key 是否 live：比對 `sk-` token 的 sha256 與 `~/.hermes/.env` 生效值
   （本次實測相同 = **live key**，不是已輪替的舊 key）

**量化更新**（已寫入 P0-core.md）：
- local-only commits：94 → **95**（本次 merge 增加 1）
- repo visibility：**PRIVATE**（`gh repo view`）→ 洩漏面僅限協作者，非公開暴露

## Pattern JJJ（2026-10-24 第十二 run 初發現）：backup script 的自我參照競態——`cp -r` 複製正在被寫入的目錄

**觀察**：Hermes Backup cron（`89c411611e6d`）2026-10-24 03:00 的輸出出現：
```
[WARN] 複製失敗: /home/x/.hermes/cron
[備份成功: hermes_2026-10-24_030034.tar.gz]
```
前 7 天（10-18 ～ 10-23）皆無此 WARN。

**根因**：backup script 把 `~/.hermes/cron` 整個納入備份範圍，但 **cron job 自己的執行紀錄
就寫在 `~/.hermes/cron/output/<job_id>/`**。執行 backup 的當下，
`~/.hermes/cron/output/89c411611e6d/2026-10-24_03-00-57.md` 正被寫入 → `cp -r` 讀到
「檔案大小在讀取期間改變」→ 回傳非 0 → 印出 WARN。
**這是 backup 複製自己輸出目錄造成的自我參照競態**，不是權限或磁碟問題
（事後 `cp -r` 手動重跑 rc=0、tarball 也有 138 個 cron entry 證明檔案本身沒問題）。

**實際影響（實測）**：03:00 的 tarball 缺 14 個 cron 檔案——
包含 4 個 `output/*` 檔（backup 自己當天的執行紀錄）、
2 個 `external-workers/*.stderr`、2 個 `admissions/*.json`。
其他 118 個檔案（config.yaml / auth.json / skills / memories / AGENTS.md / kanban.db）**完整無缺**。

**修復**：`~/.hermes/scripts/hermes-backup.sh` 的複製步驟從 `cp -r` 改為 `tar` pipe：
```bash
tar -cf - -C "$(dirname "$item")" --ignore-failed-read "$(basename "$item")" 2>/dev/null \
    | tar -xf - -C "$BACKUP_DIR" 2>/dev/null
if [ ${PIPESTATUS[0]} -ne 0 ]; then
```
- `--ignore-failed-read`：讀取中變動的檔案只發警告，不中止整個 archive
- `PIPESTATUS[0]` 取的是**左側 tar**（producer）的退出碼，不是管線最後一段的
  ——用 `$?` 會拿到 extract 的碼，判斷錯對象

**驗證**：手動重跑 → **無 WARN**；新 tarball `gzip -t` rc=0；
cron 檔案 **132/132 全數收錄，0 missing**（修正前 03:00 版缺 14 個）。

**預防**：
1. 任何「把某目錄整包備份」的 script，若該目錄會被執行中的 job 寫入 → 必然有自我參照競態
2. 複製目錄用 `tar` pipe 優於 `cp -r`：前者對檔案變動具容錯，後者整個指令失敗
3. 判斷管線成功要看 **producer**（`PIPESTATUS[0]`），不是最後一段

## Pattern KKK（2026-10-24 第十二 run 確認）：Agent repo 的 dangling tree 同樣可清乾淨（Pattern EEE 跨 repo 適用）

**觀察**：Agent repo `git fsck --full` 回報 **3 個 dangling tree**
（`396782399e...` / `9986fffcca...` / `b88e378ded...`），每個含 ~40,000 個 entry。

**處置**（與 Vault 相同手法）：
```bash
cd ~/Documents/Agent
git reflog expire --expire=now --all
git gc --prune=now      # 不需要 --aggressive
git fsck --full         # → 完全無輸出
git count-objects -v    # → count: 0, size: 0
```
**結果**：3 個 dangling tree 全清，`in-pack` 45,317 → 45,827（重新打包），
packs 2 → 1，fsck 全無輸出 ✅

**預防**：Pattern EEE 不只適用於 Vault，**任何 repo 都適用**。
Phase 1/3 報 dangling tree 時應直接實際清理並用 `git fsck --full` 驗證，
不要歸類為「無害殘留」留到下個 session。

## Pattern LLL（2026-10-24 第十二 run 初發現）：`hermes-backup-protocol.md` 描述的是一套從未運作的流程

**觀察**：`skills/neat-freak/references/hermes-backup-protocol.md` 描述的備份系統
與磁碟上的實際情況**完全不同**：

| 項目 | 文件寫的 | 實際 |
|------|---------|------|
| 目的地 | `~/Documents/Agent/backups/hermes/` | `~/Documents/Backup/hermes/`（**該目錄根本不存在**） |
| 產物 | `memory_<TS>/` 散檔 | `hermes_<TS>.tar.gz`（單一 tarball） |
| 排程 | `0 0 * * *`（midnight） | `0 3 * * *`（03:00） |
| 流程 | `git add backups/hermes/` + `git commit` + **`git push`** | 沒有任何 git 步驟 |
| Cron output | 「**不備份**」 | 整個 `~/.hermes/cron` 都備份（含 output/） |
| Skills | `cd ~/.hermes/skills && git status` | `~/.hermes/skills` **不是 git repo**（`fatal: not a git repository`） |

**為什麼舊檢查抓不到**：這份文件描述的是**另一套設計方案**，不是「過期版本」——
它從未被實作過。檔案裡每一條指令單獨看都合理（`cp -r`、`git commit`、`find`），
沒有相對時間詞、沒有過期路徑，所有既有 grep 檢查全部漏掉。
只有「逐條驗證文件宣稱的每個路徑/指令是否真的存在」才會發現。

**實測驗證**：
- `~/Documents/Agent/backups/` → `No such file or directory`
- `~/.hermes/skills` → `fatal: 不是一個 git 版本庫`
- 腳本實際 `ITEMS` 陣列 = 10 項（config.yaml / AGENTS.md / auth.json / credentials /
  skills / memories / plugins / cron / memory / kanban.db）
- cron 排程實測 = `0 3 * * *`

**修復**：全面重寫為「實測現況 + 陷阱」格式，並附上還原演練與磁碟容量章節。
舊版保留在 git history（`c94eb7dc`）。

**預防**：
1. **文件宣稱的每個路徑與指令都要實際跑一次**——「合理但未實作」是比「過期」更隱蔽的腐敗
2. 特別檢查文件裡的 `git push` 步驟：本次發現的這份文件會建議對含 live API key 的
   Agent repo 執行 push ——照著做就會洩漏憑證
3. `cd <dir> && git status` 這類「假設該目錄是 repo」的指令要先驗證 `.git` 存在

## 本次未處理（需 Pigo 明確授權）

**Agent repo 的 95 個 local-only commits 仍不可 `git push`**：
ancestor 物件含 live MiniMax API key（88 個 commit 的 tree 含該 key）。
清理需 force-push rewrite（破壞性）→ **必須 Pigo 明確口頭授權才執行**。
repo 為 PRIVATE，remote 9 個 refs 目前皆不含 live key —— 保持乾淨是最高優先級。

## 教訓

- **量詞要分層**（Pattern IIII）：引入點 vs 繼承點，差 30 倍。同一句「3 個 commit 含 key」
  可以對也可以錯，取決於問的是哪個問題。
- **`git grep` 的參數順序有坑**：commit 必須在 `--` 前，否則靜默回傳 0 命中。
- **自我參照是靜態程式的通病**：backup 複製 job 自己的輸出目錄 → 必然競態。
  改用 `tar` pipe 而非 `cp -r`。
- **Pattern EEE 跨 repo 通用**：dangling tree 該清就清，別拖。
