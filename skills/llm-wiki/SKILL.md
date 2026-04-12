---
name: llm-wiki
description: Use when ingesting external sources or work materials into Pigo's Obsidian wiki, especially when a workflow needs Obsidian-first filing, optional Notion input sync, index/log maintenance, cross-reference updates, git sync, or routing content into either the Learning area or the parallel Lumentum work knowledge area.
---

# LLM Wiki Skill

## Core Principle

Pigo 的 Obsidian vault 是一個由 LLM 維護的可累積知識庫，不是每次重新推理的暫存區。

實際主 vault：`C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian`

Human 負責挑來源、問問題、判斷價值。  
LLM 負責整理、結構化、交叉連結、維護索引與時間線。

**知識是一次編譯，然後保持最新——不是每次查詢時重新派生。**

**Query also improves wiki：** 在回答問題的過程中，如果發現兩個筆記明明相關卻未連結，要把這個發現寫回 wiki。查詢本身就是改進知識庫的動作。

---

## Two Parallel Knowledge Areas

### 1. Learning

`Learning/` 保留給外部學習型知識：
- YouTube
- Twitter/X
- 文章
- Notion 知識整理
- Repo 學習筆記

### 2. Lumentum

`Lumentum/` 是與 `Learning/` 平行的工作知識區，專門存放：
- 週報
- 會議筆記
- 專案追蹤
- 問題單 / 異常 / RMA / FA / customer issue

不要把 Lumentum 工作內容混寫進 `Learning/`。

---

## Three Core Actions

### Ingest

1. 讀取來源內容
2. 抽取重點，不逐字轉錄
3. 根據 routing rule 寫入正確區域
4. 更新該區域的 `index.md`
5. 必要時補上交叉連結
6. 更新該區域的 `log.md`
7. 若這次 ingest 屬於正式同步流程，再做 git commit + push

### Query

1. 先查 vault 現有內容
2. 用既有筆記回答
3. 若在回答過程中發現缺少連結、摘要或新關聯，**應寫回 wiki**
4. 若答案有長期價值（深度比較、系統性綜合），建立 `queries/` 或 `comparisons/` 頁面

### Lint（Step-by-Step）

當使用者要求整理、檢查 vault 健康狀況時，逐步執行：

① **孤兒頁面：** 尋找沒有 inbound `[[wikilinks]]` 的頁面（從未被其他頁面引用）

② **失效連結：** 尋找指向不存在的頁面的 `[[wikilinks]]`

③ **Index 完整性：** 每個 vault 頁面都應出現在 `index.md` 中

④ **Frontmatter 驗證：** 每個頁面必填欄位：title、source、source_url、processed、classification_path

⑤ **過時內容：** 實體頁面超過 90 天未更新，且新週報已有相關資訊覆蓋

⑥ **矛盾內容：** 同主題頁面出現不同聲明。標記兩者並標明日期，標題註明「需確認」

⑦ **頁面大小：** 單頁超過 200 行 → 候選分割

⑧ **Tag 審計：** 列出所有在用 tag，標記不在 taxonomy 的自由標籤

⑨ **Log 輪換：** `log.md` 超過 500 條目 → 輪換

⑩ **彙報結果：** 按嚴重度分組（失效連結 > 孤兒 > 過時 > 格式問題）

---

## Unified URL Ingest Pipeline

當使用者提供 YouTube / X / article / repo URL 並要求用 `llm-wiki` ingest 時，預設順序如下：

### Step 0 — URL 擷取策略（預設 defuddle，失敗回退）

- 一般網址（article / repo docs / web pages）預設先使用 `defuddle` 擷取正文 Markdown
- 若 `defuddle` 失敗、回傳空內容、或內容明顯不完整，立即回退到直接讀原頁
- YouTube、X/Twitter 等有既有專用流程的來源，仍優先走專用流程

### Step 1 — 寫入 Obsidian（最優先）

- 辨識來源型別：YouTube / X / article / repo
- 抽取必要 metadata：title、url、author、published date、source id
- 先寫入對應的 `Learning/` 子目錄
- frontmatter 至少保留：`source`、`source_url`、`processed: true`、`classification_path`

### Step 2 — Optional Notion input sync

如果這次流程有要求同步 Notion input database：

- 先查重
- 有則 update，無則 create
- 至少回填：title、URL、source、status

### Step 3 — Update index / log / cross-links

- 更新對應區域入口
- 補齊 related links / cross-links
- append `log.md`

### Step 4 — Git sync

只有在這次 ingest 明確屬於正式同步流程時才做：

- `git add -A`
- `git commit -m "..."`
- `git pull origin main --rebase`
- `git push origin main`

---

## Bulk Ingest（多個來源一次處理）

當一次攝入多個來源時，批次處理以減少重複更新：

1. 先把所有來源讀完
2. 一次識別所有實體和概念（一次搜尋，不是 N 次）
3. 對所有實體檢查現有頁面（一次搜尋，不是 N 次）
4. 批次建立/更新頁面
5. 最後一次更新 `index.md`
6. 寫一條涵蓋整批的 log 條目

---

## Page Thresholds（控制頁面數量）

- **建立新頁：** 實體/概念出現在 2+ 個來源，**或**在一個來源中處於核心位置
- **增加到現有頁：** 來源提到已存在的實體
- **不要建頁：** 僅一次提到的名字、過場細節、或偏離 vault 範圍的內容
- **分割大頁：** 超過 ~200 行 → 拆分成子主題並以 `[[wikilinks]]` 互連
- **歸檔：** 內容完全被取代 → 移至 `_archive/`，從 index 移除

