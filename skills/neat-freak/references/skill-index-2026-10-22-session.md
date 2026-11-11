# neat-freak session — 2026-10-22（系統性 mojibake 腐蝕修復）

## 觸發

cron job「Vault 整潔同步（neat-freak）」Phase 1 的 vault git health 檢查延伸：
`git fsck` 只報 dangling object，但真正的腐蝕是靠 `ftfy` badness 掃描才發現的。

## 發現：跨三層的系統性 UTF-8 mojibake 雙重編碼腐蝕

掃描範圍與結果（`ftfy.badness.badness()` > 50）：

| 位置 | 檔案數 | 最高 badness |
|------|-------|-------------|
| `~/.hermes/skills/`（canonical） | 7 | 1862（vault-GPS/SKILL.md）|
| `~/Documents/Agent/skills/`（workspace） | 44 | 2784（nuwa-skill/README.md）|
| `~/Documents/Pigo_Obsidian/`（vault） | 9 | 3908（12-Meta/reports/2026-08-08-audit-wikilinks.md）|

受影響 skill 家族：`knowledge-vault` 系列（vault-GPS / vault-check / vault-reshape /
vault-deep-clean / inbox-check / tag-check）、`nuwa-skill`、`matt-writing-research-lab`、
`browser-web-social`（web-access / research-to-diagram）、`darwin-skill`、
`finance-skill-pack`（6 檔）、`clinical-decision-support`。

## 關鍵教訓

### 1. `file` 命令與 `grep` 完全抓不到

Pattern II 已記錄 `file` 只測編碼類型不測內容語意。本次再確認：
**`grep -E "今天|昨天"` 對 mojibake 100% 盲眼**，因為 double-encoded 中文裡沒有任何
相對時間詞。唯一可靠偵測是逐檔算 badness。

### 2. 錯誤的「相對時間殘留」grep 檢查是無效防線

neat-freak checklist 裡的「相對時間 grep 清零」檢查對這類腐蝕毫無作用。
建議補上 badness 掃描。

### 3. ftfy 版本與 interpreter

`ftfy` 裝在 `/usr/bin/python3`（python3.12, `~/.local/lib/python3.12/site-packages`），
**不在** Hermes venv（`~/.hermes/installs/.../venv`）也**不在** `~/.hermes/tools/python-3.14.7`。
執行時必須用 `/usr/bin/python3`，否則 `ModuleNotFoundError: No module named 'ftfy'`。

### 4. 用 `fix_encoding` 而不是 `fix_text`

`fix_text()` 會順便做 punctuation normalization（把 `：` 改成 `:`、`，` 改成 `,`），
造成大量非必要 diff。`fix_encoding()` 只修編碼，保留全形標點。**修復一律用 `fix_encoding()`**。

### 5. ASCII 骨架比對是必經的 safety check

`fix_encoding()` 對**整檔**套用時會失敗（UTF-8 decode error），
因為 double-encoding 的長鏈在某些位置已無法還原。正確做法是**逐行套用**：

```python
for l in lines:
    if is_bad(l):
        cur = l
        for _ in range(4):
            cur = fix_encoding(cur)   # iterate until stable
        # 安全條件：非 ASCII 骨架（ASCII 骨架相同）且 badness 下降
        if ascii_skeleton(cur) == ascii_skeleton(l) and badness(cur) < badness(l):
            emit(cur)
```

這同時解決兩件事：
- 避免把 code block / 路徑 / YAML key 改壞
- 對整檔無法還原的行自動放棄（audit 報告有 3 行仍 badness>0，保留原樣）

驗證：`git diff` 逐檔檢查「刪除行 vs 新增行」的 ASCII 骨架必須完全一致。
本次 Agent repo 39+5 檔、vault 9 檔全部通過（ascii-diff lines: 0）。

### 6. 殘留 badness 分布

- vault `12-Meta/reports/2026-08-08-audit-wikilinks.md`（4.4MB, 14958 行）：
  148 行修復，3 行因 ASCII 骨架不匹配而跳過，最終 badness 351 仍 > 50。
  這是**已知的誤報殘留**（該檔是歷史 audit 報告，本身記錄了大量歷史路徑），
  不值得再強制修復——強行修會破壞報告的歷史保真性。
- Agent repo 修完後剩 5 檔 badness 67–86（threshold 100 漏掉的），第二次以
  threshold 20 重掃補掉。

## 修完後的驗證

| 檢查 | 結果 |
|------|------|
| `sync-check.py` | ✓ CLEAN（canonical ↔ workspace neat-freak 結構）|
| `skill-index-check.py` | ✓ ALL CLEAN（759 rows = header = 8 sections，0 dangling）|
| Agent repo badness > 20 | 0 |
| vault badness > 20 | 1（歷史 audit 報告，誤報殘留）|
| canonical badness > 20 | 0 |
| vault `git fsck` dangling | 1 dangling tree + 1 dangling commit（SAFETY snapshot，**故意保留**）|

## Git 處理

- Agent repo：commit `793ed1b7`（39 檔）+ `bf0e577f`（5 檔），皆 push
- Vault：commit `46eb319d0`（7 檔）+ `5ea721ec3`（2 檔），皆 push
  - vault push 第一次被拒（remote 有新 commit `75ea7117f` 晚報）→ `git pull --no-rebase` → merge → push（Pattern LL 流程）

## 未處理（需裁決）

**canonical ↔ Agent repo skill 結構分歧**：
`~/.hermes/skills/` 有 269 個 top-level skill dir，其中 224 個在 Agent repo
沒有同名 top-level 對應；88 個內容等價（md5 比對），88 個是**重新組織**後的變體
（如 canonical `gstack-autoplan/` vs workspace `skills/agent-workflows/gstack/commands/gstack-autoplan/`，
且版本不同——workspace 是較新的 upstream 版本）。
剩餘 136 個（含 `comfyui` 系列、`hermes-*`、`vault-rag` 系列、`mcp`、`llm-local`、
`gstack-*` 40+ 個、category namespace dirs 如 `media/` `web/` `meta/` `automation/`）
在 workspace 完全找不到。

判斷：這是**架構性分歧**，不是腐敗。Agent repo 走的是「13 大類 + Root-level」分組
（見 `docs/Skill_Index.md` A2-改2 政策），canonical 走 flat namespace。
把 136 個 skill 硬搬進 repo 屬架構決策，需 Pigo 裁決，不屬 neat-freak 的機械式修復範圍。

## 環境事實

- `ftfy` 6.3.1 在 `/usr/bin/python3`（3.12）
- 修復腳本：`/home/x/.hermes/cache/scratch/fix_mojibake.py`（scratch，24h 自動清）
- 備份：`/home/x/.hermes/cache/scratch/mojibake-backup/`（52 份原檔）
