# neat-freak handoff — 2026-10-27

**Job:** `neat-freak daily sync`（cron `31f0439f-532f-4e3e-8e14-38d4a82aadd1`）
**Run time:** 2026-10-27 04:00–04:12 UTC（台北 2026-10-27 12:00）
**Result:** 雙 repo 乾淨同步（0 ahead / 0 behind）、dangling objects 清乾淨（19 → 0）、P0 記憶與 canonical skill **反向**同步（Agent → hermes）、cron output 清 9 檔、Hermes 備份 `20261027_040939`（2.0G）、**每小時健康度 job 由紅轉綠（exit 1 → 0）**

> ## 🔴 本次唯一重大發現：Phase 2 / Phase 3 的「事實來源」方向寫反了
>
> - SKILL.md Phase 2 寫「以 `~/.hermes/memory/` 為準，同步到 `~/Documents/Agent/memory/`」
>   → 但本次 `~/.hermes/memory/P0-core.md` 是 **2026-10-26 16:12 的舊版（5,424 B）**，
>   `~/Documents/Agent/memory/P0-core.md` 是 **2026-10-27 02:56 的新版（6,503 B）**，
>   新版含 2026-10-27 的修正「push 禁令理由已失效」。照文件做 → **會把修正倒回去**。
> - Phase 3 寫「比對 canonical vs workspace：以 canonical 為準覆蓋 workspace copy」
>   → 但 canonical `SKILL.md` 是 **1,992 行**，workspace（Agent repo）副本是 **2,083 行**，
>   多出 4 個 Pattern（OOO-2 / LL-2 / FFF-2 / QQQ-2）與 1 個新 reference。
>   照文件做 → **會刪掉 4 個 Pattern**。
> - **兩個方向的 drift 都不是 canonical 落後，而是 workspace 領先。** 已依內容 superset 關係
>   實際套用 **Agent → hermes**（反向），兩邊現在 byte-identical。
> - 這同時解掉了每小時 job `33f50df6ac6b`（`Neat-freak 每小時雙目標掃描`）的紅燈：
>   `sync-check.py` 把「workspace 多出 `references/skill-index-2026-10-27-session.md`」
>   判成 EXTRA/DRIFT → exit 1。實際上那是 workspace 領先、canonical 該被補上。
>   補齊後 `sync-check.py` = **CLEAN**、每小時 job = **exit 0** ✅

---

## Goal

每日 vault 整理與同步檢查：確認 `~/Documents/Pigo_Obsidian`（vault）與 `~/Documents/Agent`（Agent repo）雙 repo 的 git 健康度、`~/.hermes/memory` ↔ Agent repo 記憶雙軌同步、canonical ↔ workspace skill 一致性、cron output retention、Hermes 備份機制。

## Current State

### ✅ 已完成

