# Ai DataBase View Reference

Use this file for the exact Notion targets and schema already verified in the user's workspace.

## Canonical targets

- Parent page URL: `https://www.notion.so/943dec13134943ab9d682bbdedf645eb`
- Parent page title: `Computer Skill`
- Database URL: `https://www.notion.so/039bbec4bfc044e8854a6239c80d8182`
- Database title: `Ai DataBase View`
- Data source URL: `collection://6c262f43-ffdb-4b3b-b5a5-38c02ac8a2e1`

## Existing core properties

- `Name` - title
- `Tags` - multi_select
- `Website` - url
- `URL` - url
- `文字` - text
- `標籤` - multi_select
- `Created` - created_time
- `已處理` - checkbox，用於追蹤文章或資料是否已完成整理流程

## Taxonomy properties added for this workflow

### 內容類型

Allowed values:

- `入門`
- `安裝部署`
- `設定`
- `故障排除`
- `成本優化`
- `工作流`
- `案例`
- `工具整合`
- `資源整理`
- `心得評論`

### 平台/環境

Allowed values:

- `Mac`
- `Windows`
- `Linux`
- `VPS`
- `Docker`
- `虛擬機`
- `Android`
- `Web UI`

### 整合對象

Allowed values:

- `Telegram`
- `Discord`
- `Feishu`
- `WhatsApp`
- `Chrome`
- `Obsidian`
- `Codex`
- `Claude Code`
- `Gemini`
- `Qwen`
- `MCP`
- `Superpowers`
- `NotebookLM`
- `Ollama`

## Schema creation statement

Use this exact DDL when the three taxonomy columns are missing:

```sql
ADD COLUMN "內容類型" MULTI_SELECT('入門':default, '安裝部署':default, '設定':default, '故障排除':default, '成本優化':default, '工作流':default, '案例':default, '工具整合':default, '資源整理':default, '心得評論':default);
ADD COLUMN "平台/環境" MULTI_SELECT('Mac':default, 'Windows':default, 'Linux':default, 'VPS':default, 'Docker':default, '虛擬機':default, 'Android':default, 'Web UI':default);
ADD COLUMN "整合對象" MULTI_SELECT('Telegram':default, 'Discord':default, 'Feishu':default, 'WhatsApp':default, 'Chrome':default, 'Obsidian':default, 'Codex':default, 'Claude Code':default, 'Gemini':default, 'Qwen':default, 'MCP':default, 'Superpowers':default, 'NotebookLM':default, 'Ollama':default)
```

## View design rule

Dedicated topic views must filter on `整合對象` only.

Recommended examples:

- `Codex` view -> `整合對象` contains `Codex`
- `Claude` view -> `整合對象` contains `Claude Code`
- `Gemini` view -> `整合對象` contains `Gemini`

Do not mix `Tags` into the primary filter once taxonomy has been written back.

## Verified MCP write format

`notion-update-page` accepted multi-select values only when they were passed as JSON strings:

```json
{
  "內容類型": "[\"工作流\",\"案例\"]",
  "平台/環境": "[\"Mac\"]",
  "整合對象": "[\"Codex\",\"Claude Code\"]"
}
```

Native arrays were rejected or did not persist reliably:

```json
{
  "內容類型": ["工作流", "案例"]
}
```

Checkbox values should use the Notion MCP checkbox write format:

```json
{
  "已處理": "__YES__"
}
```

or

```json
{
  "已處理": "__NO__"
}
```

## Verification pattern

After update:

1. Fetch a few changed pages.
2. Confirm each property shows the expected values.
3. If values are missing, re-check string encoding before changing the schema again.

## Recursive read baseline (for crawl/report tasks)

- Preferred entry database URL: `https://www.notion.so/039bbec4bfc044e8854a6239c80d8182`
- Preferred data source URL: `collection://6c262f43-ffdb-4b3b-b5a5-38c02ac8a2e1`
- Batch query suggestions for coverage expansion: `AI`, `Claude`, `Codex`, `Notion`, `Prompt`
- Always de-duplicate by page ID, then run `notion-fetch` page-by-page.
- If a page fetch returns `object_not_found`, classify as `權限不足或不存在` and keep it in unread report.

## Obsidian sync baseline (for full transfer tasks)

- Recommended target vault folder: `Learning/notion-ai-database-full-sync`
- One Notion page -> one markdown note
- Required per-note frontmatter fields:
  - `notion_page_id`
  - `notion_url`
  - `source: notion`
  - `processed`
- Only pages with successful note write can be marked in Notion:
  - `{"已處理":"__YES__"}`
- Always export import manifests:
  - imported list (ID + file path)
  - missing list (ID + reason)
