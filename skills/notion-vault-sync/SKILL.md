---
name: notion-vault-sync
description: "When Pigo shares a URL (YouTube, Twitter/X, article, Substack) or asks to archive/save content, automatically fetch the content, write a structured note to ~/Documents/Pigo/Learning/ with the exact standard format, push to GitHub, and write the same content to Notion Input Database. Routing: YouTube goes to Learning/youtube/, Twitter/X to Learning/twitter/, articles/Substack to Learning/articles/. Always use the exact standard page template. After writing to Obsidian, always run git add -A and git commit and git pull origin main --rebase and git push origin main."
---

# Notion-Vault Sync Skill

## Standard Page Template (必須嚴格遵守)

```markdown
tags:
 - [Tag1]
 - [Tag2]
---

# [標題]

## 核心摘要

[2-3 句話總結這篇的核心價值]

## 文章分析

### 核心論點

- [論點 1]
- [論點 2]
- ...

### 風險與限制

- [限制 1]
- [限制 2]
- ...

## 關鍵知識點

- [知識點 1]
- [知識點 2]
- ...

## 我會怎麼用這篇文章

[2-3 句話，結合 Pigo 的 vault 和實際應用場景]

## 全文（繁中重寫）

[完整內容的繁體中文重寫，或原文精華節選]

## Source

- [原始 URL]
- Vault 位置：[路徑]
```

**格式規則：**
- `tags:` 和 `---` 是 markdown frontmatter，不是 block
- 標題：`# ` 開頭
- 每個 `##` 區塊都要有內容，不能留空
- 如果某個 section（如風險與限制）真的沒有內容，用一句話說明原因
- `## 全文（繁中重寫）` 不能省略

## Routing Rules

| 來源類型 | 目的地 | 範例 |
|---------|--------|------|
| YouTube URL | `Learning/youtube/` | `Google-Antigravity-不會寫程式也能開發App.md` |
| Twitter/X URL | `Learning/twitter/` | `berryxia-karpathy-idea-file.md` |
| Substack / Blog | `Learning/articles/` | `什麼是駕馭工程-Harness-Engineering.md` |
| GitHub repo | `Learning/repos/` | `repo名稱.md` |

## Workflow

### Step 1: Fetch Content

```bash
# YouTube
yt-dlp --dump-json --no-playlist -- "URL" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print('Title:', d.get('title', ''))
print('Channel:', d.get('channel', ''))
print('Duration:', d.get('duration', 0))
desc = d.get('description', '')
for line in desc.split('\n'):
    stripped = line.strip()
    if stripped and any(c.isdigit() for c in stripped[:6]) and ':' in stripped:
        print(stripped)
"

# Web / Twitter
curl -s --max-time 12 "https://r.jina.ai/URL"
```

### Step 2: Write Vault Note

- 寫入 `~/Documents/Pigo/Learning/<type>/<檔名>.md`
- **嚴格使用上面的 Standard Page Template**
- 每個 section 都要填內容，不能跳過

### Step 3: Git Push

```bash
cd ~/Documents/Pigo
git add -A && git commit -m "feat: add <type> - <標題>" && git pull origin main --rebase && git push origin main
```

### Step 4: Write to Notion

使用 `scripts/sync-to-notion.js`：

```bash
node scripts/sync-to-notion.js "<title>" "<tags_csv>" "<summary>" "<core_points_csv>" "<risks_csv>" "<keypoints_csv>" "<apply>" "<fulltext>" "<source_url>" "<vault_path>"
```

**參數說明：**
- `<title>` — 頁面標題
- `<tags_csv>` — 標籤（逗號分隔）
- `<summary>` — 核心摘要（單行）
- `<core_points_csv>` — 核心論點（逗號分隔，每點用 `。` 或換行區分）
- `<risks_csv>` — 風險與限制（逗號分隔）
- `<keypoints_csv>` — 關鍵知識點（逗號分隔）
- `<apply>` — 我會怎麼用這篇文章
- `<fulltext>` — 全文（繁中重寫或精華節選）
- `<source_url>` — 原始 URL
- `<vault_path>` — vault 檔案路徑

**Notion Database ID:** `33a42529-badd-80fd-9178-000b0c7998fc`

## Notion API Notes

- Use `@notionhq/client` v5
- Import: `const { Client } = require('/home/pigo/.nvm/versions/node/v22.22.2/lib/node_modules/@notionhq/client')`
- Page creation: `parent: { data_source_id: '33a42529-badd-80fd-9178-000b0c7998fc' }`
- Block text limit: 2000 chars per block（長文字需分段）
- Available tags: AI, LLM, Claude, Codex, Agent, Prompt, Notebooklm, SKILLS, 知識庫, Knowledge, Tool, Video Edit, Recipe, cooking, investment, Vincent, AI_Training, Gemini, 數位分身, 工作流

## Tags for Common Content Types

| 內容類型 | Tags |
|---------|------|
| LLM/Wiki | LLM, 知識庫 |
| YouTube 影片 | AI, [頻道名] |
| Claude Code | Claude, AI |
| OpenClaw | Agent, AI |
| 知識庫架構 | 知識庫, LLM |
