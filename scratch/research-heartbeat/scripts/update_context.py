#!/usr/bin/env python3
"""Generate today's market observations and prepend them to LOOP-STATE.md.

Why this exists (2026-11-13):
  Step 4 of run_loop.sh used to append a machine log line ("Loop run OK, fetch=...")
  to the BOTTOM of the 「當前市場線索」 section, while write_report.py reads the
  FIRST lines of that section. Two consequences:
    1. every report quoted the PREVIOUS day's context;
    2. criterion 6 (「當前市場線索」段含今天日期) could never pass on the first run
       of a day, because the only thing written there was a log line with no date.

  This module synthesises real observations from the fetch JSON and prepends them
  so the report always quotes the current session.

Usage:
    update_context.py <fetch_json> <state_md> <timestamp>
"""
import json
import re
import sys
from pathlib import Path

MARKER = "## 當前市場線索"
US_MARKERS = ("NASDAQ", "NYSE", "HKG")
PRIORITY = ["LITE", "2330", "NVDA", "TSM", "AMD", "ORCL", "2454", "PLTR"]


def _pct(entry):
    c = entry.get("change_pct")
    return c if isinstance(c, (int, float)) else None


def _fmt(entry):
    price = entry["price"]
    currency = entry.get("currency") or "USD"
    prefix = "NT$" if currency == "TWD" else "$"
    chg = _pct(entry)
    chg_s = f"（{chg:+.2f}%）" if chg is not None else ""
    return f"{prefix}{price:,.2f}{chg_s}"


def build_observations(entries, timestamp):
    """Build the bullet list for today's market context."""
    ok = {e["ticker"]: e for e in entries
          if isinstance(e, dict) and e.get("status") == "ok"
          and isinstance(e.get("price"), (int, float))}

    observations = []

    # 1) LITE (自家公司) always gets its own bullet.
    lite = ok.get("LITE")
    if lite:
        chg = _pct(lite)
        if chg is None:
            direction = "持平"
        elif chg > 0:
            direction = "上漲"
        elif chg < 0:
            direction = "下跌"
        else:
            direction = "持平"
        extra = ""
        if chg is not None and abs(chg) >= 5:
            extra = "（單日大漲，警惕追高）" if chg > 0 else "（單日重挫，注意是否為個股事件）"
        observations.append(
            f"- **[{timestamp}]** **LITE {_fmt(lite)}** {direction}"
            + (f" {chg:+.2f}%" if chg is not None else "") + "（自家公司，重點追蹤）" + extra
        )

    # 2) US AI chain, strongest first.
    us = [ok[t] for t in PRIORITY
          if t in ok and t != "LITE" and ok[t].get("exchange") in US_MARKERS]
    if us:
        us.sort(key=lambda e: (_pct(e) if _pct(e) is not None else 0), reverse=True)
        txt = " / ".join(f"{e['ticker']} {_fmt(e)}" for e in us[:4])
        observations.append(f"- **[{timestamp}]** **美股 AI 鏈**：{txt}")

    # 3) TW AI chain.
    tw = [t for t in PRIORITY if t in ok and ok[t].get("exchange") == "TPE"]
    if tw:
        txt = " / ".join(f"{t} {_fmt(ok[t])}" for t in tw[:4])
        observations.append(f"- **[{timestamp}]** **台股 AI 鏈**：{txt}")

    # 4) Biggest single mover across the whole watchlist.
    movers = [e for e in ok.values() if _pct(e) is not None]
    if movers:
        top = max(movers, key=lambda e: abs(_pct(e)))
        extra = ""
        if _pct(top) >= 5:
            extra = "（單日大漲，警惕追高）"
        elif _pct(top) <= -5:
            extra = "（單日重挫，注意是否為個股事件）"
        observations.append(
            f"- **[{timestamp}]** **全池最大波動**：{top['ticker']} {_fmt(top)}{extra}"
        )

    # 5) Coverage / data-source gaps.
    unavailable = [e.get("ticker") for e in entries
                   if isinstance(e, dict) and e.get("status") != "ok"]
    if unavailable:
        observations.append(
            f"- **[{timestamp}]** **資料缺口**：{', '.join(str(t) for t in unavailable)} "
            "無報價頁（Google Finance 覆蓋缺口，非抓取失敗）"
        )

    # 6) Watchlist drift — priority tickers that did not make it into the fetch.
    missing = [t for t in PRIORITY if t not in ok]
    if missing:
        observations.append(
            f"- **[{timestamp}]** **關注股缺漏**：{', '.join(missing)} 未進本次報價，"
            "需檢查 watchlist／交易所代碼"
        )

    if not observations:
        observations.append(f"- **[{timestamp}]** 本次無有效報價，無法產生市場觀察")

    return observations


