# Skill Discovery Patterns

## 驗證 Skill 是否存在於 Skill_Index.md

### 標準 SKILL.md（小寫）
```bash
# 有效：grep + wc
grep -c "skill-name" ~/Documents/Agent/docs/Skill_Index.md
# 返回 1 = 存在，返回 0 = 不存在
```

### 非標準 Skill.md（大寫 S）— grep 可能失敗
某些 skill 使用 `Skill.md` 而非標準的 `SKILL.md`，例如 `paper-read`。
grep 在大量輸出被截斷時可能無法正確匹配。

**可靠做法（按優先順序）：**
1. `grep -c` 返回 0 時，立即用 `read_file` 搭配 offset/limit 人工確認
2. 直接列出 skill 目錄：`ls ~/Documents/Agent/skills/<name>/`
3. 驗證檔案存在：`ls ~/Documents/Agent/skills/<name>/SKILL.md 2>/dev/null || ls ~/Documents/Agent/skills/<name>/Skill.md`

**實戰順序（2026-05-09 確認）：**
```bash
# Step 1: 嘗試 grep（快速）
grep -c "learning-assistant\|paper-read" ~/Documents/Agent/docs/Skill_Index.md
# → 0 表示未列入

# Step 2: 確認 skill 實體存在
ls ~/Documents/Agent/skills/learning-assistant/SKILL.md
ls ~/Documents/Agent/skills/paper-read/Skill.md  # 大寫 S

# Step 3: 如有疑問，用 read_file 驗證 Skill_Index 該分類區塊
# sed 或 read_file offset/limit 找到對應 category
```

## 修復計數錯誤
Skill_Index.md 的抬頭如 `(24)` 是手工維護，容易出錯。
發現漏列後：
1. 先數 category 內的實際行數（`| Skill |` 開頭的行）
2. 同時更新抬頭數字
3. Commit message 註明「was incorrectly stated as X」

## 發現歷程（2026-05-09）
- `learning-assistant`：SKILL.md 存在，但從未列入 Skill_Index
- `paper-read`：Skill.md 存在（大寫 S），從未列入
- `awesome-design-md`：是 VoltAgent awesome list 的目錄結構，非獨立 skill，**不應列入**

---

## Skill_Index.md 行數計算陷阱（2026-05-12 確認）

**問題**：`grep -c` 會把「分類抬頭行」如 `| [ce:ideate](../ce-ideate/SKILL.md)` 也算進去，
導致回傳數字比實際 skill 數量多一個數量級（594 行 vs 42 個 skill）。

**實測**：
```bash
cat ~/Documents/Agent/docs/Skill_Index.md | grep -c "| \["   # 回傳 594（錯）
ls ~/Documents/Agent/skills/ | grep -v "^\\." | wc -l          # 回傳 42（正確）
```

**可靠做法**：
```bash
# 數 skill 數量 → 數目錄
SKILL_COUNT=$(ls ~/Documents/Agent/skills/ | grep -v "^\\." | wc -l)

# Finance skill pack 特殊情況：51 個 finance-* skills 以「imported reference copy」形式列入，
# 標注「not installed in Codex runtime hot set」。這些是 Codex 全域離線學習參考，
# 不占 skills/ 目錄實體。若數目錄落後於 Skill_Index，記得排除 finance-skill-pack/codex-skills/。
```

---

## 嵌入式 .git 目錄偵測模式（2026-05-12 確認）

**問題**：子目錄內含 `.git/` 時（如 `book-reader/`、`spinedigest/`、`Horizon/`），
Git 會視為「nested repo」，`?? SubDir/` 出現在根目錄 untracked 列表。

**跡象**：
```bash
git status --short        # 看到 ?? SomeDir/
ls SomeDir/.git 2>/dev/null  # 有輸出 = 嵌入式 .git
```

**修復**：
1. 外部專案（非此 repo 的一部分）→ 加進 `.gitignore`：`echo "SomeDir/" >> .gitignore`
2. 上游 fork 或 submodule → 用 `git submodule add` 而非直接 clone

**已確認有嵌入式 .git 的目錄**（已加入 .gitignore）：
- `book-reader/`
- `spinedigest/`

**待確認**：`Horizon/`（Jekyll link blog scraper）— 需要 Pigo 確認是否要追蹤

---

## 記憶路徑真相（2026-05-14 確認，2026-05-20 更新）

**上次假設已修正**：`~/Documents/Agent/memory/` 目錄**存在**，不是「雙向同步」的問題。

**實際結構（2026-05-20 實測）**：
- `~/.hermes/memory/` = Hermes 的唯一事實來源（P0-core.md, P1-90days.md, P2-30days.md）
- `~/Documents/Agent/memory/` = Codex 的鏡像副本（含 Readme.md 由 Codex 的 directory-readme-generation 技能生成）
- 兩邊內容需手動保持同步（目前同步方式：發現差異後手動 commit）

**驗證是否同步**：
```bash
diff ~/.hermes/memory/P0-core.md ~/Documents/Agent/memory/P0-core.md
diff ~/.hermes/memory/P1-90days.md ~/Documents/Agent/memory/P1-90days.md
diff ~/.hermes/memory/P2-30days.md ~/Documents/Agent/memory/P2-30days.md
```

**驗證方法**：
```bash
ls ~/Documents/Agent/memory/ 2>/dev/null && echo "EXISTS" || echo "DOES NOT EXIST"
```

**需要同步的時機**：任一次記憶變更後，檢查兩邊是否一致，不一致則以 `~/.hermes/memory/` 為準同步到 Codex copy 並 commit。

---

## Pigo_Obsidian 孤兒物件偵測（2026-05-14 確認）

**問題**：git crash/push 中斷留下 dangling commit/tree，不影響功能但汙染 repo。

**跡象**：
```bash
git fsck --full 2>&1 | grep "dangling"
```

**修復**：
```bash
git gc  # 自動清除孤兒物件
git fsck --full 2>&1 | grep "dangling"  # 驗證乾淨
```

**已確認**：2026-05-14 執行 gc 後清除 20+ dangling objects，repo 恢復乾淨。
