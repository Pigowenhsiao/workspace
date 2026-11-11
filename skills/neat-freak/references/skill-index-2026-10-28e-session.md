# neat-freak session — 2026-10-28 (第十八 run)

## 摘要

本次跑 5 Phase。Vault 大幅路徑重整（Daily→07-Daily、transcripts→09-Article-Notes、
vault-weekly→12-Meta/Vault-Weekly-Synthesis）共 83 檔，commit + push 成功。
Memory P0/P1/P2 byte-identical。Skill 三項 checker 全綠。
Cron output 各目錄 ≤50 檔（門檻 500）。備份重跑並驗證涵蓋。

**本次新發現的內容級 drift 類型**：canonical ↔ workspace 之間存在 **31 個檔案內容不同**，
其中只有 2 個能機械式單向同步，其餘 29 個是「雙向都有獨有內容」的真分歧。

## 新 Pattern：TTT — 內容分歧的「superset 測試」決定同步方向

### 觀察

`diff -rq` 只會給你「哪些檔案不同」，不會告訴你**該往哪個方向同步**。
本次 31 個分歧檔案中，mtime 與內容豐富度**方向相反**的有 5 個
（`x-note/bin/config_loader.py` canonical 新但 workspace 較完整、
`Article-writer/references/*.md` workspace 新但 canonical 較完整）。

mtime 不是可靠的方向指標（Pattern SSS 已證 mtime 不可信）。

### 可靠的判定法：superset 測試

```python
# canonical 的每一個非空行，都出現在 workspace 裡？
cl = [l for l in canon_text.splitlines() if l.strip()]
wl = set(l for l in ws_text.splitlines() if l.strip())
is_superset = all(l in wl for l in cl)
```

- `is_superset == True` → workspace 是 canonical 的嚴格超集 → **安全可單向同步 workspace→canonical**
- `is_superset == False` 且反向也 False → **真分歧**，兩邊都有獨有內容 → 不可自動同步，需人工裁決

### 本次結果

**可安全同步（workspace→canonical）2 檔**：
- `x-note/bin/resolve_profile.py`（workspace 多了 anti-detection flags `--disable-blink-features=AutomationControlled`）
- `llm-wiki/references/pigo-note-format-notebooklm-chrome-plugins.md`（workspace 多了 Detailed Analysis / Why It Matters 段）

同步前已用 `tar -tzf <最新備份> <path>` 確認備份涵蓋該檔（P0 硬規則 1），
且過 `grep -E "sk-[A-Za-z0-9_-]{20,}"` 掃描無憑證外洩。

**真分歧待裁決 29 檔**（canonical 與 workspace 互有獨有內容）：
- `x-note/bin/` 8 檔（curator.py 差 462 行、write_to_inbox.py canonical 多 270 行 → 幾乎是兩個不同世代的實作）
- `x-note/references/` 8 檔、`x-note/scripts/x-note-playwright.py`
- `Article-writer/references/` 2 檔（canonical 較完整，workspace 是舊版）
- 各 skill 的 `Readme.md` 11 檔（canonical 是 Codex 目錄說明模板，workspace 是實際 skill 說明 → 兩者用途不同，非 drift）

**注意**：`Readme.md` 類的差異**不是 drift**——canonical 那份是
`<!-- BEGIN AGENT_DIRECTORY_README -->` 的自動生成目錄說明，
workspace 那份是 skill 自己的說明文件，兩者本來就該不同。硬同步反而會破壞語意。

### `x-note/config_loader.py` 是「平台遷移」而非「版本落後」

canonical 版讀 `~/.pi/agent/.path-config.json`（Ubuntu 主機實際存在），
workspace 版讀 `~/.codex/.path_config.jason`（Windows-only，本機不存在）。
→ 這是 2026-10-22 那次平台適應的產物，**兩邊都是對的，只是適用平台不同**。
不可合併、不可單向覆寫。

## Phase 3 的既有結論（不需重跑）

- `sync-check.py`：CLEAN
- `skill-index-check.py`：ALL CLEAN（760 rows = header = 8 sections，0 dangling）
- 磁碟 ↔ index 雙向比對：index 760 筆全在磁碟；磁碟多出的 17 筆全是
  `skills/agent-workflows/gstack/test/fixtures/` 與 `skills/nuwa-skill/examples/`
  → **測試 fixture 與範例，不是 active skill**，不應列進 index（Pattern QQQ）
- canonical 樹 name 衝突：93 個，全部是「多版本並存」型（0 個可 byte-identical 合併）→ 待裁決
- canonical 樹 851 skill / workspace 1578 skill；**canonical 少 205 個 skill 名**，
  這是組織方式差異（canonical 用分類子目錄、workspace 用另一套），既有結論不是 drift

## Vault 本次變更（Pattern 驗證）

- 83 檔：Daily→07-Daily、00-Inbox/transcripts→09-Article-Notes/transcripts、
  12-Meta/vault-weekly{,-synthesis}→12-Meta/Vault-Weekly-Synthesis
- 逐字稿與來源檔皆已確認搬遷後實體存在（`find` 逐一驗證），非刪除
- `git diff HEAD` 密鑰掃描：僅 slug 字串命中，無 live key
- push 被拒 → `git fetch` + `git merge --no-edit origin/main`（auto-sync commit）
  → 無 conflict → push 成功。**不要用 `git commit --amend`**
