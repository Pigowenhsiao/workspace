# neat-freak session — 2026-11-12c（第三次 run，OpenClaw cron 16:00 UTC）

## 摘要
同日第三次 neat-freak run。**主要事件＝撞上同日第二次 run 的 competing commit**，以及**查清 3 個週期 cron job 連續 error 的根因**（strata SSH tunnel 在 v100 端服務重啟期間斷線）。

---

## 一、Competing commit 撞車：同一份 reference 被兩個 run 同時寫

### 症狀
`git fetch origin` 後 Agent repo 顯示 `origin/main...HEAD` = **2 / 1**（不是 0/0）。
遠端多出 2 個 commit，作者 `Hermes (cron) <pigo@hermes-agent.local>`，時間 **2026-11-12 18:06~18:07 CST = 10:06~10:07 UTC**：

| commit | 內容 |
|---|---|
| `acb721e5f4` | `git rm` 孤兒 `references/skill-index-2026-11-03-session.md.keep`（143 行） |
| `b06ced8d68` | 寫 `references/skill-index-2026-11-12-session.md`（35 行）+ 兩份 SKILL.md 各 +4 行 |

本地 commit `b17d7e3a19`（04:16 UTC）寫的是**同名** `references/skill-index-2026-11-12-session.md`（102 行）→ `git merge origin/main` 產生 **add/add conflict**。

### 根因
同日有兩套排程系統在跑 neat-freak：
- Hermes cron `33f50df6ac6b`（`0 2,8,14,20 * * *`）→ 10:06~10:07 UTC 這一輪
- OpenClaw cron `31f0439f`（`0 */12 * * *` Asia/Taipei）→ 04:00 UTC 這一輪（就是本檔）

兩者**各自**在 canonical→workspace 同步流程中寫同一個檔名，沒有共用 run-id namespace。

### 處置（沿用 11-03 / 11-03b 命名機制，零刪除）
1. `git merge origin/main` → 3 處 conflict（2 份 SKILL.md content conflict + 1 份 reference add/add）
2. 遠端版本**另存**為 `references/skill-index-2026-11-12b-session.md`（35 行，未刪任何一版）
3. 本次版本保留在 `references/skill-index-2026-11-12-session.md`（102 行）
4. 兩份 SKILL.md 手動解 conflict：保留 Pattern EEEE 全文 + 追加 `11-12b` 引用行
5. SKILL.md「附：2026-11-12 run 新增參考」區塊同時列 `11-12` / `11-12b` / `11-12c` 三條

**教訓（Pattern 延伸）**：
- **同日多 run 的 reference 檔名必須帶 run 序號**（`-session` / `-b-session` / `-c-session`），否則第二個 run 必然覆蓋第一個。
- **不要用 `git rebase --skip`**（已知會靜默丟棄本地 commit）。正確處置是 `git merge` + 兩版並存 + 引用行分列。
- merge upstream 後**必須**重跑 `sync-check.py` 與 `skill-index-check.py`（本次兩者皆 CLEAN 才 commit）。

### `.keep` 孤兒刪除的一致性收尾
遠端 `acb721e5f4` 刪了 Agent repo 的 `.keep`，但 canonical `~/.hermes/skills/neat-freak/references/` 與 OpenClaw workspace 副本**都還在** → 這是 drift 的種子。
本次驗證：`cmp` 確認 `.keep` 與 `skill-index-2026-11-03-session.md` **byte-identical**（143 行），全 repo grep **零引用**，canonical scripts 亦零引用 → **零資訊損失的純重複**，故從 canonical 與 OpenClaw workspace 一併移除，讓三處狀態一致。

---

## 二、3 個週期 cron job 連續 error 的根因（本次查清）

### 症狀
`fbb0a9e5147b`（BensBites 週精讀）、`ba23c28aec2c`（週技能健康度）、`ed7968b363f1`（Kanban 週歸檔）
三者 `last_error` **字串完全相同**：`RuntimeError: Connection error.`，`failure_streak: 1`，最後執行時間都在 **2026-11-08**。

