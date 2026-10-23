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
TW_EXCHANGES = {"TPE", "TWSE", "TPEX"}

# Yahoo Finance chart API (no geo-block, reliable for TW/HK/CN/US)
YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{code}?range=1d&interval=1d"


def _yahoo_code(ticker: str, exchange: str) -> str:
    """Map (ticker, exchange) to a Yahoo Finance symbol."""
    ex = (exchange or "").upper()
    t = (ticker or "").strip()
    if ex in TW_EXCHANGES and not t.upper().endswith((".TW", ".TWO")):
        return f"{t}.TW"
    return t


async def _fetch_yahoo(ticker: str, exchange: str) -> dict:
    """Fetch via Yahoo Finance chart API (fast, no geo-block, good for TPE).

    Chosen as the TPE source because Google Finance hard-blocks this host
    with HTTP 403 ("Google 財經目前不支援你所在的地區"), so the Playwright
    parser never sees a rendered price for Taiwan tickers.
    """
    import urllib.request

    code = _yahoo_code(ticker, exchange)
    codes = [code]
    # Older TWSE/TPEX listings are indexed by Yahoo under the ".TWO" suffix
    # (e.g. 4533 -> 4533.TWO), while ".TW" returns HTTP 404 / "symbol may be
    # delisted". Fall back to ".TWO" only after the primary symbol fails, so
    # working tickers keep their existing single-request path.
    if code.upper().endswith(".TW"):
        codes.append(code[:-3] + ".TWO")

    def _build(code: str) -> urllib.request.Request:
        url = YAHOO_CHART.format(code=code)
        return urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    def _get(req: urllib.request.Request):
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _parse(data):
        """Return (payload, error_message). error_message is None on success."""
        chart = (data or {}).get("chart") or {}
        if chart.get("error"):
            return None, str(chart["error"])[:200]
        results = chart.get("result") or []
        if not results:
            return None, "empty chart result"
        meta = results[0].get("meta") or {}
        price = meta.get("regularMarketPrice")
        if price is None:
            return None, "no regularMarketPrice in meta"
        return (chart, meta), None

    parsed = None
    last_err = None
    for attempt_code in codes:
        try:
            data = await asyncio.to_thread(_get, _build(attempt_code))
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            continue
        parsed, perr = _parse(data)
        if parsed is not None:
            last_err = perr
            break
        last_err = perr

    if parsed is None:
        return _error_result(ticker, exchange, "yahoo", str(last_err))

    chart, meta = parsed
    price = meta.get("regularMarketPrice")

    prev_close = meta.get("chartPreviousClose") or meta.get("previousClose")
    change_pct = None
    if price is not None and prev_close:
        change_pct = round((price - prev_close) / prev_close * 100, 4)

    return {
        "ticker": ticker,
        "exchange": exchange,
        "price": price,
        "currency": meta.get("currency"),
        "change_pct": change_pct,
        "prev_close": prev_close,
        "open": meta.get("regularMarketOpen"),
        "high": meta.get("regularMarketDayHigh"),
        "low": meta.get("regularMarketDayLow"),
        "volume": meta.get("regularMarketVolume"),
        "amount": None,
        "turnover_rate": None,
        "pe": None,
        "pb": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "yahoo",
        "source_native": "yahoo_chart_api",
        "source_ts": None,
        "status": "ok",
        "error": None,
        "yahoo_symbol": code,
    }


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
    if source == "yahoo":
        return await _fetch_yahoo(ticker, exchange)
    if source == "auto":
        # Google Finance is HTTP 403 geo-blocked on this host, so for
        # Taiwan tickers go straight to Yahoo and never pay the ~20s
        # Playwright cost for a guaranteed failure.
        if (exchange or "").upper() in TW_EXCHANGES:
            yahoo_result = await _fetch_yahoo(ticker, exchange)
            if yahoo_result["status"] == "ok":
                return yahoo_result
            return yahoo_result
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
    ap.add_argument("--source", choices=["auto", "google", "stocksdk", "yahoo"], default="auto")
    args = ap.parse_args()
    
    result = asyncio.run(fetch_quote_unified(args.ticker, args.exchange, source=args.source))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    sys.exit({"ok": 0, "unavailable": 2}.get(result["status"], 1))


if __name__ == "__main__":
    main()
