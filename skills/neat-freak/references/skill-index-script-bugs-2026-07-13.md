# Skill_Index Script Bugs — 2026-07-13 Session

## Bug Summary

Four bugs found in `skill-index-check.py` on 2026-07-13:

| Bug | Location | Error | Fix |
|-----|----------|-------|-----|
| AGENT_ROOT macOS path | Line 15 | `"~/Documents/Agent"` | `"/home/pigo/Documents/Agent"` |
| Row regex missing `\s+` | `check_header_drift`, `check_per_section_drift`, `check_dangling` | `\.md\|` should be `\.md\s+\|` | Add `\s+` before final `\|` |
| Header regex double-backslash | `check_header_drift` | `Active Skills:\s+\\\*\\\*(\d+)\\\*\\\*` | `Active Skills:\s+\*\*\*(\d+)\*\*\*` |
| Script returning actual=0 while reporting "clean" | All three functions | False confidence signal |三口徑驗證命令見正文 |

## Root Cause

2026-06-29 Skill_Index.md was fully rebuilt with a new format (pipe table `| name | path | desc | api_key |`) but the script's regexes were never updated to match.

## Verification Command (must run before trusting script output)

```python
import os
import re
c = open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')).read()
lines = c.split('\n')
actual = [l for l in lines if re.match(r'^\| [A-Za-z0-9]', l) and 'SKILL.md' in l]
print(f'Actual rows: {len(actual)}')  # Must be > 0
hm = re.search(r'Active Skills:\s+\*\*\*(\d+)\*\*\*', c)
print(f'Header: {hm.group(1) if hm else None}')  # Must be non-None
```
