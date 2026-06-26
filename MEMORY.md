# MEMORY.md - Jarvis 的長期記憶

> 參考三級優先級框架管理：P0（核心永不淘汰）、P1（90天）、P2（30天）

---

## 核心設定

- [P0][2026-03-08] 身份：Jarvis，風格是「精明的助理」，效率導向
- [P0][2026-06-21] **Vault 路徑（已更正）**：`~/Documents/Pigo_Obsidian/`（Obsidian vault，git repo，remote = `git@github.com:Pigowenhsiao/Pigo_Obsidian.git`）；**不要與 `~/Documents/Pigo/` 混淆**（Pigo 是無關的第三個獨立 repo）
- [P0][2026-06-21] **Agent 路徑**：`~/Documents/Agent/`（git repo，remote = `git@github.com:Pigowenhsiao/Agent.git`，**不要與 Pigo_Obsidian 混淆** — 兩者命名相似但內容完全獨立）
- [P0][2026-04-10] Agent 路徑：~/Documents/Agent（獨立的 git repo）
- [P0][2026-04-30] Repo clone 預設路徑：`~/Downloads/`（日後新 clone 的 repo 放這裡）
- [P2][2026-06-26 → 已結案] **沿用異常清理（06-26 早批次）**：MEMORY 自身包含 #7564 的「workspace 90 untracked + 3 M」是 06-21 快照，**已 stale**（現場 `git status --short` 顯示只有 3M+1??：MEMORY.md / tasks/index.md / cron-handover.md + 2026-06-10_News-Update.md，無 90 untracked）。neat-freak SKILL.md drift 已修（workspace 141→183 行，與 Agent HEAD 088c03e5 對齊）。**沿用異常 ① ② ③ ⑤ 結案**；④ hermes-backup.sh 待 Pigo 裁決
- [P2][2026-06-26 → 已結案] **沿用異常 ④ hermes-backup.sh**（#7564 早批次）：`~/.hermes/scripts/hermes-backup.sh` 不存在，neat-freak Phase 5 永久略過。**Pigo 06-26 08:06 裁決走 (a) 建 sh** → 已寫入 `~/.hermes/scripts/hermes-backup.sh`（3137 bytes，可執行）。`--dry` 顯示備份 MEMORY.md / AGENTS.md / IDENTITY.md / SOUL.md / TOOLS.md / USER.md / memory / skills，跳過 arxiv_papers / handoffs / tmp_* 等。**沿用異常 5 條全結案**
- [P0][2026-04-10] `/home/pigo/Documents/` 是受信任工作區；其中的 git 維護操作（含 pull、push、status、fetch、add、commit、rebase、checkout、branch）與必要的安全檔案操作，必須優先使用 `workdir + 單一命令 + security: full`；避免 `cd ... && ...`、`git -C ... 2>&1`、pipe 與 shell chain
- [P0][2026-03-08] 偏好：用繁體中文與 Pigo 溝通
- [P0][2026-03-08] 安全紅線：不主動發送未經確認的外部訊息
- [P0][2026-04-30] 工作流程：收到任務時優先順序——已安裝 skills → Agent repo Skill Index → 無則自己建議執行
- [P0][2026-03-09] 已安裝技能：agent-browser, multi-search-engine, self-improving, skill-vetter, openclaw-tavily-search, neat-freak (以及內建的 summarize, gog)
- [P1][2026-06-18] Cron 排程：5 個 jobs — HF Daily Papers 09:00 / neat-freak 每 12h (04:00+16:00±5min) / 每日新聞 00:00 (全天總覽) + 12:00 午間 (市場焦點，2026-06-18 新建 job 8d465121) / Weekly Vault Defrag 每週一 04:00
- [P0][2026-05-05] 系統訊息（System 回應、Heartbeat、Gateway 重啟通知等）一律使用繁體中文，不得夾雜英文或簡體中文
- [P0][2026-04-29] Telegram 群組已設定 `requireMention: true`，只有被 @ 提問才回應
- [P0][2026-06-19] **minimax Code Plan API key**：`sk-cp-` 開頭的 key 是訂閱制，**不會過期**（除非配額/帳號問題）。sync 來源：`~/.local/share/opencode/auth.json` 的 `minimax.key`。x-note 等 skill 讀 `~/.pi/agent/auth.json`，**記得同步過去**，否則會 HTTP 401（2026-06-19 x-note 批次踩過）。opencode 與 `.pi/agent` 是兩個獨立位置，任一個被清空都不會通知對方

---

## 回覆規則

