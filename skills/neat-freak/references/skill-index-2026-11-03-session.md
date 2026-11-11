# neat-freak session — 2026-11-03（cron 紅燈診斷）

## 觸發

Pigo 回報 cron job `33f50df6ac6b`（Neat-freak 每日四次雙目標掃描）**連續失敗**。
最新 run `2026-11-03_02-00-40.md` 的失敗點是 `sync-check FAILED`。

## 歷史失敗形態（`~/.hermes/cron/output/33f50df6ac6b/`）

| 區間 | 狀態 | EXTRA 數 |
|------|------|---------|
| 2026-10-28 01–12 | ok | 0 |
| 2026-10-28 13 – 2026-10-30 08 | script failed | 5 |
| 2026-10-30 14 – 2026-10-31 20 | ok | 0 |
| 2026-11-01 02 – 2026-11-01 20 | script failed | 6 |
| 2026-11-02 02 – 2026-11-03 02 | script failed | 7 |

→ 紅燈與 `EXTRA in workspace` 數量同步遞增，典型「新增 session 產物沒回寫 canonical」特徵。

## 根因（兩層，疊加）

### 第一層：session 產物只寫 workspace，沒進 canonical（Pattern DDDD）

canonical `~/.hermes/skills/neat-freak/references/` 缺少 7 個 session reference：

```
skill-index-2026-10-28e-session.md
skill-index-2026-10-29-session.md
skill-index-2026-10-29b-session.md
skill-index-2026-10-29c-session.md
skill-index-2026-10-29d-session.md
skill-index-2026-10-29e-session.md
skill-index-2026-11-02-session.md
```

這些檔在 workspace（`~/Documents/Agent/skills/neat-freak/references/`）都在，
且已被 Agent repo commit（`578111e4c7`、`74149aae46`、`9b51f502ae`）——
**session 寫進 workspace 就收了工，沒有 copy 回 canonical**。

`sync-check.py` 掃到 workspace 多出這 7 個檔 → `EXTRA in workspace` → `RESULT: DRIFT DETECTED` → exit 1。

### 第二層：watchdog 的「雙目標」是假的（Pattern CCCC）

`~/.hermes/scripts/neat-freak-hourly.sh` 的 `check_target()` 以 argv 傳路徑：

```bash
python3 "$CANONICAL_SKILL/scripts/sync-check.py" "$path"
python3 "$CANONICAL_SKILL/scripts/skill-index-check.py" "$path"
```

但兩個 script **都不讀 argv**：

- `sync-check.py` 只讀 `WORKSPACE_DIR`（預設 `~/Documents/Agent/skills/neat-freak`）與 `WORKSPACE_ROOT`
- `skill-index-check.py` 只讀 `AGENT_ROOT`（預設 `~/Documents/Agent`）

→ 「Vault」與「Agent」兩輪跑的是同一份 Agent workspace。
證據：`/tmp/neat-freak-Vault.log` 與 `/tmp/neat-freak-Agent.log` **逐 byte 相同**（`diff` → "Files are identical"）。

而 Vault 實際上：
- 沒有 `skills/neat-freak/`
- 沒有 `docs/Skill_Index.md` / `docs/Skill_Category.md`
- 沒有 `neat-freak/SKILL.md` repo-root 副本

→ 對 Vault 跑 skill-index-check 從來就是無效操作，「雙目標掃描」只有一個目標真正被檢查。

### 第三層（隱藏）：過期副本 `productivity/neat-freak` 讓 skill 載入 ambiguous

`~/.hermes/skills/productivity/neat-freak/`（1,398 行，2026-10-30 09:12）與
canonical（2,504 行）同名 → `skill_view(name='neat-freak')` 回
`Ambiguous skill name 'neat-freak': 2 candidates`。

SKILL.md 第 32 行記載 2026-10-26 已移除此副本並備份至
`/home/x/.hermes/cache/scratch/removed_prod_neatfreek_20261026_2350`，
但它**又被重建回來**（該路徑是 v100 的 home，本機沒有 → 2026-10-26 的備份不在本機，
無法比對是誰重建的）。

**該副本內含一條 canonical 從未收錄的教學**（`EXTRA 的新成因：session 產物只寫 workspace、沒進 canonical`），
恰好就是本次根因 → 已於 2026-11-03 救回 canonical，寫成 Pattern DDDD。

