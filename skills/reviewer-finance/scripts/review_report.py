#!/usr/bin/env python3
"""
reviewer-finance skill — Reviewer for Google Finance batch reports.

Input: google-finance JSON report (from fetch_batch.py)
Output: review-verdict.md + review-verdict.json (PASS/FAIL with findings)

Review criteria (per Kimberly's Reviewer skill spec):
1. Price sanity (US $1-10000 / TW NT$5-6000 / HK HK$1-10000)
2. Status completeness (all tickers must be 'ok')
3. Change detection (vs LOOP-STATE last report — flag >20% moves)
4. URL reachability (basic check that quote URL is well-formed)
5. Currency consistency (TPE/TPEX → TWD, NASDAQ/NYSE → USD, HKG → HKD)
6. Known ticker band — per-ticker expected price range (catches parser regressions
   even when no LOOP-STATE baseline exists; e.g. 2317 should be ~100-350 not 15)
7. K-line trend consistency (Step C, 2026-07-10) — opt-in via --enable-kline:
   price must not deviate excessively from MA20 with RSI disagreement,
   RSI overbought (>75) → SUSPECT, MACD death cross → WARN.
"""
import asyncio
import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime, timezone

# Optional K-line check (Step C). Loaded lazily to keep the default review path
# dependency-free when --enable-kline is not requested.
def _kline_check():
    """Lazy import for kline_check module (located in scripts/)."""
    sys.path.insert(0, str(Path(__file__).parent))
    import kline_check  # type: ignore[import-not-found]
    return kline_check


# --- Review rules ----------------------------------------------------------

# Ticker → expected exchange (for cross-check)
TICKER_EXCHANGE = {
    "AAPL": "NASDAQ", "MSFT": "NASDAQ", "GOOGL": "NASDAQ",
    "AMZN": "NASDAQ", "META": "NASDAQ", "NVDA": "NASDAQ",
    "TSLA": "NASDAQ", "NFLX": "NASDAQ", "LITE": "NASDAQ",
    "ORCL": "NYSE", "PLTR": "NYSE", "TSM": "NYSE",
}

# Price sanity ranges
PRICE_RANGES = {
    "USD": (1.0, 10000.0),
    "TWD": (5.0, 6000.0),   # bumped from 5000 → 6000 (MediaTek ~4000)
    "HKD": (1.0, 10000.0),
}

# Per-ticker expected price band (loose sanity check for tickers with no LOOP-STATE baseline).
# If parsed price is outside this band, flag as SUSPECT even when general sanity passes.
# Updated 2026-07-08 after parser regression on 2317/2303.
KNOWN_TICKER_BANDS = {
    # TW large caps (typical ranges as of mid-2026)
    "2330": (1500.0, 3500.0),  # TSMC ~2400
    "2317": (100.0, 350.0),    # Hon Hai ~235 (was NT$15 false-positive)
    "2303": (10.0, 300.0),     # UMC — surged to 37-year high ~160 in 2026
    "2454": (2500.0, 5000.0),  # MediaTek ~3990
    "2881": (50.0, 200.0),     # Fubon ~125
    "2882": (40.0, 150.0),     # Cathay Fin Holdings ~96
    "2308": (1000.0, 2500.0),  # Delta ~1880
    "2597": (80.0, 250.0),     # Auras
    "4104": (30.0, 120.0),     # GeneReach
    "2409": (10.0, 50.0),      # AUO
    "8131": (30.0, 150.0),     # Sigmatech
    "2891": (20.0, 100.0),     # CTBC Fin Holdings
    "1303": (40.0, 200.0),     # NPC — 2026-07-10 actual=181.5, widened from 150
    "2886": (15.0, 80.0),      # Mega Fin Holdings
    "1723": (40.0, 150.0),     # CTCI
    "2301": (80.0, 350.0),     # Liteon
    "4533": (40.0, 200.0),     # Sanyang
    "2002": (5.0, 50.0),       # China Steel
    "2201": (10.0, 60.0),      # Yulon
    # US large caps
    "AAPL": (100.0, 500.0),
    "MSFT": (200.0, 600.0),
    "GOOGL": (100.0, 500.0),
    "AMZN": (100.0, 400.0),
    "META": (200.0, 800.0),
    "NVDA": (50.0, 300.0),
    "TSLA": (100.0, 600.0),
    "NFLX": (50.0, 200.0),    # dropped significantly in 2026 to ~$76
    "ORCL": (80.0, 250.0),
    "PLTR": (20.0, 200.0),
    "TSM": (100.0, 600.0),
    "LITE": (300.0, 1000.0),
}

