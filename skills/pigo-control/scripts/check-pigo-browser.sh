#!/bin/bash
# check-pigo-browser.sh — check if a specific CDP endpoint is reachable

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-9222}"

curl -s --max-time 3 "http://$HOST:$PORT/json" 2>/dev/null | grep -o '"url":"[^"]*"' | head -1 | sed 's/"url":"//;s/"$//'