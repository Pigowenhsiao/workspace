# Hermes Cron Job Reference

## jobs.json Structure

Location: `~/.hermes/cron/jobs.json`

Top-level key is `"jobs"` (array), NOT a dict keyed by job name.

```python
import os
import json
with open(os.path.expanduser('~/.hermes/cron/jobs.json')) as f:
    d = json.load(f)
# d['jobs'] is the list of job objects
```

Each job object fields:
- `id`: unique string
- `name`: display name
- `prompt`: execution prompt
- `skills`: list of skill names to load
- `skill`: primary skill name (null if script-based)
- `model`: model name (e.g. "MiniMax-M2.7") or null
- `provider`: provider name or null
- `schedule`: `{"kind": "cron", "expr": "0 0 * * *", "display": "0 0 * * *"}`
- `schedule_display`: cron expression string
- `repeat`: `{"times": null, "completed": N}` — completed count
- `enabled`: bool
- `state`: "scheduled" | "paused" | ...
- `last_run_at`: ISO timestamp
- `last_status`: "ok" | "error" | ...
- `deliver`: "telegram" | "origin" | ...
- `origin`: `{"platform": "telegram", "chat_id": "...", "chat_name": "..."}`

## Output Directory

Each job has an output dir under `~/.hermes/cron/output/<job-id>/` containing timestamped `.md` files with job run outputs.

## Health Check Command

```bash
# List all jobs with schedule + enabled + last_status
# Read jobs.json as array (not dict)
python3 -c "
import json
with open('$HOME/.hermes/cron/jobs.json') as f:
    d = json.load(f)
for j in d['jobs']:
    print(f\"{j['name']}: schedule={j['schedule_display']} last={j.get('last_status','?')} enabled={j['enabled']}\")"
```

## Cron Job Patterns (Pigo's Setup)

| Name | Schedule | Model | Skills | Deliver |
|------|----------|-------|--------|---------|
| 每日晨報 | `0 0 * * *` | default | none | telegram |
| Hermes 每日備份 | `0 0 * * *` | default | none | telegram |
| HF Daily Papers | `0 1 * * *` | default | hermes-agent | telegram |
| 每日精選晚報 | `0 12 * * *` | MiniMax-M2.7 | hermes-agent, article-to-obsidian-knowledge | origin |
| 週更新 superpowers+GSD+gstack | `0 1 * * 1` | MiniMax-M2.7 | none | origin |
| Vault 整潔同步（neat-freak） | `0 16 * * *` | default | neat-freak | origin |