#!/usr/bin/env python3
"""
Adapter providing unified quote fetch across google-finance (slow, browser) and
stock-sdk (fast, Tencent Finance API).

Output schema (canonical, both sources produce this shape):
    {
        "ticker": str,
        "exchange": str,
        "price": float | None,
        "currency": str | None,
        "change_pct": float | None,
        "prev_close": float | None,
        "open": float | None,
        "high": float | None,
        "low": float | None,
        "volume": int | None,
        "amount": int | None,
        "turnover_rate": float | None,
        "pe": float | None,
        "pb": float | None,
        "timestamp": str (ISO 8601 UTC),
        "source": "google" | "stocksdk",
        "source_native": str,
        "source_ts": str | None,
        "status": "ok" | "unavailable" | "error",
        "error": str | None,
    }

Usage:
    from fetch_with_stock_sdk import fetch_quote_unified
    result = asyncio.run(fetch_quote_unified("AAPL", "NASDAQ", source="auto"))

CLI:
    python3 fetch_with_stock_sdk.py AAPL NASDAQ
    python3 fetch_with_stock_sdk.py AAPL NASDAQ --source=stocksdk
"""
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR / "lib"))
NODE_BRIDGE = SKILL_DIR / "lib" / "node-bridge" / "stock-sdk-bridge.mjs"

US_EXCHANGES = {"NASDAQ", "NYSE", "NYSEARCA", "NYMEX", "COMEX", "OTC", "BATS", "AMEX"}
HK_EXCHANGES = {"HKG", "HKEX", "SEHK"}
CN_EXCHANGES = {"SSE", "SZSE", "SH", "SZ"}


def _exchange_to_stocksdk_market(exchange: str) -> str:
    """Map Google Finance exchange code to stock-sdk market code."""
    ex = (exchange or "").upper()
    if ex in US_EXCHANGES:
        return "us"
    if ex in HK_EXCHANGES:
        return "hk"
    if ex in CN_EXCHANGES:
        return "cn"
    return "us"


def _error_result(ticker: str, exchange: str, source: str, error_msg: str) -> dict:
    return {
        "ticker": ticker,
        "exchange": exchange,
        "price": None,
        "currency": None,
        "change_pct": None,
        "prev_close": None,
        "open": None,
        "high": None,
        "low": None,
        "volume": None,
        "amount": None,
        "turnover_rate": None,
        "pe": None,
        "pb": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "source_native": None,
        "source_ts": None,
        "status": "error",
        "error": str(error_msg)[:500],
    }


async def _fetch_stocksdk(ticker: str, exchange: str) -> dict:
    """Fetch via stock-sdk Node bridge (Tencent Finance API, ~0.5s/ticker)."""
    market = _exchange_to_stocksdk_market(exchange)
    payload = json.dumps({"tickers": [{"code": ticker, "market": market}]})

    if not NODE_BRIDGE.exists():
        return _error_result(ticker, exchange, "stocksdk",
                             f"bridge missing: {NODE_BRIDGE}")

    proc = await asyncio.create_subprocess_exec(
        "node", str(NODE_BRIDGE),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(payload.encode("utf-8")),
            timeout=30,
        )
    except asyncio.TimeoutError:
        proc.kill()
        return _error_result(ticker, exchange, "stocksdk", "bridge timeout (30s)")

    if proc.returncode != 0:
        return _error_result(ticker, exchange, "stocksdk",
                             stderr.decode("utf-8", "replace")[:500] or f"exit={proc.returncode}")

    try:
        bridge_out = json.loads(stdout)
    except json.JSONDecodeError as e:
        return _error_result(ticker, exchange, "stocksdk",
                             f"bridge returned invalid JSON: {e}")

    for r in bridge_out.get("results", []):
        if r["ticker"].upper() == ticker.upper():
            return _from_stocksdk(r, ticker, exchange)

    for e in bridge_out.get("errors", []):
        if e["ticker"].upper() == ticker.upper():
            return _error_result(ticker, exchange, "stocksdk", e.get("error", "unknown"))

    return {
        "ticker": ticker,
        "exchange": exchange,
        "price": None, "currency": None, "change_pct": None,
        "prev_close": None, "open": None, "high": None, "low": None,
        "volume": None, "amount": None, "turnover_rate": None,
        "pe": None, "pb": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "stocksdk",
        "source_native": "tencent",
        "source_ts": None,
        "status": "unavailable",
        "error": "ticker not in stocksdk response (may not exist or unsupported market)",
    }


