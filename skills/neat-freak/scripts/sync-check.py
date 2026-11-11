#!/usr/bin/env python3
"""
sync-check.py — Verify neat-freak canonical vs workspace sync copy integrity.

Runs in ~1s, replaces the manual 5-step ls/diff inspection.
Exit codes: 0 = clean, 1 = drift detected, 2 = error.

Usage:
    python3 sync-check.py
"""

import os
import sys
import subprocess
from pathlib import Path

def get_files(dir_path):
    """Return sorted list of relative file paths under dir_path, recursive."""
    files = []
    for root, _, filenames in os.walk(dir_path):
        for f in filenames:
            rel = Path(root).relative_to(dir_path)
            files.append(str(rel / f) if str(rel) != '.' else f)
    return sorted(files)

def get_dirs(dir_path):
    """Return sorted list of immediate subdirectories."""
    try:
        return sorted([d.name for d in Path(dir_path).iterdir() if d.is_dir()])
    except FileNotFoundError:
        return []

def canonical_dir():
    return Path.home() / ".hermes" / "skills" / "neat-freak"

def workspace_dir():
    # Default workspace for OpenClaw; override via WORKSPACE_DIR env var
    return Path(os.environ.get("WORKSPACE_DIR", str(Path.home() / "Documents" / "Agent" / "skills" / "neat-freak")))

def workspace_root_dir():
    """Repo root of the Agent workspace (parent of the skills/ dir)."""
    return Path(os.environ.get("WORKSPACE_ROOT", str(Path.home() / "Documents" / "Agent")))

def repo_root_copy():
    """The second, easily-forgotten copy of SKILL.md at <workspace-root>/neat-freak/SKILL.md.

    This copy is NOT covered by the canonical-vs-workspace directory comparison above
    (it lives outside skills/neat-freak/). It has silently fallen behind canonical
    three times (2026-10-27, 2026-10-29a, 2026-10-29b) precisely because no check
    looked at it. See session reference 2026-10-29b.
    """
    return workspace_root_dir() / "neat-freak" / "SKILL.md"

def check_pycache(dir_path, label):
    """Check for __pycache__ directories under dir_path."""
    issues = []
    for root, dirs, _ in os.walk(dir_path):
        if "__pycache__" in dirs:
            issues.append(str(Path(root) / "__pycache__"))
    return issues

def run():
    canonical = canonical_dir()
    workspace = workspace_dir()

    errors = []
    pycache_issues = []
    missing_in_ws = []
    extra_in_ws = []
    dir_mismatch = []

    # --- Directory structure check ---
    canonical_subdirs = get_dirs(canonical)
    workspace_subdirs = get_dirs(workspace)

    for d in set(canonical_subdirs + workspace_subdirs):
        in_canonical = d in canonical_subdirs
        in_workspace = d in workspace_subdirs
        if in_canonical and not in_workspace:
            missing_in_ws.append(d)
        elif in_workspace and not in_canonical:
            extra_in_ws.append(d)

    # --- Per-directory file comparison ---
    for subdir in sorted(set(canonical_subdirs)):
        canonical_sub = canonical / subdir
        workspace_sub = workspace / subdir
        canonical_files = get_files(canonical_sub)
        workspace_files = get_files(workspace_sub)

        for f in canonical_files:
            if f not in workspace_files:
                missing_in_ws.append(f"{subdir}/{f}")
        for f in workspace_files:
            if f not in canonical_files:
                extra_in_ws.append(f"{subdir}/{f}")

    # --- __pycache__ check ---
    if workspace.exists():
        pycache_issues.extend(check_pycache(workspace, "workspace"))

    # --- Content consistency check (canonical vs skills/neat-freak copy) ---
    # sync-check.py historically only compared *existence*, never *content*, so a
    # stale-but-present file passed as "clean" (Pattern H item 9, Pattern AAA).
    content_drift = []
    if canonical.exists() and workspace.exists():
        for f in get_files(canonical):
            c_path = canonical / f
            w_path = workspace / f
            if not w_path.exists():
                continue
            try:
                if c_path.read_bytes() != w_path.read_bytes():
                    content_drift.append(f)
            except OSError:
                content_drift.append(f)

    # --- Repo-root copy check (canonical vs <workspace-root>/neat-freak/SKILL.md) ---
    repo_root_status = None
    rr = repo_root_copy()
    canon_skill = canonical / "SKILL.md"
    if rr.exists() and canon_skill.exists():
        try:
            if rr.read_bytes() == canon_skill.read_bytes():
                repo_root_status = "in sync ✓"
            else:
                c_lines = len(canon_skill.read_text(encoding="utf-8", errors="replace").splitlines())
                r_lines = len(rr.read_text(encoding="utf-8", errors="replace").splitlines())
                repo_root_status = (f"STALE — canonical {c_lines} lines vs repo-root copy {r_lines} lines")
                content_drift.append("neat-freak/SKILL.md (repo-root copy)")
        except OSError as e:
            repo_root_status = f"unreadable: {e}"
    elif canon_skill.exists() and not rr.exists():
        repo_root_status = "MISSING — no repo-root copy present"
    else:
        repo_root_status = "not applicable"

    # --- Report ---
    print("=== Canonical:", canonical)
    print("=== Workspace:", workspace)
    print()
    print("--- Directory structure ---")
    if missing_in_ws:
        print(f"  MISSING in workspace ({len(missing_in_ws)}):")
        for f in missing_in_ws:
            print(f"    - {f}")
    else:
        print("  All canonical subdirs/files present in workspace ✓")

    if extra_in_ws:
        print(f"  EXTRA in workspace ({len(extra_in_ws)}):")
        for f in extra_in_ws:
            print(f"    + {f}")
    else:
        print("  No extra files in workspace ✓")

    print()
    print("--- Content consistency (canonical vs workspace copy) ---")
    if content_drift:
        print(f"  CONTENT DIFFERS ({len(content_drift)}):")
        for f in content_drift:
            print(f"    ! {f}")
        print("  → sync with: cp <canonical>/<file> <workspace>/<file>")
    else:
        print("  All files byte-identical ✓")

    print()
    print("--- Repo-root copy (<workspace-root>/neat-freak/SKILL.md) ---")
    print(f"  {repo_root_status}")

    print()
    print("--- __pycache__ check ---")
    if pycache_issues:
        print(f"  FOUND ({len(pycache_issues)}):")
        for p in pycache_issues:
            print(f"    ! {p}")
    else:
        print("  Clean ✓")

    has_issues = bool(missing_in_ws or extra_in_ws or pycache_issues or content_drift)
    print()
    if has_issues:
        print("RESULT: DRIFT DETECTED")
        return 1
    else:
        print("RESULT: CLEAN")
        return 0

if __name__ == "__main__":
    sys.exit(run())