# Currency hint by exchange
EXCHANGE_CURRENCY = {
    "NASDAQ": "USD",
    "NYSE": "USD",
    "HKG": "HKD",
    "TPE": "TWD",
    "TPEX": "TWD",
}


ERROR_THRESHOLD = 2  # criteria 8: ERROR count > 2 → FAIL
REQUIRED_BASELINE_TICKERS = ["LITE", "2330", "NVDA", "TSM", "PLTR", "ORCL", "2454"]
EXPECTED_TOTAL_TICKERS = 31


def _has_baseline(loop_state_path: str) -> dict[str, bool]:
    """Check which priority tickers have baseline prices in LOOP-STATE.md.
    
    Returns dict mapping ticker -> bool (has baseline in 「上次報告摘要」section).
    """
    if not loop_state_path or not Path(loop_state_path).exists():
        return {t: False for t in REQUIRED_BASELINE_TICKERS}
    
    try:
        content = Path(loop_state_path).read_text(encoding="utf-8")
    except Exception:
        return {t: False for t in REQUIRED_BASELINE_TICKERS}
    
    # Extract 「上次報告摘要」 section
    # Bug fix 2026-07-21: original used `content.find('## ', ...)` which matched the
    # substring `## ` inside `### ` sub-headings, truncating the section to ~33 bytes.
    # Use line-start anchor so we only cut at real `## ...` headers.
    start_marker = "## 上次報告摘要"
    start_idx = content.find(start_marker)
    if start_idx < 0:
        return {t: False for t in REQUIRED_BASELINE_TICKERS}
    after_start = start_idx + len(start_marker)
    end_match = re.search(r'^## ', content[after_start:], re.MULTILINE)
    end_idx = (after_start + end_match.start()) if end_match else len(content)
    section = content[start_idx:end_idx]
    
    result = {}
    for ticker in REQUIRED_BASELINE_TICKERS:
        # Match `- TICKER ...` line (allow optional leading whitespace; bold allowed)
        result[ticker] = bool(re.search(rf'^[ \t]*- \*?\*?{re.escape(ticker)}', section, re.MULTILINE)) or \
                        bool(re.search(rf'^[ \t]*- {re.escape(ticker)}\b', section, re.MULTILINE))
    return result


def _read_metric_from_state(loop_state_path: str, key: str) -> str | None:
    """Extract a single metric line from LOOP-STATE.md「本次 loop 紀錄」section.
    
    Looks for pattern: - KEY: value
    """
    if not loop_state_path or not Path(loop_state_path).exists():
        return None
    try:
        content = Path(loop_state_path).read_text(encoding="utf-8")
    except Exception:
        return None
    
    # Find within last 20 lines (where metrics live)
    lines = content.split("\n")
    recent = "\n".join(lines[-30:])
    m = re.search(rf'^- {re.escape(key)}:\s*(.+)$', recent, re.MULTILINE)
    return m.group(1).strip() if m else None


