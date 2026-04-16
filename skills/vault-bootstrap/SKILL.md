---
name: vault-bootstrap
description: |
  Vault 初始化 Skill。當需要為一個新專案、工作空間、或知識庫進行初始結構建立，或需要重建 vault 架構時觸發。
  適用場景：
  - 新しい專案啟動，需要建立 vault 結構
  - 現有 vault 混亂，需要重建組織架構
  - 建立新的知識庫起點
  - 規劃新的筆記分類系統
  
  觸發詞：初始化 vault、新建 vault、重建結構、vault 設定、vault 架構
  
  注意：本 skill 只做結構規劃，不處理實際內容搬遷。
---

# Vault Bootstrap Skill

## 什麼時候用

- 使用者說「幫我建立一個新的 vault 結構」
- 使用者說「我的 vault 很亂，幫我重新整理」
- 使用者說「為這個專案建立一個 vault」
- 使用者說「規劃一下我的筆記分類方式」

## 工作流程

### Step 1: 確認需求

向使用者確認：

```
必要：
- vault 類型（個人知識庫、專案管理、工作空間、團隊協作）
- 主要領域或用途
- 是否需要從現有 vault 遷移

可選：
- 預期筆記數量
- 團隊人數（如果是協作用途）
- 是否需要標籤系統
```

### Step 2: 分析與規劃結構

根據需求規劃 vault 結構：

```markdown
## 規劃維度

### 入口結構
- index.md（總覽）
- Inbox（收集點）

### 主要分類方式（選擇一種或混合）
1. 按領域：工作、學習、個人
2. 按專案：每個專案一個目錄
3. 按時間：年度 > 月度
4. 按類型：筆記、資料、模板

### 元資料系統
- 標籤策略
- 連結策略（雙向連結）
- 命名規範
```

### Step 3: 生成結構規劃

```markdown
# Vault 結構規劃 [用途]

## 頂層結構
vault/
├── 00-Inbox/          # 收集點，所有新筆記先放這裡
├── 01-Projects/      # 專案目錄
├── 02-Areas/         # 責任領域
├── 03-Resources/    # 資源參考
├── 04-Archives/      # 歸檔（不活躍的內容）
├── index.md           #  vault 總覽
├── daily/             # 每日筆記（可選）
└── _templates/       # 模板檔案（可選）

## 各目錄用途

### 00-Inbox
- 所有新建筆記的起點
- 每天的收集點
- 定期整理到其他目錄

### 01-Projects
- 每個專案一個子目錄
- 結構：index + 相關筆記

### 02-Areas
- 持續進行的責任領域
- 例如：工作、學習、健康、財務

### 03-Resources
- 永久參考資料
- 不屬於特定專案的知識

### 04-Archives
- 已完成的專案
- 不再活躍的領域
```

### Step 4: 創建實際結構

在確定的位置建立目錄結構：

```bash
mkdir -p vault/00-Inbox
mkdir -p vault/01-Projects
mkdir -p vault/02-Areas
mkdir -p vault/03-Resources
mkdir -p vault/04-Archives
mkdir -p vault/_templates
touch vault/index.md
```

### Step 5: 建立核心檔案

#### index.md
```markdown
# [Vault 名稱]

## vault 目標
[一句話描述 vault 的用途]

## 結構
- [[00-Inbox]] - 收集點
- [[01-Projects]] - 專案
- [[02-Areas]] - 領域
- [[03-Resources]] - 資源
- [[04-Archives]] - 歸檔

## 最近更新
<!-- 最近更新的筆記連結 -->

## 待整理
<!-- inbox 中等待整理的筆記 -->
```

#### Inbox index
```markdown
# Inbox

所有新建筆記的起點。

## 規則
1. 新筆記先放在這裡
2. 每天或每週整理一次
3. 整理時移動到正確位置並加入連結

## 最近筆記
<!-- 自動列表或手動維護 -->
```

### Step 6: 交付與說明

展示：
1. 建立的目錄結構
2. 每個目錄的用途說明
3. 使用規範（如有）
4. 下一步建議

## vault 類型模板

### 類型 A：個人知識庫
```
Personal/
├── 00-Inbox/
├── 01-Learning/      # 學習筆記
├── 02-Work/          # 工作筆記
├── 03-Life/          # 生活記錄
├── 04-Archives/
└── _templates/
```

### 類型 B：專案管理
```
Projects/
├── 00-Inbox/
├── [Project-A]/
│   ├── index.md
│   ├── notes/
│   └── resources/
├── [Project-B]/
└── _templates/
```

### 類型 C：工作空間
```
Workspace/
├── 00-Inbox/
├── 01-Daily/         # 每日工作記錄
├── 02-Projects/     # 所有專案
├── 03-Meetings/     # 會議記錄
├── 04-Templates/
└── 05-Archives/
```

## 邊界條件

| 情況 | 處理方式 |
|------|----------|
| 現有 vault 要遷移 | 先規劃新結構，再建議遷移策略（不執行實際搬遷） |
| vault 已存在 | 確認是否要覆蓋，還是只在現有結構上補充 |
| 多人協作需求 | 明確區分個人區域和共用區域 |
| 筆記數量龐大 | 分階段建立，先建立核心結構 |
| 需要導入既有筆記 | 先規劃分類策略，不立即執行搬遷 |

## 示例

### 典型使用場景

**輸入：**
> 幫我建立一個新的知識庫 vault

**規劃輸出：**
```markdown
# 新個人知識庫結構

## 選擇的結構
按領域分類

## 建立的目錄
vault/
├── 00-Inbox/
├── 01-Domain/          # 領域研究
│   ├── AI/
│   ├── Product/
│   └── Business/
├── 02-Projects/        # 專案
├── 03-Notes/           # 零散筆記
├── 04-Archives/        # 歸檔
└── _templates/
```

## 後續建議

1. **設定標籤系統**（使用 tag-check skill）
2. **建立模板**（meeting note template, daily template 等）
3. **制定整理習慣**（每天整理一次 inbox）
4. **培訓團隊成員**（如果適用）

## 限制說明

- 本 skill 只建立結構，不處理內容遷移
- 不執行實際的檔案搬遷操作
- 建議搭配 vault-deep-clean 做定期維護
