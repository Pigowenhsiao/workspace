---
name: refresh-obsidian-note-from-notion
description: Use when the user provides an Obsidian note path and wants the note refreshed from its linked Notion page, rewritten into a structured Traditional Chinese Obsidian note, and saved back to the same file.
---

# Refresh Obsidian Note From Notion

## Overview

Use this skill when the user gives you an existing Obsidian note path and wants you to refresh that note from its original Notion source instead of rewriting everything manually.

The core pattern is:

1. read the Obsidian note
2. recover the Notion location from the note itself
3. fetch the Notion page
4. rewrite the note into a structured Traditional Chinese Obsidian note
5. write back to the same path

## When to Use

Use this skill when the user asks for outcomes like:

- 「我貼 Obsidian 筆記路徑，你幫我重整」
- 「從這篇筆記裡找 Notion 來源，再重新整理」
- 「把現有 Notion 轉存筆記改成新的整理版」
- 「依照既有格式，把這篇 Obsidian 筆記重新整理」

Do not use this skill when:

- the user only gives a Notion URL and no existing note path
- the user wants a brand-new note in a new location
- the note has no recoverable Notion reference and the user has not provided one elsewhere

In those cases, prefer `article-to-obsidian-knowledge` directly.

## Required Inputs

- One existing Obsidian note path

The note should already exist and contain at least one recoverable Notion reference in one of these places:

- frontmatter: `notion_url`
- frontmatter: `source_url`
- frontmatter: `notion_page_id`
- frontmatter: `source_page_id`
- body text: `https://www.notion.so/...`

## Recovery Order

Read the note and recover the Notion location in this order:

1. `notion_url`
2. `source_url`
3. full Notion URL found in body
4. `notion_page_id`
5. `source_page_id`

If only a page ID exists, convert it into:

```text
https://www.notion.so/<page-id-without-dashes>
```

If no recoverable Notion reference exists:

- stop
- report exactly which fields were checked
- ask the user for the Notion URL or page ID

## Fetch Rule

Once the Notion location is recovered:

- fetch the page through the Notion MCP tool
- use the fetched `properties + content` as the source of truth
- do not trust stale note body content over the live Notion page

If Notion MCP returns auth/session failure:

1. ask the user for a cookie export file first (prefer `cookies.txt`)
2. recover session with cookie import
3. retry Notion fetch
4. only fall back to manual interactive login when cookie recovery fails

## Output Rule

Rewrite the note in Traditional Chinese (`繁體中文`) unless the user explicitly requests another language.

Default to this structure unless the source strongly needs a different shape:

```markdown
---
title: "..."
aliases:
  - "..."
source: "notion"
notion_page_id: "..."
source_page_id: "..."
notion_url: "..."
processed: true
synced_at: "YYYY-MM-DD"
tags:
  - ...
---

# Title

## 核心摘要

## 文章分析

### 核心論點

### 風險與限制

## 關鍵知識點

## 我會怎麼用這篇文章

## 全文（繁中重寫）

## Source
```

## Writing Rules

- preserve source traceability
- prefer Traditional Chinese wording throughout
- use `[[wikilinks]]` only for concepts likely to become reusable notes
- do not overlink every noun
- keep the note readable as a standalone knowledge asset, not just a raw archive
- if the old note contains useful frontmatter fields, preserve them when they still match reality

## File Write Rule

- overwrite the same Obsidian file path the user provided
- do not create a sibling file unless the user explicitly asks for versioned output
- if the current note is only a raw dump, replace it fully
- if the current note already contains valuable related links or local annotations, preserve them only when they do not conflict with the refreshed structure

## Verification

After writing, verify all of the following:

- the file exists
- `notion_url` is present
- `notion_page_id` or `source_page_id` is present
- `## 核心摘要` exists
- `## 文章分析` exists
- `## Source` exists

If the note is rewritten in the full format, also verify:

- `## 全文（繁中重寫）` exists

## STATUS Logging

If the active project or workspace requires `STATUS_*.md` tracking:

- create or update a status file
- record:
  - what was changed
  - which note path was updated
  - how the Notion source was recovered
  - verification results
  - remaining risks

If no such project convention exists, this step is optional.

## Minimal Workflow

1. Read the Obsidian note path.
2. Recover Notion URL or page ID from the note.
3. Fetch the Notion page.
4. Synthesize the refreshed note in Traditional Chinese.
5. Overwrite the same note file.
6. Verify required headings and source metadata.
7. Update `STATUS_*.md` when the workspace policy requires it.

## Related Skills

- `article-to-obsidian-knowledge` for the synthesis pattern
- `obsidian-markdown` for valid Obsidian formatting
- `ce:compound` when this workflow should be documented as a reusable team learning
