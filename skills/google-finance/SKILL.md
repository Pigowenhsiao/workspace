---
name: google-finance
description: Fetch stock quotes from Google Finance via Playwright using Hsiaopigo Chrome profile. Works for US, HK, TW stocks. Use when Yahoo Finance is rate-limited (429) or when user asks for Google Finance data.
---

# Google Finance Skill

Fetch stock quotes from `google.com/finance/beta/quote/{ticker}:{exchange}` using Playwright with the **Hsiaopigo Chrome profile** (Profile 1) — bypasses Yahoo Finance 429 rate limits because Google Finance uses Google's own session cookies.

## When to use

- Yahoo Finance API (`query1.finance.yahoo.com`) returns HTTP 429
- User explicitly asks for Google Finance data
- Need real-time prices for US, HK, or Taiwan stocks without rate-limit issues

## When NOT to use

- Need historical data (Yahoo is better)
- Need options chains, fundamentals, or deep financial metrics
- Ticker is on an exchange Google Finance doesn't cover (e.g., AU stocks)

## Setup

- **Profile**: `/home/pigo/.config/google-chrome/Profile 1` (already has Google session)
- **Playwright**: Already installed at `~/.cache/ms-playwright/chromium-1223`
- **No additional install needed** — but if running on a new machine: `pip install playwright && playwright install chromium`

## Usage

### Single ticker
```bash
python3 ~/.openclaw/workspace/skills/google-finance/scripts/fetch_quote.py AAPL NASDAQ
python3 ~/.openclaw/workspace/skills/google-finance/scripts/fetch_quote.py 2330 TPE
```

Output: JSON with `ticker`, `exchange`, `price`, `currency`, `change_pct`, `source`, `status`, `timestamp`.

Exit codes:
- `0` = success
- `1` = error
- `2` = unavailable (no data)

### Batch from watchlist
```bash
# Create your watchlist
cat > /tmp/my-watchlist.json << EOF
[
  {"ticker": "AAPL", "exchange": "NASDAQ"},
  {"ticker": "2330", "exchange": "TPE"}
]
EOF

# Fetch batch → Markdown report
python3 ~/.openclaw/workspace/skills/google-finance/scripts/fetch_batch.py /tmp/my-watchlist.json /tmp/report.md
```

Outputs:
- `report.md` — human-readable Markdown
- `report.json` — raw JSON for downstream processing

### Fast unified fetcher (stock-sdk adapter) — Step B (2026-07-10)

For batch/cron use cases where browser scraping is too slow (~20s/ticker), use the unified adapter that
also supports the faster stock-sdk backend (Tencent Finance API, ~0.5s/ticker).

```bash
# Single ticker, force source
python3 ~/.openclaw/workspace/skills/google-finance/scripts/fetch_with_stock_sdk.py AAPL NASDAQ --source=stocksdk
python3 ~/.openclaw/workspace/skills/google-finance/scripts/fetch_with_stock_sdk.py AAPL NASDAQ --source=google

# Auto mode: google first, fallback to stocksdk on failure
python3 ~/.openclaw/workspace/skills/google-finance/scripts/fetch_with_stock_sdk.py AAPL NASDAQ --source=auto
```

**Source modes**:

| Mode | Behavior | Speed (per ticker) | Use case |
|------|----------|---------------------|----------|
| `google` | Only Google Finance (browser scrape) | ~6-20s | Authoritative for TW/HK, has change% from title |
| `stocksdk` | Only stock-sdk (Tencent Finance API, no browser) | ~0.5s | Fast batch cron, US/HK/CN markets |
| `auto` | Try google first, fallback to stocksdk | — | Best of both, preserves accuracy for US stocks |

**Unified output schema** (both sources produce identical keys):

```json
{
  "ticker": "AAPL", "exchange": "NASDAQ",
  "price": 316.22, "currency": "USD", "change_pct": 0.9,
  "prev_close": 313.39, "open": 310.51, "high": 316.53, "low": 308.16,
  "volume": 48124490, "amount": 15128365320,
  "turnover_rate": 0.33, "pe": 38.28, "pb": 8.26,
  "timestamp": "2026-07-10T05:05:08+00:00",
  "source": "stocksdk", "source_native": "tencent",
  "source_ts": "2026-07-09 16:00:01",
  "status": "ok", "error": null
}
```

**Programmatic API** (for cron scripts):

