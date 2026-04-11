# Agent Skill 設計模式：Pipeline（流水線）模式

**來源:** Pigo 分享之文章
**日期:** 2026-03-19
**標籤:** #AgentSkill #Pipeline #DesignPattern #ADK #GoogleADK

---

## 核心概念

用**有門控 (Gated) 的流水線**拆解複雜工作流，每一步有明確輸入/輸出，關鍵步驟設「關卡」讓人類審核，避免把所有邏輯塞進單一 system prompt。

---

## 範例：從 Python 源碼生成 API 文檔

### 角色定義
```yaml
description: 通過有門控的流水線，從 Python 源碼生成 API 文檔。
metadata:
  pattern: pipeline
```

### 流水線步驟

| 步驟 | 名稱 | 動作 | 輸出 |
|------|------|------|------|
| 1 | 提取 | 掃描源碼，提取所有 docstring 和函數簽名 | `workspace/raw_data.json` |
| 2 | 驗證 **🚧 關卡** | 向用戶展示提取的 docstring，問「描述準確嗎？」否→修改，是→繼續 | 用戶確認 |
| 3 | 轉換 | 讀取 raw_data.json + 載入 `assets/doc-template.md` 模板 → 轉成 Markdown | `workspace/draft.md` |
| 4 | 校驗 | 讀取 draft.md + 載入 `references/style-guide.md` → 檢查缺失描述或壞連結 | 校驗報告 |
| 5 | 交付 | 向用戶呈現最終 draft.md | 完成 |

---

## 關鍵設計原則

### 門控 (Gate)
- 在關鍵步驟設置人類審核點
- 用戶否定 → 回到修改步驟
- 用戶肯定 → 繼續下一步
- 防止錯誤累積到最終輸出

### 模式可組合
- **Pipeline + 審核步驟**：流水線末尾加自檢（self-review）
- **Generator + 反轉模式**：生成器開頭先用反轉（inversion）收集變量，再填模板
- 模式之間不互斥，靈活搭配

### 上下文效率
- ADK 的 SkillToolset + 漸進式披露（Progressive Disclosure）
- Agent 在運行時僅消耗所需模式的上下文 token
- 不把複雜指令塞入單一 system prompt

---

## 實踐要點

1. **拆解工作流** — 別用一個巨大 prompt 做所有事
2. **應用結構模式** — Pipeline / Generator / Reviewer 等
3. **設置關卡** — 關鍵步驟讓人類確認
4. **明確輸入輸出** — 每步有明確的檔案路徑與格式
5. **組合使用** — 根據需求混搭不同模式

---

## 與 OpenClaw 的對應

| Pipeline 概念 | OpenClaw 對應 |
|---------------|---------------|
| 步驟拆解 | Skill 內的分階段工作流 |
| 門控/關卡 | Approvals 機制 |
| 模板載入 | Skill 內的 assets/ 目錄 |
| 漸進式披露 | 按需載入 SKILL.md |
| 自檢步驟 | Self-Improving Skill |
