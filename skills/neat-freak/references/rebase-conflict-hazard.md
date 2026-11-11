# Rebase Conflict Hazard — Agent Repo Push

## 觀察（2026-06-08）

**場景**：本地 commit → `git pull --rebase` → conflict → `git rebase --skip` → push回报 "Everything up-to-date"

**根本原因**：`git rebase --skip` 丟棄當前 commit 的變更，將 HEAD 直接移到遠端分支的 tip。本地 commit 的內容在 rebased commit 中不復存在。

**實際變更被丟棄**：
```
Local: abca15c28 chore(skills): update llm-wiki + x-note skills
Remote: 3fe533bdd sync: update baoyu-skills path refs + sync all x-* skills
After skip: HEAD = 3fe533bdd (abca15c28 消失)
```

##正確處置流程

###情境：本地分支落後於遠端，需要 push

**DO NOT** 直接 `git pull --rebase`（會在 conflict 時觸發危險的 skip 選項）

**推薦做法 A（保留完整歷史）**：
```bash
# 1. 查看本地即將被取代的 commit
git log --oneline -3

# 2. 若需要保留：先創建 backup branch
git branch backup-before-rebase

# 3. 使用 merge 而非 rebase
git pull --no-rebase origin main
# →產生 merge commit，兩邊歷史都保留

# 4. 若 push 被 rejected（not fast-forward）
git push origin HEAD:main
# → 失敗，匯出變更後再處理
```

**推薦做法 B（明確解決 conflict）**：
```bash
# 1. 手動 resolution：選擇 ours 或 theirs
git checkout --ours<file> # 保留本地版本
git checkout --theirs <file> # 採用遠端版本

# 2. add + continue
git add <resolved-files>
git rebase --continue
```

**推薦做法 C（dump 成 patch，強行套用）**：
```bash
# 從 backup branch 取出 commit 內容
git show abca15c28 > /tmp/local_changes.patch
#然後手動 apply 或 cherry-pick 到乾淨分支
```

## 驗證/commit 前必查

```bash
#確認即將 push 的 commit 包含預期變更
git log --oneline origin/main..HEAD
git diff origin/main HEAD --stat
```

## 緊急恢復

若已 skip丟失 commit：
```bash
#1. 從 reflog 找回
git reflog | grep "abca15c28"
#輸出類似：abca15c28 HEAD@{N}: commit: chore(skills): update llm-wiki + x-note

# 2. 恢復到該 commit
git checkout abca15c28
git branch recovery-branch

# 3. 在 recovery branch 上 rebase 到 origin/main
git rebase origin/main
#這次手動解決所有 conflicts
```

## 預防原則

| 情境 | 策略 |
|------|------|
| 自己的 branch，無需保留乾淨歷史 | `git pull --rebase` + 手動 resolve conflicts |
| 共享 branch，需保留精確歷史 | `git pull --no-rebase`（merge commit）|
| 已落後很多，先看內容再行動 | `git fetch` + `git log --oneline origin/main..HEAD` |
| 不確定會不會 conflict | 先 `git branch backup` 再操作 |

## 關聯檔案

- `scripts/git-dangling-cleanup.sh` — 用於事後清理 rebase 產生的 dangling objects
