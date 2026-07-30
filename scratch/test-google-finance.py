#!/usr/bin/env python3
"""
Test playwright with Hsiaopigo profile -> Google Finance (HEADLESS)
Better wait + extraction for SPA content
"""
import asyncio
import os
import re
import json

PROFILE_PATH = "/home/pigo/.config/google-chrome/Profile 1"

async def main():
    from playwright.async_api import async_playwright
    
    print(f"PROFILE_PATH: {PROFILE_PATH}")
    print(f"PROFILE exists: {os.path.exists(PROFILE_PATH)}")
    print()
    
    async with async_playwright() as p:
        # Launch Chrome with persistent context (profile) in headless mode
        context = await p.chromium.launch_persistent_context(
            PROFILE_PATH,
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
                "--window-size=1920,1080",
                "--start-maximized",
                "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ],
            locale="zh-TW",
            timezone_id="Asia/Taipei",
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
        )
        
        page = await context.new_page()
        
        # Test function to extract stock data
        async def get_stock_price(ticker, exchange="NASDAQ"):
            """Navigate to stock page and extract price"""
            
            # Build URL based on exchange
            if exchange == "TPEX" or exchange == "TW":
                url = f"https://www.google.com/finance/quote/{ticker}:TPEX"
            elif exchange == "TPE":
                url = f"https://www.google.com/finance/quote/{ticker}:TPE"
            else:
                url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"
            
            print(f"\n=== Loading {ticker} ({exchange}) ===")
            print(f"URL: {url}")
            
            try:
                # Wait for network idle (JS must finish loading)
                await page.goto(url, wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(5000)  # Extra wait for JS rendering
                
                # Method 1: Look for price in JSON data embedded in page
                content = await page.content()
                
                # Find AF_initData or similar JSON
                json_patterns = [
                    r'AF_initDataCallback\(\[(\{.*?})\]',
                    r'window\["AF_initDataKeys"\] = (\[.*?\])',
                    r'"ds:(\d+)":\s*\{.*?"data":\s*(\[.*?\]|\{.*?\})',
                ]
                
                for pattern in json_patterns:
                    matches = re.findall(pattern, content, re.DOTALL)
                    if matches:
                        print(f"Found JSON data with pattern: {pattern[:50]}...")
                        # Try to parse
                        for m in matches[:3]:
                            if '"price"' in m.lower() or '"last"' in m.lower():
                                print(f"  -> Contains price data: {m[:200]}...")
                
                # Method 2: Look for price in DOM - try various selectors
                selectors = [
                    '.zz4ke',  # Common price class
                    '.YM1jed', 
                    '[class*="price"]',
                    '[data-price]',
                    '.N12wcc',
                    '.xqMXec',
                    '.f61wIb',
                    'span[class*="price"]',
                    'div[class*="price"]',
                ]
                
                for sel in selectors:
                    try:
                        elem = await page.query_selector(sel)
                        if elem:
                            txt = await elem.inner_text()
                            if txt and re.search(r'[0-9]', txt):
                                print(f"  Found with selector '{sel}': {txt[:100]}")
                    except:
                        pass
                
                # Method 3: Regex search in full content for price patterns
                # Look for typical Google Finance price patterns
                price_patterns = [
                    r'(\$|NTD|TWD|USD)\s*([0-9,]+\.?\d*)',
                    r'([0-9,]+\.?\d*)\s*(?:USD|NTD|TWD)',
                    r'"price"\s*:\s*"?([0-9,]+\.?\d*)"?',
                    r'"last"\s*:\s*"?([0-9,]+\.?\d*)"?',
                    r'data-price="([0-9,]+\.?\d*)"',
                ]
                
                for pattern in price_patterns:
                    matches = re.findall(pattern, content[:50000])
                    if matches:
                        print(f"  Pattern '{pattern[:40]}': {matches[:3]}")
                        break
                
                # Method 4: Evaluate JavaScript to get price
                try:
                    price = await page.evaluate('''
                        () => {
                            // Try to find price from various sources
                            // 1. From data attributes
                            const priceAttr = document.querySelector('[data-price]');
                            if (priceAttr) return 'data-price: ' + priceAttr.getAttribute('data-price');
                            
                            // 2. From price container classes
                            const priceContainers = document.querySelectorAll('.zz4ke, .YM1jed, .N12wcc, .xqMXec');
                            for (const c of priceContainers) {
                                const text = c.innerText;
                                if (text && /\\$|NTD|USD/.test(text) && /[0-9]/.test(text)) {
                                    return 'container: ' + text;
                                }
                            }
                            
                            // 3. From window data
                            if (window.AF_initDataChunkQueue) {
                                return 'AF_initDataChunkQueue exists, length: ' + window.AF_initDataChunkQueue.length;
                            }
                            
                            return null;
                        }
                    ''')
                    if price:
                        print(f"  JS evaluation: {price}")
                except Exception as e:
                    print(f"  JS evaluation error: {e}")
                
                print(f"\n  Final URL: {page.url}")
                print(f"  Title: {await page.title()}")
                
            except Exception as e:
                print(f"Error loading {ticker}: {e}")
        
        # Test multiple stocks
        await get_stock_price("AAPL", "NASDAQ")
        await get_stock_price("2330", "TPEX")
        await get_stock_price("MSFT", "NASDAQ")
        
        # Save final HTML for inspection
        html = await page.content()
        with open("/tmp/google-finance-test.html", "w") as f:
            f.write(html)
        print(f"\n=== Final HTML saved: {len(html)} bytes ===")
        
        await context.close()
        print("\n=== Done ===")

if __name__ == "__main__":
    asyncio.run(main())
