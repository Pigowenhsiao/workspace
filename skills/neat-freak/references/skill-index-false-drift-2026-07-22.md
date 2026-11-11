# Skill_Index 虛假 drift 案例 — 2026-07-22

## 觸發情境
cron job 執行 `skill-index-check.py` 回報：
- Header drift: `Actual rows: 605`, `Header: 0`, `✗ DRIFT -605`
- Per-section: `✗ 6 section(s) off`
- 看似嚴重 drift

獨立口徑驗證結果（見下方命令）：
- **Actual rows: 603**
- **Summary header: 603**（diff=0）
- **Category Map sum: 603**
- **Per-section: 全部 ✓**

## 根因
`skill-index-check.py` 的 `check_header_drift()` regex 仍残留 Pattern AA bug：`re.search(r'Active Skills:\s*\*\*(\d+)\*\*', ...)` 匹配不到格式（格式為 `- Active Skills: ***N***` 有 dash prefix），導致 header 永遠抓成 0。

## 獨立驗證命令（當 drift 報告出現時，必須先跑這個）

```bash
python3 - <<'PY'
import os, re
c = open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')).read()
lines = c.split('\n')

# Count actual rows（pipe table format；必須同時過濾 'SKILL.md'，
# 否則 Category Map 的數字列也會被算進來 → 假 drift）
actual_rows = [l for l in lines if re.match(r'^\| [A-Za-z0-9]', l) and 'SKILL.md' in l]
print(f'Actual rows: {len(actual_rows)}')

# Summary header（實際格式為 `- Active Skills: ***N***`，2~3 個星號都必須匹配）
m = re.search(r'- Active Skills:\s*\*{2,3}(\d+)\*{2,3}', c)
summary = int(m.group(1)) if m else None
print(f'Summary header: {summary} (diff={abs(len(actual_rows)-summary) if summary else "N/A"})')

# Category Map sum
cm_lines = [l for l in lines if re.match(r'^\| [^|]+\| \d+ \|', l)]
cm_sum = sum(int(re.search(r'\d+', l.split('|')[2]).group()) for l in cm_lines if re.search(r'\d+', l.split('|')[2]))
print(f'Category Map sum: {cm_sum}')

# Per-section
section_headers = [(i, l) for i, l in enumerate(lines) if re.match(r'^## [^#]', l)]
all_ok = True
for num, line in section_headers:
    hm = re.match(r'^## [^#].+\((\d+)\)', line)
    if not hm:
        continue
    expected = int(hm.group(1))
    end = len(lines)
    for j in range(num + 1, len(lines)):
        if re.match(r'^## [^#]', lines[j]):
            end = j
            break
    rows = [l for l in lines[num + 1:end] if re.match(r'^\| [A-Za-z0-9]', l) and 'SKILL.md' in l]
    status = '✓' if expected == len(rows) else f'✗(expected={expected}, actual={len(rows)})'
    if '✗' in status:
        all_ok = False
    print(f'  {line[:55]} => {len(rows)} rows {status}')
print(f'All sections OK: {all_ok}')
PY
```

**口徑判斷原則**：
- 獨立驗證 `actual rows = Summary header = Category Map sum` → 口徑正確，script 的 drift 報告是虛假信號
- 獨立驗證與 script 報告不一致 → script 有 bug，用獨立值為準

## 2026-07-22 session 驗證結果
- Actual rows: **603**
- Summary header: **603** ✓
- Category Map sum: **603** ✓
- All per-sections: **✓**
- 結論：**口徑完全正確，script 報告的 drift 全為虛假**
