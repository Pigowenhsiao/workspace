---
name: llm-wiki
description: "Unified LLM Wiki ingestion orchestrator. Use when Pigo provides YouTube/X/article URLs and wants one workflow that: (1) writes to Obsidian first, (2) syncs to Notion input database, (3) updates llm-wiki index/log/cross-links, (4) commits and pushes."
---

# LLM Wiki Skill

## Description

此 Skill 是統一入口（single entrypoint）：

- 一次處理 YouTube / X / 一般文章 URL
- Step 1（最優先）：寫入 Obsidian vault
- Step 2：寫入 Notion input database
- Step 3：維護 llm-wiki 骨架（`index.md`、`log.md`、cross-links）
- Step 4：Git commit + push

## Core Principle

The vault at `/home/pigo/Documents/Pigo` is an LLM-maintained wiki.

> **別讓 AI 每次都從零開始幫你想，讓它幫你把知識攢起來。**
> — 范凱（fankaishuoai），2+ 個月 OpenClaw + Obsidian 實踐

**Human's job:** curate sources, ask good questions, think about meaning.
**LLM's job:** summarize, cross-reference, file, lint — all bookkeeping.

## Unified Entry

當使用者提供 URL 時，統一使用以下入口意圖：

`請用 llm-wiki ingest 這個連結：<URL>`

## Default Targets

- Obsidian Vault: `/home/pigo/Documents/Pigo`
- Notion database: `Ai DataBase View`（input database）
- Notion data source: `collection://6c262f43-ffdb-4b3b-b5a5-38c02ac8a2e1`

若使用者明確指定其他路徑或資料庫，優先遵照使用者指定。

## Unified Ingest Pipeline（正確順序）

### Step 1 — 來源判斷與 Obsidian 寫入（最優先）

1. **來源判斷與 metadata 萃取**
   - 辨識來源型別：YouTube / X / Article / Repo
   - 抽取最小必要 metadata（title、url、id、author、published date）

2. **寫入 Obsidian vault**
   - 寫入對應 `Learning/` 子目錄（YouTube → `youtube/`、X → `twitter/`、Article → `articles/`、Repo → `repos/`）
   - frontmatter 至少包含：`source`、`source_url`、`processed: true`、`classification_path`
   - **每篇筆記必須包含 `## 全文（繁中重寫）` 區塊**：用繁體中文將原文內容重新轉寫成流暢、可讀的段落，不可省略此區塊
   - 內容以「可重用知識」為主，同時保留全文轉寫作為背後依據
   - 先完成 Obsidian 檔案寫入與路徑確認

### Step 2 — Notion Input Database 同步

- 查重（同 URL 或同來源 ID）
- 有則 update，無則 create
- 至少回填：標題、URL、來源平台、處理狀態
- Notion page URL 取得後再繼續下一步

### Step 3 — 維護 llm-wiki 骨架

- 更新 `index.md` 對應分類入口（Sources / Entities / Concepts 適當位置）
- 補齊 related links / cross-links
- 在 `log.md` 追加一筆 ingest 記錄（append-only，格式：`## [YYYY-MM-DD] ingest | <標題>`）

### Step 4 — Git Commit + Push（最後執行）

- `git add -A`
- `git commit -m "feat: add <type> - <title>"`
- `git pull origin main --rebase`
- `git push origin main`

---

## Source Routing Rules

| Source | Delegate Skill / Method | Obsidian Destination |
|--------|------------------------|---------------------|
| YouTube URL | `youtube-obsidian-notion-ingest`（由 llm-wiki 統一編排） | `Learning/youtube/` |
| Twitter/X URL | `curl`/`jina` + llm-wiki 整理 | `Learning/twitter/` |
| Substack/News/Blog | `curl`/`web_fetch`/`jina` + llm-wiki 整理 | `Learning/articles/` |
| GitHub repo | metadata + llm-wiki 整理 | `Learning/repos/` |

---

## Query（查詢）

1. Search vault for relevant notes
2. Synthesize answer from existing notes
3. If new connections discovered during query, write them back to wiki
4. If answer is valuable, file it as a new note
5. Cite note paths

---

## Lint（健康檢查）

Periodic checks for:
- Orphan pages (no inbound links)
- Stale claims superseded by newer sources
- Missing cross-references
- Contradictions between pages
- Concepts mentioned but without their own page

---

## Schema Reference

See `references/llm-wiki-architecture.md` for Karpathy's original LLM Wiki Idea File.

See `references/agents-md-guide.md` for how to structure AGENTS.md as the wiki's schema layer.
