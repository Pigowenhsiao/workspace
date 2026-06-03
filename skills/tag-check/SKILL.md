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

## Vault Root

`/home/pigo/Documents/Pigo_Obsidian`

---

## 執行流程（實測修正版）

### Phase 1：分層探測（嚴禁一開始暴力掃描）

`find . -name "*.md" | xargs grep "^tags:"` 容易被 allowlist 拒絕。
**正確做法：分層 spot-check。**

**Step 1：讀取 Taxonomy SSOT**

```bash
cat /home/pigo/Documents/Pigo_Obsidian/12-Meta/tag-taxonomy.md
```

這是 canonical tag list，檢查它是否與實際使用 drift。

**Step 2：Spot-check 重點區域（不用 find/rg）**

```bash
ls /home/pigo/Documents/Pigo_Obsidian/00-Inbox/ | head -30   # 抽樣 inbox tags
ls /home/pigo/Documents/Pigo_Obsidian/08-Learning/01_AI-Agent/  # AI-Agent 相關 tags
ls /home/pigo/Documents/Pigo_Obsidian/08-Learning/02_Knowledge-Systems/  # Knowledge 相關
```

**Step 3：讀取具代表性的 notes frontmatter**

```bash
# 直接讀 note 檔案（前 30 行）
cat /home/pigo/Documents/Pigo_Obsidian/00-Inbox/2026-05-05_30-Agents-*.md | head -30
cat /home/pigo/Documents/Pigo_Obsidian/08-Learning/index.md | head -20
```

### Phase 2：每次 tag-check 都要檢查的 5 類問題

1. **Format Inconsistency**
   - 多詞 tag：有無統一用 `-` 連結（e.g., `ai-agent` vs `AI Agent`）
   - `#` 前綴：有沒有統一加（Obsidian proper tag 需 `#`）
   - 中文 tags：是否保持原生

2. **Taxonomy Drift**
   - `12-Meta/tag-taxonomy.md` 定義的 canonical tags 是否仍被使用
   - 有沒有新增的 tags 不在 taxonomy 內

3. **Source-Type Tags 未退場**
   - `twitter`、`youtube`、`article` 這類來源平台型 tags
   - 原則上應逐漸用 `classification_path` 取代

4. **同義 Tag 衝突**
   - `AI-Engineering` vs `AI-Agent` vs `ai-agent`
   - `claude-code` vs `Claude-Codex`
   - 需要人工判斷語意邊界

5. **Tag 使用頻率異常**
   - 只出現 1-2 次的低頻 tags
   - 超高頻 tags（可能該升級為 MOC 或分類）

### Phase 3：Output 寫入規範

**Tag Check Report 寫到：**
```
12-Meta/vault-tag-check-report-YYYY-MM-DD.md
```

**結構：**
```
1. 核心結論
2. Tag Taxonomy 現況（canonical vs actual）
3. Format Inconsistency 問題
4. Source-Type Tags 狀態
5. Low-risk 直接可處理清單
6. Pending Approval Plan
7. 建議下一步
```

---

## Tag Taxonomy SSOT

位於：`/home/pigo/Documents/Pigo_Obsidian/12-Meta/tag-taxonomy.md`

Canonical tags：

| 分類 | Tags |
|------|------|
| Area | `#area/work`、`#area/learning-knowledge-base` |
| Content Type | `#meeting`、`#project`、`#task`、`#note`、`#idea`、`#person`、`#moc`、`#daily`、`#weekly-review` |
| Work | `#work-log`、`#weekly-report`、`#improvement` |
| Learning | `#book`、`#course`、`#article-note`、`#topic-knowledge`、`#methodology`、`#ai-tools`、`#ai-agent`、`#claude-code` |

---

## Obsidian Tag 解析行為（重要）

- 嚴格來說 `#tag` 才算 Obsidian proper tag
- YAML frontmatter 的 `tags: []` 陣列中，陣列元素會被視為 tag
- **建議**：所有正式 tags 寫入 frontmatter `tags: []` 陣列，並加 `#` 前綴

---

## Risk-Tier Contract

- `Low-risk`
  可直接提出 format-only normalization 建議（大小寫、空白、連字號統一）。
- `Medium-risk`
  同義 tag 合併、taxonomy 更新、批次 retag 一律進 `Pending Approval Plan`。
- `High-risk`
  不在本 skill 裡重做整套 tag 模型，也不主動發明新的大分類 tag family。

---

## Tag Workflow

### 1. Tag Inventory

盤點：

- 總 tag 數量（抽樣估算，不用全量 find）
- 高頻 tag（spot-check 各 topic 目錄）
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

---

## Expected Output

輸出至少要有：

- `核心結論`
- `tag inventory`（format inconsistency、taxonomy drift、source-type tags 未退場）
- `format-only 問題`
- `merge candidates`
- `Pending Approval Plan`
- `建議下一步`

---

## 常見 mistake（犯過的，不要再犯）

1. **一開始就用 `find . -name "*.md" | xargs grep "^tags:"` 全量掃描** → 被 allowlist 拒絕，改用 spot-check + 讀取具代表性 note frontmatter
2. **跳過 `12-Meta/tag-taxonomy.md`** → 這是 SSOT，不先讀就無法判斷 drift
3. **只看 00-Inbox 的 tags** → 08-Learning、09-Article-Notes 都有各自的主流 tags
4. **只改 tag 不檢查主題是否應升級為 MOC/hub** → 高頻 tag 可能預示需要分類升級
5. **忽略 Obsidian 的 `#` 前綴解析規則** → YAML frontmatter 的 tags 若要被視為 proper tag，需加 `#`

---

## Handoff

`tag-check` 完成後，下一步通常是：

- 執行 format normalization（需授權）
- `inbox-triage`（00-Inbox 大量 tags 需整理）
- `vault-check` 複測
- `note-update`（單篇定點 tag 修正）
- `vault-reshape`（處理同義 tag 合併等 Medium risk）