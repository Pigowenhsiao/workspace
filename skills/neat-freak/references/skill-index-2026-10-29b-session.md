# neat-freak session — 2026-10-29 第二 run（第二十 run）

**Job:** `539040a91ad2`（Vault 整潔同步 / neat-freak，每 120 分鐘）
**Run time:** 2026-10-29 03:30–03:45 CST
**結果:** 五 Phase 全執行；發現並修復 **backup script 遺漏所有 `.env` 憑證檔**（新 Pattern WWW）；repo 根 `neat-freak/SKILL.md` 再次落後 canonical（Pattern 舊坑復現）；memory 雙軌補 6 檔後 byte-identical；Vault dangling 全清。

---

## Phase 1 — Vault Git Health

| 項目 | 結果 |
|---|---|
| `git status --short` | 0 檔（工作樹乾淨，無需 commit） |
| branch 狀態 | `main`，與 `origin/main` **完全同步**（0 ahead / 0 behind） |
| `git stash list` | 空 |
| rebase 殘留 | 無（`.git/rebase-merge` 不存在，Pattern LL-2 未復發） |
| dangling objects | `count-objects -v` 顯示 `count: 218` loose → 跑 `git reflog expire --expire=now --all` + `git gc --prune=now` → `count: 0`、`fsck --full` **完全無輸出** ✅ |

Vault HEAD = `a7ab6477c chore(vault): fix frontmatter YAML quoting in 60 files`（上次 run 的 Pattern UUU 產物，已 push）。

## Phase 2 — Memory Sync

- `P0-core.md` / `P1-90days.md` / `P2-30days.md`：**三檔 byte-identical**（兩樹 `diff` 無輸出）✅
- handoffs：44 檔檔名清單一致、內容無差異 ✅
- **差異只在 `memory/dreaming/` 與 `memory/.dreams/`**（canonical 多 4 + 2 檔，2026-10-28/29 dreaming 產物 + session-corpus）
  → 依「以 `~/.hermes/memory/` 為準」規則 **canonical → workspace 單向補齊 6 檔**
  → 補完後 `diff -rq` **兩樹完全無輸出** ✅
- 注意：這兩個目錄在 Agent repo `.gitignore`（`memory/dreaming/`、`memory/.dreams/`）→ 補齊檔案不會進 git，只影響工作樹一致性。

## Phase 3 — Skills Consistency

| 檢查 | 結果 |
|---|---|
| `sync-check.py` | `RESULT: CLEAN`（references 90/90、scripts 無 drift、無 `__pycache__`）✅ |
| `skill-index-check.py` | `✓ ALL CLEAN`（actual 760 = Summary 760 = 8 sections 全對、0 dangling、0 purpose cell 腐蝕）✅ |
| **Index ↔ 磁碟雙向比對**（Pattern QQQ-2） | listed 760 = disk active 760，兩邊差集皆 **0** ✅ |
| **purpose cell ↔ frontmatter 語意比對**（Pattern RRR） | 760 rows、**mismatches = 0** ✅ |
| canonical 樹 frontmatter（`parse_frontmatter`） | 850 SKILL.md、**no-frontmatter = 0** ✅ |
| workspace 樹 frontmatter | 1,578 SKILL.md、**no-frontmatter = 0** ✅ |
| canonical 樹同名群組 | 92 組，套用 SSS 三條件安全刪除檢查 → **SAFE-to-delete = 0**（Pattern VVV 再次確認：可安全刪數很小是常態） |
| 同相對路徑內容比對 | 370 組共有路徑中 **29 組內容不同** → 全部 **DIVERGE**（雙向都有獨有內容）→ 不可自動同步，留待人工裁決（與 2026-10-28 第十八 run 同一批 29 檔，狀態未變） |

### 修復：repo 根 `neat-freak/SKILL.md` 再次落後 canonical

- 症狀：`~/Documents/Agent/neat-freak/SKILL.md` 2,143 行 vs canonical 2,278 行
- superset 測試：canonical **是** workspace 的嚴格超集（`ws->canon: True`）→ 單向 canonical → workspace 安全
- 動作：`cp ~/.hermes/skills/neat-freak/SKILL.md ~/Documents/Agent/neat-freak/SKILL.md`
- 驗證：`cmp` 三方（canonical / `skills/neat-freak/` / repo 根）**byte-identical** ✅
- **教訓復現**：`sync-check.py` 只比 canonical vs `skills/neat-freak/`，**不涵蓋 repo 根副本**。這是第二次因同一原因落後（上一次 2026-10-24 修過，10-28 又落後）。
  → 下次同步必做 `diff -rq neat-freak/ skills/neat-freak/`。