- 一律使用繁體中文回覆
- 回覆精簡，只保留必要資訊
- 成功時只回簡短結論；失敗、需要決策或有風險時才補充原因
- 預設格式：結論 → 必要細節 → 下一步

## 當前階段

- [P1][2026-04-29] llm-wiki 預設目的地改為 `00-Inbox/`，完成後再移至正式分類（Learning/articles/ 等）
- [P1][2026-05-03] 新筆記落地規則（強制）：所有新筆記一律先寫入 `00-Inbox/`，完成整理分類後再搬至正式位置（`08-Learning/` 各子目錄或 `09-Article-Notes/`）；此規則已寫入 `llm-wiki` 與 `note-update` 兩個 skill 的 SKILL.md
- [P1][2026-05-03] 任務日誌機制：建立 `memory/tasks/` 目錄，index.md 為首頁，每月一個 `.md` 檔；完成任務後同步更新 `memory/tasks/YYYY-MM.md` 和 `memory/tasks/index.md` 的待處理队列
- [P1][2026-06-26][STALE_AFTER=7d → 2026-07-03] **RTK 累計效益**：4,818 cmds / 23.5M in / 21.4M out / **省 2.1M tokens（9.1%）**（從 06-25 16:04 的 4,728 / 2.1M / 9.1% 提升 +90 cmds / +0.4M / +0.0%）；平均 1.1s/cmd。**Daily（06-26 截至 04:00）**：74 cmds / 398.2K in / 375.7K out / 22.6K saved (5.7%) / 2.0s（save% 較低，因本週早段大多 cron 觸發）。**Weekly（06-22~06-28 截至 06-26 04:00）**：859 cmds / 4.0M in / 3.3M out / 648.4K saved (16.2%)。**Monthly（2026-06）**：4,817 cmds / 23.5M in / 21.4M out / 2.1M saved (9.1%)。**07-03 之前重跑 `rtk gain -a` 更新此條**。**SOP**：neat-freak 跑時自動跑 `rtk gain -a -H`，產出「RTK 效益」章節附在報告中（2026-06-24 Pigo 決定）
- [P1][2026-04-29] Telegram groupPolicy 改為 mention-only（groupPolicy 受保護無法修改，但 requireMention 已設為 true）
- [P0][2026-06-18] 當前模型：minimax/MiniMax-M3（openclaw.json primary = runtime，皆為 M3；**MEMORY 早期誤記 M2.7 已更正**；fallback M2.5；M2.7/M2.7-highspeed/M2.5 皆已定義但未啟用）；Node v22.22.3；openclaw-tavily-search 已替代 tavily-search
- [P1][2026-06-20] **x-note 7.7.x 已 release**（commit `ac7bea369`+`e1bc4d5a2`，github.com/Pigowenhsiao/Agent.git）: Flow B Step 2 改為 fxtwitter API（`fetch_fxtwitter.py`，零認證零 CDP）；preflight `verify_score_scales.py` 改 score 1-5 vs 0-50 漂移；score threshold 固定 ≥3（1-5）。**未修復問題**：xnote2_curator.call_minimax_curator 仍 ~51s/call（`max_tokens=4000`+thinking enabled），target 7.7.3
- [P1][2026-06-20] **x-note 7.7.3 已 release**（commit `4b677ddc3`+`71b42af77`，github.com/Pigowenhsiao/Agent.git）: curator 30s SIGALRM hard cap + 1 retry + disk cache at `~/.cache/x-note-curator/`（sha256 key，重跑 0s）；score_and_note gate score≥4 才走 curator（~70% 減少 LLM call，wall clock 16min→3.6min）；xnote2_curator system prompt 0-50 docstring→1-5 對齊；parse_response 加 1-5 range check + dist outlier bucket（修 SCORE=0 KeyError）。Preflight `verify_score_scales.py` 7/7 PASS。Hermes session 09:22 UTC 實戰驗證全管線跑通。
- [P1][2026-06-20] **x-note 7.7.4 已 release**（commit `6370fed84`+`65a6339d9`，github.com/Pigowenhsiao/Agent.git）: 品質閘門（quality gate）+ sources traceability + curator_status；curator payload 關閉 thinking budget（Hermes 09:22 UTC 實測 51s/call → 預期縮短）。**Hermes production 2026-06-20 batch 已 ingest** vault（commits 81a83527 + b3fefce0 + 6d6995be），00-Inbox 從 21 個回升至 39 個
- [P1][2026-06-22] **x-note 7.7.5 已 release**（commit `1a3b0e84a`，github.com/Pigowenhsiao/Agent.git，06-22 10:59 UTC）: API fallback chain 硬化 — (a) fxtwitter endpoint 修正為 `/twitter/status/{id}`（舊 `/status/{id}` 會回 empty body）；(b) vxtwitter endpoint 必須用純 numeric ID，**不可**用 `{handle}/status/{id}`（會 empty）；(c) fallback 順序固定為 fxtwitter → vxtwitter（pure ID）→ ADHX → Playwright+cookies，fxtwitter empty 時**不可跳過** vxtwitter
- [P1][2026-06-25] **x-note 7.8.0 已 release**（commit `7c1f3f998`，github.com/Pigowenhsiao/Agent.git，06-25 08:11 +0900 = 06-25 04:11 UTC）: **Score contract migration 1-5 → 0-10**（breaking change）— (a) keep threshold ≥6.5（原 ≥3）、curator threshold ≥8.0（原 ≥4）；(b) `score_and_note.py` 強制執行 `verify_score_scales.py` preflight；(c) legacy quality scorer 預設 safe-by-default，刪除需加 `--delete`；(d) Flow A 改為 FxTwitter 為主（`fetch_fxtwitter.py` + `https://api.fxtwitter.com/twitter/status/<id>?decode=true`），baoyu-fetch+CDP 降為 fallback（threads/articles/失敗恢復）。**未修復問題**：`xnote2_curator.call_minimax_curator` ~51s/call 是否受 0-10 影響待驗證。**注意**：1-5 → 0-10 是真正分制變更，與 06-20「0-50 撤回」事件**無關**（不是 revert），是契約升級
- [P2][2026-06-23] **Agent repo 06-21 ~ 06-23 未記錄 commits**（neat-freak 觀察）：`ef07e5b28` evolve(neat-freak) rewrite SKILL.md 為 operational runbook + phase checklist（06-21 17:05）；`bc9c7fe75` feat(skills) add punk-skills（punk-cover + punk-avatar 視覺生成，adrianpunk/Punk-Skill，06-21 02:06）；`aa91c61c8` merge notebooklm-bridge skill into main（05:13 不詳）；`13a8153eb` chore auto-evolve skills 2026-06-21；`a5b6149bb` weekly defrag sync 2026-06-21；`2c0ba2497` feat @sairahul1 加入 AI/開發者工具清單（06-23 00:43）；`825a346ad` refactor 移除長期無內容帳號，新增 shao__meng/undefinedKi/kunchenguid/Easycompany333（06-23 00:46）
- [P2][2026-06-25] **Agent repo 06-25 13:31 UTC commit `4e9251993` neat-freak SKILL.md frontmatter corruption fix**（neat-freak 觀察）：修 SKILL.md Phase 3 與 Phase 5，**新增兩種 Pattern 偵測** — Pattern A `name: hermes-cron-jobs`（sync 時被 hermes-cron-jobs 內容覆寫）；Pattern B 檔案以 `import json` 開頭（Python import 殘留，line 4 覆寫 description）。驗證從 `head -3` 改 `head -5`。**新增 hermes-backup 缺失防呆**：Phase 5 加 `ls ~/.hermes/scripts/hermes-backup.sh` 預檢，**不存在就略過 phase** 不再 panic。commit 引用 `references/frontmatter-corruption-bug.md` 但實際 references 沒有此檔（**reference 缺失**，待補建）
- [P2][2026-06-25] **`~/.hermes/scripts/hermes-backup.sh` 不存在**（neat-freak 觀察）：`~/.hermes/scripts/` 實際只有 `bb-browser-daemon-startup.sh` / `cloakbrowser_twitter_test.py` / `extract_codex_cookies.py` / `horizon-daily.sh` / `kanban-daily-cleanup.sh` / `markitdown-mcp-health.sh` / `news-fetch.py` / `obscura-serve.sh` + `__pycache__`。**結論**：hermes 備份機制從未設定，neat-freak Phase 5 須略過。4e9251993 commit 已加防呆，下次跑 cron 不會誤判
- [P2][2026-06-25 → 已關閉 2026-06-26] **`frontmatter-corruption-bug.md` reference 缺失**（neat-freak 觀察）：commit `4e9251993` 修 SKILL.md 時引用 `references/frontmatter-corruption-bug.md`，但 reference 原本 0 內容。**Pigo 06-26 07:40 裁決走 (a) 補建** → 已寫入 `~/Documents/Agent/skills/neat-freak/references/frontmatter-corruption-bug.md`（3388 bytes，涵蓋 Pattern A/B 觸發情境、偵測腳本、修復流程、事件時間線）。MEMORY 沿用異常 ⑤ 結案
- [P2][2026-06-26] **Agent repo 06-25 21:37 UTC commit `a4aea5c1a` add @eng_khairallah1 to AI/開發者工具**（neat-freak 觀察）：Pigowenhsiao 手動 commit，`name.md` AI/開發者工具清單新增 @eng_khairallah1（位置在 @sairahul1 後、@shao__meng 前）；與 `ece98f6e` KAW: 12個月AI Engineer路線圖 by eng_khairallah 同作者同時間，是「先 commit 清單 → 再 commit KAW 詳解」的雙步驟入庫流程。**該作者背景**：中東/埃及的 AI Engineer KOL（與 @sairahul1 同分類）
- [P2][2026-06-20] **0-50 分制訊息時間線**（避免下次重複繞路）: Pigo 06:34 訊息要求 0-50 評分→Hermes 跑 0 條（threshold 不匹配）→ Pigo 07:49 發現版次 7.7.2 是 1-5 → 撤回 0-50。OpenClaw session 訊息 08:29/08:36/08:42 是延續同一思考，最終「放棄」=保留 1-5 = 7.7.3 已做的方向。**未來若 Pigo 再要求 0-50，先確認是否真的要 revert**（影響 4 個 commit），別假設。
- [P1][2026-06-20] **OpenClaw session 跟 Hermes session 是兩個獨立 runtime**: OpenClaw 看到 `~/.openclaw/workspace/skills/` 跟 `~/.openclaw/workspace/MEMORY.md`；Hermes 看到 `~/.hermes/skills/` 跟 `~/.hermes/memory/`（含 `xurl` CLI、`~/.hermes/logs/agent.log`）。**OpenClaw session 不會看到 Hermes 那邊的訊息，反之亦然**。同一 Pigo 可能在兩個 session 都發訊息造成 race condition；要查 Hermes 進度可讀 `~/.hermes/logs/agent.log`（已驗證可行）。