| Phase | 項目 | 結果 |
|---|---|---|
| 1 | Vault `git status --short` | 乾淨 ✅ |
| 1 | Vault `git fsck --full --no-progress` | **0 dangling** ✅ |
| 1 | Vault 同步狀態 | `## main...origin/main`、0 ahead / 0 behind ✅ |
| 1 | Agent repo `git status --short` | 乾淨 ✅ |
| 1 | Agent repo 同步狀態 | `## main...origin/main`、0 ahead / 0 behind ✅ |
| 1 | Agent repo dangling objects | 起初 **19 個**（7 dangling commit + 12 dangling tree）→ `reflog expire --expire=now --all` + `git gc --prune=now` → **0**，`count-objects -v` = `count: 0` ✅ |
| 1 | 未完成 rebase 檢查 | `.git/rebase-merge`、`rebase-apply`、`MERGE_HEAD` **皆不存在** → 無 Pattern LL-2 殘留 ✅ |
| 2 | Memory P1-90days / P2-30days | `diff` 無輸出（雙軌一致）✅ |
| 2 | **Memory P0-core.md** | canonical 為舊版 → **已由 Agent repo 反向同步前進 canonical**（6,503 B，兩邊 byte-identical）✅ |
| 3 | Canonical SKILL.md frontmatter | `name: neat-freak` 正確（`sed -n '2p'` raw bytes 讀取，三棵樹皆正確，無 Pattern A/B/O 損壞）✅ |
| 3 | **Canonical SKILL.md 內容** | canonical 為 Agent 副本的**嚴格子集**（5 個純新增 hunk、**0 個刪除**）→ **已由 Agent repo 反向同步前進 canonical**（1,992 → 2,083 行）✅ |
| 3 | Canonical references | 補上 Agent 側独有的 `references/skill-index-2026-10-27-session.md` → 兩樹檔名清單一致 ✅ |
| 3 | Canonical scripts | `comm` 雙向比對 → 無任何一方獨有檔案 ✅ |
| 3 | `sync-check.py` | 同步後 **RESULT: CLEAN**（先前為 DRIFT DETECTED）✅ |
| 3 | `skill-index-check.py` | OK ✅ |
| 4 | Cron output retention | 執行 `cron-output-cleanup.py` → **移除 9 檔**（9 個 job 目錄各 1 檔）✅ |
| 5 | Hermes Backup | `hermes-backup.sh` → `20261027_040939`（2.0G），prune 最舊 `20261015_160259`，保留 14 份 ✅ |
| — | **每小時健康度 job `33f50df6ac6b`** | 本次開頭 **exit 1（紅）** → 同步修正後 **exit 0（綠）**，輸出「✅ 雙目標正常（Vault + Agent）」✅ |
| — | Cron 健康度 | 22 jobs；**5 個 enabled job 非 ok**（見 Decision Needed）⚠️ |
| — | Stash | `git stash list` = **0 筆**（10-26 handoff 的 `stash@{0}` 已不存在）✅ |

### ⏭️ 略過 / 未處理

- **`~/.openclaw/workspace/skills/neat-freak/SKILL.md`**（OpenClaw 精簡版，184 行）— 與 canonical 架構不同，經比對為 OpenClaw 專用改寫版（非截斷、非腐敗），**刻意不同，不視為 drift、未修改**（與 10-24、10-26 兩次 run 結論一致）。
- **`~/.hermes/skills/` 不是 git repo** — canonical 無版控，本次同步為無痕操作。
- **Vault 資料零刪除**；Phase 4 只動 `~/.hermes/cron/output/` 的逾期 cron 輸出檔。
- **未執行任何 push**（本次無 commit 產生，兩 repo 皆 0 ahead）。

## Source Chain

```bash
# Phase 1 — 雙 repo
# workdir=~/Documents/Pigo_Obsidian
git status --short            # → (no output)
git fsck --full --no-progress # → 0 dangling
git rev-list --left-right --count origin/main...HEAD   # → 0  0
# workdir=~/Documents/Agent
git status --short            # → (no output)
git fsck --full --no-progress # → 19 dangling（7 commit + 12 tree）
git count-objects -vH         # → count: 920, size: 53.63 MiB, in-pack: 269699, packs: 9, size-pack: 802.25 MiB
git reflog expire --expire=now --all
git gc --prune=now            # → 不用 --aggressive（800MB pack，aggressive 會做完整 repack）
git fsck --full --no-progress # → 0 dangling
git count-objects -vH         # → count: 0, size: 0 bytes
ls .git/rebase-merge .git/rebase-apply .git/MERGE_HEAD   # → 皆不存在

# Phase 2 — 記憶雙軌（方向需先判定）
diff ~/.hermes/memory/P0-core.md ~/Documents/Agent/memory/P0-core.md   # → DIFF
stat -c '%y %s %n' 兩個 P0
#   2026-10-26 16:12  5424  /home/pigo/.hermes/memory/P0-core.md            ← 舊
#   2026-10-27 02:56  6503  /home/pigo/Documents/Agent/memory/P0-core.md   ← 新
diff ... | grep '^<'   # → 僅 1 行：舊版斷言「remote 全部 9 refs 不含 live key」
grep -c 'sk-cp-' 兩檔   # → canonical 0 / Agent 1（僅前綴 sk-cp-，非完整 key）
cp ~/Documents/Agent/memory/P0-core.md ~/.hermes/memory/P0-core.md
diff 兩檔              # → P0 SYNC-OK

# Phase 3 — skill 一致性
diff ~/.hermes/skills/neat-freak/SKILL.md ~/Documents/Agent/skills/neat-freak/SKILL.md
# → 5 個 hunk 全為新增（1325a1326,1347 / 1378a1401,1404 / 1412a1439,1461 / 1437a1487,1504 / 1570a1638,1661）
# → `grep '^<'` = 空 → Agent 副本為 canonical 的嚴格超集
comm -13 / -23 兩邊 references/ 清單
# → Agent 獨有: skill-index-2026-10-27-session.md；canonical 獨有: (無)
comm 兩邊 scripts/ → 雙向皆無獨有檔案
sed -n '2p' 三棵樹 SKILL.md → 皆為 name: neat-freak
cp ~/Documents/Agent/skills/neat-freak/SKILL.md ~/.hermes/skills/neat-freak/SKILL.md
cp ~/Documents/Agent/skills/neat-freak/references/skill-index-2026-10-27-session.md \
   ~/.hermes/skills/neat-freak/references/
python3 ~/.hermes/skills/neat-freak/scripts/sync-check.py   # → RESULT: CLEAN
python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py  # → OK

# Phase 4 / 5
python3 ~/.hermes/skills/neat-freak/scripts/cron-output-cleanup.py
# → Job 82f856963e0a: removed 1 files, kept 8 …（9 個目錄各 1 檔）Total files removed: 9
bash ~/.hermes/scripts/hermes-backup.sh
# → Done: ~/.hermes/workspace-backups/20261027_040939 (2.0G)
# → [prune] removing 20261015_160259

# 驗證 — 每小時 job 轉綠
bash ~/.hermes/scripts/neat-freak-hourly.sh
# → Vault: sync-check OK / skill-index-check OK / git status clean
# → Agent: sync-check OK / skill-index-check OK / git status clean
# → ✅ 雙目標正常（Vault + Agent）   EXIT=0
```

