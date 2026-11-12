# Neat-freak 每日同步交接 — 2026-11-12（04:00 UTC run）

## Goal
執行 neat-freak skill 五個 Phase 的每日 vault 整理與同步檢查：Vault git 健康、記憶副本同步、neat-freak skill 一致性、cron output retention、Hermes 備份。遵守「不刪 vault 資料、commit 後需檢查再 push」的約束。

> **本輪主要成果**：發現並修復一個 **watchdog false-negative bug**（`neat-freak-hourly.sh` 對 Vault 有 500+ 筆未 commit 變更卻回報 "git status clean"）。此 bug 讓 cron job `33f50df6ac6b` 連續回報 ok，但 Vault 真實狀態**從未被真正檢查過**。

## Current State

### Phase 1 — Vault Git ⚠️（Vault 正在被其他行程寫入中）
- `~/Documents/Pigo_Obsidian` working tree **534 筆變更**（264 D + 31 M + 239 ??），`main...origin/main` 無落後，HEAD = `9a9dc8676 chore: auto-sync 2026-11-12 03:08`。
- `git fsck --full --no-progress` → **exit 0**，僅 1 個 `dangling tree 9a92e3cd`（無 dangling commit，無資料遺失風險）。
- `git count-objects -v` → count: 366 / garbage: 0 / in-pack: 126244 / packs: 1 / size-pack: 987620 KB。
- **218 筆 ` D` 經逐檔比對確認為「搬移」而非刪除**（`00-Inbox/` → `08-Learning/` 分類目錄）：
  - **211 檔**：body + frontmatter 完全相同（僅位置改變）
  - **7 檔**：body 相同，差異僅 frontmatter 新增 `status: filed` / `filed-date: 2026-11-12` / `location:` 與 self-wikilink 路徑改寫
  - **零內容遺失**。這是 2026-11-12 vault-deep-clean run 的未提交成果（`12-Meta/vault-deep-clean-report-2026-11-12.md`）。
- **Vault 在巡檢期間持續被寫入**：`omp` worker (PID 120697) 的 cwd 就是 vault，`index.md` / `LLM-Wiki-Index.md` / `11-MOC/AI-Agent-MOC.md` 每分鐘都在改。00-Inbox 檔數在觀察窗內從 345 → 337 變動。
- → **本次不 stage / 不 commit / 不 push Vault**，屬其他 session 進行中成果。

### Phase 2 — Memory Sync ✅
- `cmp -s ~/.hermes/memory/<f> ~/Documents/Agent/memory/<f>` ×3 → **P0-core.md / P1-90days.md / P2-30days.md 全部 SYNC-OK**（逐 byte 相同）。

### Phase 3 — Skills Consistency ✅ + **本輪主要修復**
- **核心 bug**：`~/.hermes/scripts/neat-freak-hourly.sh` 的 Vault 檢查是**假的**。
  - 舊寫法：`if git -C "$path" status --short | grep -q .; then` 在 `set -o pipefail` 下，`grep -q` 命中即 exit → `git status` 收到 **SIGPIPE (141)** → pipefail 取最右非零碼 → pipeline 非零 → `if` 走 else → **有變更卻報 clean**。
  - 實測：Vault 實際 483 筆變更，watchdog 卻印「✅ Vault git status clean」。Agent repo 當下真的乾淨所以看起來正常。
  - **修法**：輸出收進變數再判斷（`CHANGES=$(git -C "$path" status --short)` + `grep -c .`），完全避開 SIGPIPE。
  - **額外修**：Summary 區分「全綠」與「有警告」——原本有未 commit 變更時仍印「✅ 檢查通過」，cron 交付文字讀起來像一切正常。
  - **驗證**：修完 → Vault 正確回報「⚠️ Vault 有未 commit 的變更 (520 筆)」，Agent 維持「✅ clean」，Summary 為警告式。
