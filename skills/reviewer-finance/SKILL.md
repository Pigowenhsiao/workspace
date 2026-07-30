---
name: reviewer-finance
description: Auto-review Google Finance batch reports. Checks price sanity, status completeness, change detection (vs LOOP-STATE), URL format, currency consistency. Outputs PASS/FAIL verdict.
---

# Reviewer Finance Skill

Automated reviewer for Google Finance batch reports (from `google-finance` skill). Implements the **Reviewer** component of Kimberly's Loop Engineering framework — "like a read-only auditor that only answers PASS or FAIL."

## When to use

- After running `fetch_batch.py` from google-finance skill
- Before writing daily research report
- As a sanity check before commit / publish

## Usage

```bash
python3 ~/.openclaw/workspace/skills/reviewer-finance/scripts/review_report.py \
    REPORT.json \
    [LOOP-STATE.md]
```

**Args**:
- `REPORT.json` — required, output from `fetch_batch.py`
- `LOOP-STATE.md` — optional, enables change detection

**Outputs** (next to REPORT.json):
- `{basename}-review.md` — human-readable verdict
- `{basename}-review.json` — machine-readable verdict

**Exit code**:
- `0` = PASS (score >= 95, no errors)
- `1` = FAIL (score < 95 or errors detected)

## Review rules (5)

| Rule | Severity | Trigger | Score impact |
|------|----------|---------|--------------|
| `status_completeness` | ERROR | status != 'ok' | -10 |
| `price_sanity` | SUSPECT | price outside `[10, 10000]` USD / `[10, 5000]` TWD / `[10, 10000]` HKD | -5 |
| `change_detection` | SUSPECT | vs LOOP-STATE last report, abs change > 20% | -5 |
| `currency_consistency` | SUSPECT | exchange→currency mismatch (TPE→TWD, NASDAQ/NYSE→USD, HKG→HKD) | -5 |
| `url_format` | SUSPECT | URL doesn't match `https://www.google.com/finance/quote/{ticker}:{exchange}` | -5 |

**Score formula**: `100 - (suspect_count × 5) - (error_count × 10)`, clamped to `[0, 100]`.

**PASS condition**: score >= 95 AND error_count == 0.

## LOOP-STATE.md parsing

`parse_loop_state_prices()` reads LOOP-STATE.md for last reported prices. Accepted formats:

```markdown
- LITE（公司股）：**$722.05 USD**
- 2330 台積電：**NT$2,450**
- NVDA：**$195.55**
```

Validated range: 10-10000 (filters out years like 2026).

## Output schema

```json
{
  "overall": "PASS",
  "score": 100,
  "summary": {
    "ok": 31,
    "suspect": 0,
    "error": 0,
    "total": 31
  },
  "findings": [
    {
      "severity": "ERROR",
      "ticker": "AAPL",
      "rule": "status_completeness",
      "message": "Status = 'unavailable'"
    }
  ]
}
```

## Files

- `scripts/review_report.py` — main reviewer logic (~280 lines, pure stdlib)

## Integration

```bash
# Daily loop pattern
python3 google-finance/scripts/fetch_batch.py watchlist.json /tmp/report.json
python3 reviewer-finance/scripts/review_report.py /tmp/report.json state/LOOP-STATE.md
# Check exit code → if 0: PASS, proceed; if 1: FAIL, escalate
```