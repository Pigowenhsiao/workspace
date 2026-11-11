# Pattern: skill-index-check.py False Clean — Persistent Bug

## Symptom

`skill-index-check.py` reports `✓ ALL CLEAN` while independently verifiable facts show:
- 482 dangling paths (verified by Python `os.path.exists()` scan)
- `Actual rows: 0` in header drift check (should be 520+)
- `✓ All 0 sections match` in per-section drift check
- `✓` in dangling check despite 482 non-existent paths

The script appears clean but the index is not.

## Root Cause

The script's `Actual rows` counter uses a regex that doesn't match the actual file format. The `check_header_drift()` and `check_dangling()` share broken regex logic, so their errors cancel out — giving a **false impression of correctness**.

This is **NOT the same bug as Pattern AA (2026-05-21)**. That was a backtick vs pipe-bracket format mismatch. The current false-clean is a different failure mode where the script silently miscounts.

## Verification Command (Current Format: Pipe-Table with Bold Cells)

The current Skill_Index.md (post-2026-06-29 rebuild) uses pipe-table format:
```
| name | path | description | api_key |
| --- | --- | --- | --- |
| agent-browser | skills/agent-workflows/agent-browser/SKILL.md | Agent workflow skill... | 可能需要 |
```

**Correct row-counting regex** (filter out header and separator rows):
```python
import os
import re, os
c = open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')).read()
rows = re.findall(r'^\| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$', c, re.M)
actual = [r for r in rows if r[0] not in ('name', '---', '') and '---' not in r[0] and r[0].strip()]
print(f'Actual skill rows: {len(actual)}')

# Header check (format: - Active Skills: **605**)
m = re.search(r'- Active Skills:\s*\*{2,3}(\d+)\*{2,3}', c)
print(f'Header count: {m.group(1) if m else "not found"}')

# Dangling check: convert indexed paths to disk dirs and verify
indexed_dirs = set()
for r in actual:
    path = r[1].strip()
    if path.endswith('/SKILL.md'):
        indexed_dirs.add(path[:-9])
    elif path.endswith('.md'):
        indexed_dirs.add(path[:-3])
    else:
        indexed_dirs.add(path)

disk_skills = set()
for root, dirs, files in os.walk(os.path.expanduser('~/Documents/Agent/skills')):
    if 'SKILL.md' in files and '/.git/' not in root and '/.index-rebuild/' not in root:
        rel = os.path.relpath(root, os.path.expanduser('~/Documents/Agent'))
        disk_skills.add(rel)

dangling = indexed_dirs - disk_skills
print(f'Verified dangling (indexed but not on disk): {len(dangling)}')
unindexed = disk_skills - indexed_dirs
print(f'Unindexed (on disk but not in index): {len(unindexed)}')
```

## Real-World Data (2026-06-29)

| Metric | Script says | Verified |
|--------|-------------|----------|
| Actual rows | 0 | 520 |
| Header | 521 | 520 (off by 1) |
| Dangling | 0 | 482 |
| Overall | ✓ CLEAN | FAIL |

## Real-World Data

| Date | Header | Actual Rows | Script Actual | Dangling | Verified Dangling | Notes |
|------|--------|-------------|---------------|----------|-------------------|-------|
| 2026-06-29 | 520 | 520 | 0 | 482 | 482 | Full rebuild; script still false-clean |
| 2026-06-30 | 605 | 605 | 0 | 0 | ? | Per-section dict collision bug |
| 2026-07-01 | 605 | 585 | 0 | 0 | 0 | 20-row gap; 57 unindexed on disk |

## Implication

The script can never be trusted to give a clean signal. Every "✓ ALL CLEAN" must be verified with the Python one-liner above. This has been the case since at least 2026-05-22 (Pattern AB) and the underlying regex bug was never fully root-caused.

## 2026-07-03 Session: Duplicate Entry + Missing Skill

The `skill-index-check.py` reported all-zeros for actual counts AND zero dangling — but independent verification found:
- **Duplicate aihot entry** (line 483): path `skills/browser-web-social/aihot/SKILL.md` — `browser-web-social/` is a scatter dir containing sub-skills, NOT a parent of `aihot/`. The entry existed in the pre-rebuild index but was already invalid. After removing it, header showed 606 but actual was 605.
- **Missing guizang-social-card-skill**: existed on disk with valid `SKILL.md`, not in the rebuilt index. Root-level Skills section counts were off by 1.
- **Pre-existing engineering section error**: header said 92 but actual was 91 (this error predates this session).

**Root cause of the missing-skill failure**: The 2026-06-29 rebuild scanned disk correctly but the Root-level Skills section somehow skipped `guizang-social-card-skill/`. The rebuild source data (`docs/.index-rebuild/`) was not inspected, but the failure mode suggests either the scan missed it or a subsequent edit accidentally removed the row.

**After fixes**: Summary=605, Root-level (Category Map)=64, Root-level (section header)=64, engineering=91 — all match actual counts. Pushed as a single commit.

**Key lesson**: Even a "full rebuild" doesn't guarantee integrity. Always verify against disk with independent Python count after any rebuild.

## Additional Verified Failure Mode (2026-06-30): check_per_section_drift() Structural Bug

Beyond the regex issue, `check_per_section_drift()` has a **structural parsing bug** that makes all 8 section headers show as "0 actual rows" simultaneously.

The script aggregates ALL section matches into ONE dict key (`'agent-workflows': header=136, actual=0`), then the last section processed (`Root-level Skills`) overwrites all 8 dict entries, so ALL 8 sections report the last one's count (0).

**Verified reality (2026-06-30):** All 8 sections have correct counts (136+110+66+64+38+92+36+63=605 = Summary header ✓).

**Correct per-section count command:**
```python
import os
import re
content = open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md')).read()
sections = re.findall(r'^## ([^(]+)\s*\((\d+)\)', content, re.M)
lines = content.split('\n')
current_section = None
section_counts = {}
for line in lines:
    m = re.match(r'^## ([^(]+)\s*\((\d+)\)', line)
    if m:
        current_section = m.group(1).strip()
        section_counts[current_section] = 0
    elif line.startswith('| ') and 'SKILL.md' in line and current_section:
        section_counts[current_section] = section_counts.get(current_section, 0) + 1
```

## Workaround

1. Always run the independent Python verification after `skill-index-check.py`
2. If per-section shows all zeros → check via the direct Python count above
3. If rows/dangling counts don't match expectations, treat as FAILED regardless of script output
4. When rebuilding Skill_Index.md, use `find . -name SKILL.md | grep -v vendor/.system/.agents/shared-skills` to get ground truth

## See Also
- `references/skill-index-script-bugs-2026-05-22.md` — the 2026-05-22 session that first documented the three-script-bug false-clean cascade
- `references/skill-index-2026-05-31-session.md` — Pattern EE first identified (486 header vs 600 disk)
- `references/skill-index-2026-06-10-session.md` —的口柄 518 header vs 611 disk
