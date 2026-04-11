# OpenClaw 與 gstack 連結與實作要點

本文說明如何把 OpenClaw 的三層記憶模型、Skills 與 MCP 架構，與 Garry Tan 的 gstack 思路對接，形成一個可實際落地的工作流。

連結到的內容：
- OpenClaw 三層記憶模型與安全機制 (memory/learning/OpenClaw_Three_Tier_Memory.md)
- Five Agent Skill Design Patterns (memory/learning/Five_Agent_Skill_Design_Patterns.md)
- Pipeline 模式詳述 (memory/learning/Agent_Skill_Pipeline_Pattern.md)
- 相關骨架模板與範例（memory/learning/Pattern_Templates/）
- Garry Tan 的 gstack 專案 (https://github.com/garrytan/gstack)

核心觀點
- gstack 提供一套以角色、手續與管控為核心的工程工作流，適合與 OpenClaw 的 MCP/Skills 結合，實現「一人團隊」的高效開發與部署。
- 透過 Slash Commands 將不同角色的工作流模組化，配合 Approvals、Heartbeat、Context Fork 等機制，可以把 Automations 推向自主管理與自我改進。

實作要點
- 在 OpenClaw 中建立一個新的 Skeleton，對應 gstack 的職責分工，例如：/office-hours、/plan-ceo-review、/browse 等等，並用 SKILL.md 內容定義觸發詞與輸出。
- 將實作分拆成多個檔案與資料夾，實作模板和踩坑記錄以利長期維護。
- 設計安全機制：/careful、/freeze、approvals，確保高風險操作有審核與日誌。

進階連結與引用
- gstack 文檔與安裝指引：https://github.com/garrytan/gstack
- OpenClaw 的相關筆記：memory/learning/Five_Agent_Skill_Design_Patterns.md、memory/learning/Agent_Skill_Pipeline_Pattern.md、memory/learning/OpenClaw_Three_Tier_Memory.md

下一步：
- 如需，我可以把這份連結寫成 memory/index.md 的條目，並在 AGENTS.md 增加引用，實現「跨檔案連結閱讀」的導航。