```python
import asyncio
from fetch_with_stock_sdk import fetch_batch_unified

results = asyncio.run(fetch_batch_unified(
    [{"ticker": "AAPL", "exchange": "NASDAQ"},
     {"ticker": "TSLA", "exchange": "NASDAQ"}],
    source="stocksdk",
    delay_between=0.5,
))
```

**Validation**: AAPL tested on 2026-07-10: stocksdk and google returned identical `price=316.22`,
`change_pct=0.9`, `currency=USD`. Step A regression tests (6/6) still pass.

**Note**: stock-sdk requires Node.js v18+ and bundled `node_modules` in `lib/node-bridge/`. The bridge
is pre-installed; if missing, run `cd lib/node-bridge && npm install`.

## Supported exchanges

| Exchange code | Market | Example | Notes |
|---------------|--------|---------|-------|
| `NASDAQ` | US Nasdaq | `AAPL:NASDAQ` | ✅ Full support |
| `NYSE` | US NYSE | `TSLA:NYSE` | ✅ Full support |
| `HKG` | Hong Kong | `0700:HKG` | ✅ Full support (Tencent) |
| `TPE` | Taiwan Stock Exchange | `2330:TPE` | ✅ Full support (TSMC) |
| `TPEX` | Taipei Exchange | (rarely used) | ⚠️ Limited — most tickers return no data |

## How it works

1. **Launch Chromium** with `--user-data-dir=/home/pigo/.config/google-chrome/Profile 1`
2. **Navigate** to `https://www.google.com/finance/quote/{ticker}:{exchange}`
3. **Wait** 4 seconds for JS rendering (Google Finance is a SPA)
4. **Extract price**:
   - Try `page.title()` first (works for US stocks: `AAPL US$312.66 (▲ 1.31%)`)
   - Fall back to `document.body.innerText` regex (works for TW stocks: `$2,460.00`)
5. **Skip first $price** in body text — it's always a hot stocks list, not the target

## Output schema

```json
{
  "ticker": "2330",
  "exchange": "TPE",
  "url": "https://www.google.com/finance/quote/2330:TPE",
  "timestamp": "2026-07-07T04:50:00+00:00",
  "price": 2460.0,
  "currency": "TWD",
  "change_pct": null,
  "source": "body",
  "status": "ok",
  "error": null
}
```

## Rate limiting

- Google Finance does **not** aggressively rate-limit per IP (unlike Yahoo)
- Recommended delay: **2 seconds between requests** (set in `fetch_batch.py`)
- No CAPTCHA observed during testing

## Known limitations

- **Taiwan TPEX stocks** (上櫃) often return no data — use TPE only
- **No historical data** — this skill is for real-time quotes only
- **Google Finance UI changes** may break DOM parsing — fallback to `body.innerText` regex should survive most changes
- **headless=True** — no visible browser window on pigoserver2

## Files

- `scripts/fetch_quote.py` — single ticker CLI
- `scripts/fetch_batch.py` — batch from watchlist.json → Markdown
- `lib/parser.py` — price extraction logic (title + body)
- `references/watchlist.example.json` — sample 12-ticker watchlist
- `templates/research-heartbeat-watchlist.json` — **31-ticker list** for research-heartbeat integration (12 US + 19 TW)

## Default watchlist (research-heartbeat)

31 tickers total: **12 US stocks (9 NASDAQ + 3 NYSE) + 19 TPE 台股**.

**NASDAQ** (9): AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, NFLX, LITE
**NYSE** (3): ORCL, PLTR, TSM
**TPE 台股** (19): 2330, 2317, 2454, 2881, 2882, 2303, 2308, 2597, 4104, 2409, 8131, 2891, 1303, 2886, 1723, 2301, 4533, 2002, 2201

Updated 2026-07-07 — verified by subagent, 31/31 ok status. Includes LITE (Pigo 是 Lumentum Taiwan 員工)。

## Integration with research-heartbeat

If using this to replace the snake-based data_fetch.py (Yahoo API):

```bash
# Old (Yahoo API, may 429):
python3 ~/.openclaw/workspace/scratch/research-heartbeat/scripts/data_fetch.py

# New (Google Finance via Playwright):
python3 ~/.openclaw/workspace/skills/google-finance/scripts/fetch_batch.py \
    ~/.openclaw/workspace/skills/google-finance/templates/research-heartbeat-watchlist.json \
    ~/.openclaw/workspace/scratch/research-heartbeat/data/raw/google-finance-$(date +%Y%m%d-%H%M%S).md
```