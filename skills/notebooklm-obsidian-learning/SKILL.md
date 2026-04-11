---
name: notebooklm-obsidian-learning
description: Use when the user wants to use the fixed NotebookLM notebook "論文代寫" as a repeatable playbook for NotebookLM + Obsidian learning, including deciding what to upload into NotebookLM, what to preserve in Obsidian, which sources must be deeply read by a human, or how to filter redundant books, articles, and videos against an existing Obsidian vault.
---

# NotebookLM Obsidian Learning

## Overview

Use this skill to turn the NotebookLM notebook below into a reusable learning operating system.

The notebook is not the final knowledge store. It teaches a division of labor:

- `NotebookLM` ingests bulky raw material, removes redundancy, compares sources, and helps choose what is worth reading
- `Obsidian` stores only the durable knowledge, decisions, and personal insights worth keeping
- the human still performs deep reading on the 1-2 most important primary sources

## Core Notebook

- Notebook title: `論文代寫`
- Notebook URL: `https://notebooklm.google.com/notebook/b4341994-db58-4821-a082-51d65715eab2`
- Notebook ID: `b4341994-db58-4821-a082-51d65715eab2`
- Preferred Obsidian vault path in this environment: `E:\obsidian\PigoVault`
- Preferred note output path in this environment: `E:\obsidian\PigoVault\article-notes`

Before using the notebook, verify auth:

```powershell
nlm doctor
```

If authentication is invalid or unstable, use Cookie-first recovery:

1. ask the user for a cookie export file (prefer Netscape `cookies.txt`)
2. import cookie state for NotebookLM/Google session recovery
3. re-run `nlm doctor`
4. only fall back to interactive manual login if cookie recovery fails

If the notebook must be queried directly, use:

```powershell
nlm notebook query b4341994-db58-4821-a082-51d65715eab2 "<question>"
```

Read [references/notebook-playbook.md](references/notebook-playbook.md) when exact source context, query ideas, or the distilled rationale behind the workflow is needed.

## Workflow

### 1. Load raw material into NotebookLM

Put the bulky, repetitive, high-volume inputs into NotebookLM:

- YouTube videos
- article URLs
- PDFs
- books
- transcripts
- review pages
- exported Obsidian vault snapshots when comparing against existing knowledge

Use NotebookLM first when the user is facing information overload, duplicate explanations, or uncertainty about whether a source is worth reading at all.

### 2. Ask NotebookLM to compress, compare, and choose

Do not ask NotebookLM to "learn for me" or "write the full essay."

Ask it to:

- identify the core concepts
- remove duplicate explanations
- compare multiple sources
- identify the 1-2 sources worth deep reading
- detect which chapters or sections are actually new relative to the user's existing knowledge base

### 3. Reserve human effort for deep reading

Apply the sandwich reading rule:

- AI scans the large pile
- the human deeply reads the 1-2 highest-value primary sources word-for-word
- AI summarizes the secondary sources for breadth

Never let AI replace deep reading of the most important source material. The point is to narrow attention, not outsource understanding.

### 4. Write only durable knowledge into Obsidian

Do not dump raw NotebookLM output into Obsidian unchanged.

Write only:

- the core thesis
- reusable knowledge points
- definitions
- personal insights from deep reading
- unresolved questions
- links to related notes
- the source notebook or primary source references

When writing synthesized notes back into Obsidian, default to Traditional Chinese (`繁體中文`) unless the user explicitly requests another language.

Use this default note shape:

```markdown
# Topic

## Summary

## Key Points
- ...

## Deep Read Insights
- ...

## Open Questions
- ...

## Related
- [[Concept A]]
- [[Concept B]]

## Source
- NotebookLM: ...
- Primary source: ...
```

### 5. Use Obsidian as a filter for future learning

When evaluating a new book, course, or article set:

1. export the relevant Obsidian notes or the whole vault into one text or PDF file
2. upload that export plus the new material into NotebookLM
3. ask what is genuinely new
4. skip materials that mostly repeat what the user already knows

This is a filtering workflow, not a summarization workflow.

## Reusable Query Recipes

Use these queries with the fixed notebook when the user wants to reuse its learning logic:

### Build a learning workflow

```powershell
nlm notebook query b4341994-db58-4821-a082-51d65715eab2 "Based on this notebook, give me a practical learning workflow that combines NotebookLM and Obsidian for [topic]. Focus on what goes into NotebookLM, what gets written into Obsidian, and what must be deeply read by a human."
```

### Pick deep-read targets

```powershell
nlm notebook query b4341994-db58-4821-a082-51d65715eab2 "For [topic], what should be scanned by AI and which 1-2 sources should be deeply read word-for-word by a human?"
```

### Filter redundant learning

```powershell
nlm notebook query b4341994-db58-4821-a082-51d65715eab2 "How should I compare a new book or article pack against my Obsidian vault so I can skip redundant material and only study what is new?"
```

### Turn learning into Obsidian notes

```powershell
nlm notebook query b4341994-db58-4821-a082-51d65715eab2 "Given this topic, what should be preserved in Obsidian as durable notes rather than left inside NotebookLM?"
```

## Common Mistakes

- Treat NotebookLM as the final note store. It should be the compression and comparison layer, not the long-term knowledge base.
- Ask AI to write final essays or arguments directly from the notebook. Use it to retrieve facts and structure; use human judgment for reasoning and final claims.
- Summarize the most important primary source instead of reading it. This removes the depth the workflow is designed to preserve.
- Dump every AI output into Obsidian. Obsidian should hold distilled knowledge, not unfiltered transcript sludge.
- Start every new learning project from scratch. Reuse the Obsidian vault as a relevance filter before investing time in new material.

## Resources

### references/notebook-playbook.md

Load this reference when exact source coverage, distilled notebook findings, or concrete prompt patterns are needed.

### No scripts required by default

If this skill later grows to include Obsidian export helpers or note-rendering helpers, add them under `scripts/` and keep the SKILL body lean.
