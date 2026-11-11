# Skill_Index Drift — 2026-05-31 Session

## Pattern FF + GG（2026-05-31 cron job 發現並修復）

**Pattern FF — Subdirectory AGENTS.md 規範漂移**
- 問題：`Agent/AGENTS.md` Requirement #5 要求寫入 `STATUS_*.md`，與根目錄 `AGENTS.md` 的 `STATUS_ALL.md` 規範衝突
- 修復：同步為 `STATUS_ALL.md` 規範，commit `6e4074d5`，已 push

**Pattern GG — Readme.md Primary Read Targets 含已封存備份**
- 問題：`Agent/Readme.md` Primary Read Targets 包含 `AGENTS_2026-05-02.md`（dated backup）
- 修復：移除該條目，commit `6e4074d5`，已 push

**修復驗證**：
```bash
cd ~/Documents/Agent && git log --oneline -1
# 6e4074d5 neat-freak: sync STATUS_*.md convention to STATUS_ALL.md across AGENT/ subdirectory
git status
# On branch main, your branch is up to date with 'origin/main'.
```

**Skill 更新**：
- Pattern FF（AGENTS.md 規範一致性交叉檢查）已寫入腐蝕圖譜
- Pattern GG（Readme.md Primary Read Targets 含 dated backup 檢查）已寫入腐蝕圖譜

## 口徑現況（2026-05-31 cron job 驗證）

| 指標 | 數值 | 備註 |
|------|------|------|
| Skill_Index.md actual rows | 486 | 獨立 Python `re.findall(r'^\| \[([^\]]+)\]\([^)]+\.md\)', c, re.M)` |
| Skill_Index.md header | 486 | `- Active Skills: 486` |
| Skill_Category.md total | 581 | 14 categories 加總，內部一致 |
| Dangling entries | 470 | 全部是 upstream origin/main 累積腐敗，非 workspace 問題 |
| Branch sync | up to date | `Your branch is up to date with 'origin/main'` |

## Script Bug 狀態（2026-05-31 仍存在）

`skill-index-check.py` 報告：
- `Actual rows: 0` — 虛假（regex 匹配不到 `- Active Skills: N` 格式）
- `Header: 0` — 虛假（同上）
- `✓ ALL CLEAN` — 虛假乾淨信號

獨立 Python 確認口徑為 486 = header，workspace 本身**完全乾淨**。

SKILL.md 已更新「已知持久性問題」章節，強化了 CRITICAL 警告和驗證流程。

## Canonical vs Workspace Sync Copy

- 所有 16 個 reference 檔內容完全一致 ✓
- 所有 3 個 script 檔內容完全一致 ✓
- 3 個 EXTRA (`agents/`、`references/Readme.md`、`scripts/Readme.md`) = origin/main 正當追蹤內容 ✓
- `__pycache__` 乾淨 ✓

## Pattern AA/AB Bug 長期修復記錄

- 2026-05-21：首次發現並記錄
- 2026-05-22：確認三個 root cause（路徑拼接錯誤、header regex 格式不符、category 命名系統混淆）
- 2026-05-31：**口徑確認 486**，但 script `Actual rows: 0` 仍未修復（CRITICAL 等級提升）
- 下次修復方向：重構 `check_header_drift()` 與口徑計數解耦
