---
name: youtube-obsidian-notion-ingest
description: 將單支 YouTube 影片轉成繁體中文 Obsidian 知識筆記（含分類落檔），並同步寫入 Notion input database（Ai DataBase View）且完成寫回驗證。
---

# YouTube Obsidian Notion Ingest

## Description

把「YouTube 影片 → Obsidian 筆記 → Notion 資料庫」變成可重複執行的固定流程。

此 Skill 適用於使用者提供 YouTube 連結，並要求：

- 依既有模板整理成繁體中文知識筆記
- 放進 Vault 正確分類資料夾
- 同步上傳到 Notion input database page
- 回報可驗證結果（頁面 URL / 欄位 / heading）

## Fixed Default Targets

- Notion database: `Ai DataBase View`
- data source: `collection://6c262f43-ffdb-4b3b-b5a5-38c02ac8a2e1`
- 預設分類根：`Learning/notion-knowledge`

若使用者指定其他資料庫或 Vault 路徑，優先遵照使用者指定。

## Required Inputs

- YouTube URL
- Vault 根目錄（若未指定，使用當前專案既有 Vault）
- （可選）筆記模板檔或既有範例筆記路徑

## SOP

### Step 1: 影片資料擷取

1. 用 `yt-dlp` 取 `title/uploader/duration/upload_date/chapters`。
2. 抽 `video_id`（例如 `u_mcwbrJ45Y`）。

### Step 2: 字幕與內容來源

1. 優先抓 `zh-Hant` 字幕，次序可為：`zh-Hant -> zh-TW -> zh -> en`。
2. 若字幕不可得，改用 metadata + 章節做摘要，並標記「無字幕降級」。

### Step 3: Obsidian 筆記產出

1. 套用固定結構（繁體中文）：
   - 核心摘要
   - 影片資訊
   - 章節時間軸
   - 關鍵重點
   - 詳細分析
   - 可執行流程
   - 局限與風險
   - 實作建議
   - Source
2. 依主題分類放入 `Learning/notion-knowledge/<分類>/...`。
3. frontmatter 至少包含：
   - `title`
   - `source: youtube`
   - `source_url`
   - `video_id`
   - `processed: true`
   - `classification_path`

### Step 4: Notion 寫入（input database）

1. 先在 data source 搜尋是否已有同 URL / 同 video_id：
   - 有：update
   - 無：create
2. 寫入欄位（欄位存在才寫）：
   - `Name`, `URL`, `Website`, `文字`
   - `已下載字幕`, `已處理`
   - `Tags`, `標籤`, `內容類型`, `平台/環境`, `整合對象`（僅用既有選項）
3. 內文至少含：
   - 影片連結（可嵌入）
   - 影片摘要（5-7句）
   - 關鍵重點（>=6）
   - 方法/流程（>=5）
   - 局限與風險（>=3）
   - 實作建議（>=4）

### Step 5: 驗證（必做）

完成後 fetch 該 Notion page，確認：

- `page_id/page_url`
- 是否含 YouTube URL
- heading 清單
- 重要欄位是否寫入（至少 `已下載字幕`、`已處理`）

## Auth & Fallback

1. Notion / NotebookLM / Browser 認證失效時，先走 Cookie-first：
   - 先向使用者索取 `cookies.txt`（或等價 cookie 匯出）
   - 嘗試 cookie 恢復後再重試
2. Cookie 無效時，才走手動登入。
3. 若當前 MCP 會話授權異常，可改走 `codex exec` 備援通道執行 Notion MCP。

## Output Contract

最終回覆至少要有：

- Obsidian 筆記絕對路徑
- Notion page URL
- create 或 update
- 驗證結果摘要（欄位與 heading）
- 若用 fallback，明確標示 fallback 類型
