# neat-freak session — 2026-10-24d（cron `539040a91ad2`，第 10 run）

**Job:** Vault 整潔同步（neat-freak）· 5-Phase · cron `539040a91ad2`
**Result:** Vault 4 個 dangling tree **首次被完全清除**（`reflog expire` + `gc --prune=now`，
不需 `--aggressive`）；memory 鏡像一致；canonical ↔ Agent repo `neat-freak` 雙軌 0 diff；
`skill-index-check.py` ✓ ALL CLEAN（759）；cron output 清掉 1 個逾 7 天檔；
Hermes Backup 手動執行並驗證（463M，gzip -t OK）。
**同時修正 P0-core.md 對 live key 傳播範圍的不精確描述**（見 Pattern EEE）。

## 各 Phase 結果

| Phase | 項目 | 結果 |
|---|---|---|
| 1 | Vault `git status` | working tree clean，無 staged/unstaged 變更 ✅ |
| 1 | Vault 同步狀態 | `origin/main...HEAD` = 0 / 0 ✅ |
| 1 | Vault stash | `git stash list` 空 ✅ |
| 1 | dangling objects | 初跑 4 個 dangling **tree** → 執行 `git reflog expire --expire=now --all && git gc --prune=now` → **0 個**，`git count-objects -v` = `count: 0` ✅ |
| 2 | memory 鏡像 | `diff -rq ~/.hermes/memory/ ~/Documents/Agent/memory/` → 零差異（P0/P1/P2 md5 全 SAME）✅ |
| 3 | `sync-check.py` | ✓ CLEAN（references / scripts 結構、__pycache__ 皆無 drift）✅ |
| 3 | 內容比對 | `diff -r ~/.hermes/skills/neat-freak/ ~/Documents/Agent/skills/neat-freak/` = **0 diff**；`~/.hermes/skills/productivity/neat-freak/` 與 canonical `SKILL.md` sha256 **完全相同**（`0295d974…`）✅ |
| 3 | skills 全域交集 | canonical 1089 / repo 1577 個 SKILL.md；同 relpath 交集 57，內容差異 **0** ✅ |
| 3 | `skill-index-check.py` | ✓ ALL CLEAN（759 = header = 8 sections，0 dangling，0 purpose corruption）✅ |
| 4 | cron output | 50 / 50 / 8 檔（+ 6 legacy `.txt`），全 < 500 門檻；`cron-output-cleanup.py` 移除 1 個 >7 天檔 ✅ |
| 5 | Hermes Backup | cron `89c411611e6d`（每日 03:00）今日已自動執行；另手動 `hermes-backup.sh` → `hermes_2026-10-24_072246.tar.gz`（463M），`gzip -t` OK ✅ |

## Pattern EEE：dangling **tree** 用 `reflog expire` + `gc --prune=now` 就能清乾淨，不需要 `--aggressive`

**觀察**：過去多次 session（2026-10-24a/b/c）都把 Vault 的 4 個 dangling tree 記為
「無害殘留，不處理」。本次實測發現**它們是可以清掉的**：

```bash
cd ~/Documents/Pigo_Obsidian
git reflog expire --expire=now --all
git gc --prune=now          # ← 不需要 --aggressive
git fsck --full             # → 完全無輸出
git count-objects -v        # → count: 0, size: 0
```

**為什麼過去判定「清不掉」**：`references/dangling-objects.md` 的觀察記錄
（2026-05-15 / 05-16）只涵蓋 **dangling commit**，並記錄「`git gc` 標準 aggressive=0
無法清除，必須搭配 reflog expire」。但 **dangling tree** 是另一類物件：
它是某個被 gc 掉的 commit/tree 的殘留容器，其子 blob 早已不可達。
`reflog expire` 清掉 reflog 對這些 tree 的引用後，普通 `gc --prune=now` 就能回收。

**驗證口徑**：`git fsck --full` 輸出「懸空 tree XXXX」→ 執行上述兩行 → 再次 `git fsck --full`
**完全無輸出** = 乾淨。不要用 `git fsck --unreachable` 判斷（見 Pattern CCC：
那會把 dangling tree 的已 gc 子物件逐一枚舉，看起來像 100+ 筆「無法取得」）。

**成本考量**：`scripts/git-dangling-cleanup.sh` 內建 `git gc --aggressive`，
對 1.1G 的 Vault repo 會做完整 repack，耗時數分鐘且產生大量 I/O。
**日常 housekeeping 用 `reflog expire + gc --prune=now` 已足夠**，
`--aggressive` 只留給「要發布乾淨 tarball / docker image」等一次性場景。

**預防**：每次 Phase 1 報「N 個 dangling tree」時，應實際跑一次清理並用
`git fsck --full` 驗證，而不是直接歸類為「無害殘留」留到下個 session。

## 附帶修正：live key 傳播範圍的精確描述（P0-core.md）

**舊描述（2026-10-24b 寫入）**：「89 個 local-only commits **全部**含硬編碼 live API key」。

**本次逐 commit 掃描的實際結果**（`git grep -l -F <key> <commit>` 逐個跑 92 個 ahead commit）：

| commit | 含 live key 的檔案 |
|---|---|
| `b861b654` | `skills/x-note/scripts/xnote_rewrite_minimax_batch.py`、`xnote_rewrite_parallel.py` |
| `9477a6ae` | 上列 2 檔 + `rewrite_33.py`、`rewrite_last.py` |
| `18eb1284` | 上列 4 檔 + `bin/omp-pigo.bat` |

**關鍵事實**：
1. **只有 3 個 commit 的 tree 含 key**，不是全部 92 個。
2. **HEAD 的 tree 本身不含 key**（`git grep -F <key> HEAD` = 0 命中）——key 已在後續 commit 被移除。
3. 但這 3 個 commit 是 local-only 分支的 **ancestor**，`git push`（即使 fast-forward）
   仍會把帶 key 的 blob 物件一併上傳 → **「不可 push」結論不變**。
4. remote 端（`git ls-remote --refs origin` 全部 9 個 refs 逐個掃描）**0 命中**，維持乾淨。

**教訓**：寫「N 個 commits 全部含 X」這種斷言前，先逐 commit 掃描取證；
過度概括會讓後人誤判風險範圍（也會讓清理方案選錯——以為要處理 92 個 commit，
實際只有 3 個）。**量詞要用實測數字。**

## 未處理（沿用既有裁決）

1. **Agent repo 92 commits ahead 未 push** — 見上，push 會上傳含 live key 的 ancestor 物件。
   乾淨解法需 force-push rewrite（破壞性）或先 rotate key，兩者都需 Pigo 明確口頭授權。
2. **canonical 1089 vs repo 1577 個 SKILL.md** — 兩套命名空間（canonical 含 category 目錄、
   repo 含 runtime-only skill），非 drift，沿 2026-10-23e 裁決維持不動。
3. **Vault 備份目錄 43 份 / 24G，磁碟 78%** — 30 天 retention 由 `hermes-backup.sh` 自動處理，
   本次無 >30 天檔案，不需手動處理。
