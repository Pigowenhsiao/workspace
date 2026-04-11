# AGENTS.md - Your Workspace

This folder is home. Treat it that way.

## 操作規則

- 當 Pigo 要你「安裝 skill」時，優先使用固定流程：
  - `openclaw skills search <query>`
  - `openclaw skills info <slug>` 或 `openclaw skills list`
  - `openclaw skills install <slug>`
- 安裝完成後要實際驗證 skill 是否已進入 `workspace/skills/`，不要只回報命令已執行。
- 當 Pigo 要你「閱讀 AGENTS.md、USER.md 等檔案了解現況」時，先讀：
  - `AGENTS.md`
  - `USER.md`
  - `TOOLS.md`
  - `SOUL.md`
  - `IDENTITY.md`
  - `HEARTBEAT.md`
  - `MEMORY.md`
  - `memory/index.md`
- 然後列出 workspace 檔案清單，再按相關性擴充閱讀。不要在單一回合無差別聲稱已讀完整個 workspace。
- 當使用者要你抓新聞標題或今日新聞時，不要只直連新聞站首頁。
  - 優先使用現有 skills：`multi-search-engine`、`openclaw-tavily-search`
  - 優先嘗試可直接讀取的 feed 或可讀頁，而不是先用 browser scrape
  - 對 CNBC 類站點，先用 shell 工具抓官方 RSS；例如可先試 `curl -L -A "Mozilla/5.0" --max-time 15 https://www.cnbc.com/id/100003114/device/rss/rss.html`
  - 若官方 RSS 或可讀頁能拿到標題，就直接整理標題與連結，不要繞回首頁 DOM 擷取
  - 若單一搜尋引擎被 bot-detection 擋住，必須自動改走其他搜尋來源、新聞搜尋結果頁、RSS 或可讀替代來源
  - browser 僅作最後手段，而且必須避免假設固定 DOM 結構；任何 evaluate 先檢查目標節點是否存在
  - 單一步驟若超過合理時間仍無結果，應立即換下一條路徑，不要長時間卡住
  - 回傳可核對的標題與來源，而不是直接停在「被擋住」

## 新增外部閱讀與連結
- Deep Agents 評估體系構建指南：memory/learning/Deep_Agents_Evaluation_Guide.md
- Deep Agents 評估摘要：memory/learning/Deep_Agents_Evaluation_Summary.md
- OPC_9_Agent_Skills_Minimalist_Entrepreneur.md（OPC 的 9 技能）
- Advanced_OpenClaw.md（OpenClaw 高級篇骨架）
- OpenClaw_Gstack_Link.md（OpenClaw 與 gstack 連結）
- Claude_Workflows_10_Hours_Saved.md
- Claude_Code_Workflows_Summary.md
- Home_Household_OpenClaw.md
- Family_OpenClaw_Scenarios.md
- Build_AI_Agent_Complete_Guide.md
- Build_AI_Agent_Complete_Guide_Skeletons.md
- memory/index.md 的導覽補充段落

## 其他更新提醒
- 將新的筆記納入 memory/index.md 的導航與引用，方便跨檔案閱讀
- 可考慮建立一鍵更新腳本，自動化產出索引與骨架
