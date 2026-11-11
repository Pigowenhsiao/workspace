# neat-freak session — 2026-10-24b（cron `539040a91ad2`，第 8 run）

**Job:** Vault 整潔同步（neat-freak）· 5-Phase · cron `539040a91ad2`
**Result:** Vault 完全乾淨且與 origin/main 同步（0/0）；canonical ↔ Agent repo 的
`neat-freak` 雙軌差距全數補齊（1 個 reference + SKILL.md 4 行索引）；memory 鏡像一致；
cron output 無需清理；Hermes Backup 已執行並驗證。

## 各 Phase 結果

| Phase | 項目 | 結果 |
|---|---|---|
| 1 | Vault `git status` | working tree clean，無 staged/unstaged 變更 |
| 1 | Vault 同步狀態 | `origin/main...HEAD` = 0 / 0（已同步，無 ahead/behind） |
| 1 | Vault stash | `git stash list` 空 ✅ |
| 1 | dangling objects | `git fsck` → 4 個 dangling **tree**、**0 dangling commit / blob**（無害殘留） |
| 2 | memory 鏡像 | `diff -rq ~/.hermes/memory/ ~/Documents/Agent/memory/` → 零差異（P0/P1/P2 三檔 md5 全 SAME） |
| 3 | canonical ↔ workspace 結構 | `sync-check.py` 初跑 DRIFT：`references/skill-index-2026-10-24a-session.md` MISSING → restore 後 **CLEAN** |
| 3 | canonical ↔ workspace 內容 | 逐一 diff：除上述 reference 外全部一致；`SKILL.md` 少 4 行「附：2026-10-24 第七 run 新增參考」→ 以 canonical 覆蓋 |
| 3 | skills 鏡像總計 | canonical `SKILL.md` 1,104 / repo 1,607；**同 relpath 交集 57**，內容差異僅 `neat-freak` 1 個（已修）→ 修後 0 |
| 3 | `skill-index-check.py` | ✓ ALL CLEAN（759 = header = 8 sections，0 dangling，0 purpose corruption） |
| 4 | cron output | 50 / 50 / 7 檔（+ 6 個 legacy `.txt`），全 < 500 門檻，**無需清理** ✅ |
| 5 | Hermes Backup | cron `89c411611e6d`（每日 03:00）今日已自動執行；另手動 `hermes-backup.sh` → `hermes_2026-10-24_030101.tar.gz`（463M），gzip -t OK ✅ |

## Pattern AAA：雙軌差距會同時出現在「檔案」與「索引行」兩層

**觀察**：canonical `SKILL.md` 已加入指向 `references/skill-index-2026-10-24a-session.md` 的
索引行（4 行），但 workspace copy 兩者都缺：
- `references/skill-index-2026-10-24a-session.md` 本身 MISSING
- `SKILL.md` 的索引行也 MISSING

**為什麼舊檢查抓不到**：`sync-check.py` 只比對**檔案存在性**，不管 `SKILL.md` 內容。
所以即使 restore 了 reference 檔，`SKILL.md` 仍落後——兩層都要獨立比對。

**偵測法**（可靠）：
```bash
# 層 1：檔案存在性
python3 ~/.hermes/skills/neat-freak/scripts/sync-check.py
# 層 2：內容（含 SKILL.md 本體）
diff ~/.hermes/skills/neat-freak/SKILL.md ~/Documents/Agent/skills/neat-freak/SKILL.md
```

**修復順序**：先 restore reference 檔（skill 明確宣告的 linked_file 契約），
再以 canonical 覆蓋 workspace `SKILL.md`（canonical 是唯一來源）。

**預防**：任何「新增 reference + 更新索引」的操作，restore 時必須兩層一起做，
否則 workspace 會有 dead link。

## Pattern AAAA：Agent repo 89 commits ahead 是「不可 push」狀態，不是待清理積壓

**觀察**：`~/Documents/Agent` 相對 `origin/main` = **ahead 89 / behind 0**，
`git push` 是 fast-forward。看起來像 Pattern U 說的「口徑修正類 commit 應立即 push」，
但**這 89 個 local-only commit 的 tree 全部含硬編碼 MiniMax live API key**。

**驗證（關鍵）**：
```bash
KEY=$(grep -m1 "^MINIMAX_API_KEY=" ~/Documents/.env | cut -d= -f2- | tr -d '"'"'"' \r\n')
git grep -l -F -- "$KEY" 26fb59a2        # → 4 個 x-note rewrite 腳本命中
git log --oneline -S"$KEY" origin/main   # → 空（remote 乾淨）
git grep -l -F -- "$KEY" origin/main     # → 空（remote tip tree 乾淨）
```

**結論**：remote 的**所有 refs** 都不含 live key（逐 ref 掃過，0 命中），
但 local 的歷史帶著它。`git push` 會把這些 ancestor 物件一併上傳 → live key 進入遠端歷史。

**處置**：`git push` **不執行**，維持 local-only。remote 端保持乾淨是當前最高優先級。
本次新增的 commit（restore reference + SKILL.md 同步）一律留在 local。

**注意取 key 的方式**：`.env` 裡 `MINIMAX_API_KEY` 有**兩行**（一行生效、一行註解），
必須 `grep -m1` 取第一行再 `tr -d '"'` 去引號，否則會取到
「兩行串接 + 引號」的 251 字元雜訊，導致 `-S` 搜尋結果失真。

## 未處理（需人工裁決）

1. **Agent repo 89 commits ahead 未 push** — 見 Pattern AAAA，push 會洩漏 live key。
   乾淨解法需要 **force-push rewrite**（破壞性）或先 rotate key，兩者都需 Pigo 明確授權。
2. **remote 歷史不含 live key** — 已用兩種口徑交叉驗證：
   - `git log --oneline -S"$LIVE_KEY" origin/main` → **空**（歷史無 live key）
   - `git log --oneline -S"sk-cp-" origin/main` → 3 筆，但內容僅是 `sk-cp-` 字面前綴
     （`d037c331` 等），**無完整憑證**
   - 逐 remote ref 掃描（`refs/remotes/*` 全 9 個）→ 全部 0 命中

   → remote 端目前是乾淨的，**風險不在遠端而在 local-only commits**（見 Pattern AAAA）。
3. **canonical 269 vs repo 471 top-level skills** — 兩套命名空間（canonical 含 category 目錄、
   repo 含 runtime-only skill），非 drift，沿用 2026-10-23e 裁決維持不動。
