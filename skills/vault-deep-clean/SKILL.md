---
name: vault-deep-clean
description: Use when the user wants a low-frequency but thorough vault cleanup focused on stale content, duplicate clusters, broken links, template drift, and accumulated maintenance debt after an audit or major reorganization.
---

# Vault Deep Clean

## Description

ault-deep-clean 是 Pigo vault 的深度維護模式。  
它處理的是 stale content、重複競爭頁、失效連結、模板漂移與累積性維護債，不負責主題分類改版，也不應取代單篇整理流程。

## When to Use

使用時機：

- vault 已累積一段時間，開始出現 stale notes、重複頁與失效入口
- ault-check 已找出大量 hygiene 問題，需要進一步清理
- 大批搬移或重分類後，需要補做深度修復
- 你懷疑有很多歷史殘留頁面、舊橋接頁、無效 Source、模板飄移

不要用在：

- 單篇筆記正式化：改用 
ote-update
- 結構改版與分類收斂：改用 ault-reshape
- 導航與 hub 治理：改用 ault-GPS
- 只想先做盤點：先用 ault-check

## Vault Index Usage

ault-deep-clean 要先用 vault index 縮小問題範圍，再對高風險候選做逐檔檢查。

- Vault root：
  C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian
- Query tool：
  C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian\.vault-index\query_vault.py
- Database：
  C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian\.vault-index\notes.db

優先查這些：

- duplicate-candidates
- ts
- elated-notes
- links-to
- links-from

原則：

1. 先用 index 找 stale cluster、duplicate cluster、link hotspot
2. 再對高風險候選做逐檔深查
3. 只有在 index 無法覆蓋細節時才 fallback 到 g

## Risk-Tier Contract

- Low-risk
  可直接產出候選清單、統計、明確可逆的 cleanup 建議與局部 deterministic fix。
- Medium-risk
  不直接執行批次合併、批次刪除或大範圍替換。先整理成 Pending Approval Plan。
- High-risk
  不在本 skill 內直接做 taxonomy redesign、結構改版或大規模語意合併。

## Deep Clean Workflow

### 1. Stale Content Scan

檢查：

- 長期未更新但仍被當成入口的頁面
- 已被新筆記取代的舊摘要頁
- 只剩歷史價值但仍佔據主要導航位置的頁面

### 2. Duplicate And Competition Review

檢查：

- 同主題競爭頁
- 同來源競爭頁
- 應合併但尚未合併的橋接頁與舊版本

### 3. Link And Source Repair

檢查：

- broken wikilinks
- stale Source 區塊
- 指向舊分類或舊標題的入口
- 只剩單向鏈接的半孤兒頁面

### 4. Template And Metadata Drift

檢查：

- frontmatter 漂移
- classification_path 與實際路徑不一致
- processed / status 過時
- 舊模板殘留欄位

### 5. Cleanup Plan

輸出：

- 可直接處理的 low-risk 修補
- 需要人工核准的 Pending Approval Plan
- 建議交給 ault-reshape 或 
ote-update 的後續工作

## Expected Output

輸出至少要有：

- 核心結論
- 主要深層問題
- duplicate / stale / broken-link 候選
- Pending Approval Plan
- 建議下一步

## Common Mistakes

- 把 ault-deep-clean 當成結構重整工具
- 沒做候選預篩就直接全 vault 暴力清理
- 把語意合併與格式修補混在同一批次亂做
- 清掉舊頁，但不補入口與回滾路徑

## Handoff

ault-deep-clean 完成後，下一步通常是：

- ault-check
- 
ote-update
- ault-reshape
- 	ag-check
"@

 = @"
---
name: tag-check
description: Use when the user wants a low-frequency audit of vault tags, including orphan tags, duplicate tags, taxonomy drift, inconsistent formats, or tag usage that no longer matches the current knowledge structure.
---

# Tag Check

## Description

	ag-check 是 Pigo vault 的 tag 專項檢查模式。  
它專注在 tag 格式一致性、taxonomy 漂移、近似 tag 合併候選與過度/過少使用的 tag，不取代結構重整，也不取代單篇整理。

## When to Use

使用時機：

- 你懷疑 tag 開始失控
- 有很多同義 tag、大小寫差異、格式不一致
- ault-check 指出 tag health 有問題
- 大量搬移或匯入後，需要重新盤點 tag

不要用在：

- 單篇筆記編修：改用 
ote-update
- 大範圍分類搬移：改用 ault-reshape
- 深度內容清理：改用 ault-deep-clean

## Vault Index Usage

目前 .vault-index 沒有專用 tag query，所以 	ag-check 應先用 index 鎖定活躍分類與高頻主題區，再回到 frontmatter / 內容做精確 tag 檢查。

- Vault root：
  C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian
- Query tool：
  C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian\.vault-index\query_vault.py

優先查這些：

- y-classification
- ts
- elated-notes

原則：

1. 先找 tag 問題最可能集中的分類區
2. 再做精確 tag 掃描與比對
3. tag 語意合併一律保守處理

## Risk-Tier Contract

- Low-risk
  可直接提出 format-only normalization 建議，例如大小寫、空白、連字號統一。
