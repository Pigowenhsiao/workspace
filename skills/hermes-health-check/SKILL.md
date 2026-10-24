---
name: "hermes-health-check"
description: "檢查 Hermes gateway 健康：服務/fd/平台/cron/遠端 v100。當使用者問「Hermes 是否正常」時觸發。"
---

# Hermes 健康檢查

回答「Hermes 是否正常」時跑這套唯讀診斷。不要為了診斷而重啟服務；先讀出狀態再判斷。

## Step 1：先確認服務實際跑在哪台

Hermes gateway 跑在**本機** systemd user service `hermes-gateway.service`，不在 `v100`。使用者常把「主機名」跟「服務位置」混著講（例如「去 v100 看一下 Hermes」）。先確認這一點，再決定要不要 SSH。

```bash
systemctl --user is-active hermes-gateway.service
systemctl --user show hermes-gateway.service -p MainPID -p NRestarts -p MemoryCurrent --value
```

判讀：`NRestarts` > 0 代表服務自己重啟過，先查原因再談健康；`MemoryCurrent` 對照 `Memory` 峰值看是否有洩漏趨勢。

## Step 2：一次讀出所有平台狀態

`~/.hermes/gateway_state.json` 內含 `platforms` 每個通道的 `state` / `error_code` / `error_message`，是判斷「哪個通道壞了」最快的單一來源。

```bash
python3 -c "
import json
d=json.load(open('/home/pigo/.hermes/gateway_state.json'))
print('state:',d.get('gateway_state'),'| pid:',d.get('pid'),'| active_agents:',d.get('active_agents'))
for k,v in (d.get('platforms') or {}).items():
    print(' -',k,':',v.get('state'),'| err:',v.get('error_code'),'|',(v.get('error_message') or '')[:80])
"
```

`state` 為 `retrying` 的通道，往對應 log 找根因，不要重啟整個 gateway。

## Step 3：服務層健康與 fd

```bash
timeout 10 curl -s http://127.0.0.1:8643/health
PID=$(systemctl --user show hermes-gateway.service -p MainPID --value)
ls /proc/$PID/fd | wc -l
grep "open files" /proc/$PID/limits
```

判讀：fd 數量接近 soft limit（預設 4096）就是 fd 洩漏徵兆，先查是哪支程序持有過量 fd，再談重啟。`8643/health` 回 `{"status":"ok"}` 代表服務層沒問題，通道問題要分開看。

## Step 4：查 log 找出真正在壞的東西

```bash
journalctl --user -u hermes-gateway.service --since "1 hour ago" --no-pager | grep -viE "telegram_network|intake slot" | tail -20
journalctl --user -u hermes-gateway.service --since "1 hour ago" --no-pager | grep -c "ConnectTimeout"
```

已知雜訊（不算故障，別當成問題回報）：

- `telegram_network ... ConnectTimeout` — 直連 Telegram IP 失敗，sticky IPv4 path 每次都會 fallback 救回來，訊息沒漏。
- `inkbox.tunnels ... status=408 reason='intake-idle-cap'` — 閒置槽位逾時，屬正常排空。

真故障訊號：`Bridge process died (exit code 1)`、`kanban dispatcher: ... deferred`、`too many open files`、`unable to open database file`。

## Step 5：WhatsApp 登出迴圈需要人介入

bridge log 出現 `Logged out. Delete session and restart to re-authenticate` 時，gateway 會每 5 分鐘重啟 bridge、每次都登出，log 持續噴。**這需要使用者拿手機掃 QR 重新認證，agent 無法自動修**。不要刪 session、不要嘗試繞過；回報「需手動重新認證」並問使用者要不要先停掉重試迴圈以免灌 log。

```bash
tail -15 ~/.hermes/whatsapp/bridge.log
journalctl --user -u hermes-gateway.service --since "2 hours ago" --no-pager | grep -c "Bridge process died"
```

### 使用者要求「停掉 WhatsApp」時的正確做法

停用開關是 `~/.hermes/.env` 的 `WHATSAPP_ENABLED`（不是 `config.yaml`；`config.yaml` 只有 `platform_toolsets.whatsapp` 工具集清單，無啟停開關）。`WHATSAPP_MODE` / `WHATSAPP_ALLOWED_USERS` 是同區的相鄰設定。

```bash
cp ~/.hermes/.env ~/.hermes/.env.bak.$(date +%Y%m%d-%H%M%S)
sed -i 's/^WHATSAPP_ENABLED=true$/WHATSAPP_ENABLED=false/' ~/.hermes/.env
systemctl --user restart hermes-gateway.service
```

改完必須重啟 gateway 才會生效；重啟後 bridge 不會再被拉起，port 3000 不再監聽。

**驗證「真的停了」要看這兩點，不要只看 `gateway_state.json`：**

1. `~/.hermes/whatsapp/bridge.log` 的 mtime **不再更新**（原本每 5 分鐘跳一次）——這是最可靠的真實指標。
2. `journalctl --user -u hermes-gateway.service --since "<重啟時刻>" | grep -i whatsapp` 沒有新行。

`gateway_state.json` 的 `platforms.whatsapp` 在重啟後仍會殘留 `state: retrying` / `error_code: whatsapp_bridge_exited`，那是**上一個 PID 寫入的舊快照**，會在新 gateway 尚未重新註冊該通道前持續顯示，不代表還在重試。判斷依優先序：bridge.log mtime > journalctl 新行 > gateway_state.json。

## Step 6：遠端 v100 可用性（獨立判斷）

v100 = `192.168.0.140`，`~/.ssh/config` 有 `Host v100`（user `x`）。

```bash
ping -c 2 -W 3 192.168.0.140
ip neigh show 192.168.0.140
timeout 20 ssh -o ConnectTimeout=10 -o BatchMode=yes v100 'hostname; uptime'
timeout 8 curl -s -o /dev/null -w "%{http_code}\n" http://192.168.0.140:8080/v1/models
```

v100 掛掉**不等於 Hermes 掛掉**。v100 只提供 `custom_providers.Qwen3.8-Q8`（`http://192.168.0.140:8080/v1`），是第三順位可選後端；主模型鏈是 `minimax`（default）+ `nvidia`（fallback），不經 v100。查 `~/.hermes/auth.json` 的 `credential_pool` 看該 provider 的 `request_count`，為 0 代表根本沒被叫過，離線無實害。

v100 離線時回報「主機無網路，需要實體開機」，並確認沒有 WOL 或 tunnel 備援路徑（`~/.ssh/config` 只有 `v100` 與 `pigo-server` 兩個 host 區段）。

## Step 7：產出報告

分三段回報，避免把雜訊講成故障：

1. **服務層**：active 與否、重啟次數、health 結果、fd 用量
2. **通道層**：逐個 platform 的 state，只標真正異常者與需要使用者動手者
3. **遠端依賴**：v100 可否連線、它在架構中是否關鍵

結尾給出明確的下一步：需要使用者動作（掃碼、開機、拍板）的分開列出，不要混在診斷裡。

## 不要做的事

- 不要為了看狀態就 `systemctl --user restart hermes-gateway.service`；先讀後動
- 不要在 v100 離線時把主模型鏈也報成故障
- 不要刪 `~/.hermes/whatsapp/session` 試圖自動重新登入
- 不要把 `ConnectTimeout` / `intake-idle-cap` 當成需要修的問題