---

## Zone-Local Index and Log

這個 vault 採用「區域自管」而不是單一全域 `index.md` / `log.md`。

### Learning

由 `Learning/` 下各子目錄依既有方式維護。

### Lumentum

固定維護：
- `Lumentum/index.md`
- `Lumentum/log.md`

`log.md` 格式固定為：

`## [YYYY-MM-DD] <action> | <description>`

---

## Routing Rules

| Source type | Destination |
| --- | --- |
| YouTube / Twitter / article / external learning content | `Learning/*` |
| Lumentum weekly report | `Lumentum/Weekly Reports/<year>/` |
| Lumentum meeting notes | `Lumentum/Meetings/` |
| Lumentum project notes | `Lumentum/Projects/` |
| Lumentum issue / RMA / FA / abnormality note | `Lumentum/Issues/` |

---

## Weekly Report Rule

Lumentum 週報一律視為結構化工作知識，而不是學習資料。

### Path format

`Lumentum/Weekly Reports/<year>/CY<yy>W<ww> - <title>.md`

### Required frontmatter

- `title`
- `company: Lumentum`
- `workspace: Lumentum`
- `type: weekly-report`
- `team`
- `cycle_year`
- `week`
- `source_file`
- `source_path`
- `tags`

### Required sections

- `## 核心摘要`
- `## 本週重點`
- `## 風險與異常`
- `## 待追蹤事項`
- `## 我會怎麼用這份週報`
- `## Source`

### Relationship indexing

對週報做 index / lint 時，除了年度與週次索引，還要維護兩種「可查找主 key」：

- `RMA / Issue key`
- `Customer key`

預設維護方式：

- `Lumentum/Issues/index.md`
- `Lumentum/Issues/RMA Keys/<slug>.md`
- `Lumentum/Customers/index.md`
- `Lumentum/Customers/Keys/<slug>.md`

每次重建 weekly report index 時，應：

1. 從週報筆記抽出 `RMA / Issue key`
2. 從同一筆記抽出 `Customer key`
3. 讓同一 issue page 能回到所有相關週報
4. 讓同一 customer page 能回到所有相關週報
5. 在 issue/customer page 中保留對向關聯

---

## 矛盾處理政策（Update Policy）

當新資訊與現有內容矛盾時：

1. 檢查日期——新來源通常覆蓋舊來源
2. 若確實矛盾，兩者都保留並標明日期和來源
3. 在 frontmatter 標記：`contradictions: [page-name]`
4. 在 Lint 報告中標記為「需用戶確認」

---

## Writing Standard

- 用結構化摘要，不要只是貼原文
- 保留產品、客戶、owner、風險、deadline、RMA/FA 關聯
- 如果週報提到可持續追蹤的議題，可在 `Issues/` 或 `Projects/` 建立後續筆記並互連
- 如果只是單次事件，至少要在週報筆記中留下清楚可搜尋的關鍵字

---

## Preferred Note Template (Pigo Longform)

當使用者明確要求「照指定格式整理筆記」或提到 `NotebookLM / Notion 內容重寫` 時，優先套用以下章節順序：

1. `## 核心摘要`
2. `## 文章分析`
3. `## 關鍵知識點`
4. `## 我會怎麼用這篇文章`
5. `## 全文（繁中重寫）`
6. `## 原文區塊`
7. `## Source`
8. `## 關聯筆記`

補充規則：

- 若來源資訊不足，必須在 `文章分析` 或 `風險與限制` 明確標記「已驗證內容邊界」
- `原文區塊` 只保留可驗證原文，不要補寫未驗證段落
- `Source` 必須包含可追溯欄位（URL、頁面 ID、擷取時間、平台屬性）
- `關聯筆記` 優先連到該領域 index / MOC 與同主題高相關筆記

完整範本與示例見：

- `references/pigo-note-format-notebooklm-chrome-plugins.md`

---

## Query Behavior

當 Pigo 問工作問題時：

1. 先查 `Lumentum/`
2. 若是學習性問題再查 `Learning/`
3. 若查詢過程中發現缺少連結、摘要或新關聯，應寫回 wiki
4. 若答案有長期價值，建立 `queries/` 或 `comparisons/` 頁面並更新 index

---

## Pitfalls（常見錯誤）

- **不要修改 raw sources：** 原始來源不可變，修正寫入 wiki 頁面
- **寫入前先讀現有 index/log：** 跳過這步會造成重複頁面和遺漏交叉連結
- **每次 ingest 後更新 index 和 log：** 跳過會讓 vault 退化
- **不要為一次提到的內容建頁：** 遵守 Page Thresholds
- **每個頁面至少 2 個 outbound wikilinks：** 孤立頁面等於看不見
- **Frontmatter 必填：** 它是搜索、過濾、與过期檢測的基礎
- **Tag 必須來自 taxonomy：** 自由標籤會變成噪音
- **大頁面要分割：** 單頁應在 30 秒內可讀完
- **大規模更新前先確認範圍：** 如果一次 ingest 影響 10+ 現有頁面，先跟用戶確認
- **處理矛盾時不要靜默覆寫：** 標記兩者並標明日期

---

## References

- `references/llm-wiki-architecture.md` — LLM Wiki 原始概念（Karpathy）
- `references/agents-md-guide.md` — Schema-layer 引導
- `references/pigo-note-format-notebooklm-chrome-plugins.md` — Pigo Longform 範本與示例
