# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

# [2026-07-25] Hermes fd leak 24h 觀察任務（重啟後）
# 起點：2026-07-25 09:10 UTC（gateway 重啟完，PID 3334516, fd 43）
# 到期：2026-07-26 09:10 UTC（24h 後）
# 檢查項：
#   1. PID 3334516 還在嗎？ (`ps -p 3334516`)
#   2. fd 數 (`ls /proc/3334516/fd | wc -l`) 應 < 200，> 500 警告，> 1000 嚴重
#   3. mcp-stderr.log 大小 (`ls -la ~/.hermes/logs/mcp-stderr.log`) 應 < 100MB，> 1GB 警告
#   4. 2971155 等背景 hermes CLI client 是否又掛了 3+ 天沒重啟 (`ps -o etime -p <PID>`)
# 失敗動作：如上面任一超標，跑 SOP: 殺 2971155 → kill -TERM gateway → systemd restart → rm 舊 log
# 參考：MEMORY.md [P1][2026-07-25] Hermes fd 滿 4.8GB mcp-stderr 事件 SOP
