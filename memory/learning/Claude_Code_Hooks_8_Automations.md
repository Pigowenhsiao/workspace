# 8 Claude Code Hooks That Automate What You Keep Forgetting

> 來源：https://t.me/zodchixquant  
> 摘要：8 個 Claude Code Hooks 自動化了平時容易忘記的瑣事，大幅提升 AI  coding 的品質與安全。

---

## 什麼是 Hooks？

Claude Code 的 Hooks 是**自動執行的動作**，在每次 Claude 編輯檔案、執行命令或完成任務時觸發。

兩個核心類型：
- **PreToolUse**：工具執行前觸發（可阻擋動作）
- **PostToolUse**：工具執行後觸發（清理、格式化、測試）
- **Stop**：Claude 完成回應時觸發

設定檔位置：
- `.claude/settings.json`（專案層級，團隊共享）
- `~/.claude/settings.json`（使用者層級）

---

## 8 個 Hooks

### 1. 自動格式化每個檔案

每次 Claude 寫入或編輯檔案後，自動跑 Prettier 格式化。

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write 2>/dev/null; exit 0"
      }]
    }]
  }
}
```

Python → `black`，Go → `gofmt`，Rust → `rustfmt`。

---

### 2. 阻擋危險命令

在 `rm -rf`、`git reset --hard`、`DROP TABLE` 等危險操作執行前阻擋。

`.claude/hooks/block-dangerous.sh`：
```bash
#!/usr/bin/env bash
set -euo pipefail
cmd=$(jq -r '.tool_input.command // ""')
dangerous_patterns=("rm -rf" "git reset --hard" "DROP TABLE" "curl.*|.*sh")
for pattern in "${dangerous_patterns[@]}"; do
  if echo "$cmd" | grep -qiE "$pattern"; then
    echo "Blocked: '$cmd'" >&2; exit 2
  fi
done
exit 0
```

---

### 3. 保護敏感檔案

禁止編輯 `.env`、`*.pem`、`secrets/*` 等檔案。

`.claude/hooks/protect-files.sh`：
```bash
#!/usr/bin/env bash
set -euo pipefail
file=$(jq -r '.tool_input.file_path // .tool_input.path // ""')
protected=(".env*" ".git/*" "package-lock.json" "*.pem" "secrets/*")
for pattern in "${protected[@]}"; do
  if echo "$file" | grep -qiE "^${pattern//\*/.*}$"; then
    echo "Blocked: '$file' is protected." >&2; exit 2
  fi
done
exit 0
```

---

### 4. 每次編輯後自動跑測試

Claude 每次寫入檔案後，自動執行測試。如果失敗，Claude 會立即看到並修復。

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "npm run test --silent 2>&1 | tail -5; exit 0"
      }]
    }]
  }
}
```

作者 Boris Cherny（Claude Code 創辦人）指出：這種 feedback loop 可提升輸出品質 2-3 倍。

---

### 5. PR 前的測試門檻

建立 PR 前，必須通過所有測試 否則阻擋。

`.claude/hooks/require-tests-for-pr.sh`：
```bash
#!/usr/bin/env bash
set -euo pipefail
if npm run test --silent; then exit 0
else echo "Tests are failing. Fix before creating PR." >&2; exit 2
fi
```

---

### 6. 自動 Lint 並回報錯誤

每次編輯後自動執行 ESLint，錯誤即時修正，不留到 code review。

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "npx eslint --fix $(jq -r '.tool_input.file_path') 2>&1 | tail -10; exit 0"
      }]
    }]
  }
}
```

可與 #1（Prettier）串聯：Prettier 先格式化，ESLint 再檢查風格。

---

### 7. 記錄每個執行的命令

每次 Bash 命令前，附加時間戳到日誌檔。

`.claude/hooks/log-commands.sh`：
```bash
#!/usr/bin/env bash
set -euo pipefail
cmd=$(jq -r '.tool_input.command // ""')
printf '%s %s\n' "$(date -Is)" "$cmd" >> .claude/command-log.txt
exit 0
```

`.claude/command-log.txt` 加入 `.gitignore`。

---

### 8. 任務完成後自動 Commit

Claude 每次停止回應時，自動 commit 所有變更。保持 commit 原子性（一個任務 = 一個 commit）。

`.claude/hooks/auto-commit.sh`：
```bash
#!/usr/bin/env bash
set -euo pipefail
git add -A
if ! git diff --cached --quiet; then
  git commit -m "chore(ai): apply Claude edit"
fi
exit 0
```

配合 `claude -w feature-branch`（worktrees）效果最佳。

---

## 完整 settings.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": ".claude/hooks/block-dangerous.sh" },
          { "type": "command", "command": ".claude/hooks/log-commands.sh" }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": ".claude/hooks/protect-files.sh" }
        ]
      },
      {
        "matcher": "mcp__github__create_pull_request",
        "hooks": [
          { "type": "command", "command": ".claude/hooks/require-tests-for-pr.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write 2>/dev/null; exit 0" },
          { "type": "command", "command": "npx eslint --fix $(jq -r '.tool_input.file_path') 2>&1 | tail -10; exit 0" }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": ".claude/hooks/auto-commit.sh" }
        ]
      }
    ]
  }
}
```

---

## 核心心得

> 「好的 Claude Code 設定與頂尖設定的差距不在模型或 prompt，在於 hooks。它們在你沒注意的時候自動運作，攔截你在 code review 或 production 才會發現的錯誤。」

**最低標配**：Hook #1（自動格式化）+ #2（阻擋危險命令）  
**完整配置**：建議全部部署，根據專案需求調整

---

tags: Claude, Code, Hooks, Automation, AI, Workflow
