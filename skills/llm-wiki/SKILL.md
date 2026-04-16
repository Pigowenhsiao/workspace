---
name: llm-wiki
description: "在 Pigo_Obsidian 中維護可持續累積的 markdown 知識庫。llm-wiki 只保留 runtime 與 references，正式內容一律寫入既有 vault 結構。"
version: 2.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, notes, markdown, obsidian]
    category: research
    related_skills: [note-update, inbox-check, vault-check]
    config:
      - key: wiki.path
        description: Path to the active vault root
        default: "~/Pigo_Obsidian"
        prompt: Vault root path
---

# LLM Wiki for Pigo_Obsidian

在這個 workspace 中，`llm-wiki` 不是內容主樹，而是 runtime package。

- `llm-wiki/` 只保留 `SKILL.md` 與 `references/`
- 正式知識內容必須落到現有 vault 結構
- 所有輸出內容一律使用繁體中文

## 何時使用

當使用者要你做以下事情時使用這個 skill：

- 整理外部來源進 vault
- 把文章、影片、repo、工具整理成可持續更新的知識筆記
- 查詢既有學習內容並做交叉整理
- 檢查 llm-wiki 輸出是否放錯位置
- 整理 `Learning` 區的 AI / 工具 / repo / 影片知識

## 本 workspace 的硬規則

### 1. `llm-wiki/` 不是內容目錄

`llm-wiki/` 只用來放：

- `SKILL.md`
- `references/`

不得再把正式內容寫入以下舊位置：

- `llm-wiki/index.md`
- `llm-wiki/log.md`
- `llm-wiki/entities/`
- `llm-wiki/00-Inbox/`

### 2. 正式內容的 canonical 目的地

依來源類型落到現有結構：

- 文章 / paper / 網頁整理 -> `Learning/articles/`
- YouTube / video 筆記 -> `Learning/youtube/`
- 工具 / repo / project / entity-style note -> `Learning/repos/`
- LLM-Wiki 索引與 ingest 歷史 -> `Learning/status/`
- 尚未整理完成的暫存來源 -> `00-Inbox/`

### 3. 導覽檔案

本 workspace 的 llm-wiki 主要導覽點是：

- `Learning/index.md`
- `Learning/status/LLM-Wiki-Index.md`
- `Learning/status/LLM-Wiki-Ingest-Log.md`

必要時再同步更新：

- `Learning/articles/index.md`
- `Learning/youtube/index.md`
- `Learning/repos/index.md`
- `Learning/status/index.md`

## Session 開始時的檢查

在做 ingest、query、lint 之前，先讀：

1. `Learning/index.md`
2. `Learning/status/LLM-Wiki-Index.md`
3. `Learning/status/LLM-Wiki-Ingest-Log.md` 的最近幾筆

目的：

- 避免重複建檔
- 避免把內容寫回舊 `llm-wiki/` 骨架
- 先理解目前索引與分類習慣

## 筆記格式

整理文章、影片、網頁、repo 或工具時，優先參考：

- `llm-wiki/references/pigo-note-format-notebooklm-chrome-plugins.md`

至少要保留：

- 清楚標題
- 可追溯來源
- 核心摘要
- 關鍵知識點
- 與現有筆記的關聯

Frontmatter 至少應包含常見欄位：

- `title`
- `source`
- `source_url`
- `created`
- `type`
- `tags`

## Ingest Workflow

當使用者提供 URL、文章、影片、repo、工具說明或貼上內容時：

1. 先判斷來源類型
2. 決定 canonical 目的地
3. 搜尋既有 `Learning` 內容，避免重複建檔
4. 建立或更新對應筆記
5. 補上 wikilinks 與必要索引
6. 更新：
   - `Learning/status/LLM-Wiki-Index.md`
   - `Learning/status/LLM-Wiki-Ingest-Log.md`

### 類型對應

- article / paper / blog / thread 整理 -> `Learning/articles/`
- YouTube / transcript / video note -> `Learning/youtube/`
- GitHub repo / CLI tool / framework / product profile -> `Learning/repos/`

### 暫存例外

只有在以下情況才先放 `00-Inbox/`：

- 來源不完整
- 還無法確定分類
- 使用者明示先暫存不要正式歸檔

一旦內容已整理完成，應移出 `00-Inbox/`。

## Query Workflow

當使用者問問題且答案應來自既有 llm-wiki / Learning 內容時：

1. 先查 `Learning/status/LLM-Wiki-Index.md`
2. 再查相關目錄：
   - `Learning/articles/`
   - `Learning/youtube/`
   - `Learning/repos/`
3. 讀取相關筆記並整合回答
4. 若這次回答本身值得保存，再寫回既有類別，而不是新建獨立 `queries/` 目錄

## Lint / Health Check Workflow

當使用者要你檢查 llm-wiki 結構時，重點不是檢查 `llm-wiki/` 底下有多少內容，而是檢查：

- 是否還有正式內容誤放在 `llm-wiki/`
- `Learning` 內容是否有壞連結
- `LLM-Wiki-Index` 是否落後
- `LLM-Wiki-Ingest-Log` 是否缺漏
- `Learning/articles`、`Learning/youtube`、`Learning/repos` 是否有明顯錯放

### 在這個 workspace 中，以下都視為結構錯誤

- 新內容被寫到 `llm-wiki/index.md`
- 新內容被寫到 `llm-wiki/log.md`
- 新內容被寫到 `llm-wiki/entities/`
- 新內容被寫到 `llm-wiki/00-Inbox/` 且沒有後續回收
- 內容仍連到不存在的 `Learning/papers/` 或 `Learning/videos/`

## 與其他 skill 的邊界

- 單篇既有筆記升級、補分類、微調 -> 優先考慮 `note-update`
- 批次整理 `00-Inbox` -> 優先考慮 `inbox-check`
- 全 vault 健檢 -> 優先考慮 `vault-check`
- 本 skill 負責的是：把外部來源或 llm-wiki 流程整理進正確的知識骨架

## 更新後必做

每次完成 llm-wiki 相關修改後，至少驗證：

1. 新筆記落在正確目錄
2. 沒有把內容寫回 `llm-wiki/`
3. `Learning/status/LLM-Wiki-Index.md` 已更新
4. `Learning/status/LLM-Wiki-Ingest-Log.md` 已更新
5. 相關 index 或 landing page 沒有壞連結

## 禁止事項

- 不要把 `llm-wiki/` 當成內容主樹
- 不要再創建新的 `llm-wiki/entities/`、`concepts/`、`comparisons/`、`queries/`
- 不要再使用 `Learning/papers/` 或 `Learning/videos/` 這種當前不存在的舊分類
- 不要跳過 index / log 更新

## 一句話原則

在 `Pigo_Obsidian` 中，`llm-wiki` 是整理流程，不是內容目的地；正式內容一律回收到 `Learning` 與既有 vault 骨架。
