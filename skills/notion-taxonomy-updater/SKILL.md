---
name: notion-taxonomy-updater
description: |
  Batch-update classification properties in the user's Notion `Ai DataBase View` via Notion MCP. Use when the user asks to read a topic/tag, add taxonomy columns, classify pages like Clawdbot/Codex/Claude/Gemini, or write back multi-select properties in that database.
  觸發詞：「更新Notion分類」、「分類這些頁面」、「Notion資料庫」、「標籤更新」、「Codex分類」、「Gemini分類」、「寫入Notion」、「notion taxonomy」、「classify pages」、「更新已處理」、「Notion同步Obsidian」
  使用時機：使用者要求對 Notion 資料庫中的頁面進行分類、更新標籤、寫入多選項屬性，或將 Notion 頁面同步到 Obsidian。
---

# Notion Taxonomy Updater

## Overview

Classify pages inside the user's Notion `Ai DataBase View` and write the result back safely through Notion MCP.

Use this skill for the specific knowledge database captured in `references/ai-database-view.md`. Load that reference first because it contains the verified database ID, data source ID, property names, allowed values, and the known-good multi-select write format.

## Workflow

1. Read `references/ai-database-view.md`.
2. Confirm the target database or data source with Notion MCP fetch before editing anything.
3. If the taxonomy columns do not exist, add them with `notion-update-data-source`.
4. Search the data source for the requested topic keyword.
5. Fetch representative pages before bulk classification. Do not classify from title alone unless the page is sparse.
6. Update pages in batches with `notion-update-page`.
7. Fetch a few updated pages to verify the properties actually persisted.

## Full Recursive Read SOP (Ai DataBase View)

Use this SOP when the user asks for a full recursive read of `Ai DataBase View` and a read/unread report.

1. Fetch target entry point first:
   - Database URL: `https://www.notion.so/039bbec4bfc044e8854a6239c80d8182`
   - Data source URL: `collection://6c262f43-ffdb-4b3b-b5a5-38c02ac8a2e1`
2. Enumerate pages in batches via `notion-search` using multiple queries (example: `AI`, `Claude`, `Codex`, `Notion`, `Prompt`) with:
   - `query_type: "internal"`
   - `data_source_url: "collection://6c262f43-ffdb-4b3b-b5a5-38c02ac8a2e1"`
   - `page_size: 25`
3. De-duplicate by page ID across all batches.
4. Fetch every discovered page with `notion-fetch` to get complete `properties + content`.
5. During each fetch, extract child targets and recurse:
   - `<page url="...">`
   - `<mention-page url="...">`
   - embedded databases/data sources (`<database ...>`, `<data-source ...>`) and then enumerate/fetch their pages.
6. Track three sets:
   - `read_pages`
   - `unread_pages`
   - `unread_reasons` (`權限不足`, `不存在`, `其他/工具限制`)
7. Final output must include:
   - Read page list
   - Unread page list
   - Unread reasons (mapped per page ID)

## Notion -> Obsidian Full Sync SOP (含 `已處理` 回寫)

Use this SOP when the user asks to move all readable Notion pages into Obsidian and mark them as processed.

1. Run **Full Recursive Read SOP** first and produce a deduplicated readable page-ID list.
2. Fetch full page content (`properties + content`) for every readable page ID.
3. Convert each page into one Obsidian markdown note:
   - Include frontmatter at minimum: `notion_page_id`, `notion_url`, `source: notion`, `processed: true/false`.
   - Default to Traditional Chinese (`繁體中文`) for synthesized note content unless the user explicitly requests another language.
   - Keep original headings, links, and checklist semantics as much as possible.
4. Write notes into a deterministic vault folder (default: topic folder under `Learning/`).
   - If no matching folder exists, create one with a clear name (for example `Learning/notion-ai-database-full-sync`).
5. Produce import manifests:
   - `imported` list (page IDs + file paths)
   - `missing` list (page IDs + reason)
6. Only mark `已處理` for pages that were successfully written into Obsidian:
   - `notion-update-page` with `{"已處理":"__YES__"}`.
   - Do not mark unread/unwritten pages.
7. Verify write-back:
   - Fetch sample pages from updated batch and confirm `已處理` is checked.
8. Final report must contain:
   - Imported count/list
   - Missing count/list + reason
   - Marked-processed count/list
   - Any pages intentionally skipped

## Vault Git Sync Rule (When User Asks Pull/Push)

When user asks to push vault changes:

1. In vault repo, run pull first:
   - `git pull --rebase --autostash origin main`
