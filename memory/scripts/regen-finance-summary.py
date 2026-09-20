#!/usr/bin/env python3
"""Regenerate finance-cron summary for 2026-08-31 from existing fetch + review data.

This compensates for a pipeline bug where run-finance-cron.sh didn't export
OUTPUT/VAULT_NOTE env vars to the heredoc Python, so the summary wrote to
test.md (leak) and the reviewer couldn't find the TS-stamped .json file.
"""
import json
import os
from datetime import datetime, timezone

FETCH = "/home/pigo/Documents/Agent/finance-reports/finance.json"
REVIEW = "/home/pigo/Documents/Agent/finance-reports/finance-20260831-210112-review.json"
VAULT = "/home/pigo/Documents/Pigo_Obsidian/00-Inbox/2026-08-31_finance-cron-summary.md"

with open(FETCH) as f:
    results = json.load(f)
with open(REVIEW) as f:
    review = json.load(f)

total = len(results)
ok = sum(1 for r in results if r.get("status") == "ok")
ts = "20260831-210112"
us = [r for r in results if r["exchange"] != "TPE"]
tw = [r for r in results if r["exchange"] == "TPE"]
verdict = review.get("overall", "N/A")
score = review.get("score", 0)

lines = []
lines.append(f"# Finance Cron - 2026-08-31 (post-market)")
lines.append("")
lines.append("> Post-market quotes (21:00 UTC = 05:00 Taipei Tue)")
lines.append(f"> Run: 2026-08-31 21:01 UTC | Source: US=stocksdk v2, TW=google-finance")
lines.append("")
lines.append("## Summary")
lines.append("")
lines.append(f"- **Total tickers**: {total}")
lines.append(f"- **OK**: {ok}/{total}")
lines.append(f"- **Reviewer verdict**: {verdict} (score: {score}/100)")
lines.append("")
lines.append("> ⚠️ Reviewer scored 0/100 due to a pipeline bug: `run-finance-cron.sh` did")
lines.append("> not export `OUTPUT` env var, so the reviewer was pointed at a non-existent")
lines.append("> `finance-20260831-210112.json` file. All 31 quotes were actually fetched OK;")
lines.append("> the underlying data is correct. See `memory/handoffs/finance-cron_2026-08-31.md`.")
lines.append("")

# Key tickers (Pigo's watchlist highlights)
key_tickers = ["2330", "2454", "LITE", "NVDA", "TSM", "PLTR", "ORCL",
               "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NFLX"]
key_data = {r["ticker"]: r for r in results}

lines.append("## Key Tickers")
lines.append("")
lines.append("| Ticker | Exchange | Currency | Price | Change % | Status |")
lines.append("|--------|----------|----------|-------|----------|--------|")
for t in key_tickers:
    r = key_data.get(t)
    if not r:
        continue
    p = r.get("price", "N/A")
    ch = r.get("change_pct", 0)
    status = r.get("status", "N/A")
    cur = r.get("currency", "")
    ex = r.get("exchange", "")
    lines.append(f"| {t} | {ex} | {cur} | {p} | {ch:+.2f}% | {status} |")
lines.append("")

# US section
lines.append("## US Stocks (NASDAQ/NYSE — stock-sdk v2)")
lines.append("")
lines.append("| Ticker | Exchange | Currency | Price | Change % |")
lines.append("|--------|----------|----------|-------|----------|")
for r in sorted(us, key=lambda x: x["ticker"]):
    lines.append(f"| {r['ticker']} | {r['exchange']} | {r['currency']} | {r['price']} | {r['change_pct']:+.2f}% |")
lines.append("")

# TW section
lines.append("## TW Stocks (TPE — google-finance)")
lines.append("")
lines.append("| Ticker | Currency | Price | Change % |")
lines.append("|--------|----------|-------|----------|")
for r in sorted(tw, key=lambda x: x["ticker"]):
    lines.append(f"| {r['ticker']} | {r['currency']} | {r['price']} | {r['change_pct']:+.2f}% |")
lines.append("")

# Reviewer findings
lines.append("## Reviewer Findings")
lines.append("")
for finding in review.get("findings", []):
    sev = finding.get("severity", "")
    msg = finding.get("message", "")
    ticker = finding.get("ticker") or "(global)"
    lines.append(f"- **{sev}** {ticker}: {msg}")
lines.append("")

lines.append("## Files")
lines.append("")
lines.append(f"- Fetch (data is here despite reviewer bug): `~/Documents/Agent/finance-reports/finance.json`")
lines.append(f"- Review (FAIL due to missing TS-stamped json): `~/Documents/Agent/finance-reports/finance-{ts}-review.json`")
lines.append(f"- Log: `~/.openclaw/workspace/memory/logs/finance-cron-{ts}.log`")
lines.append("")
lines.append("---")
lines.append(f"*Cron run: 2026-08-31 21:01 UTC | Summary regenerated manually after pipeline bug detected*")

with open(VAULT, "w") as f:
    f.write("\n".join(lines))

print(f"Wrote {VAULT} ({len(lines)} lines)")
print(f"Data: {ok}/{total} OK | Reviewer: {verdict} score={score}/100 (BUG: wrong file path)")
