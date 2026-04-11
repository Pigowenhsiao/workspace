# Claude Code Skills Best Practices (摘要整合於 OpenClaw 知識庫)

以下為核心要點，便於快速檢索與落地實作：

- 目的與定位
  - Skills = 大腦與流程，MCP = 手腳，二者組合才是真正的 AI 能力乘法。
  - 以檔案系統為核心的漸進式揭露，避免單一大提示造成的不可控風險。
- 類型與用途
  - Reference: 背景知識與坑點，避免了解偏差。
  - Validation: 自動化驗證與斷言，提升輸出穩定性。
  - Data: 數據與監控相關，連接資料源。
  - Automation: 自動化工作流與重複任務。
  - Scaffolding: 提供模板與骨架。
  - Review: 程式與代碼審查。
  - Workflow: 端到端流程。
  - Investigation: 跨工具調查與報告。
  - Maintenance: 例行運維與風險控制。
- 設計與實作原則
  - 模式組合：Pipeline、Generator、Reviewer、Inversion 等可混用。
  - 漸進式披露：assets/ references/ SKILL.md 的組織與引用。
  - 動態上下文注入：在每次執行時注入實時信息。
  - 內部與外部工具分工：Skills 提供規範與 SOP，MCP 提供工具接入能力。
- 實作要點
  - 優先清晰的輸入/輸出、明確的檢查點與審核節點。
  - 將坑點與常見失誤寫入 Reference，避免重複同樣錯誤。
  - 記憶與日誌：使用可持續的儲存以支援長期回顧。

- 應用到 OpenClaw
  - 使用 SKILL.md 的相對路徑引用，方便分拆與組合。
  - Approvals 機制用於高風險動作的審核。
  - Skills 與 MCP 的協同使用，提升系統穩定性與可維護性。
