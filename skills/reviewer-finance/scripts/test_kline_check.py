#!/usr/bin/env python3
"""
Unit tests for reviewer-finance/scripts/kline_check.py (Step C).

Tests evaluation logic without hitting the stock-sdk bridge (uses synthetic
bar data with MA/MACD/RSI pre-computed).
"""
import sys
from pathlib import Path

SKILL_DIR = Path("/home/pigo/.openclaw/workspace/skills/reviewer-finance")
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from kline_check import _evaluate_kline  # noqa: E402


def _make_kline(price, ma5, ma20, rsi14, macd_dif, macd_dea):
    """Helper: build minimal last_bar shape that _evaluate_kline consumes."""
    return {
        "ticker": "TEST",
        "bars": [
            {"date": "2026-07-09", "close": price,
             "ma": {"ma5": ma5, "ma20": ma20},
             "rsi": {"rsi14": rsi14},
             "macd": {"dif": macd_dif, "dea": macd_dea}}
        ],
        "last_bar": {
            "date": "2026-07-09", "close": price,
            "ma": {"ma5": ma5, "ma20": ma20},
            "rsi": {"rsi14": rsi14},
            "macd": {"dif": macd_dif, "dea": macd_dea},
        },
        "source": "tencent",
    }


def test_bullish_no_flags():
    """Healthy uptrend: MA5 > MA20, RSI moderate, price close to MA20 → 1 OK only."""
    kline = _make_kline(price=150.0, ma5=148.0, ma20=145.0, rsi14=60.0, macd_dif=2.0, macd_dea=1.0)
    findings = _evaluate_kline("TST", 150.0, kline)
    sev = [f["severity"] for f in findings]
    assert "SUSPECT" not in sev, f"Expected no SUSPECT, got {findings}"
    assert any(f["severity"] == "OK" and f["rule"] == "kline_ma_bullish" for f in findings), \
        "Should flag MA5 > MA20 bullish"
    print("  ✓ Healthy uptrend: 1 OK finding (MA bullish), no SUSPECT")


def test_rsi_overbought():
    """RSI > 75 → SUSPECT (overbought reversal risk)."""
    kline = _make_kline(price=180.0, ma5=170.0, ma20=160.0, rsi14=82.0, macd_dif=2.0, macd_dea=1.0)
    findings = _evaluate_kline("TST", 180.0, kline)
    assert any(f["severity"] == "SUSPECT" and f["rule"] == "kline_rsi_overbought" for f in findings), \
        f"Expected RSI overbought SUSPECT, got {findings}"
    print("  ✓ RSI=82 → SUSPECT (kline_rsi_overbought)")


def test_price_far_above_ma20_rsi_confirms():
    """Price 12%+ above MA20 with RSI > 65 confirms — no SUSPECT."""
    # price=200, ma20=160 → +25%, RSI=70 → confirms (i.e. likely real)
    kline = _make_kline(price=200.0, ma5=190.0, ma20=160.0, rsi14=70.0, macd_dif=2.0, macd_dea=1.0)
    findings = _evaluate_kline("TST", 200.0, kline)
    assert not any(f["severity"] == "SUSPECT" and f["rule"] == "kline_price_far_from_ma20" for f in findings), \
        f"RSI confirm should block price_far_from_ma20 SUSPECT, got {findings}"
    print("  ✓ Price 25% above MA20 + RSI=70 (confirms) → no SUSPECT")


def test_price_far_above_ma20_rsi_disagrees():
    """Price 12%+ above MA20 but RSI moderate → SUSPECT (possible parser error)."""
    kline = _make_kline(price=200.0, ma5=190.0, ma20=160.0, rsi14=55.0, macd_dif=2.0, macd_dea=1.0)
    findings = _evaluate_kline("TST", 200.0, kline)
    assert any(f["severity"] == "SUSPECT" and f["rule"] == "kline_price_far_from_ma20" for f in findings), \
        f"RSI disagree should trigger SUSPECT, got {findings}"
    print("  ✓ Price 25% above MA20 + RSI=55 (disagrees) → SUSPECT (parser suspect)")


def test_macd_death_cross():
    """DIF < DEA with gap > 0.5 → WARN."""
    kline = _make_kline(price=150.0, ma5=148.0, ma20=145.0, rsi14=45.0, macd_dif=-1.5, macd_dea=0.5)
    findings = _evaluate_kline("TST", 150.0, kline)
    assert any(f["severity"] == "WARN" and f["rule"] == "kline_macd_death_cross" for f in findings), \
        f"Expected MACD death cross WARN, got {findings}"
    print("  ✓ MACD DIF=-1.5 < DEA=0.5 (gap > 0.5) → WARN (death cross)")


def test_macd_slight_below():
    """DIF < DEA but tiny gap (< 0.5) → no WARN (noise)."""
    kline = _make_kline(price=150.0, ma5=148.0, ma20=145.0, rsi14=50.0, macd_dif=-0.1, macd_dea=0.0)
    findings = _evaluate_kline("TST", 150.0, kline)
    assert not any(f["severity"] == "WARN" and f["rule"] == "kline_macd_death_cross" for f in findings), \
        f"Tiny MACD gap should not warn, got {findings}"
    print("  ✓ MACD DIF=-0.1 < DEA=0.0 (tiny gap) → no WARN")


def test_missing_rsi():
    """Missing RSI → price_far_from_ma20 check cannot confirm, default to SUSPECT."""
    kline = _make_kline(price=200.0, ma5=190.0, ma20=160.0, rsi14=None, macd_dif=2.0, macd_dea=1.0)
    findings = _evaluate_kline("TST", 200.0, kline)
    # With rsi14=None, rsi_confirms=False → SUSPECT fires
    assert any(f["severity"] == "SUSPECT" and f["rule"] == "kline_price_far_from_ma20" for f in findings), \
        f"Missing RSI should trigger SUSPECT, got {findings}"
    print("  ✓ Missing RSI + price far from MA20 → SUSPECT (parser suspect)")


def test_no_ma20():
    """Missing MA20 → only RSI check applies."""
    kline = _make_kline(price=150.0, ma5=None, ma20=None, rsi14=82.0, macd_dif=2.0, macd_dea=1.0)
    findings = _evaluate_kline("TST", 150.0, kline)
    # RSI overbought still fires
    assert any(f["severity"] == "SUSPECT" and f["rule"] == "kline_rsi_overbought" for f in findings), \
        f"Missing MA20 should still allow RSI check, got {findings}"
    # MA bullish won't fire (ma5=ma20=None → no comparison)
    assert not any(f["rule"] == "kline_ma_bullish" for f in findings), "Should not flag MA bullish when MA missing"
    print("  ✓ Missing MA20 → RSI check still fires; no false MA bullish")


if __name__ == "__main__":
    print("=== reviewer-finance K-line check unit tests (Step C) ===")
    tests = [
        test_bullish_no_flags,
        test_rsi_overbought,
        test_price_far_above_ma20_rsi_confirms,
        test_price_far_above_ma20_rsi_disagrees,
        test_macd_death_cross,
        test_macd_slight_below,
        test_missing_rsi,
        test_no_ma20,
    ]
    failures = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"  ✗ {t.__name__}: {e}")
            failures += 1
        except Exception as e:
            print(f"  ✗ {t.__name__}: ERROR {type(e).__name__}: {e}")
            failures += 1
    print(f"\n=== {len(tests)} tests, {failures} failures ===")
    sys.exit(0 if failures == 0 else 1)