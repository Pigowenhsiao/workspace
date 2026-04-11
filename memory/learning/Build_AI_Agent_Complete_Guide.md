# 從零構建 AI Agent 完整指南

來源：hoeem (@hooeem) 的完整教學文章
日期：2026-03-27
標籤：#AIAgent #BuildGuide #Anthropic #OpenAI #Workflows #Tools #Memory

---

## 核心概念

**Agent 運作原理：**
- 核心循環：User input → LLM thinks → LLM decides (respond or call tool) → execute tool → feed result back → repeat
- Augmented LLM = Tools + Retrieval + Memory

**Workflows vs True Agents：**
- Workflows：確定性程式控制，便宜，適合固定步驟任務
- Agents：動態，LLM 決定下一步，適合開放任務但成本高

---

## 五個核心工作流模式

1. **Prompt Chaining**：分解任務為順序步驟，每步處理上一步輸出
2. **Routing**：分類輸入，導向專門處理器
3. **Parallelisation**：同時運行多個 LLM 呼叫
4. **Orchestrator-workers**：中央 LLM 動態分解任務委派子任務
5. **Evaluator-optimiser**：生成輸出 → 評估 → 反饋 → 循環直到達標

---

## 構建 Agent 的四個問題

1. **Outcome**：最終產出是什麼？
2. **Information**：需要什麼資訊（網路/文件/數據庫）？
3. **Actions**：允許什麼操作（讀/寫/搜尋/執行）？
4. **Rules**：必須遵守什麼規則？

**公式：** Agent = Role + Goal + Tools + Rules + Output format

---

## 五種入門 Agent 類型

1. **Research Agent**：蒐集資訊並總結
2. **Content Agent**：寫作/重寫/摘要內容
3. **Workflow Agent**：重複性業務流程
4. **Personal Knowledge Agent**：用戶文檔問答（RAG）
5. **Operator Agent**：在環境中執行操作（讀寫文件/執行命令）

---

## 工具使用原則

- **少即是多**：好工具 > 多工具
- **工具職責單一**：一個工具做一件事
- **明確使用時機**：告訴 Agent 何時使用工具

---

## 記憶系統

- **Short-term**：對話歷史（預設）
- **Long-term**：外部知識（RAG）

大部分場景不需要複雜記憶，從簡單開始。

---

## 測試與調優

- 用真實 messy 輸入測試
- 一次只修復一個問題
- 先建立單一 Agent，再擴展到多 Agent

---

## 與 OpenClaw 對應

- **Workflow 模式** → Pipeline / Generator Skill
- **工具定義** → SKILL.md 的 tools 描述
- **系統提示分段** → 分離 static/dynamic blocks 優化快取
- **權限管理** → Approvals 與 Hook

---

## 下一步

- 可將此框架應用於 OpenClaw 的 Skill 設計
- 參考：memory/learning/Five_Agent_Skill_Design_Patterns.md