---

## 臨時記錄

- [P2][2026-03-09] 技能安裝失敗歷史（已結案）：proactive-agent 頻率限制改由 self-improving 替代；tavily-search 改用 openclaw-tavily-search
- [P2][2026-06-21] **判斷錯誤案例（已結案，預防再犯）**：把 `~/Documents/Pigo/`（空殼）當成 vault、誤推斷 vault 沒有 git、又誤把 `Pigowenhsiao/Pigo_Obsidian` repo 內容當成 Agent。**教訓**：clone repo 或 ls 陌生目錄時，**先看 .obsidian/、AGENTS.md、index.md 等自我描述檔**，再下結論；不要只看目錄命名
- [P2][2026-06-21] **2026-06-14 vault defrag 報告是 defect**：cron 掃的是錯誤路徑 `/home/pigo/Documents/Pigo`（空殼）而非真 vault `~/Documents/Pigo_Obsidian`；**Weekly Vault Defrag cron 的 vault root 設定需要修正**（見 C 項）
- [P1][2026-06-22] **OpenClaw cron registry 對 Hermes-執行 job 誤報 `Apply Patch failed`**（2026-06-22 12:00 午間新聞 `8d465121` 實測）：OpenClaw 排程註冊 → Hermes 實際執行 → OpenClaw 收到的 status patch 解析失敗 → 顯示 error + Telegram 未送達。**但實際 vault commit `bf932ee9` 已 push 成功**。**教訓**：看到 cron `Apply Patch failed` **先查 vault git log 與檔案存在性**（`git -C <vault> log --oneline -5` + `ls <vault>/00-Inbox/YYYY-MM-DD_News-Update*.md`），**不要信 registry 的 status**。commit author 是 `Hermes Agent <hermes@nos.com>` 或 `Hermes Cron <hermes@cron>` 可作為 Hermes 執行的辨識特徵
- [P2][2026-06-22] **git log --since/--until 過窄會漏掉 cron commit**：每日新聞 cron 跑在 cron scheduled 04:00 CST（= UTC 20:00 前一天），commit timestamp 跟 cron 觸發時間有時差（+0~60 分鐘）；用 `git log --since=YYYY-MM-DD --until=YYYY-MM-DD+1` 之類的窄範圍會錯過。**正確查法**：`git log --all --oneline | grep <pattern>` 或 `git log --since=YYYY-MM-DD --author=Hermes` 寬一點
