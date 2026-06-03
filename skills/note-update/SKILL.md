---
name: note-update
description: "Use when an existing Obsidian note should be upgraded into a formal knowledge note, moved out of Inbox into a better category, linked to related notes, indexed, or minimally backfilled into nearby notes without doing a full vault ingest or lint pass. **新筆記落地點永遠是 00-Inbox/，完成後再移至正式分類。**"
---

# Note Update

## Description

`note-update` 用來把既有筆記升級成正式的 Obsidian 知識筆記，而不是單純保存原文或只做小修小補。

它適合處理：

- `00-Inbox` 半成品筆記正式昇級
- 既有筆記的結構重寫與內容整理
- 重新判斷更適合的分類位置
- 補 `[[wikilinks]]`、`相關筆記`、`分類索引`
- 對直接相關的既有筆記做最小必要的反向修補

它不負責：

- 從 URL / YouTube / X / PDF 抓原始來源
- 全 vault ingest
- 全域 lint
- Notion sync
- git sync 正式發布流程

這些仍應交給 `llm-wiki` 或其他專用技能。

## Persistent Wiki Node

`note-update` 的目標不是把單篇筆記修飾漂亮，而是把它變成 wiki 裡可持續累積、可被引用、可被更新的節點。

處理後的筆記應當：

- 能被未來查詢與重用
- 能落在正確分類之下
- 能和周邊主題形成穩定連結
- 能在新資訊出現時被持續更新，而不是被新檔案取代

## When to Use

在以下情況使用：

- 使用者要把某篇既有筆記「轉正式」
- 使用者要把 `00-Inbox` 筆記搬到更正確的類別
- 使用者要補筆記之間的關聯、相關筆記、分類索引入口
- 使用者嫌某篇筆記目前只是摘要，不像可回用的知識
- 查詢或整理過程中，已經知道某篇筆記應當被重寫或重新分類

不要在以下情況使用：

- 還沒有本地筆記，只有原始來源
- 要做整個知識庫的批次清理
- 要重新抓取大量來源或同步外部資料

## Control Plane

更新任何筆記前，先讀過優先層級規範：

1. user instruction
2. `AGENTS.md`
3. `SCHEMA.md`
4. 本 skill

若規範衝突，先遵守更高優先順序，再做最小安全更新。

## Vault Path & Index

- Vault root：`/home/pigo/Documents/Pigo_Obsidian`
- 現有 vault index 可用則用，否則 fallback 到 `rg` 或直接掃描

### 新筆記落地規則（強制）

**所有新筆記落地點永遠是 `00-Inbox/`**，完成整理分類後再搬至正式位置。

- `llm-wiki` 負責把外部來源攝入並先放到 `00-Inbox/`
- `note-update` 負責把 `00-Inbox/` 裡的半成品昇級、搬移到正確分類
- 禁止把新內容直接寫入 `08-Learning/` 正式子目錄（必須先經過 `00-Inbox/`）

### 現有 vault 結構（08-Learning 為主要內容區）

| 分類 | 路徑 |
|------|------|
| AI Agent / Workflow / 工程 | `08-Learning/01_AI-Agent/` |
| 知識系統 / Notion / Obsidian / NotebookLM | `08-Learning/02_Knowledge-Systems/` |
| Prompt / Context Engineering | `08-Learning/03_Prompt-Context-Engineering/` |
| 工具 / Repo / CLI / Framework | `08-Learning/04_AI-Engineering-Tools/repos/` |
| 研究論文 / arXiv | `08-Learning/05_Research-Papers/` |
| 商業 / 財經 | `08-Learning/07_Business-Finance/` |
| 創作應用 / Design / Media | `08-Learning/08_Creative-Applications/` |
| 一般學習 / 通識 | `08-Learning/09_General-Learning/` |
| Newsletter / Digest 攝入 | `08-Learning/news/` |
| 未整理來源緩衝 | `00-Inbox/` |
| Twitter / X 推文 | `08-Learning/twitter/` |
| YouTube 影片筆記 | `08-Learning/youtube/` |
| 一般文章 / 指南 | `09-Article-Notes/` |

## Core Workflow

### 1. Read the local note first

- 讀原筆記全文，不要直接重寫
- 看清它目前是：
  - 原文摘要
  - 半成品整理
  - 已有部分結構的正式筆記

### 2. Reclassify before rewriting

- 不迷信原始來源素材
- 依筆記真正的知識用途決定分類
- 優先問這篇筆記未來要被怎麼被找回重用，而不是它來自哪個平台

例如：
- YouTube 來源，但主體是 agent workflow 方法論
  - 應放 `08-Learning/01_AI-Agent/`（而非 `youtube/`）
- X thread 來源，但主體是工具比較
  - 可能應放工具或 framework 分類，而非 `twitter/`

### 2.1 Duplicate resolution policy

若發現來源重複、內容高度重疊，或 vault 內已存在等效正式筆記，優先做合併，而不是再產生一篇競爭版本。

判斷原則：

- 同來源、同主題、內容大幅重疊：合併到既有正式筆記
- 同主題但角度不同、用途不同：保留各自立場，改做串連連結

合併時要：

- 保留 source trace
- 保留值得留下的補充內容
- 避免留下兩篇平行但互相競爭的正式筆記

### 3. Rewrite into a formal knowledge note

把內容改寫成可重用知識，不只是影響摘要或原文摘要。

