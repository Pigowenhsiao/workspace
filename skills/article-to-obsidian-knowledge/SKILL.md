---
name: article-to-obsidian-knowledge
description: Use when the user wants to turn articles, webpages, X threads, PDFs, videos, or other source material into structured knowledge notes for Obsidian, including summaries, knowledge points, wikilinks, tags, and reusable note sections.
---

# Article To Obsidian Knowledge

## Description

The `article-to-obsidian-knowledge` skill is for turning source material into reusable Obsidian notes instead of leaving it as raw content.

Use it when the agent needs to:

- convert an article, URL, PDF, transcript, or thread into knowledge points
- extract key ideas, methods, principles, and actionable takeaways
- rewrite source material into Obsidian-friendly notes with `[[wikilinks]]`
- preserve source context while making the note easier to review later
- create notes that are meant to live inside an Obsidian vault rather than a generic Markdown folder

## When to use

Use this skill when the user asks for any of these outcomes:

- 「把文章變成知識點」
- 「整理成 Obsidian 筆記」
- 「做成可回顧的知識卡 / 筆記」
- 「把網址 / PDF / 影片內容整理成筆記」
- 「萃取重點、方法、洞見並存進 Obsidian」

Do not use this skill when the user only wants the raw article archived without synthesis. In that case, prefer `baoyu-url-to-markdown` or `markitdown` alone.

## Source acquisition

Choose the lightest reliable ingestion path first:

1. URL / article / X / YouTube:
   - prefer `baoyu-url-to-markdown`
2. PDF / Office / local files:
   - prefer `markitdown`
3. Already-available Markdown or pasted text:
   - use it directly without re-fetching

The note should preserve source traceability, but the goal is not archival fidelity. The goal is usable knowledge.

## Obsidian vault target

This environment already has a primary Obsidian vault:

- Vault path: `E:\obsidian\PigoVault`

This vault should still expose Codex content through junctions or symlinks:

- `CodexDocs` -> `C:\Users\pigow\.codex\docs`
- `CodexSkills` -> `C:\Users\pigow\.codex\skills`

So for this environment, the default note target should be treated as:

- Obsidian-visible path:
  `E:\obsidian\PigoVault\article-notes\`
- Real filesystem path:
  `E:\obsidian\PigoVault\article-notes\`

Unless the user explicitly asks for a different location, prefer writing finished notes directly into the Vault folder above.

If any of these are missing, create them before writing notes:

- `E:\obsidian\PigoVault\article-notes\`
- `E:\obsidian\PigoVault\CodexDocs`
- `E:\obsidian\PigoVault\CodexSkills`

## Output shape

Default to this Obsidian-friendly structure:

```markdown
# Title

## Summary

## Knowledge Points

## Methods / Principles

## Why It Matters

## Related Topics

## My Notes

## Source
```

Adapt section names only when the source type clearly needs a different shape.

## Obsidian conventions

When producing the final note:

- write the synthesized note in Traditional Chinese (`繁體中文`) unless the user explicitly requests another language
- use `[[wikilinks]]` for obvious reusable concepts, tools, people, or projects
- keep headings shallow and scannable
- use bullets for discrete knowledge points
- keep source citation in a final `## Source` section
- add tags only when they help future retrieval

Good wikilink targets usually include:

- concepts
- tools
- frameworks
- people
- companies
- related projects

Do not overlink every noun. Link only the terms likely to become their own notes.

## Synthesis rules

Transform raw material into knowledge, not just shorter prose.

Always try to extract:

1. the core thesis
2. the most reusable knowledge points
3. any method, workflow, or decision rule
4. when the idea applies
5. any limitation, caveat, or tradeoff
6. what is worth linking to other notes

If the source is mostly opinion, still turn it into:

- claims
- reasoning
- implications
- questions worth revisiting

## Recommended workflow

### 1. Ingest the source

- fetch or convert the source into Markdown/text

### 2. Identify the note type

Decide whether the output is mainly:

- concept note
- workflow note
- tool note
- summary note
- argument / viewpoint note

### 3. Rewrite into knowledge form

Prefer short sections over long essay blocks.

### 4. Add Obsidian structure

- title
- clear headings
- `[[wikilinks]]`
- optional tags
- source block

## Minimal example

```markdown
# Claude Code Learning Note

## Summary
This article argues that [[Claude Code]] is most valuable when treated as a repeatable workflow engine instead of a one-shot chatbot.

## Knowledge Points
- High-signal usage comes from stable workflows, not ad hoc prompting.
- [[MCP]] becomes more useful when paired with task-specific scripts.
- Sequential execution can be more stable than parallel execution for some browser-heavy tools.

## Methods / Principles
- Build repeatable command paths before optimizing prompts.
- Prefer observable artifacts like Markdown, JSON, and logs.

## Related Topics
- [[AI agents]]
- [[OpenCLI]]
- [[Workflow design]]

## Source
- Original URL: https://example.com
```

## Related skills

- `baoyu-url-to-markdown` for URL ingestion
- `markitdown` for file conversion
- `knowledge-framework` when the user explicitly wants a framework-based rewrite
- `obsidian-markdown` when Obsidian syntax details matter

Use this skill as the orchestration layer that turns raw content into a reusable knowledge note.

## Scripts

This skill ships with:

- `scripts/render_obsidian_note.py`

Use the script when the agent has already completed the synthesis step and wants a stable way to materialize the final Obsidian note.

Recommended pattern:

1. ingest the source with `baoyu-url-to-markdown` or `markitdown`
2. synthesize the note sections in the current session
3. place the structured note content into a JSON spec
4. render the final note with:

```bash
python scripts/render_obsidian_note.py \
  --source-md /path/to/source.md \
  --spec-json /path/to/note-spec.json \
  --output /path/to/final-note.md
```

For this environment, the default output should usually be:

```bash
python scripts/render_obsidian_note.py \
  --source-md /path/to/source.md \
  --spec-json /path/to/note-spec.json \
  --output E:\obsidian\PigoVault\article-notes\<note-name>.md
```

The script handles:

- YAML frontmatter for Obsidian
- section ordering
- wikilink-friendly bullet rendering
- source metadata extraction from the original markdown frontmatter

The script does not replace synthesis. The agent is still responsible for deciding what the important knowledge points are.