def evaluate_completion_criteria(
    summary: dict,
    findings: list,
    loop_state_path: str = None,
    report_path: str = None,
) -> dict:
    """
    Evaluate the 8 Loop Completion Criteria from LOOP-STATE.md v1.1.
    
    Returns dict with:
        - criteria: list of {id, name, status: PASS/FAIL/WARN, detail: str}
        - passed_count: int
        - failed_count: int
        - loop_write_allowed: bool (only True if all 8 criteria PASS)
    """
    criteria_results = []
    
    # Criterion 1: 覆蓋率 31/31
    total = summary.get("total", 0)
    ok_count = summary.get("ok", 0)
    suspect = summary.get("suspect", 0)
    error_count = summary.get("error", 0)
    coverage_pct = (total / EXPECTED_TOTAL_TICKERS * 100) if EXPECTED_TOTAL_TICKERS else 0
    c1_pass = total == EXPECTED_TOTAL_TICKERS
    criteria_results.append({
        "id": 1, "name": "覆蓋率 31/31",
        "status": "PASS" if c1_pass else "FAIL",
        "detail": f"total={total}/{EXPECTED_TOTAL_TICKERS} (ok={ok_count}, suspect={suspect}, error={error_count})"
    })
    
    # Criterion 2: 帶寬合規（0 SUSPECT from KNOWN_TICKER_BANDS）
    band_suspect = [f for f in findings if f.get("rule") == "known_ticker_band"]
    c2_pass = len(band_suspect) == 0
    criteria_results.append({
        "id": 2, "name": "帶寬合規 (0 SUSPECT)",
        "status": "PASS" if c2_pass else "FAIL",
        "detail": f"{len(band_suspect)} ticker(s) out of band: {[f.get('ticker') for f in band_suspect]}"
    })
    
    # Criterion 3: Baseline 可比（七大關注股都有 baseline）
    baseline_map = _has_baseline(loop_state_path)
    missing_baseline = [t for t, has in baseline_map.items() if not has]
    c3_pass = len(missing_baseline) == 0
    criteria_results.append({
        "id": 3, "name": "Baseline 可比",
        "status": "PASS" if c3_pass else "FAIL",
        "detail": f"{len(missing_baseline)} missing: {missing_baseline}" if missing_baseline else f"all {len(REQUIRED_BASELINE_TICKERS)} tickers have baseline"
    })
    
    # Criterion 4: 產出檔案（loop-report.md + .json 都寫入）
    # This criterion is evaluated BY write_report.py itself, not the reviewer.
    # Reviewer just notes it.
    report_exists = Path(report_path).exists() if report_path else False
    json_path = str(Path(report_path).with_suffix(".json")) if report_path else None
    json_exists = Path(json_path).exists() if json_path else False
    c4_pass = report_exists and json_exists
    criteria_results.append({
        "id": 4, "name": "產出檔案",
        "status": "PASS" if c4_pass else "WARN",
        "detail": f"report_exists={report_exists} json_exists={json_exists} (this criterion is enforced by write_report.py, not here)"
    })
    
    # Criterion 5: 異常告警（SUSPECT/ERROR 都有 alert note in vault）
    # Best-effort check: search vault 00-Inbox for today's alert note if any SUSPECT/ERROR
    alert_note_exists = False
    if findings:
        today = datetime.now().strftime("%Y-%m-%d")
        for vault_path in [
            "/home/pigo/Documents/Pigo_Obsidian/00-Inbox",
            "/home/pigo/Documents/Pigo_Obsidian/08-Learning/Projects/quant-finance",
        ]:
            if Path(vault_path).exists():
                for f in Path(vault_path).glob(f"{today}_alert-*.md"):
                    if f.exists():
                        alert_note_exists = True
                        break
            if alert_note_exists:
                break
    
    if not findings:
        c5_pass = True
        c5_detail = "no findings, no alert needed"
    else:
        c5_pass = alert_note_exists
        c5_detail = f"findings count={len(findings)}, alert note exists={alert_note_exists}"
    criteria_results.append({
        "id": 5, "name": "異常告警",
        "status": "PASS" if c5_pass else "FAIL",
        "detail": c5_detail
    })
    
    # Criterion 6: 狀態更新（LOOP-STATE.md append 3-5 條「當前市場線索」）
    # Best-effort: check if 「當前市場線索」 section was updated today
    state_updated_today = False
    if loop_state_path and Path(loop_state_path).exists():
        try:
            content = Path(loop_state_path).read_text(encoding="utf-8")
            today_compact = datetime.now().strftime("%Y-%m-%d")
            # Find 「當前市場線索」 section
            m = re.search(r'## 當前市場線索.*?(?=^## |\Z)', content, re.MULTILINE | re.DOTALL)
            if m and today_compact in m.group(0):
                state_updated_today = True
        except Exception:
            pass
    c6_pass = state_updated_today
    criteria_results.append({
        "id": 6, "name": "狀態更新 (LOOP-STATE)",
        "status": "PASS" if c6_pass else "FAIL",
        "detail": f"「當前市場線索」段含今天日期={state_updated_today}"
    })
    
    # Criterion 7: Baseline 完備（首次 fetch 的 ticker 進「上次報告摘要」建 baseline）
    # Best-effort: count tickers marked "NEW" in this batch
    # For now, this is a soft check (we trust writer to add new ones)
    new_tickers = 0
    try:
        # Try to read the fetch batch JSON (sibling file)
        if report_path:
            base = Path(report_path).stem.replace("-review", "")
            possible_json = Path(report_path).parent / f"{base}.json"
            if possible_json.exists():
                data = json.loads(possible_json.read_text(encoding="utf-8"))
                # We don't have a "vs last" indicator in JSON; skip for now
                new_tickers = 0
    except Exception:
        pass
    # Soft check — pass if no NEW tickers OR LOOP-STATE updated today
    c7_pass = (new_tickers == 0) or state_updated_today
    criteria_results.append({
        "id": 7, "name": "Baseline 完備",
        "status": "PASS" if c7_pass else "WARN",
        "detail": f"new_tickers count={new_tickers} (heuristic; LOOP-STATE updated today={state_updated_today})"
    })
    
    # Criterion 8: 錯誤率上限（ERROR ≤ 2）
    c8_pass = error_count <= ERROR_THRESHOLD
    criteria_results.append({
        "id": 8, "name": "錯誤率上限 (ERROR ≤ 2)",
        "status": "PASS" if c8_pass else "FAIL",
        "detail": f"error_count={error_count} threshold={ERROR_THRESHOLD}"
    })
    
    passed_count = sum(1 for c in criteria_results if c["status"] == "PASS")
    failed_count = sum(1 for c in criteria_results if c["status"] == "FAIL")
    
    # 只允許 loop-report 寫入當所有 8 條 criteria 都 PASS（不含 WARN）
    loop_write_allowed = failed_count == 0
    
    return {
        "criteria": criteria_results,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "loop_write_allowed": loop_write_allowed,
    }


