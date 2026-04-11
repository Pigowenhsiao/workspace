# Classification Playbook

Use these examples as anchors when classifying similar pages in `Ai DataBase View`.

## Core policy

- `整合對象` is the canonical topic field.
- Dedicated topic views must filter only on `整合對象`.
- `Tags` can remain broader and messier; taxonomy navigation should not depend on them.
- Cross-topic pages may carry multiple `整合對象` values when each tool is central to the page.
- If a tool is only mentioned in passing, do not add it to `整合對象`.

## Clawdbot family

### Intro / overview pages

- `Clawdbot`
  - `內容類型`: `入門`, `案例`, `心得評論`
  - `平台/環境`: `Web UI`
  - `整合對象`: `Telegram`, `WhatsApp`, `Chrome`

### Setup / deployment pages

- `Clawdbot超级小白入门指南...`
  - `內容類型`: `安裝部署`, `設定`, `入門`
  - `平台/環境`: `Mac`, `虛擬機`
  - `整合對象`: `Feishu`, `Discord`

### Troubleshooting pages

- `ClawwdBot/MoltBot 踩坑全集`
  - `內容類型`: `故障排除`, `安裝部署`, `設定`
  - `平台/環境`: `Docker`, `Windows`
  - `整合對象`: `Discord`, `Telegram`, `Chrome`

### Cost pages

- `如何把 OpenClaw ... API 账单砍掉 60-80%`
  - `內容類型`: `成本優化`, `設定`, `工作流`
  - `平台/環境`: `Web UI`
  - `整合對象`: `Ollama`

### Agent orchestration pages

- `OpenClaw + Codex/ClaudeCode Agent Swarm...`
  - `內容類型`: `工作流`, `案例`, `工具整合`
  - `平台/環境`: `Mac`
  - `整合對象`: `Codex`, `Claude Code`

## Codex family

- `Codex`
  - `內容類型`: `資源整理`
  - `平台/環境`: `Web UI`
  - `整合對象`: `Codex`

- `Codex Skills讓自動撰寫報告也能又快又好`
  - `內容類型`: `工作流`, `工具整合`, `案例`
  - `平台/環境`: `Web UI`
  - `整合對象`: `Codex`

## Claude family

- `Claude Code创始人分享了他最新的15条CC使用技巧！`
  - `內容類型`: `工作流`, `工具整合`, `心得評論`
  - `平台/環境`: `Web UI`
  - `整合對象`: `Claude Code`, `Telegram`, `Chrome`, `Discord`

- `Claude Code Skills 完全指南...`
  - `內容類型`: `工作流`, `工具整合`, `入門`
  - `平台/環境`: `Web UI`
  - `整合對象`: `Claude Code`

## Gemini family

- `Gemini-CLI`
  - `內容類型`: `工具整合`, `資源整理`
  - `平台/環境`: `Mac`, `Windows`, `Linux`
  - `整合對象`: `Gemini`

- `我克隆了"宝玉"...用 Gemini + NotebookLM...`
  - `內容類型`: `工作流`, `案例`, `工具整合`
  - `平台/環境`: `Web UI`
  - `整合對象`: `Gemini`, `NotebookLM`

## NotebookLM family

- `我克隆了"宝玉"...用 Gemini + NotebookLM...`
  - `內容類型`: `工作流`, `案例`, `工具整合`
  - `平台/環境`: `Web UI`
  - `整合對象`: `Gemini`, `NotebookLM`

## Cross-topic guidance

- `Codex + Claude Code`: add both values when orchestration or delegation is central.
- `Gemini + NotebookLM`: add both values when NotebookLM is part of the actual workflow, not just cited.
- Topic view inclusion is driven by `整合對象`, so conservative multi-tagging matters.

## Decision shortcuts

- Playlist, many links, or video collections: bias toward `資源整理`
- Setup and environment bring-up: bias toward `安裝部署`
- Errors, pitfalls, or "踩坑": bias toward `故障排除`
- Cross-tool pipelines: bias toward `工具整合` and often `工作流`
- Personal lessons, comparisons, or quitting a tool: bias toward `心得評論`
