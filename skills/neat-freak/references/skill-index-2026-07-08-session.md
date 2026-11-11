# Skill Index — 2026-07-08 Session

## 口徑修復（只有 1 drift）

本次口徑 drift 極小（actual=595, header/category/section 全為 594），但三口徑各自落後仍是 drift。

**三口徑獨立驗證命令**（不走 script 的可能有 bug 的 regex）：
```python
import os
import re
c = open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')).read()
lines = c.split('\n')

actual = [l for l in lines if re.match(r'^\| [a-z0-9]', l) and 'SKILL.md' in l]
m = re.search(r'Active Skills:\s*\*\*(\d+)\*\*', c)
summary = int(m.group(1)) if m else None
cm_lines = [l for l in lines if re.match(r'^\| [^|]+\| \d+ \|', l)]
cm_sum = sum(int(re.search(r'\| (\d+) \|', l).group(1)) for l in cm_lines)
section_headers = [(i, l) for i, l in enumerate(lines) if re.match(r'^## [^#](.+)\((\d+)\)', l)]
section_sum = sum(int(re.match(r'^## [^#](.+)\((\d+)\)', l).group(2)) for _, l in section_headers)
print(f'Actual: {len(actual)}, Summary: {summary}, Category: {cm_sum}, Section: {section_sum}')
print(f'All aligned: {len(actual) == summary == cm_sum == section_sum}')
```

**口徑修復**（execute_code，不能用 patch 因為要換三個地方）：
```python
import os
c = open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')).read()
c = c.replace('- Active Skills: **594**', '- Active Skills: **595**', 1)
c = c.replace('| Media, Documents & Writing | 62 |', '| Media, Documents & Writing | 63 |', 1)
c = c.replace('## media-documents (62)', '## media-documents (63)', 1)
open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md'), 'w').write(c)
```

## Pattern OO 再確認

Script `skill-index-check.py` 仍報告 `Actual rows: 0` 和 `✓ ALL CLEAN` 同時存在——虛假乾淨信號。獨立 Python count 是唯一可靠口徑。

## `execute_code` f-string 反斜槓限制

Python 3.11+ 不允許 f-string 表達式內含反斜槓：
```python
# 錯誤（SyntaxError）
print(f'Section sum: {sum(int(re.match(r"^## [^#](.+)\((\d+)\)", l).group(2)) for _,l in section_headers)}')

# 正確：先把 regex 拿出來
section_sum = sum(int(re.match(r'^## [^#](.+)\((\d+)\)', l).group(2)) for _, l in section_headers)
print(f'Section sum: {section_sum}')
```

## Pattern Z EXTRA 再次確診

`sync-check.py` 報告的 3 項 EXTRA（`agents/`、`references/Readme.md`、`scripts/Readme.md`）全部 origin/main tracked content。`git ls-files` 確認皆有 commit history，不是 script 誤寫入。

## 修復 commit

```
docs: fix Skill_Index.md口径(+1) and restore missing canonical reference
2 files changed, 43 insertions(+), 3 deletions(-)
push: 56f0f48c..6564b8db  main -> main
```
