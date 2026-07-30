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

# --- Step 1: FETCH ---
echo "--- Step 1: Fetch (google-finance) ---"
FETCH_OUT="$OUT_DIR/google-finance-$TS.md"
python3 "$FETCHER" "$WATCHLIST" "$FETCH_OUT"
FETCH_JSON="${FETCH_OUT%.md}.json"

if [ ! -f "$FETCH_JSON" ]; then
    echo "❌ Fetch JSON not produced: $FETCH_JSON"
    exit 1
fi

OK_COUNT=$(python3 -c "import json; d=json.load(open('$FETCH_JSON')); print(sum(1 for t in d if t.get('status')=='ok'))")
TOTAL=$(python3 -c "import json; d=json.load(open('$FETCH_JSON')); print(len(d))")
echo "Fetch: $OK_COUNT / $TOTAL ok"
echo ""

# --- Step 2: REVIEW ---
echo "--- Step 2: Review (reviewer-finance) ---"
python3 "$REVIEWER" "$FETCH_JSON" "$STATE"
REVIEW_JSON="${FETCH_JSON%.json}-review.json"
REVIEW_MD="${FETCH_JSON%.json}-review.md"

if [ ! -f "$REVIEW_JSON" ]; then
    echo "❌ Review JSON not produced"
    exit 1
fi

VERDICT=$(python3 -c "import json; d=json.load(open('$REVIEW_JSON')); print(d.get('overall','?'))")
SCORE=$(python3 -c "import json; d=json.load(open('$REVIEW_JSON')); print(d.get('score',0))")
echo "Review: $VERDICT (score=$SCORE)"
echo ""

# --- Step 3: WRITE ---
echo "--- Step 3: Write (finance-writer) ---"
REPORT_OUT="$OUT_DIR/loop-report-$TS.md"
python3 "$WRITER" "$FETCH_JSON" "$REVIEW_JSON" "$STATE" "$REPORT_OUT"

if [ ! -f "$REPORT_OUT" ]; then
    echo "❌ Report not produced: $REPORT_OUT"
    exit 1
fi

echo "Report: $REPORT_OUT ($(wc -l < "$REPORT_OUT") lines)"
echo ""

# --- Step 4: UPDATE STATE ---
echo "--- Step 4: Update LOOP-STATE.md ---"
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")
MARKET_LINE="- **[${TIMESTAMP}]** Loop run OK, fetch=${OK_COUNT}/${TOTAL}, verdict=${VERDICT}(${SCORE})"

# Append market context entry
if [ $STATE_NEW -eq 0 ]; then
    # Insert before "## 下次繼續追蹤" section
    STATE="$STATE" TIMESTAMP="$TIMESTAMP" OK_COUNT="$OK_COUNT" TOTAL="$TOTAL" VERDICT="$VERDICT" SCORE="$SCORE" MARKET_LINE="$MARKET_LINE" python3 << 'PYEOF'
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
import re
match = re.search(r"## 上次報告摘要\n\n- \*\*時間\*\*：([^\n]+)\n\n- \*\*總計\*\*：([^\n]+)", content)
if match:
    new_summary = f"## 上次報告摘要\n\n- **時間**：{timestamp}\n\n- **總計**：{ok_count}/{total} ok, verdict={verdict}({score})"
    content = content[:match.start()] + new_summary + content[match.end():]

# Append market context
market_marker = "## 當前市場線索"
if market_marker in content:
    idx = content.find(market_marker)
    # Find next section
    next_idx = content.find("\n## ", idx + 3)
    if next_idx == -1:
        next_idx = len(content)
    # Insert before next section
    new_market = market_line + "\n"
    content = content[:next_idx] + new_market + content[next_idx:]

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