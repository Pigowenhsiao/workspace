---
name: tag-check
description: Use when the user wants a low-frequency audit of vault tags, including orphan tags, duplicate tags, taxonomy drift, inconsistent formats, or tag usage that no longer matches the current knowledge structure.
---

# Tag Check

## Description

`tag-check` 是 Pigo vault 的 tag 專項檢查模式。  
它專注在 tag 格式一致性、taxonomy 漂移、近似 tag 合併候選與過度/過少使用的 tag，不取代結構重整，也不取代單篇整理。

## When to Use

使用時機：

- 你懷疑 tag 開始失控
- 有很多同義 tag、大小寫差異、格式不一致
- `vault-check` 指出 tag health 有問題
- 大量搬移或匯入後，需要重新盤點 tag

不要用在：

- 單篇筆記編修：改用 `note-update`
- 大範圍分類搬移：改用 `vault-reshape`
- 深度內容清理：改用 `vault-deep-clean`

## Vault Index Usage

目前 `.vault-index` 沒有專用 tag query，所以 `tag-check` 應先用 index 鎖定活躍分類與高頻主題區，再回到 frontmatter / 內容做精確 tag 檢查。

- Vault root：
  `C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian`
- Query tool：
  `C:\Users\hsi67063\Box\00-home-pigo.hsiao\VBA\Pigo_Obsidian\.vault-index\query_vault.py`

優先查這些：

- `by-classification`
- `fts`
- `related-notes`

原則：

1. 先找 tag 問題最可能集中的分類區
2. 再做精確 tag 掃描與比對
3. tag 語意合併一律保守處理

## Risk-Tier Contract

- `Low-risk`
  可直接提出 format-only normalization 建議，例如大小寫、空白、連字號統一。
- `Medium-risk`
  同義 tag 合併、taxonomy 更新、批次 retag 一律進 `Pending Approval Plan`。
- `High-risk`
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

- `核心結論`
- `tag inventory`
- `format-only 問題`
- `merge candidates`
- `Pending Approval Plan`

## Common Mistakes

- 沒先看分類上下文就直接合併 tag
- 把語意不同但字面相近的 tag 強行合併
- 只改 tag，不檢查該主題是否其實應升級為分類或 hub

## Handoff

`tag-check` 完成後，下一步通常是：

- `vault-check`
- `vault-reshape`
- `note-update`
