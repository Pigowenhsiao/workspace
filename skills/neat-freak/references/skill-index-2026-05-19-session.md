# Skill_Index.md 腐敗實錄（2026-05-19 Session）

## Pattern V：Systematic Per-Section Header Drift — All 14 Headers Equally Off

**日期**：2026-05-19  
**觸發**：cron job neat-freak pass

**現象**：用 Python script 統計 `docs/Skill_Index.md` 全部 14 個 per-section 類別的 actual row count，發現每個 header 的宣告值都比 actual 少 1，且 drift 量完全一致（全部 +1）。

```
Agent, Workflow & Skill Operations         declared=103 actual=104  +1
Knowledge, Obsidian & Personal Productivity declared=40 actual=41   +1
Git, DevOps & Deployment                   declared=27 actual=28    +1
Code Quality, Review & Engineering         declared=25 actual=26    +1
Browser, Web, Search & Social Automation   declared=40 actual=41     +1
Design, Frontend & Visual UI               declared=23 actual=24    +1
Media, Images, Slides & Visualization      declared=36 actual=37     +1
Documents, Writing & Research Publishing   declared=63 actual=64     +1
Data Science, Statistics & Scientific      declared=38 actual=39    +1
Biomedical, Chemistry & Lab Research       declared=72 actual=73    +1
Business, Finance & Product Analysis       declared=74 actual=75    +1
Learning, Reasoning & Expert Personas      declared=21 actual=22    +1
Utilities, Formats & Local Automation       declared=4  actual=5     +1
Other / Needs Manual Review                declared=15 actual=16    +1
---------------------------------------------------------------------------
TOTAL                                      declared=581 actual=595  -14
```

**診斷方法**：Python script 解析 Skill_Index.md，在 `## Skills by Category` 區段內：
1. 以 `### <category> (N)` header 為界，收集每段內所有 `| Name | Purpose |` 行
2. 排除 `|---|` 分隔行和 `| Name | Purpose |` 表頭
3. 計數 actual rows
4. 與 header `(N)` 比對

```python
import os
import re

with open(os.path.expanduser('~/Documents/Agent/docs/Skill_Index.md'), 'r') as f:
    lines = f.readlines()

in_cat_section = False
current_cat = None
current_declared = None
current_rows = []

for line in lines:
    stripped = line.rstrip('\n')
    if '## Skills by Category' in stripped:
        in_cat_section = True
        continue
    if in_cat_section and stripped.startswith('### '):
        if current_cat is not None:
            actual = len(current_rows)
            print(f"{current_cat}: declared={current_declared} actual={actual} drift={current_declared-actual:+d}")
        m = re.match(r'### (.+?) \((\d+)\)', stripped)
        if m:
            current_cat = m.group(1)
            current_declared = int(m.group(2))
            current_rows = []
        else:
            current_cat = None
    elif in_cat_section and stripped.startswith('|') and current_cat is not None:
        if re.match(r'\|[-:\s]+\|', stripped):
            continue
        if 'Name' in stripped and 'Purpose' in stripped:
            continue
        current_rows.append(stripped)
```

**修復**：Python script 批次置換所有 14 個 header 的 `(N)` 為 `(N+1)`，同步更新 Summary `Active Skills: 581→595`，更新 `Generated: 2026-05-06 → 2026-05-19`，更新 Skill_Category.md 的驗證註解。

**鑑別診斷**：若 drift 為「全部 sections 一致偏移」，這是 Pattern V 的特徵；若是「不均勻 drift，有的多有的少」，則是普通 Pattern I（general per-section drift）。Pattern V 的 uniform +1 offset 是新增 skill/remove skill 時只更新 Summary 忘了更新 per-section headers 的典型後果。

**預防**：任何 bulk skill 操作後（add/remove/archive），都必須重跑 `python3 ~/.hermes/skills/neat-freak/scripts/skill-index-check.py` 驗證口徑，不能只靠 git diff 好不好看。

---

## Pattern W：execute_code 與 terminal() 的適用場景

**日期**：2026-05-19  
**觸發**：修復 Skill_Index.md 時嘗試用 `terminal(command='cd X && python3 -c "..."')` 執行多行 Python script

**問題**：inline Python script 包含 `&` 時，`terminal()` 回傳 exit code -1，錯誤訊息「Foreground command uses '&' backgrounding」。

**解決**：改用 `execute_code`（Hermes sandbox Python）執行多行文字處理。`terminal()` 只用於已知的 shell-safe 指令（`ls`, `git status`, `wc -l`, `diff` 等）。

**選擇原則**：
| 工具 | 適用場景 |
|------|---------|
| `execute_code` | Python 腳本、檔案內容操作、多行邏輯、`re.findall`/`re.sub`、字串處理 |
| `terminal()` | 簡單 `ls`、git status、已知安全的單行指令、`diff` 比對兩個已知檔案、`cp` 已知檔案 |

---

## Pattern X：patch Tool 在 sibling subagent 修改後失敗

**日期**：2026-05-19  
**觸發**：對 Skill_Index.md 進行第二次 patch 時（第一次已成功），回報「File was modified by sibling subagent」

**解決**：重新 `read_file()` 目標檔案後再 patch。`read_file` 會刷新工具對當前檔案狀態的認知。

---

## Pattern Y：metadata 必須與內容變更同時更新

**日期**：2026-05-19  
**觸發**：Skill_Index.md 口徑修正完成後忘了更新 `Generated:` date，留下「count 已改、date 沒動」的狀態

**解決**：任何時間修改帶有 `Generated:`、`Last updated:`、`Updated:` 的檔案，都必須在同一次 commit 中更新 metadata。漏掉的 metadata 落後會造成日後 agent 看到「數字已更新但日期還是舊的」無法判斷修復是否已套用。