def _from_stocksdk(r: dict, ticker: str, exchange: str) -> dict:
    return {
        "ticker": ticker,
        "exchange": exchange,
        "price": r.get("price"),
        "currency": r.get("currency"),
        "change_pct": r.get("change_pct"),
        "prev_close": r.get("prev_close"),
        "open": r.get("open"),
        "high": r.get("high"),
        "low": r.get("low"),
        "volume": r.get("volume"),
        "amount": r.get("amount"),
        "turnover_rate": r.get("turnover_rate"),
        "pe": r.get("pe"),
        "pb": r.get("pb"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "stocksdk",
        "source_native": r.get("raw_source", "tencent"),
        "source_ts": r.get("source_ts"),
        "status": "ok" if r.get("price") is not None else "unavailable",
        "error": None,
    }


async def _fetch_google(ticker: str, exchange: str) -> dict:
    """Fetch via google-finance (Playwright, ~20s/ticker)."""
    from fetch_quote import fetch_quote as fetch_google_raw
    raw = await fetch_google_raw(ticker, exchange)
    return _from_google(raw)


def _from_google(raw: dict) -> dict:
    change_pct = raw.get("change_pct")
    if isinstance(change_pct, str):
        try:
            change_pct = float(change_pct.replace("+", "").replace("%", ""))
        except ValueError:
            change_pct = None

    return {
        "ticker": raw.get("ticker"),
        "exchange": raw.get("exchange"),
        "price": raw.get("price"),
        "currency": raw.get("currency"),
        "change_pct": change_pct,
        "prev_close": None,
        "open": None,
        "high": None,
        "low": None,
        "volume": None,
        "amount": None,
        "turnover_rate": None,
        "pe": None,
        "pb": None,
        "timestamp": raw.get("timestamp"),
        "source": "google",
        "source_native": raw.get("source", "body"),
        "source_ts": None,
        "status": raw.get("status", "unknown"),
        "error": raw.get("error"),
    }


async def fetch_quote_unified(ticker: str, exchange: str, source: str = "auto") -> dict:
    """Fetch a single quote with unified schema across sources.
    
    Args:
        ticker: e.g. "AAPL", "2330"
        exchange: e.g. "NASDAQ", "TPE"
        source: "auto" (google → stocksdk fallback), "google", or "stocksdk"
    
    Returns:
        Unified schema dict.
    """
    if source == "stocksdk":
        return await _fetch_stocksdk(ticker, exchange)
    if source == "google":
        return await _fetch_google(ticker, exchange)
    if source == "auto":
        google_result = await _fetch_google(ticker, exchange)
        if google_result["status"] == "ok":
            return google_result
        stocksdk_result = await _fetch_stocksdk(ticker, exchange)
        if stocksdk_result.get("status") == "ok":
            stocksdk_result["note"] = (
                f"google fell through (status={google_result['status']}, "
                f"err={google_result.get('error') or 'no_change_pct'})"
            )
        return stocksdk_result
    raise ValueError(f"unknown source: {source!r}")


async def fetch_batch_unified(watchlist: list, source: str = "auto",
                              delay_between: float = 0.5) -> list:
    """Fetch a watchlist with unified schema."""
    results = []
    for i, item in enumerate(watchlist):
        ticker = item["ticker"]
        exchange = item["exchange"]
        print(f"[{i+1}/{len(watchlist)}] {ticker}:{exchange} ({source})...",
              file=sys.stderr)
        result = await fetch_quote_unified(ticker, exchange, source=source)
        results.append(result)
        if result.get("price"):
            print(f"  ✓ {result['currency']} {result['price']} "
                  f"({result.get('change_pct')}%, source={result['source']})",
                  file=sys.stderr)
        else:
            print(f"  ✗ {result['status']}: {result.get('error', '?')}",
                  file=sys.stderr)
        if i < len(watchlist) - 1:
            await asyncio.sleep(delay_between)
    return results


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("ticker")
    ap.add_argument("exchange")
    ap.add_argument("--source", choices=["auto", "google", "stocksdk"], default="auto")
    args = ap.parse_args()
    
    result = asyncio.run(fetch_quote_unified(args.ticker, args.exchange, source=args.source))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    sys.exit({"ok": 0, "unavailable": 2}.get(result["status"], 1))


if __name__ == "__main__":
    main()