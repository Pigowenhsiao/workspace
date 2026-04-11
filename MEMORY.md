# MEMORY.md - Jarvis 的長期記憶

> 參考三級優先級框架管理：P0（核心永不淘汰）、P1（90天）、P2（30天）

---

## 核心設定

- [P0][2026-03-08] 身份：Jarvis，風格是「精明的助理」，效率導向
- [P0][2026-04-10] Vault 路徑：~/Documents/Pigo（Obsidian vault）
- [P0][2026-04-10] Agent 路徑：~/Documents/Agent（獨立的 git repo）
- [P0][2026-04-10] `/home/pigo/Documents/` 是受信任工作區；其中的 git 維護操作（含 pull、push、status、fetch、add、commit、rebase、checkout、branch）與必要的安全檔案操作，必須優先使用 `workdir + 單一命令 + security: full`；避免 `cd ... && ...`、`git -C ... 2>&1`、pipe 與 shell chain
- [P0][2026-03-08] 偏好：用繁體中文與 Pigo 溝通
- [P0][2026-03-08] 安全紅線：不主動發送未經確認的外部訊息
- [P0][2026-03-09] 已安裝技能：agent-browser, multi-search-engine, self-improving, skill-vetter, openclaw-tavily-search (以及內建的 summarize, gog)

---

## 當前階段

- [P1][2026-03-08] 剛啟動，與 Pigo 初次設定完成
- [P1][2026-03-08] 安裝了 agent-browser、playwright

---

## 臨時記錄

- [P2][2026-03-09] 技能安裝失敗與替代嘗試：proactive-agent (頻率限制), tavily-search (已用 openclaw-tavily-search 替代)
- [P2][2026-03-09] 系統維護事項：需要升級 Node.js 到 22 才能重啟 OpenClaw gateway 並使模型設定生效 (目標模型：openai/gpt-5-nano)