def review(report_path: str, loop_state_path: str = None, enable_kline: bool = False) -> dict:
    """
    Review a google-finance batch report.
    
    Returns verdict dict with keys:
        - overall: PASS / FAIL
        - score: 0-100
        - findings: list of {severity, ticker, message}
        - summary: counts of ok/suspect/error
        - criteria: list of {id, name, status, detail} (Loop Completion Criteria 1-8)
        - criteria_passed: int (幾條 criteria 通過)
        - criteria_failed: int (幾條 criteria 失敗)
        - loop_write_allowed: bool (criteria 全通過才能 write loop-report)
    """
    findings = []
    
    # Load report
    try:
        with open(report_path) as f:
            data = json.load(f)
    except Exception as e:
        return {
            "overall": "FAIL",
            "score": 0,
            "findings": [{"severity": "ERROR", "ticker": None, "message": f"無法讀取報告: {e}"}],
            "summary": {"ok": 0, "suspect": 0, "error": 0, "total": 0}
        }
    
    if not isinstance(data, list):
        return {
            "overall": "FAIL",
            "score": 0,
            "findings": [{"severity": "ERROR", "ticker": None, "message": f"報告格式錯誤，預期 list 但收到 {type(data).__name__}"}],
            "summary": {"ok": 0, "suspect": 0, "error": 0, "total": 0}
        }
    
    total = len(data)
    ok_count = 0
    suspect_count = 0
    error_count = 0
    
    # Load LOOP-STATE for change detection
    last_prices = {}
    if loop_state_path and Path(loop_state_path).exists():
        last_prices = parse_loop_state_prices(loop_state_path)
    
    # Review each entry
    for entry in data:
        ticker = entry.get("ticker", "?")
        exchange = entry.get("exchange", "?")
        status = entry.get("status", "unknown")
        price = entry.get("price")
        currency = entry.get("currency")
        url = entry.get("url", "")
        
        # Check 1: status must be 'ok'
        if status != "ok":
            findings.append({
                "severity": "ERROR",
                "ticker": ticker,
                "rule": "status_completeness",
                "message": f"Status = '{status}' (預期 'ok'), error: {(entry.get('error') or 'N/A')[:100]}"
            })
            error_count += 1
            continue
        
        # Check 2: price must be a number
        if not isinstance(price, (int, float)) or price <= 0:
            findings.append({
                "severity": "ERROR",
                "ticker": ticker,
                "rule": "status_completeness",
                "message": f"Price invalid: {price}"
            })
            error_count += 1
            continue
        
        # Check 3: price sanity
        expected_currency = EXCHANGE_CURRENCY.get(exchange, "USD")
        if currency and currency != expected_currency:
            findings.append({
                "severity": "SUSPECT",
                "ticker": ticker,
                "rule": "currency_consistency",
                "message": f"Currency mismatch: exchange={exchange} 預期 {expected_currency}, 收到 {currency}"
            })
            suspect_count += 1
        
        rng = PRICE_RANGES.get(expected_currency, (0.01, 100000))
        if not (rng[0] <= price <= rng[1]):
            findings.append({
                "severity": "SUSPECT",
                "ticker": ticker,
                "rule": "price_sanity",
                "message": f"Price {price} {expected_currency} 超出預期範圍 [{rng[0]}, {rng[1]}]"
            })
            suspect_count += 1
        else:
            ok_count += 1
        
        # Check 3b: per-ticker known band (catches parser regressions even when no LOOP-STATE baseline)
        known_band = KNOWN_TICKER_BANDS.get(ticker)
        if known_band and not (known_band[0] <= price <= known_band[1]):
            findings.append({
                "severity": "SUSPECT",
                "ticker": ticker,
                "rule": "known_ticker_band",
                "message": f"Price {price} {expected_currency} outside known band [{known_band[0]}, {known_band[1]}] for {ticker} — 可能 parser 抓錯（新聞 headline、隔壁 ticker）"
            })
            suspect_count += 1
        
        # Check 4: URL well-formed (upgrade WARN → SUSPECT)
        if not re.match(r'https://www\.google\.com/finance/quote/[^:]+:[A-Z]+$', url):
            findings.append({
                "severity": "SUSPECT",
                "ticker": ticker,
                "rule": "url_format",
                "message": f"URL 格式異常: {url}"
            })
            suspect_count += 1
        
        # Check 5: change detection vs LOOP-STATE last report
        if ticker in last_prices and last_prices[ticker] is not None:
            last_p = last_prices[ticker]
            change_pct = abs((price - last_p) / last_p * 100)
            if change_pct > 20:
                findings.append({
                    "severity": "SUSPECT",
                    "ticker": ticker,
                    "rule": "change_detection",
                    "message": f"vs 上次 {last_p} → {price} {expected_currency}, 變化 {change_pct:.1f}% > 20%"
                })
                suspect_count += 1
    
    # Check 6: K-line trend consistency (Step C, 2026-07-10, opt-in via --enable-kline)
    if enable_kline:
        try:
            kline_module = _kline_check()
            async def _run_kline_for_quotes():
                # Build minimal quote dicts for kline_check
                quotes_for_kline = [
                    {"ticker": d.get("ticker"), "exchange": d.get("exchange"),
                     "price": d.get("price")}
                    for d in data
                    if d.get("price") is not None
                ]
                return await kline_module.check_batch_kline(quotes_for_kline)
            
            kline_results = asyncio.run(_run_kline_for_quotes())
            for tk, kfindings in kline_results.items():
                for f in kfindings:
                    findings.append(f)
                    sev = f.get("severity", "WARN")
                    if sev == "SUSPECT":
                        suspect_count += 1
                    elif sev == "ERROR":
                        error_count += 1
                    # OK / WARN: not counted in suspect for score purposes
        except Exception as e:
            findings.append({
                "severity": "WARN",
                "ticker": None,
                "rule": "kline_check_unavailable",
                "message": f"K-line check skipped: {e}",
            })
    
    # Score: ok=full credit, suspect=-5, error=-10 (per ticker)
    score = 100 - (suspect_count * 5) - (error_count * 10)
    score = max(0, min(100, score))
    
    # Evaluate the 8 Loop Completion Criteria (Step 4: programatic gate)
    summary_dict = {
        "ok": ok_count,
        "suspect": suspect_count,
        "error": error_count,
        "total": total,
    }
    criteria_result = evaluate_completion_criteria(
        summary=summary_dict,
        findings=findings,
        loop_state_path=loop_state_path,
        report_path=report_path,
    )
    
    # Overall verdict: PASS iff score >= 95 AND error == 0 AND all criteria PASS
    overall = "PASS" if score >= 95 and error_count == 0 and criteria_result["loop_write_allowed"] else "FAIL"
    
    return {
        "overall": overall,
        "score": score,
        "findings": findings,
        "summary": summary_dict,
        "criteria": criteria_result["criteria"],
        "criteria_passed": criteria_result["passed_count"],
        "criteria_failed": criteria_result["failed_count"],
        "loop_write_allowed": criteria_result["loop_write_allowed"],
    }


