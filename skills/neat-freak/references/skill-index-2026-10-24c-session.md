# neat-freak session — 2026-10-24c（cron `539040a91ad2`，第 9 run）

**Job:** Vault 整潔同步（neat-freak）· 5-Phase · cron `539040a91ad2`
**Result:** Vault 完全乾淨且與 origin/main 同步（0/0）；`~/.hermes/memory/` ↔ Agent repo
memory 鏡像補齊 1 檔；canonical ↔ Agent repo `neat-freak` 雙軌一致（0 diff）；
**`productivity/neat-freak` 雙軌分歧已修**（導致 cron skill 載入 ambiguous 警告）；
cron output 無需清理；Hermes Backup 已排程且今日已執行並驗證。

## 各 Phase 結果

| Phase | 項目 | 結果 |
|---|---|---|
| 1 | Vault `git status` | working tree clean，無 staged/unstaged 變更 |
| 1 | Vault 同步狀態 | `origin/main...HEAD` = 0 / 0（fetch 後確認） |
| 1 | Vault stash | `git stash list` 空 ✅ |
| 1 | dangling objects | `git fsck` → 4 個 dangling **tree**、0 dangling commit/blob；`fsck --strict` 僅同一批 tree；exit 0 |
| 1 | Vault `git fsck --unreachable` | 125 筆「無法取得」→ 這是 `fsck --unreachable` 對 dangling tree 的**子物件列舉**（tree 的 blob 已被 gc），非 repo 損毀；`git cat-file -t` 逐一驗證物件皆可讀 |
| 2 | memory 鏡像 | 差 1 檔：`~/.hermes/memory/dreaming/rem/2026-10-24.md`（hermes 端今日 03:00 dreaming 產出）→ 已複製到 Agent repo，重跑 `diff -rq` = 0 |
| 2 | P0/P1/P2 三檔 | md5 與內容皆完全一致 ✅ |
| 3 | canonical ↔ Agent repo `neat-freak` | `sync-check.py` = CLEAN；references / scripts / SKILL.md 逐一 diff = 0 diff；skills 全域交集 57 檔內容 diff = 0 |
| 3 | canonical ↔ **productivity/neat-freak** | **原先分歧**（SKILL.md 落後 3 個 reference + 4 行索引）→ 已以 canonical 覆蓋，現 `diff -rq` = 0 |
| 3 | `skill-index-check.py` | ✓ ALL CLEAN（759 = header，0 dangling，0 purpose corruption） |
| 4 | cron output | 50 / 50 / 8 檔（+ 7 個 legacy `.txt`），全 < 500 門檻，**無需清理** ✅ |
| 5 | Hermes Backup | cron `89c411611e6d`（每日 03:00）今日已自動執行；`hermes_2026-10-24_030034.tar.gz`（484MB）gzip -t OK，25,091 entries，含 memory/skills/cron ✅ |

## Pattern BBB：skill 名稱在「同名不同內容」時會被 loader 拒絕載入（ambiguous ≠ 載入失敗的兩種狀態）

**觀察**：本次 cron job 的 skill 預載入報錯：

```
⚠️ Skill(s) not found and skipped: Ambiguous skill name neat-freak: use one of productivity/neat-freak
```

但 `~/.hermes/skills/` 下**兩個** neat-freak 都存在且內容幾乎相同：

| 路徑 | SKILL.md | references |
|---|---|---|
| `~/.hermes/skills/neat-freak/`（canonical） | 110,941 bytes | 75 |
| `~/.hermes/skills/productivity/neat-freak/` | 104,785 bytes | 72 |

**機制**（`agent/skill_utils.py`）：
- `provably_same_skill()` 只在**所有**候選 SKILL.md 的 sha256 **完全相同**時才視為同一個 skill
- 兩份內容不同 → `pick_skill_candidate()` 回傳 `None` → catalog status = `ambiguous`
- cron 的 skill 預載入遇到 ambiguous 直接 **skip**，job 照跑但 skill 沒載入