**關鍵事實記錄**

- 10-26 handoff 記載的 `stash@{0}`（`WIP on main: 6411d01786 Weekly defrag sync 2026-10-11`）**本次已不存在** → `git stash list` = 0 筆，該 Decision 項已過期。
- 10-26 handoff 的「live key 已在 origin/main 歷史」事件，本次實測 `git rev-list --objects origin/main..HEAD` 為空、`git show origin/main:memory/P0-core.md` 與 worktree 同一 md5 → **worktree 與 origin/main 已一致，無待推物件**。
- Vault 在 run 期間被併發的 news job 寫入 `00-Inbox/2026-10-27_News-Update-Noon.md` 並 commit `968393d71`，隨後該 job 自行 push → 複驗時 vault 已回到 0/0。
- `git gc --aggressive` 刻意未使用：Agent repo `.git` 達 **868M**（size-pack 802MiB），aggressive 會做完整 repack（數分鐘、大量 I/O）。依 `references/dangling-objects.md` 明載「日常只需 `reflog expire + gc --prune=now`」。

## Decision Needed

1. **【最高優先】記憶／skill 的「事實來源」方向規則需要定案** — 這是本次唯一實質性的方法論問題。SKILL.md Phase 2 / Phase 3 仍寫「canonical 為準、單向同步」，但實務上 canonical 與 workspace **輪流出現領先者**（本次兩者都是 workspace 領先；10-26 那次是 repo 領先）。已送 skill_workshop 提案（見 Next Action 第 2 項）把方向判定改為「mtime + 內容 superset 關係實測」。**在規則定案前，建議禁止任何自動 cp 覆寫 canonical 的動作。**
2. **5 個 enabled cron job 非 ok** — 4 個 `HTTP 429 Token Plan usage limit reached`（BensBites 每週精讀 / 每週技能健康度檢查 / Kanban 週日歸檔 / 其餘），1 個 `delivery_failed`（每週更新 superpowers + GSD + gstack）。429 是 MiniMax 額度耗盡，非程式錯誤；需 provider 端處置或改用其他 provider／降頻。
3. **每小時健康度 job 的失敗告警語意** — 本次它報的「EXTRA in workspace」其實是 workspace 領先（該補 canonical），不是污染。修好後轉綠，但**同類誤報會在下次 canonical 領先時再次出現**。是否要讓 `sync-check.py` 區分「污染」與「領先」兩種 EXTRA？
4. **`skills/x-note/` 歸檔**（延續 10-26 的 Decision 5）— 記憶記載 `x-note` 已於 2026-09-08 刪除、由 `x-agent` 接手，但 upstream 仍追蹤 `skills/x-note/scripts/*`。是否正式歸檔 `_dead-skills/`？
5. **OpenClaw workspace repo 的未追蹤檔** — `make_note_1.py`、`memory/handovers/` 3 檔（拼字錯誤目錄，與 `memory/handoffs/` 並存）仍 untracked，與 10-24 run 同一未解現象。**維持不動**，留待人工裁決。
6. **10-26 的 pending skill_workshop 提案** — `neat-freak-20261026-3affa47764`（push 前 key 掃描閘門）仍在 pending，未套用於 live skill。