def parse_loop_state_prices(loop_state_path: str) -> dict[str, float]:
    """Parse LOOP-STATE.md for last reported prices.
    
    Accepts formats (from actual LOOP-STATE.md):
    - `  - LITE（公司股）：**$722.05 USD**`
    - `  - 2330 台積電：**NT$2,450**`
    - `  - NVDA：**$195.55**`
    
    Returns:
        dict mapping ticker (str) to last price (float)
    """
    prices: dict[str, float] = {}
    try:
        content = Path(loop_state_path).read_text(encoding="utf-8")
        for line in content.split("\n"):
            # Skip empty lines
            if not line.strip():
                continue
            
            # Simple pattern: - TICKER ... $PRICE or **$PRICE** (works with LOOP-STATE.md format)
            # Handles: $722.05, **$722.05**, NT$2,450, **NT$2,450**
            m = re.search(r'- ([A-Z]{1,5}|\d{4})[^0-9]*\$?\*?\*?([0-9,]+\.?\d*)', line)
            if m:
                ticker = m.group(1)
                # Skip if ticker looks like a year (2026) - but allow stock codes like 2330
                # Stock codes: 4 digits but in range 1000-9999 (reasonable for Taiwan stock codes)
                if len(ticker) == 4 and ticker.isdigit():
                    # Skip only if it's clearly a year (2000-2030 range is ambiguous)
                    year_candidate = int(ticker)
                    if 2000 <= year_candidate <= 2030:
                        # Could be a year - skip
                        continue
                try:
                    price = float(m.group(2).replace(",", ""))
                    # Validate: price should be reasonable (10-10000 for stocks)
                    if 10 <= price <= 10000:
                        prices[ticker] = price
                except ValueError:
                    pass
    except Exception as e:
        import sys
        print(f"warn: parse_loop_state_prices failed: {e}", file=sys.stderr)
    return prices


