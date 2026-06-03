---
name: vault-deep-clean
description: Use when the user wants a low-frequency but thorough vault cleanup focused on stale content, duplicate clusters, broken links, template drift, and accumulated maintenance debt after an audit or major reorganization.
---

# Vault Deep Clean

## Description

`vault-deep-clean` 是 Pigo vault 的深度維護模式。
它處理的是 stale content、重複競爭頁、失效連結、模板漂移與累積性維護債，不負責主題分類改版，也不應取代單篇整理流程。

## When to Use

使用時機：

- vault 已累積一段時間，開始出現 stale notes、重複頁與失效入口
- `vault-check` 已找出大量 hygiene 問題，需要進一步清理
- 大批搬移或重分類後，需要補做深度修復
- 你懷疑有很多歷史殘留頁面、舊橋接頁、無效 Source、模板飄移

不要用在：

- 單篇筆記正式化：改用 `note-update`
- 結構改版與分類收斂：改用 `vault-reshape`
- 只想先做盤點：先用 `vault-check`

## Vault Root

`/home/pigo/Documents/Pigo_Obsidian`

---

## 執行流程（2026-05-10 實測修正版）

### Phase 1：結構探測（嚴禁一開始就暴力掃描）

Vault 有大量目錄，直接用 `find . -name "*.md" | wc -l` 或 `rg` 很容易觸發 allowlist 限制。
**正確做法：分層探測。**

**Step 1：用 `ls` 建立地圖**

```bash
ls /home/pigo/Documents/Pigo_Obsidian/          # vault 根目錄
ls /home/pigo/Documents/Pigo_Obsidian/00-Inbox/ # inbox 現況
ls /home/pigo/Documents/Pigo_Obsidian/08-Learning/ # 學習區結構
ls /home/pigo/Documents/Pigo_Obsidian/09-Article-Notes/ # 文章區結構
ls /home/pigo/Documents/Pigo_Obsidian/10-LLM-Wiki/ # 確認舊 runtime 殘留
```

**Step 2：用 `ls` 對重點區域做 spot-check**

- `ls 10-LLM-Wiki/` → 確認 entities/log/raw 是否仍存在
- `ls 12-Meta/` → 確認有哪些維護文件
- `ls 11-MOC/` → 確認導航層狀態

**Step 3：用 `find` 對特定問題做 targeted 查詢**

```bash
# 查舊分類殘留（被 skill 禁止的舊路徑）
find . -path "*/08-Learning/articles/" -o -path "*/08-Learning/youtube/" ...

# 查 staging/backup 檔
ls *.bak.md 2>/dev/null || echo "none"
ls *.bak 2>/dev/null || echo "none"
```

### Phase 2：分類掃描重點

**每次 deep-clean 都要檢查這 5 類：**

1. **`10-LLM-Wiki/` 舊內容**
   - 現已遷移到 `~/.openclaw/workspace/skills/llm-wiki/`
   - Vault 內的 `10-LLM-Wiki/` 純為 runtime references，不放正式內容
   - 常見殘留：`log.md`、`entities/`、`raw/`、`README.md`
   - 處理原則：確認無 inbound links → 移至 `04-Archive/`

2. **Vault Root 過渡檔**
   - 常見模式：`AGENTS.*.bak.md`、`STATUS_*.md`、`skill_diff_*.json`、`skill_sync_*.log`
   - `CLAUDE.md` at root（可能是備份或遷移殘留）
   - 處理原則：確認非必要 → 移至 `04-Archive/sync-archive/`

3. **命名異常目錄**
   - `01.1-TEST STUDY/`（多了一個 dot）
   - `Archive 5j/`（非常規命名）
   - 處理原則：進 `Pending Approval Plan`

4. **Source 型分類殘留**
   - `08-Learning/twitter/`、`08-Learning/youtube/`、`08-Learning/news/`
   - 這些是 source-type 分類，vault 目前的共識是逐漸收納成 topic-type
   - 處理原則：已有對應 topic 的內容應遷移；純 sources 的可保留但檢查是否有進階

