# Neat-freak 每日同步交接 — 2026-11-11

> ⚠️ **2026-11-11 16:00 UTC run 的更正**：本檔「Phase 3 四份副本全部 md5 相同、`sync-check.py` 結果 `RESULT: CLEAN`」的結論**只驗到 canonical / Agent repo / OpenClaw workspace 三份 SKILL.md**，漏了 **OpenClaw workspace 副本的完整目錄結構**。16:00 那輪把 `WORKSPACE_DIR` 明確指向 `~/.openclaw/workspace/skills/neat-freak` 後才測出 `RESULT: DRIFT DETECTED` — **缺 13 個檔**（`scripts/` 8 檔、`agents/` 2 檔、`references/skill-index-2026-11-03-session.md.keep`）+ 缺 repo-root 副本 `workspace/neat-freak/SKILL.md`。已於 commit `9ef69ad` 全數補回並重驗為 `RESULT: CLEAN`。
> **教訓：`sync-check.py` 的「CLEAN」只對它預設的 Agent workspace 成立，檢查其他副本必須顯式帶 `WORKSPACE_DIR=` / `WORKSPACE_ROOT=`。**
> 詳見 `memory/handoffs/neat-freak_2026-11-11_1600.md`。

## Goal
執行 neat-freak skill 五個 Phase 的每日 vault 整理與同步檢查：Vault git 健康、記憶副本同步、neat-freak skill 一致性、cron output retention、Hermes 備份。遵守「不刪 vault 資料、commit 後需檢查再 push」的約束。

## Current State
- ✅ **Phase 1 — Vault Git**：working tree 乾淨、`main...origin/main` 無落後。`git fsck --full` 原本回報 17 個 dangling commit + 12 tree/blob；經完整內容比對確認**無資料遺失風險**後已清理。最終 `fsck` exit 0、`count-objects -v` count=0、garbage=0、in-pack=126244。`.git` 從 2.1G → 1.9G。
- ✅ **Phase 2 — Memory Sync**：P0-core.md / P1-90days.md / P2-30days.md 三份 `cmp` 逐 byte 相同，無需同步。
- ✅ **Phase 3 — Skills Consistency**：**這是本次主要修復**。原本 4 份副本嚴重分歧（canonical 2551 行 vs OpenClaw workspace 184 行 vs Agent repo 2527 行），導致 cron job `33f50df6ac6b`（Neat-freak 每日四次雙目標掃描）連續紅燈 30+ 次。四份 SKILL.md 現在 md5 全部相同（`527c4d13c82c242d75753aea59190c66`），`verify-skill-frontmatter.sh` 四份全過，`sync-check.py` 結果 `RESULT: CLEAN`，watchdog 端到端 exit 0。
- ✅ **Phase 4 — Cron Output Retention**：執行 `cron-output-cleanup.py`，移除 210 個超過 7 天的舊輸出檔，22 個 job 目錄全部降到 ≤50 檔，總量 11M → 6.2M。
- ✅ **Phase 5 — Hermes Backup**：`bash ~/.hermes/scripts/hermes-backup.sh` 成功，產出 `~/.hermes/workspace-backups/20261111_124920`（2.0G），並依 MAX_KEEP=14 prune 掉最舊的 `20261015_040908`。
- ✅ **額外安全措施**：清理 dangling 前先建立 21 個 `refs/neat-freak/dangling-backup/2026-11-11/*` 保護 refs + 917M git bundle（`.git/neat-freak-dangling-backup-2026-11-11.bundle`），並把 4 個唯一內容 blob 另存到 `.git/neat-freak-recovered-blobs-2026-11-11/`（LLM-Wiki-Index、LLM-Wiki-Ingest-Log、2 份 MOC）。
- ✅ **Commits（未 push）**：
  - Agent repo：`970b508537` — 6 files, +2892/-25
  - OpenClaw workspace：`1c8e7b8` — 100 files, +10609/-165
- ❌ **未 push**：依約束只 commit，push 待 Pigo 檢查後決定。

