---
name: finance-writer
description: Generate Loop report from fetch + review + LOOP-STATE. Creates human-readable markdown with TL;DR, ticker table, investment notes.
---

# Finance Writer Skill

Generates Loop report from google-finance + reviewer-finance outputs + LOOP-STATE.md.

## When to use

- After fetch + review (kimberly's Loop Step 5: Writer)
- As final step in daily Loop

## Usage

```bash
python3 ~/.openclaw/workspace/skills/finance-writer/scripts/write_report.py \
    FETCH.json \
    REVIEW.json \
    STATE.md \
    OUTPUT.md
```

**Args**:
1. `FETCH.json` — output from `google-finance/fetch_batch.py`
2. `REVIEW.json` — output from `reviewer-finance/review_report.py`
3. `STATE.md` — `LOOP-STATE.md` (memory core)
4. `OUTPUT.md` — path to write report

## Output

Markdown report with:

- **TL;DR** (5 key points, priority tickers first: LITE, 2330, NVDA, TSM, PLTR)
- **Reviewer Verdict** (PASS/FAIL + score)
- **Summary** (OK/SUSPECT/ERROR counts)
- **Findings** (if any SUSPECT/ERROR)
- **31 ticker full table** (with vs-last comparison)
- **Investment notes** (from LOOP-STATE: user prefs, market context, next watch)

## Files

- `scripts/write_report.py` (~200 lines, pure stdlib)

## Integration

```bash
# Daily Loop flow
python3 google-finance/scripts/fetch_batch.py watchlist.json /tmp/fetch.json
python3 reviewer-finance/scripts/review_report.py /tmp/fetch.json state/LOOP-STATE.md
python3 finance-writer/scripts/write_report.py \
    /tmp/fetch.json \
    /tmp/fetch-review.json \
    state/LOOP-STATE.md \
    ~/Downloads/Sotck/loop-report-$(date +%Y%m%d).md
```
