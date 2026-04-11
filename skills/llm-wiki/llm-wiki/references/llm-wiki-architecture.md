# LLM Wiki — Idea File

> 日期：2026-04-06
> 來源：Andrej Karpathy（Idea File）
> 標籤：#AI #Karpathy #LLM #知識庫 #Obsidian #HarnessEngineering

---

## 核心概念

大多數人使用 LLM 和文檔的方式是 RAG：上傳一堆文件，LLM 在查詢時檢索相關區塊，生成答案。這種方式有效，但 LLM 每次問題都要從頭重新發現知識——沒有累積。

**這裡的想法不同**：LLM 不是只在查詢時從原始文檔檢索，而是**增量構建和維護一個持續的 wiki**——一個結構化的、相互連結的 markdown 文件集合，介於你和原始來源之間。

當你添加一個新來源時，LLM 不只是為後續檢索做索引。它：
- 讀取內容
- 提取關鍵資訊
- 將其整合到現有 wiki
- 更新實體頁面
- 修改主題摘要
- 標記新數據何時推翻舊聲明

**知識是一次編譯，然後保持最新——不是每次查詢時重新派生。**

---

## 關鍵差異

- **Wiki 是持續的、複利的產物**——交叉引用已經存在，矛盾已經被標記，摘要已經反映了你閱讀的所有內容
- **Wiki 隨著每個添加的來源和每個問題變得越來越豐富**
- 你幾乎不親自寫 wiki——LLM 撰寫和維護所有內容
- 人類負責：策展來源、探索、引導分析、問好問題
- LLM 負責：所有其他工作——摘要、交叉引用、歸檔、簿記

**實際操作**：LLM agent 和 Obsidian 同時開啟。LLM 根據對話進行編輯，瀏覽者即時查看結果。**Obsidian 是 IDE；LLM 是程序員；wiki 是代碼庫。**

---

## 適用場景

| 場景 | 說明 |
|------|------|
| 個人 | 追蹤目標、健康、心理、自我提升——歸檔日誌、文章、Podcast 筆記，逐步建立結構化的自我畫像 |
| 研究 | 數週或數月深入一個主題——閱讀論文、文章、報告，逐步建立一個有 evolving thesis 的綜合 wiki |
| 讀書 | 每章歸檔，建立角色、主題、情節線條和它們之間連接的頁面 |
| 商業/團隊 | 內部 wiki，由 LLM 維護，來源是 Slack 對話、會議記錄、項目文檔、客戶來電 |
| 競爭分析、盡職調查、旅程規劃、課程筆記 | 任何需要隨時間累積知識並希望其有組織的場景 |

---

## 架構：三層

```
Layer 1: Raw Sources（原始來源）
  - 策展的來源文檔集合
  - 不可變——LLM 讀取但不改變
  - 這是你的真理來源

Layer 2: The Wiki（Wiki）
  - LLM 生成的 markdown 文件目錄
  - 摘要、實體頁面、概念頁面、比較、概述、綜合
  - LLM 完全擁有這層
  - 創建頁面、新來源到來時更新、維護交叉引用、保持一切一致

Layer 3: The Schema（模式/約定）
  - 一個文檔（例：CLAUDE.md 或 AGENTS.md）
  - 告訴 LLM wiki 的結構、約定是什麼、攝入來源/回答問題/維護 wiki 時要遵循的工作流程
  - **這是關鍵配置檔案**——它使 LLM 成為一個自律的 wiki 維護者，而非通用聊天機器人
  - 人類和 LLM 共同演化這個，因為你會逐步找出什麼適合你的領域
```

---

## 操作：攝入、查詢、整理

### Ingest（攝入）

你將新來源放入 raw 集合，告訴 LLM 處理它。一個典型流程：
1. LLM 閱讀來源，與你討論要點
2. 在 wiki 寫摘要頁面
3. 更新 index
4. 更新相關實體和概念頁面
5. 在日誌中追加條目

一個來源可能觸及 10-15 個 wiki 頁面。

### Query（查詢）

