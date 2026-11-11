# Skill_Index.md 2026-10-23 (third run) — Purpose cell 三型腐蝕 + checker 誤判 bug

## 觸發

cron job `539040a91ad2`（Vault 整潔同步 neat-freak，every 120m）。

## 發現 1：`skill-index-check.py` 的 Purpose cell 檢查**漏掉單一反斜線腐蝕**

實測：index 內有 14 個 row 的 purpose cell 是 `\|`（pipe 未逸出，cell 被截成單一反斜線），
但 script 回報 `✓ ALL CLEAN`。

**根因（兩個疊加）**：

1. `check_purpose_corruption()` 用 `line.split('|')` 切 cell。`\|` 裡的 `|` 也被當分隔符，
   row 被切成 5 段而不是 4 段，`cells[2]` 取到的不是 purpose cell。
2. 判定條件是 `purpose in ('\\\\', '\\\\\\\\') or purpose.startswith('\\\\')`（Python source 裡
   `\\\\` = 2 個反斜線）。單一 `\` 不在集合裡，`startswith` 也不成立 → 漏判。

**修復**：

- 新增 `_split_row()`：`re.split(r'(?<!\\)\|', line)` — 只在未被 escape 的 pipe 上切分。
- 判定集合加入單一 `'\\'`。
- 順帶把回傳 tuple 擴為 5 元素（加 `reason`），並更新列印端。

## 發現 2：Purpose cell 有兩型「非 pipe」腐蝕，舊 script 完全看不到

1. **佔位描述**：`| agent-browser | ... | Agent workflow skill for agent-browser. | ... |`
   — 這是 rebuild 腳本在抓不到 frontmatter description 時自動生成的無資訊佔位字串。
   全庫共 57 個 row 受影響（agent-workflows 大區塊幾乎全中）。
2. **字面量 `\n`**：`goal-style-workflow` 的 purpose 含兩字元 `\n`（YAML block scalar
   的換行被寫成 literal escape）。

**檢測條件（已加入 script）**：

```python
elif re.match(r'^Agent workflow skill for .+\.$', purpose):  reason = 'placeholder'
elif '\\n' in purpose:                                      reason = 'literal-newline'
```

## 發現 3：佔位描述行的 frontmatter 本身可能是「非 YAML 格式」

57 個佔位行中，55 個有正常 YAML frontmatter（可直接取回 description）；
但 `inside-finding` 與 `design-frontend-visual/100-layout-compositions` 兩個
SKILL.md **根本沒有 YAML frontmatter**，只有 `## Purpose` / `## When to Use` 區段。

→ 這兩個得人工寫 description（本次已寫入 index）。
→ 長期解：這兩個 SKILL.md 應補 frontmatter（本次未改 skill 本體，避免動到內容）。

## 修復流程（本次實作）

1. 掃描全部 row → 辨識 degraded purpose（backslash / placeholder / literal `\n`）
2. 從對應 SKILL.md 的 frontmatter `description` 取回原文
   - YAML block scalar（`description: |` / `>`）必須展開多行為單行
   - 引號包住的字串要去殼
   - `\n` escape 要還原成空格
3. pipe 逸出（`|` → `\|`）、壓縮空白、截斷至 200 字 + `…`
4. 無 frontmatter 者人工撰寫
5. `skill-index-check.py` 重跑 → `✓ ALL CLEAN`（759 = header = 8 sections，0 dangling）

## 驗證

```
舊版 index → 新 checker：detect 72（backslash 14 / placeholder 57 / literal-newline 1）
新版 index → 新 checker：detect 0
```

## 口徑陷阱

- 舊版 index 有 **14 個** `\|` row，但用 grep `\\|` 只會數到「行內出現 `\|` 的次數」，
  會把 purpose 裡合法逸出的 pipe 也算進去 → 不能用 grep 驗證這個數字。
- `check_purpose_corruption()` 的 name 取用原本是 regex `\| \[name\]\(`（舊 link 格式），
  現行 pipe table 格式根本匹配不到 → 一律 fallback 成 `'?'`。已改用 `cells[0]`。

## 未裁決（延續）

canonical `~/.hermes/skills` ↔ Agent repo `skills/` 的**結構**分歧仍在：
canonical 271 top-level dir，其中 100 個在 repo 找不到對應 frontmatter name
（含 `openclaw-imports/` 391 個 nested skill、`creative/` 16、`productivity/` 29、
`autonomous-ai-agents/` 5、`git-devops/` 5 等 category namespace 目錄）。
屬架構決策（A/B/C），需 Pigo 裁決，不做機械式搬移。