**關鍵**：這不是「skill 不存在」，而是**同名但內容分歧**。若只把兩個目錄都擺在那不處理，
每次 cron 都會被 skip，且 SKILL.md 越改越多、兩邊分歧越大。

**驗證（修復後）**：
```python
from agent import skill_utils
# 用 get_skill_search_roots() + resolve_skill_catalog() 重跑
# → tier 1 neat-freak              status=unique    load_name=neat-freak
# → tier 1 productivity/neat-freak  status=shadowed  load_name=None
```
canonical（淺層）勝出、另一份被 shadowed，ambiguity 消失。

**修復**：
```bash
cp -f ~/.hermes/skills/neat-freak/SKILL.md ~/.hermes/skills/productivity/neat-freak/SKILL.md
cp -f ~/.hermes/skills/neat-freak/references/*.md ~/.hermes/skills/productivity/neat-freak/references/
diff -rq ~/.hermes/skills/neat-freak/ ~/.hermes/skills/productivity/neat-freak/   # → 無輸出
```
`cp -f` 覆寫後兩份 sha256 相同 → `provably_same_skill()` 成立 → 不再 ambiguous。

**預防**：
- **任何 skill 的第二份副本（category 目錄下 vs 頂層）必須與 canonical 保持 byte-identical**
- 只靠 `sync-check.py` 檢查 canonical ↔ **Agent repo** 不夠——它完全不檢查 `~/.hermes/skills/` 內部的
  同名雙軌（canonical vs productivity/）
- 偵測方式（比 loader 更早）：
  ```bash
  # 找出 ~/.hermes/skills/ 下所有同名 skill
  find ~/.hermes/skills -name SKILL.md -exec grep -l '^name:' {} \; | \
    xargs -I{} sh -c 'grep -m1 "^name:" "{}"' | sort | uniq -d
  ```
  然後對每組同名逐一比對 sha256，不一致即為「ambiguous 來源」
- 另一種確認法（loader 層級，最權威）：
  ```python
  from agent import skill_utils
  # 組出 entries 後呼叫 resolve_skill_catalog()，看 status 是否為 'ambiguous'
  ```

## Pattern CCC：`git fsck --unreachable` 的「無法取得」不等於 repo 損毀

**觀察**：`git fsck --unreachable` 對 Vault 報 125 筆「無法取得（missing）」tree/blob，
看起來像嚴重損毀。但：

- `git fsck`（無參數）exit code = 0，只列 4 個 dangling tree
- `git fsck --strict` 同樣只列那 4 個 dangling tree
- 對報出的物件逐一 `git cat-file -t` → **全部可讀**（tree / blob 正常）
- `git rev-list --objects HEAD` 的 51,490 個物件 → `cat-file --batch-check` 全部命中

**機制**：`--unreachable` 會**遞迴列舉 dangling tree 的子物件**。dangling tree 本身可讀，
但它底下的 blob 已被 `git gc` 回收 → 報「無法取得」。這是 dangling tree 的**正常後果**，
不是 repo 損毀。

**驗證速查（三口徑）**：
```bash
git fsck --no-progress            # exit code 0 = 健康；只看 dangling 類型
git cat-file -t <sha>             # 逐一驗證報出的物件確實可讀
git rev-list --objects HEAD | git cat-file --batch-check | grep -c missing   # 0 = HEAD 完整
```

**預防**：報告 dangling objects 時**不要**直接引用 `--unreachable` 的行數當作損毀規模。
用 `--no-progress` 的 exit code + `cat-file` 交叉驗證，結論才是可靠的。

## Pattern DDD：Scratch 目錄裡的 git worktree 會持有 vault 的 dangling objects 與未追蹤內容

**觀察**：`~/Documents/Pigo_Obsidian/.git/worktrees/mtest` 存在一個 linked worktree，
實際路徑在 `~/.hermes/cache/scratch/mtest`（scratch 為暫存區，24h idle 會被清）。

- worktree HEAD `0374e373e` **不是** main 的 ancestor（分支過期的實驗分支）
- index 內有 **467 個 staged 變更**（22,395 insertions）
- 工作樹有 **150 個 .md 檔**在 main vault 中不存在