對 wiki 提問。LLM 搜索相關頁面，閱讀它們，用引用綜合答案。答案可以呈現不同形式——markdown 頁面、比較表、簡報（Marp）、圖表（matplotlib）、畫布。**重要洞察**：好的答案可以作為新頁面歸檔回 wiki——你的探索就像攝入的來源一樣在知識庫中複利。

### Lint（整理）

定期要求 LLM 對 wiki 進行健康檢查：
- 頁面之間的矛盾
- 被新來源取代的過時聲明
- 沒有入站連結的孤兒頁面
- 被提及但缺少自己頁面的重要概念
- 缺失的交叉引用
- 可以用網路搜索填補的數據缺口

LLM 擅長建議進一步要調查的新問題和新來源。

---

## 索引和日誌

### index.md（內容導向）

目錄——wiki 中每個頁面列出，帶連結、一行摘要、可選元數據（如日期或來源計數）。按類別組織（實體、概念、來源等）。LLM 每次攝入時更新。回答查詢時，LLM 先讀 index 找到相關頁面，再深入研究。在中等規模（~100 來源，數百頁）下效果出奇地好，**避免了对基于嵌入的 RAG 基礎設施的需求**。

### log.md（時間順序）

Append-only 的記錄——發生了什麼、何時發生。實用技巧：如果每個條目以一致的前綴開頭（如 `## [2026-04-02] ingest | Article Title`），日誌可以用簡單的 unix 工具解析——`grep "^## \[" log.md | tail -5` 給你最後 5 個條目。日誌給你 wiki 演變的時間線，並幫助 LLM 理解最近做了什麼。

---

## 可選：CLI 工具

在某些時候，你可能想構建小工具幫助 LLM 更高效地操作 wiki。最明顯的是 wiki 上的搜索引擎——在小規模時 index 文件足夠，但隨著 wiki 增長你需要適當的搜索。

[qmd](https://github.com/tobi/qmd) 是一個好選擇：這是一個本地 markdown 文件搜索引擎，帶混合 BM25/向量搜索和 LLM 重排序，全部在設備上運行。

---

## 與 OpenClaw 的關聯

- **Pigo 的 vault = LLM Wiki 架構的實際實現**
- **Obsidian = Wiki 前端**
- **Librarian skill = 自動化 URL → markdown 攝入**
- **Karpathy 的 idea file = Schema/AGENTS.md 的理論基礎**
- **持續的、被動維護的知識庫 vs 每次從頭 RAG**——這是核心差異

---

## 原文

> This document is intentionally abstract. It describes the idea, not a specific implementation. The exact directory structure, the schema conventions, the page formats, the tooling — all of that will depend on your domain, your preferences, and your LLM of choice. Everything mentioned above is optional and modular — pick what's useful, ignore what isn't.

---

*由 Librarian skill 自動歸檔*

---

## 實踐者的改造（范凱，fankaishuoai）

> 「Karpathy 的方案很優雅，但直接照搬不現實。AI 研究者 vs AI 內容創作者，需求差太遠。」

### 核心改進

1. **Query also improves the wiki** — 在查詢過程中，如果發現兩個筆記實際相關但未連結，AI 會把這個發現寫回 wiki。查詢本身就是改進知識庫的動作。

2. **工具棧綁定** — OpenClaw + Obsidian + Claude Code（不綁定特定 AI）

3. **AGENTS.md 作為 Schema** — 把操作約定寫進 AGENTS.md，讓任何新 AI 接手都能正確操作 vault

4. **log.md 格式約定** — `## [YYYY-MM-DD] <action> | <description>`，可用 `grep "^## \[" log.md | tail -5` 快速查看

### 為什麼 bookkeeping 決定成敗

> 「維護知識庫最累的不是閱讀和思考，而是記帳。」
> — Karpathy

人類擅長：讀文章、判斷價值、決定方向
LLM 擅長：整理格式、更新連結、維護索引、檢查過時

讓對的人做對的事，維護成本接近零。

---

*由 Librarian skill 自動歸檔（實踐者補充）*
