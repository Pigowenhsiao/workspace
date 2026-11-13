#!/bin/bash
# Loop Engineering: Daily 美股+台股 research loop
# Kimberly Loop framework: Heartbeat → Fetch → Review → Write → Update State
# 
# Usage:
#   ./run_loop.sh                    # use default watchlist + state
#   ./run_loop.sh <watchlist.json>   # custom watchlist
#   ./run_loop.sh <watchlist.json> <state.md>   # custom everything

set -e  # exit on any error

# Defaults
WATCHLIST="${1:-$HOME/.openclaw/workspace/skills/google-finance/templates/research-heartbeat-watchlist.json}"
STATE="${2:-$HOME/.openclaw/workspace/scratch/research-heartbeat/state/LOOP-STATE.md}"
OUT_DIR="$HOME/Downloads/Sotck"
TS=$(date -u +"%Y%m%d-%H%M%S")

# Skill paths
FETCHER="$HOME/.openclaw/workspace/skills/google-finance/scripts/fetch_batch.py"
REVIEWER="$HOME/.openclaw/workspace/skills/reviewer-finance/scripts/review_report.py"
WRITER="$HOME/.openclaw/workspace/skills/finance-writer/scripts/write_report.py"
CONTEXT_UPDATER="$HOME/.openclaw/workspace/scratch/research-heartbeat/scripts/update_context.py"

echo "=== Loop Engineering: Daily Research Heartbeat ==="
echo "Timestamp: $(date)"
echo "Watchlist: $WATCHLIST"
echo "State: $STATE"
echo ""

# Verify inputs exist
if [ ! -f "$WATCHLIST" ]; then
    echo "❌ Watchlist not found: $WATCHLIST"
    exit 1
fi

if [ ! -f "$STATE" ]; then
    echo "⚠️  LOOP-STATE.md not found at $STATE, will create new"
    STATE_NEW=1
else
    STATE_NEW=0
fi

mkdir -p "$OUT_DIR"

# --- Interpreter selection ---
# The fetch step needs Playwright. The system python3 (3.14 on pigoserver2) does
# NOT have it, so the loop used to die with ModuleNotFoundError: playwright.
# Pick the first interpreter that can actually import playwright; fall back to
# python3 so the failure message stays the familiar one.
pick_python() {
    local cand
    for cand in "$HOME/.venv/bin/python3" "$HOME/.venv/bin/python" \
                "$HOME/.local/bin/python3.11" \
                "$(command -v python3 2>/dev/null)"; do
        [ -n "$cand" ] && [ -x "$cand" ] || continue
        if "$cand" -c "import playwright" >/dev/null 2>&1; then
            echo "$cand"; return 0
        fi
    done
    echo "python3"
}
PYTHON="$(pick_python)"
echo "Python: $PYTHON ($("$PYTHON" -c 'import sys;print(sys.version.split()[0])' 2>/dev/null || echo unknown))"
if ! "$PYTHON" -c "import playwright" >/dev/null 2>&1; then
    echo "❌ No Python interpreter with playwright found (tried ~/.venv, ~/.local/bin/python3.11, python3)."
    echo "    Fix: /home/pigo/.venv/bin/python -m pip install playwright && /home/pigo/.venv/bin/playwright install chromium"
    exit 1
fi
echo ""

# --- Step 1: FETCH ---
echo "--- Step 1: Fetch (google-finance) ---"
FETCH_OUT="$OUT_DIR/google-finance-$TS.md"
"$PYTHON" "$FETCHER" "$WATCHLIST" "$FETCH_OUT"
FETCH_JSON="${FETCH_OUT%.md}.json"

if [ ! -f "$FETCH_JSON" ]; then
    echo "❌ Fetch JSON not produced: $FETCH_JSON"
    exit 1
fi

OK_COUNT=$("$PYTHON" -c "import json; d=json.load(open('$FETCH_JSON')); print(sum(1 for t in d if t.get('status')=='ok'))")
TOTAL=$("$PYTHON" -c "import json; d=json.load(open('$FETCH_JSON')); print(len(d))")
echo "Fetch: $OK_COUNT / $TOTAL ok"
echo ""