### 根因（不是 job 邏輯問題，是 provider 連線層）
從 `~/.hermes/logs/agent.log.3` 抽出完整錯誤堆疊：
```
openai.APIConnectionError: Connection error.
agent.conversation_loop: API call failed (attempt 1/3)
  error_type=APIConnectionError
  provider=custom  base_url=http://127.0.0.1:8081/v1/  model=qwen3.8-flash-next-iq3_s
  policy=default  error=Connection error.
```
`8081` 是 **SSH local-forward tunnel**（`~/.config/systemd/user/strata-tunnel.service`）：
```
ssh -N -L 8080:127.0.0.1:8081 -L 8081:127.0.0.1:8081
    -L 18080:127.0.0.1:8081 -L 18081:127.0.0.1:8081 ... v100
```
`journalctl --user -u strata-tunnel.service` 在 2026-11-08 22:03~23:05 密集出現：
```
ssh[1535274]: channel 8: open failed: connect failed: Connection refused
```
→ **v100 上的 inference server 8081 在 11-08 當時重啟／離線**，SSH tunnel 本身活著但後端 port 拒絕連線，OpenAI SDK 丟出泛用的 `Connection error.`

### 量測佐證
- 錯誤分布：`agent.log.3` 956 筆、`agent.log.2` 276 筆、`agent.log.1` 265 筆、當前 `agent.log` **0 筆**
- 時間戳集中在 2026-11-08 13:34~17:00 與 22:03~23:05 → 與 tunnel 斷線時段吻合
- 目前 tunnel `Active: active (running) since Thu 2026-11-12 06:20:40 UTC`，`curl http://127.0.0.1:8081/v1/models` → **HTTP 401**（服務活著，只是要 auth）

### 結論
三個 job 共用同一 provider（`custom` / `127.0.0.1:8081` / `qwen3.8-flash-next-iq3_s`），**一個 tunnel 斷線就同時打三個 job**。不是三個獨立 bug。

**建議處置**：把這三個 job 的 `last_status` 錯誤理解為「provider 連線層事件」而非 job 邏輯錯誤；
下次 `0 2 * * 0`（11-15 02:00 UTC）三個 job 會同時重跑——若 v100 當時活著，應自動恢復 ok。
若 11-15 仍紅，才需要個別排查。

### 第 4 個 error job 是不同問題
`0c0aca87f467`（每日精選晚報）`last_error: interrupted`，2026-11-11 12:08 輸出 **0 bytes**。
且 **2026-11-12 12:00 那輪完全沒有輸出檔**（`~/.hermes/cron/output/0c0aca87f467/` 沒有 `2026-11-12*`）→ 連續兩天沒產出，與 tunnel 無關，屬 job 本身被中斷。

---

## 三、五 Phase 巡檢結果

| Phase | 結果 |
|---|---|
| 1 Vault git | `git status` **0 筆**（早上那輪的 534 筆已被寫入者收尾，`HEAD=f9cbef5d0 chore: auto-sync 2026-11-12 15:10`）；`main...origin/main` = **0/0**；`fsck --full` → 2 dangling tree + 1 dangling commit |
| 2 Memory | P0-core / P1-90days / P2-30days 三檔 `cmp` 逐 byte 相同（SYNC-OK） |
| 3 Skills | canonical↔Agent **CLEAN**、canonical↔OpenClaw（帶 `WORKSPACE_DIR=`/`WORKSPACE_ROOT=`）**CLEAN**；`skill-index-check.py` → **OVERALL ✓ ALL CLEAN**（761 rows / 582 categories / 32+193+536） |
| 4 Cron output | `cron-output-cleanup.py` 移除 3 個 >7 天舊檔（`33f50df6ac6b` 2 檔、`421c65050d13` 1 檔）；總量 12M |
| 5 Backup | `hermes-backup.sh` → `20261112_160649 (2.0G)`，prune 最舊 `20261018_160412`，維持 14 份 |

---

## 四、dangling commit 這次有內容

