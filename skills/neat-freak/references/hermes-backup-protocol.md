# Hermes Backup Protocol

> **2026-10-24（第十二 run）全面重寫**：舊版描述的是一套**從未實際運作**的流程
> （`~/Documents/Agent/backups/hermes/`、`git commit` + `git push`、`0 0 * * *` 排程）。
> 實際運作的是 `~/.hermes/scripts/hermes-backup.sh` + cron `89c411611e6d`。
> 舊版內容保留在 git history（`c94eb7dc`），可對照。

## 實際架構

| 項目 | 實際值 |
|------|--------|
| 執行腳本 | `~/.hermes/scripts/hermes-backup.sh` |
| 排程 | cron `89c411611e6d`（Hermes Backup），`0 3 * * *`（每日 03:00 CST） |
| 備份目的地 | `~/Documents/Backup/hermes/`（**不在** Agent repo 內） |
| 產物 | `hermes_<YYYY-MM-DD>_<HHMMSS>.tar.gz`（約 463–484MB/份） |
| 保留策略 | 30 天（`KEEP_DAYS=30`，`find -mtime +30 -delete`） |
| 執行模式 | `no_agent (script)` — cron 直接跑 shell，不經 Agent |
| 來源 | `~/.hermes/scripts/hermes-backup.sh`（**不在** git 管理下，改動需手動備份） |

## 備份範圍（腳本 `ITEMS` 陣列的實測值）

| 資料 | 路徑 | 存在 | 備註 |
|------|------|------|------|
| 主設定 | `~/.hermes/config.yaml` | ✅ | 含硬編碼 `strata-*` provider api_key |
| 全域指令 | `~/.hermes/AGENTS.md` | ✅ | |
| 認證 | `~/.hermes/auth.json` | ✅ | **含敏感憑證** |
| 憑證目錄 | `~/.hermes/credentials/` | ✅ | **含敏感憑證** |
| **主環境變數** | `~/.hermes/.env` | ✅ | **含敏感憑證**：`TELEGRAM_BOT_TOKEN`、`TELEGRAM_ALLOWED_USERS`、`GATEWAY_ALLOW_ALL_USERS`（2026-10-29 補入） |
| **Analysis profile env** | `~/.hermes/profiles/analysis/.env` | ✅ | **含敏感憑證**：`MINIMAX_API_KEY`、`STRATA_API_KEY`（2026-10-29 補入，保留相對路徑） |
| **Strata profile env** | `~/.hermes/profiles/strata/.env` | ✅ | **含敏感憑證**：`STRATA_API_KEY`（2026-10-29 補入，保留相對路徑） |
| **Documents env** | `~/Documents/.env` | ✅ | **含敏感憑證**：`MINIMAX_API_KEY`、`STRATA_API_KEY`、`GITHUB_TOKEN`、`HF_TOKEN`、`BRAVE_API_KEY`、`TWITTER_AUTH_TOKEN`、`OPENROUTER_API_KEY`、`DEEPSEEK_API_KEY`、`INKBOX_API_KEY` 等（2026-10-29 第二 run 補入；skills / shell script 實際使用的憑證檔，位於 `.hermes` 之外） |
| Skills | `~/.hermes/skills/` | ✅ | canonical skill 本體 |
| Memories | `~/.hermes/memories/` | ✅ | |
| Plugins | `~/.hermes/plugins/` | ✅ | |
| Cron | `~/.hermes/cron/` | ✅ | 含 `output/`（歷史執行紀錄） |
| Memory | `~/.hermes/memory/` | ✅ | P0/P1/P2 + dreaming + handoffs |
| Kanban DB | `~/.hermes/kanban.db` | ✅ | |

**不納入**：`~/.hermes/profiles/` 的其餘內容（模型檔、state-snapshots，體積評估後另行決定）、`~/.hermes/backups/`（curator 自己的備份）。

> ⚠️ **2026-10-29 修正**：原本三個 `.env` 都不在備份範圍內。
> `config.yaml` 裡的 `key_env: MINIMAX_API_KEY` 指的是**環境變數名**，
> 而該變數的**實際值來源**是 `~/.hermes/profiles/analysis/.env` ——
> 只備份 config 不備份 .env，**還原後 Telegram bot 與 minimax/strata provider 會完全失效**。
> 詳見 [skill-index-2026-10-29b-session.md](skill-index-2026-10-29b-session.md) Pattern WWW。
>
> ⚠️ **tar 平鋪 basename 的陷阱**：複製邏輯是 `tar -C "$(dirname "$item")" "$(basename "$item")"`，
> 只取 basename → 多個同名 `.env` 會被寫成同一個 `$BACKUP_DIR/.env` 互相覆蓋。
> 因此 profile 內的 `.env` 走 `EXTRA_ITEMS` 迴圈，保留相對路徑（`./profiles/analysis/.env`）。
> `EXTRA_ITEMS` 格式為 `<來源絕對路徑>::<backup 內相對路徑>`，以支援 `.hermes` 之外的來源
> （如 `~/Documents/.env` → `./Documents/.env`）。

## 已知問題與陷阱

### 自我參照競態（Pattern JJJ，2026-10-24 修正）

腳本把 `~/.hermes/cron` 整包納入備份，但 **cron job 自己的執行紀錄就寫在
`~/.hermes/cron/output/<job_id>/`**。執行 backup 的當下該日誌正被寫入 →
`cp -r` 讀到「檔案大小在讀取期間改變」→ 回傳非 0 → 印出 `[WARN] 複製失敗`。
**這不是權限或磁碟問題，是 backup 複製自己輸出目錄造成的自我參照競態。**

