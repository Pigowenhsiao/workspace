# Skill_Index 口徑修正 Session — 2026-07-30

## 口徑狀態
- Root-level: 64 → 66（+2 drift 修復）
- Summary header: 471（已對齊）
- Actual total: 471（已驗證）

## 發現的問題

### Root-level section drift（本次修復）

**Root cause**：`skill-index-check.py` 的 row-count regex `^\| [a-z]` 不匹配大寫字母開頭的 skill names。

Root-level 包含 5 個大寫開頭的 skills（`Slide Deck`、`Remotion`、`Scholar Evaluation`、`X-note`、`AutoIt v3`），script 統計時將其排除：
- Script count（`[a-z]`）：64 rows
- 實際 count（含大寫）：66 rows
- Drift：+2

**三口徑驗證（不走 script 的口徑）**：
```bash
python3 - << 'EOF'
import re
c = open('/home/pigo/Documents/Agent/docs/Skill_Index.md').read()
lines = c.split('\n')
all_rows = [l for l in lines if re.match(r'^\| [^|]', l) and 'SKILL.md' in l and '---' not in l]
print(f'Total rows: {len(all_rows)}')
m = re.search(r'\*\*\*(\d+)\*\*\*', lines[6])
print(f'Summary header: {m.group(1) if m else "?"}')
EOF
```

**修復**：Root-level section header `## Root-level Skills (64)` → `## Root-level Skills (66)`

**預防**：script 的 `[a-z]` regex 在 Skill_Index format 從 pipe-bracket link 改為 pipe table 後未同步更新。見 Pattern OO（2026-07-07）。

## Pattern OO 更新（2026-07-30 再次確認）

Script 的 actual count regex (`[a-z0-9]`) 仍不匹配大寫開頭的 skill names，導致：
1. `check_header_drift()` 的 actual count 低估
2. `check_per_section_drift()` 的 section count 低估
3. 兩個低估互相抵消，給出「All 7 sections match ✓」的假信號

**驗證方法**：不走 script，用 `[a-zA-Z]` 或更寬鬆的 `[^|]` 重新 count。

## Commit History
- `adc7f9c09` fix Skill_Index.md: correct Root-level section header 64→66 (2026-07-30)