**內容判定（重要）**：這 150 檔並非遺失資料，而是**分類搬移前的舊位置**。
以 `2026-10-23_arXiv_DONIC` 為例：
- mtest：`00-Inbox/2026-10-23_arXiv_DONIC_...md`，`tags: [paper, arXiv, hf-daily]`（未引號）
- origin/main：`10-LLM-Wiki/AI-News/2026-10-23_arXiv_DONIC_...md`，`tags: ["paper", "arxiv", "hf-daily"]`（已引號+小寫）

→ 同一篇筆記，mtest 是**批次改寫前**的快照，main 是改寫後的版本。mtest 內容是 main 的**過時前驅**，不是 main 缺漏。

**教訓**：
1. `git worktree list` 裡出現指向 scratch 目錄的 worktree → 是**臨時實驗殘留**，不是 vault 的真實分支
2. 比對「worktree 獨有檔案」時，**必須比對 blob hash 與內容**，不能只看路徑 basename——
   否則會把「改寫前舊版」誤報成「資料遺失」
3. 判定口徑：
   ```bash
   # 1. worktree 獨有檔案的 blob 是否存在於 origin/main
   git -C <worktree> hash-object --stdin-paths < filelist
   git -C <vault> ls-tree -r origin/main   # 取全部 blob hash 做集合比對
   # 2. 若 blob 不在 origin/main，再 diff 內容看是「舊版」還是「真的獨有」
   ```
4. **不要**因為 worktree 有 467 staged 變更就把它 commit 或 push 到 origin/main——
   那是過期實驗分支，會污染 main

## 各 Phase 實際執行的變更

| 檔案 | 變更 | 原因 |
|---|---|---|
| `~/Documents/Agent/memory/dreaming/rem/2026-10-24.md` | 新增（複製自 `~/.hermes/memory/`） | memory 鏡像補齊（該路徑被 Agent repo `.gitignore:56 memory/dreaming/` 排除，不進 git，僅磁碟鏡像） |
| `~/.hermes/skills/productivity/neat-freak/SKILL.md` | 以 canonical 覆蓋 | 消除 cron skill ambiguous skip（Pattern BBB） |
| `~/.hermes/skills/productivity/neat-freak/references/*.md` | 以 canonical 覆蓋 + 補 3 檔 | 同上；canonical 多出的 3 個 session reference 一併補齊 |

## 未處理（需人工裁決）

1. **Agent repo 91 commits ahead 未 push** — 延續 Pattern AAAA：local-only commits
   `18eb1284` / `9477a6ae` / `b861b654` 歷史含 live MiniMax API key，
   `git grep -F "$KEY" origin/main` = 0 命中、remote 歷史 = 0 命中，**遠端乾淨**。
   push 會把 key 的 ancestor 物件一併上傳 → 不執行。乾淨解法需 force-push rewrite（破壞性）
   或先 rotate key，兩者皆需 Pigo 明確授權。
2. **Vault 4 個 dangling tree** — `git fsck` exit 0、無 dangling commit/blob、`fsck --strict` 同樣僅此 4 筆。
   判定為無害殘留（見 Pattern CCC），未執行 `git prune`。
3. **Scratch worktree `mtest`** — 內容為 main 的改寫前舊版（Pattern DDD），非資料遺失。
   因位於 scratch（24h idle 自動清理）且索引含 467 staged 變更，未做 `git worktree remove`
   或 commit/push，以免把過期實驗分支混入 main。
4. **canonical 269 vs repo 471 top-level skills** — 兩套命名空間（canonical 含 category 目錄、
   repo 含 runtime-only skill），非 drift，沿用 2026-10-23e 裁決維持不動。
5. **`~/.hermes/skills/` 內部同 trait 名雙軌** — 本次只修了 neat-freak。
   建議下次以 loader 層級（`resolve_skill_catalog()`）全面掃描 `~/.hermes/skills/`，
   找出所有 status=`ambiguous` 的 skill 一併對齊，避免同樣的 cron skip 重演。
