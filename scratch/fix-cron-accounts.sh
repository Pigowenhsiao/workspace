#!/bin/bash
# Repair legacy cron automations that lack a recorded inference account.
# Requires exclusive offline state ownership: stop gateway -> doctor --fix -> start gateway.
LOG=/home/pigo/.openclaw/workspace/scratch/fix-cron-accounts.log
exec >>"$LOG" 2>&1
echo "=== start $(date -u +%FT%TZ)"
systemctl --user stop openclaw-gateway.service
sleep 6
cd /home/pigo
openclaw doctor --fix --force
echo "=== doctor exit: $?"
systemctl --user start openclaw-gateway.service
sleep 12
systemctl --user is-active openclaw-gateway.service
echo "=== done $(date -u +%FT%TZ)"
