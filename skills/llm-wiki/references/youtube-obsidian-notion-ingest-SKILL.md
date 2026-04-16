---
name: youtube-obsidian-notion-ingest-reference
description: YouTube 來源整理為 Obsidian 筆記並視需要同步 Notion 的 reference playbook
---

# YouTube -> Obsidian -> Notion Reference

這份文件是 `llm-wiki` 的 reference playbook，用來說明 YouTube 來源如何整理進 `Pigo_Obsidian`，以及何時再同步到 Notion。

## 目的

把以下流程固定化：

- YouTube 影片
- 擷取 metadata / transcript / 摘要
- 產出繁體中文 Obsidian 筆記
- 放到正確 vault 類別
- 視需要同步到 Notion input database

## 預設落點

在目前 vault 中，YouTube 筆記的 canonical 位置是：

- `Learning/youtube/`

相關索引應同步更新：

- `Learning/youtube/index.md`
- `Learning/status/LLM-Wiki-Index.md`
- `Learning/status/LLM-Wiki-Ingest-Log.md`

## 整理模板

優先使用：

- `llm-wiki/references/pigo-note-format-notebooklm-chrome-plugins.md`

## 基本流程

### Step 1: 擷取影片資訊

至少取得：

- `title`
- `channel`
- `video_id`
- `upload_date`
- `duration`
- `url`

### Step 2: 取得可用內容

優先順序：

1. 官方字幕
2. 自動字幕
3. transcript
4. 無法取得逐字內容時，以可驗證資訊整理摘要版筆記

### Step 3: 建立 Obsidian 筆記

檔名建議：

- `YYYY-MM-DD_<Title>.md`

Frontmatter 至少包含：

- `title`
- `source: youtube`
- `source_url`
- `video_id`
- `created`
- `tags`

正文至少包含：

- `## 核心摘要`
- `## 文章分析`
- `## 關鍵知識點`
- `## 我會怎麼用這篇內容`
- `## Source`
- `## 關聯筆記`

### Step 4: 放到正確目錄

預設放到：

- `Learning/youtube/`

若內容其實更像 repo / tool profile，可在整理完成後改放：

- `Learning/repos/`

### Step 5: 更新索引

至少更新：

- `Learning/youtube/index.md`
- `Learning/status/LLM-Wiki-Index.md`
- `Learning/status/LLM-Wiki-Ingest-Log.md`

## Notion 同步規則

只有在以下情況才需要同步 Notion：

- 使用者明示要求
- 該內容本來就是要進 Notion input database 的收集流

若未被明示要求，預設先完成 Obsidian 落檔，不強制同步 Notion。

## 驗證

完成後至少確認：

1. 筆記已存在於正確路徑
2. `video_id` 與來源 URL 正確
3. 目錄索引已更新
4. 若有同步 Notion，頁面可 fetch 驗證

## 失敗時的降級策略

若遇到以下情況：

- 字幕不存在
- transcript 品質太差
- 網站或 API 無法取用

則改成：

- 保留 metadata
- 僅整理可驗證主線觀點
- 明確標示限制與缺口

不要假裝自己拿到了完整逐字內容。

## 一句話總結

YouTube 整理流程的重點不是把影片硬轉成長文，而是把可驗證的內容落到正確 vault 類別，再視需要同步到 Notion。