**實際影響（2026-10-24 03:00 實測）**：該次 tarball 缺 14 個 cron 檔案
（4 個當天 `output/*`、2 個 `external-workers/*.stderr`、2 個 `admissions/*.json`）；
其餘 118 個（config.yaml / auth.json / skills / memories / AGENTS.md / kanban.db）完整無缺。

**修復**：複製步驟從 `cp -r` 改為 `tar` pipe —

```bash
tar -cf - -C "$(dirname "$item")" --ignore-failed-read "$(basename "$item")" 2>/dev/null \
    | tar -xf - -C "$BACKUP_DIR" 2>/dev/null
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "[WARN] 複製失敗: $item"
    FAILED=1
fi
```

- `--ignore-failed-read`：讀取中變動的檔案只發警告，不中止整個 archive
- **`PIPESTATUS[0]` 取的是左側 tar（producer）**，不是管線最後一段；用 `$?` 會判斷錯對象

**驗證**：手動重跑 → 無 WARN；`gzip -t` rc=0；cron 檔案 **132/132 全數收錄，0 missing**。

## 驗證方法

```bash
# 1. 完整性
gzip -t ~/Documents/Backup/hermes/hermes_<最新>.tar.gz && echo GZIP_OK

# 2. 內容抽查（關鍵檔案必須在裡面）
tar -tzf ~/Documents/Backup/hermes/hermes_<最新>.tar.gz | grep -E '^\./(config\.yaml|auth\.json|AGENTS\.md|kanban\.db)$'

# 3. 逐檔比對 cron 收錄率（應為 0 missing）
#    見 session handoff：references/skill-index-2026-10-24f-session.md
```

## 還原演練（季度）

```bash
LATEST=$(ls -t ~/Documents/Backup/hermes/hermes_*.tar.gz | head -1)
mkdir -p /tmp/hermes-restore && tar -xzf "$LATEST" -C /tmp/hermes-restore
diff -rq ~/.hermes/memory/ /tmp/hermes-restore/memory/ | head -20
rm -rf /tmp/hermes-restore
```

**注意**：tarball 含 `auth.json` / `credentials/`（**明文憑證**）。
解開後務必 `rm -rf` 暫存目錄，不要留在磁碟上。

## 刪除備份的流程規則（Always-on）

1. **刪除前必須拿到使用者明確口頭授權**（例：回覆「可以刪除」）。之前授權過不代表這次可以刪——每次重新取得。
2. **先把要刪的完整清單列出給使用者看**（檔名 + 份數 + 回收量 + 保留區間），再執行。
3. **先驗證保留區間的備份完整**（`gzip -t` + `tar -tzf` 抽查關鍵檔案）再刪舊的——不要先刪再發現壞掉。
4. **保留至少一份最新且可驗證的 tarball**，並確認涵蓋連續日期段。
5. **刪除後量測實際 bytes**（見下方「精確容量核算」），確認落在目標內；差 1 份就是界線換算問題，不是 retention 故障。

## 磁碟容量

- 每份 ~462MB（2026-10 起；早期 09 月份為 ~922MB）
- **雙重保留機制**：
  1. `KEEP_DAYS=30` — `find -mtime +30 -delete`（依日期）
  2. `MAX_TOTAL_MB=10240` — 總量上限保護（2026-10-24 加入）：從最舊開始刪，直到總量 ≤ 10GiB。冪等，每次 cron 執行都收斂
- 為何需要第 2 層：`KEEP_DAYS` 只管天數不管總量。同一天可能有多份備份（cron 03:00 + 手動觸發），實測 2026-10-24 一天有 8 份。單份大小也會變動（922MB → 462MB）。只靠天數，總量會隨機漂移撐破上限
- 實測（2026-10-24 第十三 run 複核）：22 份 / **9.925 GiB**（10,656,542,804 bytes），涵蓋 10-12 ~ 10-24 連續 13 天
- 每日份數分佈（2026-10-24）：10-17 ~ 10-21 各 1 份、**10-22 有 4 份、10-23 有 2 份、10-24 有 8 份** → 總量逼近上限的主因是**同日多份**，不是 retention 故障
- 系統碟使用率 77%（404GB free）

### 排障：份數異常偏多

`find -mtime +30` 的 `+30` 是「嚴格大於 30 個 24h 週期」，不是日曆天。判斷 retention 是否正常，要看**最早那份的年齡**，不是看「清到哪天」：
- 若最早那份恰好 ≈30 天 → retention 正常，份數偏多的原因是**每日多份**
- 每日份數分布：`ls -1 hermes_*.tar.gz | sed -E 's/hermes_([0-9-]{10})_.*/\1/' | sort | uniq -c`

### 精確容量核算

`du -sh` 會因進位顯示為 11G。需用 bytes 精確核算：

```bash
find ~/Documents/Backup/hermes -maxdepth 1 -name "hermes_*.tar.gz" -printf '%s\n' | awk '{s+=$1} END {printf "%.3f GiB\n", s/1073741824}'
```

**注意**：用 `stat -c %s` 累加時，若中途改用 MB 單位換算（除以 1048576）會與 bytes 累加產生偏差，可能差 1 份。核算與刪除界線都用 bytes 為準。
