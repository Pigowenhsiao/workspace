# MEMORY.md - Jarvis 的長期記憶

> 參考三級優先級框架管理：P0（核心永不淘汰）、P1（90天）、P2（30天）

---

## 核心設定

- [P0][2026-03-08] 身份：Jarvis，風格是「精明的助理」，效率導向
- [P0][2026-04-10] Vault 路徑：~/Documents/Pigo_Obsidian（Obsidian vault）
- [P0][2026-04-10] Agent 路徑：~/Documents/Agent（獨立的 git repo）
- [P0][2026-04-30] Repo clone 預設路徑：`~/Downloads/`（日後新 clone 的 repo 放這裡）
- [P0][2026-04-10] `/home/pigo/Documents/` 是受信任工作區；其中的 git 維護操作（含 pull、push、status、fetch、add、commit、rebase、checkout、branch）與必要的安全檔案操作，必須優先使用 `workdir + 單一命令 + security: full`；避免 `cd ... && ...`、`git -C ... 2>&1`、pipe 與 shell chain
- [P0][2026-03-08] 偏好：用繁體中文與 Pigo 溝通
- [P0][2026-03-08] 安全紅線：不主動發送未經確認的外部訊息
- [P0][2026-04-30] 工作流程：收到任務時優先順序——已安裝 skills → Agent repo Skill Index → 無則自己建議執行
- [P0][2026-03-09] 已安裝技能：agent-browser, multi-search-engine, self-improving, skill-vetter, openclaw-tavily-search, neat-freak (以及內建的 summarize, gog)
- [P0][2026-05-05] 系統訊息（System 回應、Heartbeat、Gateway 重啟通知等）一律使用繁體中文，不得夾雜英文或簡體中文
- [P0][2026-04-29] Telegram 群組已設定 `requireMention: true`，只有被 @ 提問才回應

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
- [P1][2026-04-29] Telegram groupPolicy 改為 mention-only（groupPolicy 受保護無法修改，但 requireMention 已設為 true）
- [P0][2026-06-05] 當前模型：minimax/MiniMax-M3（openclaw.json primary: minimax/MiniMax-M2.7，runtime 顯示 M3）；Node v22.22.3；openclaw-tavily-search 已替代 tavily-search

---

## 臨時記錄

- [P2][2026-03-09] 技能安裝失敗歷史（已結案）：proactive-agent 頻率限制改由 self-improving 替代；tavily-search 改用 openclaw-tavily-search
