---
name: ui-design-system
description: |
  UI 設計系統 Skill。當需要建立設計系統、維護視覺一致性、生成設計令牌（Design Tokens）、或進行設計開發交接時觸發。
  適用場景：
  - 建立新的設計系統
  - 生成色彩、字體間距令牌
  - 建立元件庫文檔
  - 響應式設計計算
  - 設計開發交接文檔
  
  觸發詞：設計系統、design system、UI tokens、色彩系統、響應式設計
---

# UI Design System Skill

## 什麼時候用

- 使用者說「幫我建立一個設計系統」
- 使用者說「生成設計令牌」
- 使用者說「這個元件的文檔」
- 使用者說「響應式設計 breakpoints」
- 使用者說「設計開發交接資料」

## 工作流程

### Step 1: 確認需求

```
必要：
- 專案類型（Web / Mobile / 兩者）
- 主要用途（內部工具 / 公開產品）

可選：
- 品牌色彩
- 現有設計檔案
- 技術棧（React / Vue / iOS / Android）
```

### Step 2: 設計令牌生成

使用 `design_token_generator.py`：

```bash
# 基本令牌生成
python scripts/design_token_generator.py "#3B82F6" modern css

# 生成所有格式
python scripts/design_token_generator.py "#3B82F6" modern json,css,scss

# 自訂風格
python scripts/design_token_generator.py "#品牌色" classic scss
```

### Step 3: 建立元件文檔

```markdown
# 元件名稱

## 規格
| 狀態 | 尺寸 | 說明 |
|------|------|------|
| Default | 40x40px | 標準狀態 |
| Hover | 44x44px | 放大效果 |
| Disabled | 40x40px | 灰階顯示 |

## 使用範例
[插入程式碼範例]

## 設計標記
[標記的位置、大小、間距]
```

### Step 4: 響應式設計定義

```markdown
## 響應式 Breakpoints

| 名稱 | 範圍 | 設計寬度 |
|------|------|----------|
| Mobile | < 768px | 375px |
| Tablet | 768-1024px | 768px |
| Desktop | 1024-1440px | 1024px |
| Large | > 1440px | 1440px |

## 間距系統
基於 8pt 網格：
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px
```

## 核心功能

| 功能 | 說明 |
|------|------|
| 設計令牌生成 | 色彩、字體、間距 |
| 元件系統架構 | 結構化元檔案 |
| 響應式計算 | Breakpoints、間距 |
| 無障礙合規 | WCAG 標準 |
| 開發交接文檔 | 設計標記、程式碼 |

## 邊界條件

| 情況 | 處理方式 |
|------|----------|
| 無品牌色彩 | 使用預設色彩系統 |
| 需要特定框架 | 調整輸出格式 |
| 缺少設計檔案 | 提供基本結構模板 |