- Medium-risk
  同義 tag 合併、taxonomy 更新、批次 retag 一律進 Pending Approval Plan。
- High-risk
  不在本 skill 裡重做整套 tag 模型，也不主動發明新的大分類 tag family。

## Tag Workflow

### 1. Tag Inventory

盤點：

- 總 tag 數量
- 高頻 tag
- 只出現 1 到 2 次的 tag
- 同義或近似 tag 候選

### 2. Format Review

檢查：

- 大小寫不一致
- 多詞 tag 格式不一致
- 舊命名殘留
- 明顯 typo

### 3. Taxonomy Drift Review

檢查：

- tag 是否仍符合當前分類與知識模型
- 是否有來源型 tag 其實應退場
- 是否有主題已成熟但 tag 仍停在臨時狀態

### 4. Merge Candidates

輸出：

- 建議保留的 canonical tag
- 建議合併的近似 tag
- 建議退休的舊 tag

## Expected Output

輸出至少要有：

- 核心結論
- 	ag inventory
- ormat-only 問題
- merge candidates
- Pending Approval Plan

## Common Mistakes

- 沒先看分類上下文就直接合併 tag
- 把語意不同但字面相近的 tag 強行合併
- 只改 tag，不檢查該主題是否其實應升級為分類或 hub

## Handoff

	ag-check 完成後，下一步通常是：

- ault-check
- ault-reshape
- 
ote-update
"@

 = @"
---
name: transcript-to-note
description: Use when the user has transcript text, meeting notes, lecture transcripts, podcast transcripts, or transcript-like material that should be turned into a structured Obsidian note before later filing or formalization.
---

# Transcript To Note

## Description

	ranscript-to-note 是 transcript intake skill。  
它把逐字稿、會議轉寫、課程 transcript、podcast transcript 或 transcript-like text 轉成結構化 Obsidian 筆記初稿，之後再交給 
ote-update 或 inbox-triage 進一步正式化與歸檔。

## When to Use

使用時機：

- 使用者已經有 transcript text
- 你要把會議、講座、podcast、訪談轉成可整理筆記
- 需要先抽出決策、行動項、關鍵知識點，再決定要不要正式歸檔

不要用在：

- 只有 raw audio 且沒有可讀文字時，這個 skill 不做原始語音辨識
- 已經是成熟正式筆記時，改用 
ote-update
- 只是要做整體分類搬移時，改用 ault-reshape

## Vault Index Usage

在轉寫內容進 note 之前，先用 vault index 查是否已有同主題或同來源正式頁，避免生成完全脫節的新草稿。

- Vault root：
  C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian
- Query tool：
  C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian\.vault-index\query_vault.py

優先查這些：

- ts
- 	itle-candidates
- elated-notes
- y-classification

## Intake Workflow

### 1. Source Gate

先分辨：

- 是否已有 transcript text
- 是否只是 raw audio
- 是否已有說明主題、講者、日期、用途

若只有 raw audio，應明確告知需要先取得 transcript text。

### 2. Transcript Structuring

將 transcript 轉成：

- 核心摘要
- 關鍵段落 或 主題區塊
- 決策 / 行動項（如果是會議）
- 關鍵知識點（如果是內容型 transcript）
- 待確認問題

### 3. Destination Decision

根據內容決定：

- 先進  0-Inbox
- 或直接交由 
ote-update 正式化
- 或標記為某一分類的候選

## Expected Output

輸出至少要有：

- 來源說明
- 核心摘要
- 結構化內容
- 可能的目標分類
- 下一步建議

## Common Mistakes

- 把 raw audio 當成 transcript text 直接處理
- transcript 太長卻不分段
- 沒有抽出決策與行動項
- 生成草稿後完全不考慮既有正式筆記

## Handoff

	ranscript-to-note 完成後，下一步通常是：

- 
ote-update
- inbox-triage
- ault-GPS
"@

 = @"
---
name: vault-bootstrap
description: Use when initializing a brand-new vault or workspace that needs first-time structure, conventions, templates, and navigation rather than maintenance on an already mature vault.
---

# Vault Bootstrap

## Description

ault-bootstrap 是新 vault / 新 workspace 的起始建置 skill。  
它不適合直接拿來重做成熟中的 Pigo 主 vault；在目前 Codex runtime 中，應把它視為規劃與初始化入口，而不是日常維護工具。

## Current Mode

目前為 deferred-mode 安裝版本：

- 可用來規劃新 vault 的初始化結構
- 可用來定義基本分類、模板與導航層
- 不應直接重做既有成熟 vault 的骨架

## Handoff

成熟 vault 的日常維護請改用：

- ault-check
- ault-reshape
- ault-GPS
"@

 = @"
---
name: agent-create
description: Use when the user wants to define a brand-new custom vault or workflow agent with a dedicated role, trigger conditions, boundaries, and output contract.
---

# Agent Create

## Description

gent-create 是建立新 agent 的入口 skill。  
目前先以 planning-first 模式安裝，適合定義新 agent 的用途、邊界與輸出契約，不建議在沒有明確需求時大量生成 agent。

## Current Mode

- 先做 role 定義
- 先做 trigger 與邊界設計
- 真正落地前，先確認是否現有 skill 已足夠
