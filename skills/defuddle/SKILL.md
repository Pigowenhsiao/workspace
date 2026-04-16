---
name: defuddle
description: |
  Defuddle 網頁內容提取 Skill。當需要從網頁提取乾淨的可讀內容、移除廣告和干擾元素、節省 token 使用時觸發。
  適用場景：
  - 從複雜網頁提取乾淨內容
  - 處理文章、部落格、文件等標準備頁面
  - 清理網頁內容以便進一步分析
  
  觸發詞：defuddle、抓網頁、清理內容、URL轉文字
  
  安裝：`npm install -g defuddle`
---

# Defuddle Skill

## 什麼時候用

- 使用者提供 URL 並說「幫我抓這個頁面的內容」
- 需要處理複雜網頁（帶廣告、導航欄）
- 需要乾淨的 Markdown 格式輸出
- 網址不是 .md 結尾的文件頁面

## 工作流程

### Step 1: 確認 URL

```
必要：
- 目標 URL

確認：
- 是否需要標題、描述等元資料
- 是否需要輸出到檔案
```

### Step 2: 執行提取

```bash
# 基本提取（Markdown 格式）
defuddle parse <url> --md

# 提取並保存到檔案
defuddle parse <url> --md -o content.md

# 只提取標題
defuddle parse <url> -p title

# 只提取描述
defuddle parse <url> -p description
```

### Step 3: 分析結果

檢查提取的內容：
- 是否完整
- 是否需要進一步處理
- 是否需要標題或結構調整

### Step 4: 交付

```markdown
# [頁面標題]

[提取的乾淨內容]
```

## 參數說明

| 參數 | 說明 |
|------|------|
| `--md` | 輸出 Markdown 格式（建議使用） |
| `-o <file>` | 輸出到指定檔案 |
| `-p <field>` | 只提取特定欄位（title, description, author, date） |

## 邊界條件

| 情況 | 處理方式 |
|------|----------|
| 頁面需要登入 | 告知「無法提取需要登入的內容」 |
| 頁面無內容 | 嘗試使用 WebFetch 作為備用 |
| URL 是 .md 檔案 | 直接使用 WebFetch，不使用 Defuddle |
| 提取失敗 | 檢查 URL 是否有效，嘗試其他方式 |

## 與 WebFetch 的分工

| 場景 | 工具 |
|------|------|
| 複雜網頁（帶廣告、干擾） | Defuddle ✅ |
| 簡單文章、部落格 | Defuddle ✅ |
| 標準備頁面文件 | Defuddle ✅ |
| .md 檔案 URL | WebFetch ✅ |
| 需要登入的內容 | 皆無法處理 |

## 示例

### 典型使用場景

**輸入：**
> 把這個文章的內容抓下來 https://blog.example.com/ai-post

**執行：**
```bash
defuddle parse https://blog.example.com/ai-post --md -o content.md
```

**輸出：**
```markdown
# AI 驅動的未來

文章內容，乾淨無廣告...
```
