---
name: github
description: |
  GitHub CLI Skill。當需要與 GitHub 互動、操作 Issue、PR、CI，或需要查詢 GitHub API 時觸發。
  適用場景：
  - 建立和管理 Issue
  - 查看和操作 Pull Request
  - 檢視 CI/CD 執行狀態
  - 查詢 repo 資料
  - 管理 GitHub Actions
  
  觸發詞：github, gh, issue, pull request, PR, CI, actions
  
  依賴：需要 `gh` CLI 已安裝（`brew install gh`）
---

# GitHub Skill

## 什麼時候用

- 使用者說「幫我建立一個 GitHub Issue」
- 使用者說「查看這個 PR 的狀態」
- 使用者說「這個 repo 的 CI 過了嗎」
- 使用者說「列出所有的 open issues」

## 工作流程

### Step 1: 確認需求

```
必要：
- 操作類型（issue / pr / run / api）
- 目標 repo（如果不在 git 目錄）

可選：
- 具體 Issue/PR 編號
- 篩選條件
```

### Step 2: 執行操作

```bash
# 確認已登入
gh auth status

# 如果未登入
gh auth login
```

### Step 3: 根據需求執行

#### Issue 操作

```bash
# 列出 open issues
gh issue list --repo owner/repo

# 建立 issue
gh issue create --repo owner/repo --title "標題" --body "內容"

# 查看 issue
gh issue view 123 --repo owner/repo

# 關閉 issue
gh issue close 123 --repo owner/repo
```

#### Pull Request 操作

```bash
# 列出 PRs
gh pr list --repo owner/repo

# 查看 PR
gh pr view 55 --repo owner/repo

# 建立 PR
gh pr create --repo owner/repo --title "標題" --body "內容"

# 查看 CI 狀態
gh pr checks 55 --repo owner/repo

# 合併 PR
gh pr merge 55 --repo owner/repo --squash
```

#### CI/CD 操作

```bash
# 查看最近的 workflow runs
gh run list --repo owner/repo --limit 10

# 查看特定 run
gh run view 123456 --repo owner/repo

# 重新執行 workflow
gh run rerun 123456 --repo owner/repo
```

#### API 操作

```bash
# 基本 API 查詢
gh api repos/owner/repo

# 查看 commit
gh api repos/owner/repo/commits

# 查看 workflow
gh api repos/owner/repo/actions/workflows
```

## 常見操作速查

| 需求 | 指令 |
|------|------|
| 列出 open issues | `gh issue list` |
| 建立 issue | `gh issue create --title "..." --body "..."` |
| 查看 PR | `gh pr view 55` |
| 建立 PR | `gh pr create` |
| CI 狀態 | `gh pr checks 55` |
| 合併 PR | `gh pr merge 55 --squash` |
| 列出 workflow | `gh run list` |
| API 查詢 | `gh api /endpoint` |

## 邊界條件

| 情況 | 處理方式 |
|------|----------|
| 未登入 | 提示執行 `gh auth login` |
| Repo 不存在 | 檢查 repo 名稱是否正確 |
| 權限不足 | 告知需要 Token 權限 |
| 操作失敗 | 顯示錯誤資訊並提供解決方案 |

## 示例

### 典型使用場景

**輸入：**
> 幫我在這個 repo 建立一個 issue：owner/project，標題是「修復登入問題」

**執行：**
```bash
gh issue create --repo owner/project --title "修復登入問題" --body "描述..."
```

**輸出：**
```
https://github.com/owner/project/issues/123
Issue 建立成功！
```

### 典型使用場景 2

**輸入：**
> 查看這個 PR 的 CI 狀態 https://github.com/owner/repo/pull/55

**執行：**
```bash
gh pr checks 55 --repo owner/repo
```

**輸出：**
```
✅ CI checks passed
- build: success
- test: success
- lint: success
```

## 限制說明

- 需要 `gh` CLI 已安裝
- 部分操作需要 GitHub Token 權限
- API 速率限制依賴 Token 等級
