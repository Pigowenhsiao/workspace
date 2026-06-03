#!/bin/bash
# start-pigo-browser.sh — launch Chrome with remote debugging on Linux

PROFILE_DIR="/home/pigo/.codex/chrome-login-profile"
PROFILE_PATH="--user-data-dir=$PROFILE_DIR"
CDP_PORT=9222
START_URL="${URL:-about:blank}"

mkdir -p "$PROFILE_DIR"

/usr/bin/google-chrome \
  $PROFILE_PATH \
  --remote-debugging-port=$CDP_PORT \
  --no-first-run \
  --no-default-browser-check \
  --start-maximized \
  "$START_URL" &

echo "Chrome started with remote debugging on http://127.0.0.1:$CDP_PORT"
echo "Profile: $PROFILE_DIR"