#!/usr/bin/env bash
set -euo pipefail

URL="${1:-}"
if [[ -z "$URL" ]]; then
  echo "Usage: $0 <URL>"
  exit 1
fi

if command -v google-chrome >/dev/null 2>&1; then
  google-chrome --headless --disable-gpu --remote-debugging-port=9222 "$URL" &
  echo "已啟動無頭模式，端口 9222 可用於自動化"
else
  echo "Chrome 未安裝，無法啟動無頭模式"
fi