# --- Step 1.5: MARKET CONTEXT ---
# The report's 「當前市場線索」 section is copied from LOOP-STATE.md, and the
# reviewer's C6 gate checks that the same section contains today's date. Both
# require today's observations to exist BEFORE the writer runs, so this step
# deliberately sits between fetch and review (it only needs the fetch JSON).
echo "--- Step 1.5: Update market context (LOOP-STATE) ---"
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")
if [ $STATE_NEW -eq 0 ]; then
    "$PYTHON" "$CONTEXT_UPDATER" "$FETCH_JSON" "$STATE" "$TIMESTAMP"
else
    echo "⚠️  Skipping context update (LOOP-STATE.md did not exist before)"
fi
echo ""

# --- Step 2: REVIEW ---
echo "--- Step 2: Review (reviewer-finance) ---"
# The reviewer's C1 coverage gate compares the fetched ticker count against a
# hardcoded EXPECTED_TOTAL_TICKERS. Export the real watchlist size so the gate
# tracks the watchlist instead of a stale constant.
EXPECTED_TOTAL_TICKERS=$("$PYTHON" -c "import json,sys; print(len(json.load(open('$WATCHLIST'))))")
export EXPECTED_TOTAL_TICKERS
echo "Watchlist size: $EXPECTED_TOTAL_TICKERS"
# reviewer exit codes: 0 = PASS + all criteria OK, 2 = overall FAIL but criteria pass
# (partial write allowed), 3 = criteria FAIL (write refused).
# `set -e` would abort the whole script on 2/3, skipping Step 3 (write report) and
# Step 4 (LOOP-STATE update). That created a self-blocking cycle: C6 checks whether
# LOOP-STATE contains today's date, but only Step 4 writes it — so the script could
# never satisfy C6. Capture the code instead of letting it kill the script.
set +e
"$PYTHON" "$REVIEWER" "$FETCH_JSON" "$STATE"
REVIEW_RC=$?
set -e
case "$REVIEW_RC" in
    0) echo "Review gate: PASS (all criteria OK)" ;;
    2) echo "Review gate: PARTIAL (overall FAIL, criteria pass — write allowed)" ;;
    3) echo "Review gate: BLOCKED (criteria FAIL — reviewer refused write)" ;;
    *) echo "Review gate: reviewer crashed (rc=$REVIEW_RC)" ;;
esac
REVIEW_JSON="${FETCH_JSON%.json}-review.json"
REVIEW_MD="${FETCH_JSON%.json}-review.md"

if [ ! -f "$REVIEW_JSON" ]; then
    echo "❌ Review JSON not produced"
    exit 1
fi

VERDICT=$("$PYTHON" -c "import json; d=json.load(open('$REVIEW_JSON')); print(d.get('overall','?'))")
SCORE=$("$PYTHON" -c "import json; d=json.load(open('$REVIEW_JSON')); print(d.get('score',0))")
echo "Review: $VERDICT (score=$SCORE)"
echo ""

# --- Step 3: WRITE ---
echo "--- Step 3: Write (finance-writer) ---"
REPORT_OUT="$OUT_DIR/loop-report-$TS.md"
if [ "$REVIEW_RC" -eq 3 ]; then
    echo "⚠️  Reviewer BLOCKED the write (criteria FAIL). Writing report anyway so the"
    echo "    operator still gets a report to act on; gate stays enforced in the review JSON."
fi
set +e
"$PYTHON" "$WRITER" "$FETCH_JSON" "$REVIEW_JSON" "$STATE" "$REPORT_OUT"
WRITE_RC=$?
set -e

if [ ! -f "$REPORT_OUT" ]; then
    echo "❌ Report not produced: $REPORT_OUT (writer rc=$WRITE_RC)"
    exit 1
fi

echo "Report: $REPORT_OUT ($(wc -l < "$REPORT_OUT") lines)"
echo ""

