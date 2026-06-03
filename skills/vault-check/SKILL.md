---
name: vault-check
description: Use when the user wants a low-frequency full-vault health check for duplicates, broken links, orphan notes, frontmatter drift, or classification inconsistency before deeper cleanup or restructuring.
---

# Vault Check

## Description

`vault-check` 是 Pigo vault 的低頻全局檢查模式。
它的工作不是大量改檔，而是先用 vault index 做候選聚焦，再輸出一份可執行的健康檢查結果、風險分級與後續建議。

## When to Use

使用時機：

- 你要做整個 vault 的健康檢查
- 你懷疑有重複筆記、孤島筆記、分類漂移或 index 遺漏
- 大量搬移、合併或重分類之前，要先聚焦風險
- `vault-reshape` 或 `vault-deep-clean` 執行前後，需要一份基準報告

不要用在：

- 單篇筆記正式化：改用 `note-update`
- `00-Inbox` 小批次整理：改用 `inbox-triage`
- 大規模結構重整：改用 `vault-reshape`
- 深度修補與批次清理：改用 `vault-deep-clean`

## Vault Root

`/home/pigo/Documents/Pigo_Obsidian`

---

## 執行流程（實測修正版）

### Phase 1：分層探測（嚴禁一開始暴力掃描）

Vault 有大量目錄，直接用 `find . -name "*.md" | wc -l` 或 `rg` 很容易觸發 allowlist 限制。
**正確做法：分層 spot-check + targeted 查詢。**

**Step 1：建立 vault 地圖**

```bash
# 根目錄結構造形
ls /home/pigo/Documents/Pigo_Obsidian/

# 重點區域 spot-check
ls /home/pigo/Documents/Pigo_Obsidian/00-Inbox/ | head -30    # inbox 現況
ls /home/pigo/Documents/Pigo_Obsidian/08-Learning/          # 學習區結構
ls /home/pigo/Documents/Pigo_Obsidian/09-Article-Notes/      # 文章區結構
ls /home/pigo/Documents/Pigo_Obsidian/10-LLM-Wiki/           # 確認舊 runtime 無正式內容
ls /home/pigo/Documents/Pigo_Obsidian/12-Meta/               # 維護文件
ls /home/pigo/Documents/Pigo_Obsidian/11-MOC/                 # 導航層
```

**Step 2：Targeted 問題查詢（用 `find` 但只對特定問題）**

```bash
# staging/backup 檔
ls /home/pigo/Documents/Pigo_Obsidian/*.bak.md 2>/dev/null
ls /home/pigo/Documents/Pigo_Obsidian/STATUS_*.md 2>/dev/null

# 舊分類殘留
ls /home/pigo/Documents/Pigo_Obsidian/01.1-TEST\ STUDY/ 2>/dev/null
ls /home/pigo/Documents/Pigo_Obsidian/"Archive 5j"/ 2>/dev/null

# 確認 10-LLM-Wiki 無正式內容
ls /home/pigo/Documents/Pigo_Obsidian/10-LLM-Wiki/entities/ 2>/dev/null
ls /home/pigo/Documents/Pigo_Obsidian/10-LLM-Wiki/raw/ 2>/dev/null
```

### Phase 2：每次 check 都要檢查的 5 類結構問題

1. **Staging 檔堆積**（vault root）
   - `AGENTS.*.bak.md`、`skill_diff_*.json`、`skill_sync_*.log`
   - `STATUS_*.md`（多個，可能是狀態報告）
   - `CLAUDE.md` at root（可能是遷移殘留）
   - `Vault-Classification.base`

2. **命名異常目錄**
   - `01.1-TEST STUDY/`（多了一個 dot）
   - `Archive 5j/`

3. **`10-LLM-Wiki/` 舊 runtime 殘留**
   - `log.md`、`entities/`、`raw/`、`README.md`
   - 現已遷移到 `~/.openclaw/workspace/skills/llm-wiki/`

4. **Source 型分類殘留**
   - `08-Learning/twitter/`、`08-Learning/youtube/`、`08-Learning/news/`
   - 原則上逐漸收納成 topic-type，但仍可保留純 sources

5. **00-Inbox 累積量**
   - 抽樣：前 30 筆可見進度
   - 超過 30 筆未整理要報告

### Phase 3：Output 寫入規範

**Check Report 寫到：**
```
12-Meta/vault-check-report-YYYY-MM-DD.md
```

**結構：**
```
1. 核心結論
2. 主要風險（5 類結構問題）
3. Low-risk 直接可處理清單
4. Pending Approval Plan
5. 建議下一步
```

---

## Risk-Tier Contract

- `Low-risk`
  可直接產出報告、統計、明確可逆的小型 hygiene 建議。
- `Medium-risk`
  不直接執行。整理成 `Pending Approval Plan`，列出精確路徑、建議動作、回滾方式。
- `High-risk`
  不在 `vault-check` 內執行。應移交 `vault-reshape` 或 `vault-deep-clean`。

---

## Audit Workflow

### 1. Coverage Scan

聚焦整體規模與主要駐留：

- 用 `ls` spot-check 各主要目錄現況
- note 數量：抽樣估算（用 `ls` + count，不用 `find` 全量）
- 主要分類覆蓋（`ls 08-Learning/`、`ls 09-Article-Notes/`）
- `youtube/twitter` 這類來源型殘留區域

### 2. Duplicate Review

檢查：

- 同標題競爭頁
- 同 `source_url` 競爭頁
- 高度相近的正式筆記

### 3. Link Health

檢查：

- 指向舊 vault 路徑（如 `C:\Users\...`）的殘留連結
- orphan notes（可用 `ls` spot-check 各 topic 目錄是否有 index.md）
- 應被 `index.md` 或主題頁收錄但尚未收錄的內容

### 4. Metadata Health

檢查：

- frontmatter 欠缺（抽樣檢查）
- `classification_path` 與實際路徑不一致
- `processed` / `status` 不合理

### 5. Navigation Health

檢查：

- `index.md` 是否欠缺入口（`ls` 各目錄確認）
- 是否存在值得立成主題頁的 cluster
- 是否有來源型分類殘留，應收納成主題型分類

---

## Expected Output

輸出應至少包含：

- `核心結論`
- `主要風險`（5 類結構問題）
- `Low-risk 直接可處理清單`
- `Pending Approval Plan`
- `建議下一步`

---

## 常見 mistake（犯過的，不要再犯）

1. **一開始就用 `find . -name "*.md" | wc -l"` 計數** → 被 allowlist 拒絕
2. **直接 `rg` 全 vault** → 容易被 allowlist 擋，改用 `ls` spot-check
3. **跳過 vault root** → staging/backup/status 檔常在 vault root
4. **忘記檢查 `10-LLM-Wiki/`** → 它已經是 runtime package，不是內容目錄
5. **把所有問題一次處理** → 沒有風險分級，執行量過大

---

## Handoff

`vault-check` 完成後，下一步通常是：

- `vault-deep-clean`（接著清理發現的問題）
- `vault-reshape`（處理 Medium/High risk 的結構問題）
- `tag-check`
- 或回到 `note-update` / `inbox-triage` 做定點修補