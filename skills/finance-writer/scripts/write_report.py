#!/usr/bin/env python3
"""
finance-writer skill — Write Loop report from fetch + review + LOOP-STATE.

Input:
- fetch_batch.json (from google-finance skill)
- review_report.json (from reviewer-finance skill)
- LOOP-STATE.md (memory core)

Output: loop-report-YYYYMMDD.md (human-readable report)
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def load_inputs(fetch_json_path: str, review_json_path: str, state_path: str) -> dict:
    """Load all inputs and return combined data."""
    data = {
        "fetch": json.loads(Path(fetch_json_path).read_text(encoding="utf-8")),
        "review": json.loads(Path(review_json_path).read_text(encoding="utf-8")),
        "state": Path(state_path).read_text(encoding="utf-8") if Path(state_path).exists() else "",
    }
    return data


def parse_last_prices_from_state(state_text: str) -> dict[str, float]:
    """Parse last prices from LOOP-STATE.md.

    Scoped to the NEWEST run block inside the 「上次報告摘要」 section.

    Bug fixed 2026-11-12: the old version scanned the whole file and let the
    LAST match win, so the legacy 2026-07-07 baseline block at the bottom of
    the section always overrode the previous run's prices. The 2026-11-12
    report consequently showed LITE -10.2% / NVDA -11.2% when Google Finance
    reported +10.67% / +2.92% for the same session.
    """
    import re
    prices = {}

    # 1. Isolate the 「上次報告摘要」 section.
    sec = re.search(r'^##\s+上次報告摘要.*$', state_text, re.MULTILINE)
    if not sec:
        return prices
    rest = state_text[sec.end():]
    nxt = re.search(r'^##\s', rest, re.MULTILINE)
    section = rest[:nxt.start()] if nxt else rest

    # 2. Isolate the newest run block inside it.
    blocks = list(re.finditer(r'^\*\*\d{4}-\d{2}-\d{2}[^*\n]*\*\*\s*$',
                              section, re.MULTILINE))
    if blocks:
        start = blocks[0].end()
        end = blocks[1].start() if len(blocks) > 1 else len(section)
        block = section[start:end]
    else:
        block = section

    for line in block.split("\n"):
        if not line.strip():
            continue
        m = re.search(r'- ([A-Z]{1,5}|\d{4})[^0-9]*\$?\*?\*?([0-9,]+\.?\d*)', line)
        if m:
            ticker = m.group(1)
            if len(ticker) == 4 and ticker.isdigit():
                if 2000 <= int(ticker) <= 2030:
                    continue
            try:
                price = float(m.group(2).replace(",", ""))
                if 10 <= price <= 10000:
                    prices[ticker] = price
            except ValueError:
                pass
    return prices


def _session_change_suffix(entry: dict) -> str:
    """Render Google's own session change (change_pct) as a suffix.

    Used when the "vs 上次" delta is unavailable or ~0 (same-session re-run),
    so the reader still sees the real daily move. Returns "" when the fetch
    carries no daily change.
    """
    chg = entry.get("change_pct")
    if not isinstance(chg, (int, float)):
        return ""
    return f" ({chg:+.2f}% 今日)"


def generate_report(data: dict, output_path: str) -> dict:
    """Generate markdown report from combined data."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    taipei_ts = datetime.now().strftime("%Y-%m-%d %H:%M 台北")
    
    fetch = data["fetch"]
    review = data["review"]
    state = data["state"]
    
    # Parse last prices for comparison
    last_prices = parse_last_prices_from_state(state)
    
    # Build report
    lines = []
    lines.append(f"# 每日美股+台股市場研究")
    lines.append(f"")
    lines.append(f"**生成時間**: {taipei_ts}  ")
    lines.append(f"**資料來源**: Google Finance via Playwright  ")
    lines.append(f"")
    lines.append("---")
    lines.append("")
    
    # TL;DR section
    lines.append("## TL;DR（5 點重點）")
    lines.append("")
    
    # Get top 5 by importance (LITE + key tickers first)
    priority = ["LITE", "2330", "NVDA", "TSM", "PLTR", "ORCL", "AMD", "MSFT", "AAPL", "GOOGL", "AMZN", "META"]
    fetch_by_ticker = {t["ticker"]: t for t in fetch}
    tldr = []
    for ticker in priority:
        if ticker in fetch_by_ticker:
            t = fetch_by_ticker[ticker]
            price = t.get("price", 0)
            currency = t.get("currency", "USD")
            if price:
                # Check change vs last
                change = ""
                if ticker in last_prices:
                    last = last_prices[ticker]
                    pct = (price - last) / last * 100
                    pct_str = f"+{pct:.1f}%" if pct > 0 else f"{pct:.1f}%"
                    # When the previous run already covered the same session the
                    # delta is ~0, which reads as "0.0% vs 上次" and hides the
                    # actual session move. Fall back to Google's own daily
                    # change in that case.
                    if abs(pct) < 0.1:
                        change = _session_change_suffix(t)
                    else:
                        change = f" ({pct_str} vs 上次)"
                else:
                    change = _session_change_suffix(t)
                tldr.append(f"- **{ticker}**: {currency} {price:,.2f}{change}")
    
    # Add any remaining
    for t in fetch:
        if t["ticker"] not in priority and len(tldr) < 5:
            ticker = t["ticker"]
            price = t.get("price", 0)
            currency = t.get("currency", "USD")
            if price:
                tldr.append(f"- **{ticker}**: {currency} {price:,.2f}")
    
    for item in tldr[:5]:
        lines.append(item)
    lines.append("")
    
    # Reviewer verdict
    lines.append("## Reviewer Verdict")
    lines.append("")
    verdict = review.get("overall", "UNKNOWN")
    score = review.get("score", 0)
    emoji = "✅" if verdict == "PASS" else "❌"
    lines.append(f"{emoji} **{verdict}** (Score: {score}/100)  ")
    lines.append("")
    
    # Summary
    summary = review.get("summary", {})
    lines.append(f"| OK | SUSPECT | ERROR |")
    lines.append(f"|---|---|---|")
    lines.append(f"| {summary.get('ok', 0)} | {summary.get('suspect', 0)} | {summary.get('error', 0)} |")
    lines.append("")
    
    # Findings (if any SUSPECT/ERROR)
    findings = review.get("findings", [])
    if findings:
        lines.append("### ⚠️ 異常警示")
        lines.append("")
        for f in findings:
            sev = f.get("severity", "?")
            ticker = f.get("ticker", "?")
            msg = f.get("message", "")
            rule = f.get("rule", "")
            lines.append(f"- **{sev}** [{ticker}] ({rule}): {msg}")
        lines.append("")
    
    # Full ticker table
    lines.append(f"## {len(fetch)} 個 ticker 完整報價")
    lines.append("")
    lines.append("| Ticker | Exchange | Price | Currency | vs 上次 (今日) |")
    lines.append("|--------|----------|-------|----------|----------------|")
    
    for t in fetch:
        ticker = t.get("ticker", "?")
        exchange = t.get("exchange", "?")
        price = t.get("price")
        currency = t.get("currency", "USD")
        
        if price:
            # Compute change vs last
            session_chg = t.get("change_pct")
            session_str = f"{session_chg:+.2f}%" if isinstance(session_chg, (int, float)) else "-"
            if ticker in last_prices:
                last = last_prices[ticker]
                pct = (price - last) / last * 100
                if abs(pct) > 0.1:
                    pct_str = f"+{pct:.1f}%" if pct > 0 else f"{pct:.1f}%"
                    change = pct_str
                else:
                    change = "-"
            else:
                change = "NEW"

            lines.append(f"| {ticker} | {exchange} | {price:,.2f} | {currency} | {change} ({session_str}) |")
    lines.append("")
    
    # Investment notes (from LOOP-STATE)
    lines.append("## 投資筆記")
    lines.append("")
    
    # Extract key sections from LOOP-STATE
    if state:
        # User preferences
        if "用戶偏好" in state:
            lines.append("### 用戶偏好")
            lines.append("")
            start = state.find("## 用戶偏好")
            if start != -1:
                end = state.find("## ", start + 3)
                if end == -1:
                    end = len(state)
                prefs = state[start:end].split("\n")[2:8]
                for p in prefs:
                    if p.strip():
                        lines.append(p)
            lines.append("")
        
        # Market context
        if "當前市場線索" in state:
            lines.append("### 當前市場線索")
            lines.append("")
            # Match the heading as a full line. `find("## ", start + 3)` used to
            # be used here, but that also matches the "## " inside a "### "
            # sub-heading, which truncated the section early.
            import re as _re
            m_ctx = _re.search(r'^##\s+當前市場線索.*$', state, _re.MULTILINE)
            if m_ctx:
                rest = state[m_ctx.end():]
                m_next = _re.search(r'^##\s', rest, _re.MULTILINE)
                ctx = rest[:m_next.start()] if m_next else rest
                # Skip the blockquote intro line and blanks; keep the bullets.
                bullets = [ln for ln in ctx.split("\n")
                           if ln.strip().startswith("- ")][:6]
                for c in bullets:
                    lines.append(c)
            lines.append("")
    
    # Next watch
    if "下次繼續追蹤" in state:
        lines.append("### 下次繼續追蹤")
        lines.append("")
        start = state.find("## 下次繼續追蹤")
        if start != -1:
            end = state.find("## ", start + 3)
            if end == -1:
                end = len(state)
            watch = state[start:end].split("\n")[2:12]
            for w in watch:
                if w.strip():
                    lines.append(w)
        lines.append("")
    
    # Footer
    lines.append("---")
    lines.append(f"*Generated by finance-writer skill at {ts}*")
    
    # Write output
    output = "\n".join(lines)
    Path(output_path).write_text(output, encoding="utf-8")
    
    return {
        "output_path": output_path,
        "tldr_count": len(tldr[:5]),
        "findings_count": len(findings),
        "tickers_count": len(fetch),
    }


def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} FETCH.json REVIEW.json STATE.md OUTPUT.md", file=sys.stderr)
        sys.exit(1)
    
    fetch_json = sys.argv[1]
    review_json = sys.argv[2]
    state_path = sys.argv[3]
    output_path = sys.argv[4]
    
    print(f"📥 Loading inputs...", file=sys.stderr)
    data = load_inputs(fetch_json, review_json, state_path)
    
    print(f"✍️  Writing report...", file=sys.stderr)
    result = generate_report(data, output_path)
    
    print(f"✅ Report written: {output_path}", file=sys.stderr)
    print(f"   TL;DR items: {result['tldr_count']}", file=sys.stderr)
    print(f"   Findings: {result['findings_count']}", file=sys.stderr)
    print(f"   Tickers: {result['tickers_count']}", file=sys.stderr)


if __name__ == "__main__":
    main()
