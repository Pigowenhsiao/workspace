#!/usr/bin/env python3
"""
Google Finance price parser - extracts price from page title or body text.

Strategy:
1. Try page title first (works for US stocks: "AAPL US$312.66 (▲ 1.31%) 蘋果 | Google 金融")
   - Note: Google Finance TW stock titles currently do NOT embed the price
     (e.g. "鴻海精密工業股份有限公司 (2317) 股價與新聞 - Google 財經"), so
     title parsing always falls through to body for TW tickers.
2. Fall back to body text. Collect ALL matches (NT$ + bare $) into a candidate
   pool, then score each by:
     - In-range for market (TWD $5-6000 / USD $1-5000 / HKD $1-5000)  [+10, else -20]
     - Has decimal point (real quotes always show decimals)             [+5, else -3]
     - NT$ prefix (weak tiebreaker)                                    [+2]
   Pick the candidate with combined signal = (neighbors_in_5pct * 2) + (occurrences * 3).
   This avoids the old bug where a stray news headline like "NT$15 Billion,
   Then Stock Retreat" would be picked over the actual "$235.00" quote.
3. Return None with diagnostics if both fail.
"""
import re

# Regex patterns
RE_TITLE_USD = re.compile(r'US\$\s*([0-9,]+\.?\d*)')          # US$312.66
RE_TITLE_HKD = re.compile(r'HK\$\s*([0-9,]+\.?\d*)')          # HK$464.80
RE_TITLE_JPY = re.compile(r'¥\s*([0-9,]+\.?\d*)')             # ¥12345
RE_TITLE_CNY = re.compile(r'(?:¥|RMB|CN¥)\s*([0-9,]+\.?\d*)') # ¥7.25 (also RMB/CNY)
RE_TITLE_TWD = re.compile(r'NT\$\s*([0-9,]+\.?\d*)')          # NT$2460.00
RE_TITLE_DOLLAR = re.compile(r'\$\s*([0-9,]+\.?\d*)')         # Generic $123.45

# Body text - find all dollar amounts
# NOTE: RE_BODY_NT is ONLY used as a *secondary hint* (currency confirmation),
# never as a primary match — Google Finance body may contain news headlines
# like "NT$15 Billion, Then Stock Retreat" which would falsely match.
RE_BODY_DOLLAR = re.compile(r'\$\s*([0-9,]+\.?\d*)')
RE_BODY_US = re.compile(r'US\$\s*([0-9,]+\.?\d*)')     # US$316.22 (Google Finance US stock prefix)
RE_BODY_NT = re.compile(r'NT\$\s*([0-9,]+\.?\d*)')
RE_BODY_HK = re.compile(r'HK\$\s*([0-9,]+\.?\d*)')

# Sector/index codes that appear in Google Finance body but are NOT the target ticker.
# These are SIX* (US sector ETFs) and similar 4-letter block codes.
RE_SECTOR_BLOCK = re.compile(r'^[A-Z]{4}$')

# Body change% — e.g. "+0.90%" / "-1.31%" / "▲ 0.90%" next to the main ticker price.
# Used as fallback when title parsing didn't get change_pct (some GF locales omit it).
# Strategy: take the first ±X.XX% appearing AFTER the first US$ (or NT$/HK$) match,
# since the change% in the price header always immediately follows the price.
RE_BODY_CHANGE_PCT = re.compile(r'[+\-]\s*([0-9]+(?:\.[0-9]+)?)\s*%')

# Plausible stock price ranges per market (used to score candidates)
# TWD: most TW stocks are NT$10-500; high-priced (MediaTek ~4000, TSMC ~2400) push upper to 6000
# USD: US stocks typically $1-5000; BRK.A is around $600,000 but we rarely fetch it
# HKD: HK stocks typically HK$1-5000
RANGE_TWD = (5.0, 6000.0)
RANGE_USD = (1.0, 5000.0)
RANGE_HKD = (1.0, 5000.0)


def _score_candidate(value: float, currency_hint: str, has_decimal: bool, nt_prefix: bool) -> int:
    """Score a candidate price for plausibility as a stock quote.
    
    Higher score = more likely to be the real quote.
    Heuristics:
      - Prices inside the per-market plausible range beat prices outside (heavy weight)
      - Decimal prices (e.g. 235.00) are quotes; integer-only (e.g. 15) often news headlines
      - NT$ prefixed matches get a weak tiebreaker boost (DO NOT rely on this alone)
    """
    score = 0
    rng = {"TWD": RANGE_TWD, "USD": RANGE_USD, "HKD": RANGE_HKD}.get(currency_hint, RANGE_USD)
    if rng[0] <= value <= rng[1]:
        score += 10
    else:
        score -= 20  # heavy penalty for out-of-range
    if has_decimal:
        score += 5
    else:
        score -= 3  # integer-only often comes from "NT$15 Billion" headlines
    if nt_prefix:
        score += 2  # weak tiebreaker — DO NOT rely on this alone
    return score


