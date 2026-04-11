# 一人公司 (OPC) 必備的 9 個 Agent Skills

**來源:** Sahil Lavingia (@shl, Gumroad 創辦人) 開源專案
**日期:** 2026-03-26
**標籤:** #OPC #OnePersonCompany #AgentSkills #MinimalistEntrepreneur #ClaudeCode #Startup
**GitHub:** https://github.com/slavingia/skills

---

## 背景

Sahil Lavingia 把他的書《The Minimalist Entrepreneur》中的極簡創業哲學，封裝成 9 個可互動的 Agent Skills，讓 AI Agent 變成你的創業教練。

每個 Skill 的實現方式高度一致：
- `skills/` 目錄下一個子資料夾
- 內含 `SKILL.md`（YAML 前置元資料 + 結構化 system prompt）
- 指導 Agent 扮演「極簡創業哲學顧問」

---

## 9 個 Skills 速查表

| Skill | 指令 | 用途 | 階段 |
|-------|------|------|------|
| Find Community | `/find-community` | 尋找商業想法、定位社區 | 0→1 構想 |
| Validate Idea | `/validate-idea` | 測試想法是否值得推進 | 0→1 驗證 |
| MVP | `/mvp` | 構建第一款產品、控制範圍 | 0→1 構建 |
| First Customers | `/first-customers` | 獲取前 100 名用戶 | 1→10 獲客 |
| Pricing | `/pricing` | 定價策略與調整 | 1→10 變現 |
| Marketing Plan | `/marketing-plan` | 產品市場契合後，通過內容規模化 | 10→100 行銷 |
| Grow Sustainably | `/grow-sustainably` | 支出、招聘、擴張決策 | 10→100 成長 |
| Company Values | `/company-values` | 定義文化、準備招聘 | 10→100 組織 |
| Minimalist Review | `/minimalist-review` | 對任何商業決策進行極簡復盤 | 全階段通用 |

---

## `/find-community` 範例解析

SKILL.md 的結構：
- **核心原則：** 先找社區，再找問題，而非先想產品
- **框架：** 4 個引導問題 + 4 項評估標準
- **反模式警示：** 避免常見陷阱
- **輸出模板：** 社區、痛點、用戶連接度、聚集地

這個模式就是典型的 **Inversion（反轉）模式**——Agent 先問你問題，收集足夠上下文後才給建議。

---

## 設計模式對應

| OPC Skill | 對應設計模式 | 說明 |
|-----------|-------------|------|
| `/find-community` | Inversion（反轉） | 先問再答，收集上下文 |
| `/validate-idea` | Reviewer（審核者） | 用清單逐項評估想法 |
| `/mvp` | Generator（生成器） | 用模板產出 MVP 規劃 |
| `/first-customers` | Pipeline（流水線） | 分步驟獲客流程 |
| `/pricing` | Tool Wrapper（工具包裝器） | 載入定價框架做分析 |
| `/marketing-plan` | Generator + Pipeline | 模板 + 分階段執行 |
| `/grow-sustainably` | Reviewer | 用標準評估每筆支出 |
| `/company-values` | Inversion | 先問價值觀再產出文件 |
| `/minimalist-review` | Reviewer | 通用決策復盤清單 |

---

## 核心啟發

### 1. Skill = 書本知識的可執行版本
把書裡的框架變成 Agent 可執行的 prompt，不只是「記住」，而是「會用」。

### 2. 極簡結構，高度可複製
每個 Skill 只有一個 SKILL.md，YAML + prompt，沒有複雜程式碼。任何人都能照著做。

### 3. 階段化設計
9 個 Skill 覆蓋從構想到成長的完整創業旅程，每個階段有明確的輸入/輸出。

### 4. 反模式警示是關鍵
不只告訴 Agent「該做什麼」，也告訴它「不該做什麼」。這就是之前讀到的「捕捉坑點」原則。

---

## 與 OpenClaw 的實作對應

| OPC 概念 | OpenClaw 對應 |
|----------|---------------|
| `skills/` 目錄 | `~/.openclaw/workspace/skills/` |
| SKILL.md（YAML + prompt） | OpenClaw SKILL.md 格式 |
| 觸發詞匹配 | description 欄位的觸發條件 |
| 反轉式提問 | Inversion 模式 |
| 決策復盤 | Reviewer 模式 + Approvals |
| 階段化流程 | Pipeline + Gate |

---

## 連結到相關筆記

- 設計模式詳解 → memory/learning/Five_Agent_Skill_Design_Patterns.md
- Pipeline 模式 → memory/learning/Agent_Skill_Pipeline_Pattern.md
- Claude Skills 最佳實踐 → memory/learning/Claude_Code_Skills_Best_Practices.md
- gstack 工程團隊模式 → memory/learning/OpenClaw_Gstack_Link.md
- 三層記憶模型 → memory/learning/OpenClaw_Three_Tier_Memory.md

---

## 行動項目

- [ ] 評估哪些 OPC Skill 可直接移植到 OpenClaw
- [ ] 用 `/minimalist-review` 的結構做一個通用的「決策復盤 Skill」
- [ ] 把 `/find-community` 的 Inversion 模式套用到其他需求收集場景