預設應包含：

- `## 核心摘要`
- `## 文章分析` 或等效分析段落
- `## 關鍵知識點`
- `## 我會怎麼用這篇文章`
- `## 全文（繁中重寫）`
- `## Source`
- `## 相關筆記`

若來源不適合全部段落，可微調，但必留：

- 核心摘要
- 可重用知識點
- Source
- 相關筆記

### 3.1 Preserve full-item pages when needed

若來源頁面或來源筆記本身是一篇含多個完整條目的文，整理時要優先保留「逐項完整內容」，而不是先榨成 highlights。

典型情況包括：

- weekly report 首頁的多項 issue / audit / RMA overview
- 一頁同時列出多個 customer case
- 一頁含多個 action item / owner / due date

這種情況下：

- 依條目逐項整理
- 保留每個 item 的數字、owner、時程、客戶、風險與後續行動
- 不可只留下一段摘要或一週更新

## Relationship Rules

建立關係時，至少做這四件事：

1. **正文內 wikilinks**
   - 對可重用概念、工具、框架、人物、方法建立 `[[wikilinks]]`
   - 不要每個名詞都連，只連未來可能被單獨查詢的項目

2. **顯式相關筆記段落**
   - 在 `## 相關筆記` 列出最直接的 3 到 8 篇相關筆記
   - 優先連到同分類 MOC、同主題核心筆記、上游框架筆記

3. **分類索引入口**
   - 把這篇筆記加入對應分類 `index.md`
   - 若該分類有 parent index，也要確保可被上層發掘

4. **反向可發掘性**
   - 若某篇既有筆記明顯應連回這篇新正式筆記，做最小必要串寫
   - 只修直接相關筆記，不做大規模重構

## Index and Log Roles

- `index.md`：內容導航與收納入口，目的是讓這篇筆記能被發掘
- `log.md`：時間序列記錄，目的是保留這次更新、合併、重分類的脈絡

不要把 `index.md` 寫成操作日誌，也不要把 `log.md` 寫成分類清冊。

## Minimal Backfill Policy

`note-update` 可以修補既有筆記，但必必制約。

允許：

- 補一兩個直接相關的 `[[wikilinks]]`
- 在同主題 index 補入口
- 在高度相關的參照筆記補一行 related note

不允許：

- 批次掃全 vault
- 一次修改十幾篇臨近筆記
- 循序改寫多個分類命名
- 把單篇更新變成大型知識庫重構

原則是：**讓這篇筆記變得可發掘、可連回、可重用，就停。**

## Proportional Surrounding Repair

更新單篇筆記時，若發現周邊 wiki 存在明顯缺漏，應做比例適當的修補。

可修的情況：

- 缺少最關鍵的反向連結
- 顯然應存在的分類入口未收納
- 已有頁面中的說法被這次整理結果明確更新

不應擴展成：

- 全 vault 清理
- 大規模 rename
- 全主題重寫

原則是：**讓 surrounding wiki 因這次更新而更一致，但不失控。**

## Output Standard

- 一律使用繁體中文，除非使用者另有要求
- 保留來源追蹤資訊
- 若原文內容不足，明確標示不足，不造假內容
- 標題與檔名應以未來查詢與重用為優先，而不是只貼近原平台標題

## Division of Labor with llm-wiki

`llm-wiki`：

- 管理個 wiki 的 ingest / query / lint / routing / index / log 規範
- 管理來源型工作流與領域分類路由

`note-update`：

- 管理單篇筆記的昇級、分類整頓、關聯建立、最小反向修補

實務上：

- 先用 `llm-wiki` 把內容進 vault
- 再用 `note-update` 把單篇筆記昇級成正式知識筆記

## Quick Checklist

處理完成前，確認：

- 這篇筆記是否已放到更合適的分類？
- 內容是否已從摘要昇級成可重用知識？
- 是否已補上 `[[wikilinks]]`？
- 是否已有 `## 相關筆記`？
- 是否已更新對應 `index.md`？
- 是否只做了最小必要的反向修補？
- 是否保留了 `## Source` 與追蹤資訊？
- **`00-Inbox/` 筆記已整理完畢並搬至正式位置？未完成者應留在 `00-Inbox/` 彙整**

## Mini Lint After Update

完成單篇更新後，至少再檢查一次：

- 這篇是否仍是 orphan
- 是否與既有正式筆記重複
- 是否已被正確 `index.md` 收納
- 是否缺少最重要的 2 到 5 個關聯入口
- 是否有 stale wording 應陸續修正

若 vault index 可用，優先用它做：

- `duplicate-candidates`
- `related-notes`
- `links-to / links-from`

若以上有明顯問題，先做最小修補，再視為完成。

## Example

情況：

- 一篇放在 `00-Inbox/` 的筆記，來源是 YouTube
- 內容主體其實是 Anthropic 多智能體協作模式與 agent workflow

正確做法：

- 不要機械式放回 `youtube/`
- 應移到更適合的知識分類，例如 `08-Learning/01_AI-Agent/Agent-Workflow/`
- 重寫成正式知識筆記
- 補上與 `[[llm-wiki]]`、`[[Claude-Code]]`、`[[Multi-Agent-System]]` 等的關聯
- 更新該分類 `index.md`
- 對一篇直接相關筆記補最小反向入口
- 確認已從 `00-Inbox/` 移出
