# neat-freak session — 2026-10-24a（cron `539040a91ad2`，第 7 run）

**Job:** Vault 整潔同步（neat-freak）· 5-Phase · cron `539040a91ad2`
**Result:** Vault 423 檔 `<think>` 殘留清理 → commit + push 完成（`d360ced1a`）；
Agent repo 與 origin/main 分歧收斂（merge `4c4b3682`）並補上上游遺漏的 security fix；
memory / skills 鏡像一致；cron output 無需清理；backup 已執行並驗證

## 各 Phase 結果

| Phase | 項目 | 結果 |
|---|---|---|
| 1 | Vault `git status` | 423 檔 modified（來源：cron `b27de85df4a3` 批次 `<think>` 清理）→ commit `d360ced1a` |
| 1 | 推送 | 首次 push 被拒（remote 有 `452caca14` / `43e6b29da` 新增 3 檔）→ `git rebase origin/main` → push ✅ |
| 1 | 內容驗證 | 純機械式移除 `<think>…</think>`；HEAD 比對僅 whitespace 差異；YAML invalid 0 / regressions 0；mojibake 0；frontmatter key 首字元脫落 0 |
| 1 | dangling objects | `git fsck` → dangling = 0 ✅ |
| 1 | 收尾狀態 | working tree clean；`origin/main...HEAD` = 0/0 ✅ |
| 2 | memory 鏡像 | `diff -rq ~/.hermes/memory/ ~/Documents/Agent/memory/` → 完全一致；P0/P1/P2 md5 SAME ✅ |
| 3 | Agent repo 分歧 | 88/88 分歧（同一批 commit 的 sanitized rewrite）→ merge `4c4b3682`，5 處 conflict 全採 upstream sanitized ✅ |
| 3 | `sync-check.py` | RESULT: CLEAN ✅ |
| 3 | `skill-index-check.py` | ✓ ALL CLEAN（759 = header = 8 sections，0 dangling，0 purpose corruption）✅ |
| 4 | cron output | 50 / 50 / 7 檔（113 總計），全 < 500 門檻，**無需清理** ✅ |
| 5 | Hermes Backup | 手動執行 `hermes-backup.sh` → `hermes_2026-10-24_004702.tar.gz`（463M），gzip OK，關鍵成員全在 ✅ |

## Pattern WW：origin/main 是 sanitized rewrite，不是「另一份歷史」

**觀察**：`~/Documents/Agent` 與 `origin/main` 分歧 88 / 88，但 88 個 commit 訊息幾乎逐字相同
（`diff` 只有 2 行差異），且 merge base 早在 `5347c617`。

**根因**：上游用 **rewrite（filter/rebase）** 產生一份 sanitized 平行歷史再 force-push，
commit 訊息保留、tree 不同（去除本機絕對路徑、去除硬編碼 secret）。
因此 local 與 remote 的 commit 是「同一件事的兩個版本」，不是「本地多做 / 上游多做」。

**判斷準則**（沿用 2026-10-23e 的規則並擴充）：
- 訊息相同 + tree 不同 → 幾乎一定是 sanitized rewrite，**衝突採 theirs**
- local 獨有 commit 帶有 upstream 沒有的功能（例：第 6 run handoff）→ 保留，不可 reset

**驗證方式**：`git diff --stat <local-sha> <origin-sha>` 應只顯示被 sanitize 的少數檔案；
若差異集中在路徑 / secret / `SKILL.md` 敘述，即確認為 rewrite 而非真實分歧。

## Pattern XX：upstream 的 security fix 只在 remote，本地沒有

**觀察**：upstream 有 `913a95a4`（fix(security): 移除硬編碼 MiniMax API key），
但 `git merge-base --is-ancestor 913a95a4 HEAD` = NO — **本地分支完全沒有這個 commit**。

**為什麼危險**：
- 本地 `bin/omp-pigo.bat` 與 4 支 `skills/x-note/scripts/rewrite_*.py` 仍硬編碼 125 字元 API key
- 該 key 存在於**全部 88 個 local-only commit 的 tree** 中 → 直接 `git push` 會把 secret 帶上遠端
- 但 upstream `origin/main` **沒有**這個 key（`git log -S<key> origin/main` = 空）→ 遠端是乾淨的

**處置**：`git merge origin/main`（不 rebase、不 force-push），5 處 conflict 全採 theirs，
merge 結果 tree 經掃描確認 0 個硬編碼 key。**不要** `git push --force`。

## Pattern YY：upstream sanitized 版本可能在本機無法執行

**觀察**：upstream `tools/minimax_key.py` 的 `_ENV_CANDIDATES` 只列 Windows 路徑
（`C:\Users\pigow\Documents\.env`），本機是 Linux → loader 直接 `SystemExit`。

**根因**：sanitize 流程移除「本機絕對路徑」時，把**該 runtime 需要的路徑**也一併移除，
導致 sanitized 版在來源機以外不可用。

**處置**：合併後補回**相對／展開式**路徑（`os.path.expanduser("~/Documents/.env")`），
不引入硬編碼絕對路徑，維持 sanitized 原則。

**驗證**：`load_minimax_api_key()` 實測可解析（len 125），
且 staged tree 的硬編碼 key 掃描為 0 hit。

## Pattern ZZ：`.env` 被程式讀取卻未被 gitignore

**觀察**：`tools/minimax_key.py` 會讀 `.env`，但 `.gitignore` 只有 `.env.context7` / `.env.notion.local`，
**沒有 `.env`** → 一旦有人在 repo 內建 `.env` 就會被 commit 上去。

**處置**：`.gitignore` 新增 `.env`（純新增一行，不影響既有規則）。

## 已知的既有 secret 曝露（非本次造成，未自行處理）

- remote 歷史 `34b7e2c5`（origin/main 可達）的 `bin/omp-pigo.bat` 仍含硬編碼 key
- 該 key 與目前 `~/Documents/.env` 的 live key **不同**（fp `649f4db0` vs `41742fc8`）→ 屬已輪替的舊 key
- 舊 key 在本機所有 `.env` 中均已不存在 → 風險已隨輪替解除
- 清理歷史需 force-push rewrite，屬破壞性操作，**未經 Pigo 明確同意不執行**

## 未處理（需人工裁決）

1. **Vault `18-Wealth/docs/每日要聞/20260919b/summary.md` 的 47 行刪除** — 已查明為 `<think>` 區塊
   （HEAD 版開頭是模型推理前言，現行版為 125 行完整新聞摘要）。屬機械式清理，非內容遺失 ✅ 已結案
2. **canonical ↔ Agent repo 技能名分歧** — canonical 254 / repo 443 top-level（排除 `_dead-skills`）；
   真正鏡像路徑 57 個，SKILL.md **0 差異** ✅。`devops` / `research` 兩者語意不同
   （canonical 是 category 目錄、repo 是單一 skill），非 drift，依 2026-10-23e 裁決維持不動
3. **canonical 254 個 skill 的子目錄（如 `devops/mcp-server-health-check`）在 Agent repo 無對應** —
   runtime-only skills，維持不動

## 環境事實

- `ftfy` 只在 `/usr/bin/python3`（3.12）；YAML 驗證一律用 `/usr/bin/python3`（預設 python3 會誤報 353/391 invalid）
- Vault 批量 rewrite 必須 binary 模式（x-note 多為 CRLF）
- `~/Documents/.env` 是本機 MiniMax key 的實際來源（`MINIMAX_API_KEY`，len 125）
- `git fsck --lost-found` 會在 `.git/lost-found` 留檔，vault 為 0 dangling
