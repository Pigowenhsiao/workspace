# Git Dangling Objects 觀察筆記

## 背景

`git fsck --full` 輸出的 `dangling commit` / `dangling tree` / `dangling blob` 是 git 日常操作的正常副產物，不代表 repo 損壞。

常見成因：
- 中斷的 rebase、merge、pull
- `git commit --amend` 替換舊 commit
- `git rebase -i` 丟棄的中間 commit
- 高頻 cron sync 中斷（30 分鐘級別的 `git add -A && git commit` 迴圈）

## 觀察記錄

| 日期 | 來源 | 殘留量 | 備註 |
|------|------|--------|------|
| 2026-05-15 | Pigo_Obsidian Vault | 11 個 objects | `git gc` 標準 aggressive=0 無法清除，repo 運作完全正常 |
| 2026-05-16 | Pigo_Obsidian Vault | 16+ objects | `git gc` 標準 aggressive=0 無法清除，`reflog expire --expire=now --all && git gc --prune=now` 後全清除，驗證 `fsck --full` 乾淨 |

| 2026-05-20 | Pigo_Obsidian Vault | 2 dangling commits | `git stash` → `git pull` → `git stash pop` 迴圈中，WIP stash 產生後被 pop，產生 2 個 dangling commits；`reflog expire --expire=now --all && git gc --prune=now` 後全清除 |
| 2026-10-24 | Pigo_Obsidian Vault | 4 dangling **tree** | 過去多次 session 誤記為「無害殘留不處理」；實測 `reflog expire --expire=now --all && git gc --prune=now`（**不需 `--aggressive`**）即可完全清除，`git fsck --full` 輸出全空、`count-objects -v` count=0。見 Pattern EEE |

## dangling tree vs dangling commit（2026-10-24 澄清）

**dangling tree 可以清掉，不必當作無害殘留。**

歷史觀察記錄（2026-05-15 / 05-16）只涵蓋 **dangling commit**，並記錄「`git gc` 標準
aggressive=0 無法清除，必須搭配 reflog expire」。但 dangling **tree** 是另一類物件：
它是某個被 gc 掉的 commit/tree 的殘留容器，其子 blob 早已不可達。
`reflog expire` 清掉 reflog 對這些 tree 的引用後，普通 `gc --prune=now` 就能回收。

**標準清理流程（日常 housekeeping）**：
```bash
cd <repo>
git reflog expire --expire=now --all
git gc --prune=now          # 日常用這個就夠
git fsck --full             # 期望：完全無輸出
git count-objects -v        # 期望：count: 0
```

**不要用 `git fsck --unreachable` 判斷乾淨度**——它會把 dangling tree 的已 gc 子物件
逐一枚舉，看起來像 100+ 筆「無法取得」（見 Pattern CCC）。判定要用 `git fsck`（exit code）
+ `cat-file` 交叉驗證。

**`scripts/git-dangling-cleanup.sh` 內建 `--aggressive`**，對 1.1G 的 Vault repo 會做完整
repack（數分鐘、大量 I/O）。日常只需 `reflog expire + gc --prune=now`；
`--aggressive` 留給「發布乾淨 tarball / docker image」等一次性場景。

## `git stash` 產生 dangling commits 的場景

`git stash` 時如果 `git pull` 沒有回傳新 commit（already up to date），`git stash pop` 會把 WIP stash 丟回工作區但不產生新的 commit，但 stash 本身（reflog 中的 `stash@{0}`）在 pop 後就變成不可達物件。這種 dangling commits 單靠 `git gc`（甚至 `--aggressive`）無法清除，必須搭配 `reflog expire`。

**實測（2026-05-20）：**
```bash
git fsck --full 2>&1 | grep "dangling"  # 2 dangling commits 殘留
git reflog expire --expire=now --all && git gc --prune=now  # 全清除
git fsck --full 2>&1 | grep "dangling"  # 乾淨
```

## `git gc` 行為澄清

`git gc` 預設 aggressive=0，只清除「鬆散物件」（loose objects）。

```
git gc           # 基本，只清理鬆散物件
git gc --aggressive  # 更深度，但仍有極限
git gc --prune=now   # 配合 reflog expire 可幾乎完全清除
```

**`git gc` 無法清除所有 dangling objects 是正常行為，不是失敗。**

真正徹底清理需要：
```bash
git reflog expire --expire=now --all
git gc --prune=now
```

## 判斷是否需要處理

- 正常開發 repo：完全不用管，無影響
- 需要發布乾淨 tarball / docker image：執行徹底清理
- 看到 dangling blob 很多：可能是 `git clone --depth` 淺 clone 的殘留，正常

## 驗證是否乾淨

```bash
git fsck --full
# 期望輸出：nothing to report (or minimal single-line summary)
# dangling_* 輸出 = 仍不乾淨
```

## Vault 自動產出目錄的處理

Pigo_Obsidian 的 `Daily/Briefing/` 是每日簡報自動產出（晨報/晚報），不應進版控。`gitignore` 應持續維護此 pattern。

```bash
# 確認是否已忽略
grep "Daily" .gitignore || echo "Daily not in gitignore"
# 如需加入
echo "Daily/" >> .gitignore && git add .gitignore && git commit -m "chore(vault): ignore Daily/ auto-generated briefing output"
```

修復後再次 `fsck --full`，輸出乾淨才算完成。