`fsck --full` 這次報的 dangling commit **不是空殼**：
```
dangling commit 31f037843a0a748e8dc1001c0c3a35070076218c
  "On main: wip-background-2026-11-12"  (2026-11-12 13:39:35 +0000)
```
`git diff 31f037843 HEAD` → **607 files changed, +57841 / -42**。
內容是 2026-11-12 的 vault 整理成果（`Daily/Briefing/2026/10/*.md` → `04-Archive/legacy-daily-dup-2026-11-12/` 的 R100 搬移、`08-Learning/01_AI-Agent/` 新增 x-note 筆記、`12-Meta/vault-defrag-report-2026-11-12-pm.md` 等）。
其中 **607 筆差異裡 `D`（dangling 有、HEAD 沒有）= 0 筆** → 沒有任何只存在於 dangling commit 的檔案，**無資料遺失風險**。

**注意**：本次 fsck 報 dangling commit，上一輪（04:00 UTC）報的是「無 dangling commit」。差異原因是中間有 `omp` worker 做了 `git stash` 類操作，stash 的 commit 在 stash 被丟棄後變成 dangling。

---

## 五、來源鏈（關鍵指令與輸出）

| 指令 | 輸出摘要 |
|---|---|
| `git -C ~/Documents/Agent fetch origin && git rev-list --left-right --count origin/main...HEAD` | **2 / 1**（原本以為 0/1，fetch 後才看到遠端多 2） |
| `git -C ~/Documents/Agent merge origin/main` | 3 conflicts（2 SKILL.md + 1 add/add） |
| `git show origin/main:skills/neat-freak/references/skill-index-2026-11-12-session.md` | 35 行（第二 run 版本） |
| `git show HEAD:.../skill-index-2026-11-12-session.md` | 102 行（第一 run 版本） |
| `cmp ~/.hermes/.../11-03-session.md.keep ~/.hermes/.../11-03-session.md` | **BYTE-IDENTICAL** |
| `grep -rn "11-03-session.md.keep"` 全 repo | 零引用（只有歷史 handover 敘述提及） |
| `grep -h "Connection error" ~/.hermes/logs/agent.log.3` | `openai.APIConnectionError` + `provider=custom base_url=http://127.0.0.1:8081/v1/ model=qwen3.8-flash-next-iq3_s` |
| `journalctl --user -u strata-tunnel.service --since 2026-11-07 --until 2026-11-09` | `channel 8: open failed: connect failed: Connection refused`（11-08 22:03~23:05） |
| `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8081/v1/models` | **401**（服務活著） |
| `git -C ~/Documents/Pigo_Obsidian fsck --full --no-progress` | 2 dangling tree + 1 dangling commit `31f037843`（607 files / +57841） |
| `git diff 31f037843 HEAD --name-status \| grep -c '^D'` | **0**（無檔案只存在於 dangling） |
| `python3 ~/.hermes/skills/neat-freak/scripts/sync-check.py` | `RESULT: CLEAN` |
| `WORKSPACE_DIR=~/.openclaw/workspace/skills/neat-freak WORKSPACE_ROOT=~/.openclaw/workspace python3 .../sync-check.py` | `RESULT: CLEAN` |
| `python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py` | `OVERALL: ✓ ALL CLEAN` |
| `python3 ~/.hermes/skills/neat-freak/scripts/cron-output-cleanup.py` | `Total files removed: 3` |
| `bash ~/.hermes/scripts/hermes-backup.sh` | `==> Done: .../20261112_160649 (2.0G)` + prune `20261018_160412` |
| `bash ~/.hermes/scripts/neat-freak-hourly.sh` | 全綠（watchdog 修好後 Vault/Agent 皆 clean） |

---

## 六、未處理

- **Agent repo `b17d7e3a19` 未 push**（本 run 改為 merge commit 解決後再 push）
- **917M dangling 保護 bundle**（`.git/neat-freak-dangling-backup-2026-11-11.bundle`）與 **21 個** `refs/neat-freak/dangling-backup/2026-11-11/*` 仍在 vault repo → 未刪（等 Pigo 裁決）
- **OpenClaw workspace 62 筆未 commit 變更**（10 M + 52 ??：DREAMS.md / dreaming journals / finance parser / codex-helper / skills-anatomy symlink 等）→ 屬其他 session 成果，本次不動
- **4 個 error cron job 的 `last_status` 未手動改寫**（本次已查明根因，等 11-15 自然重跑驗證）
