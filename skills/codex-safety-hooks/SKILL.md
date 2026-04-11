# Codex Safety Hooks

Pigo 的 Codex 安全 hooks，阻擋危險命令並記錄所有操作。

## 功能

1. **block_dangerous.py** — 阻擋危險命令
2. **log_commands.py** — 記錄所有 Bash 命令到日誌
3. **auto_commit.sh** — 回應結束後自動 commit

## 已阻擋的模式

- `rm -rf /` 及系統目錄
- `git push --force`
- `git reset --hard`
- `DROP TABLE` / `TRUNCATE` / `DELETE FROM` (無 WHERE)
- `curl/wget ... | bash` (管線注入風險)
- `mkfs` / `dd` 磁碟寫入
- `chmod 777`
- Fork bomb、系統關機命令

## 檔案位置

- Hooks 設定：`~/.codex/hooks.json`
- Scripts：`~/.codex/hooks/`
- 命令日誌：`~/.codex/command_log.txt`

## 觸發方式

Pigo 說「幫我做一個安全 hook」或「設定 Codex hooks」時使用。