## 修復動作

### 1. canonical 補齊（workspace 領先 → workspace→canonical）

方向依 SKILL.md 既有規則（2026-10-27b）：`'<'` 數與 mtime 實測決定。

- `SKILL.md`：canonical 2085 行 → workspace 2504 行（canonical 獨有 47 行全是**重複**的
  Pattern AB 段落，md5 確認兩處 `4821901a...` 完全相同 → workspace 是去重後的嚴格超集）
- `scripts/sync-check.py`、`scripts/skill-index-check.py`：workspace 版較新，
  多出 `repo_root_copy` 檢查（repo-root 副本第三次落後的解法）與 **content-consistency 檢查**
- `references/`：補 7 個 session reference + 4 個內容落後的 reference

4 個內容落後的 reference 差異確認（workspace 較新、為修正後版本）：

| 檔案 | 差異 |
|------|------|
| `hermes-backup-protocol.md` | workspace 補入 `.env` 備份覆蓋（只備 config 不備 .env → 還原後 bot 與 provider 全失效）與 tar basename 覆蓋陷阱 |
| `hermes-cron-jobs.md` | `/home/pigo/...` → `$HOME/...`（可攜） |
| `openclaw-exec-allowlist-fix.md` | 硬編碼絕對路徑 → `os.path.expanduser('~')` |
| `workspace-snapshot.md` | 修正「Agent.md 三檔永久刪除」的過期敘述（實為使用者刻意保留的孤兒，不得再刪） |

修完 `sync-check.py` 揭露第二層問題（content drift 4 檔）→ 補齊後 `RESULT: CLEAN` exit 0。

### 2. watchdog 改用 env 介面

`~/.hermes/scripts/neat-freak-hourly.sh` 重寫：

- `WORKSPACE_DIR=` + `WORKSPACE_ROOT=` → sync-check（只對 Agent workspace 做，語意正確）
- `AGENT_ROOT=` → skill-index-check（只對有 `docs/Skill_Index.md` 的 repo 做）
- Vault 目標改成「目錄存在 + git 狀態」（Vault 沒有 skill workspace 副本，跑 skill check 是無效操作）
- `set -euo pipefail` → `set -uo pipefail`（`-e` 會讓 `grep -q` 在無 match 時直接中止整支腳本）
- dangling 檢查關鍵字修正：舊版抓 `[1] Dangling references`，實際輸出是 `[3] Dangling references` → 舊版的精確檢查從未生效

### 3. 驗證

正向：
```
bash ~/.hermes/scripts/neat-freak-hourly.sh → exit 0
  ✅ sync-check OK / ✅ skill-index-check OK / Vault clean / Agent 41 筆未 commit（僅警告）
```

負向（**必須做，否則只是關掉警報**）：

| 注入 | 結果 |
|------|------|
| workspace 多一個 `references/__drift_probe.md` | exit 1，`❌ sync-check FAILED` ✓ |
| canonical `SKILL.md` 尾端加一行 | exit 1，`❌ sync-check FAILED` ✓ |
| 還原後 | exit 0 ✓ |

`skill-index-check.py` → `OVERALL: ✓ ALL CLEAN`（dangling ✓、header drift ✓、
API key subtotal 32/193/535 三口徑全對、Skill_Category total 581 一致）。

## 備份

- canonical 全量：`~/.hermes/cache/scratch/neat-freak-canonical-backup-20261103-064340/neat-freak/`
- watchdog：`~/.hermes/cache/scratch/neat-freak-hourly.sh.bak-*`

## 未解（需 Pigo 裁決）

- `~/.hermes/skills/productivity/neat-freak/` 過期副本仍在 → `skill_view(name='neat-freak')`
  仍回 ambiguous。該副本**獨有 66 行**（含本次救回的教學、Pattern W、Pattern AB 舊版）。
  依 2026-10-29 Pattern VVV 的三條件判斷法，category 化 richer 副本未必可安全刪。
  → 未擅自刪除；建議單獨 session 處理 93 個同名群組的整體清理。
- Agent repo 有 41 筆未 commit（`artifacts/*.json`），與本次修復無關，未動。
