---
name: markitdown-first
description: 優先使用本機 ~/marky-env/bin/markitdown 將檔案、網頁與可讀 URL 轉成 markdown，再交給 llm-wiki / Obsidian / 摘要流程整理。用於使用者要你抓取檔案內容、抽取網頁正文、把 PDF/Office/HTML/URL 轉 markdown、或在整理知識前先做乾淨抽取時。
---

# markitdown-first

當任務的第一步是「把來源內容抽乾淨」時，優先使用這個 skill。

## 本機固定路徑

- venv: `/home/pigo/marky-env`
- CLI: `/home/pigo/marky-env/bin/markitdown`

不要假設系統 `python3` 或 PATH 上有 `markitdown`。

## 何時優先用它

優先處理這些來源：

- 本機檔案：PDF、docx、pptx、xlsx、csv、epub、ipynb、html、txt
- 使用者提供的網頁 URL
- 想先把內容轉 markdown 再整理進 Obsidian / llm-wiki 的任務

## 基本用法

### 檔案轉 markdown

```bash
/home/pigo/marky-env/bin/markitdown /path/to/file.pdf -o /tmp/file.md
```

### URL 轉 markdown

```bash
/home/pigo/marky-env/bin/markitdown "https://example.com/article" -o /tmp/article.md
```

### 輸出到 stdout

```bash
/home/pigo/marky-env/bin/markitdown /path/to/file.pdf
```

## 建議工作流

1. 先判斷來源是不是 markitdown 可吃的檔案或 URL
2. 先用 markitdown 做一次 markdown 抽取
3. 檢查抽取品質
4. 再交給後續流程：
   - llm-wiki
   - article-to-obsidian-knowledge
   - summarize
   - 手動整理成 Obsidian note

## 對 llm-wiki 的規則

當使用者是要「整理進 vault」而來源又是檔案或網頁時：

- 第一優先：`/home/pigo/marky-env/bin/markitdown`
- 第二優先：`web_fetch` 或其他可讀抓取工具
- 第三優先：其他平台專用 skill

不要一開始就直接把原始 URL 丟進摘要。先抽 markdown，再整理。

## 品質判斷

適合 markitdown：
- 需要正文
- 需要保留標題與段落結構
- 希望減少 HTML 雜訊

不適合只靠 markitdown：
- 需要登入後內容
- 強互動頁面
- X / Twitter 這種常有登入牆的平台
- 明顯被 bot protection 擋住的頁面

這些情況改走平台專用 skill 或其他抓取方式。

## 常見參數

- `-o, --output`: 輸出檔案
- `-x, --extension`: 指定副檔名提示
- `-m, --mime-type`: 指定 MIME type
- `-c, --charset`: 指定編碼
- `-p, --use-plugins`: 啟用 plugins
- `--list-plugins`: 列出 plugins
- `--keep-data-uris`: 保留 data URI
- `-v, --version`: 顯示版本

## 失敗時的處理

如果 markitdown 失敗：

1. 確認檔案存在或 URL 可達
2. 對 stdin 或無副檔名來源，補 `-x` / `-m`
3. 若是登入牆 / 平台限制，改用平台專用 skill
4. 若是一般網頁，再改用 `web_fetch`

## 一句話原則

**能先用 markitdown 抽成乾淨 markdown，就不要直接拿原始檔案或髒 HTML 開整理。**