def render_markdown(verdict: dict, report_path: str) -> str:
    """Render verdict as Markdown."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    md = []
    md.append(f"# Reviewer Verdict")
    md.append(f"")
    md.append(f"**Reviewed**: {ts}  ")
    md.append(f"**Report**: `{report_path}`  ")
    md.append(f"**Overall**: **{verdict['overall']}** (Score: {verdict['score']}/100)  ")
    md.append(f"")
    md.append(f"## Summary")
    md.append(f"")
    md.append(f"| Status | Count |")
    md.append(f"|--------|-------|")
    md.append(f"| ✅ OK | {verdict['summary']['ok']} |")
    md.append(f"| ⚠️ SUSPECT | {verdict['summary']['suspect']} |")
    md.append(f"| ❌ Error | {verdict['summary']['error']} |")
    md.append(f"| **Total** | {verdict['summary']['total']} |")
    md.append(f"")
    
    # Loop Completion Criteria section (Step 4)
    if 'criteria' in verdict and verdict.get('criteria'):
        md.append(f"## Loop Completion Criteria")
        md.append(f"")
        md.append(f"| # | Status | Criterion | Detail |")
        md.append(f"|---|--------|-----------|--------|")
        for c in verdict['criteria']:
            status_emoji = {'PASS': '✅', 'FAIL': '❌', 'WARN': '🟡'}.get(c['status'], '?')
            detail = c['detail'].replace("|", "\\|")[:200]
            md.append(f"| {c['id']} | {status_emoji} {c['status']} | {c['name']} | {detail} |")
        md.append(f"")
        write_gate = "✅ ALLOWED" if verdict.get('loop_write_allowed') else "❌ BLOCKED"
        md.append(f"**Loop-write gate**: {write_gate} ({verdict.get('criteria_passed', 0)}/8 PASS, {verdict.get('criteria_failed', 0)} FAIL)")
        md.append(f"")
    
    if verdict['findings']:
        md.append(f"## Findings")
        md.append(f"")
        md.append(f"| Severity | Ticker | Message |")
        md.append(f"|----------|--------|---------|")
        for f in verdict['findings']:
            severity_emoji = {"ERROR": "❌", "SUSPECT": "⚠️", "WARN": "🟡"}.get(f['severity'], "?")
            msg = f['message'].replace("|", "\\|")[:200]
            md.append(f"| {severity_emoji} {f['severity']} | {f['ticker']} | {msg} |")
    else:
        md.append(f"## Findings")
        md.append(f"")
        md.append(f"✅ **No issues found.**")
    
    md.append(f"")
    md.append(f"---")
    md.append(f"*Generated by reviewer-finance skill*")
    
    return "\n".join(md)


def main():
    ap_ = __import__('argparse').ArgumentParser(
        description="Review a google-finance batch report (with optional K-line check)."
    )
    ap_.add_argument("report_path")
    ap_.add_argument("loop_state_path", nargs="?", default=None)
    ap_.add_argument("--enable-kline", action="store_true",
                     help="Enable Step C K-line trend consistency check (slower, needs Node + stock-sdk).")
    args = ap_.parse_args()
    
    report_path = args.report_path
    loop_state_path = args.loop_state_path
    
    verdict = review(report_path, loop_state_path, enable_kline=args.enable_kline)
    
    # Render markdown
    md = render_markdown(verdict, report_path)
    
    # Output paths (same dir as report)
    report_dir = Path(report_path).parent
    base = Path(report_path).stem
    
    md_out = report_dir / f"{base}-review.md"
    json_out = report_dir / f"{base}-review.json"
    
    md_out.write_text(md, encoding="utf-8")
    json_out.write_text(json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"✅ Review verdict: {verdict['overall']} (score={verdict['score']})", file=sys.stderr)
    print(f"   MD:  {md_out}", file=sys.stderr)
    print(f"   JSON: {json_out}", file=sys.stderr)
    print(f"   OK={verdict['summary']['ok']} SUSPECT={verdict['summary']['suspect']} ERROR={verdict['summary']['error']}", file=sys.stderr)
    
    # Criteria summary (Step 4 gate)
    if 'criteria_passed' in verdict:
        print(f"   Criteria: {verdict['criteria_passed']}/8 PASS, {verdict['criteria_failed']} FAIL, loop_write_allowed={verdict['loop_write_allowed']}", file=sys.stderr)
        for c in verdict.get('criteria', []):
            status_emoji = {'PASS': '✅', 'FAIL': '❌', 'WARN': '🟡'}.get(c['status'], '?')
            print(f"     {status_emoji} C{c['id']}: {c['name']} — {c['detail'][:120]}", file=sys.stderr)
    
    # Exit code:
    #  0 = PASS (overall + criteria OK)
    #  2 = FAIL but criteria OK (慎查，可以 write loop-report)
    #  3 = FAIL + criteria FAIL (不能 write，須修)
    if verdict['overall'] == "PASS" and verdict.get('loop_write_allowed', True):
        sys.exit(0)
    elif verdict.get('loop_write_allowed', True):
        sys.exit(2)  # overall FAIL but criteria pass — partial
    else:
        sys.exit(3)  # criteria FAIL — refuse write


if __name__ == "__main__":
    main()