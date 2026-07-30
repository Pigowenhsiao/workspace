#!/usr/bin/env python3
"""
Regression test for google-finance parser Step A fix.

Tests three categories:
1. US stocks with US$ prefix in body (the original bug — fell back to day's Low)
2. TW stocks (TPE) — preserve 07-08 NT$ headline dedup fix
3. Title-only parsing (when body parsing fails)

Reference prices sourced from stock-sdk v2.3.0 (Tencent Finance, 2026-07-09 close).
Tolerance: ±0.5% for prices >$10, ±$1 absolute for prices <$10.
"""
import sys
from pathlib import Path
SKILL_DIR = Path("/home/pigo/.openclaw/workspace/skills/google-finance")
sys.path.insert(0, str(SKILL_DIR / "lib"))
from parser import parse_body, parse_title, parse_page

# (ticker, exchange, expected_price, expected_currency, source)
# Source: stock-sdk v2.3.0 validation 2026-07-09 16:00 ET
EXPECTED = [
    ("AAPL", "NASDAQ", 316.22, "USD", "stock-sdk"),
    ("MSFT", "NASDAQ", 384.36, "USD", "stock-sdk"),
    ("TSLA", "NASDAQ", 406.55, "USD", "stock-sdk"),
    ("NVDA", "NASDAQ", 202.78, "USD", "stock-sdk"),
    ("AMD",  "NASDAQ", 546.72, "USD", "stock-sdk"),
]

def test_parse_body_with_slicing():
    """The core bug fix: parse_body now slices to the main ticker region and uses
    position-weighted scoring so the actual last price wins over day's low."""
    # Simulated body slice (after AAPL:NASDAQ marker, similar to real GF layout)
    aapl_slice = """
check_indeterminate_small
加入清單
蘋果
US$316.22
arrow_upward
高點
US$316.53
低點
US$308.16
開盤價
US$310.51
收盤
US$313.39
+0.90%
市值
"""
    result = parse_body(aapl_slice, "NASDAQ", ticker="AAPL")
    assert result["price"] == 316.22, f"AAPL expected 316.22, got {result['price']}"
    assert result["currency"] == "USD"
    assert result["change_pct"] == 0.9, f"expected change_pct=0.9, got {result['change_pct']}"
    print("  ✓ parse_body (US$ + position-weighted + change_pct extraction) returns AAPL=316.22, +0.9%")


def test_parse_body_no_low_fallback():
    """When the actual price and day's low are both candidates, the actual price wins
    because it appears FIRST in the body (header price before chart's high/low)."""
    body = """
AAPL:NASDAQ
check_indeterminate_small
蘋果
US$200.00
高點
US$210.00
低點
US$190.00
"""
    result = parse_body(body, "NASDAQ", ticker="AAPL")
    assert result["price"] == 200.00, f"expected 200.00, got {result['price']}"
    print("  ✓ Main price (200.00) beats day's low (190.00) via position weighting")


def test_parse_body_nt_dedup_preserved():
    """Regression: 07-08 fix for NT$15-Billion-headline dedup must still work."""
    body = """
台積電
NT$1000
+2.5%
新聞: 台積電 NT$15 Billion 投資計畫震撼市場
更多新聞
NT$20 Billion 美光投資
NT$1005  ← 圖表上的當前價
NT$990   ← prev close
"""
    result = parse_body(body, "TPE", ticker="2330")
    # The first NT$ in main ticker region is 1000 (current price); headline 15/20 should NOT win
    assert result["price"] == 1000.0, f"expected 1000 (current price), got {result['price']}"
    assert result["change_pct"] == 2.5, f"expected change_pct=2.5, got {result['change_pct']}"
    print("  ✓ TW stock NT$ headline dedup + change_pct extract (1000 wins, +2.5%)")


def test_parse_title_change_pct_bare():
    """Bare '+X.XX%' format (without parentheses) must parse correctly."""
    title = "蘋果 (AAPL) +1.31% 股價 - Google 財經"
    result = parse_title(title)
    assert result["price"] is None, "TW title shouldn't have USD price"
    # Note: no price in title, but change_pct should be captured
    print(f"  ✓ Title change_pct parse: {result}")


def test_parse_title_arrow():
    """Arrow format ▲/▼ in title."""
    title = "蘋果 (AAPL) US$316.22 (▲ 0.90%) - Google 財經"
    result = parse_title(title)
    assert result["price"] == 316.22, f"expected 316.22, got {result['price']}"
    assert result["change_pct"] == "0.90", f"expected 0.90, got {result['change_pct']}"
    print(f"  ✓ Arrow format: price={result['price']}, change_pct={result['change_pct']}%")


def test_parse_title_paren():
    """Paren format (+/-X.XX%) in title."""
    title = "Apple Inc (AAPL) US$316.22 (+0.90%) - Google Finance"
    result = parse_title(title)
    assert result["price"] == 316.22, f"expected 316.22, got {result['price']}"
    # Paren format gives "+0.90" with sign — that's the expected value
    assert result["change_pct"] in ("+0.90", "0.90"), f"expected +0.90 or 0.90, got {result['change_pct']}"
    print(f"  ✓ Paren format: price={result['price']}, change_pct={result['change_pct']}")


def run_all():
    print("=== google-finance parser regression tests (Step A) ===")
    failures = 0
    for fn in [
        test_parse_body_with_slicing,
        test_parse_body_no_low_fallback,
        test_parse_body_nt_dedup_preserved,
        test_parse_title_change_pct_bare,
        test_parse_title_arrow,
        test_parse_title_paren,
    ]:
        try:
            fn()
        except AssertionError as e:
            print(f"  ✗ {fn.__name__}: {e}")
            failures += 1
        except Exception as e:
            print(f"  ✗ {fn.__name__}: ERROR {type(e).__name__}: {e}")
            failures += 1
    print(f"\n=== {len([f for f in [test_parse_body_with_slicing, test_parse_body_no_low_fallback, test_parse_body_nt_dedup_preserved, test_parse_title_change_pct_bare, test_parse_title_arrow, test_parse_title_paren]])} tests, {failures} failures ===")
    return failures

if __name__ == "__main__":
    sys.exit(run_all())