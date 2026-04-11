---
name: weekly-summary
description: Use when ingesting one or more weekly report files into Pigo's Obsidian vault, especially Lumentum SAG/SAG-TAK/TAK weekly updates, when normalizing CY or FY week naming, rebuilding Lumentum weekly indexes, or repairing mislabeled weekly report notes after bulk imports.
---

# Weekly Summary

## Core Use

這個 skill 用來把「單份或整批週報」轉成可累積的 Obsidian 工作知識，而不是只做一次性摘要。

目前預設目標是 Pigo 的 Lumentum 週報工作流：

- 來源目錄：
  - `C:\Users\hsi67063\Box\3DS Quality Taiwan\Pigo\Weekly report\SAG Weekly report`
- Obsidian vault：
  - `C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian`
- 輸出目錄：
  - `Lumentum/Weekly Reports/<year-or-fiscal-year>/`

## When To Use

- 使用者要把整個週報資料夾批次匯入 wiki
- 使用者要把單份 `pptx` / `pdf` 週報整理成標準筆記
- 匯入後需要重建 `Lumentum/index.md` 與 `Lumentum/log.md`
- 已有週報筆記被錯分成錯的 team/title，需要批次修正
- 需要保留週次索引，即使來源檔損壞也不能讓時間線斷掉

不要用在：

- 一般學習內容整理
- 非週報類的 meeting minutes / article / Twitter thread
- 需要高度人工詮釋的正式管理報告撰寫

## Workflow

1. 先確認來源是否為週報檔案，辨識 `CY/FY + week`
2. 優先使用較完整的 `pptx`；若沒有，再使用 `pdf`
3. 以 `markitdown` 轉出可讀文字
4. 產生標準筆記：
   - frontmatter
   - `## 核心摘要`
   - `## 本週重點`
   - `## 風險與異常`
   - `## 待追蹤事項`
   - `## 我會怎麼用這份週報`
   - `## Source`
5. 重建 `Lumentum/index.md`
6. 更新 `Lumentum/log.md`
7. 寫入對應 `STATUS_*.md`

## Routing Rules

- `SAG Quality Weekly Update*` -> `SAG Quality`
- `SAG-TAK Quality Weekly Update*` -> `SAG-TAK Quality`
- `TAK Quality Weekly Update*` -> `TAK Quality`
- `Weekly SAG-Ops Report*` -> `SAG Ops`

輸出檔名格式：

- `CY25W10 - SAG Quality Weekly Update.md`
- `FY24W24 - TAK Quality Weekly Update.md`

年度資料夾規則：

- `CY25` -> `2025/`
- `FY24` -> `FY24/`

## Failure Handling

- 若來源檔是 `0 bytes` 或 `markitdown` 無法讀取：
  - 仍要建立 placeholder 筆記
  - frontmatter 保留 `source_file` / `source_path`
  - `extraction_confidence: failed`
  - 在 `風險與異常` 寫清楚失敗原因

## Bundled Script

批次匯入與修正使用：

`scripts/batch_ingest_lumentum_weeklies.py`

執行方式：

```powershell
python C:\Users\hsi67063\.codex\skills\weekly-summary\scripts\batch_ingest_lumentum_weeklies.py
```

如果要同步 Agent 版 skill，也要保持同一份腳本：

```powershell
python C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Agent\weekly-summary\scripts\batch_ingest_lumentum_weeklies.py
```

## Verification

完成後至少驗證：

- `Lumentum/Weekly Reports/` 下筆記數量是否合理
- `Lumentum/index.md` 是否可正常列出新筆記
- `Lumentum/log.md` 是否有本次匯入紀錄
- 抽樣至少 2 到 3 份不同 team / year 的筆記
- 若有 placeholder，確認原因是否真的是來源檔問題

## Current Implementation Note

目前這個 skill 是從 2026-04-08 的 Lumentum 週報批次整理流程抽出來的。若之後要支援其他公司或其他週報格式，應先擴充腳本與 routing，而不是直接改掉現有 Lumentum 規則。