def _pick_best_price(candidates: list[tuple[float, bool, bool, int]], currency_hint: str) -> float | None:
    """Pick the best candidate price from a list of (value, has_decimal, nt_prefix, first_pos) tuples.
    
    Selection strategy:
      1. Filter to candidates with positive base score (in-range + has_decimal preferred)
      2. Compute three signals per candidate:
         - neighbor_count: how many other candidates are within ±5% (chart range cluster)
         - occ_count: how many times this exact value appears (current + prev close + chart)
         - first_pos: position of FIRST occurrence in body (lower = earlier = more likely the
           current price, since the main ticker header price appears before high/low/prev close
           further down the page). Earlier position gets a heavy boost.
      3. Combined score: neighbors * 2 + occ * 3 + (max_pos - first_pos) * 0.01
         (positional boost is a tiebreaker, not dominant, so we don't break the neighbor cluster
         signal)
      4. Final tiebreak: earlier first_pos wins; then lower value.
    
    Returns None if no candidate has a positive score.
    """
    if not candidates:
        return None
    
    scored = [(v, _score_candidate(v, currency_hint, d, n), d, n, p) for v, d, n, p in candidates]
    positive = [(v, s, d, n, p) for v, s, d, n, p in scored if s > 0]
    if not positive:
        return None
    
    vals = [v for v, _, _, _, _ in positive]
    
    def neighbor_count(target_v: float, tol_pct: float = 0.05) -> int:
        if target_v == 0:
            return 0
        return sum(1 for v in vals if v != target_v and abs(v - target_v) / target_v <= tol_pct)
    
    def occ_count(target_v: float) -> int:
        return sum(1 for v in vals if abs(v - target_v) < 0.01)
    
    max_pos = max(p for _, _, _, _, p in positive) or 1
    
    # Combined signal: weighted sum
    # Sort: (combined desc, score desc, first_pos asc, value asc)
    positive.sort(key=lambda x: (
        -(neighbor_count(x[0]) * 2 + occ_count(x[0]) * 3 + (max_pos - x[4]) * 0.01),
        -x[1],
        x[4],
        x[0],
    ))
    return positive[0][0]


def parse_title(title: str) -> dict:
    """
    Parse Google Finance page title.
    
    Returns dict with keys:
        price: float or None
        currency: str or None
        change_pct: str or None (e.g., "+1.31%")
    """
    if not title or title.strip() == "Google Finance":
        return {"price": None, "currency": None, "change_pct": None, "source": "title"}
    
    # Try each currency pattern
    patterns = [
        (RE_TITLE_USD, "USD"),
        (RE_TITLE_HKD, "HKD"),
        (RE_TITLE_TWD, "TWD"),
        (RE_TITLE_JPY, "JPY"),
        (RE_TITLE_CNY, "CNY"),
    ]
    
    price = None
    currency = None
    for pattern, curr in patterns:
        match = pattern.search(title)
        if match:
            price = float(match.group(1).replace(',', ''))
            currency = curr
            break
    
    # Generic $ - might be USD or TWD (Google Finance uses $ for NT dollars too)
    if price is None:
        match = RE_TITLE_DOLLAR.search(title)
        if match:
            price = float(match.group(1).replace(',', ''))
            currency = "USD"  # default assumption; caller can override
    
    # Extract change percentage: (▲ 1.31%) or (+1.31%) or (-0.96%)
    # Also handle bare "+1.31%" / "-0.96%" without parentheses (some GF locales omit them)
    change_match = re.search(r'[▲▼]\s*([0-9.]+)%|\(([+\-][0-9.]+)%\)|\B([+\-][0-9.]+)%', title)
    change_pct = None
    if change_match:
        # Pick the first non-None group (priority: arrow > paren > bare)
        change_pct = next((g for g in change_match.groups() if g), None)
    
    return {
        "price": price,
        "currency": currency,
        "change_pct": change_pct,
        "source": "title"
    }


