# Skill Library Maintenance Workflow

## Source

Originally `agent-workflow/skill-library-maintenance/SKILL.md` — merged into `neat-freak` on 2026-06-01.

## Purpose

Audit, diagnose, and regenerate broken skill index files in the Agent repo. Use when:
- `Skill_Index.md` shows wrong counts or broken paths
- New skills were added but not indexed
- Duplicate skill names across vendor/canonical layers
- After importing or reorganizing many skills at once

## Key Insight: Index Path Format

Index paths use `../SKILL.md` relative to `docs/`. If the repo structure changed (e.g., skills moved into `skills/` subdirectory), all paths drift. Always check disk structure before assuming paths are correct.

## Common Pitfalls

- **`git ls-files --error-unmatch` false confidence**: just because a file is tracked doesn't mean it's at the path the index claims
- **Vendor skills** (`vendor/`) are imports, not canonical — keep them out of the active index
- **Runtime skills** (`.agents/`, `.system/`) are system-only
- **Path drift pattern**: if 400+ "broken" paths all share the same prefix issue, the problem is index format drift, not missing files
- **Python 3.13 `re` module syntax regression**: `\\.+` subpattern in character class causes `re.PatternError`
- **`git status --short` doesn't show staged deletion**: always use `git status` (non-short) before assuming workspace is clean

## Standard Regeneration

1. `find . -name "SKILL.md" | grep -v ".git" | sort > /tmp/all_skills.txt`
2. Count actual rows from disk
3. Regenerate index with correct path format
4. Commit and verify

## When Dangling Rows Are the Problem

If index references paths that don't exist on disk (dangling rows), the root cause is often upstream reorganization that wasn't reflected in the index. Don't just delete dangling rows — check if the skills moved or were deleted, then decide whether to remove the reference or restore the skill.

## Reference

Full Skill_Index.md regeneration process is in the `## Skill Library Maintenance` section of `neat-freak/SKILL.md`.