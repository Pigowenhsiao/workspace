# OpenClaw 三層記憶模型與外部知識庫架構

**來源:** Pigo 分享之文章
**日期:** 2026-03-19
**標籤:** #OpenClaw #MemoryModel #MCP #KnowledgeBase #Agent

## 核心概念
將 OpenClaw 不僅視為聊天機器人，而是視為**多 Agent 共享的外接知識庫**。透過 MCP 協議連接外部筆記工具（如網易有道雲筆記），實現記憶的雲端化與流動性。

## 三層記憶模型 (The Three-Tier Memory Model)

建立在 OpenClaw 內部的分層結構：

### Tier 1: 信息層 (Information)
- **內容:** 原始記錄、學習筆記、對話記錄、網頁剪藏。
- **位置:** `memory/learning/` (目錄)
- **策略:** 只追加不刪除，按需檢索。
- **作用:** 原始素材庫。

### Tier 2: 知識層 (Knowledge)
- **內容:** 每日提煉的工作日誌、重要決策、結構化後的知識點。
- **位置:** `memory/YYYY-MM-DD.md` (每日記憶檔)
- **策略:** 每日更新，由 Agent (如 `youdaonote-news` skill) 主動加工提煉。
- **作用:** 階段性總結，具備時效性與關聯性。

### Tier 3: 智慧層 (Wisdom)
- **內容:** 跨領域洞察、底層規律、核心方法論 (Core Methodology)。
- **位置:** `MEMORY.md`
- **策略:** 控制在 100-200 行以內，每次 Session 都能加載。
- **作用:** Agent 的長期記憶與「性格/大腦」。

## 認知升級與實踐

### 1. 從本地記憶到雲端知識中台
- **問題:** 本地記憶換設備即斷片，Agent 間無法共享。
- **解法:** 使用 MCP 協議 (如 `youdaonote-clip`) 將 Tier 1 素材實時同步至雲端筆記。
- **效果:** Telegram 收集、Cursor 寫代碼調用、Claude 規劃產品，皆可訪問同一套知識庫。

### 2. 從被動存儲到主動加工
- **工具:** 使用具備加工能力的 Skill (如 `youdaonote-news`)。
- **流程:** 
  1. 提取核心觀點。
  2. 補充行業最新動態。
  3. 輸出結構化筆記 (Tier 2)。
  4. 若涉及核心概念，主動關聯至 Tier 3。
- **價值:** 知識庫具備自我進化能力。

### 3. 從單點工具到系統基礎設施
- **整合:** OpenClaw 作為中樞，連接 3200+ MCP Skills。
- **自動化工作流範例:**
  - 收集 (Telegram) -> 歸檔 (Tier 1)
  - 整理 (OpenClaw 读取 Tier 2) -> 推送日報 (WhatsApp)
  - 應用 (Cursor) -> 調取方法論 (Tier 3) -> 解決報錯
- **終極意義:** 知識資產私有化且可攜（Portable）。不依賴特定 Agent 框架，經驗沉淀為可複用的基礎設施。