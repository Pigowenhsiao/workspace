# 5 種 Agent 技能設計模式（摘要）

原文描述來源：Yanhua 的推文，聚焦於 ADK/OpenClaw 的技能設計模式與實作要點。

核心內容：介紹五種常見的設計模式，及其在 ADK / OpenClaw 生態中的應用與實作要點。

1) 工具包裝器 (Tool Wrapper)
- 讓代理在需要時動態載入特定庫的上下文
- 不把 API 慣例硬編碼到系統提示中，透過技能將約定封裝
- 範例：FastAPI 開發專家，載入 references/conventions.md 以指引實作

2) 生成器 (Generator)
- 用模板填充的方式強制輸出結構的一致性
- 使用 assets/、references/ 存放模板與風格指南
- 流程：載入風格指南、詢問缺失變量、填充文檔

3) 審核者 (Reviewer)
- 將檢查內容與檢查方法分離
- 依據 references/review-checklist.md 逐條評分、分級顯示
- 支援不同審計（如 OWASP、風格檢查）

4) 反轉 (Inversion)
- 以面試官的方式先提問，收集上下文再產出
- 關卡式指令，階段性取得所需資訊

5) 流水線 (Pipeline)
- 將代理視為狀態機，強制執行嚴格的步驟與檢查點
- 支援菱形關卡（需要用戶批准才能進入下一階段）
- 路徑：可選擇搭配 Gate、Generator、Reviewer 等模式

結論
- 這五種模式可單獨使用，也可組合使用，提升內容產出、審查與自我改進的效率。
- 在 OpenClaw 的實作中，透過 references、assets、以及 approvals 機制，可以打造穩健、可審核且可擴展的技能工作流。
