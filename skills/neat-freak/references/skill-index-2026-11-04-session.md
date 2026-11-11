# neat-freak session — 2026-11-04（cron，第二十五 run）

## 結果：Phase 1/2/4/5 全綠；Phase 3 抓到 11-03 斷言與實況矛盾

| Phase | 結果 |
|---|---|
| 1 Vault git | uncommitted 1 檔（audit report 再生 15,637→15,786 files / 84,755→85,952 occurrences）→ `git add -f`（`12-Meta/reports/` 在 .gitignore 但已追蹤）→ commit `160183c2f`；push 被拒（remote 領先 1 個晚報 commit）→ fetch → 零重疊檔案 → merge（ort）→ push `0f840600f`。`git fsck --full` 完全無輸出 |
| 2 Memory | P0-core / P1-90days / P2-30days 三檔 `cmp` byte-identical；rsync 增量同步 `dreaming/deep/`（2 檔）與 `.dreams/session-corpus/`（4 檔）→ 兩樹 `diff -rq` 完全一致。dreaming/.dreams 在 Agent repo `.gitignore`（56、69 行）→ 不入 git，正常 |
| 3 Skills | sync-check CLEAN（content + repo-root copy）；skill-index-check 七項全綠（760/760、API breakdown 32+193+535=760、Skill_Category 581 自洽）；frontmatter 掃描 canonical 849 / workspace 1,578 檔 invalid 0、nofence 0；磁碟↔index 雙向比對 listed 760 = disk 760（排除 _dead-skills/_revived/.bak/examples 後）；**但 canonical↔workspace 真分歧 34 檔仍在**（見發現 1） |
| 4 Cron output | 最大目錄 50 檔（b27de85df4a3 / 94b3875ed533 / 539040a91ad2），遠低於 500 阈值 |
| 5 Backup | `hermes_2026_11-04_030020.tar.gz`（486MB）今日 03:00 已跑；`tar -tzf` 確認 4 個 `.env`（root/analysis/strata/Documents）全在 — Pattern WWW 修復持續有效 |

## 本次發現

### 1. 11-03「真分歧首次歸零（34→0）」斷言與實測矛盾 — 34 檔分歧原樣存在

11-03 session reference 宣稱 `diff -rq` canonical ↔ workspace **0 differ**。
本次用 `filecmp.cmp(shallow=False)` 對 canonical 樹全部 shared-path 檔案逐一比對：
**34 個內容分歧**，集合與 11-02 記錄的 34 檔完全相同：
- `x-note/**`（bin/×10、references/×11、SKILL.md）— Windows vs Ubuntu 平台遷移兩版本並存
- `*/Readme.md` 系列 ×11 — Codex 自動生成目錄說明 vs skill 自身說明（用途不同）
- `inbox-check/SKILL.md` — canonical v4 完整規格 vs workspace 精簡版

mtime 佐證：workspace `x-note/SKILL.md` 最後修改 11-01，canonical 09-20 —
11-03 前後**沒有任何一方被同步改寫過**，分歧不可能「曾歸零後又復發」。
結論：**11-03 的 0-differ 是量測錯誤**（可能只掃了部分目錄，或把 Only-in-X 噪音排除後誤讀為一致）。

**預防**（Pattern W 延伸）：
1. 「歸零」類斷言必須附**可複現命令 + 輸出**。`diff -rq` 輸出需同時列「只在 X」與「檔案不同」兩類，
   只 grep「檔案不同」再宣稱 0 differ 會漏掉量測基準問題。
2. 下次 run 若測到與上次宣稱相反的狀態，**先查 mtime 判斷是「新腐敗」還是「上次量測錯」**——
   mtime 全部早於上次 run 時間 → 上次量測錯的機率遠高於復發。

### 2. ftfy badness 掃描範圍教訓：只掃 skills/ 會漏掉 vendor/ 與 skill-backups/ 的真實 mojibake

本次把掃描範圍扩至整個 Agent repo：24 個 badness>50 命中，其中
`vendor/openclaw-imports/darwin-skill/README.md`（badness 971）實測
`fix_encoding()` 會改寫 → **真實 mojibake**（`中文` → `ä¸­æ–‡` 型雙重編碼）。

**處置：不修。** 全部 24 檔位於 `vendor/`（外部 bundle，非 canonical）與
`skill-backups/`（dated 封存備份，Pattern DD）。與 11-02 記錄「ftfy 0 命中」不矛盾——
那是因為當時掃描範圍只有 skills/ 兩樹。

**記錄**：未来 ftfy 掃描報告應標明範圍；vendor/backups 命中屬既有積壓，
只在新 ingest 到 skills/ 時才需要攔截。

### 3. Vault push race 持續屬常態

（另記 2026-11-04 第十八 run 實測）：本機 GitHub SSH 認證是**間歇性**的——同一 key
（`id_rsa` 檔名、實際是 ED25519）`ssh -T git@github.com` 成功、`git fetch` 成功，
但隨後 `git push` 連續 4 次 `Permission denied (publickey)`，等待 ~90 秒後**未改任何設定**
自行成功（`f00f2d1d6..4b221804e main -> main`）。
**處置準則**：遇到 `Permission denied (publickey)` 但先前同一 session 有成功的 SSH 操作時，
**不要改 key / 不要改 GIT_SSH_COMMAND**，sleep 後重試即可；連續失敗 >10 分鐘才升級排查。

本次 remote 領先 1 個晚報 commit（另一 job 18 點寫入），零重疊檔案、ort 乾淨 merge。
與 11-02 附記一致：Vault repo 的 push 競爭屬常態，照 Pattern LL 處置即可。

## 未處理
- canonical↔workspace 34 檔真分歧：全部 Pattern TTT 判定「不可機械同步」，留待 Pigo 裁決
  （x-note 平台遷移要保留哪邊、Readme.md 目錄說明要不要統一生成器）
- vendor/backups 24 檔 mojibake：封存區，不修（本次已記錄）
