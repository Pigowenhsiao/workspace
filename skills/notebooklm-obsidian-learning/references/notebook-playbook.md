# NotebookLM Obsidian Learning Playbook

## Fixed Notebook

- Title: `論文代寫`
- URL: `https://notebooklm.google.com/notebook/b4341994-db58-4821-a082-51d65715eab2`
- Notebook ID: `b4341994-db58-4821-a082-51d65715eab2`

## Source Coverage

This notebook combines five sources:

1. `Claude Code + NoteBookLM = Infinite Memory`
2. `NotebookLM obsidian學習方式`
3. `Teriki 模式：人機協作論文寫作指南`
4. `带着一百万...我们去了论文代写聚集地`
5. `智勝 AI：Teriki 的人機協作學術寫作之道`

The notebook is useful for three recurring tasks:

- building a NotebookLM + Obsidian study workflow
- deciding what must be deeply read by a human
- avoiding redundant learning by comparing new material against an existing knowledge base

## Distilled Guidance

### Division of labor

- `NotebookLM` is the ingestion, de-duplication, comparison, and retrieval layer
- `Obsidian` is the durable personal knowledge store
- the human is responsible for deep reading and final judgment

### What belongs in NotebookLM

- raw, bulky source material
- multi-source comparisons
- repeated explanations from videos, articles, and books
- new books or courses being evaluated for relevance
- exported Obsidian notes when filtering for novelty

### What belongs in Obsidian

- compressed durable knowledge
- definitions
- personal interpretations
- deep-read insights
- links to related concepts
- open questions worth revisiting

### Human deep-read rule

Use AI to scan broadly, but reserve human effort for the 1-2 most important primary sources.

That rule comes from the "sandwich reading" idea inside the notebook:

- AI scans
- human deeply reads core material
- AI summarizes secondary material

### Redundancy filtering rule

Before committing to a new book or course:

1. export existing Obsidian knowledge into one text or PDF file
2. upload that export together with the new material into NotebookLM
3. ask what is actually new
4. skip the material if it mostly overlaps with known content

## Recommended Query Set

### Workflow design

```powershell
nlm notebook query b4341994-db58-4821-a082-51d65715eab2 "Based on this notebook, give me a practical learning workflow that combines NotebookLM and Obsidian for [topic]. Focus on what goes into NotebookLM, what gets written into Obsidian, and what must be deeply read by a human."
```

### Deep-read selection

```powershell
nlm notebook query b4341994-db58-4821-a082-51d65715eab2 "For [topic], what should be scanned by AI and which 1-2 sources should be deeply read word-for-word by a human?"
```

### Redundant material filtering

```powershell
nlm notebook query b4341994-db58-4821-a082-51d65715eab2 "How should I compare a new book, course, or article pack against my Obsidian vault so I can skip redundant material and focus only on what is new?"
```

### Obsidian note shaping

```powershell
nlm notebook query b4341994-db58-4821-a082-51d65715eab2 "Given this topic, what should be preserved in Obsidian as durable knowledge rather than left in NotebookLM?"
```

## Default Obsidian Note Shape

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

## Pitfalls

- Do not ask NotebookLM to write the final argument or essay and mistake that for learning.
- Do not store raw NotebookLM dumps in Obsidian.
- Do not let AI summarize the most important primary source without human reading.
- Do not start from zero each time; reuse the vault as a filter.