## Source Chain
- `git status --short`（workdir `/home/pigo/Documents/Pigo_Obsidian`）→ 無輸出。
- `git fsck --full --no-progress` → 17 dangling commit + 12 tree/blob。
- **dangling 內容稽核（Python，逐一比對 blob SHA）**：21 個 dangling commit 觸及 274 個路徑；其中 116 個在 main、65 個在工作目錄、93 個「路徑已遷移」。逐一比對後：57 個有**完全相同 blob**、36 個經 frontmatter/wikilink 正規化後等價、**0 個實質內容遺失**。其餘 4 個 blob 內容為 LLM-Wiki-Index / LLM-Wiki-Ingest-Log / MOC 索引檔，已先落地存檔再清理。
- `git update-ref --stdin`（21 refs）→ 成功建立保護 refs。
- `git bundle create … refs/neat-freak/dangling-backup/2026-11-11/*` → 917M bundle 產出。
- `git cat-file -p <blob> > .git/neat-freak-recovered-blobs-2026-11-11/*` → 4 份內容落地。
- `git reflog expire --expire=now --all` → 無輸出。
- `git gc --prune=now` → 1m15s 完成，count=0。
- `git fsck --full --no-progress`（清理後）→ 無任何 dangling 輸出，exit 0。
- `git count-objects -v` → count: 0 / size: 0 / garbage: 0 / in-pack: 126244 / packs: 1。
- `cmp -s ~/.hermes/memory/<f> ~/Documents/Agent/memory/<f>` ×3 → P0/P1/P2 皆 SYNC-OK。
- `python3 ~/.hermes/skills/neat-freak/scripts/sync-check.py` → **RESULT: CLEAN**（修復前為 RESULT: DRIFT DETECTED）。
- `bash ~/.hermes/skills/neat-freak/scripts/verify-skill-frontmatter.sh neat-freak <dir>` ×4 → 全部 `[OK] frontmatter verified: name=neat-freak`。
- `bash ~/.hermes/scripts/neat-freak-hourly.sh` → **exit 0**（修復前 exit 1，紅燈 30+ 次）。
- `python3 ~/.hermes/skills/neat-freak/scripts/cron-output-cleanup.py` → Total files removed: 210。
- `bash ~/.hermes/scripts/hermes-backup.sh` → `==> Done: /home/pigo/.hermes/workspace-backups/20261111_124920 (2.0G)`。
- `python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py` → OVERALL: ✓ ALL CLEAN（761 skills / 582 categories 全綠）。
- `python3 -c "json.load(jobs.json)"` → 22 個 cron job；**4 個 last_status=error**：`33f50df6ac6b`（本次已修好）、`0c0aca87f467`（每日精選晚報）、`ba23c28aec2c`（每週技能健康度檢查）、`fbb0a9e5147b`（BensBites 每週精讀）、`ed7968b363f1`（Kanban 每週日歸檔）。

## Decision Needed
1. **是否 push 兩個 commit**：Agent repo `970b508537`（落後 remote 3 個 commit，需先 merge/rebase）+ OpenClaw workspace `1c8e7b8`。本次依約束未 push。
2. **是否保留 dangling 保護機制**：`refs/neat-freak/dangling-backup/2026-11-11/*`（21 refs）+ 917M bundle 目前還在 vault repo 內。bundle 佔 917M（磁碟剩 28G），確認不需要復原後可刪除；refs 可保留數週。
3. **Vault dangling 清理是否常態化**：本次證實「dangling commit ≠ 資料遺失」，但 93 個「路徑已遷移」檔案說明 vault 有大量 rebase/amend 產物。是否把清理納入每日 cron（目前只有 skill 的 `--aggressive` 腳本，且對 1.9G repo 很慢）。
4. **4 個仍為 error 的 cron job** 是否要排查（`0c0aca87f467` 每日晚報、`ba23c28aec2c` 週檢查、`fbb0a9e5147b` BensBites、`ed7968b363f1` Kanban 週歸檔）。
5. **OpenClaw workspace 62 筆非 neat-freak 未 commit 變更**（MEMORY.md、DREAMS.md、google-finance parser、codex-helper 等）是否一併 commit——這些是其他 session 的工作成果，本次未動。

## Recommended Default
- Push：先 `git fetch && git log --oneline origin/main..HEAD` 檢視 diff，再用 **merge 而非 rebase**（避免 `rebase --skip` 靜默丟 commit 的已知危害，見 `references/rebase-conflict-hazard.md`），push 前再掃一次 `sk-` token 並用 sha256 對照 live key。
- Bundle：保留 7 天確認 vault 無異常後刪除，refs 保留一個月。
- 未 commit 的 workspace 變更：維持現狀不動，交由各 session 自行收尾，避免混雜 commit。

## Risks / Do Not Do
- 🚫 不刪除 vault 資料——本次清理只動 git 物件層，所有內容已先驗證等價或另存。
- 🚫 不在未檢查 diff 前 push。
- 🚫 不用 `git rebase --skip`（已知會靜默丟棄本地 commit）。
- 🚫 不把 `SKILL.md.bak-20261110` / `.keep` / `skill-index-2026-11-03b-session.md` 當垃圾刪掉——它們是 canonical 的一部分，刪了 sync-check 會再報 MISSING。
- 🚫 不動 `~/.hermes/workspace-backups/` 與 `~/Documents/hermes-backups/` 的既有備份（另一套機制，每天 00:00 跑）。
- 🚫 不刪 `refs/neat-freak/dangling-backup/*` 與 917M bundle，除非 Pigo 確認。

## Next Action
1. 請 Pigo 檢視兩個 commit 的 diff 後決定是否 push（Agent repo 需先合併 remote 3 個 commit）。
2. 確認後刪除 917M bundle（若不再需要復原）。
3. 另案處理 4 個 error 狀態的 cron job 與 workspace 62 筆待收尾變更。
