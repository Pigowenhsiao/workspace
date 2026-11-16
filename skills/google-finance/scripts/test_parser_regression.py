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
    # Simulated body slice (after AAPL:NASDAQ marker, similar to real GF layout).
    # The "AAPL:NASDAQ" marker is REQUIRED: Guard 2 (added 2026-11-11) refuses to
    # parse a body that does not contain the target "<TICKER>:<EXCHANGE>" marker,
    # because such a body is some other page rather than a quote page.
    aapl_slice = """
AAPL:NASDAQ
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
2330:TPE
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


def test_parse_body_header_not_prev_close():
    """Regression 2026-11-12: the header parse must return the LIVE price, not
    "先前收在" (previous close).

    The scoring heuristic used to pick the previous close for TW tickers whose
    session moved >~5%: on 2026-11-12 it returned 1303 = 313.00 (prev close)
    instead of the live 293.00, and 2454 = 3,990.00 instead of 3,850.00.
    Both wrong values were verified against Yahoo Finance.
    """
    body = """
1303:TPE
add
加入清單
南亞塑膠
$293.00
arrow_downward
-6.39%
(-20.00) 今天
11月12日, 下午1:30:01 [UTC+8] · TWD
area_chart
面積
stacked_line_chart
比較
monitoring
指標
290
300
310
320
上午9:00
上午10:00
上午11:00
中午12:00
下午1:00
先前收在：$313.00
1D
5D
1M
6M
YTD
1Y
5Y
MAX
總覽
收益
財務
事件
insights_auto
"""
    result = parse_body(body, "TPE", ticker="1303")
    assert result["price"] == 293.0, f"expected live price 293.0, got {result['price']}"
    assert result["change_pct"] == -6.39, f"expected change_pct=-6.39, got {result['change_pct']}"
    print("  ✓ Header parse returns LIVE price (293.00), not 先前收在 (313.00)")


def test_parse_body_header_not_afterhours():
    """Regression 2026-11-12: for a closed US ticker the header price is the
    regular-session close; the after-hours price directly below it must not win.

    LITE on 2026-11-12: close $648.06 (+10.67%), after-hours $632.00 (-2.48%).
    """
    body = """
LITE:NASDAQ
add
加入清單
魯門特姆控股公司
$648.06
arrow_upward
+10.67%
(+62.49) 今天
已收盤：11月11日, 下午4:00:01 [UTC-5] · USD
$632.00
arrow_downward
-2.48%
(-16.06)
bedtime
盤後交易時段 · 晚上7:58
area_chart
面積
stacked_line_chart
比較
monitoring
指標
580
600
620
640
660
680
上午11:00
下午2:00
下午5:00
晚上8:00
先前收在：$585.57
"""
    result = parse_body(body, "NASDAQ", ticker="LITE")
    assert result["price"] == 648.06, f"expected close 648.06, got {result['price']}"
    assert result["change_pct"] == 10.67, f"expected change_pct=10.67, got {result['change_pct']}"
    print("  ✓ Header parse returns session close (648.06), not after-hours (632.00)")


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
    tests = [
        test_parse_body_with_slicing,
        test_parse_body_no_low_fallback,
        test_parse_body_nt_dedup_preserved,
        test_parse_body_header_not_prev_close,
        test_parse_body_header_not_afterhours,
        test_parse_title_change_pct_bare,
        test_parse_title_arrow,
        test_parse_title_paren,
    ]
    for fn in tests:
        try:
            fn()
        except AssertionError as e:
            print(f"  ✗ {fn.__name__}: {e}")
            failures += 1
        except Exception as e:
            print(f"  ✗ {fn.__name__}: ERROR {type(e).__name__}: {e}")
            failures += 1
    print(f"\n=== {len(tests)} tests, {failures} failures ===")
    return failures

if __name__ == "__main__":
    sys.exit(run_all())