5. **00-Inbox 累積量**
   - 超過 30 筆未整理時，建議本週執行一次 `inbox-triage`
   - 不在 deep-clean 內批次處理，但應報告讓使用者知道

### Phase 3：Output 寫入規範

**Deep Clean Report 寫到：**
```
12-Meta/vault-deep-clean-report-YYYY-MM-DD.md
```

**結構：**
```
1. 核心結論
2. 逐類問題（stale content / staging files / naming anomalies / inbox overflow）
3. Low-risk 直接可處理清單
4. Pending Approval Plan（Medium/High risk）
5. 建議下一步
```

---

## Risk-Tier Contract

- `Low-risk`（可直接執行）
  - 純過渡檔搬遷（`.bak`, `.log`, `.json` staging 檔）
  - `10-LLM-Wiki/entities/` 或 `raw/` 這類確認無 inbound links 的舊 runtime 殘留歸檔
  - 明確的 duplicate 檔刪除

- `Medium-risk`（進 Pending Approval Plan）
  - 命名異常目錄（`01.1-TEST STUDY/`、`Archive 5j/`）
  - 批量 staging 檔處理（`STATUS_*.md` 這類不確定用途的）
  - 需要合併的 competition pages

- `High-risk`（進 `vault-reshape`）
  - 結構重分類
  - Taxonomy redesign
  - 大規模內容遷移

---

## Deep Clean Workflow

### 1. Stale Content Scan

檢查重點：
- `10-LLM-Wiki/` 舊內容（log.md、entities/、raw/、README.md）
- 已被新筆記取代但仍存在的舊摘要頁
- vault root 的狀態/staging 檔（`STATUS_*.md`、`AGENTS.*.bak`）

### 2. Duplicate And Competition Review

檢查重點：
- 同主題競爭頁（可用 `ls` spot-check 各 topic 目錄）
- 同來源競爭頁
- 應合併但尚未合併的橋接頁與舊版本

### 3. Link And Source Repair

檢查重點：
- `10-LLM-Wiki/` 內的 wikilinks 是否仍有效
- 指向舊 vault 路徑（如 `C:\Users\...`）的殘留連結
- 指向已廢棄 `10-LLM-Wiki/` 內容的 inbound links

### 4. Template And Metadata Drift

檢查重點：
- frontmatter 漂移（format 不一致）
- `classification_path` 與實際路徑不一致
- `processed` / `status` 過時

### 5. Cleanup Plan

**輸出格式：**
- Low-risk：可直接執行的動作清單
- Medium/High-risk：`Pending Approval Plan`，含精確路徑、建議動作、回滾方式

---

## Expected Output

輸出至少要有：

- `核心結論`
- `主要深層問題`
- `Low-risk 直接可處理清單`
- `Pending Approval Plan`
- `建議下一步`

---

## 常見 mistake（犯過的，不要再犯）

1. **一開始就用 `find . -name "*.md" | wc -l"計數** → 被 allowlist 拒絕，正確做法是用分層 `ls` spot-check
2. **以為 `10-LLM-Wiki/` 還是內容目錄** → 它已經是 runtime package，所有正式內容都在 vault 正式分類
3. **用 `rg` 或 `find -path "*/08-Learning/articles/"` 做複雜查詢** → 容易被 allowlist 擋，改用 `ls` 確認存在性
4. **忘記 vault root 也是 staging 檔的溫床** → staging/backup/status 檔常在 vault root
5. **把所有問題一次處理** → 這次沒有的風險分級，導致執行量過大

---

## Handoff

`vault-deep-clean` 完成後，下一步通常是：

- 執行 Low-risk cleanup（需使用者授權）
- `vault-check` 複測
- `inbox-triage`（如果 inbox 累積過多）
- `note-update`（單篇定點修補）
- `vault-reshape`（處理 Medium/High risk 的結構問題）
- `tag-check`