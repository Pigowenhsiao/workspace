---
name: setup
description: |
  專案設定 Skill。當需要為 Compound Engineering 工作流程配置專案級別設定，或需要了解當前設定狀態時觸發。
  適用場景：
  - 初始化新專案的設定
  - 檢視現有專案設定
  - 調整工作流程配置
  - 多人協作的專案配置
  
  觸發詞：專案設定、setup、專案配置、專案初始化
  
  注意：目前 review agent 選擇已由 `ce:review` skill 自動處理。
---

# Setup Skill

## 什麼時候用

- 使用者說「幫我設定這個專案」
- 使用者說「這個專案的設定是什麼」
- 使用者說「初始化一個新專案」
- 使用者說「更新專案配置」

## 工作流程

### Step 1: 確認專案類型

```
必要：
- 專案名稱/路徑
- 專案類型（Web / API / CLI / 函式庫）

可選：
- 技術棧（Node / Python / Rust 等）
- 團隊規模
- 現有設定檔案
```

### Step 2: 檢視現有設定

檢查專案根目錄的設定檔：

```bash
# 檢查常見設定檔
ls -la *.json *.yaml *.toml .env* 2>/dev/null
ls -la CLAUDE.md AGENTS.md .claude 2>/dev/null
```

### Step 3: 根據類型配置

#### 類型 A：Node.js 專案

```json
{
  "name": "project-name",
  "scripts": {
    "dev": "...",
    "build": "...",
    "test": "..."
  }
}
```

#### 類型 B：Python 專案

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.black]
line-length = 88
```

#### 類型 C：Rust 專案

```toml
[package]
name = "project-name"
version = "0.1.0"

[dependencies]
```

### Step 4: 建立設定檔

根據檢查結果建立必要的設定檔：

```markdown
## 已建立/更新的設定檔

| 檔案 | 用途 |
|------|------|
| CLAUDE.md | Agent 專案說明 |
| .env.example | 環境變數範本 |
| package.json | Node.js 設定 |

## 建議的下一步

1. 執行 `ce:review` 檢視初始設定
2. 建立 CLAUDE.md 說明專案目標
3. 設定環境變數
```

## 邊界條件

| 情況 | 處理方式 |
|------|----------|
| 專案已有很多設定 | 只補充缺少的部分 |
| 新專案 | 建立完整設定結構 |
| 設定衝突 | 指出衝突讓使用者選擇 |

## 示例

### 典型使用場景

**輸入：**
> 幫我初始化這個 Node.js 專案

**輸出：**
```markdown
## 初始化結果

已建立：
- package.json（含基本 scripts）
- .env.example
- CLAUDE.md

建議下一步：
- npm install
- 建立 src/ 目錄
- 設定 TypeScript（如需要）
```
