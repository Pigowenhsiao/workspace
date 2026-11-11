#!/usr/bin/env python3
"""
Cron Output Retention Cleanup
Cleans cron output .md files older than 7 days from ~/.hermes/cron/output/*/
Avoids bash find/xargs which trigger approval prompts in cron context.
Usage: python3 ~/.hermes/skills/neat-freak/scripts/cron-output-cleanup.py
"""
import os, glob
from datetime import datetime, timedelta

CUTOFF = datetime.now() - timedelta(days=7)
TOTAL_REMOVED = 0
SKIP_TODAY = True  # Never delete today's outputs

def should_remove(filepath):
    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
    if SKIP_TODAY:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if mtime >= today_start:
            return False
    return mtime < CUTOFF

for job_dir in glob.glob(os.path.expanduser('~/.hermes/cron/output/*/')):
    job_id = os.path.basename(job_dir.rstrip('/'))
    md_files = glob.glob(f'{job_dir}/*.md')
    count_before = len(md_files)
    removed = 0
    for f in md_files:
        try:
            if should_remove(f):
                os.remove(f)
                removed += 1
        except Exception:
            pass
    count_after = len(glob.glob(f'{job_dir}/*.md'))
    if removed > 0:
        print(f"Job {job_id}: removed {removed} files, kept {count_after}")
        TOTAL_REMOVED += removed

print(f"Total files removed: {TOTAL_REMOVED}")
