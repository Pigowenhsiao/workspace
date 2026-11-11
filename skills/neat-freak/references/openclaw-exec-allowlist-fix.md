# OpenClaw 安全設定：safeBins + safeBinProfiles 同步規則（2026-05-25 實測）

## 核心規則

**每一個 `tools.exec.safeBins` entry 都必須在 `tools.exec.safeBinProfiles` 有對應 entry。**

即使 profile 值是空物件 `{}`，也必須存在。沒有例外。

## 兩層根因：`allowlist miss` 的完整診斷（2026-05-25 新增）

`allowlist miss` 錯誤有兩個獨立層次的根因，可能同時存在：

| 層次 | 根因 | 處理 |
|------|------|------|
| **Layer 1** | 命令根本不在 `safeBins` 清單中 | 將命令加入 `safeBins` |
| **Layer 2** | 命令在 `safeBins` 但無 `safeBinProfiles` 條目 | 補上 `safeBinProfiles` entry（`{}`） |

**兩者都報 `allowlist miss`**，但只修 Layer 2 不修 Layer 1 不會生效。

快速確認：
```python
import os
import json
with open(os.path.expanduser('~/.openclaw/openclaw.json')) as f:
    d = json.load(f)
sb = d.get('tools', {}).get('exec', {}).get('safeBins', [])
sbp = d.get('tools', {}).get('exec', {}).get('safeBinProfiles', {})
COMMON = ['wc', 'test', 'head', 'tail', 'sort', 'xargs', 'find', 'grep', 'sed', 'awk']
for cmd in COMMON:
    in_sb = cmd in sb
    in_sbp = cmd in sbp
    if not in_sb:
        print(f"L1 MISS: {cmd} not in safeBins → add to safeBins")
    elif not in_sbp:
        print(f"L2 MISS: {cmd} in safeBins but no profile → add to safeBinProfiles")
```

## 為什麼 Layer 2 會發生

當 `tools.exec.security = "allowlist"` 時，OpenClaw 內部的 allowlist 評估邏輯會：

1. 檢查 `safeBins` 中每個 binary 是否有對應的 `safeBinProfiles` 條目
2. 若有 entry 但無 profile → 寫 log `ignoring unprofiled safeBins entries (<binary>)`
3. 該 binary 從 effective allowlist 中被移除
4. 任何使用該 binary 的 shell command 被 exec deny：`exec denied: allowlist miss`

## 日誌徵兆（辨識用）

```
[exec] ignoring unprofiled safeBins entries (node)
[exec] interpreter/runtime binaries in safeBins (node) are unsafe without explicit hardened profiles; prefer allowlist entries
[tools] exec failed: exec denied: allowlist miss
```

## 修復模板（Python，完整兩層）

