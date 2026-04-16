---
name: lint
description: |
  Lint 程式碼品質檢查 Skill。當需要對 Ruby 和 ERB 檔案進行程式碼品質檢查、發現問題、或執行自動修復時觸發。
  適用場景：
  - 推送程式碼前進行檢查
  - 發現並修復程式碼風格問題
  - 資訊安全漏洞掃描
  - 維護程式碼一致性
  
  觸發詞：lint、程式碼檢查、code quality、Ruby lint、ERB lint
  
  注意：主要用於 Ruby on Rails 專案
---

# Lint Skill

## 什麼時候用

- 使用者說「幫我 lint 一下這些檔案」
- 使用者說「檢查 Ruby 程式碼」
- 使用者說「自動修復 ERB 問題」
- 使用者說「推送前檢查」

## 工作流程

### Step 1: 確認檢查範圍

```
必要：
- 檔案或目錄路徑

可選：
- 語言類型（Ruby / ERB / 兩者）
- 是否自動修復
```

### Step 2: 執行檢查

#### Ruby 檔案檢查

```bash
# 標準檢查（推薦）
bundle exec standardrb

# 自動修復
bundle exec standardrb --fix
```

#### ERB 範本檢查

```bash
# 檢查所有 ERB
bundle exec erblint --lint-all

# 自動修復
bundle exec erblint --lint-all --autocorrect
```

#### 安全漏洞掃描

```bash
# Rails 安全掃描
bin/brakeman
```

### Step 3: 分析結果

分析檢查輸出：

```markdown
## 檢查結果

### 🔴 錯誤（需修復）
| 檔案 | 行 | 問題 | 嚴重性 |
|------|----|------|--------|
| [檔案] | [行] | [問題] | Error |

### 🟡 警告（建議修復）
| 檔案 | 行 | 問題 | 嚴重性 |
|------|----|------|--------|

### ✅ 通過
[通過的檔案清單]
```

### Step 4: 執行修復（如需要）

```bash
# 自動修復可安全的問題
bundle exec standardrb --fix
bundle exec erblint --lint-all --autocorrect

# 重新檢查
bundle exec standardrb
```

### Step 5: 提交修復

```bash
git add -A
git commit -m "style: linting auto-fixes"
```

## 工具速查

| 語言 | 檢查 | 自動修復 |
|------|------|----------|
| Ruby | `bundle exec standardrb` | `--fix` |
| ERB | `bundle exec erblint --lint-all` | `--autocorrect` |
| Rails Security | `bin/brakeman` | ❌ |

## 邊界條件

| 情況 | 處理方式 |
|------|----------|
| bundle not found | 執行 `bundle install` |
| 檢查失敗 | 顯示詳細錯誤並提供修復建議 |
| 部分檔案失敗 | 標記失敗檔案，其餘繼續 |
| 無法自動修復 | 手動修復並標記 |

## 示例

### 典型使用場景

**輸入：**
> 幫我檢查 app/models 和 app/views

**執行：**
```bash
bundle exec standardrb app/models
bundle exec erblint --lint-all app/views
```

**輸出：**
```
Checking app/models...
..F.....

1 error found:
- app/models/user.rb:23 - Style/Todo: TODO found

Checking app/views...
All clear!
```
