#!/usr/bin/env bash
set -euo pipefail

URL="${1:-}"
if [[ -z "$URL" ]]; then
  echo "Usage: $0 <URL>"
  exit 1
fi

if command -v google-chrome >/dev/null 2>&1; then
  google-chrome --new-window "$URL"
elif command -v chromium-browser >/dev/null 2>&1; then
  chromium-browser --new-window "$URL"
else
  echo "Chrome/Chromium 未安裝，改用預設瀏覽器"
  xdg-open "$URL"
fi
