# Claude Code Workflows (综合研究摘錄)

來源：ThinkInAIXYZ/clawdhome 與 Boris Cherny 的 15 条/章節整理，以及 DarkZodChi 的 Claude Workflows 概要。重點聚焦於如何在實務中落地，從長任務的分解、工具使用、記憶與自動化，到多工作區協作等核心要點。

摘要要點
- 工作流程核心：輸入任務 → LLM 推理與決策 → 工具調用 → 結果回饋 → 重複，形成穩定迴圈。
- 主要模式：Prompt Chaining、Routing、Parallelisation、Orchestrator-workers、Evaluator-optimiser。
- 重點實作：系統提示分段、CACHE 機制、memory 管理、日誌與回滾、測試與驗證。
- 兼容性與工具整合：MCP、LSP、外部工具與 GitHub/Git 相關流程。

OpenClaw 與 Claude Code 的對接要點
- Skill 與 Skeleton：以 SKILL.md 為單位，配合骨架模板與工具描述。
- Workflow 導向：把流程分拆成階段化任務，使用 Gate 進行審核。
- 安全性：Approvals、Hub / Hook、Heartbeat 的落地以保證穩健性。
- 跨平台與多模型：支援 Claude Opus/Sonnet/Haiku 等型號，混合推理與動態調度。

參考連結
- ThinkInAIXYZ clawdhome 頁面（GitHub）：https://github.com/ThinkInAIXYZ/clawdhome
- Claude Code 官方指南與 API：https://code.claude.com/docs/en
- Claude Code 工作流（相關筆記）：memory/learning/Claude_Workflows_10_Hours_Saved.md、memory/learning/Claude_Code_Workflows_Summary.md
- OpenClaw 的相關筆記與骨架：memory/learning/OpenClaw_Gstack_Link.md, memory/learning/Advanced_OpenClaw.md

下一步建議
- 將此筆記與實作 Skeleton 整合到 memory/index.md 的導航中，方便快速檢索。
- 產出以此為核心的 Skeleton 套件，包含 /tools、/memory、/skilles 的對應結構，方便日後導入 OpenClaw。
