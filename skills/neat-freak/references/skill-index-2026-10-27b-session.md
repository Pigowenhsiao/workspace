# neat-freak session — 2026-10-27（04:00 UTC daily run）

**Job:** cron `31f0439f-532f-4e3e-8e14-38d4a82aadd1`（neat-freak daily sync）
**Handover:** `memory/handoffs/neat-freak_2026-10-27.md`

---

## 核心發現：Phase 2 / Phase 3 的「事實來源」方向規則寫反了

SKILL.md 原本寫死「以 canonical（`~/.hermes/`）為準，單向同步到 workspace（`~/Documents/Agent/`）」。
本次實測**兩個方向都會造成內容回退**。

### 實測證據

| 對象 | canonical | workspace (Agent repo) | 真相 |
|---|---|---|---|
| `memory/P0-core.md` | 2026-10-26 16:12, 5,424 B | 2026-10-27 02:56, 6,503 B | **workspace 領先**（多 11 行 2026-10-27 修正） |
| `skills/neat-freak/SKILL.md` | 1,992 行 | 2,083 行 | **workspace 領先**（多 4 個 Pattern） |
| `references/` 清單 | 缺 1 檔 | 獨有 `skill-index-2026-10-27-session.md` | **workspace 領先** |
| `scripts/` 清單 | — | — | 雙向無獨有檔案 |

`diff canonical workspace | grep -c '^<'` = **0** → workspace 為 canonical 的**嚴格超集**。
照原規則單向覆寫會：
- 把 P0 記憶的「push 禁令理由已失效（2026-10-27 修正）」倒回舊版
- 刪掉 Pattern OOO-2 / LL-2 / FFF-2 / QQQ-2 四個新 Pattern

**處置**：依 superset 判斷，實際套用 **workspace → canonical**（反向），兩邊 byte-identical。

### 為什麼兩側會輪流領先

canonical 樹（`~/.hermes/`）**不在 git 版控下**，每次 session 對它的寫入都是無痕的；
workspace 樹（`~/Documents/Agent/`）在 git 內，會被 commit 並 push。
任何在 workspace 側完成的修正（記憶、安全定案、Pattern 記錄）**不會自動回流 canonical**，
下一輪 neat-freak 若照「canonical 為準」執行就會回退。

2026-10-26 那次是 canonical 領先（repo 落後 17 行安全定案段落），2026-10-27 是 workspace 領先
→ **方向不是常數，必須每次實測**。

### 新規則（已寫入 skill proposal）

```
diff <canonical> <workspace> | grep -c '^<'
  0        → workspace 為嚴格超集 → 由 workspace → canonical 同步
  >0 且 >0 → 兩側各有獨有內容 → 停止覆寫，回報 + 交接
  皆 0      → 內容實質相同 → 走 trailing newline 對齊
```
並以 `stat -c '%y %s %n'` 的 mtime 作第二重佐證。

---

## 附帶解掉：每小時健康度 job `33f50df6ac6b` 長期紅燈

- 症狀：`Neat-freak 每小時雙目標掃描` 每小時 exit 1，`last_error` 報
  `EXTRA in workspace (1): + references/skill-index-2026-10-27-session.md`
- 真因：那個檔案是 **workspace 領先的新增**，canonical 尚未收錄；`sync-check.py` 的 EXTRA
  規則把「污染」與「領先」混為一談
- 處置：把該 reference 補進 canonical → `sync-check.py` = **CLEAN** → 每小時 job = **exit 0** ✅
- 教訓：`sync-check.py` 的 EXTRA 有兩義性，**不可直接當污染處理**；先看該檔 mtime 與內容性質

---

## 其他本次觀察

- **Agent repo dangling objects**：19 個（7 dangling commit + 12 dangling tree）。
  `git gc --prune=now` 後 → 0（`count-objects -v` = `count: 0`）。
  **未用 `--aggressive`**：`.git` 已 868M（size-pack 802MiB），aggressive 會做完整 repack。
  日常只需 `reflog expire --expire=now --all` + `git gc --prune=now`（`references/dangling-objects.md` 已載明）。
- **無未完成 rebase**：`.git/rebase-merge` / `rebase-apply` / `MERGE_HEAD` 皆不存在 → 無 Pattern LL-2 殘留。
- **`stash@{0}` 已消失**：10-26 handoff 記載的 `WIP on main: 6411d01786 Weekly defrag sync 2026-10-11`
  本次 `git stash list` = 0 筆 → 該 Decision 項已過期。
- **Cron output**：執行 always-on 的 `cron-output-cleanup.py` → 移除 9 檔（9 個 job 目錄各 1 檔）。
  任一 job 目錄均未達 500 檔門檻（最大 50）。
- **Hermes 備份**：`20261027_040939`（2.0G），prune `20261015_160259`，保留 14 份。
- **Vault 在 run 期間被併發 news job 寫入**：`00-Inbox/2026-10-27_News-Update-Noon.md` +
  commit `968393d71`，隨後該 job 自行 push → 複驗時 vault 已回到 0 ahead / 0 behind。
- **5 個 enabled cron job 非 ok**（延續 10-26）：4 個 `HTTP 429 Token Plan usage limit reached`
  （MiniMax 額度耗盡）、1 個 `delivery_failed`（每週更新 superpowers + GSD + gstack）。
- **OpenClaw workspace repo** 仍有未追蹤項（`make_note_1.py`、`memory/handovers/` 3 檔拼字錯誤目錄），
  與 10-24 run 同一未解現象 → **維持不動**，留待人工裁決。

---

## 本次未做（需授權）

- 未 force-push、未改寫任何 git 歷史
- 未刪除任何 vault 資料（全程零刪除）
- 未執行任何 push（兩 repo 皆 0 ahead）
- 未套用 pending skill 提案（`neat-freak-20261026-3affa47764` 已修訂，含本次方向規則，仍待審查）