- **Pattern EEEE 已寫入 canonical SKILL.md**（2551 → 2591 行）+ 新建 `references/skill-index-2026-11-12-session.md`。
- **五份 SKILL.md md5 全部一致** = `59f8b84c2cdbbb75df2fc8678acb90c9`（canonical / Agent workspace / Agent repo-root / OpenClaw workspace / OpenClaw repo-root）。
- `sync-check.py` → canonical↔Agent **CLEAN**；canonical↔OpenClaw（帶 `WORKSPACE_DIR=` / `WORKSPACE_ROOT=`）**CLEAN**。
- `skill-index-check.py` → **OVERALL: ✓ ALL CLEAN**（761 rows / 582 categories / 32+193+536 全對齊）。
- `verify-skill-frontmatter.sh neat-freak .` → `[OK] frontmatter verified: name=neat-freak`。

### Phase 4 — Cron Output Retention ✅
- `cron-output-cleanup.py` → 移除 **12 個** >7 天舊輸出檔（`82f856963e0a` 2 檔、`33f50df6ac6b` 2 檔、其餘 8 個 job 各 1 檔），各 job 維持 ≤50 檔；`~/.hermes/cron` 總量 **13M**。

### Phase 5 — Hermes Backup ✅
- `bash ~/.hermes/scripts/hermes-backup.sh` → **`==> Done: /home/pigo/.hermes/workspace-backups/20261112_041319 (2.0G)`**
- prune 最舊 `20261018_200625`，備份維持 **14 份**（MAX_KEEP=14）。磁碟剩 30G / 86%。

### Commits
- **Agent repo（本輪已 commit，未 push）**：`b17d7e3a19` — 3 files, +182/-0
  - `skills/neat-freak/SKILL.md`（+40，Pattern EEEE 條目）
  - `neat-freak/SKILL.md`（repo-root 副本，+40）
  - `skills/neat-freak/references/skill-index-2026-11-12-session.md`（新建，102 行）
  - **驗證**：staged + committed diff 的 secret scan（`sk-` / `ghp_` / `AKIA` / `xox`）→ **零命中**。
- **OpenClaw workspace（本輪已 stage，未 commit）**：`neat-freak/SKILL.md`、`skills/neat-freak/SKILL.md`、`skills/neat-freak/references/skill-index-2026-11-12-session.md`、`skills/neat-freak/SKILL.md.bak-20261110`（後者補進來是因為 canonical 有、OpenClaw 副本先前缺；Agent repo 是 tracked 的）。
- **未 push**（依約束：commit 後需檢查再 push）。

### ✅ 推翻前次交接的結論
- 前次說「Agent repo `main` 落後 origin/main 3 commits + 本地 1 個未 push commit `970b508537`」→ **已不成立**。現況 `git rev-list --left-right --count origin/main...HEAD` = **0 / 0**，本地 commit 已改寫為 `663afbc132`。
- 前次說「OpenClaw workspace ahead 2 commits」→ 現為 **ahead 3**（多了 `400daf3`）。

### ❌ 未完成
- **未 push**（Agent repo `b17d7e3a19`；OpenClaw workspace 3 個既有 commit + 本輪 staged）。
- **4 個 cron job 仍為 error**（非本次可解，見 Decision Needed）。
- **Vault 534 筆變更未 commit**（其他 session 進行中成果）。
- **OpenClaw workspace 其餘 52 untracked + 8 M 未動**（DREAMS.md / dreaming journals / codex-helper / finance parser / research-heartbeat / model-catalog-prune / skills-anatomy symlink 等，屬其他 session 成果）。
- **未刪** 917M bundle + 21 個保護 refs。

## Source Chain