## Phase 4 — Cron Output Retention

- 各 job 目錄檔案數：50 / 50 / 50 / 8（全部 < 500 門檻；且 Hermes 內建 `cron.output_retention: 50` 已自動修剪到 50 上限）
- 總量 6.2 MB << 1 GB 門檻
- 7 天以上舊檔：2 個 → 已刪（`89c411611e6d/2026-10-22_03-00-33.md`、`539040a91ad2_20261021_192400.txt`）
- 22 個散落在 `cron/output/` 根目錄的 legacy `*.txt`（舊 flat 命名格式）→ 全在 7 天內，未動

## Phase 5 — Hermes Backup

- 排程存在（cron `89c411611e6d`，`0 3 * * *`，`no_agent (script)`），今日 03:00 已自動跑過（`last_status: ok`）
- 本 run 手動重跑一次以驗證新 script：`hermes_2026-10-29_033618.tar.gz`（464M）
- `gzip -t` → **GZIP_OK** ✅
- tarball 內容抽查：`./config.yaml`、`./AGENTS.md`、`./auth.json`、`./kanban.db` ✅；`./cron/` 206 檔
- 總量 9.952 GiB / 22 份（≤ 10 GiB 上限，機制正常）

---

## Pattern WWW（2026-10-29 第二 run 新發現）：backup script 遺漏所有 `.env` 憑證檔

### 觀察

`~/.hermes/scripts/hermes-backup.sh` 的 `ITEMS` 陣列備份了 `config.yaml`、`auth.json`、`credentials/`，
但**沒有備份任何 `.env`**：

```
ITEMS=(config.yaml AGENTS.md auth.json credentials skills memories plugins cron memory kanban.db)
```

實測磁碟上的憑證分佈：

| 檔案 | 內容 | 在 backup？ |
|---|---|---|
| `~/.hermes/.env` | `TELEGRAM_BOT_TOKEN`、`TELEGRAM_ALLOWED_USERS`、`GATEWAY_ALLOW_ALL_USERS` | ❌ |
| `~/.hermes/profiles/analysis/.env` | `MINIMAX_API_KEY`、`STRATA_API_KEY` | ❌ |
| `~/.hermes/profiles/strata/.env` | `STRATA_API_KEY` | ❌ |
| `~/.hermes/config.yaml` | `strata-iq3` / `strata-q4` 的 `api_key`（硬編碼） | ✅ |

`config.yaml` 裡 provider 宣告 `key_env: MINIMAX_API_KEY` — 指的是**環境變數名**，
而環境變數的**實際值來源**是 `~/.hermes/profiles/analysis/.env`。
備份了 config 卻沒備份 .env = **還原後 Telegram bot 完全失效、minimax/strata provider 拿不到 key**。

### 為什麼舊檢查抓不到

- `tar -tzf` 抽查只查「關鍵檔案在不在」→ config.yaml 在，就回報 ✅
- Hermes 內建 `hermes_cli/backup.py` 的 `_SECRET_FILE_NAMES = {".env", "auth.json", ...}`
  把 `.env` 視為**刻意排除**的 secret → 那是 Hermes 自家 backup 的策略，
  但本機的 `hermes-backup.sh` 是**自製腳本**，兩套策略不一致且互相不感知
- `hermes-backup-protocol.md` 的「備份範圍」表格列了 10 項 `ITEMS`，
  **照著文件讀的人不會知道 `.env` 缺席**——文件描述的就是腳本的實際內容，兩者一致，但都錯

### 修復

1. `ITEMS` 加 `"$HOME/.hermes/.env"`
2. profile 內的 `.env` 走新的 `EXTRA_ITEMS`（保留相對路徑）

**關鍵陷阱 — 多個同名 `.env` 會互相覆蓋**：
原本的複製邏輯是 `tar -C "$(dirname "$item")" "$(basename "$item")"` → **只取 basename 平鋪到 backup 根**。
若直接把 `profiles/analysis/.env` 和 `profiles/strata/.env` 加進 `ITEMS`，
兩者都會被寫成 `$BACKUP_DIR/.env` → 後者覆蓋前者 → **只留一份 key**。
因此必須另走保留相對路徑的路徑：

