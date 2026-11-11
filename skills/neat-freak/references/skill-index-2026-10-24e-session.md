# neat-freak session — 2026-10-24e（cron `539040a91ad2`，第 11 run）

**Job:** Vault 整潔同步（neat-freak）· 5-Phase · cron `539040a91ad2`
**Result:** Vault 落後 origin 10 commits → pull 後完全同步；memory 鏡像一致；
canonical ↔ Agent repo `neat-freak` 雙軌 0 diff（內容層也 0 diff）；
`skill-index-check.py` ✓ ALL CLEAN（759）；cron output 全 < 500 門檻；
Hermes Backup 排程 03:01 自動執行（gzip -t OK）。
**本次新修兩處 canonical skill 自身的腐蝕**（Pattern GGG / HHH）——
都是「SKILL.md 是給未來 agent 的權威口徑，它錯了比 script 錯更危險」的典型。

## 各 Phase 結果

| Phase | 項目 | 結果 |
|---|---|---|
| 1 | Vault `git status` | 初跑 **落後 origin/main 10 commits**（fetch 後顯示 `[落後 10]`）→ `git pull --no-rebase origin main` → 同步 ✅ |
| 1 | Vault working tree | pull 後 clean，無 staged/unstaged ✅ |
| 1 | Vault stash | `git stash list` 空 ✅ |
| 1 | dangling objects | `git fsck --full` **完全無輸出**；`git count-objects -v` count=0 ✅ |
| 2 | memory 鏡像 | `diff -rq ~/.hermes/memory/ ~/Documents/Agent/memory/` → 零差異（P0/P1/P2 + handoffs 全 SAME）✅ |
| 3 | `sync-check.py` | ✓ CLEAN（references / scripts 結構、__pycache__ 皆無 drift）✅ |
| 3 | 內容一致性 | 逐檔 `diff` canonical ↔ workspace `references/` + `scripts/` → **0 diff**（先前腳本用 `$(dirname)` 拼出絕對路徑導致假 DIFF，已修正為相對路徑比對）✅ |
| 3 | `productivity/neat-freak` | 與 canonical `diff -rq` → 0 diff ✅（ambiguity 仍乾淨） |
| 3 | skills 全域交集 | canonical 897 / repo 1577 個 SKILL.md；同 relpath 交集 57，內容差異 **0** ✅ |
| 3 | `skill-index-check.py` | ✓ ALL CLEAN（759 = header = 8 sections，0 dangling，0 purpose corruption）✅ |
| 3 | **canonical skill 自身** | **發現 2 處腐蝕並修復**（見下）⚠️→✅ |
| 4 | cron output | 50 / 50 / 7 檔，全 < 500 門檻；`cron-output-cleanup.py` 移除 0 個 ✅ |
| 5 | Hermes Backup | cron `89c411611e6d`（每日 03:00）今日 03:01 自動執行；`gzip -t` 通過 ✅ |

## Pattern GGG：口徑 count regex 只認小寫開頭的 row

**觀察**：`skill-index-check.py` 報 `✓ ALL CLEAN`（759），但照 **SKILL.md 自己記載的**
「三口徑驗證命令」獨立重跑，得到 **749**，差 header 759 整整 10 個。

**根因**：SKILL.md 正文（Pattern OO / NN 兩節）記載的 regex 是
`re.match(r'^\| [a-z0-9]', l)` — 只認小寫/數字開頭。但 index 有 10 個 row
以大寫開頭：`Skill-Develop`、`Remotion`、`Scholar Evaluation`、
`Slide Deck (幻燈片簡報)`、`X-note`、`AutoIt v3`、`Paper-Read`、
`GordenImage2PPTX`、`GordenImagePPTGen`、`GordenSuperPPTSkill`。

**script 是對的**：`skill-index-check.py` 用 `^\| [^|]+\| [^\s|]+\.md\s+\|`，
不限定首字元 → 759 正確。壞掉的是 SKILL.md 正文。

**危險性**：未來 agent 照 SKILL.md 跑「獨立驗證」會得到 749 ≠ 759 的假 drift，
可能因此「修壞」一個其實乾淨的 index。SKILL.md 的權威性高於 script。

**修復**：SKILL.md 內 `^\| [a-z]` / `^\| [a-z0-9]` → `^\| [A-Za-z0-9]`。

## Pattern HHH：canonical skill 內的 macOS 絕對路徑在 Linux 機器上全部失效

**觀察**：`/Users/pigo/Documents/Agent/...` 散落在 canonical SKILL.md 與 5 個
references，共 21 處。這台機器是 Linux（`/home/x`），那些路徑不存在。

**受影響檔案**：`SKILL.md`、`skill-index-verification.md`、
`skill-index-corruption-patterns.md`、`skill-index-false-clean-pattern.md`、
`workspace-snapshot.md`、`skill-index-script-bugs-2026-07-13.md`。

**修復**：
- 敘述性路徑 → `~/Documents/Agent`
- **Python 片段 → `os.path.expanduser('~/Documents/Agent/...')`**
  （`~` 在 Python 字串裡不自動展開）

**踩到的坑**：批次 `str.replace("open('~/X'", "open(os.path.expanduser('~/X'")`
會留下不平衡括號 → 用 regex `open\(os\.path\.expanduser\('(~[^']*)'\)` 補收尾括號修復。

## 未處理（沿用既有裁決）

1. **Agent repo 93 commits ahead 未 push** — 3 個 ancestor commit
   （`b861b654` / `9477a6ae` / `18eb1284`）的 tree 含 live MiniMax key；
   HEAD tree 本身不含 key；remote 全部 9 個 refs 逐個掃描 = 0 命中 ✅。
   乾淨解法需 force-push rewrite（破壞性）或先 rotate key → 需 Pigo 口頭授權。
2. **canonical 897 vs repo 1577 個 SKILL.md** — 兩套命名空間（canonical 含
   category 目錄、repo 含 runtime-only skill），非 drift，沿 2026-10-23e 裁決維持不動。
3. **repo 根 `neat-freak/SKILL.md`（1424 行）是 workspace 內的舊副本**，
   與 `skills/neat-freak/SKILL.md`（1661 行）內容不同。git 有追蹤，
   但 Skill_Index 只列 `skills/neat-freak/SKILL.md`。屬「三軌」殘留 ——
   刪除或同步都需裁決，本 session 不動。
4. **Vault 備份 43 份 / 24G，磁碟 78%** — 30 天 retention 由 `hermes-backup.sh`
   自動處理，無 >30 天檔案。
5. **mojibake**：ftfy badness 全域掃描（排除 vendor / skill-backups / archive）
   = **0 hits** ✅。vendor 與 skill-backups 內仍有舊的雙重編碼檔案，
   屬外部 bundle / 封存備份，不動。

## 預防

- SKILL.md 記載的驗證命令與 script 的 regex 應定期對齊（SKILL.md 是權威口徑）
- canonical skill 內的路徑一律 `~` + `os.path.expanduser()`，不寫死家目錄
- 平台遷移時把 skill 內路徑納入 migration checklist
