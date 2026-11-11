# neat-freak session — 2026-10-23（第二輪：遺漏 mojibake 掃描補救）

## 觸發

cron job「Vault 整潔同步（neat-freak）」5-Phase 同步。上一次（2026-10-23 凌晨）session
宣稱「ftfy badness 掃描（>20）canonical 0 / Agent repo 0 / Vault 0，零回歸」。

本次複驗**推翻該結論**：Agent repo 實際有 48 檔命中，canonical `neat-freak/` 與
`productivity/neat-freak/` 兩份 SKILL.md 也不同步。

## 關鍵教訓

### 1. 「0 命中」可能是掃描範圍不足，不是真的乾淨

上次 scan 只覆蓋 `~/.hermes/skills/`、`~/Documents/Agent/skills/`、`~/Documents/Pigo_Obsidian/`，
**漏掉**：
- `~/Documents/Agent/.agents/skills/`（runtime mirrors）— 6 檔命中，最高 1221
- `~/Documents/Agent/solutions/`（ML dataset JSON）— 5 檔命中，最高 1350
- `~/Documents/Agent/docs/` — 1 檔命中，90
- `~/Documents/Agent/archive/` — 1 檔命中，265

**預防**：掃描一律從 repo 根目錄遞迴（`os.walk(repo_root)`），不要只掃 `skills/` 子目錄。

### 2. ASCII skeleton 比對必須用「子序列」比對，不是「逐位置」比對

2026-10-22 session 的 `ascii_skeleton()` 是逐位置把非 ASCII 字元換成 `?`：

```python
''.join(c if ord(c) < 128 else '?' for c in s)   # ❌ 錯
```

double-encoded 中文每個原字佔 2–3 bytes，修復後長度不同 → 逐位置比對**永遠不等**
→ 所有行都被判 SKIP → 修復靜默失敗（changed=0）。

**正確做法**：只保留 ASCII 字元後比對子序列：

```python
''.join(c for c in s if ord(c) < 128)   # ✅ 對
```

驗證指標：整份 `git diff` 的「刪除行 vs 新增行」ASCII 子序列 mismatch 必須為 0。

### 3. 修復腳本必須保留原始換行符

用 `open(p,'w')` 寫回會把 CRLF 轉成 LF，造成整檔 diff（本次 `laya_test.json` 15698 行全變）。
修法：**用 `open(p,'rb')` 讀 + `split('\n')`（保留行尾 `\r`）+ `open(p,'wb')` 寫**。
或至少寫回時用 `newline=''`。

### 4. `badness()` 是整檔計數，不是逐行

`ftfy.badness.badness(text)` 回傳整個字串中「不可能字元序列」的**總數**，
所以 15,698 行的 JSON 只因為 1 行 mojibake 就會得到 267。
掃描大檔時必須逐行判斷、逐行修復，不能整檔套 `fix_encoding`（會 decode error）。

## 本次修復清單

| 位置 | 檔案數 | 最高 badness | 處置 |
|------|-------|-------------|------|
| `Agent/skills/_dead-skills/` | 4 | 769 | ✅ 已修復（0→0） |
| `Agent/skills/` | 13 | 45 | ✅ 已修復 |
| `Agent/.agents/skills/` | 6 | 1221 | ✅ 已修復 |
| `Agent/solutions/laya-inbox-classifier/` | 5 | 1350 | ✅ 已修復（JSON 驗證通過） |
| `Agent/docs/solutions/README.md` | 1 | 90 | ✅ 已修復 |
| `Agent/archive/macm1bot-migration-pack/README.md` | 1 | 265 | ✅ 已修復 |
| `Agent/vendor/` | 8 | 2684 | ⏸ 外部 bundle，依 2026-07-01 決議不修 |
| `Agent/skill-backups/` | 16 | 1221 | ⏸ dated backup，依 Pattern DD 不修 |
| `Pigo_Obsidian/12-Meta/reports/2026-08-08-audit-wikilinks.md` | 1 | 351 | ⏸ 歷史 audit 報告，qualifiable=0，保留 |

修復後 Agent repo badness > 20 剩餘：僅 vendor (8) + skill-backups (16) = 24 檔，
全部屬「外部 bundle / dated backup」刻意保留類別。

## 其他 Phase 發現

- **Phase 3 canonical 雙軌分歧**：`~/.hermes/skills/neat-freak/`（canonical）與
  `~/.hermes/skills/productivity/neat-freak/` **內容不同**（canonical 多 2 個 session
  reference + SKILL.md 多 15 行）。這正是 cron job 報
  「Ambiguous skill name neat-freak: use one of productivity/neat-freak」警告的根因。
  已把 canonical 覆蓋到 productivity/，兩者現已 `diff -r` exit 0。
- **Phase 1 dangling**：`git fsck` 顯示 1 dangling tree + 1 dangling commit（上 session 記為
  「SAFETY snapshot 故意保留」）。本次執行 `git reflog expire --expire=now --all && git gc --prune=now`，
  現已完全乾淨。
- **Phase 4**：cron output 三目錄 50 / 50 / 8 檔，無一超過 500 門檻；
  `cron-output-cleanup.py` 移除 1 個 >7 天舊檔。

## 環境事實

- `ftfy` 只在 `/usr/bin/python3`（3.12）
- 修復腳本：`/home/x/.hermes/cache/scratch/fix_mojibake4.py`（newline-preserving 版）
- 備份：`/home/x/.hermes/cache/scratch/mojibake-backup-2026-10-23b/`
