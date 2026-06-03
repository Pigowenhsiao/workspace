# OpenClaw Codex CLI Plugin

將 OpenAI Codex CLI（codex / opencode）接入 OpenClaw 作為文字推論後端。

## 安裝方式

### 方法一：本地開發（不發布）
Plugin 已安裝在：
```
/home/pigo/.openclaw/workspace/skills/openclaw-codex-plugin/
```

### 方法二：發布到 ClawHub
```bash
cd /home/pigo/.openclaw/workspace/skills/openclaw-codex-plugin
npm publish
# 其他用戶可透過 openclaw plugins install clawhub:@pigo/openclaw-codex-cli 安裝
```

## 設定

在 `openclaw-codex-plugin/openclaw.plugin.json` 設定：

```json
{
  "configSchema": {
    "command": "codex",      // CLI 命令（codex / opencode）
    "model": "gpt-4o",      // 預設模型
    "temperature": 0.7,
    "args": ""
  }
}
```

## 使用方式

在 OpenClaw 的 model config 或 agent prompt 中使用：
```
model: codex-cli/codex
```

## 前置需求

1. 已安裝 `codex` 或 `opencode` CLI
2. 已經過 OpenAI 登入驗證（`codex auth` 或 `opencode auth`）
3. Node.js >= 22.19

## 測試

```bash
codex --version
opencode --version
```

## 疑難排解

**Q: Plugin 沒被載入？**
A: 檢查 Gateway 重啟後日誌確認 plugin discovery 成功

**Q: 認證失敗？**
A: 先在 terminal 執行 `codex auth` 完成 OpenAI 登入