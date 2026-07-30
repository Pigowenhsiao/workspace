#!/usr/bin/env python3
"""
K-line + technical indicators sanity check (Step C, 2026-07-10).

Calls stock-sdk bridge to fetch 30 daily bars with MA(5,20) / RSI(14) / MACD,
then evaluates per-ticker findings about trend consistency.

Adds Check 6 to review_report.py — but the check is opt-in: if kline data is
unavailable (e.g. unsupported market / API error), findings default to empty
and review_report proceeds normally with the existing 5 checks.

Returns findings in same shape as review_report.findings:
    [{
        "severity": "SUSPECT" | "WARN" | "OK",
        "ticker": str,
        "rule": str,
        "message": str,
    }]
"""
import asyncio
import json
import sys
from pathlib import Path

# Path to the stock-sdk Node bridge (shared with google-finance skill)
BRIDGE = Path("/home/pigo/.openclaw/workspace/skills/google-finance/lib/node-bridge/stock-sdk-bridge.mjs")

# Tickers that have reliable K-line data via stock-sdk (US 105.X pseudo-symbol format)
# For non-US or unsupported markets, kline_check returns no findings.
US_TICKER_RE = "^[A-Z]{1,5}$"  # crude check


async def fetch_kline(ticker: str, market: str = "us", limit: int = 30) -> dict | None:
    """Fetch K-line + indicators from stock-sdk bridge.
    
    Args:
        ticker: e.g. "AAPL"
        market: "us" only (HK/CN need a different symbol format we don't generate)
        limit: bars to fetch (default 30, min 20 needed for MA20 + RSI)
    
    Returns:
        dict with shape {ticker, bars: [...], last_bar: {...}, source: "tencent"}
        or None if fetch failed.
    """
    if market != "us":
        # HK/CN use different kline format; out of scope for Step C
        return None
    
    # stock-sdk uses pseudo-symbol 105.AAPL for US stocks
    pseudo_symbol = f"105.{ticker}"
    payload = json.dumps({
        "kline": {"code": pseudo_symbol, "period": "daily", "limit": limit,
                  "indicators": {"ma": {"periods": [5, 20]}, "rsi": {"period": 14}, "macd": {}}},
    })
    
    # Use a small Node script that takes pseudo_symbol and returns kline
    node_script = f"""
import {{ StockSDK }} from 'stock-sdk';
const sdk = new StockSDK();
const r = await sdk.kline.withIndicators('{pseudo_symbol}', {{
  period: 'daily',
  limit: {limit},
  indicators: {{ ma: {{ periods: [5, 20] }}, rsi: {{ period: 14 }}, macd: {{}} }},
}});
console.log(JSON.stringify({{ bars: r.map(b => ({{date: b.date, close: b.close, ma: b.ma, macd: b.macd, rsi: b.rsi}})) }}));
"""
    
    proc = await asyncio.create_subprocess_exec(
        "node", "--input-type=module", "-e", node_script,
        cwd=str(BRIDGE.parent),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=20,
        )
    except asyncio.TimeoutError:
        proc.kill()
        return None
    
    if proc.returncode != 0:
        return None
    
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return None
    
    if not data.get("bars"):
        return None
    
    return {
        "ticker": ticker,
        "bars": data["bars"],
        "last_bar": data["bars"][-1] if data["bars"] else None,
        "source": "tencent",
    }


