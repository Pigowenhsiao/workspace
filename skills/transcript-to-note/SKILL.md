---
name: transcript-to-note
description: Use when the user has transcript text, meeting notes, lecture transcripts, podcast transcripts, or transcript-like material that should be turned into a structured Obsidian note before later filing or formalization.
---

# Transcript To Note

## Description

`transcript-to-note` 是 transcript intake skill。  
它把逐字稿、會議轉寫、課程 transcript、podcast transcript 或 transcript-like text 轉成結構化 Obsidian 筆記初稿，之後再交給 `note-update` 或 `inbox-triage` 進一步正式化與歸檔。

## When to Use

使用時機：

- 使用者已經有 transcript text
- 你要把會議、講座、podcast、訪談轉成可整理筆記
- 需要先抽出決策、行動項、關鍵知識點，再決定要不要正式歸檔

不要用在：

- 只有 raw audio 且沒有可讀文字時，這個 skill 不做原始語音辨識
- 已經是成熟正式筆記時，改用 `note-update`
- 只是要做整體分類搬移時，改用 `vault-reshape`

## Vault Index Usage

在轉寫內容進 note 之前，先用 vault index 查是否已有同主題或同來源正式頁，避免生成完全脫節的新草稿。

- Vault root：
  `/home/pigo/Documents/Pigo_Obsidian`
- Query tool：
  使用 `rg` 或 Obsidian CLI

優先查這些：

- `fts`
- `title-candidates`
- `related-notes`
- `by-classification`

## Intake Workflow

### 1. Source Gate

先分辨：

- 是否已有 transcript text
- 是否只是 raw audio
- 是否已有說明主題、講者、日期、用途

若只有 raw audio，應明確告知需要先取得 transcript text。

### 2. Transcript Structuring

將 transcript 轉成：

- `核心摘要`
- `關鍵段落` 或 `主題區塊`
- `決策 / 行動項`（如果是會議）
- `關鍵知識點`（如果是內容型 transcript）
- `待確認問題`

### 3. Destination Decision

根據內容決定：

- 先進 `00-Inbox`
- 或直接交由 `note-update` 正式化
- 或標記為某一分類的候選

## Expected Output

輸出至少要有：

- `來源說明`
- `核心摘要`
- `結構化內容`
- `可能的目標分類`
- `下一步建議`

## Common Mistakes

- 把 raw audio 當成 transcript text 直接處理
- transcript 太長卻不分段
- 沒有抽出決策與行動項
- 生成草稿後完全不考慮既有正式筆記

## Handoff

`transcript-to-note` 完成後，下一步通常是：

- `note-update`
- `inbox-triage`
- `vault-GPS`