| # | 指令 / 腳本 | 輸出摘要 |
|---|---|---|
| 1 | `git -C ~/Documents/Pigo_Obsidian fsck --full --no-progress` | exit 0、僅 1 個 `dangling tree 9a92e3cd` |
| 2 | `git -C ~/Documents/Pigo_Obsidian count-objects -v` | count: 366 / garbage: 0 / in-pack: 126244 / packs: 1 |
| 3 | `git -C ~/Documents/Pigo_Obsidian status --porcelain` | **534 筆**（264 D / 31 M / 239 ??） |
| 4 | Python 稽核腳本（`git hash-object` + frontmatter 正規化比對）×218 | **211 全等 + 7 僅 frontmatter/link 差異 + 0 內容遺失** |
| 5 | `cmp -s ~/.hermes/memory/<f> ~/Documents/Agent/memory/<f>` ×3 | P0 / P1 / P2 皆 SYNC-OK |
| 6 | `python3 ~/.hermes/skills/neat-freak/scripts/sync-check.py` | `RESULT: CLEAN`（Agent workspace） |
| 7 | `WORKSPACE_DIR=~/.openclaw/workspace/skills/neat-freak WORKSPACE_ROOT=~/.openclaw/workspace python3 .../sync-check.py` | `RESULT: CLEAN`（OpenClaw workspace） |
| 8 | `python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py` | `OVERALL: ✓ ALL CLEAN`（761 / 582 / 32+193+536） |
| 9 | `bash ~/.hermes/scripts/neat-freak-hourly.sh`（修前） | **`✅ Vault git status clean`（假）— 實際 483 筆變更** |
| 10 | `bash -c 'set -uo pipefail; git status --short \| grep -q .; echo $?'` | **141（SIGPIPE）** — 根因實證 |
| 11 | `bash -c 'set -uo pipefail; out=$(git status --short); ...'` | `NONEMPTY` — 修法驗證 |
| 12 | `bash ~/.hermes/scripts/neat-freak-hourly.sh`（修後） | `⚠️ Vault 有未 commit 的變更 (520 筆)` + `⚠️ 檢查通過但有 1 項警告` |
| 13 | `bash ~/.hermes/skills/neat-freak/scripts/verify-skill-frontmatter.sh neat-freak .` | `[OK] frontmatter verified: name=neat-freak` |
| 14 | `md5sum` ×5 份 SKILL.md | 全部 `59f8b84c2cdbbb75df2fc8678acb90c9` |
| 15 | `python3 ~/.hermes/skills/neat-freak/scripts/cron-output-cleanup.py` | `Total files removed: 12` |
| 16 | `bash ~/.hermes/scripts/hermes-backup.sh` | `==> Done: .../20261112_041319 (2.0G)` + `[prune] removing .../20261018_200625` |
| 17 | `git -C ~/Documents/Agent rev-list --left-right --count origin/main...HEAD` | `0  0`（**推翻前次「落後 3 commits」**） |
| 18 | `git -C ~/.openclaw/workspace rev-list --left-right --count origin/master...HEAD` | `0  3`（ahead 3） |
| 19 | `ps -p 120697 -o args=` + `ls -l /proc/120697/cwd` | `omp` worker，**cwd = vault**（確認寫入者） |
| 20 | secret scan（`sk-`/`ghp_`/`AKIA`/`xox`）on staged + committed diff | **零命中** |

## Decision Needed

1. **是否 push Agent repo 的 `b17d7e3a19` 與 OpenClaw workspace 的 3 個 commit**。Agent repo 目前 0/0 同步，落後 0，落後遠端 0 → push 風險極低。OpenClaw workspace ahead 3 + 本輪 staged 1 → 需先檢視 diff。
2. **917M dangling 保護 bundle 是否刪除**：`.git/neat-freak-dangling-backup-2026-11-11.bundle`（960,750,291 bytes）+ **21 個** `refs/neat-freak/dangling-backup/2026-11-11/*` 仍在 vault repo。磁碟剩 30G / 86%。本次 `fsck` 已確認只剩 1 個 dangling tree、**無 dangling commit**，保護機制的價值已隨時間遞減。
3. **4 個 error 狀態 cron job 是否排查**：
   - `fbb0a9e5147b` BensBites + Readwise 每週精讀 → `RuntimeError: Connection error.`（last 11-08 02:05，next 11-15）
   - `ba23c28aec2c` 每週技能健康度檢查 → `RuntimeError: Connection error.`（last 11-08 17:05，next 11-15）
   - `ed7968b363f1` Kanban 每週日歸檔 → `RuntimeError: Connection error.`（last 11-08 16:05，next 11-15）
   - `0c0aca87f467` 每日精選晚報 → `interrupted`（last 11-11 12:08，輸出 0 bytes；next 11-12 12:00）
   - 三個週 job 錯誤字串**完全相同**，高度疑似 **provider 連線層**問題而非各 job 邏輯問題，建議合併為一件事查。