```python
import os
import json

with open(os.path.expanduser('~/.openclaw/openclaw.json')) as f:
    d = json.load(f)

exec_cfg = d.get('tools', {}).get('exec', {})
sb = exec_cfg.get('safeBins', [])
sbp = exec_cfg.get('safeBinProfiles', {})

# Layer 1: 確保所有 safeBins entry 有 profile
for entry in sb:
    if entry not in sbp:
        sbp[entry] = {}

# Layer 2: 所有 interpreter/runtime 明確設定 profile
for runtime in ['node', 'python3', 'python']:
    for path in [
        runtime,
        os.path.expanduser(f'~/.nvm/versions/node/v22.22.3/bin/{runtime}'),
        os.path.expanduser(f'~/.nvm/versions/node/v22.22.2/bin/{runtime}'),
    ]:
        if path not in sbp:
            sbp[path] = {}

# Layer 3: 確保所有常見 shell 命令在 safeBins 中（防止 layer-1 miss）
COMMON_COMMANDS = [
    'wc', 'cd', 'print', 'test', 'head', 'tail', 'sort', 'xargs',
    'find', 'grep', 'sed', 'awk', 'ls', 'cat', 'echo', 'pwd',
    'mkdir', 'cp', 'mv', 'rm', 'sleep', 'printf', 'curl', 'rg',
    'bash', 'sh', 'git', 'pip', 'pip3', 'hermes', 'npx', 'yt-dlp'
]
for cmd in COMMON_COMMANDS:
    if cmd not in sb:
        sb.append(cmd)
        print(f'Added {cmd} to safeBins')
    if cmd not in sbp:
        sbp[cmd] = {}

# Layer 4: 完整路徑 version 也補上
FULL_PATHS = {
    'ls': '/usr/bin/ls', 'cat': '/usr/bin/cat', 'echo': '/usr/bin/echo',
    'grep': '/usr/bin/grep', 'head': '/usr/bin/head', 'tail': '/usr/bin/tail',
    'sort': '/usr/bin/sort', 'wc': '/usr/bin/wc', 'find': '/usr/bin/find',
    'xargs': '/usr/bin/xargs', 'test': '/usr/bin/test', 'cp': '/usr/bin/cp',
    'mv': '/usr/bin/mv', 'mkdir': '/usr/bin/mkdir', 'pwd': '/usr/bin/pwd',
    'bash': '/usr/bin/bash', 'sh': '/usr/bin/sh', 'sed': '/usr/bin/sed',
    'awk': '/usr/bin/awk', 'git': '/usr/bin/git', 'cd': '/usr/bin/cd',
    'sleep': '/usr/bin/sleep', 'printf': '/usr/bin/printf',
    'curl': '/usr/bin/curl', 'pip': '/usr/bin/pip', 'pip3': '/usr/bin/pip3',
    'rg': '/usr/bin/rg', 'yt-dlp': '/usr/bin/yt-dlp',
    'hermes': os.path.expanduser('~/.local/bin/hermes'),
    'npx': os.path.expanduser('~/.nvm/versions/node/v22.22.3/bin/npx'),
    'bb-browser': os.path.expanduser('~/.local/bin/bb-browser'),
    'codex': os.path.expanduser('~/.nvm/versions/node/v22.22.3/bin/codex'),
}
for bin_name, full_path in FULL_PATHS.items():
    if full_path not in sbp:
        sbp[full_path] = {}

with open(os.path.expanduser('~/.openclaw/openclaw.json'), 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)

print(f'safeBins count: {len(sb)}')
print(f'safeBinProfiles count: {len(sbp)} (all should be {{}})')
```

## 驗證流程

```bash
# 重啟 gateway
kill -9 $(pgrep -f "openclaw.*gateway")
openclaw gateway start &
sleep 12
curl -s http://localhost:18800/health

# 檢查 log 中不再出現 "ignoring unprofiled"
journalctl --user -u openclaw-gateway -n 30 | grep -E "unprofiled|allowlist miss"
# 乾淨輸出：只有 exec.approval.list 的 ✓，無 denied
```

## 新增 safeBins entry 時的同步檢查清單

每次手動或透過 `openclaw doctor --fix` 新增 binary 到 `safeBins`：
- [ ] 確認該 binary 的 name 版本在 `safeBinProfiles` 有 entry
- [ ] 確認該 binary 的完整路徑版本在 `safeBinProfiles` 有 entry
- [ ] 若該 binary 是 interpreter/runtime，profile 值用 `{}`
- [ ] 重啟 gateway 後驗證 journal 無 `unprofiled` 警告

## 已知風險 binary（最容易漏 profile）

| Binary | 典型路徑 | 風險 |
|--------|---------|------|
| `node` | `~/.nvm/versions/node/v22.22.3/bin/node` | 高：幾乎一定在 safeBins 但最常被忽略 |
| `python3` | `/usr/bin/python3` | 高：同上 |
| `codex` | `~/.nvm/versions/node/v22.22.3/bin/codex` | 中：codex 常用 |
| `bb-browser` | `~/.local/bin/bb-browser` | 中：daemon 常用 |

---

**相關知識點**：這個規則與 OpenClaw 的 `exec.approval` 機制是分開的。`safeBins` + `safeBinProfiles` 控制哪些 shell command 可以執行；`exec-approvals.json` 控制哪些工具有審批流程。兩者獨立運作。