```bash
EXTRA_ITEMS=(
    "profiles/analysis/.env"
    "profiles/strata/.env"
)
for rel in "${EXTRA_ITEMS[@]}"; do
    if [ -e "$HOME/.hermes/$rel" ]; then
        mkdir -p "$BACKUP_DIR/$(dirname "$rel")"
        tar -cf - -C "$HOME/.hermes" --ignore-failed-read "$rel" 2>/dev/null \
            | tar -xf - -C "$BACKUP_DIR" 2>/dev/null
        if [ ${PIPESTATUS[0]} -ne 0 ]; then
            echo "[WARN] 複製失敗: $rel"
            FAILED=1
        fi
    fi
done
```

### 驗證

`tar -tzf` 確認三個 .env 都在且路徑不重疊：

```
./.env
./profiles/analysis/.env
./profiles/strata/.env
```

### 預防

1. **備份清單要從「憑證實際存放位置」反推，不能只看 config 宣告**：
   `key_env: X` → 找哪個 `.env` 真的定義了 `X`
2. **tar 平鋪 basename 的副作用**：任何同名的第二層檔案都會覆蓋第一層 → 必須保留相對路徑
3. 備份腳本改動後**立刻手動重跑 + `tar -tzf` 抽查**，不要等隔天 cron
4. 兩套 backup 策略（Hermes 內建 vs 自製腳本）不一致時，**以自製腳本為準並同步更新 protocol 文件**

---

## 本 run 未處理（需人工裁決）

1. **canonical ↔ workspace 29 檔真分歧** — 兩邊各有獨有內容，不可自動覆寫。
   `x-note/bin|references|scripts` 17 檔（Windows↔Ubuntu 平台遷移，兩邊都對）、
   `Article-writer/references` 2 檔、各 skill `Readme.md` 11 檔（Codex 自動生成目錄說明 vs skill 自身說明，用途不同）
2. **canonical 樹 92 組同名 skill** — 巢狀自我複本 / category 化 richer 副本 / 上游 bundle vs 本地 fork，三類都是「兩邊都對」，刪任一邊都會丟資訊
3. **Agent repo `docs/STATUS_ALL.md` 含硬編碼 api_key 前綴**（第 967 行 `FqHksK6…(redacted)…`，僅前綴、值不完整）→ 是否輪換該 key 需 Pigo 決定

## 第二 run 追加：憑證檔不只在 `~/.hermes/`

追查「`.env` 到底在哪裡」時發現 **`~/Documents/.env`** 也是憑證來源，
且**位於 `.hermes` tree 之外**，同樣沒被備份。內容（變數名，值不列出）：
`MINIMAX_API_KEY`、`STRATA_API_KEY`、`GITHUB_TOKEN`、`HF_TOKEN`、`BRAVE_API_KEY`、
`TWITTER_NAME` / `TWITTER_AUTH_TOKEN` / `TWITTER_CT0`、`OPENROUTER_API_KEY`、
`DEEPSEEK_API_KEY`、`TYPESAVE_AI_API_KEY`、`INKBOX_API_KEY` / `INBOX_API_KEY`。

→ `EXTRA_ITEMS` 格式改為 `<來源絕對路徑>::<backup 內相對路徑>`，
同時解決「同名不同路徑互相覆蓋」與「來源在 tree 外」兩個問題。

最終 tarball 內四個憑證檔並存（`tar -tzf` 驗證）：
`./.env`、`./profiles/analysis/.env`、`./profiles/strata/.env`、`./Documents/.env` ✅

四個檔案權限皆 600 ✅

備份總量因新增項目觸發上限清理：11,172,420,427 bytes > 10,240 MB → 刪最舊一份
（`hermes_2026-10-24_030101.tar.gz`），餘 22 份。

## 機械式修正清單

- ✅ `~/.hermes/scripts/hermes-backup.sh`：`ITEMS` 加 `~/.hermes/.env`；新增 `EXTRA_ITEMS` 保留相對路徑的 profile `.env`
- ✅ `~/Documents/Agent/neat-freak/SKILL.md`：canonical → workspace 單向同步，三方 byte-identical
- ✅ `~/Documents/Agent/memory/`：補 6 檔（4 dreaming + 2 session-corpus）→ 兩樹 byte-identical
- ✅ cron output：刪 2 個 >7 天舊檔
- ✅ Vault：dangling 清理（`count: 218 → 0`）