def prepend_to_state(state_path, observations):
    """Prepend the observation bullets right under the 「當前市場線索」 heading.

    The heading must be matched as a full line — the section title is
    「## 當前市場線索（Market Context）」, so inserting at the end of the bare
    marker string would split the heading in half.

    Two more details that matter:
      * the intro blockquote (「> 每日 loop 跑完會在這裡 append…」) must stay
        directly under the heading, so the bullets go AFTER it;
      * re-running the loop on the same day used to stack duplicate bullets for
        the same date. Bullets belonging to today are removed first.
    """
    path = Path(state_path)
    content = path.read_text(encoding="utf-8")

    match = re.search(rf"^{re.escape(MARKER)}.*$", content, re.MULTILINE)
    if not match:
        raise SystemExit(f"❌ 「{MARKER}」section not found in {state_path}")

    heading_end = match.end()

    # Find the end of the section (next level-2 heading).
    rest = content[heading_end:]
    m_next = re.search(r"^##\s", rest, re.MULTILINE)
    section_end = heading_end + (m_next.start() if m_next else len(rest))
    section = content[heading_end:section_end]

    # Split the section into: intro blockquote lines, bullets, and blanks.
    # The intro (「> 每日 loop 跑完會在這裡 append…」) can drift into the middle of
    # the section after earlier manual edits, so collect it wherever it sits.
    body = []
    intro_lines = []
    for ln in section.split("\n"):
        if ln.lstrip().startswith(">"):
            intro_lines.append(ln)
        else:
            body.append(ln)

    # Remove every bullet that already belongs to today (duplicate re-runs).
    # Key on the DATE only, not the full timestamp — a re-run at 07:36 must also
    # clear the 07:29 / 07:19 bullets written by earlier runs on the same day.
    stamp = observations[0].split("**")[1].strip("[]") if "**" in observations[0] else ""
    today_key = stamp.split(" UTC")[0].strip()[:10]
    body = [ln for ln in body
            if not (ln.lstrip().startswith("- ") and today_key and today_key in ln)]

    # Collapse runs of blank lines left behind by the removal.
    cleaned = []
    for ln in body:
        if not ln.strip() and cleaned and not cleaned[-1].strip():
            continue
        cleaned.append(ln)
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    while cleaned and not cleaned[-1].strip():
        cleaned.pop()

    intro = "\n".join(intro_lines)
    parts = []
    if intro:
        parts.append("\n" + intro + "\n")
    parts.append("\n" + "\n".join(observations) + "\n")
    if cleaned:
        parts.append("\n" + "\n".join(cleaned) + "\n")
    new_section = "".join(parts)

    content = content[:heading_end] + new_section + content[section_end:]
    path.write_text(content, encoding="utf-8")
    return len(observations)


def main():
    if len(sys.argv) < 4:
        raise SystemExit("Usage: update_context.py <fetch_json> <state_md> <timestamp>")
    fetch_json, state_path, timestamp = sys.argv[1], sys.argv[2], sys.argv[3]

    entries = json.loads(Path(fetch_json).read_text(encoding="utf-8"))
    observations = build_observations(entries, timestamp)
    n = prepend_to_state(state_path, observations)
    print(f"✅ Market context updated ({n} observations): {state_path}")


if __name__ == "__main__":
    main()