def parse_body(body_text: str, exchange: str = None, ticker: str = None) -> dict:
    """
    Parse Google Finance body text.
    
    Google Finance body contains:
    - Hot stocks list at top (IGNORE first price)
    - Target stock price further down
    
    Args:
        body_text: full body.innerText from page
        exchange: TPE/TPEX/NASDAQ/HKG etc to disambiguate $ sign
        ticker: target ticker code (e.g. "AAPL") to locate the main price block.
                If provided, we slice the body to the region immediately following
                the first occurrence of "<TICKER>:<EXCHANGE>" to avoid sector
                lists (SIXB/SIXC/...) and unrelated news prices polluting the pool.
    
    Returns:
        dict with keys: price, currency, change_pct, source
    """
    if not body_text:
        return {"price": None, "currency": None, "change_pct": None, "source": "body"}
    
    # For Taiwan stocks (TPE/TPEX), $ means NT$ 
    if exchange in ("TPE", "TPEX"):
        currency_hint = "TWD"
    elif exchange == "HKG":
        currency_hint = "HKD"
    else:
        currency_hint = "USD"
    
    # Step 1: Locate the main price block — slice body to the region right
    # after "<TICKER>:<EXCHANGE>" first appears. This excludes the hot-stocks
    # list at the top and unrelated news headlines further down.
    search_text = body_text
    if ticker and exchange:
        marker = f"{ticker}:{exchange}"
        idx = body_text.find(marker)
        if idx >= 0:
            # Take ~2000 chars after the marker to cover header price + chart + high/low
            search_text = body_text[idx:idx + 2000]
    
    # Collect ALL candidate matches across all currency patterns.
    # We merge NT$ + US$ + bare $ (and HK$ for HKG) into a single candidate pool,
    # then score each to pick the most plausible stock quote.
    # This avoids the old bug where a stray news headline like "NT$15 Billion"
    # would be picked over the actual "$316.22" quote.
    raw_nt = RE_BODY_NT.findall(search_text) if currency_hint == "TWD" else []
    raw_hk = RE_BODY_HK.findall(search_text) if currency_hint == "HKD" else []
    raw_us = RE_BODY_US.findall(search_text) if currency_hint == "USD" else []
    raw_dollar = RE_BODY_DOLLAR.findall(search_text)
    
    # Build candidate list: (value, has_decimal, nt_prefix, first_pos_in_search_text)
    # We use finditer to capture the position of the FIRST occurrence of each unique value.
    candidates: list[tuple[float, bool, bool, int]] = []
    seen: set[float] = set()
    
    def _add_candidates(matches_iter, nt_prefix: bool):
        for m in matches_iter:
            try:
                v = float(m.group(1).replace(',', ''))
                if 0.01 < v < 100000 and v not in seen:
                    seen.add(v)
                    candidates.append((v, '.' in m.group(1), nt_prefix, m.start()))
            except (ValueError, IndexError):
                pass
    
    if currency_hint == "TWD":
        _add_candidates(RE_BODY_NT.finditer(search_text), True)
    if currency_hint == "HKD":
        _add_candidates(RE_BODY_HK.finditer(search_text), True)
    if currency_hint == "USD":
        _add_candidates(RE_BODY_US.finditer(search_text), True)  # US$ gets tiebreaker boost
    _add_candidates(RE_BODY_DOLLAR.finditer(search_text), False)
    
    if not candidates:
        return {"price": None, "currency": currency_hint, "change_pct": None, "source": "body"}
    
    # Pick best candidate by scoring (with positional tiebreaker)
    price = _pick_best_price(candidates, currency_hint)
    if price is None:
        return {"price": None, "currency": currency_hint, "change_pct": None, "source": "body"}
    
    # Try to extract change% from body (e.g. "+0.90%" appearing near the main price).
    # Take the first ±X.XX% match in the sliced region. We intentionally grab the
    # EARLIEST occurrence because it correlates with the main ticker header,
    # while later ±X.XX% values belong to news/sector listings further down.
    change_pct = None
    first_change = RE_BODY_CHANGE_PCT.search(search_text)
    if first_change:
        try:
            change_pct = float(first_change.group(1))
            # Preserve sign from the match string
            sign = -1.0 if '-' in first_change.group(0) else 1.0
            change_pct = sign * change_pct
        except (ValueError, IndexError):
            change_pct = None
    
    return {
        "price": price,
        "currency": currency_hint,
        "change_pct": change_pct,
        "source": "body"
    }


def parse_page(title: str, body_text: str, exchange: str = None, ticker: str = None) -> dict:
    """
    Combined parse: try title first, fall back to body.
    
    Returns dict with all fields.
    
    Strategy:
      1. parse_title() — yields price + change_pct when GF embeds them in title.
         Common cases: "US$316.22 (+0.90%) ..." (US locale) or "US$316.22 (▲ 0.90%) ...".
      2. If title has no price (e.g. TW locale "蘋果 (AAPL) 股價與新聞 - Google 財經"),
         parse_body() extracts price from body. With Step A fix this also typically
         captures the body's change_pct.
      3. If parse_title() got price but no change_pct (e.g. "US$316.22 ..." without
         trailing % token), fall back to body's change_pct while keeping title's price
         (authoritative).
    """
    title_result = parse_title(title)
    body_result = None
    
    if title_result["price"] is None:
        # Fallback: body for price (title was price-less)
        return parse_body(body_text, exchange, ticker=ticker)
    
    # Title gave us a price — but maybe not change_pct.
    # If change_pct missing, try supplementing from body.
    if title_result["change_pct"] is None:
        body_result = parse_body(body_text, exchange, ticker=ticker)
        if body_result.get("change_pct") is not None:
            title_result["change_pct"] = body_result["change_pct"]
    
    return title_result