#!/usr/bin/env python3
"""
research-heartbeat / data_fetch.py

從 Yahoo Finance v8 chart API 抓 watchlist 報價，寫入 data/raw/。
- 純 urllib，零外部依賴
- 5 天日線 (range=5d)
- name check：抓回的公司英文名必須包含預期關鍵字，否則 raise SystemExit（合約錯誤，不靜默）
- 單檔 fetch 失敗：跳過 + 記 warning，整批仍繼續（部分資料比全無好）
- 輸出：data/raw/YYYY-MM-DD_HHMM.json
"""
import json
import sys
import time
import urllib.request
import urllib.parse
import argparse
from pathlib import Path
from datetime import datetime, timezone

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0"
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# Watchlist：ticker → 預期 name 關鍵字（name check 用，全部小寫比對）
WATCHLIST = {
    # ASX 指數
    "^AXJO": ["s&p/asx 200", "asx 200"],
    "^AORD": ["all ordinaries"],
    # ASX 權值 10 檔
    "BHP.AX": ["bhp"],
    "CBA.AX": ["commonwealth bank"],
    "CSL.AX": ["csl"],
    "NAB.AX": ["national australia bank"],
    "WBC.AX": ["westpac"],
    "ANZ.AX": ["anz"],
    "WES.AX": ["wesfarmers"],
    "WOW.AX": ["woolworths"],
    "WDS.AX": ["woodside"],
    "FMG.AX": ["fortescue"],
    # TW 4 檔
    "4169.TW": ["tcm biotech"],          # 泰宗
    "9939.TW": ["hon chuan"],            # 宏全
    "2330.TW": ["taiwan semiconductor"],  # 台積電
    "2303.TW": ["united microelectronics"],  # 聯電
}

# 板塊（先預留，未來用）
SECTORS = {
    "Energy": "^AXEJ",
    "Materials": "^AXMJ",
    "Industrials": "^AXNJ",
    "ConsumerDiscretionary": "^AXDJ",
    "ConsumerStaples": "^AXSJ",
    "HealthCare": "^AXHJ",
    "Financials": "^AXFJ",
    "RealEstate": "^AXPJ",
    "InfoTech": "^AXIJ",
    "CommServices": "^AXTJ",
    "Utilities": "^AXUJ",
}


def fetch_quote(ticker: str) -> dict | None:
    """抓一支 ticker 的 5 天日線 + meta，回傳 dict 或 None（網路/解析失敗）"""
    encoded = urllib.parse.quote(ticker, safe="")
    # Yahoo 有兩個 chart endpoint，遇到 429 可切換
    for endpoint in ("query1", "query2"):
        url = f"https://{endpoint}.finance.yahoo.com/v8/finance/chart/{encoded}?interval=1d&range=5d"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read())
        except Exception as e:
            print(f"[WARN] {ticker}: {endpoint} fetch failed: {e}", file=sys.stderr)
            continue

        if not data.get("chart") or not data["chart"].get("result"):
            err = data.get("chart", {}).get("error")
            print(f"[WARN] {ticker}: {endpoint} no result (error={err})", file=sys.stderr)
            continue

        return data

    print(f"[WARN] {ticker}: all endpoints failed", file=sys.stderr)
    return None


def parse_quote(ticker: str, raw: dict) -> dict:
    """從 Yahoo v8 response 抽出乾淨欄位 + 做 name check"""
    meta = raw["chart"]["result"][0]["meta"]
    last = meta.get("regularMarketPrice")
    prev = meta.get("chartPreviousClose")
    chg_pct = ((last - prev) / prev * 100) if (last and prev) else None

    # 5d 漲跌
    closes = raw["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    closes_clean = [c for c in closes if c is not None]
    if len(closes_clean) >= 2:
        chg_5d_pct = (closes_clean[-1] - closes_clean[0]) / closes_clean[0] * 100
    else:
        chg_5d_pct = None

    name = meta.get("longName") or meta.get("shortName") or ""
    name_lower = name.lower()
    mkt_time = meta.get("regularMarketTime")
    as_of_utc = (
        datetime.fromtimestamp(mkt_time, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        if mkt_time
        else None
    )

    return {
        "ticker": ticker,
        "name": name,
        "exchange": meta.get("fullExchangeName"),
        "currency": meta.get("currency"),
        "last": round(last, 4) if last else None,
        "prev_close": round(prev, 4) if prev else None,
        "chg_pct_1d": round(chg_pct, 2) if chg_pct is not None else None,
        "chg_pct_5d": round(chg_5d_pct, 2) if chg_5d_pct is not None else None,
        "volume": int(meta.get("regularMarketVolume") or 0),
        "52w_high": meta.get("fiftyTwoWeekHigh"),
        "52w_low": meta.get("fiftyTwoWeekLow"),
        "as_of_utc": as_of_utc,
    }


def name_check(ticker: str, parsed: dict) -> None:
    """name check：實際拿到的 name 必須包含預期關鍵字之一，否則 raise"""
    expected_keywords = WATCHLIST[ticker]
    name_lower = parsed["name"].lower()
    if not any(kw in name_lower for kw in expected_keywords):
        raise SystemExit(
            f"[FATAL] name check FAILED for {ticker}\n"
            f"  expected one of: {expected_keywords}\n"
            f"  got: {parsed['name']!r}\n"
            f"  → ticker 對應的公司可能已換或 Yahoo ID 漂移，請手動驗證後再跑"
        )


def main():
    ap = argparse.ArgumentParser(description="research-heartbeat data fetcher")
    ap.add_argument("--tickers", nargs="*", help="只抓指定 tickers（預設全 watchlist）")
    ap.add_argument("--out", help="指定輸出檔（預設 data/raw/YYYY-MM-DD_HHMM.json）")
    args = ap.parse_args()

    targets = args.tickers if args.tickers else list(WATCHLIST.keys())

    print(f"[INFO] fetching {len(targets)} tickers...", file=sys.stderr)
    quotes = []
    name_check_results = []  # 記錄哪幾檔 name check 通過
    for i, t in enumerate(targets):
        # rate-limit 防護：Yahoo 對短時間 burst 會回 429
        if i > 0:
            time.sleep(0.3)
        raw = fetch_quote(t)
        if raw is None:
            continue
        parsed = parse_quote(t, raw)
        name_check(t, parsed)  # raise if fail
        name_check_results.append((t, parsed["name"]))
        quotes.append(parsed)

    if not quotes:
        print("[FATAL] no quotes fetched", file=sys.stderr)
        sys.exit(1)

    # 輸出檔
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
    out_path = Path(args.out) if args.out else RAW_DIR / f"{ts}.json"

    payload = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "source": "Yahoo Finance v8 chart API (query1.finance.yahoo.com)",
        "range": "5d",
        "watchlist_size": len(WATCHLIST),
        "requested": len(targets),
        "fetched": len(quotes),
        "name_check": [
            {"ticker": t, "name": n, "passed": True} for t, n in name_check_results
        ],
        "quotes": quotes,
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"[OK] wrote {out_path} ({len(quotes)}/{len(targets)} quotes)", file=sys.stderr)
    print(f"[OK] name check passed: {len(name_check_results)}/{len(quotes)}", file=sys.stderr)


if __name__ == "__main__":
    main()