4. **Vault 534 筆未 commit 變更由誰收尾**：本次確認是 `omp` worker 持續寫入的進行中成果。是否要讓 Vault Git Sync（`421c65050d13`，每 720 分鐘）負責收尾，還是等相關 session 自己收？
5. **watchdog 負向測試是否常態化**：本次是「先量到異常 → 看到 watchdog 報綠 → 修 → 看到 watchdog 報紅」才抓到 bug。是否要把負向測試寫成一支可重複執行的 script，避免同類 false negative 再發生。
6. **OpenClaw workspace 剩餘 52 untracked + 8 M 是否一併 commit**（DREAMS.md、45 份 dreaming journals、codex-helper / codex-safety-hooks frontmatter、lightpanda-browser YAML 尾逗號、google-finance parser、reviewer-finance、research-heartbeat、model-catalog-prune、skills/anatomy symlink、make_note_1.py、scratch/fix-cron-accounts.sh）。

## Recommended Default

- **Push**：Agent repo 直接 push（0/0 同步，無落後，diff 僅 3 檔 neat-freak 相關 + secret scan 乾淨）。OpenClaw workspace 先 `git log --oneline origin/master..HEAD` + `git diff --cached --stat` 檢視再 push。
- **Bundle**：刪除 917M bundle（fsck 已證實無 dangling commit、無資料遺失風險，21 個 refs 保留一個月）。磁碟只剩 30G / 86%。
- **4 個 error job**：先查 provider 連線層（三個週 job 錯誤字串完全相同），不要逐 job 各自排查。
- **Vault 534 筆**：維持不動，等寫入者收尾，避免 commit 到「寫到一半」的狀態。
- **watchdog 負向測試**：寫成 `scripts/watchdog-negative-test.sh`，每次改 watchdog 後必跑。
- **workspace 其餘變更**：維持現狀不動，交由各 session 自行收尾。`skills/anatomy` symlink 建議**不進 git**（無先例 + 指向外部 absolute path），改用 `git update-index --skip-worktree` 或加入 `.gitignore`。

## Risks / Do Not Do

- 🚫 **不刪除 vault 資料**——本輪對 vault 僅做唯讀檢查（fsck / count-objects / status / hash 比對），零寫入。
- 🚫 **不在未檢查 diff 前 push**。
- 🚫 **不用 `git rebase --skip`**（已知會靜默丟棄本地 commit）。
- 🚫 **不刪 `refs/neat-freak/dangling-backup/2026-11-11/*` 與 917M bundle**，除非 Pigo 確認。
- 🚫 **不動其他 session 的未 commit 成果**（Vault 534 筆、OpenClaw workspace 52 untracked + 8 M）。
- 🚫 **不把 `SKILL.md.bak-20261110` 當垃圾刪掉**——它是 canonical 的一部分（Agent repo 有 tracked），刪了 sync-check 會再報 MISSING。
- 🚫 **不動 `~/.hermes/workspace-backups/` 與 `~/Documents/hermes-backups/` 的既有備份**（另一套機制，每天 00:00 跑）。
- 🚫 **不對外發送任何內容**——本輪零對外動作。

## Next Action

1. 請 Pigo 檢視並決定是否 push：Agent repo `b17d7e3a19`、OpenClaw workspace 3 個既有 commit + 本輪 staged。
2. 確認後刪除 917M bundle（fsck 已確認安全）。
3. 另案處理：4 個 error cron job（先查 provider 連線層）、Vault 534 筆變更的收尾歸屬、watchdog 負向測試腳本化、OpenClaw workspace 剩餘變更。
