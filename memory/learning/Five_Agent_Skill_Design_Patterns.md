# 每個 ADK 開發者都應了解的 5 種 Agent 技能設計模式

**來源:** Yanhua (@yanhua1010) 推文
**日期:** 2026-03-19
**標籤:** #AgentSkill #DesignPattern #ADK #GoogleADK #SKILL.md #Pipeline #Generator #Reviewer #Inversion #ToolWrapper

---

## 背景

隨著 30+ 種 Agent 工具（Claude Code、Gemini CLI、Cursor 等）統一採用相同的 SKILL.md 佈局，格式問題已不再是挑戰。真正的挑戰是**內容設計**——如何構建技能的內部邏輯。

通過研究 Anthropic、Vercel、Google 等內部指南，歸納出五種常見設計模式。

---

## 模式 1：工具包裝器 (Tool Wrapper)

**用途：** 讓 Agent 即刻成為任意函式庫的專家。

**核心思路：**
- 不把 API 慣例硬編碼進 system prompt
- 打包成技能，Agent 僅在需要時動態載入相關上下文
- 監聽用戶 prompt 中的特定關鍵詞 → 載入 `references/` 下的內部文檔

**範例：FastAPI 開發專家**

```yaml
name: api-expert
description: FastAPI 開發最佳實踐和約定。用於構建、審查或調試 FastAPI 應用時。
metadata:
  pattern: tool-wrapper
  domain: fastapi
```

**工作流：**
- 審查代碼時：載入約定 → 逐條檢查 → 引用具體規則建議修正
- 編寫代碼時：載入約定 → 嚴格遵守 → 類型註解 → 依賴注入用 Annotated 風格

---

## 模式 2：生成器 (Generator)

**用途：** 強制一致輸出結構，解決「每次生成文檔結構都不同」的問題。

**核心思路：**
- `assets/` 存放輸出模板
- `references/` 存放風格指南
- 指令充當項目經理：載入模板 → 讀取風格指南 → 詢問用戶缺失變量 → 填充文檔

**範例：技術報告生成器**

```yaml
name: report-generator
description: 生成結構化 Markdown 技術報告。
metadata:
  pattern: generator
  output-format: markdown
```

**步驟：**
1. 載入 `references/style-guide.md` 取得語氣和格式規則
2. 載入 `assets/report-template.md` 取得輸出結構
3. 詢問用戶缺失資訊（主題、關鍵發現、目標受眾）
4. 根據風格指南填充模板，每個部分必須呈現
5. 返回完整 Markdown 報告

---

## 模式 3：審核者 (Reviewer)

**用途：** 模組化代碼審查，將「檢查內容」與「檢查方法」分離。

**核心思路：**
- 評分標準存在 `references/review-checklist.md`
- Agent 載入清單 → 逐條評分 → 按嚴重等級分類
- 換掉清單（如 OWASP 安全清單代替 Python 風格清單），同一結構即可做不同審計

**範例：Python 代碼審核員**

```yaml
name: code-reviewer
description: 審核 Python 代碼的質量、風格和常見錯誤。
metadata:
  pattern: reviewer
  severity-levels: error,warning,info
```

**輸出結構：**
- **總結**：代碼功能及整體質量評估
- **問題列表**：按嚴重程度分組（error → warning → info）
- **評分**：1-10 分 + 理由
- **前三條推薦**：最具影響力的改進建議

---

## 模式 4：反轉 (Inversion)

**用途：** 顛覆「用戶提問 → Agent 回答」的動態，讓 Agent 先面試用戶再行動。

**核心思路：**
- 明確且不可折中的關卡指令：「在所有階段完成前不要開始構建」
- 按步驟問結構化問題，每問完一個等待回答
- Agent 在資訊充分前拒絕生成最終結果

**範例：項目規劃器**

```yaml
name: project-planner
description: 通過訪談收集需求，規劃新軟體項目。
metadata:
  pattern: inversion
  interaction: multi-turn
```

**階段：**
1. **問題識別**（逐一提問）：解決什麼問題？主要用戶是誰？預期規模？
2. **技術約束**（階段 1 完成後）：部署環境？技術棧？不可妥協的需求？
3. **綜合規劃**（所有問題回答完畢後）：載入模板 → 填寫 → 展示 → 迭代確認

---

## 模式 5：流水線 (Pipeline)

**用途：** 最複雜的模式。把 Agent 當狀態機，強制嚴格操作序列，每步輸出是下步必需輸入。

**核心思路：**
- 不同於普通鏈式思考，流水線有**檢查點（Gate）**
- 指令本身就是工作流定義
- 菱形關卡條件（如需用戶批准才能繼續）
- 僅在特定步驟拉取不同參考文件和模板，保持上下文窗口清晰

**範例：API 文檔生成流水線**

```yaml
name: doc-pipeline
description: 通過有門控的流水線，從 Python 源碼生成 API 文檔。
metadata:
  pattern: pipeline
```

**步驟：**
1. **提取**：掃描源碼 → 提取 docstring 和函數簽名 → 存入 `workspace/raw_data.json`
2. **驗證 🚧 關卡**：展示提取的 docstring → 問用戶「準確嗎？」→ 否則修改，是則繼續
3. **轉換**：讀取 raw_data.json + 載入模板 → 轉成 Markdown → 存入 `workspace/draft.md`
4. **校驗**：讀取 draft.md + 載入 style-guide.md → 檢查缺失描述或壞連結
5. **交付**：向用戶呈現最終 draft.md

---

## 模式組合原則

這五種模式**不互斥**，可以組合：
- 流水線末尾加**審核步驟**（Pipeline + Reviewer）
- 生成器開頭用**反轉**收集變量後再填模板（Generator + Inversion）
- ADK 的 SkillToolset + 漸進式披露 → Agent 僅消耗所需模式的上下文 token

**核心理念：** 別再把複雜脆弱的指令塞入單一 system prompt。拆解工作流，應用恰當結構模式，打造可靠的 Agent。

---

## 五種模式速查表

| 模式 | 核心動作 | 關鍵目錄 | 適用場景 |
|------|----------|----------|----------|
| Tool Wrapper | 動態載入知識 | `references/` | 框架專家、編碼規範 |
| Generator | 模板填充 | `assets/` + `references/` | 文檔生成、標準化輸出 |
| Reviewer | 清單審核 | `references/` | 代碼審查、安全審計 |
| Inversion | 先問再做 | `assets/`（模板） | 需求收集、項目規劃 |
| Pipeline | 狀態機 + 關卡 | 全部 | 多步工作流、文檔流水線 |

---

## 與 OpenClaw Skill 的對應

| 模式概念 | OpenClaw 實作 |
|----------|---------------|
| `references/` 目錄 | Skill 目錄下的參考文件 |
| `assets/` 模板 | Skill 目錄下的資產檔案 |
| 門控/關卡 | Approvals 機制 / 用戶確認 |
| 漸進式披露 | 按需載入 SKILL.md |
| 模式組合 | 多 Skill 串接或單 Skill 內分階段 |
