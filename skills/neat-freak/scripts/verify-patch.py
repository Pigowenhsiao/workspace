#!/usr/bin/env python3
"""Verify skill-index-check.py against the current Skill_Index.md.

Independent re-count (Pattern W): never trust skill-index-check.py's own numbers —
recompute the three 口径 from the file and compare. Uses the CURRENT pipe-table
row format `| name | path | description | api_key |` (the backtick-link format
this script used before 2026-07-07 no longer exists on disk).
"""
import os
import re
import sys

AGENT_ROOT = os.environ.get("AGENT_ROOT", os.path.join(os.path.expanduser("~"), "Documents/Agent"))
IDX_PATH = os.path.join(AGENT_ROOT, "docs/Skill_Index.md")

# A skill row: `| name | path/to/SKILL.md | description | api_key |`
ROW_RE = re.compile(r'^\| [^|]+\| [^\s|]+\.md\s+\|')

with open(IDX_PATH) as f:
    idx = f.read()

lines = idx.split('\n')
actual_rows = [l for l in lines if ROW_RE.match(l)]

# Summary header — rendered as `- Active Skills: ***N***` or `**N**`
header_m = re.search(r'- Active Skills:\s*\*{2,3}(\d+)\*{2,3}', idx)
header_n = int(header_m.group(1)) if header_m else None

print(f"Actual skill rows:  {len(actual_rows)}")
print(f"Summary header:     {header_n}")

sections = [(i, l) for i, l in enumerate(lines) if re.match(r'^## [^#].+\(\d+\)\s*$', l)]
print(f"Section count:      {len(sections)}")

# Per-section recount
mismatches = []
for k, (i, line) in enumerate(sections):
    expected = int(re.match(r'^## [^#].+\((\d+)\)\s*$', line).group(1))
    end = len(lines)
    for j in range(i + 1, len(lines)):
        if re.match(r'^## ', lines[j]):
            end = j
            break
    rows = sum(1 for l in lines[i + 1:end] if ROW_RE.match(l))
    if rows != expected:
        mismatches.append((line[:60], expected, rows))

if header_n is None:
    print("\nSummary header: NOT FOUND — check the `- Active Skills:` line format")
elif header_n != len(actual_rows):
    print(f"\nDRIFT: header={header_n} actual={len(actual_rows)} ({header_n - len(actual_rows):+d})")
else:
    print("\nSummary: MATCH")

if mismatches:
    print("\nPer-section DRIFT:")
    for name, h, a in mismatches:
        print(f"  {name}: header={h}, actual={a}")
else:
    print(f"Per-section: ALL CLEAN ({len(sections)} sections)")

sys.exit(1 if mismatches or header_n != len(actual_rows) else 0)
