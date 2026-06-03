#!/bin/bash
# find-pigo-browser.sh — discover reachable CDP endpoints on Linux

HOST="127.0.0.1"
PORT_START=9222
PORT_END=9332
PRIORITY_PORTS="9233 19825"

echo "=== Pigo Browser Discovery ==="

fetch_browser_info() {
  local port=$1
  local json
  json=$(curl -s --max-time 3 "http://$HOST:$port/json" 2>/dev/null)
  if [ -z "$json" ] || [ "$json" = "[]" ]; then
    echo "empty"
    return
  fi
  # Get first page-type entry (skip iframes/workers)
  echo "$json" | grep -o '"title":"[^"]*"' | grep -v 'Service Worker' | grep -v 'chrome-extension' | grep -v 'chrome-untrusted' | head -1 | sed 's/"title":"//;s/"$//'
}

# Priority ports first
for port in $PRIORITY_PORTS; do
  response=$(curl -s --max-time 1 -o /dev/null -w "%{http_code}" "http://$HOST:$port/json" 2>/dev/null)
  if [ "$response" = "200" ]; then
    info=$(fetch_browser_info $port)
    [ -n "$info" ] && echo "[FOUND] http://$HOST:$port | $info" || echo "[FOUND] http://$HOST:$port (no title)"
  fi
done

# Scan range
for port in $(seq $PORT_START $PORT_END); do
  skip=0
  for p in $PRIORITY_PORTS; do [ "$port" = "$p" ] && skip=1 && break; done
  [ "$skip" = "1" ] && continue
  response=$(curl -s --max-time 1 -o /dev/null -w "%{http_code}" "http://$HOST:$port/json" 2>/dev/null)
  if [ "$response" = "200" ]; then
    info=$(fetch_browser_info $port)
    [ -n "$info" ] && echo "[FOUND] http://$HOST:$port | $info" || echo "[FOUND] http://$HOST:$port (no title)"
  fi
done

echo "=== End Discovery ==="