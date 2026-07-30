#!/usr/bin/env python3
"""
Single ticker fetch from Google Finance using Playwright + Hsiaopigo profile.

Usage:
    python3 fetch_quote.py TICKER EXCHANGE
    python3 fetch_quote.py AAPL NASDAQ
    python3 fetch_quote.py 2330 TPE

Output: JSON to stdout (price, currency, change_pct, source, ticker, exchange, timestamp)
"""
import asyncio
import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# Add lib to path
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR / "lib"))

from parser import parse_page  # noqa: E402

PROFILE_PATH = "/home/pigo/.config/google-chrome/Profile 1"


async def fetch_quote(ticker: str, exchange: str) -> dict:
    """Fetch single quote from Google Finance."""
    from playwright.async_api import async_playwright
    
    url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"
    result = {
        "ticker": ticker,
        "exchange": exchange,
        "url": url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "price": None,
        "currency": None,
        "change_pct": None,
        "source": None,
        "status": "unknown",
        "error": None,
    }
    
    context = None
    try:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                PROFILE_PATH, headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--no-first-run",
                ],
                locale="zh-TW",
                timezone_id="Asia/Taipei",
                viewport={"width": 1920, "height": 1080},
            )
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(4000)  # Let JS render
            
            title = await page.title()
            body_text = await page.evaluate('''() => document.body.innerText''')
            
            parsed = parse_page(title, body_text, exchange, ticker=ticker)
            result.update(parsed)
            
            if parsed["price"] is not None:
                result["status"] = "ok"
            else:
                result["status"] = "unavailable"
                
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    finally:
        if context:
            try:
                await context.close()
            except:
                pass
    
    return result


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} TICKER EXCHANGE", file=sys.stderr)
        print(f"  Example: {sys.argv[0]} AAPL NASDAQ", file=sys.stderr)
        print(f"  Example: {sys.argv[0]} 2330 TPE", file=sys.stderr)
        sys.exit(1)
    
    ticker = sys.argv[1]
    exchange = sys.argv[2]
    
    result = asyncio.run(fetch_quote(ticker, exchange))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # Exit code reflects status
    if result["status"] == "ok":
        sys.exit(0)
    elif result["status"] == "unavailable":
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()