---
name: brave-search
description: |
  Brave Search 網頁搜尋與內容提取 Skill。當需要搜尋文件、查詢事實、提取網頁內容、或進行任何不需要瀏覽器的網頁搜尋時觸發。
  適用場景：
  - 搜尋技術文件、API 參考
  - 查詢事實或當前資訊
  - 從特定 URL 提取內容
  - 任何需要網頁搜尋但不需要互動式瀏覽的任務
  
  觸發詞：搜尋、search、查資料、web search、找文件
  
  依賴：需要 Brave API Key（環境變數：BRAVE_API_KEY）
---

# Brave Search Skill

## 什麼時候用

- 使用者說「幫我搜尋一下這個技術的文件」
- 使用者說「查一下這個事實」
- 使用者說「把這個網頁的內容抓下來」
- 使用者說「找找看有沒有相關資訊」

## 前置設定

### 首次設定

```bash
cd ~/Projects/agent-scripts/skills/brave-search
npm ci
```

### 環境需求

需要設定環境變數：
```bash
export BRAVE_API_KEY="你的_API_Key"
```

## 搜尋指令

### 基本搜尋

```bash
# 基本搜尋（5 個結果）
./search.js "query"

# 指定結果數量
./search.js "query" -n 10

# 包含頁面內容
./search.js "query" --content

# 組合使用
./search.js "query" -n 3 --content
```

### 進階搜尋

```bash
# 只搜尋特定網域
./search.js "site:github.com query"

# 限定檔案類型
./search.js "filetype:pdf query"

# 排除特定網域
./search.js "query -site:example.com"
```

## 內容提取

### 從 URL 提取內容

```bash
./content.js https://example.com/article
```

將網頁內容以 Markdown 格式提取。

### 輸出格式

```
--- Result 1 ---
Title: 頁面標題
Link: https://example.com/page
Snippet: 搜尋結果描述

--- Result 2 ---
...
```

加上 `--content` 時：

```
--- Result 1 ---
Title: 頁面標題
Link: https://example.com/page
Snippet: 搜尋結果描述

Content:
提取的 Markdown 內容...

--- Result 2 ---
...
```

## 工作流程

### Step 1: 確認搜尋需求

```
必要：
- 搜尋關鍵字或查詢目標

可選：
- 結果數量（預設 5）
- 是否需要內容提取
- 特定網域或檔案類型
```

### Step 2: 執行搜尋

```bash
./search.js "關鍵字" -n 數量 --content
```

### Step 3: 分析結果

根據搜尋結果決定：
- 是否需要深入提取某個頁面的內容
- 是否需要進一步搜尋相關主題
- 是否已有足夠資訊

### Step 4: 提取需要的內容

```bash
./content.js 需要的_URL
```

### Step 5: 整理交付

將結果整理為結構化格式交付給使用者。

## 邊界條件

| 情況 | 處理方式 |
|------|----------|
| BRAVE_API_KEY 未設定 | 告知使用者需要設定 API Key |
| 搜尋無結果 | 嘗試不同的關鍵字或擴大範圍 |
| URL 無法訪問 | 告知「無法取得該頁面內容」 |
| API 限流 | 等待後重試，或建議降低搜尋頻率 |
| 內容提取失敗 | 使用 --content 重新嘗試 |

## 與瀏覽器的分工

| 任務 | 工具 |
|------|------|
| 快速事實查詢 | Brave Search ✅ |
| 文件搜尋 | Brave Search ✅ |
| 互動式網頁操作 | agent-browser ❌ |
| 截圖需求 | agent-browser ❌ |
| JavaScript 渲染頁面 | agent-browser ❌ |

## 示例

### 典型使用場景 1

**輸入：**
> 幫我搜尋一下 OpenAI API 的文件

**執行：**
```bash
./search.js "OpenAI API documentation" -n 5 --content
```

**輸出：**
```
--- Result 1 ---
Title: OpenAI API Reference
Link: https://platform.openai.com/docs/api-reference
Snippet: 完整的 API 參考文檔
...
```

### 典型使用場景 2

**輸入：**
> 把這個文章的內容抓下來 https://blog.example.com/ai-trends

**執行：**
```bash
./content.js https://blog.example.com/ai-trends
```

**輸出：**
```markdown
# 文章標題

文章內容以 Markdown 格式呈現...
```

## 限制說明

- 需要有效的 Brave API Key
- 每日有使用限制
- 某些網站可能有存取限制
- 內容提取效果取決於頁面結構
