---
name: agent-create
description: |
  Agent 創建 Skill。當需要定義一個新的自訂 vault 或 workflow agent，包含明確的職責、觸發條件、邊界、和輸出契約時觸發。
  適用場景：
  - 建立新的自訂 agent
  - 定義 agent 的職責範圍
  - 設計 agent 的觸發條件
  - 建立輸出契約
  
  觸發詞：agent-create、建立 agent、新增 agent、自訂 agent
  
  注意：目前採用 planning-first 模式，適合在明確需求後建立新 agent。
---

# Agent Create Skill

## 什麼時候用

- 使用者說「幫我建立一個新的 agent」
- 使用者說「定義一個自訂的 vault agent」
- 使用者說「我需要一個新的技能，要怎麼做」
- 使用者說「設計一個專門處理 X 的 agent」

## 當前模式

本 skill 採用 **planning-first** 模式：
- 先做 role 定義
- 先做 trigger 與邊界設計
- 真正落地前，先確認是否現有 skill 已足夠

## 工作流程

### Step 1: 確認需求

向使用者確認：

```
必要：
- 這個 agent 的主要任務是什麼
- 使用場景（什麼情況觸發）

可選：
- 現有的類似 agent 或 skill
- 偏好的實作方式
```

### Step 2: 檢查現有 Skills

在建立新 agent 前，先確認現有 skill 是否已足夠：

```markdown
## 現有 Skills 檢查清單

| 任務類型 | 現有 Skill |
|---------|------------|
| [任務描述] | [檢查結果] |

如果現有 skill 足夠：
→ 建議直接使用或擴展現有 skill

如果現有 skill 不足：
→ 繼續 Step 3
```

### Step 3: 定義 Agent 規格

定義新 agent 的完整規格：

```markdown
# Agent 名稱

## 基本資訊
- **名稱**：[名稱]
- **類型**：vault/workflow
- **職責**：一句話描述這個 agent 負責什麼
- **觸發條件**：[什麼情況下觸發]

## 邊界
- **處理範圍**：[這個 agent 會處理的]
- **不處理**：[這個 agent 不會處理的]

## 輸入/輸出契約
- **輸入**：[期望的輸入格式]
- **輸出**：[期望的輸出格式]

## 實作考量
- **實作方式**：skill / agent-script / hybrid
- **依賴**：[需要的其他 skill 或工具]
```

### Step 4: 生成 Agent 檔案

根據規格生成實際檔案：

```markdown
## Agent 檔案結構

agent-name/
├── SKILL.md              # 主要定義
├── scripts/               # 脚本（如需要）
├── references/            # 參考資料（如需要）
└── test/                  # 測試（如需要）
```

### Step 5: 交付與驗證

1. 展示完整 agent 規格
2. 確認是否符合預期
3. 提供測試指引

## 常見 Agent 類型模板

### 類型 A：Vault Agent
```
職責：維護 vault 的某個部分
觸發：vault 相關請求
邊界：只處理該部分
```

### 類型 B：Workflow Agent
```
職責：執行特定工作流程
觸發：明確的工作流程請求
邊界：只執行該流程
```

## 邊界條件

| 情況 | 處理方式 |
|------|----------|
| 現有 skill 足夠 | 建議不建立新 agent |
| 需求不明確 | 先釐清需求再建立 |
| 複雜需求 | 建議拆分為多個簡單 agent |
| 類似 agent 已存在 | 建議擴展現有而非新建 |

## 示例

### 典型使用場景

**輸入：**
> 我需要一個專門處理每週總結的 agent

**輸出：**
```markdown
# Weekly Summary Agent

## 基本資訊
- **名稱**：weekly-summary
- **職責**：生成每週工作總結
- **觸發**：每週五或使用者請求

## 邊界
- 只處理週總結，不處理日/月總結
- 需要明確的週範圍

## 實作建議
- 基於現有 weekly-summary skill 擴展
- 添加 vault 整合功能
```

## 下一步

1. 確認規格是否符合需求
2. 如需要，生成實際 SKILL.md 檔案
3. 整合到 vault 或 workspace