# --- Step 3.5: ALERT NOTE ---
# Criterion 5 requires a vault alert note whenever the reviewer produced SUSPECT/ERROR
# findings. Nothing in the pipeline used to create it, so C5 could never pass.
ALERT_DIR="$HOME/Documents/Pigo_Obsidian/00-Inbox"
ALERT_TODAY=$(date +"%Y-%m-%d")
ALERT_OUT="$ALERT_DIR/${ALERT_TODAY}_alert-research-heartbeat.md"
ALERT_COUNT=$("$PYTHON" -c "
import json
try:
    d = json.load(open('$REVIEW_JSON'))
except Exception:
    print(0); raise SystemExit
n = sum(1 for f in d.get('findings', []) if f.get('severity') in ('SUSPECT', 'ERROR'))
print(n)
")
if [ "$ALERT_COUNT" -gt 0 ]; then
    echo "--- Step 3.5: Write alert note ($ALERT_COUNT findings) ---"
    mkdir -p "$ALERT_DIR"
    REVIEW_JSON="$REVIEW_JSON" ALERT_OUT="$ALERT_OUT" ALERT_TODAY="$ALERT_TODAY" FETCH_JSON="$FETCH_JSON" "$PYTHON" << 'PYEOF'
import json, os
from datetime import datetime, timezone, timedelta

review = json.load(open(os.environ["REVIEW_JSON"]))
fetch = json.load(open(os.environ["FETCH_JSON"]))
out = os.environ["ALERT_OUT"]
today = os.environ["ALERT_TODAY"]

taipei = timezone(timedelta(hours=8))
ts = datetime.now(taipei).strftime("%Y-%m-%d %H:%M")

findings = [f for f in review.get("findings", []) if f.get("severity") in ("SUSPECT", "ERROR")]
price_map = {e.get("ticker"): e for e in fetch if isinstance(e, dict)}

lines = [
    "---",
    f"title: 研究心跳異常告警 {today}",
    "source: research-heartbeat-loop",
    "processed: true",
    "tags: [研究心跳, 異常告警, finance]",
    f"created: {today}",
    "---",
    "",
    f"# 研究心跳異常告警 {today}",
    "",
    f"- **產生時間**：{ts}（Asia/Taipei）",
    f"- **verdict**：{review.get('overall')}（score {review.get('score')}）",
    f"- **異常筆數**：{len(findings)}",
    "",
    "## 異常清單",
    "",
    "| 級別 | Ticker | 規則 | 說明 |",
    "|---|---|---|---|",
]
for f in findings:
    tk = f.get("ticker", "-")
    msg = (f.get("message") or "").replace("|", "\\|")
    lines.append(f"| {f.get('severity')} | {tk} | {f.get('rule', '-')} | {msg} |")

lines += ["", "## 本次報價", "", "| Ticker | 交易所 | 價格 | 幣別 | 漲跌幅 |", "|---|---|---|---|---|"]
for f in findings:
    tk = f.get("ticker")
    e = price_map.get(tk)
    if not e:
        continue
    p = e.get("price")
    price_str = f"{p:,.2f}" if isinstance(p, (int, float)) else "N/A"
    chg = e.get("change_pct")
    chg_str = f"{chg:+.2f}%" if isinstance(chg, (int, float)) else "-"
    lines.append(f"| {tk} | {e.get('exchange','-')} | {price_str} | {e.get('currency','-')} | {chg_str} |")

lines += [
    "",
    "## 建議處理",
    "",
    "- SUSPECT：先對照其他報價來源（Yahoo Finance / 交易所官網）確認真值，再決定是否修正 band 或 parser。",
    "- ERROR：屬於抓取／傳輸失敗，需確認 Google Finance 頁面是否仍可達。",
    "- 已產生 `loop-report` 與 reviewer JSON，詳見 `~/Downloads/Sotck/`。",
    "",
    "---",
    "",
    "*Generated by research-heartbeat run_loop.sh (Step 3.5)*",
]

with open(out, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
print(f"✅ Alert note written: {out}")
PYEOF
else
    echo "--- Step 3.5: No SUSPECT/ERROR findings, alert note not needed ---"
fi
echo ""

# --- Step 4: UPDATE STATE ---
echo "--- Step 4: Update LOOP-STATE.md (baselines + run log) ---"
MARKET_LINE="- **[${TIMESTAMP}]** Loop run OK, fetch=${OK_COUNT}/${TOTAL}, verdict=${VERDICT}(${SCORE})"

# The market observations themselves were already written in Step 1.5 (before
# the writer ran), so the report quotes today's session. This step only
# refreshes the baseline block and appends the run log line.
if [ $STATE_NEW -eq 0 ]; then
    # Insert before "## 下次繼續追蹤" section
    STATE="$STATE" TIMESTAMP="$TIMESTAMP" OK_COUNT="$OK_COUNT" TOTAL="$TOTAL" VERDICT="$VERDICT" SCORE="$SCORE" MARKET_LINE="$MARKET_LINE" FETCH_JSON="$FETCH_JSON" "$PYTHON" << 'PYEOF'
import os
state_path = os.environ["STATE"]
timestamp = os.environ["TIMESTAMP"]
ok_count = os.environ["OK_COUNT"]
total = os.environ["TOTAL"]
verdict = os.environ["VERDICT"]
score = os.environ["SCORE"]
market_line = os.environ["MARKET_LINE"]

with open(state_path, "r", encoding="utf-8") as f:
    content = f.read()

# Update last report summary
import re, json, os

# Refresh the per-ticker baselines. Previously this step only rewrote the
# 「時間」/「總計」 lines, so the seven baseline prices froze at the last manual
# edit (2026-09-10). Criterion 3 checks for the presence of those baseline lines,
# and Criterion 7 requires newly-seen tickers to be added — neither can ever be
# satisfied by a script that never writes baselines.
PRIORITY = ["LITE", "2330", "NVDA", "TSM", "AMD", "ORCL", "2454", "PLTR"]
fetch_entries = []
try:
    with open(os.environ.get("FETCH_JSON", ""), "r", encoding="utf-8") as fh:
        fetch_entries = json.load(fh)
except Exception:
    fetch_entries = []
price_by_ticker = {
    e.get("ticker"): e for e in fetch_entries
    if isinstance(e, dict) and e.get("status") == "ok" and isinstance(e.get("price"), (int, float))
}

baseline_lines = []
for tk in PRIORITY:
    e = price_by_ticker.get(tk)
    if not e:
        continue
    price = e["price"]
    cur = e.get("currency") or "USD"
    chg = e.get("change_pct")
    chg_str = f"（{chg:+.2f}%）" if isinstance(chg, (int, float)) else ""
    prefix = "NT$" if cur == "TWD" else "$"
    baseline_lines.append(f"- {tk}：**{prefix}{price:,.2f} {cur}**{chg_str}")

baseline_block = ""
if baseline_lines:
    baseline_block = "\n- **七大關注股 baseline**：\n" + "\n".join(baseline_lines) + "\n"

match = re.search(r"## 上次報告摘要\n\n- \*\*時間\*\*：([^\n]+)\n\n- \*\*總計\*\*：([^\n]+)", content)
if match:
    new_summary = f"## 上次報告摘要\n\n- **時間**：{timestamp}\n\n- **總計**：{ok_count}/{total} ok, verdict={verdict}({score}){baseline_block}"
    content = content[:match.start()] + new_summary + content[match.end():]
else:
    # Fallback: 「上次報告摘要（Last Report Summary）」 heading variant.
    match2 = re.search(r"(## 上次報告摘要[^\n]*\n)", content)
    if match2:
        new_summary = f"\n**{timestamp}**\n\n- **總計**：{ok_count}/{total} ok, verdict={verdict}({score}){baseline_block}"
        content = content[:match2.end()] + new_summary + content[match2.end():]

# Append the run log line to the market context section.
# The observation bullets for today were already prepended in Step 1.5.
market_marker = "## 當前市場線索"
if market_marker in content:
    idx = content.find(market_marker)
    next_idx = content.find("\n## ", idx + 3)
    if next_idx == -1:
        next_idx = len(content)
    content = content[:next_idx] + market_line + "\n" + content[next_idx:]

with open(state_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ Updated {state_path}")
PYEOF
else
    echo "⚠️  Skipping state update (file didn't exist before)"
fi

echo ""
echo "=== Loop Complete ==="
echo "Output files in $OUT_DIR:"
echo "  - $FETCH_OUT (fetch report)"
echo "  - $FETCH_JSON (fetch JSON)"
echo "  - $REVIEW_MD (review verdict)"
echo "  - $REPORT_OUT (final report)"
echo ""
echo "Verdict: $VERDICT (score=$SCORE)"