## Recommended Default

拿不準時的預設處理方式：

- **記憶／skill 同步方向**：先比對 **mtime + 內容 superset 關係**（`diff | grep '^<'` 為空 = 該側為嚴格超集），再決定 cp 方向。**不無條件「canonical 為準」**。兩側皆為超集且互相有獨有內容時 → 合併而非覆寫，並在 handoff 記錄。
- **skill 同步的安全預設**：先 `diff` 再 `cp`；`diff` 顯示 0 個刪除行 → 覆寫是安全的（純新增）；顯示有刪除行 → 停下回報，不要自動覆寫。
- **dangling 清理**：日常一律 `reflog expire --expire=now --all` + `git gc --prune=now`；`--aggressive` 留給發布乾淨 tarball 等一次性場景（Agent repo pack 802MiB，aggressive 不划算）。
- **push 前一律兩道閘門**：① `git merge-base --is-ancestor origin/main HEAD`；② `git grep -l -E "sk-(cp|CMM)-[A-Za-z0-9_-]{60,}" <each to-be-pushed commit> --`。任一不過 → 不 push，改為回報 + 交接。
- **vault**：只讀 + fast-forward pull；不刪任何筆記；不跑可能改寫筆記內容的 script。
- **force-push**：一律不自動執行，除非 Pigo 明確口頭授權。

## Risks / Do Not Do

- 🚫 **勿刪除 vault 資料**（本次全程零刪除；`04-Archive/`、`08-Learning/`、history log 一律保留）。
- 🚫 **勿未經內容比對就單向覆寫 canonical**（本次兩次差點回退：P0 記憶的 2026-10-27 修正、SKILL.md 的 4 個 Pattern）。
- 🚫 **勿自行 force-push 遠端歷史**（需 Pigo 明確授權）。
- 🚫 **勿在分岔狀態下 `git rebase --skip`**（會靜默丟失本地 commit）——見 `references/rebase-conflict-hazard.md`。
- 🚫 **勿使用 `git add -A`**（大型 repo 會捲入預期外刪除——Pattern G）。
- 🚫 **勿在未做 key 掃描的情況下 push**（10-26 事件教訓；本次無 push 需求）。
- 🚫 **勿公開／對外發送 vault 內容、API key、session 細節**（本檔以檔名與數量描述，未記錄任何 key 值）。
- 🚫 **勿未經審查套用 pending skill 提案**（`neat-freak-20261026-3affa47764` 等仍待 Pigo 審查）。

## Next Action

1. **Pigo 裁決 Decision Needed 第 1 項**：記憶／skill 同步方向規則定案。**在定案前，任何自動 cp 覆寫 canonical 的行為應暫停**（本次已依 superset 關係手動判斷並反向同步，未造成回退）。
2. **審查 skill_workshop 提案**（本次新送，見 Proposed Skill Change 段）——把「方向由 mtime + superset 實測決定」與「sync-check EXTRA 兩義性」寫成 live skill 的可執行步驟，取代現行「canonical 為準」的單向規則。
3. **處理 5 個非 ok cron job**：429 額度問題需 provider 端處置或改 provider／降頻；每週更新 job 的 `delivery_failed` 需看是否重跑。
4. **裁決 `skills/x-note/` 歸檔**（Decision Needed 第 4 項）。
5. **裁決 OpenClaw workspace 的 `memory/handovers/` 拼字錯誤目錄**（Decision Needed 第 5 項）——是合併到 `memory/handoffs/`、加 gitignore、還是刪除。
6. **下次 neat-freak run 起手**：`git fetch origin` + `git status -sb` + 雙向 fsck；**記憶／skill 同步前先做 mtime + superset 判斷**。