2. Verify only intended files are staged.
3. Commit with clear scope (for example Notion full sync batch).
4. Push:
   - `git push origin main`
5. Report commit SHA and pushed file scope.

## Recursive Read Limits (Must Report)

- `notion-search` does not support empty query and has per-call cap (`page_size <= 25`).
- `notion-search` has no explicit cursor in this connector, so perfect no-miss coverage cannot be guaranteed by a single query stream.
- Date filters may drift; do not treat date-filtered results as complete coverage evidence.
- Always state these limits explicitly in the final read/unread report.

## Database Scope

This skill targets:

- Parent page: `Computer Skill`
- Embedded database: `Ai DataBase View`
- Data source: `collection://6c262f43-ffdb-4b3b-b5a5-38c02ac8a2e1`

If the user asks to classify another Notion database, do not assume this schema applies. Fetch that database first and adapt the workflow.

## Classification Rules

Use exactly these three properties unless the user explicitly asks to change the schema:

- `內容類型`
- `平台/環境`
- `整合對象`

Stay inside the allowed option set recorded in `references/ai-database-view.md`. If a needed option does not exist, update the schema first rather than inventing an unsupported value.

Load `references/classification-playbook.md` when the topic is close to the examples there. Reuse those examples as anchors for similar pages.

Treat `整合對象` as the primary navigation field for topic views. Do not mix `Tags` into view filtering once a page has been taxonomized.

## Multi-Select Write Rule

Notion MCP accepted this database only when multi-select values were passed as JSON-array strings, not native arrays.

Use this pattern:

```json
{
  "內容類型": "[\"工作流\",\"案例\"]",
  "平台/環境": "[\"Mac\"]",
  "整合對象": "[\"Codex\",\"Claude Code\"]"
}
```

Do not send:

```json
{
  "內容類型": ["工作流", "案例"]
}
```

That format failed during real use on this database.

## Recommended Execution Pattern

### Add missing columns

Use `notion-update-data-source` against the data source, not the page URL. Reuse the exact schema statements from `references/ai-database-view.md`.

### Find candidate pages

Use `notion-search` with:

- `query_type: "internal"`
- `data_source_url: "collection://6c262f43-ffdb-4b3b-b5a5-38c02ac8a2e1"`
- a focused topic query such as `Clawdbot`, `Codex`, `Claude`, or `Gemini`

### Read before classifying

Fetch representative pages to determine:

- whether the page is an intro, setup guide, troubleshooting note, workflow write-up, or resource list
- which platforms are explicitly mentioned
- which tools and integrations are actually present

### Batch update carefully

- Prefer small batches.
- Merge with any existing taxonomy values if they are already present and still valid.
- Do not overwrite unrelated properties.

### Verify write-back

After each batch, fetch at least 2-3 pages and confirm the final property values.

## Heuristics

Use page content first. Use title and search highlights only when the page is too sparse to infer more.

Good signals:

- `入門`: concept overview, what the tool is, orientation content
- `安裝部署`: setup, install, deployment, environment bring-up
- `設定`: configuration, parameter tuning, auth or integration setup
- `故障排除`: errors, pitfalls, broken flows, fixes
- `成本優化`: billing, token reduction, cost-saving patterns
- `工作流`: repeatable operational flow, orchestration, team process
- `案例`: real usage, walkthrough, implementation example
- `工具整合`: one tool operating with another system
- `資源整理`: link dumps, playlists, collections, references
- `心得評論`: opinions, lessons learned, adoption/abandonment notes

## Consistency Rules

- Use `整合對象` as the only primary filter key for dedicated topic views such as `Codex`, `Claude`, and `Gemini`.
- Keep `Tags` as a secondary discovery field only. Do not depend on `Tags` for persistent taxonomy navigation.
- Add multiple `整合對象` values when a page is truly cross-topic, such as `Gemini + Codex` or `Codex + Claude Code`.
- Leave `整合對象` partially empty rather than guessing when the page mentions a tool only in passing.
- Fill `平台/環境` only when the environment is explicit in the page or clearly implied by setup steps.
- Prefer fewer, more defensible `內容類型` values over maximal labeling.
- Reuse an existing taxonomy label when it is close enough; avoid creating new semantics through inconsistent interpretation.

## Common Mistakes

- Updating the database page instead of the data source.
- Sending native arrays to multi-select properties.
- Classifying too many pages without fetching examples first.
- Creating new option labels ad hoc.
- Claiming the batch succeeded without fetching pages to verify persistence.
- Building views from `Tags` after `整合對象` has already been established.

## References

- `references/ai-database-view.md`
- `references/classification-playbook.md`
