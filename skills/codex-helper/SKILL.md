# Codex Helper Skill

## 觸發關鍵字
- `/codex`
- `幫我寫 code`
- `用 codex`

## 功能
透過 exec tool 呼叫本地 `codex` 或 `opencode` CLI 來處理任務。

## 使用方式

### 直接在對話中說：
- `/codex [你的需求]` — 例如：`/codex 幫我寫一個 Python sorting function`
- `用 codex 幫我做 [事情]`

### 背後執行方式
Agent 收到請求後，透過 exec tool 執行：
```javascript
exec({
  command: "codex --model gpt-5.5 --no-color",
  pty: true,
  input: "<user prompt>"
})
```

## 設定
- 預設命令：`codex`
- 備用命令：`opencode`
- 預設模型：`gpt-5.5`

## 前置需求
1. 已安裝 OpenAI Codex CLI
2. 已執行 `codex auth` 完成登入
3. 系統有 Node.js >= 22

## 故障排除
- 若回應 `command not found`，表示 codex 未安裝或不在 PATH
- 若認證失敗，先執行 `codex auth`