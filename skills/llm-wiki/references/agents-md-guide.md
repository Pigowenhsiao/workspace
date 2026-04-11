# AGENTS.md as Wiki Schema Layer

`AGENTS.md` 是定義 LLM Wiki 操作規則的核心配置文件。相當於 vault 的「法則」——告訴任何接手這個 vault 的 LLM：目錄結構是什麼、約定是什麼、每個 workflow 怎麼跑。

---

## 基本結構

```markdown
# Vault Schema

## 目錄結構
- `Learning/` — 學習筆記
  - `youtube/` — YouTube 影片報告
  - `twitter/` — Twitter/X 推文存檔
  - `articles/` — 部落格、Newsletter 文章
  - `notion-*/` — Notion 遷移內容
- `index.md` — Wiki 全域目錄
- `log.md` — 時間線日誌

## 命名約定
- 檔名：`主題-關鍵描述.md`（中文）
- 範例：`Gemma-on-Raspberry-Pi-本地AI設定.md`

## Frontmatter 格式
```yaml
---
date: YYYY-MM-DD
source: URL or Channel name
tags: [tag1, tag2]
---
```

## Ingest Workflow
1. Fetch source
2. Synthesize (not transcribe)
3. Write to appropriate subdirectory
4. Update index.md
5. Update cross-references
6. Append to log.md

## Query Response Format
- Synthesize from existing notes
- File valuable discoveries back to wiki
- Always cite sources with [[links]]

## Lint Frequency
每週或每累積 10 個新來源後，主動做一次 lint。

## Git Workflow
- `git add -A && git commit -m "feat: add <type> - <title>"`
- `git pull origin main --rebase && git push origin main`
- Always use --rebase, never merge
```

---

## 為什麼 AGENTS.md 重要

- **不綁定特定 AI**：無論是 OpenClaw、Claude Code、還是其他 Agent，讀了 AGENTS.md 就能正確操作 vault
- **沉澱工作流**：你和 LLM 共同演化出來的約定，不會因為換 session 就消失
- **自我說明的 wiki**：新 AI 接手時，不需要人類解釋，直接讀 AGENTS.md

---

## 與 Karpathy Schema 的對應

| Karpathy 說的 | AGENTS.md 裡的位置 |
|--------------|-------------------|
| Raw sources 目錄 | `Learning/` 各子目錄 |
| Wiki 結構 | `index.md` + `Learning/` 子目錄 |
| 操作規則（Schema） | 本文件 `AGENTS.md` |
| Index file | `index.md` |
| Log file | `log.md` |

---

*由 Librarian skill 自動歸檔*
