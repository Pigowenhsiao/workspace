# Claude Code Workflows - 完整整理（來自文章片段）

來源：Axel Bitblaze 分享的內容摘要與整理，涵蓋 Claude Code 的工作流程與實作要點。

內容要點概覽：
- 工作流程核心：輸入任務 -> 讓 LLM 思考與決策 -> 使用工具 -> 迴圈直到任務完成
- Workflows 與 Agent：分別描述工作流程與真正的自動化代理的差異與適用情境
- 模型分級與工具整合：思考與工具的組合使用，以及如何在不同模型版本間切換
- 設計原則：分層架構、記憶管理、日誌與錯誤處理、測試與回滾
- 探討的模式：Pattern 1 Prompt chaining、Pattern 2 Routing、Pattern 3 Parallelisation、Pattern 4 Orchestrator-workers、Pattern 5 Evaluator-optimiser
- 進階實作：提供 Skeleton 檔案與模板的落地方式，適合直接復用於專案

關鍵連結與參考：
- 文章中的多段落內容與示例，與 OpenClaw 的對應關係相似，皆強調以流程與工具為核心的實作。
- 連結到其他相關筆記：memory/learning/Deep_Agents_Evaluation_Guide.md、memory/learning/Claude_Workflows_10_Hours_Saved.md、memory/learning/Claude_Code_Workflows_Summary.md

下一步建議：
- 將此筆記與相關 Skeleton/模板整合至 memory/index.md，方便快速檢索與導覽。
- 對應 OpenClaw 的技能，產出實作骨架以便直接測試。