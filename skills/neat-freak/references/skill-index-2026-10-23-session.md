# Skill Index / Neat-Freak Session — 2026-10-23

**Run:** cron（neat-freak 5-Phase 同步）
**Result:** 全部 CLEAN，零回歸

## 檢查結果

| Phase | 項目 | 結果 |
|---|---|---|
| 1 | Vault `git status` | clean，與 origin/main 一致，無需 commit/push |
| 1 | `git fsck` | 1 dangling tree + 1 dangling commit（SAFETY snapshot，故意保留） |
| 2 | memory P0/P1/P2 md5 | `~/.hermes/memory` ≡ `~/Documents/Agent/memory`，完全一致 |
| 3 | `sync-check.py` | RESULT: CLEAN |
| 3 | `diff -r canonical/ workspace/` | exit 0，內容完全一致 |
| 3 | `skill-index-check.py` | ✓ ALL CLEAN（759 rows = header = 8 sections，0 dangling） |
| 3 | ftfy badness 掃描 (>20) | canonical 0 / Agent repo 0 / Vault 0 |
| 4 | cron output 目錄檔數 | 50 / 50 / 7，無一超過 500 門檻 |
| 4 | `cron-output-cleanup.py` | Total files removed: 0 |
| 5 | Hermes Backup | 排程 job `89c411611e6d`（每日 03:00）正常；最新備份 462M，tar 完整性通過 |

## 關鍵觀察：2026-10-22 的 60 檔 mojibake 修復零回歸

2026-10-22 session 修復了 60 檔 UTF-8 double-encoding 亂碼（canonical 7 / Agent repo 44 / vault 9）。
本次用同一套 ftfy badness 掃描（門檻 >20）複驗三個樹，**全部 0 命中**，
包含先前被判定為「歷史報告殘留、維持現狀」的 `12-Meta/reports/2026-08-08-audit-wikilinks.md`——
該檔 badness 已降至門檻下，無需再列為裁決項。

### 掃描腳本要點（可重用）

```python
from ftfy import badness
# 限制：檔案 <6MB、副檔名白名單、跳過 .git/node_modules/__pycache__
# ftfy 只裝在 /usr/bin/python3 (3.12)，Hermes venv 與 tools/python-3.14.7 沒有
b = badness(txt)
if b and b > 20: hits.append((b, path))
```

**注意事項**：`file` / `grep` 抓不到 mojibake（雙重編碼仍是合法 UTF-8），ftfy badness 是唯一可靠手段。

## 同步操作

- 新增 `memory/handoffs/neat-freak_2026-10-23.md` 到 `~/.hermes/memory/handoffs/` 與
  `~/Documents/Agent/memory/handoffs/`（兩處 IDENTICAL）
- Agent repo commit `0e13e760` → push origin/main OK

## 未裁決（延續自 2026-10-22）

canonical ↔ Agent repo skill 結構分歧：canonical 269 top-level skill dir，136 個在 repo 無對應
（comfyui、mcp、llm-local、gstack-* 40+、category namespace dirs）。需 Pigo 選 A/B/C。

## 參考

- `references/skill-index-2026-10-22-session.md`
- `~/.hermes/memory/handoffs/neat-freak_2026-10-23.md`