def _evaluate_kline(ticker: str, current_price: float, kline: dict) -> list[dict]:
    """Evaluate a single ticker's K-line indicators.
    
    Args:
        ticker: e.g. "AAPL"
        current_price: latest price (from quote fetcher)
        kline: dict returned by fetch_kline
    
    Returns:
        list of findings (empty list if no issues)
    """
    findings = []
    last = kline["last_bar"]
    if not last:
        return findings
    
    ma5 = last.get("ma", {}).get("ma5")
    ma20 = last.get("ma", {}).get("ma20")
    rsi14 = last.get("rsi", {}).get("rsi14")
    macd_dif = last.get("macd", {}).get("dif")
    macd_dea = last.get("macd", {}).get("dea")
    
    # Rule 1: RSI overbought (price might reverse soon)
    if rsi14 is not None and rsi14 > 75:
        findings.append({
            "severity": "SUSPECT",
            "ticker": ticker,
            "rule": "kline_rsi_overbought",
            "message": f"RSI(14)={rsi14:.1f} > 75 — short-term overbought, watch for reversal",
        })
    
    # Rule 2: Price far above MA20 — overextended, OR far below — oversold
    if ma20 is not None and ma20 > 0:
        deviation_pct = ((current_price / ma20) - 1) * 100
        if abs(deviation_pct) > 12:
            # Check RSI doesn't confirm the move (i.e. price should be overbought if far above MA20)
            rsi_confirms = (
                (deviation_pct > 0 and rsi14 is not None and rsi14 > 65) or
                (deviation_pct < 0 and rsi14 is not None and rsi14 < 35)
            )
            if not rsi_confirms:
                rsi_str = f"{rsi14:.1f}" if rsi14 is not None else "N/A"
                findings.append({
                    "severity": "SUSPECT",
                    "ticker": ticker,
                    "rule": "kline_price_far_from_ma20",
                    "message": (
                        f"Price {current_price} deviates {deviation_pct:+.1f}% from MA20={ma20:.2f}, "
                        f"but RSI(14)={rsi_str} doesn't confirm — "
                        f"possible parser/spurious quote"
                    ),
                })
    
    # Rule 3: MACD death cross (DIF < DEA, bearish signal)
    if macd_dif is not None and macd_dea is not None and macd_dif < macd_dea:
        # Only flag if divergence is significant
        if abs(macd_dif - macd_dea) > 0.5:
            findings.append({
                "severity": "WARN",
                "ticker": ticker,
                "rule": "kline_macd_death_cross",
                "message": (
                    f"MACD DIF={macd_dif:.2f} < DEA={macd_dea:.2f} — short-term bearish"
                ),
            })
    
    # Positive signal (for context, not suspicion)
    if ma5 is not None and ma20 is not None and ma5 > ma20:
        findings.append({
            "severity": "OK",
            "ticker": ticker,
            "rule": "kline_ma_bullish",
            "message": f"MA5={ma5:.2f} > MA20={ma20:.2f} — short-term uptrend confirmed",
        })
    
    return findings


async def check_ticker_kline(ticker: str, current_price: float, market: str = "us") -> list[dict]:
    """Fetch K-line and evaluate for one ticker. Returns findings list (may be empty)."""
    if market != "us":
        return []
    
    kline = await fetch_kline(ticker, market=market)
    if kline is None or not kline.get("last_bar"):
        # Silently skip on failure — kline check is opt-in
        return []
    
    return _evaluate_kline(ticker, current_price, kline)


async def check_batch_kline(quotes: list[dict]) -> dict[str, list[dict]]:
    """Run kline check on a batch of quotes.
    
    Args:
        quotes: list of unified-schema quote dicts (from fetch_with_stock_sdk)
                Must include 'ticker', 'exchange' (→ market), 'price'.
    
    Returns:
        dict mapping ticker → list of findings.
    """
    out = {}
    for q in quotes:
        ticker = q.get("ticker")
        price = q.get("price")
        exchange = q.get("exchange", "")
        if not ticker or price is None:
            continue
        market = "us" if exchange.upper() in {"NASDAQ", "NYSE", "NYSEARCA", "AMEX", "BATS", "OTC"} else None
        if not market:
            continue
        findings = await check_ticker_kline(ticker, price, market=market)
        if findings:
            out[ticker] = findings
        # Brief delay to avoid hammering the API
        await asyncio.sleep(0.2)
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("ticker")
    ap.add_argument("price", type=float, nargs="?", default=None,
                    help="Current price (optional, for cross-check with K-line close)")
    args = ap.parse_args()
    
    async def _run():
        kline = await fetch_kline(args.ticker, market="us")
        if kline is None:
            print(json.dumps({"ticker": args.ticker, "error": "fetch_kline failed"}, indent=2))
            return
        last = kline["last_bar"]
        print(json.dumps({
            "ticker": args.ticker,
            "bars_count": len(kline["bars"]),
            "last_bar": last,
        }, indent=2))
        
        if args.price is not None and last:
            findings = _evaluate_kline(args.ticker, args.price, kline)
            print("\n=== Findings ===")
            print(json.dumps(findings, indent=2))
    
    asyncio.run(_run())


if __name__ == "__main__":
    main()